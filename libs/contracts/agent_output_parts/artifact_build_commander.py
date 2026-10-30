from __future__ import annotations
from typing import Any, Dict, List


def build_commander_output_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
 facade) -> Dict[str, Any]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    allowed_playbooks, banned_playbooks, commander_decision, commander_market_regime, commander_risk_mode, commander_session_bias, cooldown_applied, cooldown_until_epoch, decision_frame, handoff_instruction, open_symbols, phase_text, portfolio_snapshot, positions, preflight, resilience, route_reason_codes, runtime_fast_path, runtime_plan, selected_route, shadow_assessment, strategist_blocked, strategist_cache_used, strategist_output = commander_route_runtime_facts(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=facade)
    decision_summary, llm_invocation_policy, monitor_mission, post_scanner_refresh_context, post_scanner_refresh_reason, post_scanner_refresh_requested, runtime_cache_reuse_context, runtime_cache_reuse_reason, runtime_refresh_context, runtime_refresh_reason, runtime_refresh_requested, scanner_mission, shadow_alignment, shadow_assessment_summary, shadow_reason_code, shadow_runtime, source_priority, strategist_cache_preference_context, strategist_cache_preference_reason, strategist_cache_preferred, strategist_fallback_used, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested = commander_decision_refresh_facts(commander_decision=commander_decision, reason=reason, decision_frame=decision_frame, state=state, shadow_assessment=shadow_assessment, runtime_fast_path=runtime_fast_path, strategist_cache_used=strategist_cache_used)
    applied_policy, applied_policy_source_chain, commander_applied_policy_summary, commander_horizon_policy, horizon_context, llm_policy_source, override_action, override_context, override_reason, override_triggered, policy_default_filled_fields, policy_fallback_reason, policy_fallback_used, policy_partial_normalized, policy_source, policy_sources, policy_validation_invalid_fields, policy_validation_missing_fields, policy_validation_status, reporter_feedback_mode, reporter_feedback_mode_reason, reporter_feedback_mode_source, reporter_feedback_semantics, strategist_runtime_policy_source = commander_applied_policy_provenance(commander_decision=commander_decision, state=state)
    llm_execution_profile_source = _clip(commander_decision.get("llm_execution_profile_source"), max_len=80)
    reporter_policy_source = _clip(commander_decision.get("reporter_policy_source"), max_len=80)
    monitor_policy_source = _clip(commander_decision.get("monitor_policy_source"), max_len=80)
    scanner_policy_source = _clip(commander_decision.get("scanner_policy_source"), max_len=80)
    execution_policy_source = _clip(commander_decision.get("execution_policy_source"), max_len=80)
    route_observability = (
        _dict(state.get("commander_route_observability"))
        or build_commander_route_observability_surface(
            selected_route=selected_route,
            route_reason=decision_summary,
            commander_decision=commander_decision,
            runtime_fast_path=runtime_fast_path,
            resilience=resilience,
            runtime_status=state.get("runtime_status"),
            runtime_transition=state.get("runtime_transition"),
        )
    )
    observations = {
        **_dict(commander_decision.get("observations")),
        **_commander_shadow_observations(state, path=path),
    }

    # Determine actual invocation and strategy source for explicit ownership
    actual_strategist_invocation = shadow_runtime.get("strategist_executed")
    if actual_strategist_invocation is None:
        actual_strategist_invocation = not strategist_cache_used and selected_route not in ("monitor_only", "blocked")
    actual_strategy_source = "cached_strategist" if strategist_cache_used else ("fresh_strategist" if actual_strategist_invocation else "none")

    artifact = _base_output(state, agent="commander", status=status or "ok")
    artifact.update(
        {
            **commander_artifact_route_fields(actual_strategist_invocation=actual_strategist_invocation, actual_strategy_source=actual_strategy_source, cooldown_applied=cooldown_applied, cooldown_until_epoch=cooldown_until_epoch, decision_frame=decision_frame, mode=mode, open_symbols=open_symbols, path=path, phase=phase, phase_text=phase_text, portfolio_snapshot=portfolio_snapshot, positions=positions, preflight=preflight, reason=reason, resilience=resilience, route_reason_codes=route_reason_codes, runtime_plan=runtime_plan, selected_route=selected_route, state=state, strategist_blocked=strategist_blocked, strategist_cache_used=strategist_cache_used, facade=facade),
            **commander_artifact_decision_fields(allowed_playbooks=allowed_playbooks, banned_playbooks=banned_playbooks, commander_decision=commander_decision, commander_market_regime=commander_market_regime, commander_risk_mode=commander_risk_mode, commander_session_bias=commander_session_bias, decision_summary=decision_summary, llm_invocation_policy=llm_invocation_policy, monitor_mission=monitor_mission, route_observability=route_observability, scanner_mission=scanner_mission, strategist_output=strategist_output),
            **commander_artifact_shadow_refresh_fields(commander_decision=commander_decision, post_scanner_refresh_context=post_scanner_refresh_context, post_scanner_refresh_reason=post_scanner_refresh_reason, post_scanner_refresh_requested=post_scanner_refresh_requested, runtime_cache_reuse_context=runtime_cache_reuse_context, runtime_cache_reuse_reason=runtime_cache_reuse_reason, runtime_refresh_context=runtime_refresh_context, runtime_refresh_reason=runtime_refresh_reason, runtime_refresh_requested=runtime_refresh_requested, shadow_alignment=shadow_alignment, shadow_assessment=shadow_assessment, shadow_assessment_summary=shadow_assessment_summary, shadow_reason_code=shadow_reason_code, source_priority=source_priority, strategist_cache_preference_context=strategist_cache_preference_context, strategist_cache_preference_reason=strategist_cache_preference_reason, strategist_cache_preferred=strategist_cache_preferred, strategist_fallback_used=strategist_fallback_used, strategist_refresh_context=strategist_refresh_context, strategist_refresh_reason=strategist_refresh_reason, strategist_refresh_requested=strategist_refresh_requested),
            **commander_artifact_policy_fields(applied_policy=applied_policy, applied_policy_source_chain=applied_policy_source_chain, commander_applied_policy_summary=commander_applied_policy_summary, commander_horizon_policy=commander_horizon_policy, execution_policy_source=execution_policy_source, horizon_context=horizon_context, llm_execution_profile_source=llm_execution_profile_source, llm_policy_source=llm_policy_source, monitor_policy_source=monitor_policy_source, override_action=override_action, override_context=override_context, override_reason=override_reason, override_triggered=override_triggered, policy_default_filled_fields=policy_default_filled_fields, policy_fallback_reason=policy_fallback_reason, policy_fallback_used=policy_fallback_used, policy_partial_normalized=policy_partial_normalized, policy_source=policy_source, policy_sources=policy_sources, policy_validation_invalid_fields=policy_validation_invalid_fields, policy_validation_missing_fields=policy_validation_missing_fields, policy_validation_status=policy_validation_status, reporter_feedback_mode=reporter_feedback_mode, reporter_feedback_mode_reason=reporter_feedback_mode_reason, reporter_feedback_mode_source=reporter_feedback_mode_source, reporter_feedback_semantics=reporter_feedback_semantics, reporter_policy_source=reporter_policy_source, scanner_policy_source=scanner_policy_source, strategist_runtime_policy_source=strategist_runtime_policy_source),
            **commander_artifact_observability_fields(commander_decision=commander_decision, decision_frame=decision_frame, handoff_instruction=handoff_instruction, mode=mode, observations=observations, path=path, phase=phase, policy_source=policy_source, preflight=preflight, reason=reason, route_observability=route_observability, runtime_fast_path=runtime_fast_path, runtime_plan=runtime_plan, state=state, status=status, strategist_cache_used=strategist_cache_used),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact
