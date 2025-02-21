import boto3
import json

def extract_entities(event, context):
    s3 = boto3.client('s3')
    
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        
        # Get the object from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        content = response['Body'].read().decode('utf-8')
        
        # Extract entities from the content (this is a placeholder, implement your own logic)
        entities = extract_entities_from_text(content)
        
        # Log the extracted entities
        print(f"Extracted entities: {entities}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Extracted entities: {entities}")
        }
    except Exception as e:
        print(f"Error extracting entities: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error extracting entities: {e}")
        }

def extract_entities_from_text(text):
    # Placeholder function to extract entities from text
    # Implement your own logic here
    return text.split()  # Example: split text into words as entities