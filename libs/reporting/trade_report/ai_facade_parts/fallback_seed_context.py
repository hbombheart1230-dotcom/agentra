"""Deterministic fallback report seed/context projection (dependency callables are passed explicitly).

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_report_ai_deterministic.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def fb_seed_action_entry_decision_seed(_build_shared_summary_seed, story_input, build_trade_report_memory_surface, _as_dict, _extract_policy_ref_context, _extract_scanner_bias_summary, _enrich_market_context_for_fallback, _fallback_section_seeds, _enrich_scanner_reason_for_fallback, _clip, *, facade):
    shared_seed = _build_shared_summary_seed(story_input)
    entry_execution_visibility = (
        shared_seed.get("entry_execution_visibility")
        if isinstance(shared_seed.get("entry_execution_visibility"), dict)
        else {}
    )
    market_context = story_input.get("market_context_human") if isinstance(story_input.get("market_context_human"), dict) else {}
    strategist_evidence = shared_seed.get("strategist_evidence") if isinstance(shared_seed.get("strategist_evidence"), dict) else {}
    scanner_reason = story_input.get("scanner_reason_human") if isinstance(story_input.get("scanner_reason_human"), dict) else {}
    has_runtime_market_context = bool(market_context)
    has_runtime_scanner_reason = bool(scanner_reason)
    filters_human = story_input.get("filters_human") if isinstance(story_input.get("filters_human"), dict) else {}
    monitor_reason = story_input.get("monitor_reason_human") if isinstance(story_input.get("monitor_reason_human"), dict) else {}
    guard_reason = story_input.get("guard_reason_human") if isinstance(story_input.get("guard_reason_human"), dict) else {}
    execution_outcome = story_input.get("execution_outcome_human") if isinstance(story_input.get("execution_outcome_human"), dict) else {}
    reporter_status = story_input.get("reporter_status_human") if isinstance(story_input.get("reporter_status_human"), dict) else {}
    memory_surface = build_trade_report_memory_surface(story_input)
    reporter_feedback_packet = _as_dict(memory_surface.get("reporter_feedback_packet"))
    operator_conclusion = (
        story_input.get("operator_conclusion_human") if isinstance(story_input.get("operator_conclusion_human"), dict) else {}
    )
    policy_ref_context = _extract_policy_ref_context(story_input, monitor_reason)
    scanner_bias_summary = _extract_scanner_bias_summary(story_input, scanner_reason)
    strategist_context = shared_seed.get("strategist_context") if isinstance(shared_seed.get("strategist_context"), dict) else {}
    market_context = _enrich_market_context_for_fallback(
        market_context=market_context,
        strategist_context=strategist_context,
        policy_ref_context=policy_ref_context,
        scanner_bias_summary=scanner_bias_summary,
    )
    has_runtime_monitor_reason = bool(monitor_reason)
    shared_scanner_reasoning = shared_seed.get("scanner_reasoning") if isinstance(shared_seed.get("scanner_reasoning"), dict) else {}
    shared_selection_trace = shared_scanner_reasoning.get("selection_trace") if isinstance(shared_scanner_reasoning.get("selection_trace"), dict) else {}
    section_seeds = _fallback_section_seeds(shared_seed)
    market_context_seed = section_seeds["market_context"]
    strategist_summary_seed = section_seeds["strategist_summary"]
    why_symbol_seed = section_seeds["why_symbol"]
    entry_decision_seed = section_seeds["entry_decision"]
    holding_story_seed = section_seeds["holding_story"]
    exit_decision_seed = section_seeds["exit_decision"]
    scanner_filters_seed = section_seeds["scanner_filters"]
    execution_quality_seed = section_seeds["execution_quality"]
    guard_approval_seed = section_seeds["guard_approval"]
    reporter_evaluation_seed = section_seeds["reporter_evaluation"]
    final_operator_conclusion_seed = section_seeds["final_operator_conclusion"]
    scanner_reason = _enrich_scanner_reason_for_fallback(
        scanner_reason=scanner_reason,
        shared_scanner_reasoning=shared_scanner_reasoning,
        shared_selection_trace=shared_selection_trace,
    )
    action = _clip(shared_seed.get("lifecycle_action"), max_len=24) or _clip(story_input.get("action"), max_len=24) or "WAIT"
    return (action, entry_decision_seed, entry_execution_visibility, execution_outcome, execution_quality_seed, exit_decision_seed, filters_human, final_operator_conclusion_seed, guard_approval_seed, guard_reason, has_runtime_market_context, has_runtime_monitor_reason, has_runtime_scanner_reason, holding_story_seed, market_context, market_context_seed, memory_surface, monitor_reason, operator_conclusion, reporter_evaluation_seed, reporter_feedback_packet, reporter_status, scanner_filters_seed, scanner_reason, shared_seed, shared_selection_trace, strategist_context, strategist_evidence, strategist_summary_seed, why_symbol_seed)
