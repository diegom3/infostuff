
# Automated FSx File System Management with AWS Lambda (Without InstanceId)

This guide will walk you through setting up an Amazon EventBridge rule that triggers an AWS Lambda function whenever a new FSx file system is created. The Lambda function will interact with the FSx API, though direct modification of SMB share permissions without using an InstanceId is limited.

## Step 1: Create the Lambda Function

1. **Go to AWS Lambda:**
   - In the AWS Management Console, search for and select **Lambda**.

2. **Create a New Lambda Function:**
   - Click **Create function**.
   - Choose **Author from scratch**.
   - Enter a name for your function, e.g., `FsxRemoveEveryonePermission`.
   - Choose the **Runtime** (e.g., Python 3.8 or later).
   - Click **Create function**.

3. **Configure the Lambda Function:**
   - In the **Function code** section, replace the existing code with the following Python script:

     ```python
     import boto3
     import json

     def lambda_handler(event, context):
         # Extract file system ID from the event
         fsx_id = event['detail']['responseElements']['fileSystemId']
         
         # Initialize FSx client
         fsx_client = boto3.client('fsx')
         
         # Describe the file system to get DNS name and other details
         response = fsx_client.describe_file_systems(FileSystemIds=[fsx_id])
         
         file_system = response['FileSystems'][0]
         dns_name = file_system['DNSName']
         
         # You would typically interact with the share via an SMB client or similar
         # But since we want to avoid using an InstanceId, we're focusing on DNS interaction
         
         # Log or take actions here depending on your specific case
         
         # For demonstration, just returning details
         return {
             'statusCode': 200,
             'body': json.dumps({
                 'message': 'Checked FSx File System DNS',
                 'file_system_dns_name': dns_name
             })
         }
     ```

   - Click **Deploy** to save the changes.

4. **Set Up the Lambda Execution Role:**
   - Go to the **Configuration** tab of your Lambda function.
   - Under **Permissions**, click on the execution role's name.
   - Attach the following policy to this role:
     - **AmazonFSxReadOnlyAccess**: Allows the Lambda function to describe FSx file systems.

## Step 2: Create the EventBridge Rule

1. **Navigate to Amazon EventBridge:**
   - In the AWS Management Console, search for and select **EventBridge**.

2. **Create a New Rule:**
   - Click on **Rules** in the left-hand menu.
   - Click **Create rule**.
   - Enter a name for your rule, e.g., `FsxCreationTrigger`.
   - Ensure the **Event bus** is set to `default`.

3. **Define the Event Pattern:**
   - Under **Event source**, select **AWS services**.
   - **Service name**: Choose `CloudTrail`.
   - **Event type**: Select `AWS API Call via CloudTrail`.
   - **Specific operation(s)**: Enter `CreateFileSystem`.

4. **Add the Lambda Function as a Target:**
   - Scroll down to the **Target(s)** section.
   - Click **Add target**.
   - **Target type**: Choose **Lambda function**.
   - **Function**: Select the Lambda function you created earlier (`FsxRemoveEveryonePermission`).

5. **Create the Rule:**
   - Click **Create rule** to save and activate it.

## Step 3: Test the Setup

1. **Create a New FSx File System:**
   - Go to the **FSx service** in the AWS Management Console.
   - Create a new file system to trigger the EventBridge rule.

2. **Verify Execution:**
   - Go to **CloudWatch Logs** and check the logs for your Lambda function to ensure it was triggered correctly and that the SSM command executed successfully.

3. **Check the Permissions (if applicable):**
   - Although this solution doesn't directly modify SMB share permissions, it retrieves and logs relevant FSx details.

## Summary

This setup allows you to trigger an AWS Lambda function whenever a new FSx file system is created. The function interacts with the FSx API to retrieve and log details about the file system, focusing on avoiding the use of an InstanceId. Direct modification of SMB share permissions without an InstanceId requires alternative approaches or custom SMB interactions, which are outside the scope of this basic setup.
