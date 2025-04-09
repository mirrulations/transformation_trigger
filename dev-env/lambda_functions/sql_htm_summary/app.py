import json
import boto3
from bs4 import BeautifulSoup
import re
from common.ingest import ingest_summary

def handler(event, context):
    """
    Lambda handler that processes an .htm file from S3,
    extracts the 'SUMMARY' section from its content,
    and prepares it for ingestion.
    
    Args:
        event (dict): Contains the payload with 'bucket' and 'file_key'
        context: Lambda context object
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        # Validate input
        if "bucket" not in event or "file_key" not in event:
            raise ValueError("Event must contain 'bucket' and 'file_key' fields.")

        s3dict = event
        print("Data: ", s3dict)

        s3 = boto3.client('s3')
        file_obj = s3.get_object(Bucket=s3dict['bucket'], Key=s3dict['file_key'])
        file_content = file_obj['Body'].read().decode('utf-8')
        print("File content retrieved!")

        if not file_content:
            raise ValueError("File content is empty")

        file_key = s3dict['file_key']
        print(f"Processing file_key: {file_key}")

        # Extract the docket-id from the file key
        file_key_parts = file_key.split('/')
        if len(file_key_parts) > 1:
            docket_id = file_key_parts[2]
            print(f"Extracted docket_id: {docket_id}")
            
        else:
            raise ValueError("Invalid file key format. Unable to extract docket-id.")

        if file_key.lower().endswith('.htm'):
            # Use BeautifulSoup to parse the HTML content
            soup = BeautifulSoup(file_content, 'html.parser')

            # Extract the plain text from the HTM
            plain_text = soup.get_text()
            print("Extracted plain text from HTM.")

            # Find the "SUMMARY:" section
            summary_start = plain_text.find("SUMMARY:")
            if summary_start != -1:
                # Extract the text starting from "SUMMARY:"
                summary_text = plain_text[summary_start + len("SUMMARY:"):]

                # Remove the page pattern and its surrounding blank lines
                summary_text = re.sub(r'\n?\s*\[\[Page \d+\]\]\s*\n?', ' ', summary_text)

                # Stop at the first empty line
                empty_line_match = re.search(r'\n\s*\n', summary_text)
                if empty_line_match:
                    summary_text = summary_text[:empty_line_match.start()].strip()

                # Clean up extra spaces in the extracted summary
                summary_text = re.sub(r'\s+', ' ', summary_text).strip()

                print("Extracted Summary:")
                print(summary_text)
            else:
                summary_text = None
                print("No SUMMARY section found in the file.")

            # Create a dictionary with docket-id and summary_text
            data = {
                "docket_id": docket_id,
                "summary_text": summary_text
            }

            # Pass the dictionary to the ingest_htm_summary function (when implemented)
            print("Ingesting summary...")
            ingest_summary(data)
            print("Summary ingestion completed.")

        else:
            raise ValueError("Provided file is not an HTM or HTML file.")

        return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Summary extracted successfully', 'data': data})
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

