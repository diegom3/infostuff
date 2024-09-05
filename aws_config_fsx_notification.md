
# AWS Config Solution for FSx Creation Notification

This guide outlines how to set up AWS Config to send a notification to a distribution list every time an FSx file system is created.

## Step 1: Set Up an SNS Topic for Notifications
First, you need to create an SNS topic that will send emails to your distribution list.

1. Go to the **Amazon SNS** service in the AWS Management Console.
2. Create a new **Topic**:
    - Choose **Standard** for the topic type.
    - Name the topic (e.g., `FSxCreationNotifications`).
3. After creating the topic, go to the **Subscriptions** tab:
    - Set the **Protocol** to **Email**.
    - Enter the email address of the distribution list.
4. Confirm the subscription by clicking the confirmation link sent to the email address.

## Step 2: Enable AWS Config
If AWS Config is not already enabled, follow these steps:

1. In the **AWS Config** console, click **Get started** (if this is your first time) or **Add rule** if AWS Config is already enabled.
2. Select the resources you want to monitor, including **Amazon FSx** resources.

## Step 3: Create an AWS Config Rule for FSx Creation
Next, you will create an AWS Config rule that checks for the creation of FSx resources.

1. In the AWS Config console, click on **Rules** and then click **Add rule**.
2. In the search bar, type **FSx**.
3. Select the **FSx Resources Encrypted** managed rule (you can use this rule to trigger on FSx resource creation).
4. In the **Trigger type**, select **Configuration changes**.
5. Define the scope of resources:
    - Choose **Amazon FSx** as the resource type.
6. Click **Next**, configure the rule (e.g., name it `FSxCreationRule`), and then click **Add rule**.

## Step 4: Set Up SNS Notification for AWS Config
Once the AWS Config rule is set for FSx file system creation, configure AWS Config to send notifications to the SNS topic.

1. Go to **Settings** in the AWS Config console.
2. Scroll down to **Delivery channels** and configure it to send notifications to the SNS topic created in step 1.
    - Select the SNS topic (e.g., `FSxCreationNotifications`) as the destination for configuration changes.

## Step 5: Create an IAM Role for AWS Config
Ensure that AWS Config has permission to publish to your SNS topic.

1. Go to **IAM** > **Roles** and find or create the role AWS Config uses.
2. Attach the following permissions policy to allow publishing to SNS:

    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": "sns:Publish",
          "Resource": "arn:aws:sns:<region>:<account-id>:<sns-topic-name>"
        }
      ]
    }
    ```

## Step 6: Test the Setup
1. Create a new FSx file system.
2. AWS Config should detect this configuration change, and based on your rule, it will send a notification to the SNS topic.
3. Check if the email distribution list receives the notification.

## Summary
This solution leverages:
- **Amazon SNS**: To send email notifications to the distribution list.
- **AWS Config**: To monitor the creation of FSx file systems.
- **IAM**: To ensure AWS Config can publish to SNS.
