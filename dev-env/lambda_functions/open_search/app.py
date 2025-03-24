import json
import os
import psycopg
import boto3
from botocore.exceptions import ClientError
from common.ingest import ingest_comment

def get_secret(secret_name):
   """
   Retrieve a secret from AWS Secrets Manager
   Args:
       secret_name: Name of the secret to retrieve
   Returns:
       dict: The secret key/value pairs
   """
   region_name = os.environ.get('AWS_REGION', 'us-east-1')

   # Create a Secrets Manager client
   session = boto3.session.Session()
   client = session.client(
       service_name='secretsmanager',
       region_name=region_name
   )

   try:
       # Get the secret value
       response = client.get_secret_value(SecretId=secret_name)

       # Decode and parse the secret string JSON
       if 'SecretString' in response:
           secret = json.loads(response['SecretString'])
           return secret
       else:
           print("Secret not found in expected format")
           raise Exception("Secret not found in expected format")

   except ClientError as e:
       print(f"Error retrieving secret: {str(e)}")
       raise e
   
def get_db_connection():
   """
   Retrieve a connection to the PostgreSQL database
   """
   secret_name = os.environ.get('DB_SECRET_NAME')
   secret = get_secret(secret_name)

   os.putenv("OPENSEARCH_HOST",secret['host'])
   os.putenv("OPENSEARCH_PORT",secret['port'])

def handler(event, context):
   """
   Lambda handler that processes data from another Lambda invocation
   and indexes it in OpenSearch.
   
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

       if 'comment' in s3dict['file_key']:
           #set environment variables
           get_db_connection()
           print("ingesting")
           ingest_comment(file_content)
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