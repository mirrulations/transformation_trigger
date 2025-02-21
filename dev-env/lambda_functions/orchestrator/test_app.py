import json
import boto3
import pytest
from moto import mock_aws
from unittest.mock import patch
from .app import orch_lambda  # Assuming this file is in the same folder as app.py

@pytest.fixture
def s3_event():
    """Mock S3 event for a .txt file upload"""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "my-test-bucket"},
                    "object": {"key": "documents/test_file.txt"}
                }
            }
        ]
    }

@pytest.fixture
def s3_event_non_txt():
    """Mock S3 event for a non-txt file upload"""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "my-test-bucket"},
                    "object": {"key": "documents/image.png"}
                }
            }
        ]
    }

@pytest.fixture
def s3_event_missing_key():
    """Mock S3 event with missing required keys"""
    return {"Records": [{}]}  # Missing required 's3' structure

@mock_aws
def test_lambda_invocation(s3_event):
    """Test that the orchestrator correctly invokes the extract_entities Lambda for .txt files"""
    
    # Patch boto3 lambda client to avoid role validation issue
    with patch("boto3.client") as mock_boto_client:
        mock_lambda = mock_boto_client.return_value

        # Mock the response for create_function (bypassing IAM validation)
        mock_lambda.create_function.return_value = {
            "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:extract_entities"
        }

        # Mock invocation response
        mock_lambda.invoke.return_value = {"StatusCode": 202}

        # Invoke the orchestrator lambda
        response = orch_lambda(s3_event, None)

        # Assertions
        assert response["statusCode"] == 200
        assert "Entities extracted and lambda invoked successfully" in response["body"]

        # Ensure Lambda function was invoked
        mock_lambda.invoke.assert_called_once()

@mock_aws
def test_lambda_not_invoked_for_non_txt(s3_event_non_txt):
    """Test that the orchestrator does NOT invoke another Lambda for non-txt files"""
    
    with patch("boto3.client") as mock_boto_client:
        mock_lambda = mock_boto_client.return_value

        # Mock create_function to avoid IAM validation
        mock_lambda.create_function.return_value = {
            "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:extract_entities"
        }

        # Invoke the orchestrator lambda
        response = orch_lambda(s3_event_non_txt, None)

        # Assertions - Since nothing is returned for non-txt files, response should be None
        assert response is None

        # Ensure Lambda function was NOT invoked
        mock_lambda.invoke.assert_not_called()

def test_missing_keys(s3_event_missing_key):
    """Test that an error is raised when event is missing required keys"""
    with pytest.raises(ValueError, match="Missing key in event"):
        orch_lambda(s3_event_missing_key, None)

