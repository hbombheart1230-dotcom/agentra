"""Market regime rail review macro snapshot reader (moved verbatim from market_regime_rail_review).

``json`` is resolved on ``facade`` (the market_regime_rail_review module) at call time; this module never imports it.
Read-only; no writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def load_latest_macro_snapshot(day: str, *, root: Path = Path("data/logs/macro_indicators"), facade: Any) -> Dict[str, Any]:
    path = root / str(day)[:10] / "latest.json"
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"available": False, "path": str(path), "error": "macro_snapshot_unavailable"}
    return {**dict(payload), "available": True, "path": str(path)}
