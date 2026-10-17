from __future__ import annotations

from typing import Any, Callable, Dict, List

from libs.reporting.trade_execution_outcome_text import execution_outcome_summary_is_placeholder
from libs.reporting.trade_report_common import (
    compact_named_rows,
    compact_scalar_dict,
    listify,
    report_clip,
)
import sys as _r3_sys
from libs.reporting.trade_report.ai_facade_parts.compact_input_facts import (
    compact_story_facts,
    cp_facts_execution_bullets_execution_summary,
)
from libs.reporting.trade_report.ai_facade_parts.compact_input_payload import (
    cp_payload_value_result,
)
from libs.agents.reporter.read_models.compact_input_bodies_01 import (  # R-4 owner bodies (facade-injected)
    compact_section_seed_for_llm_r4_impl,
    sparse_story_input_for_llm_r4_impl,
)


def as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}

def compact_section_seed_for_llm(value: Any) -> Dict[str, Any]:
    return compact_section_seed_for_llm_r4_impl(value, facade=_r3_sys.modules[__name__])


def sparse_story_input_for_llm(
    story_input: Dict[str, Any],
    *,
    compact_story_input_for_llm: Callable[[Dict[str, Any]], Dict[str, Any]],
    reporter_summary_is_placeholder: Callable[[Any], bool],
    compact_timeline_rows: Callable[..., List[Dict[str, Any]]],
) -> Dict[str, Any]:
    return sparse_story_input_for_llm_r4_impl(story_input, compact_story_input_for_llm=compact_story_input_for_llm, reporter_summary_is_placeholder=reporter_summary_is_placeholder, compact_timeline_rows=compact_timeline_rows, facade=_r3_sys.modules[__name__])

def compact_story_input_for_llm(
    story_input: Dict[str, Any],
    *,
    deps: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the compact LLM story payload behind the reporting façade."""

    _build_shared_summary_seed = deps["build_shared_summary_seed"]
    _extract_policy_ref_context = deps["extract_policy_ref_context"]
    _extract_scanner_bias_summary = deps["extract_scanner_bias_summary"]
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    _listify = deps["listify"]
    _compact_scalar_dict = deps["compact_scalar_dict"]
    _reporter_summary_is_placeholder = deps["reporter_summary_is_placeholder"]
    _compact_strategist_report_context = deps["compact_strategist_report_context"]
    _build_report_strategist_refresh_trace = deps["build_report_strategist_refresh_trace"]
    _compact_entry_or_exit_summary = deps["compact_entry_or_exit_summary"]
    _compact_holding_summary = deps["compact_holding_summary"]
    _compact_named_rows = deps["compact_named_rows"]
    _compact_monitor_snapshot = deps["compact_monitor_snapshot"]
    _compact_entry_candidate_cascade = deps["compact_entry_candidate_cascade"]
    _compact_timeline_rows = deps["compact_timeline_rows"]
    _evidence_digest = deps["evidence_digest"]
    execution_outcome_summary_is_placeholder = deps["execution_outcome_summary_is_placeholder"]

    commander_route, diagnostics, entry_execution_visibility, execution_outcome, execution_quality_seed, filters_human, guard_reason, holding_story_seed, lifecycle_summary, market_context, market_context_seed, monitor_reason, monitor_reasoning, operator_conclusion, policy_ref_context, report_section_seeds, reporter_status, scanner_bias_summary, scanner_filters_seed, scanner_reason, scanner_reasoning, strategist_context, strategist_evidence, strategist_summary_seed, why_symbol_seed = compact_story_facts(story_input=story_input, _build_shared_summary_seed=_build_shared_summary_seed, _extract_policy_ref_context=_extract_policy_ref_context, _extract_scanner_bias_summary=_extract_scanner_bias_summary, _as_dict=_as_dict, facade=_r3_sys.modules[__name__])
    if _clip(execution_outcome.get("summary"), max_len=280) and execution_outcome_summary_is_placeholder(execution_quality_seed.get("summary")):
        execution_quality_seed = dict(execution_quality_seed)
        execution_quality_seed["summary"] = _clip(execution_outcome.get("summary"), max_len=280)
        if execution_outcome.get("bullets"):
            execution_quality_seed["bullets"] = _listify(execution_outcome.get("bullets"), max_items=6, max_len=220)
        if execution_outcome.get("status"):
            execution_quality_seed["status"] = _clip(execution_outcome.get("status"), max_len=48)
    execution_bullets, execution_summary, filters_bullets, filters_summary, guard_bullets, guard_summary, market_context_bullets, market_context_summary, monitor_bullets, monitor_summary, reporter_seed, scanner_bullets, scanner_summary = cp_facts_execution_bullets_execution_summary(_clip=_clip, market_context=market_context, market_context_seed=market_context_seed, _listify=_listify, strategist_summary_seed=strategist_summary_seed, scanner_reason=scanner_reason, why_symbol_seed=why_symbol_seed, filters_human=filters_human, scanner_filters_seed=scanner_filters_seed, monitor_reason=monitor_reason, holding_story_seed=holding_story_seed, guard_reason=guard_reason, _as_dict=_as_dict, report_section_seeds=report_section_seeds, execution_outcome=execution_outcome, execution_quality_seed=execution_quality_seed, facade=_r3_sys.modules[__name__])
    if _reporter_summary_is_placeholder(reporter_status.get("summary")) and _clip(reporter_seed.get("summary"), max_len=280):
        reporter_status = dict(reporter_status)
        reporter_status["summary"] = _clip(reporter_seed.get("summary"), max_len=280)
        if reporter_seed.get("bullets"):
            reporter_status["bullets"] = _listify(reporter_seed.get("bullets"), max_items=5, max_len=180)
        if reporter_seed.get("status"):
            reporter_status["status"] = _clip(reporter_seed.get("status"), max_len=32)
        if reporter_seed.get("grade"):
            reporter_status["grade"] = _clip(reporter_seed.get("grade"), max_len=24)
    reporter_summary = _clip(reporter_status.get("summary"), max_len=280) or _clip(reporter_seed.get("summary"), max_len=280)
    reporter_bullets = _listify(reporter_status.get("bullets"), max_items=5, max_len=180) or _listify(reporter_seed.get("bullets"), max_items=5, max_len=180)
    conclusion_current_action = _clip(operator_conclusion.get("current_action"), max_len=24) or _clip((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("current_action"), max_len=24)
    conclusion_watch_next = _listify(operator_conclusion.get("watch_next"), max_items=5, max_len=180) or _listify((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("watch_next"), max_items=5, max_len=180)
    conclusion_thesis_invalidation = _listify(operator_conclusion.get("thesis_invalidation"), max_items=5, max_len=180) or _listify((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("thesis_invalidation"), max_items=5, max_len=180)
    conclusion_summary = _clip(operator_conclusion.get("summary"), max_len=280) or _clip((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("summary"), max_len=280)
    return cp_payload_value_result(strategist_evidence=strategist_evidence, entry_execution_visibility=entry_execution_visibility, _compact_strategist_report_context=_compact_strategist_report_context, story_input=story_input, _build_report_strategist_refresh_trace=_build_report_strategist_refresh_trace, _compact_entry_or_exit_summary=_compact_entry_or_exit_summary, _compact_holding_summary=_compact_holding_summary, scanner_bias_summary=scanner_bias_summary, market_context_summary=market_context_summary, market_context_bullets=market_context_bullets, scanner_summary=scanner_summary, scanner_bullets=scanner_bullets, filters_summary=filters_summary, filters_bullets=filters_bullets, monitor_summary=monitor_summary, monitor_bullets=monitor_bullets, guard_summary=guard_summary, guard_bullets=guard_bullets, execution_summary=execution_summary, execution_bullets=execution_bullets, reporter_summary=reporter_summary, reporter_bullets=reporter_bullets, conclusion_summary=conclusion_summary, conclusion_current_action=conclusion_current_action, conclusion_watch_next=conclusion_watch_next, conclusion_thesis_invalidation=conclusion_thesis_invalidation, _compact_timeline_rows=_compact_timeline_rows, _listify=_listify, _as_dict=_as_dict, _clip=_clip, _compact_scalar_dict=_compact_scalar_dict, _compact_named_rows=_compact_named_rows, _compact_monitor_snapshot=_compact_monitor_snapshot, monitor_reason=monitor_reason, _evidence_digest=_evidence_digest, market_context=market_context, commander_route=commander_route, scanner_reason=scanner_reason, _compact_entry_candidate_cascade=_compact_entry_candidate_cascade, lifecycle_summary=lifecycle_summary, policy_ref_context=policy_ref_context, scanner_reasoning=scanner_reasoning, guard_reason=guard_reason, execution_outcome=execution_outcome, diagnostics=diagnostics, strategist_context=strategist_context, monitor_reasoning=monitor_reasoning, reporter_status=reporter_status, report_section_seeds=report_section_seeds, execution_quality_seed=execution_quality_seed, facade=_r3_sys.modules[__name__])



