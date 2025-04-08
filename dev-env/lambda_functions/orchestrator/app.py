import boto3
import json
import os

def extractS3(event):
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
    lambda_client = get_lambda_client()

    # Retrieve the SQL ingest function's name (or ARN) from the environment
    sql_docket_function = os.environ.get("SQL_DOCKET_INGEST_FUNCTION")
    if not sql_docket_function:
        raise Exception("SQL ingest function name is not set in the environment variables")
    sql_document_function = os.environ.get("SQL_DOCUMENT_INGEST_FUNCTION")
    if not sql_document_function:
        raise Exception("SQL ingest function name is not set in the environment variables")
    opensearch_function = os.environ.get("OPENSEARCH_INGEST_FUNCTION")
    if not opensearch_function:
        raise Exception("OpenSearch ingest function name is not set in the environment variables")
    

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
            
        elif '.json' in s3dict['file_key'] and 'document' in s3dict['file_key']:
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
        elif '.json' in s3dict['file_key'] and 'comments' in s3dict['file_key']:
            print("comment json found!")
            response = lambda_client.invoke(
                FunctionName=opensearch_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )
        # process attachments from comments (e.g. pdf, docx)
        elif '.pdf' in s3dict['file_key'] and 'comments' in s3dict['file_key']:
            print("pdf attachment found!")
            response = lambda_client.invoke(
                FunctionName=pdf_text_extraction_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(s3dict)
            )
            
        else:
            print("File not processed")
            return {
                'statusCode': 200,
                'body': json.dumps('File not processed - not a docket JSON or document JSON file')
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
    