# where_test.py
"""
Unit tests for S3 Path Generator functions.
Tests determine_raw_path and determine_derived_path.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from where import extract_agency_docket, determine_raw_path, upload_file, process_file, get_s3_client  

# Function to print test results
def print_test_result(test_name, expected, actual):
    print(f"\nRunning {test_name}...")
    if expected == actual:
        print(f"✅ {test_name} PASSED")
    else:
        print(f"❌ {test_name} FAILED\nExpected: {expected}\nActual:   {actual}")

class TestS3PathGenerator(unittest.TestCase):
    
    def test_extract_agency_docket(self):
        expected = ("EPA", "EPA-2024-12345")
        actual = extract_agency_docket("EPA-2024-12345-0001")
        print_test_result("test_extract_agency_docket (Valid EPA)", expected, actual)
        self.assertEqual(expected, actual)

        expected = ("DHS", "DHS-2023-67890")
        actual = extract_agency_docket("DHS-2023-67890-0010")
        print_test_result("test_extract_agency_docket (Valid DHS)", expected, actual)
        self.assertEqual(expected, actual)

        expected = ("UNKNOWN", "UNKNOWN")
        actual = extract_agency_docket("invalid_file_name")
        print_test_result("test_extract_agency_docket (Invalid File Name)", expected, actual)
        self.assertEqual(expected, actual)

    def test_determine_raw_path(self):
        expected = "Raw_data/EPA/EPA-2024-12345/text-EPA-2024-12345/dockets/EPA-2024-12345-0001.json"
        actual = determine_raw_path("EPA-2024-12345-0001.json", "docket", "json")
        print_test_result("test_determine_raw_path (Docket JSON)", expected, actual)
        self.assertEqual(expected, actual)

        expected = "Raw_data/EPA/EPA-2024-12345/binary-EPA-2024-12345/documents_attachments/EPA-2024-12345-attachment.pdf"
        actual = determine_raw_path("EPA-2024-12345-attachment.pdf", "document", "pdf")
        print_test_result("test_determine_raw_path (Document Attachment PDF)", expected, actual)
        self.assertEqual(expected, actual)

    @patch("where.boto3.client")  # Mock S3 client
    def test_upload_file(self, mock_boto_client):
        print("\nRunning test_upload_file...")

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        bucket_name = "test-bucket"
        file_name = "test_upload.txt"
        s3_path = "Raw_data/EPA/EPA-2024-12345/text/test_upload.txt"

        # Create a test file
        with open(file_name, "w") as f:
            f.write("test upload content")

        upload_file(mock_s3, bucket_name, file_name, s3_path)

        # Verify if put_object and upload_file were called
        mock_s3.put_object.assert_called()
        mock_s3.upload_file.assert_called_with(file_name, bucket_name, s3_path)

        print("✅ test_upload_file PASSED")

        os.remove(file_name)

    @patch("where.boto3.client")  # Mock S3 client
    def test_process_file(self, mock_boto_client):
        print("\nRunning test_process_file...")

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        bucket_name = "test-bucket"
        file_name = "test_process.json"
        file_content = json.dumps({"data": {"type": "documents"}})

        # Create a test file
        with open(file_name, "w") as f:
            f.write(file_content)

        process_file(mock_s3, bucket_name, file_name)

        # Verify S3 upload call
        mock_s3.upload_file.assert_called()

        print("✅ test_process_file PASSED")

        os.remove(file_name)

    @patch("boto3.client")  # Mock S3 client creation
    def test_get_s3_client(self, mock_boto_client):
        print("\nRunning test_get_s3_client...")
        mock_boto_client.return_value = MagicMock()
        client = get_s3_client()
        print(f"Mock S3 Client Created: {'✅ SUCCESS' if client else '❌ FAILURE'}")
        self.assertIsNotNone(client)
        mock_boto_client.assert_called_once_with("s3")

if __name__ == "__main__":
    print("\n===== Running S3 Path Generator Tests (No AWS Credentials Needed) =====")
    unittest.main(argv=[''], exit=False)
