import json
import boto3
from common.ingest import ingest_federal_document

def handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    try:
        s3dict = event
        print("Data: ", s3dict)

        s3 = boto3.client('s3')
        file_obj = s3.get_object(Bucket=s3dict['bucket'], Key=s3dict['file_key'])
        file_content = file_obj['Body'].read().decode('utf-8')
        print("File content Retrieved!")

        if not file_content:
            raise ValueError("File content is empty")

        print("Ingesting federal register document...")
        ingest_federal_document(file_content)
        print("Ingest complete!")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data processed successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }