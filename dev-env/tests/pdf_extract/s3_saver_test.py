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

from lambda_functions.pdf_text_extract.app import handler, extract_text, s3_saver  # Import from app.py

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


def test_s3_saver_saves_file_correctly(s3_mock):
    # Sample content to save
    content = "This is a test file."
    file_stream = BytesIO(content.encode("utf-8"))
    key = "derived-data/APHIS/APHIS-2004-0001/mirrulations/comments_extracted_text/pypdf/APHIS-2004-0001-0005_attachment_1_extracted.txt"

    # Call the s3_saver function
    s3_saver(file_stream, "test-bucket", key)

    # Retrieve the saved file from mock S3 and verify its contents
    response = s3_mock.get_object(Bucket="test-bucket", Key=key)
    saved_content = response["Body"].read().decode("utf-8")
    assert saved_content == content
    
def test_s3_saver_with_binary_content(s3_mock):
    # Binary content to save (simulating image or PDF)
    content = b"binarydatahere"
    file_stream = BytesIO(content)
    key = "derived-data/APHIS/APHIS-2004-0001/mirrulations/comments_extracted_text/pypdf/APHIS-2004-0001-0005_attachment_1_extracted.pdf"

    # Call the s3_saver function
    s3_saver(file_stream, "test-bucket", key)

    # Retrieve the saved file and verify its contents
    response = s3_mock.get_object(Bucket="test-bucket", Key=key)
    saved_content = response["Body"].read()
    assert saved_content == content

def test_s3_saver_with_large_content(s3_mock):
    # Large content to save
    content = "A" * 10**6  # 1MB of "A"s
    file_stream = BytesIO(content.encode("utf-8"))
    key = "derived-data/APHIS/APHIS-2004-0001/mirrulations/comments_extracted_text/pypdf/APHIS-2004-0001-0005_attachment_1_extracted_large.txt"

    # Call the s3_saver function
    s3_saver(file_stream, "test-bucket", key)

    # Retrieve the saved file and verify its contents
    response = s3_mock.get_object(Bucket="test-bucket", Key=key)
    saved_content = response["Body"].read().decode("utf-8")
    assert saved_content == content

def test_s3_saver_with_empty_file(s3_mock):
    # Empty file content
    content = ""
    file_stream = BytesIO(content.encode("utf-8"))
    key = "derived-data/APHIS/APHIS-2004-0001/mirrulations/comments_extracted_text/pypdf/APHIS-2004-0001-0005_attachment_1_extracted_empty.txt"

    # Call the s3_saver function
    s3_saver(file_stream, "test-bucket", key)

    # Retrieve the saved file and verify its contents
    response = s3_mock.get_object(Bucket="test-bucket", Key=key)
    saved_content = response["Body"].read().decode("utf-8")
    assert saved_content == content



