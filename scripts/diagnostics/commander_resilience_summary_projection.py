from typing import Any, Dict, List


def _summary(rows: List[Dict[str, Any]], *, total_matched: int) -> Dict[str, Any]:
    event_total: Dict[str, int] = {}; cooldown_transitions = intervention_total = error_total = 0
    latest_status = latest_run_id = ""
    for rec in rows:
        event = str(rec.get("event") or ""); payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        event_total[event] = int(event_total.get(event, 0)) + 1
        if (event == "transition" and (str(payload.get("transition") or "") == "cooldown" or str(payload.get("reason") or "") == "cooldown_active")) or (event == "resilience" and str(payload.get("reason") or "") == "incident_threshold_cooldown"): cooldown_transitions += 1
        if event == "intervention": intervention_total += 1
        if event == "error": error_total += 1
        status = str(payload.get("status") or "")
        if status: latest_status = status
        latest_run_id = str(rec.get("run_id") or latest_run_id)
    return {"total_matched": int(total_matched), "shown": int(len(rows)), "event_total": event_total, "cooldown_transition_total": int(cooldown_transitions), "intervention_total": int(intervention_total), "error_total": int(error_total), "latest_status": latest_status, "latest_run_id": latest_run_id}
