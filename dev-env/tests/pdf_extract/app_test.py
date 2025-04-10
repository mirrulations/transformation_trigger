import pytest
import boto3
from moto import mock_aws
import os
import sys
from unittest.mock import patch, MagicMock
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

# Mock the imports before importing the handler
sys.modules['common.ingest'] = MagicMock()
sys.modules['common.ingest'].ingest_extracted_text = MagicMock()
sys.modules['psycopg'] = MagicMock()

from lambda_functions.pdf_text_extract.app import handler, extract_text  # Import from app.py

# Fixture to mock AWS credentials
@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Fixture to mock the S3 environment using Moto
@pytest.fixture(scope="function")
def s3_mock(aws_credentials):
    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket="test-bucket")
        yield s3

# Fixture to mock the Lambda environment using Moto
@pytest.fixture(scope="function")
def mock_lambda_client():
    with mock_aws():
        lambda_client = boto3.client("lambda", region_name="us-east-1")

        # Create mock Lambda function for PDF text extraction
        lambda_client.create_function(
            FunctionName="PDFTextExtractFunction",
            Runtime="python3.8",
            Role="role",
            Handler="handler",
            Code={"ZipFile": b"fakezipcontent"},
            Timeout=60,
        )
        yield lambda_client

# Helper function to create a valid PDF content
def create_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Fake PDF Content")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


# raw-data/APHIS/APHIS-2022-0055/binary-APHIS-2022-0055/comments_attachments/APHIS-2022-0055-0002_attachment_1.pdf
# event = {
    # "bucket": bucket_name,
    # "file_key": object_key
# }

#test for handler function
def test_pdf_extractor_handler(s3_mock):
    pdf_content = create_pdf()
    bucket_name = "test-bucket"
    file_key = "raw-data/APHIS/APHIS-2022-0055/binary-APHIS-2022-0055/comments_attachments/APHIS-2022-0055-0002_attachment_1.pdf"
    
    # Upload the PDF to the mock S3 bucket
    s3_mock.put_object(Bucket=bucket_name, Key=file_key, Body=pdf_content)
    event = {
     "bucket": 'test-bucket',
     "file_key": file_key
 }
    response = handler(event, None)
    assert response['statusCode'] == 200
    

    
    
    