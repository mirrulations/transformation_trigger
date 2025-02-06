import os
import boto3
import re

# AWS S3 Configuration
S3_BUCKET = "mirrulations-test1"
s3_client = boto3.client("s3")

# Old and New Structure Prefixes
RAW_PREFIX = "Raw_data/"
DERIVED_PREFIX = "Derived_data/"

def list_s3_files(prefix):
    """List all files in S3 under a given prefix."""
    files = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        if "Contents" in page:
            for obj in page["Contents"]:
                files.append(obj["Key"])
    return files

def extract_and_move_comments():
    """Move extracted comment text from pdfminer to Derived_data."""
    raw_files = list_s3_files(RAW_PREFIX)

    for file_key in raw_files:
        if "/text-" in file_key and "/comments_extracted_text/pdfminer/" in file_key:
            # Extract relevant parts from the path
            parts = file_key.split("/")
            agency, docket_id = parts[1], parts[2].replace("text-", "")
            extracted_filename = parts[-1]

            # Remove '_extracted' from filename
            new_filename = re.sub(r"_extracted", "", extracted_filename)

            # Define new destination path
            new_key = f"{DERIVED_PREFIX}{agency}/{docket_id}/mirrulations/extracted_txt/comment_attachment/{new_filename}"

            # Download, rename, re-upload, and delete old file
            temp_file = f"/tmp/{new_filename}"
            s3_client.download_file(S3_BUCKET, file_key, temp_file)
            s3_client.upload_file(temp_file, S3_BUCKET, new_key)
            print(f"Moved: {file_key} -> {new_key}")

if __name__ == "__main__":
    extract_and_move_comments()
    print("Comment extraction and migration completed successfully!")
