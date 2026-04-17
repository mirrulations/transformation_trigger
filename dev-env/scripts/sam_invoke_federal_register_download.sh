#!/usr/bin/env bash
# Local SAM invoke for Federal Register document ingest (when that Lambda exists in template.yaml).
# Maintainer wires the logical resource id after the function is added to dev-env/template.yaml.
#
# Usage from repo root:
#   FRDOCNUM=2024-12345 ./dev-env/scripts/sam_invoke_federal_register_download.sh
#
# Override the SAM function logical id if it differs:
#   SAM_FEDERAL_INGEST_FUNCTION=YourFederalIngestFunction FRDOCNUM=2024-12345 ./dev-env/scripts/...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_ENV="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$DEV_ENV"

FUNCTION_LOGICAL_ID="${SAM_FEDERAL_INGEST_FUNCTION:-SQLFederalDocumentIngestFunction}"
FRDOCNUM="${FRDOCNUM:?Set FRDOCNUM (e.g. FRDOCNUM=2024-12345)}"

EVENT_FILE="$(mktemp)"
trap 'rm -f "$EVENT_FILE"' EXIT
printf '{"frdocnum": "%s"}\n' "$FRDOCNUM" > "$EVENT_FILE"

sam build
sam local invoke "$FUNCTION_LOGICAL_ID" --event "$EVENT_FILE"
