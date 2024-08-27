
# Step-by-Step Guide: Automating FSx File System Share Permissions with EventBridge and SSM

This guide will walk you through setting up an Amazon EventBridge rule that triggers an AWS Systems Manager (SSM) Run Command whenever a new FSx file system is created. This setup ensures that the "Everyone" permission is removed from the FSx share automatically.

## Step 1: Create the SSM Document

1. **Go to AWS Systems Manager**:
   - In the AWS Management Console, search for **Systems Manager** and select it.

2. **Create a New Document**:
   - In the left-hand menu, click on **Documents** under **Shared Resources**.
   - Click **Create document**.
   - Choose **Command or Session**.
   - Enter a name for your document, e.g., `FsxLockdownDocument`.
   - Set the **Document type** to `Command`.
   - In the **Content** section, paste the following YAML:

     ```yaml
     ---
     schemaVersion: '2.2'
     description: "Remove Everyone permission from FSx share"
     parameters:
       InstanceId:
         type: String
         description: "ID of the instance where the command will run"
       ShareName:
         type: String
         description: "Name of the share to modify"
         default: "share"
     mainSteps:
       - action: "aws:runPowerShellScript"
         name: "RemoveEveryonePermission"
         inputs:
           runCommand:
             - 'Remove-SmbShareAccess -Name "{{ ShareName }}" -AccountName "Everyone" -Force'
           InstanceIds:
             - "{{ InstanceId }}"
     ```

3. **Create the Document**:
   - Review the details, then click **Create document**.

## Step 2: Set Up the EventBridge Rule

1. **Navigate to Amazon EventBridge**:
   - In the AWS Management Console, search for **EventBridge** and select it.

2. **Create a New Rule**:
   - In the left-hand menu, click on **Rules**.
   - Click **Create rule**.
   - Enter a name for your rule, e.g., `FsxCreationRule`.
   - Optionally, add a description.
   - Ensure the **Event bus** is set to `default`.

3. **Define the Event Pattern**:
   - Under **Event source**, select **AWS services**.
   - **Service name**: Choose `CloudTrail`.
   - **Event type**: Select `AWS API Call via CloudTrail`.
   - **Specific operation(s)**: Enter `CreateFileSystem`.
   - Leave other fields as default.

4. **Select the Target**:
   - **Target type**: Choose **AWS Systems Manager Run Command**.
   - **Document**: Select the SSM document you created earlier (`FsxLockdownDocument`).
   - **Document version**: Leave as default unless you have multiple versions.
   - **Target key**: This field is used to identify the input fields from the JSON structure. However, if this doesn’t match your setup or throws errors, proceed with the **Input Transformer**.

5. **Configure Input Transformer**:
   - **Input Paths Map**:
     - Map the fields from the event JSON to variables:
     - Example:
       ```json
       {
         "instanceId": "$.detail.responseElements.instanceId",
         "shareName": "$.detail.requestParameters.shareName"
       }
       ```

   - **Input Template**:
     - Format the extracted values to pass to the SSM document:
     - Example:
       ```json
       {
         "InstanceId": "<instanceId>",
         "ShareName": "<shareName>"
       }
       ```

6. **Configure Additional Settings (Optional)**:
   - **Retry policy**: Set this if you want EventBridge to retry in case of failures.
   - **Dead-letter queue**: Set this if you want failed events to be sent to a DLQ for further analysis.

7. **Review and Create**:
   - Review all settings to ensure everything is correct.
   - Click **Create rule** to save and activate it.

## Step 3: Test the Setup

1. **Create a New FSx File System**:
   - Go to the **FSx service** in the AWS Management Console.
   - Create a new file system to trigger the rule.

2. **Verify the Execution**:
   - Go to **Systems Manager** > **Run Command** and check if the SSM document was executed with the correct parameters.
   - Connect to the Windows instance associated with the FSx file system and verify that the "Everyone" permission has been removed from the share.

3. **Check CloudWatch Logs (if needed)**:
   - If something doesn't work as expected, check the CloudWatch logs for detailed error messages that can help with troubleshooting.

## Summary

This process should correctly set up an EventBridge rule that triggers an SSM Run Command with the necessary parameters whenever a new FSx file system is created. By using the Input Transformer, you ensure that the correct values (such as `InstanceId` and `ShareName`) are passed to the SSM document, avoiding common errors like the "Invalid Ssm Run Command Target Key" error.
