"""Commander decision snapshots/preflight/risk-off/fast-path context (no hard veto changes).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple
from libs.agents.commander.projections import decision_context_read_model as _context_read_model


def decision_ctx_entry_capacity_available_market_regime(state, mode_value, phase_value, status_value, path_value, reason_text, *, facade):
    portfolio_snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    preflight = state.get("portfolio_preflight") if isinstance(state.get("portfolio_preflight"), dict) else {}
    runtime_fast_path = state.get("runtime_fast_path") if isinstance(state.get("runtime_fast_path"), dict) else {}
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    resilience = state.get("runtime_resilience_state") if isinstance(state.get("runtime_resilience_state"), dict) else {}
    shadow_assessment = facade._build_shadow_assessment_summary(
        state,
        mode_value=mode_value,
        phase_value=phase_value,
        status_value=status_value,
        path_value=path_value,
        reason_text=reason_text,
    )
    positions = [row for row in list(portfolio_snapshot.get("positions") or []) if isinstance(row, dict)]
    open_position_count = len(positions)
    max_positions = facade._resolve_risk_max_positions(state)
    entry_capacity_available = open_position_count < max_positions
    market_regime, strategist_fallback_used = facade._derive_commander_market_regime(state, shadow_assessment=shadow_assessment)
    return _context_read_model.decision_context_readout(state, phase_value, status_value, path_value, preflight, runtime_fast_path, strategist_output, resilience, shadow_assessment, open_position_count, max_positions, entry_capacity_available, market_regime, strategist_fallback_used)


class DecisionPolicyContext(NamedTuple):
    """Result of `decision_policy_context` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    allowed_playbooks: Any
    applied_policy_meta: Any
    banned_playbooks: Any
    command_intent: Any
    flow_instruction: Any
    llm_policy: Any
    monitor_mission: Any
    no_trade_reason_code: Any
    observations: Any
    reporter_feedback_policy: Any
    scanner_mission: Any
    shadow_reason_summary: Any
    shadow_used: Any
    source_priority: Any
    source_refs: Any
    strategist_cache_preference_context: Any
    strategist_cache_preference_reason: Any
    strategist_cache_preferred: Any
    strategist_invocation: Any
    strategist_refresh_context: Any
    strategist_refresh_reason: Any
    strategist_refresh_requested: Any


def decision_policy_context(risk_mode, session_bias, path_value, phase_value, runtime_fast_path, shadow_assessment, open_position_count, entry_capacity_available, state, market_regime, strategist_fallback_used, *, facade):
    if risk_mode == "blocked":
        allowed_playbooks = []
    elif risk_mode == "defensive":
        allowed_playbooks = ["defensive", "pullback"]
    elif risk_mode == "offensive":
        allowed_playbooks = ["breakout", "pullback"]
    else:
        allowed_playbooks = ["pullback", "defensive", "breakout"]
    all_playbooks = ["breakout", "pullback", "reversal", "defensive"]
    banned_playbooks = [x for x in all_playbooks if x not in allowed_playbooks]

    if risk_mode == "defensive":
        scanner_mission = "Prioritize liquid leaders and defensive candidates with resilient participation."
        monitor_mission = "Require cleaner confirmation and protect downside quickly."
    elif risk_mode == "offensive":
        scanner_mission = "Prioritize liquid momentum leaders with strong participation and clean continuation."
        monitor_mission = "Confirm intraday continuation promptly while respecting risk rails."
    elif session_bias == "position_management":
        scanner_mission = "Keep candidate refresh narrow while existing exposure is being managed."
        monitor_mission = "Focus on hold versus exit confirmation for open positions first."
    elif session_bias == "multi_position_selection":
        scanner_mission = "Continue candidate selection while existing exposure is monitored, avoiding held symbols."
        monitor_mission = "Evaluate fresh entries only when position capacity remains and duplicate-symbol guards pass."
    else:
        scanner_mission = "Prioritize balanced liquid leaders with clear scanner fit and manageable risk."
        monitor_mission = "Wait for confirmation and avoid low-quality chase entries."

    if "cached" in str(path_value or "") or str(runtime_fast_path.get("reason") or "").strip() == "flat_position_cached_strategist":
        llm_policy = "prefer_cached_context"
    elif session_bias == "position_management":
        llm_policy = "allow_if_context_changed"
    elif str(phase_value or "").strip() == "preopen":
        llm_policy = "allow_context_refresh"
    else:
        llm_policy = "allow"

    shadow_used = bool(shadow_assessment)
    shadow_no_trade_reason_code = str(shadow_assessment.get("no_trade_reason_code") or "").strip()
    shadow_reason_summary = str(shadow_assessment.get("reason_summary") or "").strip()
    command_intent = str(shadow_assessment.get("decision") or "OBSERVE_ONLY").strip() if shadow_used else "OBSERVE_ONLY"
    strategist_invocation = str(shadow_assessment.get("strategist_action_recommendation") or "").strip() if shadow_used else ""
    llm_policy = str(shadow_assessment.get("llm_call_advice") or llm_policy).strip()
    flow_instruction = str(shadow_assessment.get("suggested_action") or "").strip()
    no_trade_reason_code = shadow_no_trade_reason_code
    if not strategist_invocation:
        strategist_invocation = "SKIP" if open_position_count > 0 and not entry_capacity_available else "RUN"
    if not flow_instruction:
        flow_instruction = "HOLD_OBSERVE" if open_position_count > 0 and not entry_capacity_available else "NO_ACTION"
    if not no_trade_reason_code:
        no_trade_reason_code = "MAX_POSITIONS_REACHED" if open_position_count > 0 and not entry_capacity_available else "NONE"
    observations = dict(shadow_assessment.get("observations") or {}) if isinstance(shadow_assessment.get("observations"), dict) else {}
    refresh_assessment = facade._assess_pre_buy_strategist_refresh_need(state, commander_market_regime=market_regime)
    strategist_refresh_requested = bool(refresh_assessment.get("requested"))
    strategist_refresh_reason = str(refresh_assessment.get("refresh_signal") or refresh_assessment.get("reason") or "").strip()
    strategist_refresh_context = {
        k: v
        for k, v in dict(refresh_assessment).items()
        if k not in {"requested"}
    }
    cache_reuse_assessment = facade._assess_cached_strategist_reuse_preference(state)
    strategist_cache_preferred = bool(cache_reuse_assessment.get("preferred"))
    strategist_cache_preference_reason = str(cache_reuse_assessment.get("reason") or "").strip()
    strategist_cache_preference_context = {
        k: v
        for k, v in dict(cache_reuse_assessment).items()
        if k not in {"preferred"}
    }
    if strategist_refresh_requested:
        strategist_invocation = "RUN_REFRESH"
        llm_policy = "allow_context_refresh"
        flow_instruction = "REFRESH_STRATEGY_FRAME"
        observations = {
            **observations,
            "strategist_refresh_requested": True,
            "strategist_refresh_reason": strategist_refresh_reason,
        }
    elif strategist_invocation == "RUN" and strategist_cache_preferred:
        strategist_invocation = "SKIP"
        llm_policy = "prefer_cached_context"
        flow_instruction = "REUSE_STRATEGY_FRAME"
        observations = {
            **observations,
            "strategist_cache_preferred": True,
            "strategist_cache_preference_reason": strategist_cache_preference_reason,
        }
    source_priority = ["shadow_commander", "runtime_observation", "strategist_fallback"]
    if strategist_refresh_requested:
        source_priority = ["commander_refresh_heuristic", *source_priority]
    elif strategist_invocation == "SKIP" and strategist_cache_preferred:
        source_priority = ["commander_cache_reuse", *source_priority]
    source_refs = {
        "shadow_event": "commander_router.shadow_assessment",
        "runtime_fast_path_reason": str(runtime_fast_path.get("reason") or ""),
        "runtime_path": str(path_value or ""),
        "strategist_fallback_fields": ["market_regime"] if strategist_fallback_used else [],
    }
    if strategist_refresh_requested:
        source_refs["strategist_refresh_reason"] = strategist_refresh_reason
        source_refs["strategist_refresh_scope"] = "strategy_frame_refresh"
    elif strategist_invocation == "SKIP" and strategist_cache_preferred:
        source_refs["strategist_cache_preference_reason"] = strategist_cache_preference_reason
        source_refs["strategist_cache_preference_scope"] = "cached_strategy_frame_reuse"
    applied_policy_meta = (
        dict(state.get("commander_applied_policy_meta") or {})
        if isinstance(state.get("commander_applied_policy_meta"), dict)
        else {}
    )
    reporter_feedback_policy = (
        dict(state.get("commander_reporter_feedback_policy") or {})
        if isinstance(state.get("commander_reporter_feedback_policy"), dict)
        else {}
    )
    return DecisionPolicyContext(allowed_playbooks, applied_policy_meta, banned_playbooks, command_intent, flow_instruction, llm_policy, monitor_mission, no_trade_reason_code, observations, reporter_feedback_policy, scanner_mission, shadow_reason_summary, shadow_used, source_priority, source_refs, strategist_cache_preference_context, strategist_cache_preference_reason, strategist_cache_preferred, strategist_invocation, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested)
