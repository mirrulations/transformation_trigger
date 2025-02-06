import os
import boto3
import re

# AWS S3 Configuration
S3_BUCKET = "mirrulations-test1"
s3_client = boto3.client("s3")

# Old and New Structure Prefixes
RAW_PREFIX = "Raw_data/"
DERIVED_PREFIX = "Derived_data/"

# Function to list files in an S3 prefix
def list_s3_files(prefix):
    files = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        if "Contents" in page:
            for obj in page["Contents"]:
                files.append(obj["Key"])
    return files

# Function to ensure a path exists in S3 by uploading a placeholder file
def ensure_s3_path_exists(prefix):
    temp_placeholder = "/tmp/placeholder.txt"
    with open(temp_placeholder, "w") as f:
        f.write("Placeholder to ensure S3 structure exists.")
    s3_client.upload_file(temp_placeholder, S3_BUCKET, f"{prefix}placeholder.txt")

# Function to move extracted comment text to Derived_data
def move_extracted_comments():
    raw_files = list_s3_files(RAW_PREFIX)
    for file_key in raw_files:
        if "/text-" in file_key and "/comments_extracted_text/pdfminer/" in file_key:
            parts = file_key.split("/")
            agency, docket_id = parts[1], parts[2].replace("text-", "")
            extracted_filename = parts[-1]
            new_filename = re.sub(r"_extracted", "", extracted_filename)
            derived_base_path = f"{DERIVED_PREFIX}{agency}/{docket_id}/mirrulations/extracted_txt/comment_attachment/"
            ensure_s3_path_exists(derived_base_path)
            new_key = f"{derived_base_path}{new_filename}"
            temp_file = f"/tmp/{new_filename}"
            s3_client.download_file(S3_BUCKET, file_key, temp_file)
            s3_client.upload_file(temp_file, S3_BUCKET, new_key)
            print(f"Moved: {file_key} -> {new_key}")

# Function to restructure Raw_data
def restructure_raw_data():
    raw_files = list_s3_files(RAW_PREFIX)
    for file_key in raw_files:
        if "/comments_extracted_text/" not in file_key:
            new_key = file_key.replace("text-", "")
            s3_client.copy_object(Bucket=S3_BUCKET, CopySource={"Bucket": S3_BUCKET, "Key": file_key}, Key=new_key)
            s3_client.delete_object(Bucket=S3_BUCKET, Key=file_key)
            print(f"Reformatted: {file_key} -> {new_key}")

# Function to create the full Derived_data structure
def create_derived_structure():
    base_dirs = ["MoravianResearch", "mirrulations", "trotterf"]
    sub_dirs = {
        "MoravianResearch": ["projectName/comment", "projectName/docket", "projectName/document"],
        "mirrulations": [
            "ai_summary/comment", "ai_summary/comment_attachments", "ai_summary/document",
            "entities/comment", "entities/comment_attachment", "entities/document",
            "extracted_txt/comment_attachment"
        ],
        "trotterf": ["projectName/fileType"]
    }
    
    for agency in list_s3_files(RAW_PREFIX):
        agency_name = agency.split("/")[1]
        for docket in list_s3_files(f"{RAW_PREFIX}{agency_name}/"):
            docket_id = docket.split("/")[2].replace("text-", "")
            for base in base_dirs:
                for sub in sub_dirs[base]:
                    derived_path = f"{DERIVED_PREFIX}{agency_name}/{docket_id}/{base}/{sub}/"
                    ensure_s3_path_exists(derived_path)

if __name__ == "__main__":
    create_derived_structure()
    move_extracted_comments()
    restructure_raw_data()
    print("Derived data structure created, extracted comments moved, and raw data reformatted successfully!")
