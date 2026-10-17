from __future__ import annotations

from typing import Any, Callable, Dict, List
import sys as _r3_sys
from libs.reporting.trade_report.ai_facade_parts.fallback_seed_context import (
    fallback_report_seed,
)
from libs.reporting.trade_report.ai_facade_parts.fallback_summary_status import (
    fb_summary_effective_scanner_selection_trace_exit_s,
    fb_summary_confidence_executive_reason,
)
from libs.reporting.trade_report.ai_facade_parts.fallback_sections_schema import (
    fb_sections_entry_decision_exit_decision,
    fb_sections_out,
)
from libs.agents.reporter.read_models.report_deterministic_bodies_01 import (  # R-4 owner bodies (facade-injected)
    build_shared_facts_r4_impl,
    attach_backward_compatible_aliases_r4_impl,
    fallback_section_seeds_r4_impl,
    append_news_scanner_choice_details_r4_impl,
    build_monitor_snapshot_r4_impl,
    enrich_market_context_for_fallback_r4_impl,
    enrich_scanner_reason_for_fallback_r4_impl,
    merge_trade_report_candidate_r4_impl,
    build_deterministic_trade_report_r4_impl,
)


def build_shared_facts(
    *,
    shared_seed: Dict[str, Any],
    action: str,
    symbol: str,
    trade_id: str,
    status_text: str,
    clip: Callable[..., str],
    as_dict: Callable[[Any], Dict[str, Any]],
) -> Dict[str, Any]:
    return build_shared_facts_r4_impl(shared_seed=shared_seed, action=action, symbol=symbol, trade_id=trade_id, status_text=status_text, clip=clip, as_dict=as_dict, facade=_r3_sys.modules[__name__])


def attach_backward_compatible_aliases(report: Dict[str, Any]) -> Dict[str, Any]:
    return attach_backward_compatible_aliases_r4_impl(report, facade=_r3_sys.modules[__name__])


def fallback_section_seeds(
    shared_seed: Dict[str, Any],
    *,
    as_dict: Callable[[Any], Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    return fallback_section_seeds_r4_impl(shared_seed, as_dict=as_dict, facade=_r3_sys.modules[__name__])


def append_news_scanner_choice_details(
    why_symbol_bullets: List[str],
    news_scanner_contribution: Dict[str, Any],
    *,
    listify: Callable[..., List[Any]],
) -> List[str]:
    return append_news_scanner_choice_details_r4_impl(why_symbol_bullets, news_scanner_contribution, listify=listify, facade=_r3_sys.modules[__name__])


def build_monitor_snapshot(
    *,
    monitor_reason: Dict[str, Any],
    story_input: Dict[str, Any],
    action: str,
    clip: Callable[..., str],
    listify: Callable[..., List[Any]],
    as_dict: Callable[[Any], Dict[str, Any]],
    entry_execution_visibility: Dict[str, Any] | None = None,
    compact_entry_candidate_cascade: Callable[[Any], Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    return build_monitor_snapshot_r4_impl(monitor_reason=monitor_reason, story_input=story_input, action=action, clip=clip, listify=listify, as_dict=as_dict, entry_execution_visibility=entry_execution_visibility, compact_entry_candidate_cascade=compact_entry_candidate_cascade, facade=_r3_sys.modules[__name__])


def enrich_market_context_for_fallback(
    *,
    market_context: Dict[str, Any],
    strategist_context: Dict[str, Any],
    policy_ref_context: Dict[str, Any],
    scanner_bias_summary: Dict[str, Any],
) -> Dict[str, Any]:
    return enrich_market_context_for_fallback_r4_impl(market_context=market_context, strategist_context=strategist_context, policy_ref_context=policy_ref_context, scanner_bias_summary=scanner_bias_summary, facade=_r3_sys.modules[__name__])


def enrich_scanner_reason_for_fallback(
    *,
    scanner_reason: Dict[str, Any],
    shared_scanner_reasoning: Dict[str, Any],
    shared_selection_trace: Dict[str, Any],
) -> Dict[str, Any]:
    return enrich_scanner_reason_for_fallback_r4_impl(scanner_reason=scanner_reason, shared_scanner_reasoning=shared_scanner_reasoning, shared_selection_trace=shared_selection_trace, facade=_r3_sys.modules[__name__])


def merge_trade_report_candidate(
    story_input: Dict[str, Any],
    candidate: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    fallback_report: Callable[..., Dict[str, Any]],
    normalize_section: Callable[..., Dict[str, Any]],
    merge_section_with_fallback: Callable[..., Dict[str, Any]],
    prefer_fallback_text: Callable[[Any, Any], str],
    listify: Callable[..., List[Any]],
    clip: Callable[..., str],
    normalize_trade_report_output: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    return merge_trade_report_candidate_r4_impl(story_input, candidate, status=status, mode=mode, model=model, reason=reason, fallback_report=fallback_report, normalize_section=normalize_section, merge_section_with_fallback=merge_section_with_fallback, prefer_fallback_text=prefer_fallback_text, listify=listify, clip=clip, normalize_trade_report_output=normalize_trade_report_output, facade=_r3_sys.modules[__name__])


def build_deterministic_trade_report(
    story_input: Dict[str, Any],
    *,
    fallback_report: Callable[..., Dict[str, Any]],
    attach_report_status_matrix: Callable[..., Dict[str, Any]],
) -> Dict[str, Any]:
    return build_deterministic_trade_report_r4_impl(story_input, fallback_report=fallback_report, attach_report_status_matrix=attach_report_status_matrix, facade=_r3_sys.modules[__name__])


def failure_report(
    story_input: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    error: str = "",
    build_shared_summary_seed: Callable[[Dict[str, Any]], Dict[str, Any]],
    clip: Callable[..., str],
    actual_lifecycle_action: Callable[[Dict[str, Any]], str],
    as_dict: Callable[[Any], Dict[str, Any]],
    utc_now_iso: Callable[[], str],
    build_report_strategist_refresh_trace: Callable[[Dict[str, Any]], Dict[str, Any]],
    listify: Callable[..., List[Any]],
    build_monitor_snapshot_fn: Callable[..., Dict[str, Any]],
    normalize_trade_report_output: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    shared_seed = build_shared_summary_seed(story_input)
    trade_id = clip(shared_seed.get("trade_id"), max_len=120) or clip(story_input.get("trade_id") or story_input.get("story_id"), max_len=120)
    action = clip(shared_seed.get("lifecycle_action"), max_len=24) or actual_lifecycle_action(story_input)
    symbol = clip(shared_seed.get("symbol"), max_len=32) or clip(story_input.get("symbol"), max_len=32) or "unknown"
    status_text = clip(shared_seed.get("lifecycle_status"), max_len=32) or clip(story_input.get("status"), max_len=32) or "unknown"
    reporter_status = story_input.get("reporter_status_human") if isinstance(story_input.get("reporter_status_human"), dict) else {}
    monitor_reason = story_input.get("monitor_reason_human") if isinstance(story_input.get("monitor_reason_human"), dict) else {}
    full_timeline = [
        row
        for row in list(story_input.get("timeline") or [])
        if isinstance(row, dict)
    ][:24]
    out = {
        "schema_version": "ai_trade_report.v2",
        "generated_at": utc_now_iso(),
        "trade_id": trade_id,
        "story_id": clip(story_input.get("story_id"), max_len=120) or trade_id,
        "run_id": clip(story_input.get("run_id"), max_len=120),
        "symbol": symbol,
        "action": action,
        "status": status_text,
        "story_type": clip(story_input.get("story_type"), max_len=40),
        "execution_mode_label": clip(story_input.get("execution_mode_label"), max_len=80),
        "generation": {
            "status": status,
            "mode": mode,
            "model": clip(model, max_len=120),
            "reason": clip(reason, max_len=320),
        },
        "failure": {
            "status": status,
            "reason": clip(reason, max_len=320),
            "error": clip(error, max_len=500),
        },
        "executive_summary": {
            "headline": f"AI trade report failed for {symbol}",
            "action": action,
            "symbol": symbol,
            "confidence": "not_available",
            "summary": "AI trade report generation failed after retry attempts. Review the saved LLM response artifact for details.",
        },
        "market_context_at_entry": {
            "summary": "AI generation failed before a rendered market-context section was produced.",
            "bullets": [],
        },
        "strategist_summary": {
            "summary": "AI generation failed before a rendered strategist-summary section was produced.",
            "bullets": [],
        },
        "strategist_refresh_trace": build_report_strategist_refresh_trace(story_input),
        "why_this_symbol_was_chosen": {
            "summary": "AI generation failed before a rendered symbol-selection section was produced.",
            "bullets": [],
        },
        "entry_decision": {
            "summary": "AI generation failed before a rendered entry-decision section was produced.",
            "bullets": [],
        },
        "holding_monitoring_story": {
            "summary": "AI generation failed before a rendered holding-monitoring section was produced.",
            "bullets": listify(monitor_reason.get("bullets"), max_items=8, max_len=260),
        },
        "exit_decision": {
            "summary": "AI generation failed before a rendered exit-decision section was produced.",
            "bullets": [],
        },
        "execution_quality": {
            "summary": "AI generation failed before a rendered execution-quality section was produced.",
            "bullets": [],
        },
        "monitor_snapshot": build_monitor_snapshot_fn(
            monitor_reason=monitor_reason,
            story_input=story_input,
            action=action,
        ),
        "scanner_filters": {
            "summary": "AI generation failed before a rendered scanner-filter section was produced.",
            "bullets": [],
        },
        "guard_approval_result": {
            "summary": "AI generation failed before a rendered guard-approval section was produced.",
            "bullets": [],
        },
        "reporter_evaluation": {
            "summary": clip(reporter_status.get("summary"), max_len=600) or "Reporter linkage status was recorded separately.",
            "status": clip(reporter_status.get("status"), max_len=40) or "missing",
            "grade": clip(reporter_status.get("grade"), max_len=16) or "N/A",
            "bullets": listify(reporter_status.get("bullets"), max_items=8, max_len=260),
        },
        "errors_weaknesses_improvement_points": {
            "summary": "AI generation failed and no rendered improvement section is available.",
            "bullets": [entry for entry in [clip(reason, max_len=240), clip(error, max_len=240)] if entry],
        },
        "full_timeline": full_timeline,
        "timeline": full_timeline,
        "final_operator_conclusion": {
            "summary": "AI generation failed. Review lifecycle artifacts and the saved LLM response artifact before taking action.",
            "current_action": "HOLD" if status_text.lower() == "open" and action == "BUY" else action,
            "watch_next": [],
            "thesis_invalidation": [],
        },
    }
    out["market_context"] = dict(out.get("market_context_at_entry") or {})
    out["why_this_symbol"] = dict(out.get("why_this_symbol_was_chosen") or {})
    out["scanner_logic_and_filters"] = dict(out.get("scanner_filters") or {})
    out["monitor_trigger_reasoning"] = dict(out.get("holding_monitoring_story") or {})
    out["execution_result"] = dict(out.get("execution_quality") or {})
    return normalize_trade_report_output(story_input, out)

def fallback_report(
    story_input: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    deps: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the deterministic fallback report behind the compatibility façade."""

    _build_shared_summary_seed = deps["build_shared_summary_seed"]
    build_trade_report_memory_surface = deps["build_trade_report_memory_surface"]
    _as_dict = deps["as_dict"]
    _extract_policy_ref_context = deps["extract_policy_ref_context"]
    _extract_scanner_bias_summary = deps["extract_scanner_bias_summary"]
    _enrich_market_context_for_fallback = deps["enrich_market_context_for_fallback"]
    _fallback_section_seeds = deps["fallback_section_seeds"]
    _enrich_scanner_reason_for_fallback = deps["enrich_scanner_reason_for_fallback"]
    _clip = deps["clip"]
    _build_report_monitor_snapshot = deps["build_report_monitor_snapshot"]
    _resolve_entry_monitor_reason = deps["resolve_entry_monitor_reason"]
    _listify = deps["listify"]
    _scanner_chart_feature_coverage = deps["scanner_chart_feature_coverage"]
    _build_scanner_choice_bullets = deps["build_scanner_choice_bullets"]
    _append_news_scanner_choice_details = deps["append_news_scanner_choice_details"]
    _lifecycle_summary_conflicts_with_status = deps["lifecycle_summary_conflicts_with_status"]
    _build_scanner_choice_summary = deps["build_scanner_choice_summary"]
    _build_market_context_summary = deps["build_market_context_summary"]
    _build_market_context_bullets = deps["build_market_context_bullets"]
    _build_market_scanner_linkage_bullet = deps["build_market_scanner_linkage_bullet"]
    _build_strategist_summary_section = deps["build_strategist_summary_section"]
    _build_entry_decision_summary = deps["build_entry_decision_summary"]
    _build_entry_decision_bullets = deps["build_entry_decision_bullets"]
    _build_holding_story_summary = deps["build_holding_story_summary"]
    _build_holding_story_bullets = deps["build_holding_story_bullets"]
    _build_exit_decision_summary = deps["build_exit_decision_summary"]
    _build_exit_decision_bullets = deps["build_exit_decision_bullets"]
    _build_execution_quality_section = deps["build_execution_quality_section"]
    _build_scanner_filters_summary = deps["build_scanner_filters_summary"]
    _build_scanner_filters_bullets = deps["build_scanner_filters_bullets"]
    _build_reporter_evaluation_section = deps["build_reporter_evaluation_section"]
    _holding_duration_label = deps["holding_duration_label"]
    _exit_reason_label = deps["exit_reason_label"]
    _is_low_information_bullet = deps["is_low_information_bullet"]
    _reporter_summary_is_placeholder = deps["reporter_summary_is_placeholder"]
    _scanner_basis_text = deps["scanner_basis_text"]
    _build_report_shared_facts = deps["build_report_shared_facts"]
    _attach_backward_compatible_aliases = deps["attach_backward_compatible_aliases"]
    _build_report_strategist_refresh_trace = deps["build_report_strategist_refresh_trace"]
    _compact_strategist_report_context = deps["compact_strategist_report_context"]
    _compact_scalar_dict = deps["compact_scalar_dict"]
    _story_post_exit_shadow = deps["story_post_exit_shadow"]
    _utc_now_iso = deps["utc_now_iso"]
    build_trade_report_truth_surface = deps["build_trade_report_truth_surface"]
    build_trade_memory_application_surface = deps["build_trade_memory_application_surface"]
    execution_outcome_summary_is_placeholder = deps["execution_outcome_summary_is_placeholder"]

    action, entry_decision_seed, entry_execution_visibility, execution_outcome, execution_quality_seed, exit_decision_seed, filters_human, final_operator_conclusion_seed, guard_approval_seed, guard_reason, has_runtime_market_context, has_runtime_monitor_reason, has_runtime_scanner_reason, holding_story_seed, market_context, market_context_seed, memory_surface, monitor_reason, operator_conclusion, reporter_evaluation_seed, reporter_feedback_packet, reporter_status, scanner_filters_seed, scanner_reason, shared_seed, shared_selection_trace, strategist_context, strategist_evidence, strategist_summary_seed, why_symbol_seed = fallback_report_seed(_build_shared_summary_seed=_build_shared_summary_seed, story_input=story_input, build_trade_report_memory_surface=build_trade_report_memory_surface, _as_dict=_as_dict, _extract_policy_ref_context=_extract_policy_ref_context, _extract_scanner_bias_summary=_extract_scanner_bias_summary, _enrich_market_context_for_fallback=_enrich_market_context_for_fallback, _fallback_section_seeds=_fallback_section_seeds, _enrich_scanner_reason_for_fallback=_enrich_scanner_reason_for_fallback, _clip=_clip, facade=_r3_sys.modules[__name__])
    monitor_snapshot = _build_report_monitor_snapshot(
        monitor_reason=monitor_reason,
        story_input=story_input,
        action=action,
        entry_execution_visibility=entry_execution_visibility,
    )
    entry_summary = story_input.get("entry_summary") if isinstance(story_input.get("entry_summary"), dict) else {}
    entry_monitor_reason = _resolve_entry_monitor_reason(story_input, monitor_reason, entry_summary)
    for key in (
        "entry_metrics",
        "entry_thresholds",
        "entry_condition_scores",
        "entry_grouped_logic_trace",
        "entry_condition_path",
        "entry_condition_paths_passed",
        "entry_reason",
    ):
        value = entry_monitor_reason.get(key)
        if value not in (None, "", [], {}) and monitor_snapshot.get(key) in (None, "", [], {}):
            monitor_snapshot[key] = value
    effective_scanner_selection_trace, exit_summary, holding_summary, improvement_points, lifecycle_summary, news_scanner_contribution, scanner_selection_trace, warnings = fb_summary_effective_scanner_selection_trace_exit_s(story_input=story_input, _listify=_listify, _as_dict=_as_dict, entry_summary=entry_summary, scanner_reason=scanner_reason, shared_selection_trace=shared_selection_trace, facade=_r3_sys.modules[__name__])
    if isinstance(effective_scanner_selection_trace.get("chart_feature_coverage"), dict):
        effective_scanner_selection_trace["chart_feature_coverage"] = _scanner_chart_feature_coverage(
            {"scanner_selection_trace": effective_scanner_selection_trace}
        )
    why_symbol_bullets = _build_scanner_choice_bullets(scanner_reason, market_context)
    why_symbol_bullets = _append_news_scanner_choice_details(why_symbol_bullets, news_scanner_contribution)
    raw_scanner_bullets = _listify(scanner_reason.get("bullets"), max_items=8, max_len=220)
    raw_scanner_bullets.extend(_listify(scanner_reason.get("why_selected"), max_items=4, max_len=180))
    selection_basis_text = _clip(scanner_reason.get("selection_basis"), max_len=220)
    if selection_basis_text:
        raw_scanner_bullets.append(f"Final decision basis: {selection_basis_text}")
    tie_break_text = _clip(scanner_reason.get("tie_break_rule"), max_len=220)
    if tie_break_text:
        raw_scanner_bullets.append(f"Tie-break rule: {tie_break_text}")
    runner_up_summaries = [
        f"Runner-ups lost because: {_clip((row or {}).get('symbol'), max_len=24)}: {_clip((row or {}).get('summary'), max_len=160)}"
        for row in list(scanner_reason.get("runner_ups_lost") or [])[:4]
        if isinstance(row, dict) and str((row or {}).get("symbol") or "").strip() and str((row or {}).get("summary") or "").strip()
    ]
    raw_scanner_bullets.extend(runner_up_summaries)
    for row in raw_scanner_bullets:
        if row and row not in why_symbol_bullets:
            why_symbol_bullets.append(row)

    confidence, executive_reason, lifecycle_summary_text, market_context_summary, scanner_choice_summary, status_text, strategist_summary, strategist_summary_summary, symbol, trade_id = fb_summary_confidence_executive_reason(_clip=_clip, shared_seed=shared_seed, story_input=story_input, operator_conclusion=operator_conclusion, lifecycle_summary=lifecycle_summary, _lifecycle_summary_conflicts_with_status=_lifecycle_summary_conflicts_with_status, execution_outcome=execution_outcome, scanner_reason=scanner_reason, _build_scanner_choice_summary=_build_scanner_choice_summary, market_context=market_context, _is_low_information_bullet=_is_low_information_bullet, has_runtime_scanner_reason=has_runtime_scanner_reason, scanner_selection_trace=scanner_selection_trace, why_symbol_seed=why_symbol_seed, _build_market_context_summary=_build_market_context_summary, has_runtime_market_context=has_runtime_market_context, market_context_seed=market_context_seed, _build_strategist_summary_section=_build_strategist_summary_section, facade=_r3_sys.modules[__name__])
    if (
        not has_runtime_market_context
        or not strategist_summary_summary
        or _is_low_information_bullet(strategist_summary_summary)
    ) and str(strategist_summary_seed.get("summary") or "").strip():
        strategist_summary["summary"] = _clip(strategist_summary_seed.get("summary"), max_len=600)
    if (not strategist_summary.get("bullets")) and isinstance(strategist_summary_seed.get("bullets"), list):
        strategist_summary["bullets"] = _listify(strategist_summary_seed.get("bullets"), max_items=10, max_len=260)
    entry_decision, exit_decision, holding_story, scanner_filters_bullets, scanner_filters_summary, strategist_refresh_trace, why_symbol_bullets = fb_sections_entry_decision_exit_decision(_build_report_strategist_refresh_trace=_build_report_strategist_refresh_trace, story_input=story_input, why_symbol_bullets=why_symbol_bullets, _listify=_listify, why_symbol_seed=why_symbol_seed, _build_scanner_filters_summary=_build_scanner_filters_summary, filters_human=filters_human, _build_scanner_filters_bullets=_build_scanner_filters_bullets, _clip=_clip, scanner_filters_seed=scanner_filters_seed, _build_entry_decision_bullets=_build_entry_decision_bullets, entry_summary=entry_summary, scanner_reason=scanner_reason, market_context=market_context, entry_monitor_reason=entry_monitor_reason, action=action, _build_entry_decision_summary=_build_entry_decision_summary, shared_seed=shared_seed, has_runtime_scanner_reason=has_runtime_scanner_reason, _is_low_information_bullet=_is_low_information_bullet, entry_decision_seed=entry_decision_seed, holding_summary=holding_summary, _build_holding_story_summary=_build_holding_story_summary, monitor_reason=monitor_reason, status_text=status_text, _build_holding_story_bullets=_build_holding_story_bullets, has_runtime_monitor_reason=has_runtime_monitor_reason, holding_story_seed=holding_story_seed, _holding_duration_label=_holding_duration_label, exit_summary=exit_summary, _build_exit_decision_bullets=_build_exit_decision_bullets, _build_exit_decision_summary=_build_exit_decision_summary, exit_decision_seed=exit_decision_seed, facade=_r3_sys.modules[__name__])
    if _clip(shared_seed.get("exit_reason"), max_len=240):
        exit_reason_label = _exit_reason_label(_clip(shared_seed.get("exit_reason"), max_len=240))
        exit_decision["bullets"] = [f"정규화된 청산 사유는 {exit_reason_label or _clip(shared_seed.get('exit_reason'), max_len=240)}입니다."] + list(
            exit_decision.get("bullets") or []
        )
    execution_quality = _build_execution_quality_section(
        story_input,
        execution_outcome,
        lifecycle_summary,
    )
    if execution_outcome_summary_is_placeholder(execution_quality_seed.get("summary")) and _clip(execution_quality.get("summary"), max_len=600):
        execution_quality_seed = dict(execution_quality_seed)
        execution_quality_seed["summary"] = _clip(execution_quality.get("summary"), max_len=600)
        if execution_quality.get("bullets"):
            execution_quality_seed["bullets"] = _listify(execution_quality.get("bullets"), max_items=12, max_len=260)
    if (
        not execution_outcome
        or not _clip(execution_quality.get("summary"), max_len=600)
        or _is_low_information_bullet(execution_quality.get("summary"))
    ) and str(execution_quality_seed.get("summary") or "").strip():
        execution_quality["summary"] = _clip(execution_quality_seed.get("summary"), max_len=600)
    if (not execution_quality.get("bullets")) and isinstance(execution_quality_seed.get("bullets"), list):
        execution_quality["bullets"] = _listify(execution_quality_seed.get("bullets"), max_items=12, max_len=260)
    reporter_eval = _build_reporter_evaluation_section(
        shared_seed,
        scanner_reason,
        monitor_reason,
        execution_outcome,
        reporter_status,
        reporter_feedback_packet,
    )
    if _reporter_summary_is_placeholder(reporter_eval.get("summary")) and _clip(reporter_evaluation_seed.get("summary"), max_len=600):
        reporter_eval["summary"] = _clip(reporter_evaluation_seed.get("summary"), max_len=600)
        if reporter_evaluation_seed.get("bullets"):
            reporter_eval["bullets"] = _listify(reporter_evaluation_seed.get("bullets"), max_items=12, max_len=260)
        if reporter_evaluation_seed.get("status"):
            reporter_eval["status"] = _clip(reporter_evaluation_seed.get("status"), max_len=48)
        if reporter_evaluation_seed.get("grade"):
            reporter_eval["grade"] = _clip(reporter_evaluation_seed.get("grade"), max_len=24)
    if (
        not reporter_status
        or not _clip(reporter_eval.get("summary"), max_len=600)
        or _is_low_information_bullet(reporter_eval.get("summary"))
    ) and str(reporter_evaluation_seed.get("summary") or "").strip():
        reporter_eval["summary"] = _clip(reporter_evaluation_seed.get("summary"), max_len=600)
    if (not reporter_eval.get("bullets")) and isinstance(reporter_evaluation_seed.get("bullets"), list):
        reporter_eval["bullets"] = _listify(reporter_evaluation_seed.get("bullets"), max_items=12, max_len=260)
    reporter_eval_status = _clip(reporter_eval.get("status"), max_len=48)
    if (
        not reporter_status
        or not reporter_eval_status
        or reporter_eval_status.lower() in {"missing", "not_captured", "unknown", "n/a"}
    ) and str(reporter_evaluation_seed.get("status") or "").strip():
        reporter_eval["status"] = _clip(reporter_evaluation_seed.get("status"), max_len=48)
    reporter_eval_grade = _clip(reporter_eval.get("grade"), max_len=24)
    if (
        not reporter_status
        or not reporter_eval_grade
        or reporter_eval_grade.lower() in {"missing", "not_captured", "unknown", "n/a"}
    ) and str(reporter_evaluation_seed.get("grade") or "").strip():
        reporter_eval["grade"] = _clip(reporter_evaluation_seed.get("grade"), max_len=24)
    weaknesses_bullets = warnings + [item for item in improvement_points if item not in warnings]
    full_timeline = [
        row
        for row in list(story_input.get("timeline") or [])
        if isinstance(row, dict)
    ][:24]

    out = fb_sections_out(trade_id=trade_id, symbol=symbol, action=action, status_text=status_text, strategist_summary=strategist_summary, strategist_refresh_trace=strategist_refresh_trace, entry_execution_visibility=entry_execution_visibility, entry_decision=entry_decision, exit_decision=exit_decision, execution_quality=execution_quality, reporter_eval=reporter_eval, full_timeline=full_timeline, _utc_now_iso=_utc_now_iso, _clip=_clip, status=status, mode=mode, executive_reason=executive_reason, market_context_summary=market_context_summary, effective_scanner_selection_trace=effective_scanner_selection_trace, news_scanner_contribution=news_scanner_contribution, holding_story=holding_story, monitor_snapshot=monitor_snapshot, scanner_filters_summary=scanner_filters_summary, scanner_filters_bullets=scanner_filters_bullets, weaknesses_bullets=weaknesses_bullets, _build_report_shared_facts=_build_report_shared_facts, model=model, reason=reason, confidence=confidence, _build_market_context_bullets=_build_market_context_bullets, market_context=market_context, _listify=_listify, _compact_scalar_dict=_compact_scalar_dict, _as_dict=_as_dict, _build_market_scanner_linkage_bullet=_build_market_scanner_linkage_bullet, scanner_reason=scanner_reason, why_symbol_bullets=why_symbol_bullets, _scanner_basis_text=_scanner_basis_text, shared_seed=shared_seed, story_input=story_input, scanner_choice_summary=scanner_choice_summary, lifecycle_summary_text=lifecycle_summary_text, strategist_context=strategist_context, strategist_evidence=strategist_evidence, guard_reason=guard_reason, guard_approval_seed=guard_approval_seed, operator_conclusion=operator_conclusion, final_operator_conclusion_seed=final_operator_conclusion_seed, build_trade_report_truth_surface=build_trade_report_truth_surface, memory_surface=memory_surface, build_trade_memory_application_surface=build_trade_memory_application_surface, _compact_strategist_report_context=_compact_strategist_report_context, facade=_r3_sys.modules[__name__])[0]
    post_exit_shadow = _story_post_exit_shadow(story_input)
    if post_exit_shadow:
        out["post_exit_shadow"] = dict(post_exit_shadow)
    return _attach_backward_compatible_aliases(out)



