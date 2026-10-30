from typing import Any, Dict, List


def required_keys_for_agent(agent: str, *, facade) -> List[str]:
    base = ["schema_version", "agent", "run_id", "day", "ts", "phase", "status"]
    specific = {
        "strategist": ["market_regime", "market_context_summary", "news_evidence_summary", "sentiment_evidence_summary", "volatility_context", "strategy_thesis", "playbook", "market_context", "news_context", "strategy_frame", "policy_selected", "llm_trace", "decision_summary", "llm_metadata_summary", "source_refs"],
        "scanner": ["candidate_pool_snapshot", "filter_funnel", "universe_size", "candidate_list_summary", "ranking_table", "selected_symbol", "selected_rank", "selection_reason", "selection_reason_detail", "rejection_summary", "filter_feature_summary", "evidence_refs"],
        "monitor": ["position_snapshot", "monitor_evaluation", "monitor_action_decision", "thresholds_guards_used", "threshold_snapshot", "signal_snapshot", "market_snapshot_refs", "evaluation_summary", "decision", "decision_phase", "decision_action", "decision_status", "decision_summary", "primary_reason_code", "primary_reason_text", "secondary_reason_codes", "intent_emitted", "evidence_quality", "missing_inputs", "generated_at", "decision_reason_chain", "trigger_details", "evidence_refs"],
        "supervisor": ["invoked_agents", "command", "decision", "approval_result", "reason", "blocked_allowed_details"],
        "executor": ["action", "order_request_summary", "execution_enabled", "approval_mode", "broker_result", "final_execution_status", "failure_reason"],
        "commander": ["mode", "phase", "path", "runtime_mode", "runtime_phase", "selected_route", "route_reason_codes", "route_reason_text", "open_position_count", "open_position_symbols", "strategist_cache_used", "strategist_blocked", "cooldown_applied", "incident_state", "portfolio_preflight_result", "generated_at", "session_type", "market_clock_phase", "portfolio_state_summary", "market_regime_summary", "goal", "agent_invocation_plan", "decision_checkpoints", "final_runtime_path", "final_reason", "handoff_instruction", "invoked_agents", "command", "decision", "approval_result", "reason", "blocked_allowed_details"],
    }
    return list(base) + list(specific.get(str(agent or "").strip().lower(), []))


def required_keys_for_artifact(obj: Dict[str, Any], *, facade) -> List[str]:
    artifact = dict(obj or {}) if isinstance(obj, dict) else {}
    agent = str(artifact.get("agent") or "").strip().lower()
    mode = str(artifact.get("mode") or "").strip().lower()
    if agent == "commander" and (mode == "shadow" or bool(artifact.get("shadow_only"))):
        return ["schema_version", "agent", "run_id", "day", "ts", "phase", "status", "mode", "decision", "strategist_action_recommendation", "llm_call_advice", "suggested_action", "next_action_recommendation", "no_trade_reason_code", "reason_summary", "observations", "actual_runtime", "monitor_gate_details", "context_delta_summary", "pre_strategist_shadow_snapshot", "post_strategist_assessment", "post_monitor_assessment", "end_of_cycle_summary", "shadow_only", "generated_at"]
    return facade._required_keys_for_agent(agent)


def validate_artifact(artifact: Dict[str, Any], *, facade) -> Dict[str, Any]:
    obj = dict(artifact or {}) if isinstance(artifact, dict) else {}
    expected = facade._required_keys_for_artifact(obj)
    present, missing = [], []
    for key in expected:
        (present if facade._is_present(obj.get(key)) else missing).append(key)
    completeness = float(len(present)) / float(len(expected)) if expected else 1.0
    status = "ok" if not missing else ("invalid" if not present else "partial")
    return {"schema_version": facade.AGENT_VALIDATION_SCHEMA_VERSION, "status": status, "required_keys_expected": expected, "required_keys_present": present, "required_keys_missing": missing, "completeness_score": completeness}
