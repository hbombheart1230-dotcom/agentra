"""Commander applied-policy/memory overlay projections (advisory only).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def decision_overlay_applied_policy_commander_horizon_policy(session_bias, memory_packets, state, strategist_output, market_regime, market_regime_rail, rail_risk_off, risk_mode, strategist_refresh_requested, strategist_refresh_reason, commander_carry_state, commander_carry_risk_bias, phase_value, strategist_refresh_context, open_position_refresh_context, observations, applied_policy, source_refs, source_priority, commander_behavior_policy, allowed_playbooks, shadow_reason_summary, reason_text, commander_override, *, facade):
    commander_memory_policy = facade.build_commander_memory_policy(
        session_bias=session_bias,
        memory_packets=memory_packets,
        usage_disabled=facade._commander_memory_usage_disabled(state),
    )
    scanner_memory_bias = facade.build_scanner_memory_bias(
        commander_memory_policy=commander_memory_policy,
        memory_packets=memory_packets,
    )
    scanner_memory_bias_summary = facade.summarize_scanner_memory_bias(scanner_memory_bias)
    monitor_memory_bias = facade.build_monitor_memory_bias(
        commander_memory_policy=commander_memory_policy,
        memory_packets=memory_packets,
    )
    monitor_memory_bias_summary = facade.summarize_monitor_memory_bias(monitor_memory_bias)
    intraday_performance_circuit = facade._build_intraday_performance_circuit(
        strategist_output=strategist_output,
        memory_packets=memory_packets,
        current_day=str(state.get("day") or state.get("trading_day") or state.get("session_day") or ""),
    )
    horizon_proposal = {}
    if isinstance(strategist_output.get("strategist_horizon_proposal"), dict):
        horizon_proposal = dict(strategist_output.get("strategist_horizon_proposal") or {})
    elif isinstance(strategist_output.get("strategy_horizon_feedback"), dict):
        horizon_proposal = dict(strategist_output.get("strategy_horizon_feedback") or {})
    commander_horizon_policy = facade.build_commander_horizon_policy(
        horizon_proposal,
        commander_context={
            "runtime_phase": str(phase_value or ""),
            "market_regime": market_regime,
            "market_regime_rail": market_regime_rail,
            "market_regime_forced_by_rail": rail_risk_off,
            "session_bias": session_bias,
            "risk_mode": risk_mode,
            "strategist_refresh_requested": strategist_refresh_requested,
            "strategist_refresh_reason": strategist_refresh_reason,
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "commander_memory_policy": dict(commander_memory_policy),
        },
        memory_packets=memory_packets,
        runtime_phase=str(phase_value or ""),
        live_validation_mode=True,
        source="commander_decision",
    )
    horizon_context = facade.build_horizon_context(commander_horizon_policy)
    strategist_refresh_context = {
        **dict(strategist_refresh_context or {}),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
    }
    if open_position_refresh_context:
        open_position_refresh_context = {
            **dict(open_position_refresh_context or {}),
            "commander_horizon_policy": dict(commander_horizon_policy),
            "horizon_context": dict(horizon_context),
        }
    observations = {
        **observations,
        "horizon_owner": "commander",
        "commander_horizon": str(commander_horizon_policy.get("strategy_horizon") or ""),
        "source_strategy_horizon": str(commander_horizon_policy.get("source_strategy_horizon") or ""),
    }
    applied_policy = dict(applied_policy)
    applied_policy["horizon"] = dict(commander_horizon_policy)
    applied_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    if list(commander_memory_policy.get("active_layers") or []):
        observations = {
            **observations,
            "memory_active_layers": list(commander_memory_policy.get("active_layers") or []),
            "memory_priority_order": list(commander_memory_policy.get("priority_order") or []),
            "symbol_memory_override_enabled": bool(commander_memory_policy.get("symbol_memory_override_enabled")),
            "scanner_memory_bias_enabled": bool(scanner_memory_bias.get("enabled")),
            "monitor_memory_bias_enabled": bool(monitor_memory_bias.get("enabled")),
        }
        source_priority = [*list(source_priority or []), *([] if "commander_memory_policy" in list(source_priority or []) else ["commander_memory_policy"])]
        source_refs = {
            **source_refs,
            "memory_active_layers": list(commander_memory_policy.get("active_layers") or []),
            "scanner_memory_bias_enabled": bool(scanner_memory_bias.get("enabled")),
            "monitor_memory_bias_enabled": bool(monitor_memory_bias.get("enabled")),
        }
    policy_sources = (
        dict(applied_policy.get("policy_sources") or {})
        if isinstance(applied_policy.get("policy_sources"), dict)
        else dict(commander_behavior_policy.get("policy_sources") or {})
        if isinstance(commander_behavior_policy.get("policy_sources"), dict)
        else {}
    )

    decision_summary = (
        f"Commander set regime={market_regime}, session_bias={session_bias}, risk_mode={risk_mode}; "
        f"allowed_playbooks={', '.join(allowed_playbooks) if allowed_playbooks else 'none'}."
    )
    if shadow_reason_summary:
        decision_summary = shadow_reason_summary
    if reason_text:
        decision_summary = f"{decision_summary} Runtime note: {str(reason_text).strip()[:180]}"
    if bool(commander_override.get("override_triggered")):
        decision_summary = (
            f"{decision_summary} Commander override requested "
            f"{str(commander_override.get('override_action') or 'force_exit_review')} "
            f"because {str(commander_override.get('override_reason') or 'open_position_risk')}."
        )
    return (applied_policy, commander_horizon_policy, commander_memory_policy, decision_summary, horizon_context, intraday_performance_circuit, monitor_memory_bias, monitor_memory_bias_summary, observations, open_position_refresh_context, policy_sources, scanner_memory_bias, scanner_memory_bias_summary, source_priority, source_refs, strategist_refresh_context)


def decision_overlay_cached_output_for_state_decision_summary(commander_carry_risk_bias, commander_carry_risk_reason, decision_summary, commander_carry_state, commander_memory_policy, strategist_invocation, strategist_refresh_requested, strategist_refresh_reason, strategist_cache_preferred, strategist_cache_preference_reason, open_position_count, entry_capacity_available, max_positions, state, *, facade):
    if commander_carry_risk_bias:
        decision_summary = (
            f"{decision_summary} Carry control classified state={commander_carry_state or 'unknown'} "
            f"with bias={commander_carry_risk_bias}."
        )
        if commander_carry_risk_reason:
            decision_summary = f"{decision_summary} Carry reason: {commander_carry_risk_reason}."
    if list(commander_memory_policy.get("active_layers") or []):
        decision_summary = (
            f"{decision_summary} Commander memory policy active layers="
            f"{', '.join(list(commander_memory_policy.get('active_layers') or []))}."
        )
        
    strategist_call_decision = strategist_invocation
    strategist_call_reason = strategist_refresh_reason if strategist_refresh_requested else ("normal_cycle" if strategist_invocation == "RUN" else "")
    strategist_skip_reason = (
        strategist_cache_preference_reason
        if strategist_cache_preferred
        else (
            ("open_positions_present" if max_positions <= 1 else "max_positions_reached")
            if open_position_count > 0 and not entry_capacity_available
            else ""
        )
    )

    # Task 2: Explicit Strategy Decision Rules
    cache_payload_for_state = facade._strategist_cache_payload(state)
    cached_output_for_state = cache_payload_for_state.get("output") if isinstance(cache_payload_for_state.get("output"), dict) else {}
    generated_epoch_for_state = max(0, facade._coerce_int(cache_payload_for_state.get("generated_epoch"), 0))
    return (cached_output_for_state, decision_summary, generated_epoch_for_state, strategist_call_decision, strategist_call_reason, strategist_skip_reason)


from libs.agents.commander.projections.decision_context_read_model import decision_overlay_blocker_counts_monitor_last_states
