import json
# import os
import psycopg
import boto3
# from botocore.exceptions import ClientError
from common.utils.ingest_docket import insert_docket

# def get_secret(secret_name):
#     """
#     Retrieve a secret from AWS Secrets Manager

#     Args:
#         secret_name: Name of the secret to retrieve
 
#     Returns:
#         dict: The secret key/value pairs
#     """
#     region_name = os.environ.get('AWS_REGION', 'us-east-1')

#     # Create a Secrets Manager client
#     session = boto3.session.Session()
#     client = session.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )

#     try:
#         # Get the secret value
#         response = client.get_secret_value(SecretId=secret_name)

#         # Decode and parse the secret string JSON
#         if 'SecretString' in response:
#             secret = json.loads(response['SecretString'])
#             return secret
#         else:
#             logger.error("Secret not found in expected format")
#             raise Exception("Secret not found in expected format")

#     except ClientError as e:
#         logger.error(f"Error retrieving secret: {str(e)}")
#         raise e

def handler(event, context):
    """
    Lambda handler that processes data from another Lambda invocation
    and stores it in a PostgreSQL database.
    
    Args:
        event (dict): Contains the payload from the invoking Lambda
        context: Lambda context object
    """
    print("Received event: %s", json.dumps(event))


    
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
        
        if "docket" in s3dict['file_key']:
            insert_docket(file_content)
        
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
    return 0