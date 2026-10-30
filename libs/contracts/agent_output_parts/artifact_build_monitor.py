from __future__ import annotations
from typing import Any, Dict, List


def build_monitor_output_artifact(state: Dict[str, Any], facade) -> Dict[str, Any]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    entry_detail, entry_info, exit_detail, exit_info, monitor, monitor_focus_state, monitor_output, scanner_selected_snapshot, selected, trace_sources, transition = monitor_state_surface_sources(state=state)

    def _first_trace_dict(key: str) -> Dict[str, Any]:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, dict) and value:
                return dict(value)
        return {}

    def _first_trace_list(key: str) -> List[Any]:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, list) and value:
                return list(value)
        return []

    def _first_trace_text(key: str) -> str:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _first_trace_bool(key: str) -> Any:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, bool):
                return value
        return None

    def _first_trace_value(key: str) -> Any:
        for source in trace_sources:
            if key not in source:
                continue
            value = source.get(key)
            if value not in (None, "", [], {}):
                return value
        return None

    exit_vs_strategy_intent, monitor_no_trade_surface, policy_trace = monitor_no_trade_policy_trace(_first_trace_dict=_first_trace_dict, _first_trace_text=_first_trace_text, _first_trace_list=_first_trace_list, _first_trace_bool=_first_trace_bool)
    if not monitor_no_trade_surface:
        commander_decision = _dict(state.get("commander_decision"))
        monitor_no_trade_surface = build_monitor_no_trade_surface(
            entry_info,
            final_decision=str(monitor_output.get("intent_side") or "NOOP").strip().upper() or "WAIT",
            buy_submitted=str(monitor_output.get("intent_side") or "").strip().upper() == "BUY",
            guard_blocked=bool(entry_info.get("guard_blocked")),
            guard_reason=entry_info.get("guard_reason"),
            commander_no_trade_reason_code=commander_decision.get("no_trade_reason_code"),
        )
    entry_blocker_surface, entry_candidate_cascade, first_intent, intent_side, intents, monitor_focus_context, open_position_count, scanner_monitor_handoff, symbol, thresholds, watch_axes = monitor_entry_cascade_handoff(_first_trace_dict=_first_trace_dict, monitor_no_trade_surface=monitor_no_trade_surface, entry_info=entry_info, scanner_selected_snapshot=scanner_selected_snapshot, selected=selected, state=state, monitor_output=monitor_output, _first_trace_list=_first_trace_list, monitor=monitor, exit_info=exit_info, monitor_focus_state=monitor_focus_state, facade=facade)
    if not monitor_focus_context:
        monitor_focus_context = monitor_focus_context_projection(monitor_output=monitor_output, entry_info=entry_info, selected=selected, scanner_monitor_handoff=scanner_monitor_handoff, exit_info=exit_info, open_position_count=open_position_count, monitor=monitor, monitor_focus_context=monitor_focus_context)[0]
    blocked_rules, decision_action, decision_phase, decision_reason_chain, decision_status, entry_chart_structure_features, entry_minute_refetch_attempted, entry_minute_refetch_failure_detail, entry_minute_refetch_failure_reason, entry_minute_refetch_runner_source, entry_minute_refetch_succeeded, entry_minute_source_present, entry_minute_source_used, entry_policy_alignment_summary, entry_policy_interpreter_trace, evidence_quality, feature_source, missing_inputs, posture, price_source, primary_reason_code, secondary_reason_codes, threshold_snapshot, triggered_rules = monitor_decision_rule_evidence(exit_info=exit_info, entry_info=entry_info, state=state, transition=transition, monitor_output=monitor_output, entry_detail=entry_detail, symbol=symbol, intent_side=intent_side, open_position_count=open_position_count, exit_detail=exit_detail, thresholds=thresholds, monitor=monitor, _first_trace_value=_first_trace_value, facade=facade)
    commander_memory_application_trace, decision_summary, market_snapshot_refs, monitor_memory_bias, monitor_memory_bias_applied, monitor_memory_bias_deltas, monitor_memory_bias_exit_applied, monitor_memory_bias_exit_deltas, monitor_memory_bias_hold_applied, monitor_memory_bias_hold_deltas, monitor_memory_bias_summary, signal_snapshot = monitor_memory_bias_application(_first_trace_value=_first_trace_value, threshold_snapshot=threshold_snapshot, policy_trace=policy_trace, _first_trace_dict=_first_trace_dict, entry_info=entry_info, exit_info=exit_info, decision_phase=decision_phase, missing_inputs=missing_inputs, primary_reason_code=primary_reason_code, symbol=symbol, price_source=price_source, feature_source=feature_source, selected=selected, facade=facade)
    artifact = _base_output(state, agent="monitor", symbol=symbol)
    artifact.update(
        {
            **monitor_artifact_decision_fields(decision_action=decision_action, decision_phase=decision_phase, decision_status=decision_status, decision_summary=decision_summary, exit_info=exit_info, exit_vs_strategy_intent=exit_vs_strategy_intent, monitor_output=monitor_output, open_position_count=open_position_count, primary_reason_code=primary_reason_code, secondary_reason_codes=secondary_reason_codes, state=state, symbol=symbol, thresholds=thresholds),
            **monitor_artifact_no_trade_fields(monitor_no_trade_surface=monitor_no_trade_surface),
            **monitor_artifact_handoff_focus_fields(entry_blocker_surface=entry_blocker_surface, entry_candidate_cascade=entry_candidate_cascade, monitor_focus_context=monitor_focus_context, scanner_monitor_handoff=scanner_monitor_handoff, threshold_snapshot=threshold_snapshot),
            **monitor_artifact_policy_memory_fields(commander_memory_application_trace=commander_memory_application_trace, entry_info=entry_info, monitor_memory_bias=monitor_memory_bias, monitor_memory_bias_applied=monitor_memory_bias_applied, monitor_memory_bias_deltas=monitor_memory_bias_deltas, monitor_memory_bias_exit_applied=monitor_memory_bias_exit_applied, monitor_memory_bias_exit_deltas=monitor_memory_bias_exit_deltas, monitor_memory_bias_hold_applied=monitor_memory_bias_hold_applied, monitor_memory_bias_hold_deltas=monitor_memory_bias_hold_deltas, monitor_memory_bias_summary=monitor_memory_bias_summary, policy_trace=policy_trace),
            **monitor_artifact_signal_entry_fields(entry_chart_structure_features=entry_chart_structure_features, entry_info=entry_info, entry_minute_refetch_attempted=entry_minute_refetch_attempted, entry_minute_refetch_failure_detail=entry_minute_refetch_failure_detail, entry_minute_refetch_failure_reason=entry_minute_refetch_failure_reason, entry_minute_refetch_runner_source=entry_minute_refetch_runner_source, entry_minute_refetch_succeeded=entry_minute_refetch_succeeded, entry_minute_source_present=entry_minute_source_present, entry_minute_source_used=entry_minute_source_used, entry_policy_alignment_summary=entry_policy_alignment_summary, entry_policy_interpreter_trace=entry_policy_interpreter_trace, market_snapshot_refs=market_snapshot_refs, policy_trace=policy_trace, signal_snapshot=signal_snapshot),
            **monitor_artifact_trace_evaluation_fields(blocked_rules=blocked_rules, decision_reason_chain=decision_reason_chain, entry_info=entry_info, evidence_quality=evidence_quality, exit_info=exit_info, exit_vs_strategy_intent=exit_vs_strategy_intent, first_intent=first_intent, intents=intents, missing_inputs=missing_inputs, monitor_output=monitor_output, policy_trace=policy_trace, posture=posture, thresholds=thresholds, triggered_rules=triggered_rules, watch_axes=watch_axes, facade=facade),
            **monitor_artifact_price_exit_metric_fields(exit_info=exit_info, feature_source=feature_source, price_source=price_source),
            **monitor_artifact_pnl_hold_exit_fields(exit_info=exit_info, watch_axes=watch_axes),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact
