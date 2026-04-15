#!/usr/bin/env bash
# Upload a local file to S3, then invoke the local Orchestrator with the same
# bucket/key as a synthetic S3 Put event (closest local equivalent of "object landed").
#
# Prerequisites:
#   - AWS CLI configured (same account/role that can PutObject to the bucket)
#   - sam local start-lambda running (default http://127.0.0.1:3001)
#   - If the child Lambda cannot read S3 from inside Docker, pass credentials via
#     sam --env-vars (see docs/running_locally.md or AWS SAM docs)
#
# Usage:
#   ./scripts/test_s3_then_invoke_orchestrator.sh <bucket> <s3-key> <local-file>
#
# Example (federal register JSON path):
#   ./scripts/test_s3_then_invoke_orchestrator.sh etllambdatest \
#     'raw-data/APHIS/APHIS-2022-0044/federal_register/my-doc.json' ./sample.json

set -euo pipefail

BUCKET="${1:?usage: $0 <bucket> <s3-key> <local-file>}"
KEY="${2:?usage: $0 <bucket> <s3-key> <local-file>}"
LOCAL="${3:?usage: $0 <bucket> <s3-key> <local-file>}"
ENDPOINT="${LAMBDA_ENDPOINT:-http://127.0.0.1:3001}"
OUT="${OUTPUT_JSON:-orchestrator-output.json}"

if [[ ! -f "$LOCAL" ]]; then
  echo "error: file not found: $LOCAL" >&2
  exit 1
fi

if [[ "$KEY" != raw-data/* ]]; then
  echo "warning: orchestrator ignores keys that do not start with raw-data/" >&2
fi

echo "Uploading s3://$BUCKET/$KEY <- $LOCAL"
aws s3 cp "$LOCAL" "s3://$BUCKET/$KEY"

EVENT_FILE="$(mktemp -t s3_put_event.XXXXXX.json)"
cleanup() { rm -f "$EVENT_FILE"; }
trap cleanup EXIT

# Minimal S3 event shape (orchestrator only needs Records[0].s3.bucket.name + object.key)
python3 - <<PY
import json
import sys

bucket = """$BUCKET"""
key = """$KEY"""

event = {
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "manual-test",
        "bucket": {
          "name": bucket,
          "ownerIdentity": {"principalId": "EXAMPLE"},
          "arn": f"arn:aws:s3:::{bucket}",
        },
        "object": {
          "key": key,
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901",
        },
      },
    }
  ]
}
path = """$EVENT_FILE"""
with open(path, "w", encoding="utf-8") as f:
    json.dump(event, f, indent=2)
PY

echo "Wrote event file: $EVENT_FILE"
echo "Invoking OrchestratorFunction at $ENDPOINT ..."

aws lambda invoke \
  --endpoint-url "$ENDPOINT" \
  --function-name OrchestratorFunction \
  --payload "fileb://$EVENT_FILE" \
  "$OUT"

echo "--- $OUT ---"
cat "$OUT"
echo
