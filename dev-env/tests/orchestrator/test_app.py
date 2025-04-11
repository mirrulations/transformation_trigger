import json
import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch

# Import the functions to be tested - update import path as needed
from lambda_functions.orchestrator.app import extractS3, orch_lambda

# Fixture for mocking AWS credentials
@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    with patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1',
        'SQL_DOCKET_INGEST_FUNCTION': 'SQLDocketIngestFunction',
        'SQL_DOCUMENT_INGEST_FUNCTION': 'SQLDocumentIngestFunction',
        'OPENSEARCH_COMMENT_INGEST_FUNCTION': 'OpenSearchCommentIngestFunction',
        'OPENSEARCH_TEXT_EXTRACT_FUNCTION': 'OpenSearchTextExtractFunction',
        'HTM_SUMMARY_INGEST_FUNCTION': 'HTMSummaryIngestFunction',
    }):
        yield

# Test cases for extractS3 function
def test_extractS3_valid_event():
    """Test extractS3 with a valid S3 event"""
    event = {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': 'test-bucket'
                    },
                    'object': {
                        'key': 'raw-data/path/to/docket_file.json'
                    }
                }
            }
        ]
    }
    
    result = extractS3(event)
    assert result == {
        "bucket": "test-bucket",
        "file_key": "raw-data/path/to/docket_file.json"
    }

def test_extractS3_empty_event():
    """Test extractS3 with an empty event"""
    with pytest.raises(ValueError) as e:
        extractS3(None)
    assert "Event is empty" in str(e.value)

def test_extractS3_invalid_event():
    """Test extractS3 with an event missing required fields"""
    event = {'Records': [{'wrong_format': True}]}
    
    with pytest.raises(ValueError) as e:
        extractS3(event)
    assert "Cannot extract S3 information from event" in str(e.value)

# Test cases for orch_lambda function
@mock_aws
def test_orch_lambda_docket_json(aws_credentials):
    """Test orch_lambda with a docket JSON file"""
    # Create test S3 bucket and object
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    s3.put_object(
        Bucket='test-bucket',
        Key='raw-data/path/to/docket_file.json',
        Body='{"test": "data"}'
    )
    
    # Create a sample S3 event
    event = {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': 'test-bucket'
                    },
                    'object': {
                        'key': 'raw-data/path/to/docket_file.json'
                    }
                }
            }
        ]
    }
    
    # Mock the lambda client invoke method
    with patch('lambda_functions.orchestrator.app.boto3.client') as mock_boto:
        mock_lambda = mock_boto.return_value
        mock_lambda.invoke.return_value = {'StatusCode': 200}
        
        # Call the function
        result = orch_lambda(event, {})
        
        # Verify lambda was called correctly
        mock_boto.assert_called_once_with('lambda')
        expected_payload = json.dumps({
                "bucket": "test-bucket",
                "file_key": "raw-data/path/to/docket_file.json"
        }).encode("utf-8")
        mock_lambda.invoke.assert_called_once_with(
            FunctionName='SQLDocketIngestFunction',
            InvocationType='RequestResponse',
            Payload=expected_payload
        )
        
    # Verify the result
    assert result['statusCode'] == 200
    assert 'Lambda function invoked successfully' in result['body']

@mock_aws
def test_orch_lambda_non_docket_file(aws_credentials):
    """Test orch_lambda with a non-docket file"""
    # Create test S3 bucket and object
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    s3.put_object(
        Bucket='test-bucket',
        Key='raw-data/path/to/regular_file.json',
        Body='{"test": "data"}'
    )
    
    # Create a sample S3 event
    event = {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': 'test-bucket'
                    },
                    'object': {
                        'key': 'raw-data/path/to/regular_file.json'
                    }
                }
            }
        ]
    }
    
    # Call the function
    result = orch_lambda(event, {})
    
    # Verify the result
    assert result['statusCode'] == 404
    assert 'File not processed' in result['body']

def test_orch_lambda_invalid_event(aws_credentials):
    """Test orch_lambda with an invalid event"""
    # Call the function with an empty event
    result = orch_lambda({}, {})
    
    # Verify the result
    assert result['statusCode'] == 400
    assert 'Error processing request' in result['body']

def test_orch_lambda_exception(aws_credentials):
    """Test orch_lambda with an exception being raised"""
    # Create a sample S3 event
    event = {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': 'test-bucket'
                    },
                    'object': {
                        'key': 'raw-data/path/to/docket_file.json'
                    }
                }
            }
        ]
    }
    
    # Mock extractS3 to raise an exception
    with patch('lambda_functions.orchestrator.app.extractS3') as mock_extract:
        mock_extract.side_effect = Exception("Unexpected error")
        
        # Call the function
        result = orch_lambda(event, {})
    
    # Verify the result
    assert result['statusCode'] == 500
    assert 'Unexpected error' in result['body']