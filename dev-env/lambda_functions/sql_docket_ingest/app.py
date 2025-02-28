import psycopg
import json
import logger
import boto3
import os
from botocore.exceptions import ClientError

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
            logger.error("Secret not found in expected format")
            raise Exception("Secret not found in expected format")
   
    except ClientError as e:
        logger.error(f"Error retrieving secret: {str(e)}")
        raise e

def handler(event, context):
    """
    Lambda handler that processes data from another Lambda invocation
    and stores it in a PostgreSQL database.
    
    Args:
        event (dict): Contains the payload from the invoking Lambda
        context: Lambda context object
    """
    logger.info("Received event: %s", json.dumps(event))
    
    # try:
    #     # Extract data from the event
    #     # If the event comes from a direct Lambda invocation, it will be the payload you provided
    #     # If it comes from an S3 event or other service, structure will be different
    #     if 'Records' in event:
    #         # Handle S3 or SQS type events
    #         logger.info("Processing event with Records")
    #         # Example: data = process_records(event['Records'])
    #         data = event['Records']
    #         print(data)
    #     else:
    #         # Handle direct Lambda invocations
    #         logger.info("Processing direct Lambda invocation")
    #         data = event
        
        # Connect to the PostgreSQL database
    #     # Use environment variables for connection details
    #     conn = get_db_connection()
        
    #     # Process data and insert into database
    #     result = insert_data_to_db(conn, data)
        
    #     # Close the connection
    #     conn.close()
        
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps({'message': 'Data processed successfully', 'result': result})
    #     }
        
    # except Exception as e:
    #     logger.error(f"Error processing event: {str(e)}")
    #     return {
    #         'statusCode': 500,
    #         'body': json.dumps({'error': str(e)})
    #     }
    return 0