
# AWS Config and Lambda Solution for FSx Creation Notification

This guide outlines how to set up AWS Config with a custom Lambda function to send a notification to a distribution list every time an FSx file system is created.

## Step 1: Set Up an SNS Topic for Notifications
First, create an SNS topic to send emails to your distribution list.

1. Go to the **Amazon SNS** service in the AWS Management Console.
2. Create a new **Topic**:
    - Choose **Standard** for the topic type.
    - Name the topic (e.g., `FSxCreationNotifications`).
3. After creating the topic, go to the **Subscriptions** tab:
    - Set the **Protocol** to **Email**.
    - Enter the email address of the distribution list.
4. Confirm the subscription by clicking the confirmation link sent to the email address.

## Step 2: Create a Lambda Function to Detect FSx Creation
AWS Config can trigger a custom Lambda function whenever an FSx file system is created. Here’s how to create the Lambda function:

1. Go to the **Lambda** console and create a new function:
    - Select **Author from scratch**.
    - Name the function (e.g., `FSxCreationLambda`).
    - Choose **Python** as the runtime.
    - Set **Permissions** to create a new role with basic Lambda permissions.
    
2. Use the following Lambda function code to detect FSx creation and send notifications via SNS:

    ```python
    import json
    import boto3

    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:<region>:<account-id>:<sns-topic-name>'  # Replace with your SNS topic ARN

    def lambda_handler(event, context):
        # Extract configuration item from event
        configuration_item = event['configurationItem']
        
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
    ```

3. Deploy the Lambda function.

4. Ensure the Lambda function has permissions to:
   - Publish to SNS.
   - Access AWS Config.

## Step 3: Create a Custom AWS Config Rule
1. Go to the **AWS Config** console.
2. Select **Rules** from the navigation pane and click **Add Rule**.
3. At the bottom of the page, click **Create custom rule**:
    - Enter a name (e.g., `FSxCreationCustomRule`).
    - Specify the **Trigger Type** as **Configuration Changes**.
    - Set the **Scope of changes** to only include resources of type **AWS::FSx::FileSystem**.
4. Attach the Lambda function (`FSxCreationLambda`) as the rule’s **Lambda Function**.
5. Complete the rule creation process.

## Step 4: Set Up SNS Notification
- Ensure the Lambda function publishes messages to the SNS topic whenever an FSx file system is created.
- This Lambda function will send a notification to your email distribution list every time a new FSx file system is detected by AWS Config.

## Step 5: Test the Setup
1. Create a new FSx file system.
2. AWS Config should trigger the Lambda function, which will send a notification to the SNS topic and email the distribution list.

## Summary
This solution uses:
- **Custom Lambda Function**: To detect FSx creation events.
- **AWS Config**: To monitor FSx resources.
- **SNS**: To notify the email distribution list.
