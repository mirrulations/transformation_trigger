# Local ETL Testing with SAM + LocalStack

This guide walks through running the full ETL pipeline locally — putting a file into a fake S3 bucket, having a Lambda process it, and verifying the result in a local PostgreSQL database. No AWS credentials or live infrastructure needed.

## How It Works

```
You (terminal)
  → upload file to LocalStack S3 (fake AWS running in Docker)
    → invoke Lambda via SAM local (Lambda runs in Docker)
      → Lambda reads file from LocalStack S3
        → Lambda calls ingest function → inserts into local PostgreSQL
```

SAM automatically sets the `AWS_SAM_LOCAL` environment variable when running locally, which tells the common layer to use plain env vars for the DB connection instead of Secrets Manager.

---

## Prerequisites

Make sure the following are installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [LocalStack](https://localstack.cloud/) and the `awslocal` wrapper:
  ```bash
  pip install localstack awscli-local
  ```
- PostgreSQL (installed via Homebrew by mirrulations-search)
- The `mirrulations-search` repo cloned alongside this one — it owns the local DB setup

---

## One-Time Setup

### 1. Initialize the submodule

From the repo root:

```bash
git submodule update --init
```

Re-run `git submodule update` whenever the DP-Ingests repo has new changes.

### 2. Create the Docker network

```bash
docker network create mirrulations
```

### 3. Create `dev-env/env.json`

This file tells SAM how to connect your Lambda containers to your local Postgres. It is gitignored — never commit it.

```bash
touch dev-env/env.json
```

Paste the following, replacing `YOUR_POSTGRES_USER` with your local Postgres username (run `psql mirrulations -c "\conninfo"` if unsure):

```json
{
  "SQLFederalDocumentIngestFunction": {
    "POSTGRES_HOST": "host.docker.internal",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "mirrulations",
    "POSTGRES_USER": "YOUR_POSTGRES_USER",
    "POSTGRES_PASSWORD": "",
    "AWS_ENDPOINT_URL": "http://host.docker.internal:4566",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
    "AWS_DEFAULT_REGION": "us-east-1"
  }
}
```

`host.docker.internal` is how a Docker container reaches services running on your Mac (like your local Postgres and LocalStack).

---

## Running the Test

### Step 1: Start your local PostgreSQL database

From the `mirrulations-search` repo:

```bash
cd ../mirrulations-search
./dev_up.sh
```

This creates the `mirrulations` database with the full schema including the `federal_register_documents` table.

### Step 2: Start LocalStack

In a dedicated terminal:

```bash
localstack start
```

Wait until you see `Ready.` in the output.

### Step 3: Create a fake S3 bucket and upload a test file

Create a sample federal register document JSON:

```bash
cat > /tmp/test_fed_reg.json << 'EOF'
{
  "document_number": "2024-00001",
  "document_id": "some-id",
  "title": "Test Rule",
  "type": "Rule",
  "abstract": "A test rule abstract.",
  "publication_date": "2024-01-01",
  "effective_on": "2024-02-01",
  "docket_ids": ["EPA-2024-0001"],
  "agencies": [{"id": 123, "raw_name": "Environmental Protection Agency"}],
  "topics": ["Environment"],
  "significant": true,
  "regulation_id_numbers": ["2060-AA00"],
  "html_url": "https://example.com",
  "pdf_url": "https://example.com/doc.pdf",
  "json_url": "https://example.com/doc.json",
  "start_page": 100,
  "end_page": 110,
  "cfr_references": [{"title": "40", "part": "50"}]
}
EOF
```

Create the bucket and upload the file:

```bash
awslocal s3 mb s3://test-bucket
awslocal s3 cp /tmp/test_fed_reg.json s3://test-bucket/raw-data/federal_register_2024-00001.json
```

Verify it uploaded:

```bash
awslocal s3 ls s3://test-bucket/raw-data/
```

### Step 4: Build the SAM project

From `dev-env/`:

```bash
cd dev-env
sam build
```

### Step 5: Start the local Lambda service

In a new terminal from `dev-env/`:

```bash
sam local start-lambda --docker-network mirrulations
```

Leave this running. It starts a local endpoint at `http://127.0.0.1:3001` that accepts Lambda invocations.

### Step 6: Invoke the Lambda

In a third terminal from `dev-env/`:

```bash
aws lambda invoke \
  --endpoint-url http://127.0.0.1:3001 \
  --function-name SQLFederalDocumentIngestFunction \
  --payload '{"bucket": "test-bucket", "file_key": "raw-data/federal_register_2024-00001.json"}' \
  --cli-binary-format raw-in-base64-out \
  output.json && cat output.json
```

A successful response looks like:

```json
{"statusCode": 200, "body": "{\"message\": \"Data processed successfully\"}"}
```

### Step 7: Verify the database entry

```bash
psql mirrulations -c "SELECT document_number, document_title, agency_id, publication_date FROM federal_register_documents;"
```

You should see the row for `2024-00001`.

---

## Teardown

Stop the SAM local Lambda service with `Ctrl+C` in that terminal.

Stop LocalStack:

```bash
localstack stop
```

To remove the test row from the database:

```bash
psql mirrulations -c "DELETE FROM federal_register_documents WHERE document_number = '2024-00001';"
```

---

## Troubleshooting

**`Connection refused` on Postgres from inside the Lambda container**
Make sure you're using `host.docker.internal` as `POSTGRES_HOST` in `env.json`, not `localhost`.

**`NoSuchBucket` error from the Lambda**
Check that `AWS_ENDPOINT_URL` is set to `http://host.docker.internal:4566` in `env.json` (not `localhost:4566`). The Lambda runs inside Docker so it can't reach your Mac's localhost directly.

**`localstack` command not found**
Make sure LocalStack is installed (`pip install localstack`) and your virtual environment is activated.

**`sam build` fails with missing common layer**
Run `git submodule update --init` from the repo root to initialize the DP-Ingests submodule.

**Lambda returns a 500**
Check the SAM local terminal for the full traceback — it prints Lambda logs there in real time.
