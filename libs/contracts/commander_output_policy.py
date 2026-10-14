"""Commander output decision summary and applied-policy provenance facts.

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_commander_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from typing import Any, NamedTuple

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _listify,
)


class CommanderDecisionRefreshFacts(NamedTuple):
    """Result of `commander_decision_refresh_facts` (positional order is the pre-T3.5 tuple order)."""

    decision_summary: Any
    llm_invocation_policy: Any
    monitor_mission: Any
    post_scanner_refresh_context: Any
    post_scanner_refresh_reason: Any
    post_scanner_refresh_requested: Any
    runtime_cache_reuse_context: Any
    runtime_cache_reuse_reason: Any
    runtime_refresh_context: Any
    runtime_refresh_reason: Any
    runtime_refresh_requested: Any
    scanner_mission: Any
    shadow_alignment: Any
    shadow_assessment_summary: Any
    shadow_reason_code: Any
    shadow_runtime: Any
    source_priority: Any
    strategist_cache_preference_context: Any
    strategist_cache_preference_reason: Any
    strategist_cache_preferred: Any
    strategist_fallback_used: Any
    strategist_refresh_context: Any
    strategist_refresh_reason: Any
    strategist_refresh_requested: Any

class CommanderAppliedPolicyProvenance(NamedTuple):
    """Result of `commander_applied_policy_provenance` (positional order is the pre-T3.5 tuple order)."""

    applied_policy: Any
    applied_policy_source_chain: Any
    commander_applied_policy_summary: Any
    commander_horizon_policy: Any
    horizon_context: Any
    llm_policy_source: Any
    override_action: Any
    override_context: Any
    override_reason: Any
    override_triggered: Any
    policy_default_filled_fields: Any
    policy_fallback_reason: Any
    policy_fallback_used: Any
    policy_partial_normalized: Any
    policy_source: Any
    policy_sources: Any
    policy_validation_invalid_fields: Any
    policy_validation_missing_fields: Any
    policy_validation_status: Any
    reporter_feedback_mode: Any
    reporter_feedback_mode_reason: Any
    reporter_feedback_mode_source: Any
    reporter_feedback_semantics: Any
    strategist_runtime_policy_source: Any

def commander_decision_refresh_facts(commander_decision, reason, decision_frame, state, shadow_assessment, runtime_fast_path, strategist_cache_used):
    scanner_mission = _clip(commander_decision.get("scanner_mission"), max_len=220)
    monitor_mission = _clip(commander_decision.get("monitor_mission"), max_len=220)
    llm_invocation_policy = _clip(
        commander_decision.get("llm_invocation_policy")
        or commander_decision.get("llm_policy"),
        max_len=120,
    )
    decision_summary = _clip(
        commander_decision.get("decision_summary")
        or decision_frame.get("final_reason")
        or reason
        or state.get("runtime_status"),
        max_len=280,
    )
    shadow_reason_code = _clip(shadow_assessment.get("no_trade_reason_code"), max_len=80)
    shadow_assessment_summary = _clip(
        shadow_assessment.get("reason_summary")
        or shadow_assessment.get("comparison_summary"),
        max_len=280,
    )
    shadow_alignment = _clip(
        (
            _dict(shadow_assessment.get("post_strategist_assessment")).get("recommendation_gap")
            or _dict(shadow_assessment.get("end_of_cycle_summary")).get("recommendation_gap")
        ),
        max_len=120,
    )
    source_priority = _listify(commander_decision.get("source_priority"), limit=4, max_len=40)
    strategist_fallback_used = bool(commander_decision.get("strategist_fallback_used"))
    strategist_refresh_requested = bool(commander_decision.get("strategist_refresh_requested"))
    strategist_refresh_reason = _clip(commander_decision.get("strategist_refresh_reason"), max_len=120)
    strategist_refresh_context = _dict(commander_decision.get("strategist_refresh_context"))
    strategist_cache_preferred = bool(commander_decision.get("strategist_cache_preferred"))
    strategist_cache_preference_reason = _clip(commander_decision.get("strategist_cache_preference_reason"), max_len=120)
    strategist_cache_preference_context = _dict(commander_decision.get("strategist_cache_preference_context"))
    shadow_runtime = _dict(state.get("commander_shadow_runtime"))
    runtime_refresh_requested = bool(shadow_runtime.get("pre_buy_refresh_requested"))
    runtime_refresh_reason = _clip(shadow_runtime.get("pre_buy_refresh_reason"), max_len=120)
    runtime_refresh_context = _dict(shadow_runtime.get("pre_buy_refresh_context"))
    post_scanner_refresh_requested = bool(shadow_runtime.get("post_scanner_refresh_requested"))
    post_scanner_refresh_reason = _clip(shadow_runtime.get("post_scanner_refresh_reason"), max_len=120)
    post_scanner_refresh_context = _dict(shadow_runtime.get("post_scanner_refresh_context"))
    if not post_scanner_refresh_requested and _clip(runtime_fast_path.get("reason"), max_len=120) == "post_scanner_selected_symbol_refresh":
        post_scanner_refresh_requested = True
        post_scanner_refresh_reason = _clip(runtime_fast_path.get("strategist_refresh_reason"), max_len=120)
        post_scanner_refresh_context = {"selected_symbol": _clip(runtime_fast_path.get("selected_symbol"), max_len=32)}
    runtime_cache_reuse_reason = _clip(
        runtime_fast_path.get("reason") if strategist_cache_used else "",
        max_len=120,
    )
    runtime_cache_reuse_context = _dict(runtime_fast_path) if strategist_cache_used else {}
    return CommanderDecisionRefreshFacts(decision_summary, llm_invocation_policy, monitor_mission, post_scanner_refresh_context, post_scanner_refresh_reason, post_scanner_refresh_requested, runtime_cache_reuse_context, runtime_cache_reuse_reason, runtime_refresh_context, runtime_refresh_reason, runtime_refresh_requested, scanner_mission, shadow_alignment, shadow_assessment_summary, shadow_reason_code, shadow_runtime, source_priority, strategist_cache_preference_context, strategist_cache_preference_reason, strategist_cache_preferred, strategist_fallback_used, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested)


def commander_applied_policy_provenance(commander_decision, state):
    applied_policy = _dict(commander_decision.get("applied_policy"))
    commander_horizon_policy = (
        _dict(commander_decision.get("commander_horizon_policy"))
        or _dict(state.get("commander_horizon_policy"))
        or _dict(applied_policy.get("horizon"))
        or _dict(applied_policy.get("commander_horizon_policy"))
    )
    horizon_context = _dict(commander_decision.get("horizon_context")) or _dict(state.get("horizon_context"))
    policy_source = _clip(commander_decision.get("policy_source"), max_len=120)
    policy_validation_status = _clip(commander_decision.get("policy_validation_status"), max_len=80)
    policy_fallback_used = bool(commander_decision.get("policy_fallback_used"))
    policy_fallback_reason = _clip(commander_decision.get("policy_fallback_reason"), max_len=220)
    policy_partial_normalized = bool(commander_decision.get("policy_partial_normalized"))
    policy_default_filled_fields = _listify(commander_decision.get("policy_default_filled_fields"), limit=12, max_len=80)
    policy_validation_missing_fields = _listify(commander_decision.get("policy_validation_missing_fields"), limit=12, max_len=80)
    policy_validation_invalid_fields = _listify(commander_decision.get("policy_validation_invalid_fields"), limit=12, max_len=80)
    override_triggered = bool(commander_decision.get("override_triggered"))
    override_reason = _clip(commander_decision.get("override_reason"), max_len=180)
    override_action = _clip(commander_decision.get("override_action"), max_len=120)
    override_context = _dict(commander_decision.get("override_context"))
    applied_policy_source_chain = _listify(commander_decision.get("applied_policy_source_chain"), limit=6, max_len=80)
    reporter_feedback_mode = _clip(commander_decision.get("reporter_feedback_mode"), max_len=40)
    reporter_feedback_mode_source = _clip(commander_decision.get("reporter_feedback_mode_source"), max_len=80)
    reporter_feedback_mode_reason = _clip(commander_decision.get("reporter_feedback_mode_reason"), max_len=120)
    reporter_feedback_semantics = _clip(commander_decision.get("reporter_feedback_semantics"), max_len=40)
    commander_applied_policy_summary = _dict(commander_decision.get("commander_applied_policy_summary"))
    policy_sources = _dict(commander_decision.get("policy_sources"))
    strategist_runtime_policy_source = _clip(commander_decision.get("strategist_runtime_policy_source"), max_len=80)
    llm_policy_source = _clip(commander_decision.get("llm_policy_source"), max_len=80)
    return CommanderAppliedPolicyProvenance(applied_policy, applied_policy_source_chain, commander_applied_policy_summary, commander_horizon_policy, horizon_context, llm_policy_source, override_action, override_context, override_reason, override_triggered, policy_default_filled_fields, policy_fallback_reason, policy_fallback_used, policy_partial_normalized, policy_source, policy_sources, policy_validation_invalid_fields, policy_validation_missing_fields, policy_validation_status, reporter_feedback_mode, reporter_feedback_mode_reason, reporter_feedback_mode_source, reporter_feedback_semantics, strategist_runtime_policy_source)
