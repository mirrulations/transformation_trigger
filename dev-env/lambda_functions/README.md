# orch_lambda

This project contains an AWS Lambda function that processes S3 events. The function extracts information from the S3 event and prints the file name and directory.

## Files

- `orch_lambda.py`: Contains the implementation of the Lambda function.
- `test_orch_lambda.py`: Contains a test for the Lambda function.

## Lambda Function

### orch_lambda

This function processes S3 events, extracts the file name and directory from the S3 object key, and prints them.

#### Handler

`orch_lambda.orch_lambda`

#### Parameters

- `event`: The event data passed to the Lambda function. This should be an S3 event.
- `context`: The context in which the Lambda function is called.

Deployment
To deploy the Lambda function, use the AWS SAM CLI. Run the following commands:

`sam build`

Testing
You can test the Lambda function locally using the AWS SAM CLI:

`sam local invoke orch_lambda`

Alternatively, you can run the test script:

`python orch_lambda/test_orch_lambda.py`
