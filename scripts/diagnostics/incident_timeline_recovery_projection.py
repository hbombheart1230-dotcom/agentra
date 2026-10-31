from typing import Any, Dict, Tuple


def _is_recovery(row: Dict[str, Any]) -> Tuple[bool, str]:
    stage, event = str(row.get("stage") or ""), str(row.get("event") or ""); payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    if stage == "commander_router" and event == "intervention": return True, "commander_router:intervention"
    if stage == "commander_router" and event == "end":
        status = str(payload.get("status") or "").strip().lower()
        if status in ("ok", "resuming", "normal"): return True, f"commander_router:end:{status or 'ok'}"
    if stage == "commander_router" and event == "resilience":
        reason = str(payload.get("reason") or "").strip().lower()
        if reason in ("cooldown_not_active", "resume_applied", "operator_resumed"): return True, f"commander_router:resilience:{reason}"
    if stage == "execute_from_packet" and event == "end": return True, "execute_from_packet:end"
    return False, ""
