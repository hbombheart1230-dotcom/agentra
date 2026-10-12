"""Monitor focus, entry/exit decision detail and evaluation projections.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def cycle_detail_entry_candidate_symbol_entry_cost_filter(scanner_monitor_handoff, scanner_selected_snapshot, entry_info, selected, entry_candidate_cascade, exit_info, monitor_symbol, final_entry_decision, open_position_count, max_positions, held_symbols_for_entry, pending_buy_symbols_for_entry, buy_submitted, *, facade):
    scanner_selected_symbol = str(
        scanner_monitor_handoff.get("scanner_selected_symbol")
        or (scanner_selected_snapshot.get("symbol") if isinstance(scanner_selected_snapshot, dict) else "")
        or ""
    ).strip()
    entry_candidate_symbol = str(
        entry_info.get("selected_symbol")
        or entry_info.get("symbol")
        or ((selected or {}).get("symbol") if isinstance(selected, dict) else "")
        or ""
    ).strip()
    entry_final_symbol = str(
        entry_candidate_cascade.get("final_selected_symbol")
        or ((selected or {}).get("symbol") if isinstance(selected, dict) else "")
        or entry_candidate_symbol
        or ""
    ).strip()
    position_focus_symbol = str(exit_info.get("symbol") or "").strip()
    monitor_output_symbol = str(monitor_symbol or position_focus_symbol or entry_final_symbol or "").strip()
    entry_cost_filter_snapshot = (
        dict(entry_info.get("entry_cost_filter") or {})
        if isinstance(entry_info.get("entry_cost_filter"), dict)
        else {}
    )
    if position_focus_symbol and entry_final_symbol and position_focus_symbol != entry_final_symbol:
        monitor_focus_mode = "entry_candidate_and_position_focus"
    elif position_focus_symbol:
        monitor_focus_mode = "position_focus"
    elif entry_final_symbol:
        monitor_focus_mode = "entry_candidate_focus"
    else:
        monitor_focus_mode = "no_symbol_focus"
    monitor_focus_context = {
        "schema_version": "monitor.focus_context.v1",
        "focus_mode": monitor_focus_mode,
        "scanner_selected_symbol": scanner_selected_symbol,
        "entry_candidate_symbol": entry_candidate_symbol,
        "entry_final_symbol": entry_final_symbol,
        "position_focus_symbol": position_focus_symbol,
        "monitor_output_symbol": monitor_output_symbol,
        "open_position_count": int(open_position_count),
        "max_positions": int(max_positions),
        "capacity_remaining": max(0, int(max_positions) - int(open_position_count)),
        "held_symbols": sorted(held_symbols_for_entry),
        "pending_buy_symbols": sorted(pending_buy_symbols_for_entry),
        "entry_evaluated": bool(entry_info.get("evaluated")),
        "entry_decision": final_entry_decision,
        "entry_triggered": bool(entry_info.get("triggered")),
        "entry_intent_submitted": bool(buy_submitted),
        "entry_guard_blocked": bool(entry_info.get("guard_blocked")),
        "entry_guard_reason": str(entry_info.get("guard_reason") or ""),
        "entry_reason": str(entry_info.get("reason") or ""),
        "entry_primary_failure_axis": str(entry_info.get("primary_failure_axis") or ""),
        "entry_cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
        "entry_cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
        "entry_cost_drag_pct": entry_info.get("cost_drag_pct"),
        "entry_cost_filter": dict(entry_cost_filter_snapshot),
        "exit_evaluated": bool(exit_info.get("evaluated")),
        "exit_triggered": bool(exit_info.get("triggered")),
        "exit_reason": str(exit_info.get("reason") or ""),
        "exit_monitor_reason": str(exit_info.get("monitor_reason") or ""),
        "exit_active_axis": str(exit_info.get("active_exit_axis") or ""),
    }
    return (entry_candidate_symbol, entry_cost_filter_snapshot, entry_final_symbol, monitor_focus_context, monitor_focus_mode, monitor_output_symbol, position_focus_symbol, scanner_selected_symbol)


def cycle_detail_entry_decision_detail(final_entry_decision, buy_skipped_reason, entry_event_metrics, scanner_selected_symbol, entry_candidate_symbol, entry_final_symbol, position_focus_symbol, monitor_output_symbol, monitor_focus_mode, buy_submitted, entry_applied_policy, monitor_no_trade_surface, scanner_monitor_handoff, entry_candidate_cascade, entry_blocker_surface, quant_entry_factor_snapshot, quant_entry_decision, quant_entry_enforcement, monitor_focus_context, entry_policy_contract, entry_info, monitor_policy_trace, *, facade):
    entry_decision_detail = {
        "decision": final_entry_decision,
        "reason": str(entry_info.get("guard_reason") or entry_info.get("reason") or "entry_wait"),
        "entry_evaluated": bool(entry_info.get("evaluated")),
        "entry_triggered": bool(entry_info.get("triggered")),
        "entry_pattern": str(entry_info.get("pattern") or ""),
        "entry_reason": str(entry_info.get("reason") or ""),
        "signal_chain": list(entry_info.get("signal_chain") or []),
        "entry_condition_path": str(entry_info.get("entry_condition_path") or ""),
        "entry_condition_paths_passed": list(entry_info.get("entry_condition_paths_passed") or []),
        "condition_scores": dict(entry_info.get("condition_scores") or {}),
        "grouped_logic_trace": dict(entry_info.get("grouped_logic_trace") or {}),
        "guard_blocked": bool(entry_info.get("guard_blocked")),
        "guard_reason": str(entry_info.get("guard_reason") or ""),
        "buy_submitted": bool(buy_submitted),
        "buy_skipped_reason": buy_skipped_reason,
        "previous_close": entry_event_metrics.get("previous_close"),
        "session_open": entry_event_metrics.get("session_open"),
        "open_gap_pct": entry_event_metrics.get("open_gap_pct"),
        "prev_close_distance_pct": entry_event_metrics.get("prev_close_distance_pct"),
        "minutes_since_session_open": entry_event_metrics.get("minutes_since_session_open"),
        "opening_gap_chase_observed": bool(entry_event_metrics.get("opening_gap_chase_observed")),
        "opening_gap_context_observation_only": bool(entry_event_metrics.get("opening_gap_context_observation_only")),
        "metrics": entry_event_metrics,
        "applied_policy": dict(entry_applied_policy),
        "policy_contract": dict(entry_info.get("policy_contract") or entry_policy_contract or {}),
        "thresholds": dict(entry_info.get("thresholds") or {}),
        "passed_checks": list(entry_info.get("passed_checks") or []),
        "failed_checks": list(entry_info.get("failed_checks") or []),
        "primary_failure_axis": str(entry_info.get("primary_failure_axis") or ""),
        "threshold_margins": dict(entry_info.get("threshold_margins") or {}),
        "transition_trace": dict(entry_info.get("entry_transition_trace") or {}),
        "hard_filter_passed": bool(entry_info.get("hard_filter_passed")),
        "hard_filter_fail_reasons": list(entry_info.get("hard_filter_fail_reasons") or []),
        "total_score": entry_info.get("total_score"),
        "score_breakdown": dict(entry_info.get("score_breakdown") or {}),
        "policy_interpretation": dict(entry_info.get("policy_interpretation") or {}),
        "signal_evidence": dict(entry_info.get("signal_evidence") or {}),
        "chart_structure_features": dict(entry_info.get("chart_structure_features") or {}),
        "policy_interpreter_trace": dict(entry_info.get("policy_interpreter_trace") or {}),
        "policy_alignment_summary": dict(entry_info.get("policy_alignment_summary") or {}),
        "policy_aware_gating": dict(entry_info.get("policy_aware_gating") or {}),
        "chart_structure_decision_hint": dict(entry_info.get("chart_structure_decision_hint") or {}),
        "entry_lane": str(entry_info.get("entry_lane") or "strict"),
        "entry_cost_filter": dict(entry_info.get("entry_cost_filter") or {}),
        "cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
        "cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
        "cost_drag_pct": entry_info.get("cost_drag_pct"),
        "monitor_memory_bias_observation_only": bool(entry_info.get("monitor_memory_bias_observation_only")),
        "monitor_memory_bias_observed_deltas": list(entry_info.get("monitor_memory_bias_observed_deltas") or []),
        "minute_source_meta": dict(entry_info.get("minute_source_meta") or {}),
        "minute_fetch_meta": dict(entry_info.get("minute_fetch_meta") or {}),
        "no_trade_surface": dict(monitor_no_trade_surface),
        "scanner_monitor_handoff": dict(scanner_monitor_handoff),
        "entry_candidate_cascade": dict(entry_candidate_cascade),
        "entry_blocker_surface": dict(entry_blocker_surface),
        "quant_factor_snapshot": dict(quant_entry_factor_snapshot),
        "entry_quant_decision": dict(quant_entry_decision),
        "quant_entry_enforcement": dict(quant_entry_enforcement),
        "monitor_focus_context": dict(monitor_focus_context),
        "scanner_selected_symbol": scanner_selected_symbol,
        "entry_candidate_symbol": entry_candidate_symbol,
        "entry_final_symbol": entry_final_symbol,
        "position_focus_symbol": position_focus_symbol,
        "monitor_output_symbol": monitor_output_symbol,
        "monitor_focus_mode": monitor_focus_mode,
        "entry_threshold": entry_info.get("entry_threshold"),
        "score_passed": bool(entry_info.get("score_passed")),
        "scoring_mode": str(entry_info.get("scoring_mode") or "disabled"),
        "legacy_entry_decision": str(entry_info.get("legacy_entry_decision") or "WAIT"),
        "scoring_entry_decision": str(entry_info.get("scoring_entry_decision") or "WAIT"),
        "policy_ref": dict(monitor_policy_trace.get("policy_ref") or {}),
        "entry_check_summary": str(monitor_policy_trace.get("entry_check_summary") or ""),
        "entry_blockers": list(monitor_policy_trace.get("entry_blockers") or []),
        "commander_context_consumed": bool(monitor_policy_trace.get("commander_context_consumed")),
        "consumed_fields": list(monitor_policy_trace.get("consumed_fields") or []),
        "flow_instruction_applied": bool(monitor_policy_trace.get("flow_instruction_applied")),
        "no_trade_reason_applied": bool(monitor_policy_trace.get("no_trade_reason_applied")),
        "shadow_used": bool(monitor_policy_trace.get("shadow_used")),
        "strategist_fallback_used": bool(monitor_policy_trace.get("strategist_fallback_used")),
    }
    return (entry_decision_detail,)


def cycle_detail_scoring_event_payload(final_entry_decision, monitor_no_trade_surface, scanner_monitor_handoff, entry_blocker_surface, monitor_symbol, entry_symbol, entry_info, state, *, facade):
    scoring_event_payload = {
        "run_id": str(state.get("run_id") or ""),
        "symbol": str(monitor_symbol or entry_symbol or ""),
        "hard_filter_passed": bool(entry_info.get("hard_filter_passed")),
        "hard_filter_fail_reasons": list(entry_info.get("hard_filter_fail_reasons") or []),
        "score_breakdown": dict(entry_info.get("score_breakdown") or {}),
        "policy_interpretation": dict(entry_info.get("policy_interpretation") or {}),
        "signal_evidence": dict(entry_info.get("signal_evidence") or {}),
        "chart_structure_features": dict(entry_info.get("chart_structure_features") or {}),
        "policy_interpreter_trace": dict(entry_info.get("policy_interpreter_trace") or {}),
        "policy_alignment_summary": dict(entry_info.get("policy_alignment_summary") or {}),
        "policy_aware_gating": dict(entry_info.get("policy_aware_gating") or {}),
        "chart_structure_decision_hint": dict(entry_info.get("chart_structure_decision_hint") or {}),
        "minute_source_meta": dict(entry_info.get("minute_source_meta") or {}),
        "minute_fetch_meta": dict(entry_info.get("minute_fetch_meta") or {}),
        "total_score": entry_info.get("total_score"),
        "entry_threshold": entry_info.get("entry_threshold"),
        "score_passed": bool(entry_info.get("score_passed")),
        "scoring_mode": str(entry_info.get("scoring_mode") or "disabled"),
        "legacy_entry_decision": str(entry_info.get("legacy_entry_decision") or "WAIT"),
        "scoring_entry_decision": str(entry_info.get("scoring_entry_decision") or "WAIT"),
        "final_decision": final_entry_decision,
        "primary_reason_code": str(entry_info.get("reason") or ""),
        "no_trade_surface": dict(monitor_no_trade_surface),
        "scanner_monitor_handoff": dict(scanner_monitor_handoff),
        "entry_blocker_surface": dict(entry_blocker_surface),
    }
    return (scoring_event_payload,)
