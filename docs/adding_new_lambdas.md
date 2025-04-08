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

Edit app.py and define the Lambda handler function (we might want to have one handler name across lambdas for consistency):

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

in orch_lambda(), the handler for the orchestrator lambda app.py, make sure to add:

```python
mynewlambda_function = os.environ.get("MY_NEW_LAMBDA_FUNCTION")
    if not mynewlambda_function:
        raise Exception("My new lambda function name is not set in the environment variables")
```

and then in the try-catch for deciding which lambda to send the file to, add a new elif case to the if-else block:

(this specific example is looking for docket and .json in the file key, you will have to change accordingly)

```python
if '.json' in s3dict['file_key'] and 'docket' in s3dict['file_key']:
            print("docket json found!")
            response = lambda_client.invoke(
                FunctionName=sql_docket_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict).encode('utf-8')
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }
```

## Step 4: Update template.yaml

Go to dev-env/template.yaml and add a new AWS Lambda resource under Resources (This is an example):

```yaml
  MyNewLambdaFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda_functions/my_new_lambda/
      Handler: app.handler      # Mame of the handler function you made above
      Runtime: python3.13
      Timeout: 10       # If you need it to be different than the template default
      MemorySize: 256   # If you need it to be different than the template default
      Policies:         # Any policies / roles that your lambda might need to run correctly ***CAN ALSO BE REPLACED WITH ROLE: and use a custom made role in AWS ***
        - AWSLambdaBasicExecutionRole
      # If the Lambda Needs an Event Trigger (e.g., S3, API Gateway, EventBridge)
      Events:
        # S3 Trigger Example:
        S3Trigger:
          Type: S3
          Properties:
            Bucket: !Ref ExistingDataBucket
            Events: s3:ObjectCreated:*
        # API Gateway Trigger Example:
        Api:
          Type: Api
          Properties:
            Path: /my-new-lambda
            Method: get
```

In Addition, you must add the lambda to Output (at the bottom of template.yaml) as such:

```yaml
Outputs:
  
  ...

  MyNewLambdaFunctionArn:
    Description: "My New Lambda Function ARN"
    Value: !GetAtt MyNewLambdaFunction.Arn
```

Also, you must add the Arn to the Orchestrator Function in two places:

```yaml
OrchestratorFunction:
    Properties:
      Policies:
        - Statement:
            Resource: 
              - !GetAtt MyNewLambdaFunction.Arn
```

and

```yaml
OrchestratorFunction:
    Properties:
      Environment:
        Variables:
          MY_NEW_LAMBDA_FUNCTION: !Ref MyNewLambdaFunction
```

## Step 5: Install Dependencies (If Needed)

If your Lambda requires additional Python packages, list them in requirements.txt:

If you need boto3, requests, etc., add them to requirements.txt:

```txt
boto3
requests
```

This ensures that they are installed when SAM does its build and deploy for the lambda functions. If wanted, you can also install them for yourself in your .venv with the following commands:

```bash
cd lambda_functions/my_new_lambda
pip install -r requirements.txt -t 
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

Run tests from `dev-env` using:

```bash
pytest tests/my_new_lambda/
```

or just

```bash
pytest
```

## Step 7: Update the GitHub Actions Workflow (If Needed)

Since our GitHub Actions runs tests before deployment, ensure it detects the new Lambda

- This should be okay and need no special actions, as github testing should test the whole tests folder, but good to know

## Step 8: GITHUB ACTIONS deploys the Updated AWS SAM Project on Merge in main

Since we use GitHub Actions to deploy, commit & push our changes, the pipeline will handle deployment automatically.

However, this is essentially what the github actions workflow is doing when it deploys, and it is possible to be done manually.

```bash
cd dev-env  # Make sure you're in the right directory
sam build
sam validate
sam deploy
```

## Summary: Quick Checklist for Adding a New Lambda

- Create a new folder in lambda_functions/
- Implement the function in app.py
- Update usage in Orchestrator Lambda
- Update template.yaml with the new Lambda
- Add dependencies, write & run unit tests in dev-env/tests/
- PR & Merge (will run sam deploy)
