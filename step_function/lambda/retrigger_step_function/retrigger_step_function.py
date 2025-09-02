import json
import boto3
import datetime
import os
import requests

WEBEX_BOT_TOKEN = "webex_token_personal_token"
WEBEX_ROOM_ID = "roomId_of_the_webex"

def send_webex_message(message):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "roomId": WEBEX_ROOM_ID,
        "text": message
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

def lambda_handler(event, context):
    # Only trigger on FAILED status
    if event.get('detail', {}).get('status') != 'FAILED':
        return {
            'statusCode': 200,
            'body': 'Not a FAILED execution event. No action taken.'
        }

    input_str = event['detail'].get('input', '{}')
    try:
        input_obj = json.loads(input_str)
    except Exception:
        input_obj = {}

    if 'rerun_date_time_stamp' in input_obj:
        # Send Webex message if Step Function fails again after retrigger
        state_machine_arn = event['detail']['stateMachineArn']
        original_name = event['detail'].get('name', 'retriggered_execution')
        message = (
            f"Step Function {state_machine_arn} failed again after retrigger. "
            f"Execution: {original_name}. Even after retrigger, the Step Function was not successful."
        )
        send_webex_message(message)
        return {
            'statusCode': 200,
            'body': 'Already retriggered once. Webex notified. No further action taken.'
        }

    sfn = boto3.client('stepfunctions')
    state_machine_arn = event['detail']['stateMachineArn']
    rerun_time = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    input_payload = input_obj.copy()
    input_payload['rerun_date_time_stamp'] = rerun_time
    original_name = event['detail'].get('name', 'retriggered_execution')
    new_execution_name = f"{original_name}_{rerun_time}"[-80:]

    try:
        response = sfn.start_execution(
            stateMachineArn=state_machine_arn,
            name=new_execution_name,
            input=json.dumps(input_payload)
        )
        # Send Webex message if retrigger is successful
        message = (
            f"Step Function {state_machine_arn} retriggered successfully. "
            f"New execution name: {new_execution_name}"
        )
        send_webex_message(message)
        return {
            'statusCode': 200,
            'body': json.dumps(f'Step Function re-triggered ONCE with execution name: {new_execution_name}')
        }
    except Exception as e:
        # Send message to Webex if retrigger fails
        message = (
            f"Step Function {state_machine_arn} failed to retrigger. "
            f"Original execution: {original_name}, error: {str(e)}"
        )
        send_webex_message(message)
        return {
            'statusCode': 500,
            'body': f"Failed to retrigger Step Function. Webex notified. Error: {str(e)}"
        }