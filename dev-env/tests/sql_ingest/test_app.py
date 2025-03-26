import json
import boto3
import pytest
from unittest.mock import patch, MagicMock
import moto
import sys
import os

# Mock the imports before importing the handler
sys.modules['common.ingest'] = MagicMock()
sys.modules['common.ingest'].ingest_docket = MagicMock()
sys.modules['psycopg'] = MagicMock()

# import the handler
from lambda_functions.sql_docket_ingest.app import handler

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def s3(aws_credentials):
    with moto.mock_aws():
        yield boto3.client('s3', region_name='us-east-1')

@pytest.fixture
def mock_s3_bucket(s3):
    s3.create_bucket(Bucket='test-bucket')
    return s3

@pytest.fixture
def sample_docket_json():
    """Sample docket JSON data"""
    return json.dumps({
        "data": {
            "id": "TEST-2023-0001",
            "links": {
                "self": "https://api.example.com/dockets/TEST-2023-0001"
            },
            "attributes": {
                "agencyId": "TEST",
                "category": "Proposed Rule",
                "docketType": "Rulemaking",
                "effectiveDate": "2023-05-01T00:00:00Z",
                "field1": "Value 1",
                "field2": "Value 2",
                "modifyDate": "2023-04-15T00:00:00Z",
                "organization": "Test Organization",
                "petitionNbr": "P-001",
                "program": "Test Program",
                "rin": "0000-AA00",
                "shortTitle": "Test Docket",
                "subType": "SubType1",
                "subType2": "SubType2",
                "title": "Test Docket Full Title"
            }
        }
    })

def test_handler_with_docket_file(mock_s3_bucket, sample_docket_json):
    """Test the handler function with a docket file."""
    # Upload a sample docket file to the S3 bucket
    mock_s3_bucket.put_object(
        Bucket='test-bucket',
        Key='docket_TEST-2023-0001.json',
        Body=sample_docket_json
    )
    
    # Mock event data
    event = {
        'bucket': 'test-bucket',
        'file_key': 'docket_TEST-2023-0001.json'
    }
    
    # Mock the ingest_docket function
    with patch('common.ingest.ingest_docket') as mock_ingest:
        # Execute the handler
        response = handler(event, {})
        
        # Assert that ingest_docket was called with the correct data
        mock_ingest.assert_called_once()
        
        # Check the handler returned the expected response
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['message'] == 'Data processed successfully'

def test_handler_with_non_docket_file(mock_s3_bucket):
    """Test the handler with a non-docket file"""
    # Upload a non-docket file
    mock_s3_bucket.put_object(
        Bucket='test-bucket',
        Key='document_123.json',
        Body=json.dumps({"test": "data"})
    )
    
    # Mock event data
    event = {
        'bucket': 'test-bucket',
        'file_key': 'document_123.json'
    }
    
    # Mock the ingest functions
    with patch('common.ingest.ingest_docket') as mock_ingest:
        # Execute the handler
        response = handler(event, {})
        
        # Assert ingest_docket was NOT called
        mock_ingest.assert_not_called()
        
        # Check the handler returned the expected response
        assert response['statusCode'] == 200

def test_handler_with_empty_file(mock_s3_bucket):
    """Test the handler with an empty file"""
    # Upload an empty file
    mock_s3_bucket.put_object(
        Bucket='test-bucket',
        Key='docket_empty.json',
        Body=''
    )
    
    # Mock event data
    event = {
        'bucket': 'test-bucket',
        'file_key': 'docket_empty.json'
    }
    
    # Execute the handler and expect an error
    with patch('common.ingest.ingest_docket') as mock_ingest:
        response = handler(event, {})
        
        # Check error response
        assert response['statusCode'] == 500
        assert 'error' in json.loads(response['body'])
        assert 'File content is empty' in json.loads(response['body'])['error']

def test_handler_with_invalid_bucket(aws_credentials):
    """Test the handler with an invalid bucket"""
    # Create a new S3 client with moto
    with moto.mock_aws():
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        # Don't create any buckets
        
        # Mock event data with non-existent bucket
        event = {
            'bucket': 'non-existent-bucket',
            'file_key': 'docket_123.json'
        }
        
        # Execute the handler and expect an error
        with patch('common.ingest.ingest_docket') as mock_ingest:
            response = handler(event, {})
            
            # Check error response
            assert response['statusCode'] == 500
            assert 'error' in json.loads(response['body'])