"""Monitor posture, threshold, handoff and blocker surface projections.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def cycle_posture_entry_applied_policy_entry_metrics(exit_info, entry_info, entry_applied_policy, commander_context, strategy_monitor_policy, strategist_plan, policy_provenance, current_reason, entry_received_policy, entry_policy_origin, commander_memory_application_trace, *, facade):
    thresholds = dict(exit_info.get("thresholds") or {}) if isinstance(exit_info.get("thresholds"), dict) else {}
    entry_metrics = dict(entry_info.get("metrics") or {}) if isinstance(entry_info.get("metrics"), dict) else {}
    entry_thresholds = dict(entry_info.get("thresholds") or {}) if isinstance(entry_info.get("thresholds"), dict) else {}
    entry_applied_policy = (
        dict(entry_info.get("applied_policy") or {})
        if isinstance(entry_info.get("applied_policy"), dict)
        else dict(entry_applied_policy or entry_thresholds)
    )
    monitor_policy_trace = facade._build_monitor_policy_trace(
        commander_context=commander_context,
        monitor_policy=strategy_monitor_policy,
        strategist_plan=strategist_plan,
        policy_provenance=policy_provenance,
        entry_info=entry_info,
        exit_info=exit_info,
        current_reason=current_reason,
    )
    policy_ref = dict(monitor_policy_trace.get("policy_ref") or {})
    policy_ref["received_policy"] = dict(entry_info.get("received_policy") or entry_received_policy or {})
    policy_ref["received_policy_source"] = str(entry_info.get("received_policy_source") or entry_policy_origin or "")
    policy_ref["effective_policy"] = dict(entry_info.get("effective_policy") or entry_applied_policy or {})
    policy_ref["effective_policy_source"] = str(entry_info.get("effective_policy_source") or "")
    policy_ref["effective_policy_source_chain"] = list(entry_info.get("effective_policy_source_chain") or [])
    policy_ref["policy_adjustments"] = dict(entry_info.get("policy_adjustments") or {})
    policy_ref["policy_adjustment_summary"] = str(entry_info.get("policy_adjustment_summary") or "")
    policy_ref["policy_adjustment_reasoning"] = str(entry_info.get("policy_adjustment_reasoning") or "")
    policy_ref["effective_policy_deltas"] = list(entry_info.get("effective_policy_deltas") or [])
    policy_ref["monitor_memory_bias_applied"] = bool(entry_info.get("monitor_memory_bias_applied"))
    policy_ref["monitor_memory_bias_observation_only"] = bool(entry_info.get("monitor_memory_bias_observation_only"))
    policy_ref["monitor_memory_bias"] = dict(entry_info.get("monitor_memory_bias") or {})
    policy_ref["monitor_memory_bias_summary"] = dict(entry_info.get("monitor_memory_bias_summary") or {})
    policy_ref["monitor_memory_bias_deltas"] = list(entry_info.get("monitor_memory_bias_deltas") or [])
    policy_ref["monitor_memory_bias_observed_deltas"] = list(entry_info.get("monitor_memory_bias_observed_deltas") or [])
    policy_ref["monitor_memory_bias_hold_applied"] = bool(exit_info.get("monitor_memory_bias_hold_applied"))
    policy_ref["monitor_memory_bias_hold_deltas"] = list(exit_info.get("monitor_memory_bias_hold_deltas") or [])
    policy_ref["monitor_memory_bias_exit_applied"] = bool(exit_info.get("monitor_memory_bias_exit_applied"))
    policy_ref["monitor_memory_bias_exit_deltas"] = list(exit_info.get("monitor_memory_bias_exit_deltas") or [])
    policy_ref["commander_memory_application_trace"] = dict(commander_memory_application_trace)
    policy_ref["monitor_memory_application_trace"] = dict(commander_memory_application_trace)
    return (entry_applied_policy, entry_metrics, entry_thresholds, monitor_policy_trace, policy_ref, thresholds)


def cycle_posture_threshold_snapshot(exit_info, entry_applied_policy, thresholds, entry_metrics, entry_received_policy, entry_policy_origin, entry_policy_contract, entry_thresholds, entry_info, *, facade):
    pnl_ratio = facade._to_float(exit_info.get("pnl_ratio")) if exit_info.get("pnl_ratio") not in (None, "") else None
    threshold_snapshot = {
        "current_price": exit_info.get("price"),
        "avg_price": exit_info.get("avg_price"),
        "peak_price": exit_info.get("peak_price"),
        "pnl_pct": pnl_ratio,
        "drawdown_pct": exit_info.get("peak_drawdown"),
        "stop_loss_pct": thresholds.get("stop_loss_pct"),
        "effective_stop_loss_pct": thresholds.get("effective_stop_loss_pct"),
        "take_profit_pct": thresholds.get("take_profit_pct"),
        "trailing_stop_pct": thresholds.get("trailing_stop_pct"),
        "final_exit_thresholds": dict(exit_info.get("final_exit_thresholds") or {}),
        "exit_threshold_source": str(exit_info.get("exit_threshold_source") or ""),
        "hold_block_reason": str(exit_info.get("hold_block_reason") or ""),
        "hold_limit_sec": exit_info.get("hold_limit_sec"),
        "max_hold_reached": bool(exit_info.get("max_hold_reached")),
        "time_stop_reached": bool(exit_info.get("time_stop_reached")),
        "time_limit_reached": bool(exit_info.get("time_limit_reached")),
        "time_limit_reason": str(exit_info.get("time_limit_reason") or ""),
        "time_limit_reassessment_required": bool(exit_info.get("time_limit_reassessment_required")),
        "time_limit_reassessment_blocked": bool(exit_info.get("time_limit_reassessment_blocked")),
        "time_limit_reassessment_blocked_reason": str(
            exit_info.get("time_limit_reassessment_blocked_reason") or ""
        ),
        "max_runup_pct": exit_info.get("max_runup_pct"),
        "peak_drawdown_from_peak": exit_info.get("peak_drawdown_from_peak"),
        "peak_drawdown_armed": bool(exit_info.get("peak_drawdown_armed")),
        "peak_drawdown_mode": str(exit_info.get("peak_drawdown_mode") or ""),
        "peak_drawdown_blocked": bool(exit_info.get("peak_drawdown_blocked")),
        "peak_drawdown_block_reason": str(exit_info.get("peak_drawdown_block_reason") or ""),
        "peak_drawdown_profit_floor_required_pct": exit_info.get("peak_drawdown_profit_floor_required_pct"),
        "peak_drawdown_profit_floor_met": bool(exit_info.get("peak_drawdown_profit_floor_met")),
        "final_peak_drawdown_ratio": exit_info.get("final_peak_drawdown_ratio"),
        "peak_drawdown_source": str(exit_info.get("peak_drawdown_source") or ""),
        "exit_trigger_metric_name": str(exit_info.get("exit_trigger_metric_name") or ""),
        "exit_trigger_metric_value": exit_info.get("exit_trigger_metric_value"),
        "exit_trigger_metric_source": str(exit_info.get("exit_trigger_metric_source") or ""),
        "cost_aware_profit_floor_enabled": bool(exit_info.get("cost_aware_profit_floor_enabled")),
        "round_trip_cost_floor_pct": exit_info.get("round_trip_cost_floor_pct"),
        "min_net_profit_buffer_pct": exit_info.get("min_net_profit_buffer_pct"),
        "cost_aware_profit_floor_pct": exit_info.get("cost_aware_profit_floor_pct"),
        "cost_aware_profit_floor_met": bool(exit_info.get("cost_aware_profit_floor_met")),
        "cost_aware_profit_floor_gap_pct": exit_info.get("cost_aware_profit_floor_gap_pct"),
        "cost_aware_profit_floor_blocked": bool(exit_info.get("cost_aware_profit_floor_blocked")),
        "expected_exit_price": exit_info.get("expected_exit_price"),
        "expected_exit_price_source": str(exit_info.get("expected_exit_price_source") or ""),
        "expected_exit_price_fallback_used": bool(exit_info.get("expected_exit_price_fallback_used")),
        "expected_exit_quote_rejected": bool(exit_info.get("expected_exit_quote_rejected")),
        "expected_exit_quote_rejected_reason": str(
            exit_info.get("expected_exit_quote_rejected_reason") or ""
        ),
        "expected_exit_quote_age_sec": exit_info.get("expected_exit_quote_age_sec"),
        "expected_exit_quote_price_divergence_pct": exit_info.get(
            "expected_exit_quote_price_divergence_pct"
        ),
        "expected_exit_slippage_buffer_pct": exit_info.get("expected_exit_slippage_buffer_pct"),
        "expected_exit_pnl_ratio": exit_info.get("expected_exit_pnl_ratio"),
        "expected_exit_net_pnl_ratio": exit_info.get("expected_exit_net_pnl_ratio"),
        "expected_exit_profit_floor_met": bool(exit_info.get("expected_exit_profit_floor_met")),
        "expected_exit_profit_floor_gap_pct": exit_info.get("expected_exit_profit_floor_gap_pct"),
        "expected_exit_profit_floor_blocked": bool(exit_info.get("expected_exit_profit_floor_blocked")),
        "expected_exit_profit_floor_blocked_reason": str(
            exit_info.get("expected_exit_profit_floor_blocked_reason") or ""
        ),
        "protective_exit_floor_blocked": bool(exit_info.get("protective_exit_floor_blocked")),
        "protective_exit_floor_blocked_reason": str(exit_info.get("protective_exit_floor_blocked_reason") or ""),
        "protective_exit_hard_invalidation": bool(exit_info.get("protective_exit_hard_invalidation")),
        "protective_exit_hard_invalidation_reason": str(
            exit_info.get("protective_exit_hard_invalidation_reason") or ""
        ),
        "vwap_distance_pct": exit_info.get("vwap_distance"),
        "volatility_regime": str(exit_info.get("volatility_regime") or ""),
        "active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
        "watch_axes": list(exit_info.get("watch_axes") or []),
        "exit_confirm_required": int(exit_info.get("exit_confirm_ticks") or 0),
        "exit_confirm_count": int(exit_info.get("exit_confirm_count") or 0),
        "price_anomaly_flag": bool(exit_info.get("price_anomaly_flag")),
        "price_anomaly_reason": str(exit_info.get("price_anomaly_reason") or ""),
        "pnl_fallback_applied": bool(exit_info.get("pnl_fallback_applied")),
        "fallback_price_source": str(exit_info.get("fallback_price_source") or ""),
        "entry_timeframe_minutes": entry_metrics.get("timeframe_minutes"),
        "entry_minute_source_present": entry_metrics.get("minute_source_present"),
        "entry_minute_source_used": entry_metrics.get("minute_source_used"),
        "entry_latest_candle_ts": entry_metrics.get("latest_candle_ts"),
        "entry_minute_snapshot_age_minutes": entry_metrics.get("minute_snapshot_age_minutes"),
        "entry_minute_snapshot_was_stale": entry_metrics.get("minute_snapshot_was_stale"),
        "entry_minute_refetch_attempted": entry_metrics.get("minute_refetch_attempted"),
        "entry_minute_refetch_succeeded": entry_metrics.get("minute_refetch_succeeded"),
        "entry_minute_refetch_reason": entry_metrics.get("minute_refetch_reason"),
        "entry_minute_refetch_trigger_reason": entry_metrics.get("minute_refetch_trigger_reason"),
        "entry_minute_refetch_failure_reason": entry_metrics.get("minute_refetch_failure_reason"),
        "entry_minute_refetch_produced_fresh_snapshot": entry_metrics.get("minute_refetch_produced_fresh_snapshot"),
        "entry_inferred_spacing_minutes": entry_metrics.get("inferred_spacing_minutes"),
        "entry_series_class": entry_metrics.get("series_class"),
        "entry_recent_high": entry_metrics.get("recent_high"),
        "entry_breakout_level": entry_metrics.get("breakout_level"),
        "entry_vwap": entry_metrics.get("vwap"),
        "entry_volume_ratio": entry_metrics.get("volume_ratio"),
        "entry_extended_from_vwap_pct": entry_metrics.get("extended_from_vwap_pct"),
        "entry_pullback_depth_pct": entry_metrics.get("pullback_depth_pct"),
        "entry_previous_close": entry_metrics.get("previous_close"),
        "entry_session_open": entry_metrics.get("session_open"),
        "entry_open_gap_pct": entry_metrics.get("open_gap_pct"),
        "entry_prev_close_distance_pct": entry_metrics.get("prev_close_distance_pct"),
        "entry_minutes_since_session_open": entry_metrics.get("minutes_since_session_open"),
        "entry_opening_gap_chase_observed": bool(entry_metrics.get("opening_gap_chase_observed")),
        "entry_opening_gap_context_observation_only": bool(entry_metrics.get("opening_gap_context_observation_only")),
        "received_policy": dict(entry_info.get("received_policy") or entry_received_policy or {}),
        "received_policy_source": str(entry_info.get("received_policy_source") or entry_policy_origin or ""),
        "policy_contract": dict(entry_info.get("policy_contract") or entry_policy_contract or {}),
        "effective_policy": dict(entry_info.get("effective_policy") or entry_applied_policy),
        "effective_policy_source": str(entry_info.get("effective_policy_source") or ""),
        "effective_policy_source_chain": list(entry_info.get("effective_policy_source_chain") or []),
        "policy_adjustments": dict(entry_info.get("policy_adjustments") or {}),
        "policy_adjustment_summary": str(entry_info.get("policy_adjustment_summary") or ""),
        "policy_adjustment_reasoning": str(entry_info.get("policy_adjustment_reasoning") or ""),
        "effective_policy_deltas": list(entry_info.get("effective_policy_deltas") or []),
        "applied_policy": dict(entry_applied_policy),
        "policy_contract": dict(entry_info.get("policy_contract") or entry_policy_contract or {}),
        "entry_volume_ratio_min": entry_thresholds.get("volume_ratio_min"),
        "entry_max_extended_from_vwap_pct": entry_thresholds.get("max_extended_from_vwap_pct"),
        "entry_min_extended_from_vwap_pct": entry_thresholds.get("min_extended_from_vwap_pct"),
        "entry_pullback_min_pct": entry_thresholds.get("pullback_min_pct"),
        "entry_pullback_max_pct": entry_thresholds.get("pullback_max_pct"),
        "entry_condition_path": str(entry_info.get("entry_condition_path") or ""),
        "entry_condition_paths_passed": list(entry_info.get("entry_condition_paths_passed") or []),
        "entry_condition_scores": dict(entry_info.get("condition_scores") or {}),
        "entry_grouped_logic_trace": dict(entry_info.get("grouped_logic_trace") or {}),
        "entry_passed_checks": list(entry_info.get("passed_checks") or []),
        "entry_failed_checks": list(entry_info.get("failed_checks") or []),
        "entry_primary_failure_axis": str(entry_info.get("primary_failure_axis") or ""),
        "entry_threshold_margins": dict(entry_info.get("threshold_margins") or {}),
        "entry_hard_filter_passed": bool(entry_info.get("hard_filter_passed")),
        "entry_hard_filter_fail_reasons": list(entry_info.get("hard_filter_fail_reasons") or []),
        "entry_total_score": entry_info.get("total_score"),
        "entry_score_breakdown": dict(entry_info.get("score_breakdown") or {}),
        "entry_policy_interpretation": dict(entry_info.get("policy_interpretation") or {}),
        "entry_signal_evidence": dict(entry_info.get("signal_evidence") or {}),
        "entry_chart_structure_features": dict(entry_info.get("chart_structure_features") or {}),
        "entry_policy_interpreter_trace": dict(entry_info.get("policy_interpreter_trace") or {}),
        "entry_policy_alignment_summary": dict(entry_info.get("policy_alignment_summary") or {}),
        "entry_policy_aware_gating": dict(entry_info.get("policy_aware_gating") or {}),
        "entry_chart_structure_decision_hint": dict(entry_info.get("chart_structure_decision_hint") or {}),
        "entry_score_threshold": entry_info.get("entry_threshold"),
        "entry_score_passed": bool(entry_info.get("score_passed")),
        "entry_scoring_mode": str(entry_info.get("scoring_mode") or "disabled"),
        "entry_legacy_decision": str(entry_info.get("legacy_entry_decision") or "WAIT"),
        "entry_scoring_decision": str(entry_info.get("scoring_entry_decision") or "WAIT"),
        "entry_transition_trace": dict(entry_info.get("entry_transition_trace") or {}),
    }
    return (threshold_snapshot,)


def cycle_posture_value_te_monitor_state_transition(previous_posture, current_posture, previous_reason, current_reason, state_changed, entry_transition_trace, exit_info, entry_info, previous_monitor_state, *, facade):
    return (
{
        "previous_posture": previous_posture,
        "current_posture": current_posture,
        "previous_reason": previous_reason,
        "current_reason": current_reason,
        "state_changed": bool(state_changed),
        "trigger_delta": {
            "previous_active_exit_axis": str(previous_monitor_state.get("active_exit_axis") or ""),
            "current_active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
            "exit_triggered": bool(exit_info.get("triggered")),
            "entry_triggered": bool(entry_info.get("triggered")),
            "entry_pattern": str(entry_info.get("pattern") or ""),
            "entry_condition_path": str(entry_info.get("entry_condition_path") or ""),
            "became_ready_this_cycle": bool(entry_transition_trace.get("became_ready_this_cycle")),
            "last_blocking_axis": str(entry_transition_trace.get("last_blocking_axis") or ""),
            "transition_readiness_score": entry_transition_trace.get("transition_readiness_score"),
        },
    }
    )


def cycle_posture_buy_skipped_reason_entry_event_metrics(buy_submitted, entry_info, state, *, facade):
    buy_skipped_reason = ""
    if not bool(buy_submitted):
        buy_skipped_reason = str(entry_info.get("guard_reason") or entry_info.get("reason") or "entry_wait").strip()
    entry_event_metrics = dict(entry_info.get("metrics") or {}) if isinstance(entry_info.get("metrics"), dict) else {}
    if "price" not in entry_event_metrics:
        entry_event_metrics["price"] = entry_event_metrics.get("current_price")
    if "vwap_distance" not in entry_event_metrics:
        entry_event_metrics["vwap_distance"] = entry_event_metrics.get("extended_from_vwap_pct")
    if "pullback_pct" not in entry_event_metrics:
        entry_event_metrics["pullback_pct"] = entry_event_metrics.get("pullback_depth_pct")
    final_entry_decision = "BUY" if bool(buy_submitted) else "WAIT"
    commander_decision = state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {}
    monitor_no_trade_surface = facade.build_monitor_no_trade_surface(
        entry_info,
        final_decision=final_entry_decision,
        buy_submitted=bool(buy_submitted),
        guard_blocked=bool(entry_info.get("guard_blocked")),
        guard_reason=entry_info.get("guard_reason"),
        commander_no_trade_reason_code=commander_decision.get("no_trade_reason_code"),
    )
    return (buy_skipped_reason, entry_event_metrics, final_entry_decision, monitor_no_trade_surface)
