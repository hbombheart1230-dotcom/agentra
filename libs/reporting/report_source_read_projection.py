"""Report source JSON/JSONL read projections (moved verbatim from report_source_helpers).

``json`` is resolved on ``facade`` (the report_source_helpers module) at call time; this module never imports it.
Read-only; no writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable


def read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def iter_jsonl(path: Path, *, facade: Any) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                try:
                    obj = facade.json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    yield obj

    return _gen()
