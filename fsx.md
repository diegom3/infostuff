
# Automatically Lock Down FSx File System Share Using EventBridge and SSM

This guide provides a solution for automatically removing the "Everyone" permission from a newly created FSx file system share using Amazon EventBridge and AWS Systems Manager (SSM).

## Step 1: Create the SSM Document

First, create an SSM document that will run a PowerShell command to remove the "Everyone" permission from the default share on the FSx instance.

### Example SSM Document (YAML format):
```yaml
---
schemaVersion: '2.2'
description: "Remove Everyone permission from FSx share"
parameters:
  ShareName:
    type: String
    description: "Name of the share to modify"
  FileSystemId:
    type: String
    description: "ID of the FSx File System"
mainSteps:
  - action: "aws:runCommand"
    name: "RemoveEveryonePermission"
    inputs:
      DocumentName: "AWS-RunPowerShellScript"
      Parameters:
        commands:
          - 'Remove-SmbShareAccess -Name "{{ ShareName }}" -AccountName "Everyone" -Force'
targets:
  - key: tag:Name
    values: ["fsx-file-system"]
```

## Step 2: Create the EventBridge Rule

Create an EventBridge rule that will trigger when a new FSx file system is created. This rule will start the execution of the SSM document.

### Example Terraform Configuration for EventBridge Rule:
```hcl
resource "aws_cloudwatch_event_rule" "fsx_creation_rule" {
  name        = "FsxCreationRule"
  description = "Trigger SSM document to lock down FSx share on creation"
  event_pattern = <<EOF
{
  "source": ["aws.fsx"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventName": ["CreateFileSystem"]
  }
}
EOF
}

resource "aws_cloudwatch_event_target" "ssm_target" {
  rule      = aws_cloudwatch_event_rule.fsx_creation_rule.name
  target_id = "SSMDocument"
  arn       = aws_ssm_document.fsx_lockdown.arn

  input_transformer {
    input_paths = {
      "detail-fileSystemId" = "$.detail.responseElements.fileSystemId"
    }

    input_template = <<EOF
{
  "FileSystemId": <detail-fileSystemId>,
  "ShareName": "share"
}
EOF
  }
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_ssm_document.fsx_lockdown.name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.fsx_creation_rule.arn
}
```

## Step 3: Create the SSM Document with Terraform

Deploy the SSM document using Terraform.

### Example Terraform Configuration for SSM Document:
```hcl
resource "aws_ssm_document" "fsx_lockdown" {
  name          = "FsxLockdownDocument"
  document_type = "Command"
  content       = <<DOCUMENT
{
  "schemaVersion": "2.2",
  "description": "Remove Everyone permission from FSx share",
  "parameters": {
    "ShareName": {
      "type": "String",
      "description": "Name of the share to modify",
      "default": "share"
    },
    "FileSystemId": {
      "type": "String",
      "description": "ID of the FSx File System"
    }
  },
  "mainSteps": [
    {
      "action": "aws:runCommand",
      "name": "RemoveEveryonePermission",
      "inputs": {
        "DocumentName": "AWS-RunPowerShellScript",
        "Parameters": {
          "commands": [
            "Remove-SmbShareAccess -Name {{ ShareName }} -AccountName Everyone -Force"
          ]
        }
      }
    }
  ]
}
DOCUMENT
}
```

## Step 4: Ensure Necessary IAM Roles and Permissions

Make sure the necessary IAM roles and policies are in place for EventBridge, SSM, and FSx access.

### Example IAM Role for SSM Execution:
```hcl
resource "aws_iam_role" "ssm_execution_role" {
  name = "SSMExecutionRole"
  
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ssm.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "ssm_execution_policy" {
  name = "SSMExecutionPolicy"
  role = aws_iam_role.ssm_execution_role.id
  
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:SendCommand",
        "ssm:ListCommands",
        "ssm:GetCommandInvocation"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "fsx:DescribeFileSystems"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}
```

## Summary

1. **SSM Document**: Create an SSM document that removes the "Everyone" permission from the FSx share.
2. **EventBridge Rule**: Use EventBridge to trigger the execution of the SSM document whenever a new FSx file system is created.
3. **IAM Roles and Permissions**: Ensure the correct IAM roles and policies are in place to allow EventBridge, SSM, and FSx operations.

This setup will automatically lock down the default share permissions by removing the "Everyone" group right after an FSx file system is created.
