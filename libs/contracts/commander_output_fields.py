"""Commander output artifact: route identity, runtime posture and portfolio fields (key order unchanged).

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_commander_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _listify,
    _safe_int,
)


def commander_artifact_route_fields(actual_strategist_invocation, actual_strategy_source, cooldown_applied, cooldown_until_epoch, decision_frame, mode, open_symbols, path, phase, phase_text, portfolio_snapshot, positions, preflight, reason, resilience, route_reason_codes, runtime_plan, selected_route, state, strategist_blocked, strategist_cache_used, *, facade):
    return {
        "ownership_version": "1.0",
        "actual_strategist_invocation": bool(actual_strategist_invocation),
        "actual_strategy_source": actual_strategy_source,
        "mode": str(mode or "").strip(),
        "phase": str(phase or "").strip(),
        "path": str(path or "").strip(),
        "runtime_mode": str(mode or "").strip(),
        "runtime_phase": phase_text,
        "selected_route": selected_route,
        "route_reason_codes": route_reason_codes,
        "route_reason_text": _clip(
            " / ".join(route_reason_codes) if route_reason_codes else (reason or state.get("runtime_status") or ""),
            max_len=280,
        ),
        "open_position_count": _safe_int(len(positions)),
        "open_position_symbols": open_symbols,
        "strategist_cache_used": strategist_cache_used,
        "strategist_blocked": strategist_blocked,
        "cooldown_applied": cooldown_applied,
        "incident_state": {
            "incident_count": _safe_int(resilience.get("incident_count")),
            "cooldown_until_epoch": cooldown_until_epoch,
            "degrade_mode": _clip(resilience.get("degrade_mode"), max_len=80),
            "last_error_type": _clip(resilience.get("last_error_type"), max_len=120),
            "last_error_ts": _clip(resilience.get("last_error_ts"), max_len=80),
        },
        "portfolio_preflight_result": preflight,
        "generated_at": facade._utc_now_iso(),
        "session_type": _clip(decision_frame.get("session_type") or runtime_plan.get("phase") or phase, max_len=40),
        "market_clock_phase": _clip(decision_frame.get("market_clock_phase") or phase or runtime_plan.get("phase"), max_len=40),
        "portfolio_state_summary": {
            "position_count": _safe_int(len(positions)),
            "cash": portfolio_snapshot.get("cash"),
            "positions_source": _clip(preflight.get("positions_source"), max_len=80),
            "preflight_status": _clip(preflight.get("status"), max_len=80),
        }
    }


def commander_artifact_decision_fields(allowed_playbooks, banned_playbooks, commander_decision, commander_market_regime, commander_risk_mode, commander_session_bias, decision_summary, llm_invocation_policy, monitor_mission, route_observability, scanner_mission, strategist_output):
    return {
        "market_regime_summary": {
            "market_regime": _clip(strategist_output.get("market_regime"), max_len=80),
            "market_sentiment": _clip(strategist_output.get("market_sentiment"), max_len=80),
            "playbook": _clip(strategist_output.get("playbook"), max_len=80),
        },
        "market_regime": commander_market_regime,
        "session_bias": commander_session_bias,
        "risk_mode": commander_risk_mode,
        "allowed_playbooks": allowed_playbooks,
        "banned_playbooks": banned_playbooks,
        "scanner_mission": scanner_mission,
        "monitor_mission": monitor_mission,
        "llm_invocation_policy": llm_invocation_policy,
        "scanner_policy": dict(commander_decision.get("scanner_policy") or {}),
        "monitor_feedback": _dict(commander_decision.get("monitor_feedback")),
        "adaptive_policy": _dict(commander_decision.get("adaptive_policy")),
        "policy_adjustment_trace": _listify(commander_decision.get("policy_adjustment_trace"), limit=10, max_len=200),
        "decision_summary": decision_summary,
        "commander_decision": commander_decision,
        "strategist_call_decision": _clip(commander_decision.get("strategist_call_decision") or route_observability.get("strategist_call_decision"), max_len=40),
        "strategist_call_reason": _clip(commander_decision.get("strategist_call_reason") or route_observability.get("strategist_call_reason"), max_len=180),
        "strategist_skip_reason": _clip(commander_decision.get("strategist_skip_reason") or route_observability.get("strategist_skip_reason"), max_len=180),
        "strategist_invocation_mode": _clip(commander_decision.get("strategist_invocation_mode"), max_len=40),
        "strategy_selection_mode": _clip(commander_decision.get("strategy_selection_mode"), max_len=40),
        "strategy_state": _clip(commander_decision.get("strategy_state"), max_len=40)
    }


def commander_artifact_shadow_refresh_fields(commander_decision, post_scanner_refresh_context, post_scanner_refresh_reason, post_scanner_refresh_requested, runtime_cache_reuse_context, runtime_cache_reuse_reason, runtime_refresh_context, runtime_refresh_reason, runtime_refresh_requested, shadow_alignment, shadow_assessment, shadow_assessment_summary, shadow_reason_code, source_priority, strategist_cache_preference_context, strategist_cache_preference_reason, strategist_cache_preferred, strategist_fallback_used, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested):
    return {
        "shadow_assessment_summary": shadow_assessment_summary,
        "shadow_used": bool(commander_decision.get("shadow_used") or shadow_assessment),
        "shadow_reason_code": shadow_reason_code,
        "shadow_alignment": shadow_alignment,
        "source_priority": source_priority,
        "strategist_fallback_used": strategist_fallback_used,
        "strategist_refresh_requested": strategist_refresh_requested,
        "strategist_refresh_reason": strategist_refresh_reason,
        "strategist_refresh_context": strategist_refresh_context,
        "strategist_cache_preferred": strategist_cache_preferred,
        "strategist_cache_preference_reason": strategist_cache_preference_reason,
        "strategist_cache_preference_context": strategist_cache_preference_context,
        "runtime_refresh_requested": runtime_refresh_requested,
        "runtime_refresh_reason": runtime_refresh_reason,
        "runtime_refresh_context": runtime_refresh_context,
        "post_scanner_refresh_requested": post_scanner_refresh_requested,
        "post_scanner_refresh_reason": post_scanner_refresh_reason,
        "post_scanner_refresh_context": post_scanner_refresh_context,
        "runtime_cache_reuse_reason": runtime_cache_reuse_reason,
        "runtime_cache_reuse_context": runtime_cache_reuse_context
    }


def commander_artifact_policy_fields(applied_policy, applied_policy_source_chain, commander_applied_policy_summary, commander_horizon_policy, execution_policy_source, horizon_context, llm_execution_profile_source, llm_policy_source, monitor_policy_source, override_action, override_context, override_reason, override_triggered, policy_default_filled_fields, policy_fallback_reason, policy_fallback_used, policy_partial_normalized, policy_source, policy_sources, policy_validation_invalid_fields, policy_validation_missing_fields, policy_validation_status, reporter_feedback_mode, reporter_feedback_mode_reason, reporter_feedback_mode_source, reporter_feedback_semantics, reporter_policy_source, scanner_policy_source, strategist_runtime_policy_source):
    return {
        "applied_policy": applied_policy,
        "commander_horizon_policy": commander_horizon_policy,
        "horizon_context": horizon_context,
        "policy_source": policy_source,
        "policy_validation_status": policy_validation_status,
        "policy_fallback_used": policy_fallback_used,
        "policy_fallback_reason": policy_fallback_reason,
        "policy_partial_normalized": policy_partial_normalized,
        "policy_default_filled_fields": policy_default_filled_fields,
        "policy_validation_missing_fields": policy_validation_missing_fields,
        "policy_validation_invalid_fields": policy_validation_invalid_fields,
        "override_triggered": override_triggered,
        "override_reason": override_reason,
        "override_action": override_action,
        "override_context": override_context,
        "applied_policy_source_chain": applied_policy_source_chain,
        "reporter_feedback_mode": reporter_feedback_mode,
        "reporter_feedback_mode_source": reporter_feedback_mode_source,
        "reporter_feedback_mode_reason": reporter_feedback_mode_reason,
        "reporter_feedback_semantics": reporter_feedback_semantics or "advisory_only",
        "commander_applied_policy_summary": commander_applied_policy_summary,
        "policy_sources": policy_sources,
        "strategist_runtime_policy_source": strategist_runtime_policy_source,
        "llm_policy_source": llm_policy_source,
        "llm_execution_profile_source": llm_execution_profile_source,
        "reporter_policy_source": reporter_policy_source,
        "monitor_policy_source": monitor_policy_source,
        "scanner_policy_source": scanner_policy_source,
        "execution_policy_source": execution_policy_source
    }


def commander_artifact_observability_fields(commander_decision, decision_frame, handoff_instruction, mode, observations, path, phase, policy_source, preflight, reason, route_observability, runtime_fast_path, runtime_plan, state, status, strategist_cache_used):
    return {
        "route_observability": dict(route_observability),
        "observations": observations,
        "route_selected": _clip(route_observability.get("route_selected"), max_len=80),
        "route_reason": _clip(route_observability.get("route_reason"), max_len=220),
        "policy_refresh_reason": _clip(route_observability.get("policy_refresh_reason"), max_len=180),
        "cache_hit": bool(strategist_cache_used or route_observability.get("cache_hit")),
        "cache_age_sec": _safe_int(route_observability.get("cache_age_sec") or runtime_fast_path.get("cache_age_sec")),
        "applied_policy_source": policy_source,
        "applied_policy_id": _clip(route_observability.get("applied_policy_id") or commander_decision.get("applied_policy_id"), max_len=120),
        "monitor_only_reason": _clip(route_observability.get("monitor_only_reason"), max_len=220),
        "full_cycle_reason": _clip(route_observability.get("full_cycle_reason"), max_len=220),
        "resilience_state": _dict(route_observability.get("resilience_state")),
        "intervention_reason": _clip(route_observability.get("intervention_reason"), max_len=180),
        "strategy_generation_mode": _clip(route_observability.get("strategy_generation_mode"), max_len=40),
        "goal": _clip(
            decision_frame.get("goal")
            or ("Execute full session chain." if phase == "session" else f"Run {phase} phase safely."),
            max_len=180,
        ),
        "agent_invocation_plan": list(runtime_plan.get("agents") or []),
        "decision_checkpoints": {
            "runtime_transition": _clip(state.get("runtime_transition"), max_len=60),
            "runtime_status": _clip(state.get("runtime_status"), max_len=80),
            "portfolio_preflight": preflight,
            "runtime_fast_path": runtime_fast_path,
        },
        "final_runtime_path": str(path or "").strip(),
        "final_reason": _clip(reason or state.get("runtime_status") or "", max_len=220),
        "handoff_instruction": handoff_instruction,
        "invoked_agents": list(_dict(state.get("runtime_plan")).get("agents") or []),
        "command": str(mode or "").strip(),
        "decision": str(path or "").strip(),
        "approval_result": status == "ok",
        "reason": _clip(reason or state.get("runtime_status") or "", max_len=220),
        "blocked_allowed_details": {
            "mode": str(mode or "").strip(),
            "phase": str(phase or "").strip(),
            "path": str(path or "").strip(),
            "portfolio_preflight": _dict(state.get("portfolio_preflight")),
            "runtime_transition": _clip(state.get("runtime_transition"), max_len=80),
        }
    }
