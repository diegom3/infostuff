import json
import boto3
import logging

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns_client = boto3.client('sns')
sns_topic_arn = 'arn:aws:sns:<region>:<account-id>:<sns-topic-name>'  # Replace with your SNS topic ARN

def lambda_handler(event, context):
    # Log the incoming event for debugging purposes
    logger.info("Received event: %s", json.dumps(event))
    
    # Parse the invokingEvent which is a stringified JSON
    invoking_event_str = event.get('invokingEvent', '{}')
    
    # Convert the stringified JSON into a dictionary
    invoking_event = json.loads(invoking_event_str)
    
    # Log the parsed invokingEvent for clarity
    logger.info("Parsed invokingEvent: %s", json.dumps(invoking_event))
    
    # Check if 'configurationItem' exists in the parsed invokingEvent
    configuration_item = invoking_event.get('configurationItem')
    
    if configuration_item:
        # Check if the resource type is FSx and the event is for creation
        if configuration_item['resourceType'] == 'AWS::FSx::FileSystem' and configuration_item['configurationItemStatus'] == 'ResourceDiscovered':
            # Send a notification to the SNS topic
            message = f"A new FSx file system has been created: {configuration_item['resourceId']}"
            
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
            return {
                'statusCode': 400,
                'body': json.dumps('Event is not related to FSx file system creation.')
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('configurationItem not found in the event.')
        }
