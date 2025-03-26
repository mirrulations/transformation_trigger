import json
import boto3
from common.ingest import ingest_document

def handler(event, context):
    """
    Lambda handler that processes data from another Lambda invocation
    and stores it in a PostgreSQL database.
    
    Args:
        event (dict): Contains the payload from the invoking Lambda
        context: Lambda context object
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        # Handle direct Lambda invocations
        s3dict = event
        print("Data: ", s3dict)
        
        # Get file contents from aws s3 (s3dict is the dictionary containing the bucket and file_key)
        s3 = boto3.client('s3')
        file_obj = s3.get_object(Bucket=s3dict['bucket'], Key=s3dict['file_key'])
        file_content = file_obj['Body'].read().decode('utf-8')
        print("File content Retrieved!")

        if not file_content:
            raise ValueError("File content is empty")

        if 'document' in s3dict['file_key']:
            #set environment variables and ingest document
            print("ingesting")
            ingest_document(file_content)
            print("ingest complete!")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data processed successfully'})
        }
        
    except Exception as e:
        # logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
