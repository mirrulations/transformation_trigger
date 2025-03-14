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

    # Construct the s3 dictionary
    s3dict = {
        "bucket": bucket_name,
        "file_key": object_key
    }
    
    return s3dict

def get_lambda_client():
    # AWS_SAM_LOCAL is set to "true" when running locally via SAM CLI.
    if os.getenv("AWS_SAM_LOCAL", "false").lower() == "true":
        return boto3.client("lambda", endpoint_url="http://host.docker.internal:3001")
    else:
        return boto3.client("lambda")


def orch_lambda(event, context):
    lambda_client = get_lambda_client()

    try:
        s3dict = extractS3(event)

        if '.json' and 'docket' in s3dict['file_key']:
            response = lambda_client.invoke(
                FunctionName='SQLDocketIngestFunction',
                InvocationType='RequestResponse',
                Payload=json.dumps({"s3dict": s3dict}).encode("utf-8")
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
    