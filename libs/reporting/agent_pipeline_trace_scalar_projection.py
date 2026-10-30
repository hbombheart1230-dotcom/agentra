"""Agent pipeline trace scalar/row projections (moved verbatim from agent_pipeline_trace).

``_to_epoch``, ``datetime`` and ``timezone`` are resolved on ``facade`` (the agent_pipeline_trace module) at call time
for ``_utc_day``; this module never imports it. Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _utc_day(ts: Any, *, facade: Any) -> Optional[str]:
    e = facade._to_epoch(ts)
    if e is None:
        return None
    return facade.datetime.fromtimestamp(e, tz=facade.timezone.utc).strftime("%Y-%m-%d")


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _latest_row(rows: List[Dict[str, Any]], *, stage: str, event: str) -> Dict[str, Any]:
    for row in reversed(rows):
        if str(row.get("stage") or "").strip() == stage and str(row.get("event") or "").strip() == event:
            return row
    return {}
