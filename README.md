# Automation Folder

This repository is a collection of automation Proof-of-Concepts (POCs), each organized in its own subfolder. The goal is to provide a central source of code for various automation solutions, making it easy to showcase, reuse, and extend automation projects.

## Structure
Each automation POC is placed in a separate folder under the root of the repository. For example:

```
automation-folder/
├── step_function/         # AWS Step Function automation (see its README for details)
├── another_automation/   # Placeholder for future automation POCs
├── ...                   # Add more as you build new automations
```

## How to Use
- Browse each folder for a specific automation use case.
- Each folder contains its own README.md with detailed instructions, features, and setup steps.
- All code is organized for clarity and easy reuse.

## Current Automations
- **step_function/**: AWS Step Function automation with Lambda retrigger and Webex notification. [See details here.](./step_function/README.md)
- **cost-explored-automation/**: AWS Cost Explorer Glue Service Deep Dive with LLM and Webex Integration.

### Glue Service Cost Analysis Automation
This use case demonstrates how to:
- Download AWS Glue service cost data for the last two months using AWS Cost Explorer.
- Analyze daily costs, detect spikes, and summarize top regions.
- Use a local LLM (Ollama + mistral) to generate deep-dive observations and recommendations.
- Automatically send concise cost reports and LLM-generated insights to a Webex Teams channel using a bot.

#### Steps to Reproduce
1. **Download Glue Cost Data:**
   ```sh
   aws ce get-cost-and-usage \
     --time-period Start=2025-07-01,End=2025-09-01 \
     --granularity DAILY \
     --metrics "UnblendedCost" \
     --filter '{"Dimensions":{"Key":"SERVICE","Values":["AWS Glue"]}}' \
     --group-by Type="DIMENSION",Key="REGION" \
     --profile <your-aws-profile> > glue_last_two_months.json
   ```
2. **Set up Webex Bot Credentials:**
   - Create a Webex bot and get its access token.
   - Get your Webex Teams room (channel) ID.
   - Export these as environment variables:
     ```sh
     export WEBEX_BOT_TOKEN=your_bot_token
     export WEBEX_ROOM_ID=your_room_id
     ```
3. **Run Ollama Locally:**
   - Install Ollama (https://ollama.com/download) and pull a model (e.g., mistral):
     ```sh
     ollama pull mistral
     ollama run mistral
     ```
4. **Run the Analysis Script:**
   - Use the provided `glue_analysis.py` script in `cost-explored-automation/`:
     ```sh
     python3 glue_analysis.py
     ```
   - The script will:
     - Analyze Glue costs and spikes
     - Use LLM for observations
     - Send concise results to your Webex channel

#### What Happens
- The script analyzes AWS Glue costs for spikes and trends.
- It uses a local LLM (Ollama + mistral) for deep-dive, human-readable analysis.
- Both the summary and LLM output are sent to your Webex Teams channel for team review and action.
- No changes are made to your AWS account; all analysis is performed on downloaded data.

#### Requirements
- Python 3, requests library
- AWS CLI configured
- Ollama installed and running with a model (e.g., mistral)
- Webex bot and room credentials

## Contributing
- Add new automation POCs as new folders.
- Include a README.md in each new folder describing the automation, setup, and usage.
- Follow best practices for code organization and documentation.

## License
This repository is open source and available under the MIT License.

---

> This repo is intended as a showcase and source of reusable automation code for personal and professional use. Each folder is self-contained and can be demonstrated independently.
# automation-folder
