import json
import boto3
from common.ingest import ingest_comment_opensearch


def handler(event, context):
   """
   Lambda handler that processes a comment.json file when an s3 event contains a comment.json and is passed to the mirrulations bucket. This function is invoked by the orchestrator function and is responsible for ingesting the comment.json file into OpenSearch database.  
   
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

       if not file_content:
           raise ValueError("File content is empty")

       if 'comments' in s3dict['file_key']:
           #set environment variables and ingest comment
           print("ingesting")
           ingest_comment_opensearch(file_content)
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