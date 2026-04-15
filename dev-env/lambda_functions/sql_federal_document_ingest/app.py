import json
import boto3
from common.ingest import ingest_federal_document, ingest_cfr_part

try:
    from federal_register_fetch import fetch_document_json
except ImportError:
    from lambda_functions.sql_federal_document_ingest.federal_register_fetch import (
        fetch_document_json,
    )


def _normalize_event(event):
    if isinstance(event, (bytes, str)):
        return json.loads(event)
    return event


def handler(event, context):
    try:
        s3dict = _normalize_event(event)
        print("Received event keys:", list(s3dict.keys()) if isinstance(s3dict, dict) else type(s3dict))
        print("Data: ", s3dict)

        if s3dict.get("frdocnum") and not s3dict.get("file_key"):
            frdocnum = str(s3dict["frdocnum"]).strip()
            if not frdocnum:
                raise ValueError("frdocnum is empty")
            print(f"Fetching Federal Register document {frdocnum!r} from API...")
            file_content = fetch_document_json(frdocnum)
        else:
            s3 = boto3.client("s3")
            file_obj = s3.get_object(Bucket=s3dict["bucket"], Key=s3dict["file_key"])
            file_content = file_obj["Body"].read().decode("utf-8")
            print("File content Retrieved!")

        if not file_content:
            raise ValueError("File content is empty")

        print("Ingesting federal register document...")
        ingest_federal_document(file_content)

        print("Ingesting CFR parts...")
        ingest_cfr_part(file_content)

        print("Ingest complete!")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data processed successfully"}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }