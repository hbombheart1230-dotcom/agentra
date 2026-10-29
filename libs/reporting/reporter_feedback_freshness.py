"""``_extract_freshness`` moved verbatim from reporter_feedback.py as ``extract_freshness``.

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def extract_freshness(payload: Mapping[str, Any] | None, *, facade: Any) -> Dict[str, Any]:
    row = dict(payload or {})
    freshness = row.get("data_freshness") if isinstance(row.get("data_freshness"), dict) else {}
    if freshness:
        return dict(freshness)
    generated_at = str(row.get("generated_at") or "")
    return {
        "generated_at": generated_at,
        "source_run_count": facade._safe_int(row.get("source_run_count"), 0),
        "latest_run_id": str(row.get("latest_run_id") or ""),
        "latest_run_ts": str(row.get("latest_run_ts") or ""),
        "freshness_status": "unknown" if not generated_at else "fresh",
        "stale": False,
        "stale_reason": "source_not_declared" if not generated_at else "aligned_with_source_window",
        "source_window_summary": "",
    }
