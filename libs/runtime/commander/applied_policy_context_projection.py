"""Commander applied policy: commander_context update surface (policy, memory, horizon, refresh fields).

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/commander_runtime.py::_attach_commander_applied_policy` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_commander_context_update(applied_policy, commander_context, commander_decision, commander_entry_control, commander_memory_policy, memory_packets, monitor_memory_bias, monitor_memory_bias_summary, policy_meta, scanner_bias_context, scanner_bias_summary, scanner_memory_bias, scanner_memory_bias_summary):
    return (
        {
            "source": str(commander_context.get("source") or "commander_decision"),
            "market_regime": str(commander_decision.get("market_regime") or commander_context.get("market_regime") or ""),
            "market_regime_rail": str(
                commander_decision.get("market_regime_rail")
                or commander_context.get("market_regime_rail")
                or ""
            ),
            "market_regime_forced_by_rail": bool(
                commander_decision.get("market_regime_forced_by_rail")
                if commander_decision.get("market_regime_forced_by_rail") is not None
                else commander_context.get("market_regime_forced_by_rail")
            ),
            "session_bias": str(commander_decision.get("session_bias") or commander_context.get("session_bias") or ""),
            "risk_mode": str(commander_decision.get("risk_mode") or commander_context.get("risk_mode") or ""),
            "allowed_playbooks": list(commander_decision.get("allowed_playbooks") or commander_context.get("allowed_playbooks") or []),
            "banned_playbooks": list(commander_decision.get("banned_playbooks") or commander_context.get("banned_playbooks") or []),
            "scanner_mission": str(commander_decision.get("scanner_mission") or commander_context.get("scanner_mission") or ""),
            "monitor_mission": str(commander_decision.get("monitor_mission") or commander_context.get("monitor_mission") or ""),
            "llm_policy": str(commander_decision.get("llm_policy") or commander_context.get("llm_policy") or ""),
            "command_intent": str(commander_decision.get("command_intent") or commander_context.get("command_intent") or ""),
            "strategist_invocation": str(commander_decision.get("strategist_invocation") or commander_context.get("strategist_invocation") or ""),
            "flow_instruction": str(commander_decision.get("flow_instruction") or commander_context.get("flow_instruction") or ""),
            "no_trade_reason_code": str(commander_decision.get("no_trade_reason_code") or commander_context.get("no_trade_reason_code") or ""),
            "decision_summary": str(commander_decision.get("decision_summary") or commander_context.get("decision_summary") or ""),
            "strategist_refresh_requested": bool(
                commander_decision.get("strategist_refresh_requested")
                if commander_decision.get("strategist_refresh_requested") is not None
                else commander_context.get("strategist_refresh_requested")
            ),
            "strategist_refresh_reason": str(
                commander_decision.get("strategist_refresh_reason")
                or commander_context.get("strategist_refresh_reason")
                or ""
            ),
            "strategist_refresh_context": dict(
                commander_decision.get("strategist_refresh_context")
                or commander_context.get("strategist_refresh_context")
                or {}
            ),
            "carry_state": str(commander_decision.get("carry_state") or commander_context.get("carry_state") or ""),
            "carry_risk_bias": str(
                commander_decision.get("carry_risk_bias") or commander_context.get("carry_risk_bias") or ""
            ),
            "carry_risk_reason": str(
                commander_decision.get("carry_risk_reason") or commander_context.get("carry_risk_reason") or ""
            ),
            "session_open_recovery_assessment": dict(
                commander_decision.get("session_open_recovery_assessment")
                or commander_context.get("session_open_recovery_assessment")
                or {}
            ),
            "observations": dict(commander_decision.get("observations") or commander_context.get("observations") or {}),
            "source_priority": list(commander_decision.get("source_priority") or commander_context.get("source_priority") or []),
            "source_refs": dict(commander_decision.get("source_refs") or commander_context.get("source_refs") or {}),
            "shadow_used": bool(
                commander_decision.get("shadow_used")
                if commander_decision.get("shadow_used") is not None
                else commander_context.get("shadow_used")
            ),
            "strategist_fallback_used": bool(
                commander_decision.get("strategist_fallback_used")
                if commander_decision.get("strategist_fallback_used") is not None
                else commander_context.get("strategist_fallback_used")
            ),
            "memory_packets": dict(memory_packets),
            "commander_memory_policy": dict(commander_memory_policy),
            "applied_policy": dict(applied_policy),
            "policy_source": str(policy_meta.get("policy_source") or ""),
            "policy_validation_status": str(policy_meta.get("policy_validation_status") or ""),
            "policy_fallback_used": bool(policy_meta.get("policy_fallback_used")),
            "policy_fallback_reason": str(policy_meta.get("policy_fallback_reason") or ""),
            "policy_partial_normalized": bool(policy_meta.get("policy_partial_normalized")),
            "policy_default_filled_fields": list(policy_meta.get("policy_default_filled_fields") or []),
            "policy_validation_missing_fields": list(policy_meta.get("policy_validation_missing_fields") or []),
            "policy_validation_invalid_fields": list(policy_meta.get("policy_validation_invalid_fields") or []),
            "override_reason": str(policy_meta.get("override_reason") or ""),
            "applied_policy_source_chain": list(policy_meta.get("applied_policy_source_chain") or []),
            "monitor_entry_policy_summary": dict(policy_meta.get("monitor_entry_policy_summary") or {}),
            "entry_control": dict(commander_entry_control),
            "commander_entry_control": dict(commander_entry_control),
            "scanner_bias": scanner_bias_context.to_dict(),
            "scanner_bias_summary": dict(scanner_bias_summary),
            "scanner_memory_bias": dict(scanner_memory_bias),
            "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
            "monitor_memory_bias": dict(monitor_memory_bias),
            "monitor_memory_bias_summary": dict(monitor_memory_bias_summary),
        }
    )

def build_commander_context_ref(applied_policy, commander_context, commander_entry_control, commander_horizon_policy, horizon_context, policy_meta, strategist_output):
    return (
        {
        **(
            dict(strategist_output.get("commander_context_ref") or {})
            if isinstance(strategist_output.get("commander_context_ref"), dict)
            else {}
        ),
        "source": str(commander_context.get("source") or ""),
        "market_regime": str(commander_context.get("market_regime") or ""),
        "market_regime_rail": str(commander_context.get("market_regime_rail") or ""),
        "market_regime_forced_by_rail": bool(commander_context.get("market_regime_forced_by_rail")),
        "session_bias": str(commander_context.get("session_bias") or ""),
        "risk_mode": str(commander_context.get("risk_mode") or ""),
        "command_intent": str(commander_context.get("command_intent") or ""),
        "strategist_invocation": str(commander_context.get("strategist_invocation") or ""),
        "llm_policy": str(commander_context.get("llm_policy") or ""),
        "no_trade_reason_code": str(commander_context.get("no_trade_reason_code") or ""),
        "strategist_refresh_requested": bool(commander_context.get("strategist_refresh_requested")),
        "strategist_refresh_reason": str(commander_context.get("strategist_refresh_reason") or ""),
        "strategist_refresh_context": dict(commander_context.get("strategist_refresh_context") or {}),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
        "entry_control": dict(commander_entry_control),
        "carry_state": str(commander_context.get("carry_state") or ""),
        "carry_risk_bias": str(commander_context.get("carry_risk_bias") or ""),
        "carry_risk_reason": str(commander_context.get("carry_risk_reason") or ""),
        "session_open_recovery_assessment": dict(
            commander_context.get("session_open_recovery_assessment") or {}
        ),
        "decision_summary": str(commander_context.get("decision_summary") or ""),
        "source_priority": list(commander_context.get("source_priority") or []),
        "policy_source": str(policy_meta.get("policy_source") or ""),
        "policy_validation_status": str(policy_meta.get("policy_validation_status") or ""),
        "policy_fallback_used": bool(policy_meta.get("policy_fallback_used")),
        "override_reason": str(policy_meta.get("override_reason") or ""),
        "applied_policy_present": bool(applied_policy),
    }
    )
