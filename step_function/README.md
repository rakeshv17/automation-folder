# AWS Step Function Automation with Lambda Retrigger and Webex Notification

## Overview
This project automates the deployment of AWS Step Functions and a Lambda function that automatically retriggers failed Step Function executions once, with notifications sent to a Webex Teams room. The infrastructure is provisioned using Terraform, and the Lambda function is written in Python.

## Features
- **Provisioning of Three AWS Step Functions** using Terraform.
- **Lambda Function** that:
  - Detects failed Step Function executions via EventBridge.
  - Retriggers the failed execution only once.
  - Sends Webex Teams notifications for both successful retriggers and final failures.
- **Webex Teams Integration** for real-time alerts.
- **Clean repository structure** with .gitignore to exclude build artifacts and dependencies.

## Folder Structure
```
step_function/
├── main.tf                        # Terraform code for AWS resources
├── .gitignore                     # Ignore Terraform state, cache, and build artifacts
├── lambda/
│   ├── retrigger_step_function.py # Lambda function source code
│   ├── .gitignore                # Ignore Lambda dependencies and build artifacts
│   └── retrigger_step_function/  # (Not committed) Lambda dependencies for deployment only
```

## How It Works
1. **Terraform** provisions all AWS resources: Step Functions, Lambda, IAM roles, and EventBridge rules.
2. **EventBridge** triggers the Lambda on Step Function failure.
3. **Lambda** checks if the execution has already been retried. If not, it retriggers the Step Function and sends a Webex notification. If already retried, it sends a final failure notification.

## Deployment Instructions
1. Clone the repository.
2. Install Terraform and AWS CLI.
3. Configure your AWS credentials.
4. Update `main.tf` with your Webex Teams room and token.
5. Package the Lambda function with its dependencies (see below).
6. Run `terraform init` and `terraform apply` in the `step_function/` directory.

### Packaging Lambda Function
- Use a virtual environment to install dependencies (`requests` and its sub-dependencies).
- Copy only the required dependencies and `retrigger_step_function.py` into a deployment folder.
- Zip the contents (not the folder itself) and upload to AWS Lambda.
- Do not commit dependencies or zip files to the repo (see .gitignore).

## Security & Best Practices
- No AWS credentials or secrets are stored in the repo.
- .gitignore ensures sensitive and build files are not committed.
- Lambda only retriggers once to avoid infinite loops.

## Use Cases
- Automated recovery and alerting for failed AWS Step Function workflows.
- Real-time notifications to Webex Teams for operational awareness.

## Author
- Your Name (replace with your name or GitHub handle)

## License
This project is open source and available under the MIT License.
