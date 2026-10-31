"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            payload = facade.json.loads(path.read_text(encoding=encoding))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            continue
    return {}


def _iter_quant_shadow_candidate_rows(reports_root: Path, *, start: str, end: str, facade: Any) -> Iterable[Dict[str, Any]]:
    root = facade._quant_shadow_candidate_root(reports_root)
    for day in facade._iter_days(start, end):
        day_root = root / day
        if not day_root.exists():
            continue
        for path in sorted(day_root.glob("*.json")):
            if path.name == "latest.json":
                continue
            payload = facade._read_json(path)
            for row in list(payload.get("candidates") or []):
                if isinstance(row, Mapping):
                    yield dict(row)
