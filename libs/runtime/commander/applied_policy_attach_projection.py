"""Commander applied-policy attach/provenance projections (state field assignment timing stays in the caller).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def attach_policy_commander_context_commander_memory_polic(strategist_output, *, facade):
    strategist_output = dict(strategist_output)
    strategy_policy = (
        dict(strategist_output.get("strategy_policy") or {})
        if isinstance(strategist_output.get("strategy_policy"), dict)
        else {}
    )
    scanner_policy = (
        dict(strategy_policy.get("scanner_policy") or {})
        if isinstance(strategy_policy.get("scanner_policy"), dict)
        else {}
    )
    commander_context = (
        dict(strategy_policy.get("commander_context") or {})
        if isinstance(strategy_policy.get("commander_context"), dict)
        else {}
    )
    memory_packets = {}
    commander_memory_policy = {}
    return (commander_context, commander_memory_policy, memory_packets, scanner_policy, strategist_output, strategy_policy)


def attach_policy_commander_decision_commander_horizon_pol(strategist_output, strategy_policy, commander_context, memory_packets, state, commander_decision, *, facade):
    horizon_proposal = {}
    if isinstance(strategist_output.get("strategist_horizon_proposal"), dict):
        horizon_proposal = dict(strategist_output.get("strategist_horizon_proposal") or {})
    elif isinstance(strategist_output.get("strategy_horizon_feedback"), dict):
        horizon_proposal = dict(strategist_output.get("strategy_horizon_feedback") or {})
    elif isinstance((strategy_policy.get("monitor_policy") or {}).get("strategy_horizon_feedback"), dict):
        horizon_proposal = dict((strategy_policy.get("monitor_policy") or {}).get("strategy_horizon_feedback") or {})
    commander_horizon_policy = facade.build_commander_horizon_policy(
        horizon_proposal,
        commander_context=commander_context,
        memory_packets=memory_packets,
        runtime_phase=str(state.get("runtime_phase") or commander_context.get("session_bias") or ""),
        live_validation_mode=True,
        source="commander_applied_policy",
    )
    horizon_context = facade.build_horizon_context(commander_horizon_policy)
    strategist_refresh_context = (
        dict(commander_context.get("strategist_refresh_context") or {})
        if isinstance(commander_context.get("strategist_refresh_context"), dict)
        else {}
    )
    strategist_refresh_context["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_refresh_context["horizon_context"] = dict(horizon_context)
    commander_context["strategist_refresh_context"] = strategist_refresh_context
    open_position_refresh_context = (
        dict(commander_context.get("open_position_refresh_context") or {})
        if isinstance(commander_context.get("open_position_refresh_context"), dict)
        else {}
    )
    if open_position_refresh_context:
        open_position_refresh_context["commander_horizon_policy"] = dict(commander_horizon_policy)
        open_position_refresh_context["horizon_context"] = dict(horizon_context)
        commander_context["open_position_refresh_context"] = open_position_refresh_context
    commander_context["commander_horizon_policy"] = dict(commander_horizon_policy)
    commander_context["horizon_context"] = dict(horizon_context)
    commander_decision = dict(commander_decision)
    return (commander_decision, commander_horizon_policy, horizon_context)


def attach_policy_monitor_policy(commander_context, strategy_policy, applied_policy, policy_meta, *, facade):
    strategy_policy["commander_context"] = commander_context

    monitor_policy = (
        dict(strategy_policy.get("monitor_policy") or {})
        if isinstance(strategy_policy.get("monitor_policy"), dict)
        else {}
    )
    monitor_policy["applied_policy"] = dict(applied_policy)
    monitor_policy["policy_source"] = str(policy_meta.get("policy_source") or "")
    monitor_policy["policy_validation_status"] = str(policy_meta.get("policy_validation_status") or "")
    monitor_policy["policy_fallback_used"] = bool(policy_meta.get("policy_fallback_used"))
    monitor_policy["policy_fallback_reason"] = str(policy_meta.get("policy_fallback_reason") or "")
    monitor_policy["policy_partial_normalized"] = bool(policy_meta.get("policy_partial_normalized"))
    monitor_policy["policy_default_filled_fields"] = list(policy_meta.get("policy_default_filled_fields") or [])
    monitor_policy["policy_validation_missing_fields"] = list(policy_meta.get("policy_validation_missing_fields") or [])
    monitor_policy["policy_validation_invalid_fields"] = list(policy_meta.get("policy_validation_invalid_fields") or [])
    monitor_policy["override_reason"] = str(policy_meta.get("override_reason") or "")
    monitor_policy["applied_policy_source_chain"] = list(policy_meta.get("applied_policy_source_chain") or [])
    return (monitor_policy,)


def attach_policy_provenance(commander_entry_control, scanner_policy, strategy_policy, policy_meta, scanner_bias_meta, *, facade):
    if commander_entry_control:
        scanner_policy["entry_control"] = dict(commander_entry_control)
        scanner_policy["max_priority_rank"] = int(
            commander_entry_control.get("max_priority_rank")
            if commander_entry_control.get("max_priority_rank") not in (None, "")
            else 10
        )
        scanner_policy["max_runner_ups"] = int(
            commander_entry_control.get("max_runner_ups")
            if commander_entry_control.get("max_runner_ups") not in (None, "")
            else 9
        )
    strategy_policy["scanner_policy"] = scanner_policy

    provenance = (
        dict(strategy_policy.get("provenance") or {})
        if isinstance(strategy_policy.get("provenance"), dict)
        else {}
    )
    provenance["applied_policy_source"] = str(policy_meta.get("policy_source") or "")
    provenance["policy_validation_status"] = str(policy_meta.get("policy_validation_status") or "")
    provenance["policy_fallback_used"] = bool(policy_meta.get("policy_fallback_used"))
    provenance["policy_fallback_reason"] = str(policy_meta.get("policy_fallback_reason") or "")
    provenance["policy_partial_normalized"] = bool(policy_meta.get("policy_partial_normalized"))
    provenance["policy_default_filled_fields"] = list(policy_meta.get("policy_default_filled_fields") or [])
    provenance["policy_validation_missing_fields"] = list(policy_meta.get("policy_validation_missing_fields") or [])
    provenance["policy_validation_invalid_fields"] = list(policy_meta.get("policy_validation_invalid_fields") or [])
    provenance["override_reason"] = str(policy_meta.get("override_reason") or "")
    provenance["applied_policy_source_chain"] = list(policy_meta.get("applied_policy_source_chain") or [])
    provenance["scanner_bias_source"] = str(scanner_bias_meta.get("bias_source") or "")
    strategy_policy["provenance"] = provenance
    return (provenance,)
