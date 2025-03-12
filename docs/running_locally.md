# Running locally

Navigate to dev-env folder in terminal

run `sam build` to build the image for the sam template (this will create a .aws-sam/ folder)

run `sam local start-lambda --docker-network mirrulations` which will start up the lambda service in the mirrulations network

then run

```bash
aws lambda invoke --endpoint-url http://127.0.0.1:3001 \
  --function-name OrchestratorFunction \
  --payload fileb://events/s3_put_event.json output.json
```

This is invoking the orchestrator lambda on the localhost endpoint with a payload (in this case, events/s3_put_event.json) and saving the lambda logs/output to output.json
