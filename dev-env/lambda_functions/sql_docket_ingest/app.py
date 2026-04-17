import json
import logging
import os
import boto3
from common.ingest import ingest_docket

logger = logging.getLogger(__name__)

try:
    from frdocnum_extract import collect_frdocnums
except ImportError:
    from lambda_functions.sql_docket_ingest.frdocnum_extract import collect_frdocnums


def _queue_federal_ingest_for_payload(file_content: str) -> None:
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError:
        return
    nums = collect_frdocnums(data)
    if not nums:
        return
    fn = os.environ.get("SQL_FEDERAL_DOCUMENT_INGEST_FUNCTION")
    if not fn:
        print(
            "SQL_FEDERAL_DOCUMENT_INGEST_FUNCTION not set; skipping federal register fan-out"
        )
        return
    client = boto3.client("lambda")
    for num in sorted(nums):
        payload = json.dumps({"frdocnum": num}).encode("utf-8")
        client.invoke(FunctionName=fn, InvocationType="Event", Payload=payload)
        print(f"Queued federal register ingest for frdocnum={num!r}")


def handler(event, context):
    """
    Lambda handler that processes a docket.json file when an s3 event contains a docket.json and is passed to the mirrulations bucket. This function is invoked by the orchestrator function and is responsible for ingesting the docket.json contents into SQL database.

    Args:
        event (dict): Contains the payload from the invoking Lambda
        context: Lambda context object
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Handle direct Lambda invocations
        s3dict = event
        print("Data: ", s3dict)
        
        # Get file contents from aws s3 (s3dict is the dictionary containing the bucket and file_key)
        s3 = boto3.client('s3')
        file_obj = s3.get_object(Bucket=s3dict['bucket'], Key=s3dict['file_key'])
        file_content = file_obj['Body'].read().decode('utf-8')
        print("File content Retrieved!")

        if not file_content:
            raise ValueError("File content is empty")

        if 'docket' in s3dict['file_key']:
            #set environment variables and ingest docket
            print("ingesting")
            ingest_docket(file_content)
            print("ingest complete!")
            _queue_federal_ingest_for_payload(file_content)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data processed successfully'})
        }
        
    except Exception as e:
        logger.exception("SQLDocketIngest failed")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
