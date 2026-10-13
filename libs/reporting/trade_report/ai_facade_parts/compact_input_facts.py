"""Stable compact prompt facts for the LLM story input.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_report_ai_compact_input.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


class CompactStoryFacts(NamedTuple):
    """Result of `compact_story_facts` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    commander_route: Any
    diagnostics: Any
    entry_execution_visibility: Any
    execution_outcome: Any
    execution_quality_seed: Any
    filters_human: Any
    guard_reason: Any
    holding_story_seed: Any
    lifecycle_summary: Any
    market_context: Any
    market_context_seed: Any
    monitor_reason: Any
    monitor_reasoning: Any
    operator_conclusion: Any
    policy_ref_context: Any
    report_section_seeds: Any
    reporter_status: Any
    scanner_bias_summary: Any
    scanner_filters_seed: Any
    scanner_reason: Any
    scanner_reasoning: Any
    strategist_context: Any
    strategist_evidence: Any
    strategist_summary_seed: Any
    why_symbol_seed: Any


def compact_story_facts(story_input, _build_shared_summary_seed, _extract_policy_ref_context, _extract_scanner_bias_summary, _as_dict, *, facade):
    market_context = story_input.get("market_context_human") if isinstance(story_input.get("market_context_human"), dict) else {}
    scanner_reason = story_input.get("scanner_reason_human") if isinstance(story_input.get("scanner_reason_human"), dict) else {}
    filters_human = story_input.get("filters_human") if isinstance(story_input.get("filters_human"), dict) else {}
    monitor_reason = story_input.get("monitor_reason_human") if isinstance(story_input.get("monitor_reason_human"), dict) else {}
    guard_reason = story_input.get("guard_reason_human") if isinstance(story_input.get("guard_reason_human"), dict) else {}
    execution_outcome = story_input.get("execution_outcome_human") if isinstance(story_input.get("execution_outcome_human"), dict) else {}
    reporter_status = story_input.get("reporter_status_human") if isinstance(story_input.get("reporter_status_human"), dict) else {}
    operator_conclusion = story_input.get("operator_conclusion_human") if isinstance(story_input.get("operator_conclusion_human"), dict) else {}
    lifecycle_summary = story_input.get("lifecycle_summary") if isinstance(story_input.get("lifecycle_summary"), dict) else {}
    diagnostics = story_input.get("ai_report_diagnostics") if isinstance(story_input.get("ai_report_diagnostics"), dict) else {}
    shared_seed = _build_shared_summary_seed(story_input)
    commander_route = shared_seed.get("commander_route") if isinstance(shared_seed.get("commander_route"), dict) else {}
    strategist_evidence = shared_seed.get("strategist_evidence") if isinstance(shared_seed.get("strategist_evidence"), dict) else {}
    strategist_context = shared_seed.get("strategist_context") if isinstance(shared_seed.get("strategist_context"), dict) else {}
    entry_execution_visibility = (
        shared_seed.get("entry_execution_visibility")
        if isinstance(shared_seed.get("entry_execution_visibility"), dict)
        else {}
    )
    scanner_reasoning = shared_seed.get("scanner_reasoning") if isinstance(shared_seed.get("scanner_reasoning"), dict) else {}
    monitor_reasoning = shared_seed.get("monitor_reasoning") if isinstance(shared_seed.get("monitor_reasoning"), dict) else {}
    policy_ref_context = _extract_policy_ref_context(story_input, monitor_reason)
    scanner_bias_summary = _extract_scanner_bias_summary(story_input, scanner_reason)
    report_section_seeds = shared_seed.get("report_section_seeds") if isinstance(shared_seed.get("report_section_seeds"), dict) else {}
    market_context_seed = _as_dict(report_section_seeds.get("market_context_at_entry"))
    strategist_summary_seed = _as_dict(report_section_seeds.get("strategist_summary"))
    why_symbol_seed = _as_dict(report_section_seeds.get("why_this_symbol_was_chosen"))
    holding_story_seed = _as_dict(report_section_seeds.get("holding_monitoring_story"))
    scanner_filters_seed = _as_dict(report_section_seeds.get("scanner_filters"))
    execution_quality_seed = _as_dict(report_section_seeds.get("execution_quality"))
    return CompactStoryFacts(commander_route, diagnostics, entry_execution_visibility, execution_outcome, execution_quality_seed, filters_human, guard_reason, holding_story_seed, lifecycle_summary, market_context, market_context_seed, monitor_reason, monitor_reasoning, operator_conclusion, policy_ref_context, report_section_seeds, reporter_status, scanner_bias_summary, scanner_filters_seed, scanner_reason, scanner_reasoning, strategist_context, strategist_evidence, strategist_summary_seed, why_symbol_seed)


def cp_facts_execution_bullets_execution_summary(_clip, market_context, market_context_seed, _listify, strategist_summary_seed, scanner_reason, why_symbol_seed, filters_human, scanner_filters_seed, monitor_reason, holding_story_seed, guard_reason, _as_dict, report_section_seeds, execution_outcome, execution_quality_seed, *, facade):
    market_context_summary = _clip(market_context.get("summary"), max_len=320) or _clip(market_context_seed.get("summary"), max_len=320)
    market_context_bullets = _listify(market_context.get("bullets"), max_items=6, max_len=220) or _listify(market_context_seed.get("bullets"), max_items=6, max_len=220)
    if not market_context_summary:
        market_context_summary = _clip(strategist_summary_seed.get("summary"), max_len=320)
    scanner_summary = _clip(scanner_reason.get("summary"), max_len=320) or _clip(why_symbol_seed.get("summary"), max_len=320)
    scanner_bullets = _listify(scanner_reason.get("bullets"), max_items=6, max_len=220) or _listify(why_symbol_seed.get("bullets"), max_items=6, max_len=220)
    filters_summary = _clip(filters_human.get("summary"), max_len=280) or _clip(scanner_filters_seed.get("summary"), max_len=280)
    filters_bullets = _listify(filters_human.get("bullets"), max_items=6, max_len=220) or _listify(scanner_filters_seed.get("bullets"), max_items=6, max_len=220)
    monitor_summary = _clip(monitor_reason.get("summary"), max_len=280) or _clip(holding_story_seed.get("summary"), max_len=280)
    monitor_bullets = _listify(monitor_reason.get("bullets"), max_items=6, max_len=220) or _listify(holding_story_seed.get("bullets"), max_items=6, max_len=220)
    guard_summary = _clip(guard_reason.get("summary"), max_len=280) or _clip((_as_dict(report_section_seeds.get("guard_approval_result"))).get("summary"), max_len=280)
    guard_bullets = _listify(guard_reason.get("bullets"), max_items=6, max_len=220) or _listify((_as_dict(report_section_seeds.get("guard_approval_result"))).get("bullets"), max_items=6, max_len=220)
    execution_summary = _clip(execution_outcome.get("summary"), max_len=280) or _clip(execution_quality_seed.get("summary"), max_len=280)
    execution_bullets = _listify(execution_outcome.get("bullets"), max_items=6, max_len=220) or _listify(execution_quality_seed.get("bullets"), max_items=6, max_len=220)
    reporter_seed = _as_dict(report_section_seeds.get("reporter_evaluation"))
    return (execution_bullets, execution_summary, filters_bullets, filters_summary, guard_bullets, guard_summary, market_context_bullets, market_context_summary, monitor_bullets, monitor_summary, reporter_seed, scanner_bullets, scanner_summary)
