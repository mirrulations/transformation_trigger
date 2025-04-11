import json
import boto3
from moto import mock_aws
import pytest
import sys
from unittest.mock import MagicMock
import os

# Mock the imports before importing the handler
sys.modules['common.ingest'] = MagicMock()
sys.modules['common.ingest'].ingest_summary = MagicMock()

# import the handler
from lambda_functions.sql_htm_summary.app import handler

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def mock_s3_setup():
    """Fixture to set up a mock S3 environment"""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        s3.create_bucket(Bucket=bucket_name)
        yield s3, bucket_name

def upload_file(s3, bucket_name, file_key, file_content):
    """Helper function to upload a file to the mock S3 bucket"""
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=file_content)

def test_handler_valid_summary(mock_s3_setup):
    """Test with a valid SUMMARY section"""
    s3, bucket_name = mock_s3_setup
    file_key = "raw-data/folder/docket-12345/test-file.htm"  # Updated file_key format
    file_content = """
    SUMMARY: This is a valid summary. It provides an overview of the document.

    DATES: This is the dates section.
    """
    upload_file(s3, bucket_name, file_key, file_content)

    event = {"bucket": bucket_name, "file_key": file_key}
    response = handler(event, None)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["data"]["summary_text"] == "This is a valid summary. It provides an overview of the document."
    assert response_body["data"]["docket_id"] == "docket-12345"

def test_handler_no_summary(mock_s3_setup):
    """Test with no SUMMARY section"""
    s3, bucket_name = mock_s3_setup
    file_key = "raw-data/folder/docket-67890/test-file.htm"  # Updated file_key format
    file_content = """
    This is a test file without a summary.

    DATES: This is the dates section.
    """
    upload_file(s3, bucket_name, file_key, file_content)

    event = {"bucket": bucket_name, "file_key": file_key}
    response = handler(event, None)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body.get("summary") is None
    assert response_body["data"]["docket_id"] == "docket-67890"

def test_handler_summary_with_page_pattern(mock_s3_setup):
    """Test with SUMMARY section containing page pattern"""
    s3, bucket_name = mock_s3_setup
    file_key = "raw-data/folder/docket-13579/test-file.htm"  # Updated file_key format
    file_content = """
    SUMMARY: This is the first page of the summary.

    [[Page 1]]
    
    The summary continues here.

    DATES: This is the dates section.
    """
    upload_file(s3, bucket_name, file_key, file_content)

    event = {"bucket": bucket_name, "file_key": file_key}
    response = handler(event, None)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["data"]["summary_text"] == "This is the first page of the summary. The summary continues here."
    assert response_body["data"]["docket_id"] == "docket-13579"

def test_handler_summary_with_extra_whitespace(mock_s3_setup):
    """Test with SUMMARY section containing extra whitespace"""
    s3, bucket_name = mock_s3_setup
    file_key = "raw-data/folder/docket-24680/test-file.htm"  # Updated file_key format
    file_content = """
    SUMMARY:     This is a summary with extra whitespace.  

    DATES: This is the dates section.
    """
    upload_file(s3, bucket_name, file_key, file_content)

    event = {"bucket": bucket_name, "file_key": file_key}
    response = handler(event, None)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["data"]["summary_text"] == "This is a summary with extra whitespace."
    assert response_body["data"]["docket_id"] == "docket-24680"

