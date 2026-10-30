"""Symbol trade report JSON/JSONL read projections (moved verbatim from symbol_trade_report).

``json`` is resolved on ``facade`` (the symbol_trade_report module) at call time (and at iteration time inside the lazy generator); this module never imports it.
Read-only; no writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _iter_jsonl(path: Path, *, facade: Any) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    row = facade.json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict):
                    yield row

    return _gen()
