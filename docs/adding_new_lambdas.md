# How to Add a New AWS Lambda Function

This guide explains how to add a new AWS Lambda function to the **mirrulations-microservices** project stack and update the necessary files.

## Overview: Quick Checklist for Adding a New Lambda

- Create a new folder in lambda_functions/
- Implement the function in app.py
- Update usage in Orchestrator Lambda
- Update template.yaml with the new Lambda
- Add dependencies, write & run unit tests in dev-env/tests/
- PR & Merge (will run sam deploy)

## Step 1: Create a New Lambda Function

Navigate to the `dev-env/lambda_functions/` directory and create a new folder for your Lambda.

```bash
cd dev-env/lambda_functions
mkdir my_new_lambda
cd my_new_lambda
```

Inside the folder, create the following files:

```bash
touch app.py  # The Lambda function code
touch requirements.txt  # Dependencies (if needed)
touch __init__.py  # Ensures that the function is recognized as python
```

## Step 2: Implement the Lambda Function

Edit app.py and define the Lambda handler function (we might want to have one handler name for consistency):

```py
import json

def handler(event, context):
    print(" My New Lambda was triggered!")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello from My New Lambda!"})
    }
```

## Step 3: Update Orchestrator Lambda Function

This section TBD, the current organization of the orchestrator is not fully finished

## Step 4: Update template.yaml

Go to dev-env/template.yaml and add a new AWS Lambda resource under Resources (This is an example):

```yaml
  MyNewLambdaFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda_functions/my_new_lambda/
      Handler: app.handler
      Runtime: python3.13
      Timeout: 10
      MemorySize: 256
      Policies:
        - AWSLambdaBasicExecutionRole
```

If the Lambda Needs an Event Trigger (e.g., S3, API Gateway, EventBridge)
S3 Trigger Example:

```yaml
      Events:
        S3Trigger:
          Type: S3
          Properties:
            Bucket: !Ref ExistingDataBucket
            Events: s3:ObjectCreated:*
```

API Gateway Trigger Example:

```yaml
      Events:
        Api:
          Type: Api
          Properties:
            Path: /my-new-lambda
            Method: get
```

## Step 5: Install Dependencies (If Needed)

If your Lambda requires additional Python packages, list them in requirements.txt, then install locally:

```bash
cd lambda_functions/my_new_lambda
pip install -r requirements.txt -t 
```

If you need boto3, requests, etc., add them to requirements.txt:

```txt
boto3
requests
```

## Step 6: Write Unit Tests

Create a tests folder at dev-env/tests/my_new_lambda/test_app.py, and write basic unit tests (this is an example):

```py
import json
from lambda_functions.my_new_lambda.app import handler

def test_my_new_lambda():
    event = {}
    response = handler(event, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Hello from My New Lambda!"
```

Run tests using:

```bash
pytest tests/my_new_lambda/
```

## Step 7: Update the GitHub Actions Workflow (If Needed)

Since our GitHub Actions runs tests before deployment, ensure it detects the new Lambda

- This should be okay, as github testing should test the whole tests folder, but good to know

## Step 8: GITHUB ACTIONS deploys the Updated AWS SAM Project on Merge in main

Since we use GitHub Actions to deploy, commit & push our changes, the pipeline will handle deployment automatically.

However, this is essentially what the github actions workflow is doing when it deploys, and it is possible to be done manually.

```bash
cd dev-env  # Make sure you're in the right directory
sam build
sam deploy
```

## Summary: Quick Checklist for Adding a New Lambda

- Create a new folder in lambda_functions/
- Implement the function in app.py
- Update usage in Orchestrator Lambda
- Update template.yaml with the new Lambda
- Add dependencies, write & run unit tests in dev-env/tests/
- PR & Merge (will run sam deploy)
