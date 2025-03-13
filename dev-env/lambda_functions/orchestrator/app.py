import boto3
import json
import os

# extract
def extractS3(event):
    if event == None:
        raise ValueError("Event is empty")
    
    if event['Records'][0]['s3']['bucket']['name'] not in event:
        raise ValueError("Bucket/path not located in the S3 event")
    if event['Records'][0]['s3']['object']['key'] not in event:
        raise ValueError("Key not located in the S3 event:")
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
       
    # Construct the file path
    file_path = f"s3://{bucket_name}/{object_key}"
    
    return file_path
  
def orch_lambda(event, context):
    try:
        file_path = extractS3(event) 
    except KeyError as e:
        raise ValueError(f"Missing key in event: {e}")


    try:
        if '.json' in file_path and 'docket' in file_path:
            lambda_client = boto3.client('lambda')
            #invoke the lambda function that extracts entities from the txt file
            lambda_client.invoke(
                FunctionName='SQLDocketIngestFunction',
                InvocationType='RequestResponse',
                Payload=file_path
        )
        elif '.json' in file_path and 'comment' in file_path:
            lambda_client.boto3.client('lambda')
            lambda_client.invoke(
                FunctionName='OSCommentIngestFunction',
                InvocationType='RequestResponse',
                Payload=file_path
            )
    except:
        raise ValueError("Error invoking Lambda function")