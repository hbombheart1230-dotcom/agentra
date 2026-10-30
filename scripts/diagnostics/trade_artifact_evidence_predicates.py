from __future__ import annotations
from typing import Any, Dict, List, Tuple


def _safe_int(value: Any, default: int = 0, facade=None) -> int:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    try:
        if value in (None, ""):
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _is_empty_placeholder(value: Any, facade=None) -> bool:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    if value is None:
        return True
    if isinstance(value, bool):
        return value is False
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len(value) == 0
    if isinstance(value, dict):
        if not value:
            return True
        return all(_is_empty_placeholder(item) for item in value.values())
    return False


def _has_substantive_entry_evidence(entry_payload: Dict[str, Any], facade=None) -> bool:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    entry = entry_payload if isinstance(entry_payload, dict) else {}
    if not entry:
        return False
    if str(entry.get("run_id") or "").strip():
        return True
    if str(entry.get("ts") or "").strip():
        return True
    for key in ("price", "avg_price", "qty"):
        if entry.get(key) not in (None, "", 0, 0.0):
            return True
    scanner_context = entry.get("scanner_context") if isinstance(entry.get("scanner_context"), dict) else {}
    if str(scanner_context.get("selected_symbol") or "").strip():
        return True
    execution_context = entry.get("execution_context") if isinstance(entry.get("execution_context"), dict) else {}
    execution_details = entry.get("execution_details") if isinstance(entry.get("execution_details"), dict) else {}
    if str(execution_context.get("order_status") or execution_details.get("order_status") or "").strip():
        return True
    if str(execution_context.get("order_id") or execution_details.get("order_id") or "").strip():
        return True
    return False


def _has_substantive_exit_evidence(exit_payload: Dict[str, Any], facade=None) -> bool:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    exit_ctx = exit_payload if isinstance(exit_payload, dict) else {}
    if not exit_ctx:
        return False
    if str(exit_ctx.get("run_id") or "").strip():
        return True
    if str(exit_ctx.get("ts") or "").strip():
        return True
    if str(exit_ctx.get("reason_human") or "").strip():
        return True
    for key in ("price", "avg_price", "qty"):
        if exit_ctx.get(key) not in (None, "", 0, 0.0):
            return True
    execution_details = exit_ctx.get("execution_details") if isinstance(exit_ctx.get("execution_details"), dict) else {}
    if str(execution_details.get("order_status") or "").strip():
        return True
    if str(execution_details.get("order_id") or "").strip():
        return True
    monitor_context = exit_ctx.get("monitor_context") if isinstance(exit_ctx.get("monitor_context"), dict) else {}
    if str(monitor_context.get("trigger_type") or "").strip():
        return True
    return False


def _is_closed_trade(lifecycle_bundle: Dict[str, Any], exit_payload: Dict[str, Any], facade=None) -> bool:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    status = str(
        lifecycle_bundle.get("trade_lifecycle_status")
        or lifecycle_bundle.get("status")
        or ""
    ).strip().lower()
    if status == "open":
        return False
    if _has_substantive_exit_evidence(exit_payload):
        return True
    return status in {"closed", "exited", "sell"}


def _section_provenance_all_fallback(report: Dict[str, Any], facade=None) -> bool:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    provenance = report.get("section_provenance") if isinstance(report.get("section_provenance"), dict) else {}
    if not provenance:
        return False
    items = [value for value in provenance.values() if isinstance(value, dict)]
    if not items:
        return False
    fallback_tags = {"fallback", "unknown", "missing"}
    return all(str(item.get("source") or "").strip().lower() in fallback_tags for item in items)
