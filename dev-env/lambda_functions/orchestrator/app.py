import boto3
import json
import os



def orch_lambda(event, context):
  try:
      bucket_name = event['Records'][0]['s3']['bucket']['name']
      object_key = event['Records'][0]['s3']['object']['key']
  except KeyError as e:
      raise ValueError(f"Missing key in event: {e}")
    
  # Construct the file path
  file_path = f"s3://{bucket_name}/{object_key}"
    
  # Extract entities from file path
  file_name = os.path.basename(object_key)
  directory = os.path.dirname(object_key)
    
  # Print or use the extracted entities
  print(f"File name: {file_name}")
  print(f"Directory: {directory}")
  
