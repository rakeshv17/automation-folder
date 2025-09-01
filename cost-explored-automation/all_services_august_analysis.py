import os
import json
from collections import defaultdict
import subprocess
import requests

# Download the AWS services cost data for August if not present
data_file = 'all_services_august.json'
if not os.path.exists(data_file):
    print(f"{data_file} not found. Downloading from AWS Cost Explorer...")
    aws_profile = os.environ.get('AWS_PROFILE', 'release-prod-admin')
    aws_cmd = [
        'aws', 'ce', 'get-cost-and-usage',
        '--time-period', 'Start=2025-08-01,End=2025-09-01',
        '--granularity', 'DAILY',
        '--metrics', 'UnblendedCost',
        '--group-by', 'Type="DIMENSION",Key="SERVICE"',
        '--profile', aws_profile
    ]
    with open(data_file, 'w') as f:
        subprocess.run(aws_cmd, stdout=f, check=True)
    print(f"Downloaded {data_file}.")

# Load the AWS services cost data for August
with open(data_file) as f:
    data = json.load(f)

daily_costs = []
service_costs = defaultdict(lambda: defaultdict(float))  # date -> service -> amount

for day in data['ResultsByTime']:
    date = day['TimePeriod']['Start']
    total = 0.0
    for group in day['Groups']:
        service = group['Keys'][0] if len(group['Keys']) > 0 else 'UnknownService'
        amount = float(group['Metrics']['UnblendedCost']['Amount'])
        service_costs[date][service] += amount
        total += amount
    daily_costs.append({'date': date, 'amount': total})

amounts = [d['amount'] for d in daily_costs]
average = sum(amounts) / len(amounts)
threshold = 2 * average
spikes = [d for d in daily_costs if d['amount'] > threshold]

# Prepare a concise summary for Webex
summary_lines = []
summary_lines.append(f"All Services - Average daily cost: ${average:.2f}")
summary_lines.append(f"All Services - Spike threshold (2x average): ${threshold:.2f}")
if spikes:
    summary_lines.append(f"Cost spikes detected: {len(spikes)} days.")
    for d in spikes[:3]:  # Only show up to 3 spike days
        date = d['date']
        summary_lines.append(f"{date}: ${d['amount']:.2f}")
else:
    summary_lines.append("No cost spikes detected.")
summary_lines.append("Top 5 services by total cost:")
service_totals = defaultdict(float)
for d in daily_costs:
    for service, amount in service_costs[d['date']].items():
        service_totals[service] += amount
for service, amount in sorted(service_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
    summary_lines.append(f"{service}: ${amount:.2f}")
summary_text = '\n'.join(summary_lines)
print(summary_text)

def send_to_webex(message, room_id, bot_token):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json"
    }
    data = {
        "roomId": room_id,
        "markdown": message
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message sent to Webex Teams channel successfully.")
    else:
        print(f"Failed to send message to Webex Teams: {response.status_code} {response.text}")

def generate_observations_ollama(spikes, daily_costs, service_costs, model="mistral"):
    prompt = f"""
You are a cloud cost analyst. Here is the daily AWS cost data for all services for August 2025. Identify any spikes, trends, and provide concise observations (max 1000 words) about which services contributed most to cost changes. Suggest possible reasons for spikes and provide optimization recommendations for the most critical (highest cost) services. Write your answer as if you are preparing a summary for the respective service teams, and ask them to investigate and take optimization measures.\n\nSpikes:\n{spikes[:3]}\n\nAll daily costs (summary):\n{daily_costs[:3]} ...\n\nService breakdown (top 5):\n{ {k: v for k, v in sorted(service_totals.items(), key=lambda x: x[1], reverse=True)[:5]} }\n"""
    try:
        result = subprocess.run([
            "ollama", "run", model, prompt
        ], capture_output=True, text=True, check=True)
        llm_output = result.stdout
        print("\nOllama LLM Observations for All Services (share this with your team):")
        print(llm_output)
        # Send concise LLM output to Webex
        room_id = os.environ.get("WEBEX_ROOM_ID")
        bot_token = os.environ.get("WEBEX_BOT_TOKEN")
        if room_id and bot_token:
            # Truncate if needed
            max_len = 7000
            llm_output_short = llm_output[:max_len]
            send_to_webex(f"**All Services Cost Analysis LLM Observations:**\n\n{llm_output_short}", room_id, bot_token)
        else:
            print("Set WEBEX_ROOM_ID and WEBEX_BOT_TOKEN as environment variables to send to Webex.")
    except Exception as e:
        print(f"\n[ERROR] Ollama call failed: {e}")

# Send the concise summary report to Webex
room_id = os.environ.get("WEBEX_ROOM_ID")
bot_token = os.environ.get("WEBEX_BOT_TOKEN")
if room_id and bot_token:
    send_to_webex(f"**All Services Cost Analysis Report (Summary):**\n\n{summary_text}", room_id, bot_token)
else:
    print("Set WEBEX_ROOM_ID and WEBEX_BOT_TOKEN as environment variables to send to Webex.")

generate_observations_ollama(spikes, daily_costs, service_costs, model="mistral")
