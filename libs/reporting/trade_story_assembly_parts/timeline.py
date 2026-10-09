from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_report_common import clip_text as clip, utc_now_iso
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human


def build_timeline(
    *,
    commander: Dict[str, Any],
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    guard_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution: Dict[str, Any],
) -> List[Dict[str, Any]]:
    route_ts = str(commander.get("route_ts") or "")
    execution_ts = str(execution.get("ts") or "")
    return [
        {"step": "strategist_frame", "status": "ok", "ts": route_ts, "summary": market_context_human.get("summary") or ""},
        {"step": "scanner_ranking", "status": "ok", "ts": route_ts, "summary": scanner_reason_human.get("summary") or ""},
        {"step": "monitor_signal", "status": "ok", "ts": execution_ts, "summary": monitor_reason_human.get("summary") or ""},
        {"step": "supervisor_approval", "status": "ok", "ts": execution_ts, "summary": guard_reason_human.get("summary") or ""},
        {"step": "broker_result", "status": "ok", "ts": execution_ts, "summary": execution_outcome_human.get("summary") or ""},
        {"step": "reporter_output", "status": "ok", "ts": utc_now_iso(), "summary": reporter_status_human.get("summary") or ""},
    ]


def collect_story_warnings(
    *,
    story_contract: Dict[str, Any],
    market_context_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
) -> List[str]:
    warnings = [str(x or "") for x in list(story_contract.get("warnings") or []) if str(x or "").strip()]
    if market_context_human.get("defensive_mode"):
        warnings.append("Macro or volatility context was defensive for this run.")
    if reporter_status_human.get("status") == "pending":
        warnings.append("Reporter evaluation is pending because same-day run linkage was not available yet.")
    elif reporter_status_human.get("status") == "missing":
        warnings.append("Reporter evaluation is missing because the same-day analysis file was not generated yet.")
    for row in list(filters_human.get("checks") or []):
        if not isinstance(row, dict):
            continue
        status = str(row.get("status") or "").upper()
        if status in {"FAIL", "PARTIAL", "NOT_AVAILABLE"}:
            warnings.append(f"{row.get('name')}: {status} ({row.get('detail') or ''})")
    if execution_outcome_human.get("outcome") == "failed":
        warnings.append("Execution did not complete successfully and needs operator review.")
    deduped: List[str] = []
    for item in warnings:
        text = clip(item, max_len=260)
        if text and text not in deduped:
            deduped.append(text)
    return deduped[:10]


def compact_canonical_monitor(canonical_monitor: Dict[str, Any] | None) -> Dict[str, Any]:
    monitor = canonical_monitor if isinstance(canonical_monitor, dict) else {}
    compact = {
        "decision_action": monitor.get("decision_action"),
        "exit_reason": monitor.get("exit_reason"),
        "current_price": monitor.get("current_price"),
        "avg_price": monitor.get("avg_price"),
        "account_pnl_ratio": monitor.get("account_pnl_ratio"),
        "effective_pnl_ratio": monitor.get("effective_pnl_ratio"),
        "price_source": monitor.get("price_source"),
    }
    if any(value not in (None, "", [], {}) for value in compact.values()):
        return compact
    return {}

# P1.5.2 R2-C: lifecycle / section-seed / final story assembly owners.


