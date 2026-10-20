"""Pure live overview aggregation and historical-snapshot reconciliation.

Only already-read inputs are interpreted here. File discovery, reads, clocks,
LLM calls and writes remain outside this Owner. The caller facade resolves its
existing date/integer helpers at use time, preserving monkeypatch behavior.
"""
from __future__ import annotations

from typing import Any, Dict, List, NamedTuple


class OverviewLiveProjection(NamedTuple):
    daily: dict[str, Any]
    executive: dict[str, Any]
    health: dict[str, Any]
    trading: dict[str, Any]
    reporter: dict[str, Any]
    reconciliation: dict[str, Any]
    recon_summary: dict[str, Any]
    ai_review: dict[str, Any]
    trade_summary: dict[str, Any]


def project_live_overview(
    *,
    latest_day,
    today_rows,
    daily,
    operator_summary,
    reporter,
    reconciliation,
    executive,
    health,
    trading,
    recon_summary,
    trade_summary,
    all_today_trades,
    traded_symbol_summary,
    overtrading_warning,
    facade,
) -> OverviewLiveProjection:
    today_rows = [row for row in today_rows if not latest_day or facade._event_day(row.get("ts_kst") or row.get("ts")) == latest_day]
    live_route_rows = [
        row
        for row in today_rows
        if str(row.get("stage") or "") == "commander_router"
        and str(row.get("event") or "") == "route"
    ]
    live_verdict_rows = [
        row
        for row in today_rows
        if str(row.get("stage") or "") == "execute_from_packet"
        and str(row.get("event") or "") == "verdict"
        and isinstance(row.get("payload"), dict)
    ]
    live_allowed_total = 0
    live_blocked_total = 0
    live_noop_total = 0
    live_block_reason_top: Dict[str, int] = {}
    for row in live_verdict_rows:
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        allowed = payload.get("allowed")
        reason = str(payload.get("reason") or "").strip()
        if allowed is True:
            live_allowed_total += 1
            continue
        if reason == "noop_intent_skipped":
            live_noop_total += 1
            continue
        if allowed is False:
            live_blocked_total += 1
            if reason:
                live_block_reason_top[reason] = facade._safe_int(live_block_reason_top.get(reason), 0) + 1
    live_run_total = len(live_route_rows)
    live_execution_total = len(all_today_trades)
    live_action_counts: Dict[str, int] = {}
    for row in all_today_trades:
        action = str(row.get("action") or "").upper().strip()
        if not action:
            continue
        live_action_counts[action] = facade._safe_int(live_action_counts.get(action), 0) + 1
    live_events_total = live_run_total
    live_symbols_traded = [str(row.get("symbol") or "") for row in traded_symbol_summary[:8] if str(row.get("symbol") or "").strip()]

    reported_run_total = facade._safe_int(trading.get("run_total"), 0)
    reported_exec_total = facade._safe_int(trading.get("executions_total"), 0)
    reported_blocked_total = facade._safe_int(trading.get("blocked_total"), 0)
    reported_daily_events = facade._safe_int(daily.get("events"), 0)
    reported_daily_approvals = facade._safe_int(daily.get("approvals"), 0)
    reported_daily_blocks = facade._safe_int(daily.get("blocks"), 0)
    reported_reporter_trade_count = facade._safe_int(trade_summary.get("trade_count"), 0)
    reported_reporter_symbols = [str(v or "") for v in list(trade_summary.get("symbols_traded") or []) if str(v or "").strip()]
    live_snapshot_mismatch = any(
        [
            live_run_total > reported_run_total,
            live_execution_total > reported_exec_total,
            live_allowed_total > reported_daily_approvals,
            live_blocked_total != reported_blocked_total and live_execution_total > 0,
            live_events_total > reported_daily_events,
            live_execution_total > reported_reporter_trade_count,
            live_symbols_traded != reported_reporter_symbols[: len(live_symbols_traded)],
        ]
    )

    if latest_day and live_snapshot_mismatch:
        top_block_reason = ""
        if live_block_reason_top:
            top_block_reason = sorted(live_block_reason_top.items(), key=lambda item: (-facade._safe_int(item[1]), str(item[0])))[0][0]
        executive = {
            "system_status": str(executive.get("system_status") or health.get("system_health_level") or "LIVE"),
            "summary_lines": [
                f"[LIVE] runs={live_run_total}, executions={live_execution_total} (approved={live_allowed_total}, blocked={live_blocked_total}, noop={live_noop_total}).",
                f"Top guard block: {top_block_reason or 'none'}",
            ] + list(executive.get("summary_lines") or []),
        }
        trading = {
            **trading,
            "run_total": live_run_total,
            "executions_total": live_execution_total,
            "blocked_total": live_blocked_total,
        }
        daily = {
            **daily,
            "events": live_events_total,
            "decision_actions": live_action_counts,
            "approvals": live_allowed_total,
            "blocks": live_blocked_total,
        }
        if reporter:
            reporter = {
                **reporter,
                "trade_summary": {
                    **trade_summary,
                    "trade_count": live_execution_total,
                    "symbols_traded": live_symbols_traded,
                },
            }
            ai_review = reporter.get("ai_review") if isinstance(reporter.get("ai_review"), dict) else {}
            trade_summary = reporter.get("trade_summary") if isinstance(reporter.get("trade_summary"), dict) else {}
            if ai_review:
                reporter["ai_review"] = {
                    **ai_review,
                    "status": "snapshot" if str(ai_review.get("status") or "").strip().lower() == "ok" else ai_review.get("status"),
                }

    reported_recon_local = facade._safe_int(recon_summary.get("local_total"), 0)
    reported_recon_broker = facade._safe_int(recon_summary.get("broker_total"), 0)
    reported_recon_matched = facade._safe_int(recon_summary.get("matched_by_ord_no"), 0)
    recon_stale_vs_live = live_execution_total > max(reported_recon_local, reported_recon_broker, reported_recon_matched)
    if latest_day and live_execution_total > 0 and (not reconciliation or recon_stale_vs_live):
        reconciliation = {
            "summary": {
                "local_total": live_execution_total,
                "broker_total": reported_recon_broker,
                "matched_by_ord_no": reported_recon_matched,
                "broker_window_limited": bool(recon_summary.get("broker_window_limited")),
                "pending": True,
                "sentence": "Intraday reconciliation has not been generated yet. Local executions are ahead of broker matching.",
            }
        }
        recon_summary = reconciliation.get("summary") if isinstance(reconciliation.get("summary"), dict) else {}

    if not operator_summary and latest_day:
        operator_summary_live_lines: List[str] = []
        if live_run_total:
            operator_summary_live_lines.append(f"live event log fallback active for {latest_day}")
        if live_execution_total:
            operator_summary_live_lines.append(f"today executions observed in log: {live_execution_total}")
        if live_blocked_total:
            operator_summary_live_lines.append(f"today blocked verdicts observed in log: {live_blocked_total}")
        live_status = "LIVE" if (live_run_total or live_execution_total or live_blocked_total) else "UNKNOWN"
        executive = {
            "system_status": live_status,
            "summary_lines": operator_summary_live_lines[:4],
        }
        health = {
            "system_health_level": live_status,
            "recommended_action": (
                [f"review same-day overtrading warning: {overtrading_warning.get('level')}"]
                if str(overtrading_warning.get("level") or "normal") in {"elevated", "high"}
                else ["generate operator summary after closeout to replace live fallback"]
            )[:4],
        }
        trading = {
            "run_total": live_run_total,
            "executions_total": live_execution_total,
            "blocked_total": live_blocked_total,
        }

    if not reporter and latest_day:
        reporter = {
            "ai_review": {"status": "not_generated_yet"},
            "ai_run_grade": "-",
            "ai_summary": "Same-day reporter analysis has not been generated yet.",
            "trade_summary": {
                "trade_count": live_execution_total,
                "symbols_traded": [str(row.get("symbol") or "") for row in traded_symbol_summary[:8]],
            },
        }
    ai_review = reporter.get("ai_review") if isinstance(reporter.get("ai_review"), dict) else {}
    trade_summary = reporter.get("trade_summary") if isinstance(reporter.get("trade_summary"), dict) else {}
    return OverviewLiveProjection(
        daily=daily,
        executive=executive,
        health=health,
        trading=trading,
        reporter=reporter,
        reconciliation=reconciliation,
        recon_summary=recon_summary,
        ai_review=ai_review,
        trade_summary=trade_summary,
    )
