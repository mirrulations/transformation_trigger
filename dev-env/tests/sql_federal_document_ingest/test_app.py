import json
from unittest.mock import MagicMock, patch

import pytest
import sys

sys.modules["common.ingest"] = MagicMock()
sys.modules["common.ingest"].ingest_federal_document = MagicMock()

from lambda_functions.sql_federal_document_ingest import app as fed_app


def test_handler_fetches_when_frdocnum_in_event():
    with patch.object(fed_app, "fetch_document_json", return_value='{"document":{}}') as fetch:
        with patch("lambda_functions.sql_federal_document_ingest.app.ingest_federal_document") as ingest:
            event = {"frdocnum": "2024-10001"}
            r = fed_app.handler(event, None)
            fetch.assert_called_once_with("2024-10001")
            ingest.assert_called_once_with('{"document":{}}')
            assert r["statusCode"] == 200


def test_handler_reads_s3_when_bucket_and_key():
    with patch("lambda_functions.sql_federal_document_ingest.app.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b'{"x":1}')),
        }
        with patch("lambda_functions.sql_federal_document_ingest.app.ingest_federal_document") as ingest:
            event = {"bucket": "b", "file_key": "raw-data/x/federal_register/y.json"}
            r = fed_app.handler(event, None)
            mock_s3.get_object.assert_called_once_with(Bucket="b", Key="raw-data/x/federal_register/y.json")
            ingest.assert_called_once_with('{"x":1}')
            assert r["statusCode"] == 200
