import json
import boto3

sns_client = boto3.client('sns')
sns_topic_arn = 'arn:aws:sns:<region>:<account-id>:<sns-topic-name>'  # Replace with your SNS topic ARN

def lambda_handler(event, context):
    # Parse the invokingEvent field to access the configuration item
    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event['configurationItem']
    
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
