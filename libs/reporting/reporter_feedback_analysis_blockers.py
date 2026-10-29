"""``_extract_reporter_analysis_blocker_totals`` moved verbatim from reporter_feedback.py as ``extract_reporter_analysis_blocker_totals``.

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def extract_reporter_analysis_blocker_totals(payload: Mapping[str, Any] | None, *, facade: Any) -> Dict[str, int]:
    row = dict(payload or {})
    monitor_eval = row.get("monitor_evaluation") if isinstance(row.get("monitor_evaluation"), dict) else {}
    supervisor = row.get("supervisor_activity") if isinstance(row.get("supervisor_activity"), dict) else {}
    intent_flow = row.get("intent_flow_analysis") if isinstance(row.get("intent_flow_analysis"), dict) else {}
    totals: Dict[str, int] = {}
    for key, value in dict(monitor_eval.get("monitor_reason_top") or {}).items():
        name = str(key or "").strip()
        if not name:
            continue
        totals[name] = totals.get(name, 0) + facade._safe_int(value, 0)
    for key, value in dict(supervisor.get("blocked_reason_top") or {}).items():
        name = str(key or "").strip()
        if not name:
            continue
        totals[name] = totals.get(name, 0) + facade._safe_int(value, 0)
    for key, value in dict(intent_flow.get("reason_top") or {}).items():
        name = str(key or "").strip()
        if not name or name.startswith("monitor:"):
            continue
        totals[name] = totals.get(name, 0) + facade._safe_int(value, 0)
    return totals
