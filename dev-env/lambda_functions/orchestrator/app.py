import boto3
import json
import os

def extractS3(event):
    if not event:
        raise ValueError("Event is empty")
 
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Cannot extract S3 information from event: {e}")

    # Construct the file path
    file_path = f"s3://{bucket_name}/{object_key}"
    return file_path

def get_lambda_client():
    # AWS_SAM_LOCAL is set to "true" when running locally via SAM CLI.
    if os.getenv("AWS_SAM_LOCAL", "false").lower() == "true":
        return boto3.client("lambda", endpoint_url="http://host.docker.internal:3001")
    else:
        return boto3.client("lambda")

lambda_client = get_lambda_client()

def orch_lambda(event, context):
    try:
        file_path = extractS3(event) 
        
        if '.json' in file_path and 'docket' in file_path:
            response = lambda_client.invoke(
                FunctionName='SQLDocketIngestFunction',
                InvocationType='RequestResponse',
                Payload=json.dumps({"file_path": file_path}).encode("utf-8")
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps('File not processed - not a docket JSON file')
            }
            
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error processing request: {str(e)}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Unexpected error: {str(e)}')
        }