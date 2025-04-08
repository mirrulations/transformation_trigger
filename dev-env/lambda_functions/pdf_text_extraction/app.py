import json
import boto3
from common.ingest import ingest_pdf_extraction
from pyPDF2 import PdfReader
from io import BytesIO





# Step 1. handler for the lambda function
def handler(event, context):
    """
    Lambda handler that processes data from another Lambda invocation
    and stores it in a PostgreSQL database.
    
    Args:
        event (dict): Contains the payload from the invoking Lambda
        context: Lambda context object
    """

    try:
        s3dict = event
        print("Data: ", s3dict)
        
        # Get file contents 
        s3 = boto3.client('s3')
        file_obj = s3.get_object(Bucket=s3dict['bucket'], Key=s3dict['file_key'])
        file_content = file_obj['Body'].read()
        
        if not file_content:
            raise ValueError("File content is empty")
        #call text extraction function
        print("Extracting text from PDF")
        extracted_text = extract_text_from_pdf(file_content)
        print("Text extracted from PDF")
        
        #write extracted text to s3
        output_key = s3dict['file_key'].replace('.pdf', '_extracted.txt')
        s3.put_object(Bucket=s3dict['bucket'], Key=output_key, Body=extracted_text)
        print("Extracted text written to S3")
  
        # Ingest extracted text into the database
        print("Ingesting extracted text into database")
        ingest_pdf_extraction(extracted_text, s3dict['file_key'])
        print('Ingest Complete')
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data processed successfully'})
        }
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

#Extract the text from the PDF file
def extract_text_from_pdf(file_content):
  try:
    extracted_text = ""
    reader = PdfReader(BytesIO(file_content))
    for page in reader.pages:
        extracted_text += page.extract_text()
    return extracted_text
  except Exception as e:
    print(f"Error extracting text from PDF: {str(e)}")
  
  
  
    
  
    
    
    


