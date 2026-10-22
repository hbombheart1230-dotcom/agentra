"""Pure evidence and section readouts for Operator Brief presentation.

Caller helpers remain resolved through the supplied facade at each use site.
No I/O, LLM coordination or persistence belongs to this Owner.
"""
from __future__ import annotations


def build_current_snapshot_section(canonical_posture, decision_reason, execution_status_summary, final_action, focus_symbol, guard_status, live_monitor_reason, monitor_reason, next_expected_step, path_label, phase):
    return (
        {
            "summary": decision_reason,
            "phase": phase,
            "path": path_label,
            "final_action": final_action,
            "selected_symbol": focus_symbol,
            "current_focus": focus_symbol,
            "posture": canonical_posture or final_action or "-",
            "monitor_reason": monitor_reason or live_monitor_reason or "-",
            "guard_status": guard_status,
            "execution_status": execution_status_summary,
            "next_expected_step": next_expected_step or "-",
        }
    )

def build_strategist_evidence_section(candidate_hints, canonical_trade, global_score, market_headlines, news_targets, playbook, strategist_evidence_summary, strategist_summary, symbol_headlines, vix_level, *, facade):
    return (
        {
            "summary": strategist_evidence_summary,
            "market_regime": str(canonical_trade.get("market_regime") or strategist_summary.get("market_regime") or "-"),
            "playbook": playbook or "-",
            "global_sentiment": facade._format_float(global_score, 2) if global_score is not None else "-",
            "vix": facade._format_float(vix_level, 2) if vix_level is not None else "-",
            "candidate_hints": facade._clean_brief_list(candidate_hints, limit=6),
            "news_targets": facade._clean_brief_list(news_targets, limit=6),
            "market_headlines": facade._clean_str_list(market_headlines, limit=3, max_len=160),
            "symbol_headlines": facade._clean_str_list(symbol_headlines, limit=3, max_len=160),
        }
    )

def build_monitor_guard_snapshot_section(active_exit_axis, entry_guard_reason, entry_reason_code, execution_status_summary, guard_status, live_monitor_reason, monitor_guard_summary, monitor_reason, stop_policy_summary, supervisor_reason):
    return (
        {
            "summary": monitor_guard_summary,
            "monitor_reason": monitor_reason or live_monitor_reason or "-",
            "entry_reason": entry_reason_code or "-",
            "entry_guard_reason": entry_guard_reason or "-",
            "active_exit_axis": active_exit_axis or "-",
            "stop_policy_summary": stop_policy_summary[:4],
            "guard_status": guard_status,
            "guard_reason": supervisor_reason or "-",
            "execution_status": execution_status_summary,
        }
    )

def build_entry_timing_section(canonical_trade, entry_evaluated, entry_guard_reason, entry_metrics, entry_pattern, entry_reason_code, entry_signal_chain, entry_triggered, final_action):
    return (
        {
            "decision": "BUY" if entry_triggered or final_action == "BUY" else "WAIT",
            "evaluated": entry_evaluated,
            "triggered": entry_triggered,
            "reason_code": entry_reason_code,
            "reason_text": str(canonical_trade.get("entry_reason") or ""),
            "pattern": entry_pattern,
            "signal_chain": entry_signal_chain[:5],
            "metrics": dict(entry_metrics or {}),
            "guard_reason": entry_guard_reason,
        }
    )

def build_position_monitor_reasoning_section(active_exit_axis, avg_price_monitor, canonical_active_exit_axis, canonical_average_price, canonical_current_drawdown, canonical_current_price, canonical_effective_stop, canonical_effective_stop_reason, canonical_exit_triggers, canonical_feature_source, canonical_hold_reasons, canonical_holding_time, canonical_peak_drawdown, canonical_peak_price, canonical_posture, canonical_price_source, canonical_price_source_policy, canonical_stop_loss, canonical_take_profit, canonical_vwap_distance, canonical_watch_axes, current_drawdown_raw, current_price, effective_stop_reason, effective_stop_text, exit_triggers, final_action, hold_reasons, holding_time, monitor_summary, monitor_trace, peak_drawdown_raw, peak_price, stop_loss_text, take_profit_text, vwap_distance_raw, watch_axes, *, facade):
    return (
        {
            "posture": canonical_posture or final_action,
            "holding_time": canonical_holding_time or holding_time,
            "stop_loss": canonical_stop_loss or stop_loss_text,
            "effective_stop": canonical_effective_stop or effective_stop_text,
            "effective_stop_reason": (
                canonical_effective_stop_reason
                or (facade._friendly_exit_reason(effective_stop_reason or "stop_loss") if effective_stop_text != "-" else "-")
            ),
            "take_profit": canonical_take_profit or take_profit_text,
            "current_price": canonical_current_price or (facade._format_float(current_price, 2) if current_price not in (None, "") else "-"),
            "average_price": canonical_average_price or (facade._format_float(avg_price_monitor, 2) if avg_price_monitor not in (None, "") else "-"),
            "peak_price": canonical_peak_price or (facade._format_float(peak_price, 2) if peak_price not in (None, "") else "-"),
            "current_drawdown": canonical_current_drawdown or (facade._format_percent(current_drawdown_raw, 2) if current_drawdown_raw not in (None, "") else "-"),
            "peak_drawdown": canonical_peak_drawdown or (facade._format_percent(peak_drawdown_raw, 2) if peak_drawdown_raw not in (None, "") else "-"),
            "vwap_distance": canonical_vwap_distance or (facade._format_percent(vwap_distance_raw, 2) if vwap_distance_raw not in (None, "") else "-"),
            "price_source": canonical_price_source or str(monitor_trace.get("price_source") or monitor_summary.get("price_source") or "-"),
            "feature_source": canonical_feature_source or str(monitor_trace.get("feature_source") or monitor_summary.get("feature_source") or "-"),
            "price_source_policy": canonical_price_source_policy or str(monitor_trace.get("price_source_policy") or monitor_summary.get("price_source_policy") or ""),
            "active_exit_axis": (facade._friendly_exit_reason(canonical_active_exit_axis) if canonical_active_exit_axis else "") or active_exit_axis,
            "watch_axes": canonical_watch_axes or watch_axes,
            "hold_reasons": canonical_hold_reasons or hold_reasons[:4],
            "exit_triggers": canonical_exit_triggers or exit_triggers[:3],
        }
    )

def build_exit_plan_section(active_exit_axis, canonical_active_exit_axis, canonical_effective_stop, canonical_effective_stop_reason, canonical_exit_triggers, canonical_take_profit, canonical_trade, canonical_watch_axes, effective_stop_reason, effective_stop_text, exit_reason, exit_triggers, final_action, monitor_reason, take_profit_text, watch_axes, *, facade):
    return (
        {
            "current_action": final_action,
            "summary": str(canonical_trade.get("exit_reason") or exit_reason or monitor_reason or ""),
            "effective_stop": canonical_effective_stop or effective_stop_text,
            "effective_stop_reason": (
                canonical_effective_stop_reason
                or (facade._friendly_exit_reason(effective_stop_reason or "stop_loss") if effective_stop_text != "-" else "-")
            ),
            "take_profit": canonical_take_profit or take_profit_text,
            "active_exit_axis": (facade._friendly_exit_reason(canonical_active_exit_axis) if canonical_active_exit_axis else "") or active_exit_axis,
            "exit_triggers": canonical_exit_triggers or exit_triggers[:3],
            "watch_axes": canonical_watch_axes or watch_axes,
        }
    )

def build_ai_trade_report_section(report_available, report_lifecycle_status, report_lifecycle_summary, report_link, report_mode, report_model, report_next_step, report_reason, report_status, report_story_type, report_summary, report_trade_id, *, facade):
    return (
        {
            "status": report_status,
            "status_label": facade._report_status_label(report_status),
            "status_badge_class": facade._report_status_badge_class(report_status),
            "reason": report_reason or "AI report diagnostics were not captured.",
            "next_step": report_next_step or "Continue with Operator Brief while report diagnostics are resolved.",
            "model": report_model or "-",
            "available": report_available,
            "trade_id": report_trade_id,
            "lifecycle_status": report_lifecycle_status or "-",
            "lifecycle_summary": report_lifecycle_summary or "-",
            "story_type": report_story_type,
            "execution_mode_label": report_mode,
            "summary": report_summary or "No per-trade AI report is linked to this run yet.",
            "link": report_link,
        }
    )
