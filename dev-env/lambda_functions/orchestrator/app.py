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
  
  #split the file name to get extension
  file_name_split = file_name.split('.')
  file_name_without_extension = file_name_split[0]
  file_extension = file_name_split[1]
  if file_extension == 'json' and 'comment' in file_name_without_extension:
    lambda_client = boto3.client('lambda')
    #invoke the lambda function that extracts entities from the txt file
    lambda_client.invoke(
        FunctionName='SQLDocketIngestFunction',
        InvocationType='RequestResponse',
        Payload=json.dumps(event)
    )
    #return response saying entities extracted and lambda invoked successfully
            # Parse the response
    
    

    
    


  
