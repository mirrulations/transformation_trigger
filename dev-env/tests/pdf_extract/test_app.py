import boto3
import pytest
import moto
import json
import sys
import os

print("Current sys.path:")
print("\n".join(sys.path))

print("Expected path to lambda_functions:")
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lambda_functions/')))

@pytest.fixture
def mock_s3():
    with moto.mock_s3():
        # Set up the mock S3 bucket
        s3 = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'fake-bucket'
        s3.create_bucket(Bucket=bucket_name)

        # Upload the test PDF file
        example_pdf_path = '../assets/test-attachment.pdf'
        with open(example_pdf_path, 'rb') as f:
            s3.put_object(Bucket=bucket_name, Key='test-attachment.pdf', Body=f.read())

        yield bucket_name

def test_pdf_text_extraction(mock_s3):
    # Prepare the event payload
    event = {
        "bucket": mock_s3,
        "key": "test-attachment.pdf"
    }

    # Call the imported Lambda function directly
    response = pdf_text_extract(event, None)

    # Assert the Lambda function processed the PDF successfully
    assert response['statusCode'] == 200
    assert 'body' in response
    body = json.loads(response['body'])
    assert 'message' in body
    assert body['message'] == 'PDF processed successfully'

    # Additional assertions for text extraction (if applicable)
    # Example: Check if extracted text contains expected content
    # assert 'Expected Text' in body.get('extracted_text', '')