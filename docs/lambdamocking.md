#  Mocking AWS Lambda with Moto

This guide provides step-by-step instructions on how to mock AWS Lambda using the Moto library in Python. Moto allows you to simulate AWS services locally for testing purposes without interacting with real AWS resources.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.13 or higher (for capstone purposes)
- `boto3` (AWS SDK for Python)
- `moto` (Library for mocking AWS services)
- `pytest` (Testing framework for Python)

You can install the required dependencies using:

```sh
pip install boto3 'moto[all]' pytest
```

## Mocking Lambda Execution Role and Function

In this example, we will:

1. Create a mock IAM execution role (necessary for Lambda mocking).
2. Create a mock AWS Lambda function.
3. Simulate invoking the Lambda function.

### Code Implementation

```python
import json
import boto3
from moto import mock_aws
import pytest

# Define the mock Lambda function's expected response
def mock_lambda_handler(event, context):
    return {"message": "Hello from ETL team!", "event": event}

@pytest.fixture
def mock_lambda_setup():
    """Fixture to setup a mock AWS Lambda environment"""
    with mock_aws():
        client = boto3.client("lambda", region_name="us-east-1")
        iam_client = boto3.client("iam", region_name="us-east-1")

        # Create a mock IAM role for Lambda execution
        role_name = "lambda_execution_role"
        role_arn = "arn:aws:iam::123456789012:role/" + role_name

        # Mock trust relationship for the Lambda execution role
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }),
        )

        # Create the Lambda function and assign the mocked role
        client.create_function(
            FunctionName="TestFunction",
            Runtime="python3.13",
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": b"dummy"},
            Description="A test lambda function",
            Timeout=30,
            MemorySize=128,
            Publish=True,
        )
        yield client  # Provide the mock client to test functions

def test_invoke_lambda(mock_lambda_setup, monkeypatch):
    """Test invoking a mocked Lambda function and manually mocking its behavior"""
    client = mock_lambda_setup 
            
    # Mock the expected response
    def mock_invoke(*args, **kwargs):
        return {
            "StatusCode": 200,
            "Payload": json.dumps(mock_lambda_handler({"key": "value"}, None)).encode()
        }
                          
    # Patch the client.invoke method to return our mock response
    monkeypatch.setattr(client, "invoke", mock_invoke)
                 
    # Invoke the Lambda function
    response = client.invoke(FunctionName="TestFunction", Payload=json.dumps({"key": "value"}))

    # Read and decode the response
    payload = json.loads(response["Payload"].decode("utf-8"))
            
    # Assert that our mock response was returned
    assert payload["message"] == "Hello from ETL team!"
    assert payload["event"] == {"key": "value"}
```

## Explanation

- **Mock IAM Role Creation**:
  - We create a fake IAM execution role and add a trust relationship allowing Lambda to assume it.
- **Mock AWS Lambda Function**:
  - The Lambda function is created using `client.create_function()` with a dummy ZIP file.
- **Mocking Invocation**:
  - Since Moto does not execute Lambda functions, we manually mock the `invoke` method.
  - We patch the `invoke` function using `monkeypatch.setattr()` to return a predefined response.

## Running the Test

To execute the test, run:

```sh
pytest your_file_name
```

## Conclusion

You have now mocked a Lambda function with Moto!
