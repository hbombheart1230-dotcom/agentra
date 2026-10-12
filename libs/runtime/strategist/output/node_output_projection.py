"""Strategist output/strategy-frame projections (pure dict building; state apply order stays in the node).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/strategist_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def strat_output_value_state_scanner_guidance(playbook, scanner_bias, trade_aggressiveness, risk_tone, themes, selected_themes, avoid_themes, scanner_bias_context, scanner_priority, scanner_source_policy, theme_strength_packet, available_themes, theme_strategy, *, facade):
    return (
{
        "themes": list(themes),
        "selected_themes": list(selected_themes),
        "avoid_themes": list(avoid_themes),
        "playbook": playbook,
        "scanner_bias": scanner_bias,
        "scanner_bias_context": dict(scanner_bias_context),
        "scanner_priority": list(scanner_priority),
        "scanner_source_policy": dict(scanner_source_policy),
        "trade_aggressiveness": trade_aggressiveness,
        "risk_tone": risk_tone,
        "theme_source": str(theme_strength_packet.get("source") or ""),
        "theme_source_status": str(theme_strength_packet.get("status") or ""),
        "theme_strength_packet": dict(theme_strength_packet),
        "available_themes": list(available_themes),
        "theme_strategy": dict(theme_strategy),
    }
    )


def strat_output_performance_summary_strategist_output(recent_strategy_feedback, strategist_feedback, market_regime, market_sentiment, playbook, trade_aggressiveness, key_events, themes, avoid_themes, scanner_bias, scanner_bias_context, scanner_priority, scanner_source_policy, risk_tone, monitor_guidance, strategy_policy, report_focus, strategic_answers, state, *, facade):
    performance_summary = {
        "feedback_window_size": int(recent_strategy_feedback.get("feedback_window_size") or 0),
        "recent_theme_performance": dict(strategist_feedback.get("recent_theme_performance") or {}),
        "recent_playbook_performance": dict(strategist_feedback.get("recent_playbook_performance") or {}),
        "top_recent_strengths": list(recent_strategy_feedback.get("top_recent_strengths") or [])[:3],
        "top_recent_weaknesses": list(recent_strategy_feedback.get("top_recent_weaknesses") or [])[:3],
        "advisory_only": bool(recent_strategy_feedback.get("advisory_only", True)),
    }
    strategist_output = facade.StrategistOutput(
        market_regime=market_regime,
        market_sentiment=market_sentiment,
        key_events=list(key_events),
        themes=list(themes),
        avoid_themes=list(avoid_themes),
        playbook=playbook,
        scanner_bias=scanner_bias if scanner_bias in ("large_cap", "leader", "momentum", "value") else "leader",
        scanner_bias_context=dict(scanner_bias_context),
        scanner_priority=list(scanner_priority),
        scanner_source_policy=dict(scanner_source_policy),
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone if risk_tone in ("conservative", "normal", "aggressive") else "normal",
        monitor_guidance=(
            monitor_guidance
            if monitor_guidance in ("hold_through_noise", "defensive_exit", "quick_take_profit")
            else "defensive_exit"
        ),
        strategy_policy=dict(strategy_policy),
        report_focus=list(report_focus),
        recent_strategy_feedback=dict(recent_strategy_feedback),
        candidates=list(state["candidate_symbols"]),
        candidate_count=len(list(state["candidate_symbols"])),
        candidate_hints=list(state["candidate_symbols"]),
        strategic_answers=dict(strategic_answers),
        source="strategist_node",
    ).to_dict()
    return (performance_summary, strategist_output)


def strat_output_value_state_strategist_llm(llm_overrides, strategist_llm_blocked, strategist_llm_block_reason, llm_meta, state, *, facade):
    return (
{
        "run_id": str(state.get("run_id") or ""),
        "status": str(llm_meta.get("status") or "disabled"),
        "llm_status": str(llm_meta.get("status") or "disabled"),
        "model": str(llm_meta.get("model") or ""),
        "applied": bool(llm_overrides),
        "latency_ms": int(llm_meta.get("latency_ms") or 0),
        "attempts": int(llm_meta.get("attempts") or 1),
        "repair_used": bool(llm_meta.get("repair_used")),
        "low_confidence": bool(llm_meta.get("repair_used")),
        "reason": str(llm_meta.get("reason") or ""),
        "llm_call_trace": dict(llm_meta.get("llm_call_trace") or {}),
        "error": str(llm_meta.get("reason") or ""),
        "recovery_method": str(llm_meta.get("recovery_method") or ""),
        "blocked": bool(strategist_llm_blocked),
        "blocked_reason": str(strategist_llm_block_reason or ""),
        "prompt_ref": str(llm_meta.get("prompt_ref") or ""),
        "response_ref": str(llm_meta.get("response_ref") or ""),
        "prompt_hash": str(llm_meta.get("prompt_hash") or ""),
        "response_hash": str(llm_meta.get("response_hash") or ""),
        "llm_stage_component": str(llm_meta.get("llm_stage_component") or ""),
        "llm_stage_index": int(llm_meta.get("llm_stage_index") or 0),
        "llm_stage_name": str(llm_meta.get("llm_stage_name") or ""),
        "llm_call_kind": str(llm_meta.get("llm_call_kind") or ""),
        "quant_context": dict(llm_meta.get("quant_context") or {}),
        "stage_prompt_ref": str(llm_meta.get("stage_prompt_ref") or ""),
        "stage_response_ref": str(llm_meta.get("stage_response_ref") or ""),
        "stage_meta_ref": str(llm_meta.get("stage_meta_ref") or ""),
        "llm_stage_manifest_ref": str(llm_meta.get("llm_stage_manifest_ref") or ""),
        "llm_execution_profile_name": str(llm_meta.get("llm_execution_profile_name") or ""),
        "llm_execution_profile_source": str(llm_meta.get("llm_execution_profile_source") or ""),
        "llm_execution_effective_config": dict(llm_meta.get("llm_execution_effective_config") or {}),
    }
    )
