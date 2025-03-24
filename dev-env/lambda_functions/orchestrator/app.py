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

    # Retrieve the SQL ingest function's name (or ARN) from the environment
    sql_docket_function = os.environ.get("SQL_DOCKET_INGEST_FUNCTION")
    if not sql_docket_function:
        raise Exception("SQL ingest function name is not set in the environment variables")
    
    pdf_extract_function = os.environ.get("PDF_TEXT_EXTRACT_FUNCTION")
    if not pdf_extract_function:
        raise Exception("PDF text extraction function name is not set in the environment variables")
    

    try:
        s3dict = extractS3(event)
        print(s3dict)

        if '.pdf' in s3dict['file_key'] and 'comment' in s3dict['file_key']:
            print('docket pdf found')
            response = lambda_client.invoke(
                FunctionName=pdf_extract_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }
        elif '.json' in s3dict['file_key'] and 'docket' in s3dict['file_key']:
            print("docket json found!")
            response = lambda_client.invoke(
                FunctionName=sql_docket_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }
        else:
            print('File not processed')
            return {
                'statusCode': 400,
                'body': json.dumps('File not processed - not a docket JSON or PDF')
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
    