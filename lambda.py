import json
import boto3
import logging

sns_client = boto3.client('sns')
sns_topic_arn = 'arn:aws:sns:<region>:<account-id>:<sns-topic-name>'  # Replace with your SNS Topic ARN

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log the incoming event for debugging purposes
    logger.info("Received event: %s", json.dumps(event))
    
    # Check if the event is an FSx CreateFileSystem event
    if 'detail' in event and event['detail']['eventName'] == 'CreateFileSystem':
        # Ensure 'responseElements' and 'fileSystemId' are present in the event
        if 'responseElements' in event['detail'] and 'fileSystemId' in event['detail']['responseElements']:
            # Extract relevant details
            file_system_id = event['detail']['responseElements']['fileSystemId']
            file_system_type = event['detail']['responseElements'].get('fileSystemType', 'Unknown')

            # Construct the notification message
            message = f"A new FSx file system has been created.\nFile System ID: {file_system_id}\nFile System Type: {file_system_type}"

            # Send the notification via SNS
            sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=message,
                Subject="FSx File System Created"
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Notification sent.')
            }
        else:
            # Log the case where 'responseElements' or 'fileSystemId' is missing
            logger.error("CreateFileSystem event does not contain 'responseElements' or 'fileSystemId'. Event: %s", json.dumps(event))
            return {
                'statusCode': 400,
                'body': json.dumps("CreateFileSystem event missing 'responseElements' or 'fileSystemId'.")
            }
    else:
        logger.info("Event is not an FSx CreateFileSystem event.")
        return {
            'statusCode': 400,
            'body': json.dumps('Event is not related to FSx creation.')
        }
