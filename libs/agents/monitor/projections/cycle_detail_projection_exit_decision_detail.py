"""Monitor focus, entry/exit decision detail and evaluation projections.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def cycle_detail_exit_decision_detail(sell_submitted, exit_info, current_reason, quant_exit_decision, monitor_policy_trace, *, facade):
    sell_skipped_reason = ""
    if bool(exit_info.get("exit_signal_detected")) and not bool(sell_submitted):
        sell_skipped_reason = str(exit_info.get("sell_guard_reason") or exit_info.get("reason") or "sell_not_submitted").strip()
    exit_decision_detail = {
        "exit_triggered": bool(exit_info.get("triggered")),
        "triggered_rule": str(exit_info.get("reason") or ""),
        "pnl_ratio": exit_info.get("pnl_ratio"),
        "raw_pnl_ratio": exit_info.get("raw_pnl_ratio"),
        "gross_pnl_ratio": exit_info.get("gross_pnl_ratio"),
        "technical_pnl_ratio": exit_info.get("technical_pnl_ratio"),
        "effective_pnl_ratio": exit_info.get("effective_pnl_ratio"),
        "stop_pnl_ratio": exit_info.get("stop_pnl_ratio"),
        "stop_pnl_ratio_source": str(exit_info.get("stop_pnl_ratio_source") or ""),
        "hard_stop_pnl_ratio": exit_info.get("hard_stop_pnl_ratio"),
        "hard_stop_pnl_ratio_source": str(exit_info.get("hard_stop_pnl_ratio_source") or ""),
        "cost_drag_pressure": bool(exit_info.get("cost_drag_pressure")),
        "cost_drag_pressure_pct": exit_info.get("cost_drag_pressure_pct"),
        "cost_drag_pressure_reason": str(exit_info.get("cost_drag_pressure_reason") or ""),
        "stop_loss_cost_drag_blocked": bool(exit_info.get("stop_loss_cost_drag_blocked")),
        "stop_loss_cost_drag_blocked_reason": str(exit_info.get("stop_loss_cost_drag_blocked_reason") or ""),
        "price": exit_info.get("price"),
        "technical_price": exit_info.get("technical_price"),
        "technical_price_source": str(exit_info.get("technical_price_source") or ""),
        "effective_price": exit_info.get("effective_price"),
        "account_mark_price": exit_info.get("account_mark_price"),
        "account_mark_price_source": str(exit_info.get("account_mark_price_source") or ""),
        "account_unrealized_pnl": exit_info.get("account_unrealized_pnl"),
        "account_pnl_ratio_source": str(exit_info.get("account_pnl_ratio_source") or ""),
        "pnl_crosscheck_applied": bool(exit_info.get("pnl_crosscheck_applied")),
        "pnl_crosscheck_reason": str(exit_info.get("pnl_crosscheck_reason") or ""),
        "pnl_crosscheck_gap": exit_info.get("pnl_crosscheck_gap"),
        "price_anomaly_flag": bool(exit_info.get("price_anomaly_flag")),
        "price_anomaly_reason": str(exit_info.get("price_anomaly_reason") or ""),
        "pnl_fallback_applied": bool(exit_info.get("pnl_fallback_applied")),
        "fallback_price_source": str(exit_info.get("fallback_price_source") or ""),
        "confirm_count": int(exit_info.get("exit_confirm_count") or 0),
        "confirm_required": int(exit_info.get("exit_confirm_ticks") or 0),
        "guard_blocked": bool(exit_info.get("sell_guard_blocked")),
        "guard_reason": str(exit_info.get("sell_guard_reason") or ""),
        "hold_block_reason": str(exit_info.get("hold_block_reason") or ""),
        "final_exit_thresholds": dict(exit_info.get("final_exit_thresholds") or {}),
        "exit_threshold_source": str(exit_info.get("exit_threshold_source") or ""),
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
        "risk_reward_take_profit_target_pct": exit_info.get("risk_reward_take_profit_target_pct"),
        "risk_reward_take_profit_rung": exit_info.get("risk_reward_take_profit_rung"),
        "resistance_price": exit_info.get("resistance_price"),
        "resistance_price_source": str(exit_info.get("resistance_price_source") or ""),
        "resistance_distance_pct": exit_info.get("resistance_distance_pct"),
        "profit_time_stop_peak_giveback_pct": exit_info.get("profit_time_stop_peak_giveback_pct"),
        "partial_exit": bool(exit_info.get("partial_exit")),
        "exit_qty": exit_info.get("exit_qty"),
        "exit_qty_fraction": exit_info.get("exit_qty_fraction"),
        "profit_ladder_level_pct": exit_info.get("profit_ladder_level_pct"),
        "profit_ladder_level_index": exit_info.get("profit_ladder_level_index"),
        "volume_ratio": exit_info.get("volume_ratio"),
        "execution_strength": exit_info.get("execution_strength"),
        "trade_strength": exit_info.get("trade_strength"),
        "opening_gap_chase_observed": bool(exit_info.get("opening_gap_chase_observed")),
        "open_gap_pct": exit_info.get("open_gap_pct"),
        "prev_close_distance_pct": exit_info.get("prev_close_distance_pct"),
        "position_entry_risk_applied": bool(exit_info.get("position_entry_risk_applied")),
        "position_entry_stop_loss_pct": exit_info.get("position_entry_stop_loss_pct"),
        "position_entry_stop_loss_source": str(exit_info.get("position_entry_stop_loss_source") or ""),
        "position_entry_invalidation_price": exit_info.get("position_entry_invalidation_price"),
        "position_entry_raw_structure_stop_loss_pct": exit_info.get("position_entry_raw_structure_stop_loss_pct"),
        "position_entry_min_structure_stop_loss_pct": exit_info.get("position_entry_min_structure_stop_loss_pct"),
        "sell_submitted": bool(sell_submitted),
        "sell_skipped_reason": sell_skipped_reason,
        "final_reason": current_reason,
        "exit_vs_strategy_intent": dict(exit_info.get("exit_vs_strategy_intent") or {}),
        "exit_quant_decision": dict(quant_exit_decision),
        "policy_ref": dict(monitor_policy_trace.get("policy_ref") or {}),
        "exit_trigger_basis": dict(monitor_policy_trace.get("exit_trigger_basis") or {}),
        "commander_context_consumed": bool(monitor_policy_trace.get("commander_context_consumed")),
        "consumed_fields": list(monitor_policy_trace.get("consumed_fields") or []),
        "shadow_used": bool(monitor_policy_trace.get("shadow_used")),
        "strategist_fallback_used": bool(monitor_policy_trace.get("strategist_fallback_used")),
    }
    return (exit_decision_detail,)


def cycle_detail_blocked_rules_reason_chain(exit_info, entry_info, state, *, facade):
    triggered_rules = []
    if bool(exit_info.get("triggered")) and str(exit_info.get("reason") or "").strip():
        triggered_rules.append(str(exit_info.get("reason") or "").strip())
    if bool(entry_info.get("triggered")) and str(entry_info.get("pattern") or "").strip():
        triggered_rules.append(f"entry:{str(entry_info.get('pattern') or '').strip()}")
    blocked_rules = []
    if bool(entry_info.get("guard_blocked")) and str(entry_info.get("guard_reason") or "").strip():
        blocked_rules.append(str(entry_info.get("guard_reason") or "").strip())
    if bool(exit_info.get("sell_guard_blocked")) and str(exit_info.get("sell_guard_reason") or "").strip():
        blocked_rules.append(str(exit_info.get("sell_guard_reason") or "").strip())
    blocked_rules.extend([str(x or "").strip() for x in list(entry_info.get("failed_checks") or []) if str(x or "").strip()])
    reason_chain = [
        str(exit_info.get("monitor_reason") or "").strip(),
        str(exit_info.get("reason") or "").strip(),
        str(entry_info.get("reason") or "").strip(),
        str((state.get("monitor_output") or {}).get("entry_exit_reason") or "").strip(),
    ]
    reason_chain = [x for x in reason_chain if x]
    return (blocked_rules, reason_chain, triggered_rules)


def cycle_detail_value_state_monitor_evaluation(current_posture, triggered_rules, monitor_no_trade_surface, scanner_monitor_handoff, entry_info, entry_received_policy, entry_policy_contract, entry_applied_policy, blocked_rules, monitor_policy_trace, exit_info, *, facade):
    return (
{
        "triggered_rules": list(triggered_rules),
        "blocked_rules": list(dict.fromkeys(blocked_rules))[:8],
        "posture": current_posture,
        "active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
        "entry_pattern": str(entry_info.get("pattern") or ""),
        "entry_passed_checks": list(entry_info.get("passed_checks") or []),
        "entry_failed_checks": list(entry_info.get("failed_checks") or []),
        "entry_threshold_margins": dict(entry_info.get("threshold_margins") or {}),
        "entry_transition_trace": dict(entry_info.get("entry_transition_trace") or {}),
        "entry_lane": str(entry_info.get("entry_lane") or "strict"),
        "entry_cost_filter": dict(entry_info.get("entry_cost_filter") or {}),
        "cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
        "cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
        "cost_drag_pct": entry_info.get("cost_drag_pct"),
        "hard_filter_passed": bool(entry_info.get("hard_filter_passed")),
        "hard_filter_fail_reasons": list(entry_info.get("hard_filter_fail_reasons") or []),
        "total_score": entry_info.get("total_score"),
        "score_breakdown": dict(entry_info.get("score_breakdown") or {}),
        "entry_threshold": entry_info.get("entry_threshold"),
        "score_passed": bool(entry_info.get("score_passed")),
        "scoring_mode": str(entry_info.get("scoring_mode") or "disabled"),
        "legacy_entry_decision": str(entry_info.get("legacy_entry_decision") or "WAIT"),
        "scoring_entry_decision": str(entry_info.get("scoring_entry_decision") or "WAIT"),
        "chart_structure_features": dict(entry_info.get("chart_structure_features") or {}),
        "policy_aware_gating": dict(entry_info.get("policy_aware_gating") or {}),
        "chart_structure_decision_hint": dict(entry_info.get("chart_structure_decision_hint") or {}),
        "entry_lane": str(entry_info.get("entry_lane") or "strict"),
        "entry_cost_filter": dict(entry_info.get("entry_cost_filter") or {}),
        "cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
        "cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
        "cost_drag_pct": entry_info.get("cost_drag_pct"),
        "no_trade_surface": dict(monitor_no_trade_surface),
        "scanner_monitor_handoff": dict(scanner_monitor_handoff),
        "policy_ref": dict(monitor_policy_trace.get("policy_ref") or {}),
        "entry_check_summary": str(monitor_policy_trace.get("entry_check_summary") or ""),
        "entry_blockers": list(monitor_policy_trace.get("entry_blockers") or []),
        "timing_assessment": dict(monitor_policy_trace.get("timing_assessment") or {}),
        "received_policy": dict(entry_info.get("received_policy") or entry_received_policy or {}),
        "policy_contract": dict(entry_info.get("policy_contract") or entry_policy_contract or {}),
        "effective_policy": dict(entry_info.get("effective_policy") or entry_applied_policy),
        "effective_policy_source": str(entry_info.get("effective_policy_source") or ""),
        "effective_policy_source_chain": list(entry_info.get("effective_policy_source_chain") or []),
        "policy_adjustments": dict(entry_info.get("policy_adjustments") or {}),
        "policy_adjustment_summary": str(entry_info.get("policy_adjustment_summary") or ""),
        "effective_policy_deltas": list(entry_info.get("effective_policy_deltas") or []),
        "commander_context_consumed": bool(monitor_policy_trace.get("commander_context_consumed")),
        "consumed_fields": list(monitor_policy_trace.get("consumed_fields") or []),
        "flow_instruction_applied": bool(monitor_policy_trace.get("flow_instruction_applied")),
        "no_trade_reason_applied": bool(monitor_policy_trace.get("no_trade_reason_applied")),
        "shadow_used": bool(monitor_policy_trace.get("shadow_used")),
        "strategist_fallback_used": bool(monitor_policy_trace.get("strategist_fallback_used")),
    }
    )


def cycle_detail_value_ate_monitor_action_decision(reason_chain, triggered_rules, entry_applied_policy, monitor_no_trade_surface, scanner_monitor_handoff, current_reason, entry_received_policy, entry_policy_contract, entry_info, blocked_rules, monitor_policy_trace, exit_info, state, *, facade):
    return (
{
        "decision": str((state.get("monitor_output") or {}).get("intent_side") or "NOOP"),
        "action_reason_human": str((state.get("monitor_output") or {}).get("entry_exit_reason") or current_reason),
        "decision_reason_chain": list(reason_chain),
        "confidence": float(facade._to_float(entry_info.get("confidence"))),
        "active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
        "triggered_rules": list(triggered_rules),
        "blocked_rules": list(dict.fromkeys(blocked_rules))[:8],
        "received_policy": dict(entry_info.get("received_policy") or entry_received_policy or {}),
        "policy_contract": dict(entry_info.get("policy_contract") or entry_policy_contract or {}),
        "effective_policy": dict(entry_info.get("effective_policy") or entry_applied_policy),
        "effective_policy_source": str(entry_info.get("effective_policy_source") or ""),
        "effective_policy_source_chain": list(entry_info.get("effective_policy_source_chain") or []),
        "policy_adjustments": dict(entry_info.get("policy_adjustments") or {}),
        "policy_adjustment_summary": str(entry_info.get("policy_adjustment_summary") or ""),
        "policy_adjustment_reasoning": str(entry_info.get("policy_adjustment_reasoning") or ""),
        "effective_policy_deltas": list(entry_info.get("effective_policy_deltas") or []),
        "applied_policy": dict(entry_applied_policy),
        "policy_source": str((monitor_policy_trace.get("policy_ref") or {}).get("policy_source") or ""),
        "policy_validation_status": str((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_status") or ""),
        "policy_fallback_used": bool((monitor_policy_trace.get("policy_ref") or {}).get("policy_fallback_used")),
        "policy_fallback_reason": str((monitor_policy_trace.get("policy_ref") or {}).get("policy_fallback_reason") or ""),
        "policy_partial_normalized": bool((monitor_policy_trace.get("policy_ref") or {}).get("policy_partial_normalized")),
        "policy_default_filled_fields": list((monitor_policy_trace.get("policy_ref") or {}).get("policy_default_filled_fields") or []),
        "policy_validation_missing_fields": list((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_missing_fields") or []),
        "policy_validation_invalid_fields": list((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_invalid_fields") or []),
        "override_reason": str((monitor_policy_trace.get("policy_ref") or {}).get("override_reason") or ""),
        "applied_policy_source_chain": list((monitor_policy_trace.get("policy_ref") or {}).get("applied_policy_source_chain") or []),
        "policy_ref": dict(monitor_policy_trace.get("policy_ref") or {}),
        "entry_check_summary": str(monitor_policy_trace.get("entry_check_summary") or ""),
        "entry_blockers": list(monitor_policy_trace.get("entry_blockers") or []),
        "exit_trigger_basis": dict(monitor_policy_trace.get("exit_trigger_basis") or {}),
        "exit_vs_strategy_intent": dict(exit_info.get("exit_vs_strategy_intent") or {}),
        "entry_transition_trace": dict(entry_info.get("entry_transition_trace") or {}),
        "hard_filter_passed": bool(entry_info.get("hard_filter_passed")),
        "hard_filter_fail_reasons": list(entry_info.get("hard_filter_fail_reasons") or []),
        "total_score": entry_info.get("total_score"),
        "score_breakdown": dict(entry_info.get("score_breakdown") or {}),
        "entry_threshold": entry_info.get("entry_threshold"),
        "score_passed": bool(entry_info.get("score_passed")),
        "scoring_mode": str(entry_info.get("scoring_mode") or "disabled"),
        "legacy_entry_decision": str(entry_info.get("legacy_entry_decision") or "WAIT"),
        "scoring_entry_decision": str(entry_info.get("scoring_entry_decision") or "WAIT"),
        "no_trade_surface": dict(monitor_no_trade_surface),
        "scanner_monitor_handoff": dict(scanner_monitor_handoff),
        "commander_context_consumed": bool(monitor_policy_trace.get("commander_context_consumed")),
        "consumed_fields": list(monitor_policy_trace.get("consumed_fields") or []),
        "shadow_used": bool(monitor_policy_trace.get("shadow_used")),
        "strategist_fallback_used": bool(monitor_policy_trace.get("strategist_fallback_used")),
    }
    )
