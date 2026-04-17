"""Collect Federal Register document numbers from nested JSON (docket / document payloads)."""

from __future__ import annotations

from typing import Any, Set

_FR_KEYS = frozenset({"frdocnum", "fdocnum"})


def collect_frdocnums(obj: Any) -> Set[str]:
    """Return unique non-empty frdocnum / fdocnum string values anywhere in the tree."""
    found: Set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, val in node.items():
                if key in _FR_KEYS and val is not None:
                    s = str(val).strip()
                    if s:
                        found.add(s)
                walk(val)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj)
    return found
