"""Strategist: policy validation, commander context reference and LLM frame status fields.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations


def fill_strategist_output_policy_and_commander(commander_context, commander_horizon_policy, horizon_context, llm_meta, llm_overrides, llm_required, llm_strict, monitor_entry_policy_validation, policy_confidence, policy_source, read_model_facts_summary, state, strategic_answers, strategist_llm_block_reason, strategist_llm_blocked, strategist_output):
    strategist_output["policy_source"] = policy_source
    strategist_output["policy_validation_status"] = str(monitor_entry_policy_validation.get("status") or "ok")
    strategist_output["policy_fallback_used"] = bool(monitor_entry_policy_validation.get("fallback_used"))
    strategist_output["policy_fallback_reason"] = str(monitor_entry_policy_validation.get("fallback_reason") or "")
    strategist_output["policy_partial_normalized"] = bool(monitor_entry_policy_validation.get("partial_normalized"))
    strategist_output["policy_default_filled_fields"] = list(monitor_entry_policy_validation.get("default_filled_fields") or [])
    strategist_output["policy_validation_issues"] = list(monitor_entry_policy_validation.get("issues") or [])
    strategist_output["policy_validation_missing_fields"] = list(
        monitor_entry_policy_validation.get("policy_validation_missing_fields")
        or monitor_entry_policy_validation.get("missing_fields")
        or []
    )
    strategist_output["policy_validation_invalid_fields"] = list(
        monitor_entry_policy_validation.get("policy_validation_invalid_fields")
        or monitor_entry_policy_validation.get("invalid_fields")
        or []
    )
    strategist_output["confidence"] = policy_confidence
    strategist_output["commander_context_ref"] = {
        "source": str(commander_context.get("source") or ""),
        "market_regime": str(commander_context.get("market_regime") or ""),
        "session_bias": str(commander_context.get("session_bias") or ""),
        "risk_mode": str(commander_context.get("risk_mode") or ""),
        "command_intent": str(commander_context.get("command_intent") or ""),
        "strategist_invocation": str(commander_context.get("strategist_invocation") or ""),
        "llm_policy": str(commander_context.get("llm_policy") or ""),
        "no_trade_reason_code": str(commander_context.get("no_trade_reason_code") or ""),
        "strategist_refresh_requested": bool(commander_context.get("strategist_refresh_requested")),
        "strategist_refresh_reason": str(commander_context.get("strategist_refresh_reason") or ""),
        "strategist_refresh_context": dict(commander_context.get("strategist_refresh_context") or {}),
        "open_position_refresh_context": dict(commander_context.get("open_position_refresh_context") or {}),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
        "memory_packets": dict(commander_context.get("memory_packets") or {}),
        "commander_memory_policy": dict(commander_context.get("commander_memory_policy") or {}),
        "scanner_memory_bias": dict(commander_context.get("scanner_memory_bias") or {}),
        "scanner_memory_bias_summary": dict(commander_context.get("scanner_memory_bias_summary") or {}),
        "monitor_memory_bias": dict(commander_context.get("monitor_memory_bias") or {}),
        "monitor_memory_bias_summary": dict(commander_context.get("monitor_memory_bias_summary") or {}),
        "decision_summary": str(commander_context.get("decision_summary") or ""),
        "source_priority": list(commander_context.get("source_priority") or []),
    }
    strategist_output["commander_invocation_hint"] = str(commander_context.get("strategist_invocation") or "")
    strategist_output["commander_llm_policy"] = str(commander_context.get("llm_policy") or "")
    strategist_output["commander_no_trade_reason_code"] = str(commander_context.get("no_trade_reason_code") or "")
    strategist_output["commander_refresh_requested"] = bool(commander_context.get("strategist_refresh_requested"))
    strategist_output["commander_refresh_reason"] = str(commander_context.get("strategist_refresh_reason") or "")
    strategist_output["commander_refresh_context"] = dict(commander_context.get("strategist_refresh_context") or {})
    strategist_output["commander_open_position_refresh_context"] = dict(
        commander_context.get("open_position_refresh_context") or {}
    )
    strategist_output["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_output["horizon_context"] = dict(horizon_context)
    strategist_output["memory_packets"] = dict(commander_context.get("memory_packets") or {})
    strategist_output["commander_memory_policy"] = dict(commander_context.get("commander_memory_policy") or {})
    strategist_output["scanner_memory_bias"] = dict(commander_context.get("scanner_memory_bias") or {})
    strategist_output["scanner_memory_bias_summary"] = dict(commander_context.get("scanner_memory_bias_summary") or {})
    strategist_output["monitor_memory_bias"] = dict(commander_context.get("monitor_memory_bias") or {})
    strategist_output["monitor_memory_bias_summary"] = dict(commander_context.get("monitor_memory_bias_summary") or {})
    strategist_output["read_model_facts_summary"] = dict(read_model_facts_summary)
    strategist_output["selected_symbol_memory"] = dict(
        ((strategic_answers.get("q15_commander_refresh_context") or {}).get("selected_symbol_memory") or {})
    )
    strategist_output["shadow_used"] = bool(commander_context.get("shadow_used"))
    strategist_output["strategist_fallback_used"] = bool(commander_context.get("strategist_fallback_used"))
    strategist_output["llm_frame_status"] = str(llm_meta.get("status") or "disabled")
    strategist_output["llm_frame_applied"] = bool(llm_overrides)
    strategist_output["llm_frame_model"] = str(llm_meta.get("model") or "")
    strategist_output["llm_frame_recovery_method"] = str(llm_meta.get("recovery_method") or "")
    strategist_output["llm_frame_low_confidence"] = bool(llm_meta.get("repair_used"))
    strategist_output["llm_frame_required"] = bool(llm_required)
    strategist_output["llm_frame_strict"] = bool(llm_strict)
    strategist_output["llm_frame_blocked"] = bool(strategist_llm_blocked)
    strategist_output["llm_frame_blocked_reason"] = str(strategist_llm_block_reason or "")
    strategist_output["llm_call_trace"] = dict(llm_meta.get("llm_call_trace") or {})
    strategist_output["runtime_theme_map_keys"] = sorted(list((state.get("theme_map") or {}).keys()))
    strategist_output["runtime_sector_map_keys"] = sorted(list((state.get("sector_map") or {}).keys()))
    return None
