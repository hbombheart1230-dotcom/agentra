from typing import Any, Dict, Tuple


def _incident_trigger(row: Dict[str, Any]) -> Tuple[bool, str]:
    stage, event = str(row.get("stage") or ""), str(row.get("event") or ""); payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    if stage == "commander_router" and event == "error": return True, f"commander_router:error:{str(payload.get('error_type') or payload.get('error') or 'commander_error')}"
    if stage == "commander_router" and event == "transition" and str(payload.get("transition") or "").strip().lower() == "cooldown": return True, f"commander_router:transition:{str(payload.get('reason') or 'cooldown_transition')}"
    if stage == "commander_router" and event == "resilience":
        reason = str(payload.get("reason") or "").strip().lower()
        if reason in ("cooldown_active", "incident_threshold_cooldown"): return True, f"commander_router:resilience:{reason}"
    if stage == "execute_from_packet" and event == "error": return True, f"execute_from_packet:error:{str(payload.get('error') or 'execute_error')}"
    return False, ""
