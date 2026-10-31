from typing import Any, Dict


def _event_reason(row: Dict[str, Any]) -> str:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    for key in ("reason", "error_type", "error", "status"):
        if payload.get(key): return str(payload[key])
    return ""
