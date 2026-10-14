"""Commander decision snapshots/preflight/risk-off/fast-path context (no hard veto changes).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


class AppliedPolicyCommandContext(NamedTuple):
    """Result of `applied_policy_command_context` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    applied_policy: Any
    command_intent: Any
    commander_applied_policy_summary: Any
    commander_behavior_policy: Any
    commander_carry_risk_bias: Any
    commander_carry_risk_reason: Any
    commander_carry_state: Any
    commander_override: Any
    commander_session_open_recovery: Any
    flow_instruction: Any
    llm_policy: Any
    monitor_mission: Any
    observations: Any
    open_position_refresh_context: Any
    scanner_mission: Any
    session_bias: Any
    source_priority: Any
    source_refs: Any
    strategist_invocation: Any
    strategist_refresh_context: Any
    strategist_refresh_reason: Any
    strategist_refresh_requested: Any


def applied_policy_command_context(applied_policy_meta, state, strategist_refresh_reason, strategist_refresh_context, open_position_count, observations, source_refs, source_priority, phase_value, strategist_refresh_requested, flow_instruction, command_intent, llm_policy, monitor_mission, scanner_mission, session_bias, strategist_invocation, *, facade):
    applied_policy = dict(applied_policy_meta.get("applied_policy") or {})
    commander_behavior_policy = (
        dict(state.get("commander_behavior_policy") or {})
        if isinstance(state.get("commander_behavior_policy"), dict)
        else {}
    )
    commander_override = (
        dict(state.get("commander_open_position_override") or {})
        if isinstance(state.get("commander_open_position_override"), dict)
        else {}
    )
    open_position_refresh_context = (
        dict(state.get("commander_open_position_refresh_context") or {})
        if isinstance(state.get("commander_open_position_refresh_context"), dict)
        else dict(commander_override.get("strategist_refresh_context") or {})
        if isinstance(commander_override.get("strategist_refresh_context"), dict)
        else {}
    )
    commander_carry_state = str(
        commander_override.get("carry_state")
        or open_position_refresh_context.get("carry_state")
        or ""
    )
    commander_carry_risk_bias = str(
        commander_override.get("carry_risk_bias")
        or open_position_refresh_context.get("carry_risk_bias")
        or ""
    )
    commander_carry_risk_reason = str(
        commander_override.get("carry_risk_reason")
        or open_position_refresh_context.get("carry_risk_reason")
        or ""
    )
    commander_session_open_recovery = (
        dict(
            commander_override.get("session_open_recovery_assessment")
            or open_position_refresh_context.get("session_open_recovery_assessment")
            or {}
        )
        if isinstance(commander_override.get("session_open_recovery_assessment"), dict)
        or isinstance(open_position_refresh_context.get("session_open_recovery_assessment"), dict)
        else {}
    )
    if str(commander_override.get("override_action") or "").strip().lower() == "strategist_refresh":
        strategist_refresh_requested = True
        strategist_refresh_reason = strategist_refresh_reason or str(
            commander_override.get("override_reason") or "repeated_hold_monitor_only"
        )
        strategist_refresh_context = {
            **strategist_refresh_context,
            **open_position_refresh_context,
        }
    if open_position_count > 0 and (commander_carry_state or commander_carry_risk_bias):
        observations = {
            **observations,
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "carry_risk_reason": commander_carry_risk_reason,
            "session_open_recovery_assessment": dict(commander_session_open_recovery),
        }
        source_priority = ["commander_carry_control", *[x for x in source_priority if x != "commander_carry_control"]]
        source_refs = {
            **source_refs,
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
        }
        if commander_carry_risk_reason:
            source_refs["carry_risk_reason"] = commander_carry_risk_reason
    if (
        str(phase_value or "").strip().lower() == "preopen"
        and open_position_count > 0
        and commander_carry_risk_bias in {"elevated", "urgent_exit_review"}
    ):
        strategist_refresh_requested = True
        strategist_refresh_reason = "preopen_carry_risk_review"
        strategist_refresh_context = {
            **dict(strategist_refresh_context or {}),
            **dict(open_position_refresh_context or {}),
            "refresh_scope": str(
                (open_position_refresh_context or {}).get("refresh_scope")
                or "preopen_open_position_review"
            ),
            "refresh_signal": "preopen_carry_risk_review",
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "carry_risk_reason": commander_carry_risk_reason,
            "session_open_recovery_assessment": dict(commander_session_open_recovery),
        }
        observations = {
            **observations,
            "strategist_refresh_requested": True,
            "strategist_refresh_reason": "preopen_carry_risk_review",
        }
        llm_policy = "allow_context_refresh"
        strategist_invocation = "RUN_REFRESH"
        command_intent = "MANAGE_OPEN_RISK"
        flow_instruction = "REVIEW_CARRY_POSITIONS_BEFORE_NEW_ENTRIES"
        source_priority = ["commander_preopen_carry_review", *[x for x in source_priority if x != "commander_preopen_carry_review"]]
        source_refs = {
            **source_refs,
            "strategist_refresh_reason": "preopen_carry_risk_review",
            "strategist_refresh_scope": "preopen_open_position_review",
        }
    if commander_carry_risk_bias == "urgent_exit_review":
        session_bias = "position_management"
        command_intent = "MANAGE_OPEN_RISK"
        scanner_mission = "Deprioritize new candidate exploration while carried-position risk is under urgent exit review."
        monitor_mission = "Prioritize carried-position exit review and failed session-open recovery before new entries."
        if str(flow_instruction or "").strip() in {
            "",
            "HOLD_OBSERVE",
            "NO_ACTION",
            "REUSE_STRATEGY_FRAME",
            "allow_current_flow",
            "RUN_STRATEGIST_REFRESH",
        }:
            flow_instruction = "REDUCE_CARRY_RISK_FIRST"
        if not strategist_refresh_requested:
            llm_policy = "allow_context_refresh"
    elif commander_carry_risk_bias == "elevated":
        session_bias = "position_management"
        scanner_mission = "Keep new candidate exploration narrow while carried exposure is being revalidated."
        monitor_mission = "Prioritize carried-position confirmation and recovery quality before new entries."
        if not strategist_refresh_requested and str(flow_instruction or "").strip() in {
            "",
            "HOLD_OBSERVE",
            "NO_ACTION",
            "allow_current_flow",
        }:
            flow_instruction = "PRIORITIZE_CARRY_REVIEW"
    if str(phase_value or "").strip().lower() == "preopen" and commander_carry_risk_bias in {"elevated", "urgent_exit_review"}:
        scanner_mission = "Review carried positions first and keep preopen candidate expansion narrow until carry risk is revalidated."
        monitor_mission = "Prepare session-open carry-risk response for held positions before allowing new entry exploration."
    commander_applied_policy_summary = dict(state.get("commander_applied_policy_summary") or {})
    return AppliedPolicyCommandContext(applied_policy, command_intent, commander_applied_policy_summary, commander_behavior_policy, commander_carry_risk_bias, commander_carry_risk_reason, commander_carry_state, commander_override, commander_session_open_recovery, flow_instruction, llm_policy, monitor_mission, observations, open_position_refresh_context, scanner_mission, session_bias, source_priority, source_refs, strategist_invocation, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested)
