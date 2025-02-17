"""
Updated S3 Path Generator for Mirrulations Project
Handles complex S3 path structures based on raw and derived data standards.
"""

import boto3
import json
import logging
import os
import sys
from botocore.exceptions import BotoCoreError, ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_PREFIX = 'Raw_data/'

def extract_agency_docket(file_name):
    parts = file_name.split('-')
    if len(parts) >= 3:
        agency = parts[0]
        docket_id = '-'.join(parts[:3])  # Agency + Year + ID
        return agency, docket_id
    return "UNKNOWN", "UNKNOWN"

def determine_raw_path(file_name, data_type, extension):
    agency, docket_id = extract_agency_docket(file_name)
    
    if 'attachment' in file_name:
        folder = 'comments_attachments' if data_type == 'comment' else 'documents_attachments'
        return f"{RAW_PREFIX}{agency}/{docket_id}/binary-{docket_id}/{folder}/{file_name}"
    
    folder = {
        'docket': 'dockets',
        'document': 'documents',
        'comment': 'comments'
    }.get(data_type, 'unknown')
    
    return f"{RAW_PREFIX}{agency}/{docket_id}/text-{docket_id}/{folder}/{file_name}"

def ensure_s3_path_exists(s3_client, bucket, path):
    try:
        s3_client.put_object(Bucket=bucket, Key=(path if path.endswith('/') else path + '/'))
        logger.info(f"Ensured path exists: {path}")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to ensure path {path}: {e}")

def upload_file(s3_client, bucket, file_path, s3_path):
    try:
        ensure_s3_path_exists(s3_client, bucket, os.path.dirname(s3_path))
        s3_client.upload_file(file_path, bucket, s3_path)
        logger.info(f"Uploaded {file_path} to {s3_path}")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"S3 upload failed: {e}")

def process_file(s3_client, bucket, file_path):
    file_name = os.path.basename(file_path)
    extension = file_name.split('.')[-1].lower()
    data_type = 'unknown'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if extension == 'json':
                try:
                    parsed = json.loads(content)
                    doc_type = parsed['data']['type']
                    if doc_type == 'dockets':
                        data_type = 'docket'
                    elif doc_type == 'documents':
                        data_type = 'document'
                    elif doc_type == 'comments':
                        data_type = 'comment'
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON format in {file_path}")
                    return
            else:
                data_type = 'text' if extension == 'txt' else 'html'
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return
    
    s3_path = determine_raw_path(file_name, data_type, extension)
    upload_file(s3_client, bucket, file_path, s3_path)

def get_s3_client():
    try:
        return boto3.client('s3')
    except Exception as e:
        logger.error(f"Error creating S3 client: {e}")
        raise

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 script.py <filename> <s3bucket>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    bucket = sys.argv[2]
    
    s3_client = get_s3_client()
    process_file(s3_client, bucket, file_path)

if __name__ == "__main__":
    main()
