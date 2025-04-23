import json
import boto3
import io
from pypdf import PdfReader as Re
from common.ingest import ingest_extracted_text


def extract_text(file_stream):
    """Extract text from a PDF file stream and return as a string."""
    try:
        reader = Re(file_stream)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return {
            'statusCode': 422,
            'body': json.dumps({'error': str(e)})
        } 
    extracted_text = " ".join([page.extract_text().replace("\n", " ") for page in reader.pages if page.extract_text()])
    return extracted_text


def s3_saver(file_stream, bucket, file_key, s3):
    """Save the file stream to S3."""
    print("starting s3saver client")
    try:
        print("Uploading file to S3...")
        s3.upload_fileobj(file_stream, bucket, file_key)
        print(f"File saved to S3 bucket {bucket} with key {file_key}")
    except Exception as e:
        print(f"Error saving file to S3: {e}")
        return {
            'statusCode': 422,
            'body': json.dumps({'error': str(e)})
        }
        

def handler(event, context):
    """
    Lambda handler that processes a PDF file when an s3 event contains a PDF and is passed to the mirrulations bucket. This function is invoked by the orchestrator function and is responsible for extracting text from the PDF file and ingesting it into OpenSearch database.
    
    Args:
        event (_type_): _description_
        context (_type_): _description_
        
    Returns:
        _type_: _description_
    """
    
    print("Received PDF file in event.")
    print(f"Received event: {json.dumps(event)}")

    try:
        # Retrieve PDF file from S3 using the event data
        s3 = boto3.client('s3')
        file_obj = s3.get_object(Bucket=event['bucket'], Key=event['file_key'])
        file_content = file_obj['Body'].read()

        # Step 2: Extract text from the PDF
        extracted_text = extract_text(io.BytesIO(file_content))

        if not extracted_text:
            raise ValueError("Extracted text is empty")

        # Extract docketId, commentId, and attachmentId from the file_key
        file_key = event['file_key']
        parts = file_key.split('/')

        # Extract docketId, commentId, and attachmentId based on file structure
        bucket = event['bucket']  # Assuming bucket is always in this position (e.g. "mirrulations")
        agency = parts[1]  # Assuming agency is always in this position (e.g. "APHIS")
        docketId = parts[2]  # Assuming docketId is always in this position (e.g. "APHIS-2022-0055")
        filename = parts[-1]  # Get the filename
        commentId = filename.split('_')[0]  # Extract commentId (e.g. "APHIS-2022-0055-0002" from "APHIS-2022-0055-0002_attachment_1.pdf")
        attachmentId = commentId + "-" + filename.split('_')[-1].replace('.pdf', '')  # Extract attachmentId (e.g. "APHIS-2022-0055-0002-1" from "APHIS-2022-0055-0002_attachment_1.pdf")

        # Construct the dictionary with the extracted text and other necessary data
        data = {
            "extractedText": extracted_text,
            "docketId": docketId,  # Extracted from the file_key
            "commentId": commentId,  # Extracted from the file_key
            "attachmentId": attachmentId,   # Extracted from the file_key
            "extractedMethod": "pypdf",  # Indicating the library used for extraction            
        }
        
        print(f"Extracted data: {data}")

        # Check if the event is related to comments_attachments
        if 'comments_attachments' in event['file_key']:
            txt_filename = filename.replace('.pdf', '_extracted.txt')
            txt_key = f"derived-data/{agency}/{docketId}/mirrulations/extracted_txt/comments_extracted_text/pypdf/{txt_filename}"
            s3_saver(io.BytesIO(extracted_text.encode('utf-8')), bucket, txt_key, s3)
            # Ingest the extracted text and the prepared data
            print("Ingesting extracted text...")
            ingest_extracted_text(data)  # Pass the dictionary to the ingest function
            print("Ingestion complete!")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data processed successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }