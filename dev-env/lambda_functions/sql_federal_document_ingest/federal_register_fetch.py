"""Fetch Federal Register document JSON by document number (frdocnum)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

# Public read API; Lambda must have outbound internet (e.g. NAT) if run inside a private VPC subnet.
_BASE = "https://www.federalregister.gov/api/v1/documents"


def fetch_document_json(frdocnum: str) -> str:
    num = frdocnum.strip()
    if not num:
        raise ValueError("frdocnum is empty")
    segment = urllib.parse.quote(num, safe="")
    url = f"{_BASE}/{segment}.json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "MirrulationsETL/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise ValueError(
            f"Federal Register API HTTP {e.code} for frdocnum={num!r}: {body[:500]}"
        ) from e
