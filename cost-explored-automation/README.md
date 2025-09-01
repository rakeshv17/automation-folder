# AWS Glue Cost Analysis Automation

This automation provides a deep-dive analysis of AWS Glue service costs for the last two months, detects cost spikes, and generates actionable insights using a local LLM (Ollama + mistral). Results are automatically sent to a Webex Teams channel for team review and action.

## Features
- Downloads daily AWS Glue cost data (by region) for the last two months using AWS Cost Explorer.
- Analyzes daily costs, detects spikes, and summarizes top regions.
- Uses a local LLM (Ollama + mistral) to generate human-readable observations and recommendations.
- Sends concise cost reports and LLM-generated insights to a Webex Teams channel using a bot.
- All analysis is performed locally on downloaded data—no changes are made to your AWS account.

## Setup & Usage

### 1. Download Glue Cost Data
Run this command to get the last two months of Glue costs by region:
```sh
aws ce get-cost-and-usage \
  --time-period Start=2025-07-01,End=2025-09-01 \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["AWS Glue"]}}' \
  --group-by Type="DIMENSION",Key="REGION" \
  --profile <your-aws-profile> > glue_last_two_months.json
```

### 2. Set Up Webex Bot Credentials
- Create a Webex bot and get its access token.
- Get your Webex Teams room (channel) ID.
- Export these as environment variables:
  ```sh
  export WEBEX_BOT_TOKEN=your_bot_token
  export WEBEX_ROOM_ID=your_room_id
  ```

### 3. Run Ollama Locally
- Install Ollama (https://ollama.com/download) and pull a model (e.g., mistral):
  ```sh
  ollama pull mistral
  ollama run mistral
  ```

### 4. Run the Analysis Script
- Use the provided `glue_analysis.py` script:
  ```sh
  python3 glue_analysis.py
  ```
- The script will:
  - Analyze Glue costs and spikes
  - Use LLM for observations
  - Send concise results to your Webex channel

## What Happens
- The script analyzes AWS Glue costs for spikes and trends.
- It uses a local LLM (Ollama + mistral) for deep-dive, human-readable analysis.
- Both the summary and LLM output are sent to your Webex Teams channel for team review and action.
- No changes are made to your AWS account; all analysis is performed on downloaded data.

## Requirements
- Python 3, requests library
- AWS CLI configured
- Ollama installed and running with a model (e.g., mistral)
- Webex bot and room credentials

## Files
- `glue_analysis.py`: Main analysis and reporting script.
- `glue_last_two_months.json`: Downloaded AWS Glue cost data (not included in repo).

## Notes
- The script automatically truncates messages to fit Webex Teams limits.
- You can customize the LLM prompt or summary logic as needed for your team.

---
This automation is intended for cost transparency, anomaly detection, and collaborative cost optimization for AWS Glue usage.
