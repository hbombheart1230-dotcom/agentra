from __future__ import annotations

from typing import Any, Dict, Mapping

from .monitor_diagnostics import build_monitor_watch_axes, build_monitor_entry_threshold_gaps


def prepare_monitor_review_context(
    monitor: Dict[str, Any], execution: Dict[str, Any], *, deps: Mapping[str, Any],
) -> tuple:
    """Collect report-only Monitor evidence without changing any trading policy."""
    _build_monitor_blocker_trace = deps["build_monitor_blocker_trace"]
    _build_monitor_stop_policy_trace = deps["build_monitor_stop_policy_trace"]
    _list_text = deps["list_text"]
    _merge_missing_values = deps["merge_missing_values"]
    format_exit_label = deps["format_exit_label"]
    format_ratio_pct = deps["format_ratio_pct"]
    safe_float = deps["safe_float"]
    safe_int = deps["safe_int"]
    action = str(execution.get("action") or "").upper()
    decision_trace = monitor.get("decision_trace") if isinstance(monitor.get("decision_trace"), dict) else {}
    thresholds = monitor.get("thresholds") if isinstance(monitor.get("thresholds"), dict) else {}
    thresholds_guards_used = (
        decision_trace.get("thresholds_guards_used")
        if isinstance(decision_trace.get("thresholds_guards_used"), dict)
        else (
            monitor.get("thresholds_guards_used")
            if isinstance(monitor.get("thresholds_guards_used"), dict)
            else {}
        )
    )
    threshold_snapshot = (
        monitor.get("threshold_snapshot")
        if isinstance(monitor.get("threshold_snapshot"), dict)
        else {}
    )
    thresholds = _merge_missing_values(
        thresholds,
        thresholds_guards_used.get("thresholds") if isinstance(thresholds_guards_used.get("thresholds"), dict) else {},
    )
    for key in (
        "stop_loss_pct",
        "effective_stop_loss_pct",
        "effective_stop_reason",
        "take_profit_pct",
        "peak_drawdown_exit_pct",
        "trailing_stop_pct",
        "vwap_breakdown_pct",
        "intraday_low_break_pct",
        "trend_strength_floor",
    ):
        if thresholds.get(key) in (None, "", [], {}):
            thresholds[key] = monitor.get(key)
    trigger_details = monitor.get("trigger_details") if isinstance(monitor.get("trigger_details"), dict) else {}
    decision_reason_chain = [str(x or "") for x in list(monitor.get("decision_reason_chain") or []) if str(x or "").strip()]
    timing_assessment = decision_trace.get("timing_assessment") if isinstance(decision_trace.get("timing_assessment"), dict) else {}
    policy_ref = decision_trace.get("policy_ref") if isinstance(decision_trace.get("policy_ref"), dict) else {}
    received_policy = (
        monitor.get("received_policy")
        if isinstance(monitor.get("received_policy"), dict)
        else (
            threshold_snapshot.get("received_policy")
            if isinstance(threshold_snapshot.get("received_policy"), dict)
            else (
                policy_ref.get("received_policy")
                if isinstance(policy_ref.get("received_policy"), dict)
                else {}
            )
        )
    )
    effective_policy = (
        monitor.get("effective_policy")
        if isinstance(monitor.get("effective_policy"), dict)
        else (
            threshold_snapshot.get("effective_policy")
            if isinstance(threshold_snapshot.get("effective_policy"), dict)
            else (
                policy_ref.get("effective_policy")
                if isinstance(policy_ref.get("effective_policy"), dict)
                else {}
            )
        )
    )
    policy_adjustment_summary = str(
        monitor.get("policy_adjustment_summary")
        or threshold_snapshot.get("policy_adjustment_summary")
        or policy_ref.get("policy_adjustment_summary")
        or ""
    ).strip()
    effective_policy_deltas = [
        dict(row)
        for row in list(
            monitor.get("effective_policy_deltas")
            or threshold_snapshot.get("effective_policy_deltas")
            or policy_ref.get("effective_policy_deltas")
            or []
        )[:8]
        if isinstance(row, dict)
    ]
    entry_check_summary = str(decision_trace.get("entry_check_summary") or "").strip()
    entry_blockers = [str(x or "") for x in list(decision_trace.get("entry_blockers") or []) if str(x or "").strip()]
    entry_reason = str(
        timing_assessment.get("entry_reason")
        or monitor.get("entry_reason")
        or ""
    ).strip()
    entry_pattern = str(
        timing_assessment.get("entry_pattern")
        or monitor.get("entry_pattern")
        or ""
    ).strip()
    entry_signal_chain = [str(x or "") for x in list(monitor.get("entry_signal_chain") or []) if str(x or "").strip()]
    entry_condition_path = str(monitor.get("entry_condition_path") or "").strip()
    entry_condition_paths_passed = [str(x or "") for x in list(monitor.get("entry_condition_paths_passed") or []) if str(x or "").strip()]
    entry_condition_scores = monitor.get("entry_condition_scores") if isinstance(monitor.get("entry_condition_scores"), dict) else {}
    entry_grouped_logic_trace = monitor.get("entry_grouped_logic_trace") if isinstance(monitor.get("entry_grouped_logic_trace"), dict) else {}
    entry_metrics = monitor.get("entry_metrics") if isinstance(monitor.get("entry_metrics"), dict) else {}
    human_chart_detail_observed = (
        entry_metrics.get("human_chart_detail_observed")
        if isinstance(entry_metrics.get("human_chart_detail_observed"), dict)
        else {}
    )
    human_chart_detail_context = (
        monitor.get("human_chart_detail_context")
        if isinstance(monitor.get("human_chart_detail_context"), dict)
        else {}
    )
    if not human_chart_detail_observed and isinstance(human_chart_detail_context.get("observed"), dict):
        human_chart_detail_observed = dict(human_chart_detail_context.get("observed") or {})
    entry_thresholds = (
        monitor.get("entry_thresholds")
        if isinstance(monitor.get("entry_thresholds"), dict)
        else {}
    )
    if not entry_thresholds and isinstance(effective_policy, dict):
        entry_thresholds = dict(effective_policy or {})
    if not entry_thresholds and isinstance(monitor.get("applied_policy"), dict):
        entry_thresholds = dict(monitor.get("applied_policy") or {})
    if not entry_thresholds and isinstance(threshold_snapshot.get("entry_thresholds"), dict):
        entry_thresholds = dict(threshold_snapshot.get("entry_thresholds") or {})
    if not entry_thresholds and isinstance(threshold_snapshot.get("applied_policy"), dict):
        entry_thresholds = dict(threshold_snapshot.get("applied_policy") or {})
    entry_guard_blocked = bool(monitor.get("entry_guard_blocked"))
    entry_guard_reason = str(monitor.get("entry_guard_reason") or "").strip()
    entry_evaluated = bool(monitor.get("entry_evaluated"))
    entry_triggered = bool(monitor.get("entry_triggered"))
    exit_reason = str(monitor.get("exit_reason") or "").strip()
    monitor_reason = str(monitor.get("monitor_reason") or monitor.get("evaluation_summary") or "").strip()
    price_source = str(monitor.get("price_source") or "").strip()
    price_source_policy = str(monitor.get("price_source_policy") or "").strip()
    feature_source = str(monitor.get("feature_source") or "").strip()
    current_price = monitor.get("current_price")
    if current_price in (None, ""):
        current_price = monitor.get("price")
    average_price = monitor.get("average_price")
    if average_price in (None, ""):
        average_price = monitor.get("avg_price")
    peak_price = monitor.get("peak_price")
    peak_drawdown = monitor.get("peak_drawdown")
    current_drawdown = monitor.get("current_drawdown")
    vwap_distance = monitor.get("vwap_distance")
    hold_limit_sec = monitor.get("hold_limit_sec")
    if hold_limit_sec in (None, ""):
        hold_limit_sec = (
            thresholds.get("time_stop_sec")
            if safe_int(thresholds.get("time_stop_sec"), 0) > 0
            else thresholds.get("max_hold_sec")
        )
    time_limit_reached = bool(monitor.get("time_limit_reached"))
    time_limit_reason = str(monitor.get("time_limit_reason") or "").strip()
    time_limit_reassessment_required = bool(monitor.get("time_limit_reassessment_required"))
    time_limit_reassessment_blocked = bool(monitor.get("time_limit_reassessment_blocked"))
    time_limit_reassessment_blocked_reason = str(
        monitor.get("time_limit_reassessment_blocked_reason") or ""
    ).strip()
    if current_drawdown in (None, "") and current_price not in (None, "") and peak_price not in (None, ""):
        current_drawdown = (safe_float(current_price, 0.0) / max(safe_float(peak_price, 1.0), 1e-9)) - 1.0
    if current_drawdown in (None, "") and peak_drawdown not in (None, ""):
        current_drawdown = peak_drawdown

    watch_axes = build_monitor_watch_axes(monitor, trigger_details, thresholds, safe_float)
    trigger_type = str(monitor.get("trigger_type") or "").strip()
    if not trigger_type:
        trigger_type = exit_reason if action == "SELL" else entry_reason or monitor_reason
    if not trigger_type and decision_reason_chain:
        trigger_type = decision_reason_chain[-1]
    active_exit_axis = str(monitor.get("active_exit_axis") or trigger_details.get("active_exit_axis") or "").strip()
    if str(monitor_reason or "").strip().lower() in {"hold", "hold_position", "eod_carry_approved"} and not bool(monitor.get("exit_triggered")):
        active_exit_axis = "Hold"
    elif not active_exit_axis:
        active_exit_axis = format_exit_label(trigger_type)
    confirm_required = safe_int(
        thresholds_guards_used.get("exit_confirm_ticks"),
        safe_int(thresholds_guards_used.get("exit_confirm_required"), safe_int(monitor.get("exit_confirm_required"), 0)),
    )
    confirm_count = safe_int(
        thresholds_guards_used.get("exit_confirm_count"),
        safe_int(monitor.get("exit_confirm_count"), 0),
    )
    guard_blocked = bool(trigger_details.get("sell_guard_blocked") or monitor.get("guard_blocked") or monitor.get("sell_guard_blocked"))
    guard_reason = str(trigger_details.get("sell_guard_reason") or monitor.get("guard_reason") or monitor.get("sell_guard_reason") or "").strip()
    exit_pending_confirmation = (
        guard_reason.startswith("exit_confirmation_pending:")
        or exit_reason.startswith("exit_confirmation_pending:")
        or monitor_reason == "exit_signal_pending_confirmation"
    )
    hold_without_confirmed_exit = bool(
        action == "SELL"
        and not bool(monitor.get("exit_triggered"))
        and str(trigger_type or monitor_reason or "").strip().lower() in {"hold", "hold_position"}
    )
    monitor_execution_mismatch = bool(
        action == "SELL"
        and not bool(monitor.get("exit_triggered"))
        and (exit_pending_confirmation or hold_without_confirmed_exit)
    )
    eod_carry_evaluated = bool(monitor.get("eod_carry_evaluated"))
    eod_carry_approved = bool(monitor.get("eod_carry_approved"))
    eod_carry_action = str(monitor.get("eod_carry_action") or "").strip()
    eod_carry_reason = str(monitor.get("eod_carry_reason") or "").strip()
    eod_carry_positive_signals = _list_text(monitor.get("eod_carry_positive_signals"), limit=6, max_len=120)
    eod_carry_blockers = _list_text(monitor.get("eod_carry_blockers"), limit=6, max_len=120)
    eod_carry_anomaly = bool(monitor.get("eod_carry_anomaly"))
    eod_carry_anomaly_reason = str(monitor.get("eod_carry_anomaly_reason") or "").strip()
    minutes_to_close = monitor.get("minutes_to_close")
    entry_threshold_gaps = build_monitor_entry_threshold_gaps(
        entry_metrics, entry_thresholds, safe_float, format_ratio_pct,
    )
    monitor_stop_policy_trace = _build_monitor_stop_policy_trace(monitor, thresholds)
    monitor_blocker_trace = _build_monitor_blocker_trace(
        {
            "entry_check_summary": entry_check_summary,
            "entry_blockers": entry_blockers,
            "entry_metrics": entry_metrics,
            "entry_thresholds": entry_thresholds,
            "timing_assessment": timing_assessment,
            "policy_ref": policy_ref,
            "entry_condition_path": entry_condition_path,
            "entry_condition_paths_passed": entry_condition_paths_passed,
            "condition_scores": entry_condition_scores,
            "grouped_logic_trace": entry_grouped_logic_trace,
        }
    )
    return (
        action, active_exit_axis, average_price, confirm_count, confirm_required,
        current_drawdown, current_price, decision_reason_chain, effective_policy, effective_policy_deltas,
        entry_blockers, entry_check_summary, entry_condition_path, entry_condition_paths_passed, entry_condition_scores,
        entry_evaluated, entry_grouped_logic_trace, entry_guard_blocked, entry_guard_reason, entry_metrics,
        entry_pattern, entry_reason, entry_signal_chain, entry_threshold_gaps, entry_thresholds,
        entry_triggered, eod_carry_action, eod_carry_anomaly, eod_carry_anomaly_reason, eod_carry_approved,
        eod_carry_blockers, eod_carry_evaluated, eod_carry_positive_signals, eod_carry_reason, exit_pending_confirmation,
        exit_reason, feature_source, guard_blocked, guard_reason, hold_limit_sec,
        hold_without_confirmed_exit, human_chart_detail_observed, minutes_to_close, monitor_blocker_trace, monitor_execution_mismatch,
        monitor_reason, monitor_stop_policy_trace, peak_drawdown, peak_price, policy_adjustment_summary,
        policy_ref, price_source, price_source_policy, received_policy, thresholds,
        thresholds_guards_used, time_limit_reached, time_limit_reason, time_limit_reassessment_blocked, time_limit_reassessment_blocked_reason,
        time_limit_reassessment_required, timing_assessment, trigger_type, vwap_distance, watch_axes,
    )
