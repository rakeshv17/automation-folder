# Automation Folder

This repository contains a collection of automation Proof-of-Concepts (POCs), each in its own subfolder. Each POC demonstrates a specific automation use case, with detailed instructions and setup in its respective README.md file.

## Repository Structure
```
automation-folder/
├── step_function/              # AWS Step Function automation (see step_function/README.md)
├── cost-explored-automation/   # AWS Glue cost analysis with LLM and Webex (see cost-explored-automation/README.md)
├── ...                         # Add more as you build new automations
```

## Use Cases
- **step_function/**: Automates AWS Step Function retriggering and notifications, including Lambda integration and Webex alerts. See [step_function/README.md](./step_function/README.md) for full details and setup.
- **cost-explored-automation/**: Deep-dive AWS Glue cost analysis using Cost Explorer, local LLM (Ollama + mistral), and automated Webex reporting. See [cost-explored-automation/README.md](./cost-explored-automation/README.md) for full details and setup.

## How to Use
- Browse each folder for a specific automation use case.
- Each folder contains its own README.md with detailed instructions, features, and setup steps.
- All code is organized for clarity and easy reuse.

## Contributing
- Add new automation POCs as new folders.
- Include a README.md in each new folder describing the automation, setup, and usage.
- Follow best practices for code organization and documentation.

## License
This repository is open source and available under the MIT License.

---

> This repo is intended as a showcase and source of reusable automation code for personal and professional use. Each folder is self-contained and can be demonstrated independently.
# automation-folder
