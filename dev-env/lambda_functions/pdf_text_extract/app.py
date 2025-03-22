import json

def handler(event, context):
    print(f"Received event: {json.dumps(event)}")