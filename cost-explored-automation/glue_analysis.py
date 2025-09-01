import json
from collections import defaultdict
import subprocess
import requests
import os

# Load the Glue cost data
with open('glue_last_two_months.json') as f:
    data = json.load(f)

daily_costs = []
region_costs = defaultdict(lambda: defaultdict(float))  # date -> region -> amount

for day in data['ResultsByTime']:
    date = day['TimePeriod']['Start']
    total = 0.0
    for group in day['Groups']:
        region = group['Keys'][0] if len(group['Keys']) > 0 else 'UnknownRegion'
        amount = float(group['Metrics']['UnblendedCost']['Amount'])
        region_costs[date][region] += amount
        total += amount
    daily_costs.append({'date': date, 'amount': total})

amounts = [d['amount'] for d in daily_costs]
average = sum(amounts) / len(amounts)
threshold = 2 * average
spikes = [d for d in daily_costs if d['amount'] > threshold]

# Prepare a concise summary for Webex
summary_lines = []
summary_lines.append(f"Glue - Average daily cost: ${average:.2f}")
summary_lines.append(f"Glue - Spike threshold (2x average): ${threshold:.2f}")
if spikes:
    summary_lines.append(f"Glue cost spikes detected: {len(spikes)} days.")
    for d in spikes[:3]:  # Only show up to 3 spike days
        date = d['date']
        summary_lines.append(f"{date}: ${d['amount']:.2f}")
else:
    summary_lines.append("No Glue cost spikes detected.")
summary_lines.append("Top 3 regions by total cost:")
region_totals = defaultdict(float)
for d in daily_costs:
    for region, amount in region_costs[d['date']].items():
        region_totals[region] += amount
for region, amount in sorted(region_totals.items(), key=lambda x: x[1], reverse=True)[:3]:
    summary_lines.append(f"{region}: ${amount:.2f}")
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

def generate_observations_ollama(spikes, daily_costs, region_costs, model="mistral"):
    prompt = f"""
You are a cloud cost analyst. Here is the daily AWS Glue cost data for the last two months. Identify any spikes, trends, and provide concise observations (max 1000 words) about which regions contributed most to cost changes. Suggest possible reasons for spikes and recommendations for cost optimization. Write your answer as if you are preparing a summary for the Glue team, and ask them to provide justifications for any spikes or unusual patterns.\n\nSpikes:\n{spikes[:3]}\n\nAll daily costs (summary):\n{daily_costs[:3]} ...\n\nRegion breakdown (top 3):\n{ {k: v for k, v in list(region_costs.items())[:3]} }\n"""
    try:
        result = subprocess.run([
            "ollama", "run", model, prompt
        ], capture_output=True, text=True, check=True)
        llm_output = result.stdout
        print("\nOllama LLM Observations for Glue (share this with your team):")
        print(llm_output)
        # Send concise LLM output to Webex
        room_id = os.environ.get("WEBEX_ROOM_ID")
        bot_token = os.environ.get("WEBEX_BOT_TOKEN")
        if room_id and bot_token:
            # Truncate if needed
            max_len = 7000
            llm_output_short = llm_output[:max_len]
            send_to_webex(f"**Glue Cost Analysis LLM Observations:**\n\n{llm_output_short}", room_id, bot_token)
        else:
            print("Set WEBEX_ROOM_ID and WEBEX_BOT_TOKEN as environment variables to send to Webex.")
    except Exception as e:
        print(f"\n[ERROR] Ollama call failed: {e}")

# Send the concise summary report to Webex
room_id = os.environ.get("WEBEX_ROOM_ID")
bot_token = os.environ.get("WEBEX_BOT_TOKEN")
if room_id and bot_token:
    send_to_webex(f"**Glue Cost Analysis Report (Summary):**\n\n{summary_text}", room_id, bot_token)
else:
    print("Set WEBEX_ROOM_ID and WEBEX_BOT_TOKEN as environment variables to send to Webex.")

generate_observations_ollama(spikes, daily_costs, region_costs, model="mistral")
