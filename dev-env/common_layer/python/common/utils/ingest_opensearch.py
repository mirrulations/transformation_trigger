import os
import json
import boto3
from .opensearch import connect as create_client


def ingest_comment_from_text(client, content):
    data = json.loads(content)
    document = {
        'commentText': data['data']['attributes']['comment'],
        'docketId': data['data']['attributes']['docketId'],
        'commentId': data['data']['id']
    }
    ingest(client, document, id = document['commentId'])

def ingest(client, document, id):
    response = client.index(index = 'comments', body = document, id = id)
    print(response)

def ingest_comment(client, bucket, key):
    obj = bucket.Object(key)
    file_text = obj.get()['Body'].read().decode('utf-8')
    data = json.loads(file_text)
    document = {
        'commentText': data['data']['attributes']['comment'],
        'docketId': data['data']['attributes']['docketId'],
        'commentId': data['data']['id']
    }
    ingest(client, document)

def ingest_all_comments(client, bucket):
    for obj in bucket.objects.all():
        if obj.key.endswith('.json') and ('/comments/' in obj.key):
            ingest_comment(client, bucket, obj.key)


if __name__ == '__main__':
    client = create_client()

    s3 = boto3.resource(
        service_name = 's3',
        region_name = 'us-east-1'
    )

    print('boto3 created')

    bucket = s3.Bucket(os.getenv('S3_BUCKET_NAME'))

    ingest_all_comments(client, bucket)
