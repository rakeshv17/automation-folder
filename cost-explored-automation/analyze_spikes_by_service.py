import json
from collections import defaultdict
import subprocess
import requests
import os

# Load the cost data
with open('last_two_months_costs.json') as f:
    data = json.load(f)

# Extract daily costs, group by service and region
daily_costs = []
service_region_costs = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))  # date -> service -> region -> amount

for day in data['ResultsByTime']:
    date = day['TimePeriod']['Start']
    total = 0.0
    for group in day['Groups']:
        service = group['Keys'][0] if len(group['Keys']) > 0 else 'UnknownService'
        region = group['Keys'][1] if len(group['Keys']) > 1 else 'UnknownRegion'
        amount = float(group['Metrics']['UnblendedCost']['Amount'])
        service_region_costs[date][service][region] += amount
        total += amount
    daily_costs.append({'date': date, 'amount': total})

# Calculate average and threshold for spikes (e.g., 2x average)
amounts = [d['amount'] for d in daily_costs]
average = sum(amounts) / len(amounts)
threshold = 2 * average

# Find spikes
spikes = [d for d in daily_costs if d['amount'] > threshold]

print(f"Average daily cost: ${average:.2f}")
print(f"Spike threshold (2x average): ${threshold:.2f}\n")

if spikes:
    print("Spikes detected and top contributing services/regions:")
    for d in spikes:
        date = d['date']
        print(f"\n{date}: ${d['amount']:.2f}")
        flat = []
        for service, regions in service_region_costs[date].items():
            for region, amount in regions.items():
                flat.append((service, region, amount))
        top = sorted(flat, key=lambda x: x[2], reverse=True)[:5]
        for service, region, amount in top:
            print(f"  {service} ({region}): ${amount:.2f}")
else:
    print("No spikes detected.")

print("\nTop contributing services/regions for each day:")
for d in daily_costs:
    date = d['date']
    print(f"\n{date}: ${d['amount']:.2f}")
    flat = []
    for service, regions in service_region_costs[date].items():
        for region, amount in regions.items():
            flat.append((service, region, amount))
    top = sorted(flat, key=lambda x: x[2], reverse=True)[:5]
    for service, region, amount in top:
        print(f"  {service} ({region}): ${amount:.2f}")

# Ollama LLM analysis (requires Ollama running locally with a model like mistral)
def send_to_webex(message, room_id, bot_token):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json"
    }
    data = {
        "roomId": room_id,
        "markdown": message  # or "text": message for plain text
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message sent to Webex Teams channel successfully.")
    else:
        print(f"Failed to send message to Webex Teams: {response.status_code} {response.text}")

# Example usage after getting LLM output:
def generate_observations_ollama(spikes, daily_costs, service_region_costs, model="mistral"):
    prompt = f"""
You are a cloud cost analyst. Here is the daily AWS cost data for the last two months. Identify any spikes, trends, and provide observations about which services and regions contributed most to cost changes. Suggest possible reasons for spikes and recommendations for cost optimization. Write your answer as if you are preparing a summary for the respective service teams, and ask them to provide justifications for any spikes or unusual patterns.

Spikes:
{spikes}

All daily costs:
{daily_costs}

Service/region breakdown (sample):
{ {k: v for k, v in list(service_region_costs.items())[:3]} }
"""
    try:
        result = subprocess.run([
            "ollama", "run", model, prompt
        ], capture_output=True, text=True, check=True)
        llm_output = result.stdout
        print("\nOllama LLM Observations (share this with your team):")
        print(llm_output)
        # Send to Webex Teams
        room_id = os.environ.get("WEBEX_ROOM_ID")  # or hardcode your room ID
        bot_token = os.environ.get("WEBEX_BOT_TOKEN")  # or hardcode your bot token
        if room_id and bot_token:
            send_to_webex(llm_output, room_id, bot_token)
        else:
            print("Set WEBEX_ROOM_ID and WEBEX_BOT_TOKEN as environment variables to send to Webex.")
    except Exception as e:
        print(f"\n[ERROR] Ollama call failed: {e}")

# Run Ollama LLM analysis
generate_observations_ollama(spikes, daily_costs, service_region_costs, model="mistral")