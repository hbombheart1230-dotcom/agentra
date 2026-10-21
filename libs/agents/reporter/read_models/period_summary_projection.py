"""Operator period/daily summary compact projections.

Pure output shapes of ``_runtime_activity_payload`` (Q9-window counts, daily-report payload, not-available and
live-summary fallback) and the CRITICAL residual-closeout readout overlay of
``build_operator_daily_summary_artifact_payload``. The streamed ``q9_decision_windows.json`` read, the live
summary lookup, memory sync, account/broker receipts, market/news and all file writes stay in
``operator_period_summary``; the pinned R3 ``operator_period_summary_parts`` owners are untouched.
"""
from __future__ import annotations

from typing import Any, Dict


def runtime_activity_from_q9_windows(*, q9_path: Any, q9_window_count: Any, decisions: Any, monitor_intents: Any, facade: Any) -> Dict[str, Any]:
    return {
        "source": "q9_decision_windows",
        "source_path": str(q9_path),
        "events": q9_window_count,
        "commander_decision_count": len(decisions),
        "missing_commander_decision_count": max(0, q9_window_count - len(decisions)),
        "approvals": sum(value in {"approve", "approved", "allow"} for value in decisions),
        "blocks": sum(value in {"reject", "blocked", "veto"} for value in decisions),
        "noops": sum(value in {"noop", "no_trade"} for value in decisions),
        "monitor_buy_count": sum(value == "BUY" for value in monitor_intents),
        "monitor_noop_count": sum(value == "NOOP" for value in monitor_intents),
        "symbols_observed_count": 0,
        "generated_symbol_report_count": 0,
    }


def runtime_activity_from_daily_payload(*, source_payload: Any, facade: Any) -> Dict[str, Any]:
    return {
        "source": "daily_report_payload",
        "events": facade._safe_int(source_payload.get("events")),
        "approvals": facade._safe_int(source_payload.get("approvals")),
        "blocks": facade._safe_int(source_payload.get("blocks")),
        "symbols_observed_count": len(list(source_payload.get("symbols_observed") or [])),
        "generated_symbol_report_count": facade._safe_int(source_payload.get("generated_symbol_report_count")),
    }


def runtime_activity_not_available(*, facade: Any) -> Dict[str, Any]:
    return {
        "source": "not_available",
        "events": 0,
        "approvals": 0,
        "blocks": 0,
        "symbols_observed_count": 0,
        "generated_symbol_report_count": 0,
    }


def runtime_activity_from_live_summary(*, live_payload: Any, live_path: Any, events: Any, execution: Any, facade: Any) -> Dict[str, Any]:
    return {
        "source": "live_summary_fallback",
        "source_path": live_path,
        "lookback_min": facade._safe_int(live_payload.get("lookback_min")),
        "events": facade._safe_int(events.get("window_total")),
        "events_scanned_total": facade._safe_int(events.get("scanned_total")),
        "approvals": facade._safe_int(execution.get("allowed_total")),
        "blocks": facade._safe_int(execution.get("blocked_total")),
        "executed_total": facade._safe_int(execution.get("executed_total")),
        "broker_fail_total": facade._safe_int(execution.get("executed_broker_fail_total")),
        "symbols_observed_count": 0,
        "generated_symbol_report_count": 0,
    }


def apply_critical_closeout_readout(*, summary: Dict[str, Any], facade: Any) -> None:
    """Prepend the CRITICAL residual-closeout issue/action/root cause to ``summary["operator_readout"]`` in place."""
    residual_risk = (
        summary.get("residual_positions", {}).get("closeout_operational_risk")
        if isinstance(summary.get("residual_positions"), dict)
        else {}
    )
    if isinstance(residual_risk, dict) and str(residual_risk.get("severity") or "").lower() == "critical":
        readout = summary["operator_readout"]
        symbols_text = ", ".join(str(x) for x in list(residual_risk.get("unresolved_symbols") or []) if str(x).strip())
        readout["issues"] = [
            f"CRITICAL closeout issue: broker truth still has unclosed position(s): {symbols_text or '-'}",
            *list(readout.get("issues") or []),
        ]
        readout["recommended_actions"] = [
            "Next open: flatten unresolved position(s) at market before new BUY evaluation.",
            *list(readout.get("recommended_actions") or []),
        ]
        readout["root_cause"] = "장마감 청산/검증 루프가 broker truth 잔여 포지션을 완전히 닫지 못했습니다."
