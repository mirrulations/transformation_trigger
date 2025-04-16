import boto3
import json
import os


def extractS3(event):
    """
    extractS3 function to extract S3 bucket name and object key from the event.
    It handles both direct S3 events and wrapped SNS events.
    It raises a ValueError if the event is empty or if the S3 information cannot be extracted.
    """
    if not event:
        raise ValueError("Event is empty")

    # Check if event is wrapped by SNS
    record = event['Records'][0]
    if 'Sns' in record:
        # Parse the inner SNS message, which is a JSON string
        message = json.loads(record['Sns']['Message'])
    else:
        message = event

    try:
        bucket_name = message['Records'][0]['s3']['bucket']['name']
        object_key = message['Records'][0]['s3']['object']['key']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Cannot extract S3 information from event: {e}")

    return {
        "bucket": bucket_name,
        "file_key": object_key
    }

def get_lambda_client():
    # AWS_SAM_LOCAL is set to "true" when running locally via SAM CLI.
    if os.getenv("AWS_SAM_LOCAL", "false").lower() == "true":
        return boto3.client("lambda", endpoint_url="http://host.docker.internal:3001")
    else:
        return boto3.client("lambda")


def orch_lambda(event, context):
    """
    The def orch_lambda function is the main entry point for the Lambda function.
    def orch_lambda(event, context) processes incoming S3 events, extracts the relevant information, and invokes other Lambda functions based on the file type. The lambda function is designed to handle various file types, and is very easily extensible to add more file types in the future. 
    """
    
    lambda_client = get_lambda_client()

    # Retrieve the SQL ingest function's name (or ARN) from the environment
    sql_docket_function = os.environ.get("SQL_DOCKET_INGEST_FUNCTION")
    if not sql_docket_function:
        raise Exception("SQL ingest function name is not set in the environment variables")
    sql_document_function = os.environ.get("SQL_DOCUMENT_INGEST_FUNCTION")
    if not sql_document_function:
        raise Exception("SQL ingest function name is not set in the environment variables")
    opensearch_function = os.environ.get("OPENSEARCH_COMMENT_INGEST_FUNCTION")
    if not opensearch_function:
        raise Exception("OpenSearch ingest function name is not set in the environment variables")
    htm_summary_function = os.environ.get("HTM_SUMMARY_INGEST_FUNCTION")
    if not htm_summary_function:
        raise Exception("HTM summary function name is not set in the environment variables")
    opensearch_text_extract_function = os.environ.get("OPENSEARCH_TEXT_EXTRACT_FUNCTION")
    if not opensearch_text_extract_function:
        raise Exception("OpenSearch text extract function name is not set in the environment variables")

    

    try:
        s3dict = extractS3(event)
        print(s3dict)
        print("Bucket: ", s3dict['bucket'])
        print("File Key: ", s3dict['file_key'])

        # Add filter: only process files under the "raw-data/" folder.
        if not s3dict['file_key'].startswith("raw-data/"):
            print("File not in raw-data folder. Skipping processing.")
            return {
                'statusCode': 200,
                'body': json.dumps("File not processed - not in raw-data folder")
            }

        if  s3dict['file_key'].endswith('.json') and 'docket' in s3dict['file_key']:

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
            
        elif s3dict['file_key'].endswith('.json') and 'document' in s3dict['file_key']:

            print("document json found!")
            response = lambda_client.invoke(
                FunctionName=sql_document_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }
        elif s3dict['file_key'].endswith('.pdf') and 'comments_attachments' in s3dict['file_key']:
            print("pdf file found!")
            response = lambda_client.invoke(
                FunctionName=opensearch_text_extract_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }  
        elif s3dict['file_key'].endswith('.json') and 'comments' in s3dict['file_key']:

            print("comment json found!")
            response = lambda_client.invoke(
                FunctionName=opensearch_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )

            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }
        elif s3dict['file_key'].endswith('.htm'):
            print("htm file found!")
            response = lambda_client.invoke(
                FunctionName=htm_summary_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Lambda function invoked successfully')
            }
            
        else:
            print("File not processed")
            return {
                'statusCode': 404,
                'body': json.dumps('File not processed')
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
    