import json
import boto3
from pypdf import PdfReader as Re

def extract_text(filename):
    file = Re(filename)
    with open("output.txt", "w") as f:
        for page in file.pages:
            f.write(page.extract_text())

def handler(event, context):
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
        # extract the text, we know it is a pdf file from the checks in the orchestrator function
        extract_text(file_content)


        if not file_content:
            raise ValueError("File content is empty")

        return {
            'statusCode': 200,

            'body': json.dumps({'message': 'Data processed successfully'})
        }
        
    except Exception as e:
        # logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }