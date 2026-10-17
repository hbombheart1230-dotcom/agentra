"""Monitor cycle output projection: monitor_output, sizing, quant result and entry/exit snapshots.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def cycle_output_value_state_monitor(order_status, fallback_reasons, order_lifecycle, intents, open_position_count, max_positions, block_buy_open_position, buy_blocked_open_position, buy_blocked_same_symbol, buy_blocked_pending_buy, max_positions_reached, buy_blocked_closeout_window, post_exit_cooldown_sec, buy_blocked_post_exit_cooldown, post_exit_cooldown_remaining_sec, entry_applied_policy, commander_memory_application_trace, entry_candidate_cascade, selected, exit_info, entry_info, entry_received_policy, entry_policy_origin, entry_policy_contract, order_status_meta, sizing_info, state, *, facade):
    return (
{
        "skill_contract_version": facade.SKILL_CONTRACT_VERSION,
        "has_intent": bool(intents),
        "intent_count": len(intents),
        "selected_symbol": (selected.get("symbol") if isinstance(selected, dict) else None),
        "order_status_loaded": bool(order_status),
        "order_status": order_status,
        "order_status_present": bool(order_status_meta.get("present")),
        "order_status_fallback": bool(fallback_reasons),
        "order_status_fallback_reasons": fallback_reasons,
        "order_status_error_count": len(fallback_reasons),
        "order_lifecycle_loaded": bool(order_lifecycle),
        "order_lifecycle": order_lifecycle,
        "exit_policy_enabled": bool(exit_info.get("enabled")),
        "exit_evaluated": bool(exit_info.get("evaluated")),
        "exit_triggered": bool(exit_info.get("triggered")),
        "exit_reason": str(exit_info.get("reason") or ""),
        "exit_vs_strategy_intent": dict(exit_info.get("exit_vs_strategy_intent") or {}),
        "exit_pnl_ratio": exit_info.get("pnl_ratio"),
        "exit_raw_pnl_ratio": exit_info.get("raw_pnl_ratio"),
        "exit_gross_pnl_ratio": exit_info.get("gross_pnl_ratio"),
        "exit_technical_pnl_ratio": exit_info.get("technical_pnl_ratio"),
        "exit_effective_pnl_ratio": exit_info.get("effective_pnl_ratio"),
        "exit_stop_pnl_ratio": exit_info.get("stop_pnl_ratio"),
        "exit_stop_pnl_ratio_source": str(exit_info.get("stop_pnl_ratio_source") or ""),
        "exit_hard_stop_pnl_ratio": exit_info.get("hard_stop_pnl_ratio"),
        "exit_hard_stop_pnl_ratio_source": str(exit_info.get("hard_stop_pnl_ratio_source") or ""),
        "exit_cost_drag_pressure": bool(exit_info.get("cost_drag_pressure")),
        "exit_cost_drag_pressure_pct": exit_info.get("cost_drag_pressure_pct"),
        "exit_cost_drag_pressure_reason": str(exit_info.get("cost_drag_pressure_reason") or ""),
        "exit_stop_loss_cost_drag_blocked": bool(exit_info.get("stop_loss_cost_drag_blocked")),
        "exit_stop_loss_cost_drag_blocked_reason": str(exit_info.get("stop_loss_cost_drag_blocked_reason") or ""),
        "exit_symbol": exit_info.get("symbol"),
        "exit_symbol_fallback": bool(exit_info.get("exit_symbol_fallback")),
        "exit_qty": int(exit_info.get("exit_qty") or exit_info.get("qty") or 0),
        "exit_raw_price": exit_info.get("raw_price"),
        "exit_technical_price": exit_info.get("technical_price"),
        "exit_technical_price_source": str(exit_info.get("technical_price_source") or ""),
        "exit_effective_price": exit_info.get("effective_price"),
        "exit_effective_price_source": str(exit_info.get("effective_price_source") or ""),
        "exit_price_freshness": dict(exit_info.get("price_freshness") or {}),
        "peak_update": (
            dict(state["peak_update_events"][-1])
            if isinstance(state.get("peak_update_events"), list)
            and state.get("peak_update_events")
            else {}
        ),
        "exit_account_current_price": exit_info.get("account_current_price"),
        "exit_account_mark_price": exit_info.get("account_mark_price"),
        "exit_account_unrealized_pnl": exit_info.get("account_unrealized_pnl"),
        "exit_account_pnl_ratio": exit_info.get("account_pnl_ratio"),
        "exit_account_pnl_ratio_source": str(exit_info.get("account_pnl_ratio_source") or ""),
        "exit_pnl_crosscheck_applied": bool(exit_info.get("pnl_crosscheck_applied")),
        "exit_pnl_crosscheck_reason": str(exit_info.get("pnl_crosscheck_reason") or ""),
        "exit_pnl_crosscheck_gap": exit_info.get("pnl_crosscheck_gap"),
        "exit_position_age_seconds": exit_info.get("position_age_seconds"),
        "exit_min_hold_sec": int(exit_info.get("min_hold_sec") or 0),
        "exit_sell_cooldown_sec": int(exit_info.get("sell_cooldown_sec") or 0),
        "exit_confirm_ticks": int(exit_info.get("exit_confirm_ticks") or 0),
        "exit_confirm_count": int(exit_info.get("exit_confirm_count") or 0),
        "exit_min_hold_blocked": bool(exit_info.get("min_hold_blocked")),
        "exit_sell_cooldown_blocked": bool(exit_info.get("sell_cooldown_blocked")),
        "exit_policy_guard_adjustments": list(exit_info.get("exit_policy_guard_adjustments") or []),
        "cost_aware_profit_floor_enabled": bool(exit_info.get("cost_aware_profit_floor_enabled")),
        "round_trip_cost_floor_pct": exit_info.get("round_trip_cost_floor_pct"),
        "min_net_profit_buffer_pct": exit_info.get("min_net_profit_buffer_pct"),
        "cost_aware_profit_floor_pct": exit_info.get("cost_aware_profit_floor_pct"),
        "cost_aware_profit_floor_met": bool(exit_info.get("cost_aware_profit_floor_met")),
        "cost_aware_profit_floor_gap_pct": exit_info.get("cost_aware_profit_floor_gap_pct"),
        "cost_aware_profit_floor_blocked": bool(exit_info.get("cost_aware_profit_floor_blocked")),
        "peak_drawdown_blocked": bool(exit_info.get("peak_drawdown_blocked")),
        "peak_drawdown_block_reason": str(exit_info.get("peak_drawdown_block_reason") or ""),
        "peak_drawdown_profit_floor_required_pct": exit_info.get("peak_drawdown_profit_floor_required_pct"),
        "peak_drawdown_profit_floor_met": bool(exit_info.get("peak_drawdown_profit_floor_met")),
        "exit_expected_exit_price": exit_info.get("expected_exit_price"),
        "exit_expected_exit_price_source": str(exit_info.get("expected_exit_price_source") or ""),
        "exit_expected_exit_price_fallback_used": bool(exit_info.get("expected_exit_price_fallback_used")),
        "exit_expected_exit_quote_rejected": bool(exit_info.get("expected_exit_quote_rejected")),
        "exit_expected_exit_quote_rejected_reason": str(
            exit_info.get("expected_exit_quote_rejected_reason") or ""
        ),
        "exit_expected_exit_quote_age_sec": exit_info.get("expected_exit_quote_age_sec"),
        "exit_expected_exit_quote_price_divergence_pct": exit_info.get(
            "expected_exit_quote_price_divergence_pct"
        ),
        "exit_expected_exit_slippage_buffer_pct": exit_info.get("expected_exit_slippage_buffer_pct"),
        "exit_expected_exit_pnl_ratio": exit_info.get("expected_exit_pnl_ratio"),
        "exit_expected_exit_net_pnl_ratio": exit_info.get("expected_exit_net_pnl_ratio"),
        "exit_expected_exit_profit_floor_met": bool(exit_info.get("expected_exit_profit_floor_met")),
        "exit_expected_exit_profit_floor_gap_pct": exit_info.get("expected_exit_profit_floor_gap_pct"),
        "exit_expected_exit_profit_floor_blocked": bool(exit_info.get("expected_exit_profit_floor_blocked")),
        "exit_expected_exit_profit_floor_blocked_reason": str(
            exit_info.get("expected_exit_profit_floor_blocked_reason") or ""
        ),
        "protective_exit_floor_blocked": bool(exit_info.get("protective_exit_floor_blocked")),
        "protective_exit_floor_blocked_reason": str(exit_info.get("protective_exit_floor_blocked_reason") or ""),
        "protective_exit_hard_invalidation": bool(exit_info.get("protective_exit_hard_invalidation")),
        "protective_exit_hard_invalidation_reason": str(
            exit_info.get("protective_exit_hard_invalidation_reason") or ""
        ),
        "eod_carry_evaluated": bool(exit_info.get("eod_carry_evaluated")),
        "eod_carry_approved": bool(exit_info.get("eod_carry_approved")),
        "eod_carry_action": str(exit_info.get("eod_carry_action") or ""),
        "eod_carry_reason": str(exit_info.get("eod_carry_reason") or ""),
        "position_sizing_enabled": bool(sizing_info.get("enabled")),
        "position_sizing_evaluated": bool(sizing_info.get("evaluated")),
        "position_sizing_qty": int(sizing_info.get("qty") or 0),
        "position_sizing_reason": str(sizing_info.get("reason") or ""),
        "position_sizing_stop_loss_pct": (sizing_info.get("inputs") or {}).get("stop_loss_pct")
        if isinstance(sizing_info.get("inputs"), dict)
        else None,
        "position_sizing_stop_loss_source": str(
            ((sizing_info.get("inputs") or {}).get("stop_loss_source") if isinstance(sizing_info.get("inputs"), dict) else "")
            or ""
        ),
        "position_sizing_invalidation_price": (sizing_info.get("inputs") or {}).get("invalidation_price")
        if isinstance(sizing_info.get("inputs"), dict)
        else None,
        "open_position_count": int(open_position_count),
        "max_positions": int(max_positions),
        "multi_position_capacity_remaining": max(0, int(max_positions) - int(open_position_count)),
        "block_buy_when_open_position": bool(block_buy_open_position),
        "buy_blocked_open_position": bool(buy_blocked_open_position),
        "buy_blocked_same_symbol": bool(buy_blocked_same_symbol),
        "buy_blocked_pending_buy": bool(buy_blocked_pending_buy),
        "max_positions_reached": bool(max_positions_reached),
        "buy_blocked_closeout_window": bool(buy_blocked_closeout_window),
        "post_exit_cooldown_sec": int(post_exit_cooldown_sec),
        "buy_blocked_post_exit_cooldown": bool(buy_blocked_post_exit_cooldown),
        "post_exit_cooldown_remaining_sec": int(post_exit_cooldown_remaining_sec),
        "minutes_to_close": entry_info.get("minutes_to_close"),
        "eod_flat_cutoff_min": int(entry_info.get("eod_flat_cutoff_min") or 0),
        "buy_closeout_cutoff_min": int(entry_info.get("buy_closeout_cutoff_min") or 0),
        "closeout_window_active": bool(entry_info.get("closeout_window_active")),
        "entry_evaluated": bool(entry_info.get("evaluated")),
        "entry_triggered": bool(entry_info.get("triggered")),
        "entry_reason": str(entry_info.get("reason") or ""),
        "entry_pattern": str(entry_info.get("pattern") or ""),
        "entry_signal_chain": list(entry_info.get("signal_chain") or []),
        "entry_condition_path": str(entry_info.get("entry_condition_path") or ""),
        "entry_condition_paths_passed": list(entry_info.get("entry_condition_paths_passed") or []),
        "entry_condition_scores": dict(entry_info.get("condition_scores") or {}),
        "entry_grouped_logic_trace": dict(entry_info.get("grouped_logic_trace") or {}),
        "entry_metrics": dict(entry_info.get("metrics") or {}),
        "entry_received_policy": dict(entry_info.get("received_policy") or entry_received_policy or {}),
        "entry_received_policy_source": str(entry_info.get("received_policy_source") or entry_policy_origin or ""),
        "entry_policy_contract": dict(entry_info.get("policy_contract") or entry_policy_contract or {}),
        "entry_applied_policy": dict(entry_applied_policy),
        "entry_effective_policy": dict(entry_info.get("effective_policy") or entry_applied_policy),
        "entry_effective_policy_source": str(entry_info.get("effective_policy_source") or ""),
        "entry_effective_policy_source_chain": list(entry_info.get("effective_policy_source_chain") or []),
        "commander_entry_control": dict(entry_info.get("commander_entry_control") or {}),
        "entry_policy_adjustments": dict(entry_info.get("policy_adjustments") or {}),
        "entry_policy_adjustment_summary": str(entry_info.get("policy_adjustment_summary") or ""),
        "entry_effective_policy_deltas": list(entry_info.get("effective_policy_deltas") or []),
        "monitor_memory_bias_applied": bool(entry_info.get("monitor_memory_bias_applied")),
        "monitor_memory_bias_observation_only": bool(entry_info.get("monitor_memory_bias_observation_only")),
        "monitor_memory_bias": dict(entry_info.get("monitor_memory_bias") or {}),
        "monitor_memory_bias_summary": dict(entry_info.get("monitor_memory_bias_summary") or {}),
        "monitor_memory_bias_deltas": list(entry_info.get("monitor_memory_bias_deltas") or []),
        "monitor_memory_bias_observed_deltas": list(entry_info.get("monitor_memory_bias_observed_deltas") or []),
        "monitor_memory_bias_hold_applied": bool(exit_info.get("monitor_memory_bias_hold_applied")),
        "monitor_memory_bias_hold_deltas": list(exit_info.get("monitor_memory_bias_hold_deltas") or []),
        "monitor_memory_bias_exit_applied": bool(exit_info.get("monitor_memory_bias_exit_applied")),
        "monitor_memory_bias_exit_deltas": list(exit_info.get("monitor_memory_bias_exit_deltas") or []),
        "commander_memory_application_trace": dict(commander_memory_application_trace),
        "monitor_memory_application_trace": dict(commander_memory_application_trace),
        "entry_thresholds": dict(entry_info.get("thresholds") or {}),
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
        "entry_lane": str(entry_info.get("entry_lane") or "strict"),
        "entry_cost_filter": dict(entry_info.get("entry_cost_filter") or {}),
        "directional_edge_estimate": dict(
            entry_info.get("directional_edge_estimate") or {}
        ),
        "entry_quality_gate": dict(entry_info.get("entry_quality_gate") or {}),
        "cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
        "cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
        "cost_drag_pct": entry_info.get("cost_drag_pct"),
        "entry_score_threshold": entry_info.get("entry_threshold"),
        "entry_score_passed": bool(entry_info.get("score_passed")),
        "entry_scoring_mode": str(entry_info.get("scoring_mode") or "disabled"),
        "entry_legacy_decision": str(entry_info.get("legacy_entry_decision") or "WAIT"),
        "entry_scoring_decision": str(entry_info.get("scoring_entry_decision") or "WAIT"),
        "entry_guard_blocked": bool(entry_info.get("guard_blocked")),
        "entry_guard_reason": str(entry_info.get("guard_reason") or ""),
        "entry_intent_submitted": bool(entry_info.get("intent_submitted")),
        "entry_legacy_fallback_used": bool(entry_info.get("legacy_fallback_used")),
        "entry_intent_cooldown_sec": int(entry_info.get("intent_cooldown_sec") or 0),
        "entry_intent_cooldown_until": entry_info.get("intent_cooldown_until"),
        "entry_candidate_cascade": dict(entry_candidate_cascade),
    }
    )


def cycle_output_monitor_entry_exit_reason_quant_entry_de(buy_blocked_post_exit_cooldown, buy_blocked_closeout_window, exit_info, buy_blocked_pending_buy, buy_blocked_same_symbol, max_positions_reached, buy_blocked_open_position, entry_info, strategist_output, strategist_plan, selected, state, *, facade):
    if bool(exit_info.get("enabled")) and bool(exit_info.get("exit_signal_detected")):
        monitor_entry_exit_reason = str(exit_info.get("reason") or "")
    elif bool(buy_blocked_post_exit_cooldown):
        monitor_entry_exit_reason = "post_exit_cooldown"
    elif bool(buy_blocked_closeout_window):
        monitor_entry_exit_reason = "buy_blocked_closeout_window"
    elif bool(buy_blocked_pending_buy):
        monitor_entry_exit_reason = "same_symbol_pending_buy"
    elif bool(buy_blocked_same_symbol):
        monitor_entry_exit_reason = "same_symbol_position_open"
    elif bool(max_positions_reached and buy_blocked_open_position):
        monitor_entry_exit_reason = "max_positions_reached"
    elif bool(buy_blocked_open_position) and str(entry_info.get("guard_reason") or "").strip() in {
        "closeout_unresolved_flatten_required",
        "overnight_carry_recovery_pending",
    }:
        monitor_entry_exit_reason = str(entry_info.get("guard_reason") or "")
    elif bool(buy_blocked_open_position):
        monitor_entry_exit_reason = "buy_blocked_open_position"
    elif bool(entry_info.get("guard_blocked")):
        monitor_entry_exit_reason = str(entry_info.get("guard_reason") or "")
    else:
        monitor_entry_exit_reason = str(entry_info.get("reason") or "entry_wait")
    tactic_id = str(
        strategist_output.get("tactical_strategy")
        or strategist_plan.get("tactical_strategy")
        or ""
    )
    tactic_playbook = str(strategist_output.get("playbook") or strategist_plan.get("selected_playbook") or "")
    quant_entry_factor_snapshot = (
        dict(entry_info.get("quant_factor_snapshot") or {})
        if isinstance(entry_info.get("quant_factor_snapshot"), dict)
        else facade.build_factor_snapshot_from_monitor_entry(
            entry_info,
            selected=selected if isinstance(selected, dict) else {},
            tactic_id=tactic_id,
            playbook=tactic_playbook,
        )
    )
    quant_entry_decision = (
        dict(entry_info.get("entry_quant_decision") or {})
        if isinstance(entry_info.get("entry_quant_decision"), dict)
        else facade.build_entry_quant_decision(
            entry_info,
            selected=selected if isinstance(selected, dict) else {},
            factor_snapshot=quant_entry_factor_snapshot,
            state=state,
            tactic_id=tactic_id,
            playbook=tactic_playbook,
        )
    )
    quant_entry_enforcement = (
        dict(entry_info.get("quant_entry_enforcement") or {})
        if isinstance(entry_info.get("quant_entry_enforcement"), dict)
        else facade.build_entry_quant_enforcement(quant_entry_decision)
    )
    quant_exit_decision = facade.build_exit_quant_decision(
        exit_info,
        state=state,
        tactic_id=tactic_id,
        playbook=tactic_playbook,
    )
    return (monitor_entry_exit_reason, quant_entry_decision, quant_entry_enforcement, quant_entry_factor_snapshot, quant_exit_decision)
