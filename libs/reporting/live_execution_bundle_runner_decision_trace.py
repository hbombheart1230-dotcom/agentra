"""``_latest_decision_trace_payload`` moved verbatim from live_execution_bundle_runner.py as ``latest_decision_trace_payload``.

Pure function; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def latest_decision_trace_payload(rows: List[Dict[str, Any]], *, event: str, agent: str) -> Dict[str, Any]:
    agent_name = str(agent or "").strip().lower()
    event_name = str(event or "").strip()
    for row in reversed(rows):
        if str(row.get("stage") or "").strip() != "decision_trace":
            continue
        if str(row.get("event") or "").strip() != event_name:
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        row_agent = str(payload.get("agent") or "").strip().lower()
        if row_agent != agent_name:
            continue
        agent_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
        return dict(agent_payload or {})
    return {}
