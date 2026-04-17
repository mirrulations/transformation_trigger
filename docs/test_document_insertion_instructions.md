# Testing Federal Register Document Insertion

This guide verifies the full two-step insertion process locally, mirroring what the Lambda functions do in production:

1. Insert a regulations.gov document (from mirrulations-fetch) into the `documents` table using DP-Ingests `utils/ingest_document.py`
2. Extract its `frDocNum` using `frdocnum_extract.py`, fetch from the Federal Register API using `federal_register_fetch.py`, and insert into `federal_register_documents` using DP-Ingests `utils/ingest_federal_document.py`

This is the same logic the `SQLDocumentIngestFunction` and `SQLFederalDocumentIngestFunction` Lambdas run — just executed directly instead of through AWS.

---

## Prerequisites

- Local Postgres running with the `mirrulations` database set up
  - If not, run `./dev_up.sh` from the `mirrulations-search` repo first
- DP-Ingests repo on the `add-fed-doc-ingest-file` branch
- transformation_trigger repo on the `add-app-for-fedreg-ingest` branch
- A document JSON from mirrulations-fetch (e.g. `CMS-2025-0304-0009.json`)

---

## Step 1: Set up a virtual environment in DP-Ingests

```bash
cd /path/to/DP-ingests
python -m venv .venv
source .venv/bin/activate
pip install 'psycopg[binary]' python-dotenv
```

---

## Step 2: Create a `.env` file in DP-Ingests

This file tells the ingest scripts how to connect to your local Postgres. It is gitignored — never commit it.

Create a `.env` file in the DP-Ingests root with the following, replacing `YOUR_POSTGRES_USER` with your local Postgres username (run `psql mirrulations -c "\conninfo"` if unsure):

```
POSTGRES_DB=mirrulations
POSTGRES_USER=YOUR_POSTGRES_USER
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---

## Step 3: Insert the document into the `documents` table

```bash
cd /path/to/DP-ingests
source .venv/bin/activate
python -m utils.ingest_document /path/to/mirrulations-fetch/CMS-2025-0304/raw-data/documents/CMS-2025-0304-0009.json
```

Expected output:
```
Document CMS-2025-0304-0009 inserted successfully.
```

Verify:
```bash
psql mirrulations -c "SELECT document_id, document_title, frdocnum FROM documents WHERE document_id = 'CMS-2025-0304-0009';"
```

---

## Step 4: Extract the `frDocNum` and fetch from the Federal Register API

Run the following from the `dev-env` directory in transformation_trigger. This uses `frdocnum_extract.py` and `federal_register_fetch.py` — the same scripts the Lambda uses — to get the FR API JSON and save it to a temp file:

```bash
cd /path/to/transformation_trigger/dev-env
source .venv/bin/activate
python - << 'EOF'
import json, sys
from pathlib import Path

sys.path.insert(0, "lambda_functions/sql_document_ingest")
sys.path.insert(0, "lambda_functions/sql_federal_document_ingest")

from frdocnum_extract import collect_frdocnums
from federal_register_fetch import fetch_document_json

doc_path = Path("/path/to/mirrulations-fetch/CMS-2025-0304/raw-data/documents/CMS-2025-0304-0009.json")
data = json.loads(doc_path.read_text())

frdocnums = collect_frdocnums(data)
if not frdocnums:
    print("No frDocNum found in document.")
    sys.exit(0)

for num in sorted(frdocnums):
    print(f"Fetching FR document: {num}")
    fr_json = fetch_document_json(num)
    out_path = f"/tmp/fr_{num}.json"
    Path(out_path).write_text(fr_json)
    print(f"Saved to {out_path}")
EOF
```

---

## Step 5: Insert into the `federal_register_documents` table

Replace `2025-13271` with the actual `frDocNum` printed in Step 4 if different:

```bash
cd /path/to/DP-ingests
python -m utils.ingest_federal_document /tmp/fr_2025-13271.json
```

Expected output:
```
Federal document 2025-13271 inserted successfully.
```

---

## Step 6: Verify both tables

Verify the `federal_register_documents` row:
```bash
psql mirrulations -c "SELECT document_number, document_title, agency_id, publication_date FROM federal_register_documents WHERE document_number = '2025-13271';"
```

Confirm the link between the two tables via `frdocnum`:
```bash
psql mirrulations -c "SELECT d.document_id, d.frdocnum, f.document_title FROM documents d JOIN federal_register_documents f ON d.frdocnum = f.document_number WHERE d.document_id = 'CMS-2025-0304-0009';"
```

---

## Cleanup

```bash
psql mirrulations -c "DELETE FROM federal_register_documents WHERE document_number = '2025-13271';"
psql mirrulations -c "DELETE FROM documents WHERE document_id = 'CMS-2025-0304-0009';"
```

---

## Troubleshooting

**`connection refused` or `could not connect to server`**
Your local Postgres is not running. Start it from `mirrulations-search` with `./dev_up.sh`.

**`FATAL: role "YOUR_POSTGRES_USER" does not exist`**
You forgot to replace `YOUR_POSTGRES_USER` in the `.env` file. Run `psql mirrulations -c "\conninfo"` to find your username.

**`An error occurred: relative import`**
Make sure you are running `python -m utils.ingest_document` (module syntax) from the DP-Ingests root — not `python utils/ingest_document.py` directly.

**`No frDocNum found`**
The document you used does not have a Federal Register document number. Try a different document — look for one where `data.attributes.frDocNum` is not null.

**Network error in Step 4**
You are not connected to the internet. The Federal Register API requires an active connection.
