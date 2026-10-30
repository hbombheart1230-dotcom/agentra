"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _read_lock_payload(path: Path, *, facade: Any) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _load_bundle_queue(path: Path, *, facade: Any) -> List[Dict[str, Any]]:
    try:
        if not path.exists():
            return []
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return []
        return [dict(row) for row in payload if isinstance(row, dict)]
    except Exception:
        return []
