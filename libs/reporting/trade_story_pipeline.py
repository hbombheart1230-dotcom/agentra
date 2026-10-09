from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Mapping

from libs.reporting.reasoning_trace import (
    build_reasoning_provenance,
    build_reasoning_trace_from_summaries,
    normalize_reasoning_provenance_aliases,
    normalize_reasoning_trace_aliases,
)
from libs.reporting.strategy_read_model import (
    build_news_symbol_linkage_view,
    build_strategist_feedback_input_view,
)
from libs.reporting.trade_read_model import normalize_trade_report_section
from libs.reporting.trade_report_ai import resolve_shared_trade_facts
from libs.reporting.trade_story_facade_parts.strategist_evidence import (
    _raw_strategist_evidence_impl, _strategist_trace_source_impl,
    _build_strategist_evidence_trace_impl,
)
from libs.reporting.trade_story_facade_parts.filter_checklist import build_filters_human_impl
from libs.reporting.trade_story_facade_parts.story_contracts import (
    slug_impl,
    feature_coverage_impl,
    normalized_feature_coverage_impl,
    confidence_label_impl,
    execution_mode_label_impl,
    classify_story_type_impl,
    build_story_id_impl,
    build_story_contract_impl,
)
from libs.reporting.trade_story_facade_parts.human_judgments import (
    build_guard_reason_human_impl, build_reporter_status_human_impl,
    build_operator_conclusion_human_impl,
)
from libs.reporting.trade_report_common import (
    clip_text as clip,
    format_exit_label,
    format_pct,
    format_ratio_pct,
    is_empty_placeholder as _is_empty_placeholder,
    list_text as _list_text,
    merge_missing_values as _merge_missing_values,
    safe_float,
    safe_int,
    utc_now_iso,
)
from libs.reporting.trade_scanner_fallback_anchor import (
    reanchor_scanner_selection_for_monitor_fallback,
)
from libs.reporting.trade_fallback_text import (
    EXECUTION_OUTCOME_NOT_CAPTURED,
    LIFECYCLE_CONCLUSION_NOT_CAPTURED,
    REPORTER_LINKAGE_NOT_CAPTURED,
    lifecycle_conclusion_summary_is_placeholder,
)
from libs.reporting.trade_execution_outcome_text import (
    build_execution_outcome_fallback_from_lifecycle,
    execution_outcome_summary_is_placeholder,
)
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human
from libs.reporting.trade_story_evidence import (
    derive_evidence_provenance as _derive_evidence_provenance_impl,
    has_substantive_exit_evidence as _has_substantive_exit_evidence_impl,
    set_or_replace_placeholder as _set_or_replace_placeholder_impl,
)
from libs.reporting.trade_story_pipeline_evidence_hydration import (
    enrich_scanner_reason_from_evidence as _enrich_scanner_reason_from_evidence_impl,
    enrich_filters_from_evidence as _enrich_filters_from_evidence_impl,
    hydrate_canonical_agent_artifacts as _hydrate_canonical_agent_artifacts_impl,
    resolve_selection_monitor_artifact as _resolve_selection_monitor_artifact_impl,
    safe_read_json_file as _safe_read_json_file_impl,
)
from libs.reporting.trade_story_pipeline_human_payloads import (
    build_scanner_reason_human as _build_scanner_reason_human_impl,
    build_monitor_reason_human as _build_monitor_reason_human_impl,
    build_market_context_human as _build_market_context_human_impl,
    build_execution_outcome_human as _build_execution_outcome_human_impl,
    build_monitor_blocker_trace as _build_monitor_blocker_trace_impl,
    build_monitor_stop_policy_trace as _build_monitor_stop_policy_trace_impl,
    normalize_stop_thresholds as _normalize_stop_thresholds_impl,
    resolve_adaptive_stop_loss_pct as _resolve_adaptive_stop_loss_pct_impl,
    resolve_strategist_adaptive_exit as _resolve_strategist_adaptive_exit_impl,
)
from libs.reporting.trade_story_pipeline_story_assembly import (
    build_trade_story_input as _build_trade_story_input_impl,
    build_report_section_seeds as _build_report_section_seeds_impl,
    build_lifecycle_bundle as _build_lifecycle_bundle_impl,
    build_timeline as _build_timeline_impl,
    collect_story_warnings as _collect_story_warnings_impl,
    compact_canonical_monitor as _compact_canonical_monitor_impl,
    normalize_trade_lifecycle_for_story_input as _normalize_trade_lifecycle_for_story_input_impl,
)
from libs.core.symbols import normalize_symbol
from libs.reporting.trade_story_pipeline_news import (
    _headline_text,
    _clean_news_fragment,
    _news_item_field,
    _news_sample_parts,
    _norm_symbol_text,
    _symbol_name_from_text,
    _sample_title_directly_matches_symbol,
    _format_symbol_news_headline,
    _collect_symbol_headlines_from_ranked_rows,
    _headline_matches_symbol,
    _collect_top_headlines,
    _title_prefixed_symbol,
    _list_text_for_symbol,
    _optional_float,
    _build_news_scanner_contribution_trace,
    _attach_news_scanner_contribution,
)
from libs.reporting.trade_story_pipeline_scanner import (
    _korea_indices_bullet,
    _top_numeric_drivers,
    _scanner_chart_fit_payload,
    _scanner_macro_chart_fit_payload,
    _candidate_sources_from_score_breakdown,
    _selection_basis_from_scores,
    _scanner_candidate_row_from_evidence,
    _build_scanner_selection_trace,
    _scanner_chart_fit_from_scanner_evidence,
    _scanner_macro_chart_fit_from_scanner_evidence,
    _normalized_feature_coverage_from_scanner_evidence,
)
from libs.reporting.trade_story_pipeline_provenance import (
    _source_confidence_label,
    _is_present,
    compute_evidence_completeness,
    _safe_path_text,
    _safe_ref_map,
    _resolve_commander_source_ref,
    _commander_reasoning_flag,
    _commander_reasoning_source_priority,
    build_commander_evidence,
    _section_source_entry,
    build_section_provenance,
    _section_seed_provenance_entry,
    build_report_section_provenance_seeds,
)


def _has_substantive_exit_evidence(exit_payload: Any) -> bool:
    return _has_substantive_exit_evidence_impl(exit_payload)


def _set_or_replace_placeholder(target: Dict[str, Any], key: str, value: Any) -> None:
    _set_or_replace_placeholder_impl(target, key, value)


def _derive_evidence_provenance(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    return _derive_evidence_provenance_impl(bundle_out)


def _safe_read_json_file(path_value: Any) -> Dict[str, Any]:
    return _safe_read_json_file_impl(path_value)


def _hydrate_canonical_agent_artifacts(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
) -> Dict[str, Any]:
    return _hydrate_canonical_agent_artifacts_impl(
        bundle_out,
        canonical_agent_artifacts,
        read_json_file=_safe_read_json_file,
    )


def _resolve_selection_monitor_artifact(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
) -> Dict[str, Any]:
    return _resolve_selection_monitor_artifact_impl(
        bundle_out,
        canonical_agent_artifacts,
        read_json_file=_safe_read_json_file,
    )


def _raw_strategist_evidence(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    return _raw_strategist_evidence_impl(bundle_out)


def _strategist_trace_source(
    canonical_strategist: Dict[str, Any],
    raw_strategist_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    return _strategist_trace_source_impl(canonical_strategist, raw_strategist_evidence)


def _build_strategist_evidence_trace(
    strategist: Dict[str, Any],
    *,
    selected_symbol: str = "",
    fallback_market_titles: Any = None,
    fallback_candidate_titles: Any = None,
) -> Dict[str, Any]:
    return _build_strategist_evidence_trace_impl(
        strategist, selected_symbol=selected_symbol,
        fallback_market_titles=fallback_market_titles,
        fallback_candidate_titles=fallback_candidate_titles,
        list_text=_list_text, collect_top_headlines=_collect_top_headlines,
        collect_symbol_headlines_from_ranked_rows=_collect_symbol_headlines_from_ranked_rows,
        list_text_for_symbol=_list_text_for_symbol,
    )


def _normalize_stop_thresholds(thresholds: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_stop_thresholds_impl(thresholds)


def _resolve_strategist_adaptive_exit(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_strategist_adaptive_exit_impl(monitor)


def _resolve_adaptive_stop_loss_pct(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Any:
    return _resolve_adaptive_stop_loss_pct_impl(monitor, thresholds)


def _build_monitor_stop_policy_trace(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_stop_policy_trace_impl(monitor, thresholds)


def _build_monitor_blocker_trace(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_blocker_trace_impl(monitor)


def _story_assembly_deps() -> Dict[str, Any]:
    return {
        "EXECUTION_OUTCOME_NOT_CAPTURED": EXECUTION_OUTCOME_NOT_CAPTURED,
        "LIFECYCLE_CONCLUSION_NOT_CAPTURED": LIFECYCLE_CONCLUSION_NOT_CAPTURED,
        "REPORTER_LINKAGE_NOT_CAPTURED": REPORTER_LINKAGE_NOT_CAPTURED,
        "_attach_news_scanner_contribution": _attach_news_scanner_contribution,
        "_build_monitor_blocker_trace": _build_monitor_blocker_trace,
        "_build_monitor_stop_policy_trace": _build_monitor_stop_policy_trace,
        "_build_scanner_selection_trace": _build_scanner_selection_trace,
        "_build_strategist_evidence_trace": _build_strategist_evidence_trace,
        "_commander_reasoning_flag": _commander_reasoning_flag,
        "_commander_reasoning_source_priority": _commander_reasoning_source_priority,
        "_compact_canonical_monitor": _compact_canonical_monitor,
        "_derive_evidence_provenance": _derive_evidence_provenance,
        "_has_substantive_exit_evidence": _has_substantive_exit_evidence,
        "_hydrate_canonical_agent_artifacts": _hydrate_canonical_agent_artifacts,
        "_is_empty_placeholder": _is_empty_placeholder,
        "_list_text": _list_text,
        "_raw_strategist_evidence": _raw_strategist_evidence,
        "_resolve_commander_source_ref": _resolve_commander_source_ref,
        "_resolve_selection_monitor_artifact": _resolve_selection_monitor_artifact,
        "_safe_ref_map": _safe_ref_map,
        "_set_or_replace_placeholder": _set_or_replace_placeholder,
        "_strategist_trace_source": _strategist_trace_source,
        "build_execution_outcome_fallback_from_lifecycle": build_execution_outcome_fallback_from_lifecycle,
        "build_news_symbol_linkage_view": build_news_symbol_linkage_view,
        "build_operator_conclusion_human": build_operator_conclusion_human,
        "build_reasoning_provenance": build_reasoning_provenance,
        "build_reasoning_trace_from_summaries": build_reasoning_trace_from_summaries,
        "build_report_section_provenance_seeds": build_report_section_provenance_seeds,
        "build_report_section_seeds": build_report_section_seeds,
        "build_section_provenance": build_section_provenance,
        "build_strategist_feedback_input_view": build_strategist_feedback_input_view,
        "compute_evidence_completeness": compute_evidence_completeness,
        "enrich_filters_from_evidence": enrich_filters_from_evidence,
        "enrich_scanner_reason_from_evidence": enrich_scanner_reason_from_evidence,
        "execution_outcome_summary_is_placeholder": execution_outcome_summary_is_placeholder,
        "lifecycle_conclusion_summary_is_placeholder": lifecycle_conclusion_summary_is_placeholder,
        "normalize_reasoning_provenance_aliases": normalize_reasoning_provenance_aliases,
        "normalize_reasoning_trace_aliases": normalize_reasoning_trace_aliases,
        "normalize_reporter_status_human": normalize_reporter_status_human,
        "normalize_trade_report_section": normalize_trade_report_section,
        "reanchor_scanner_selection_for_monitor_fallback": reanchor_scanner_selection_for_monitor_fallback,
        "resolve_shared_trade_facts": resolve_shared_trade_facts,
    }

def build_lifecycle_bundle(
    *,
    day: str,
    trade_id: str,
    run_id: str,
    symbol: str,
    lifecycle: Dict[str, Any],
    strategist_summary: Dict[str, Any],
    scanner_summary: Dict[str, Any],
    monitor_summary: Dict[str, Any],
    commander_summary: Dict[str, Any],
    story_input: Dict[str, Any],
    diagnostics: Dict[str, Any],
    canonical_refs: Dict[str, Any],
    llm_refs: Dict[str, Any],
    artifact_links: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_lifecycle_bundle_impl(
        day=day, trade_id=trade_id, run_id=run_id, symbol=symbol,
        lifecycle=lifecycle, strategist_summary=strategist_summary,
        scanner_summary=scanner_summary, monitor_summary=monitor_summary,
        commander_summary=commander_summary, story_input=story_input,
        diagnostics=diagnostics, canonical_refs=canonical_refs,
        llm_refs=llm_refs, artifact_links=artifact_links,
        deps=_story_assembly_deps(),
    )

def build_report_section_seeds(
    *,
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any] | None = None,
    execution_outcome_human: Dict[str, Any] | None = None,
    guard_reason_human: Dict[str, Any] | None = None,
    reporter_status_human: Dict[str, Any] | None = None,
    operator_conclusion_human: Dict[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    return _build_report_section_seeds_impl(
        market_context_human=market_context_human,
        scanner_reason_human=scanner_reason_human,
        filters_human=filters_human,
        monitor_reason_human=monitor_reason_human,
        execution_outcome_human=execution_outcome_human,
        guard_reason_human=guard_reason_human,
        reporter_status_human=reporter_status_human,
        operator_conclusion_human=operator_conclusion_human,
        deps=_story_assembly_deps(),
    )

def slug(value: Any, *, max_len: int = 80) -> str:
    return slug_impl(value, max_len=max_len, re=re)


def feature_coverage(selected_candidate: Dict[str, Any]) -> Dict[str, Any]:
    return feature_coverage_impl(selected_candidate)


def normalized_feature_coverage(scanner: Dict[str, Any], selected_candidate: Dict[str, Any]) -> Dict[str, Any]:
    return normalized_feature_coverage_impl(scanner, selected_candidate, feature_coverage=feature_coverage, safe_int=safe_int, safe_float=safe_float)


def confidence_label(value: Any) -> str:
    return confidence_label_impl(value, safe_float=safe_float)


def execution_mode_label(executor: Dict[str, Any]) -> str:
    return execution_mode_label_impl(executor)


def classify_story_type(execution: Dict[str, Any], executor: Dict[str, Any]) -> str:
    return classify_story_type_impl(execution, executor)


def build_story_id(day: str, execution: Dict[str, Any]) -> str:
    return build_story_id_impl(day, execution, slug=slug)


def build_story_contract(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    return build_story_contract_impl(bundle_out, classify_story_type=classify_story_type, execution_mode_label=execution_mode_label)


def _human_payload_deps() -> Dict[str, Any]:
    return {
        "build_strategist_evidence_trace": _build_strategist_evidence_trace,
        "korea_indices_bullet": _korea_indices_bullet,
        "list_text": _list_text,
        "format_pct": format_pct,
        "safe_float": safe_float,
        "safe_int": safe_int,
        "build_news_scanner_contribution_trace": _build_news_scanner_contribution_trace,
        "build_scanner_selection_trace": _build_scanner_selection_trace,
        "scanner_chart_fit_payload": _scanner_chart_fit_payload,
        "scanner_macro_chart_fit_payload": _scanner_macro_chart_fit_payload,
        "clip": clip,
        "confidence_label": confidence_label,
        "normalized_feature_coverage": normalized_feature_coverage,
        "build_monitor_blocker_trace": _build_monitor_blocker_trace,
        "build_monitor_stop_policy_trace": _build_monitor_stop_policy_trace,
        "merge_missing_values": _merge_missing_values,
        "format_exit_label": format_exit_label,
        "format_ratio_pct": format_ratio_pct,
    }

def build_market_context_human(strategist: Dict[str, Any]) -> Dict[str, Any]:
    return _build_market_context_human_impl(strategist, deps=_human_payload_deps())

def build_scanner_reason_human(scanner: Dict[str, Any], strategist: Dict[str, Any]) -> Dict[str, Any]:
    return _build_scanner_reason_human_impl(scanner, strategist, deps=_human_payload_deps())

def _evidence_enrichment_deps() -> Dict[str, Any]:
    return {
        "normalized_feature_coverage_from_scanner_evidence": _normalized_feature_coverage_from_scanner_evidence,
        "scanner_candidate_row_from_evidence": _scanner_candidate_row_from_evidence,
        "scanner_chart_fit_from_scanner_evidence": _scanner_chart_fit_from_scanner_evidence,
        "scanner_macro_chart_fit_from_scanner_evidence": _scanner_macro_chart_fit_from_scanner_evidence,
        "selection_basis_from_scores": _selection_basis_from_scores,
        "top_numeric_drivers": _top_numeric_drivers,
    }

def enrich_scanner_reason_from_evidence(
    scanner_reason_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    return _enrich_scanner_reason_from_evidence_impl(scanner_reason_human, scanner_evidence, deps=_evidence_enrichment_deps())

def enrich_filters_from_evidence(
    filters_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
    *,
    selected_symbol: str,
    monitor_evidence: Optional[Dict[str, Any]] = None,
    entry_execution_details: Optional[Dict[str, Any]] = None,
    exit_execution_details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _enrich_filters_from_evidence_impl(
        filters_human,
        scanner_evidence,
        selected_symbol=selected_symbol,
        monitor_evidence=monitor_evidence,
        entry_execution_details=entry_execution_details,
        exit_execution_details=exit_execution_details,
        deps=_evidence_enrichment_deps(),
    )

def build_filters_human(scanner: Dict[str, Any], strategist: Dict[str, Any], supervisor: Dict[str, Any]) -> Dict[str, Any]:
    return build_filters_human_impl(
        scanner, strategist, supervisor,
        normalized_feature_coverage=normalized_feature_coverage, safe_float=safe_float,
    )


def build_monitor_reason_human(monitor: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_reason_human_impl(monitor, execution, deps=_human_payload_deps())

def build_guard_reason_human(supervisor: Dict[str, Any]) -> Dict[str, Any]:
    return build_guard_reason_human_impl(supervisor)


def build_execution_outcome_human(
    execution: Dict[str, Any],
    executor: Dict[str, Any],
    *,
    story_type: str,
    mode_label: str,
) -> Dict[str, Any]:
    return _build_execution_outcome_human_impl(
        execution,
        executor,
        story_type=story_type,
        mode_label=mode_label,
    )


def build_reporter_status_human(reporter: Dict[str, Any], reporter_day_obj: Dict[str, Any]) -> Dict[str, Any]:
    return build_reporter_status_human_impl(
        reporter, reporter_day_obj,
        normalize_reporter_status_human=normalize_reporter_status_human,
    )


def build_operator_conclusion_human(
    *,
    execution: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
) -> Dict[str, Any]:
    return build_operator_conclusion_human_impl(
        execution=execution,
        scanner_reason_human=scanner_reason_human,
        filters_human=filters_human,
        monitor_reason_human=monitor_reason_human,
        execution_outcome_human=execution_outcome_human,
        reporter_status_human=reporter_status_human,
    )


def build_timeline(
    *,
    commander: Dict[str, Any],
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    guard_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return _build_timeline_impl(
        commander=commander,
        market_context_human=market_context_human,
        scanner_reason_human=scanner_reason_human,
        monitor_reason_human=monitor_reason_human,
        guard_reason_human=guard_reason_human,
        execution_outcome_human=execution_outcome_human,
        reporter_status_human=reporter_status_human,
        execution=execution,
    )


def collect_story_warnings(
    *,
    story_contract: Dict[str, Any],
    market_context_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
) -> List[str]:
    return _collect_story_warnings_impl(
        story_contract=story_contract,
        market_context_human=market_context_human,
        filters_human=filters_human,
        reporter_status_human=reporter_status_human,
        execution_outcome_human=execution_outcome_human,
    )


def _normalize_trade_lifecycle_for_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    existing_story_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _normalize_trade_lifecycle_for_story_input_impl(
        bundle_out,
        trade_lifecycle=trade_lifecycle,
        existing_story_input=existing_story_input,
    )


def build_trade_story_input_from_bundle(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    existing_story_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_lifecycle = _normalize_trade_lifecycle_for_story_input(
        bundle_out,
        trade_lifecycle=trade_lifecycle,
        existing_story_input=existing_story_input,
    )
    story_input = build_trade_story_input(
        bundle_out,
        trade_lifecycle=normalized_lifecycle if normalized_lifecycle else trade_lifecycle,
    )
    existing = existing_story_input if isinstance(existing_story_input, dict) else {}
    for key in (
        "report_runtime_mode",
        "skip_separated_report_llm",
        "entry_strategist_run_id",
        "strategy_anchor_run_id",
    ):
        if key not in story_input and key in existing:
            story_input[key] = existing.get(key)
    for key in ("trade_id", "day", "run_id"):
        if story_input.get(key) in (None, "", [], {}) and existing.get(key) not in (None, "", [], {}):
            story_input[key] = existing.get(key)
    return story_input


def _compact_canonical_monitor(canonical_monitor: Dict[str, Any] | None) -> Dict[str, Any]:
    return _compact_canonical_monitor_impl(canonical_monitor)


def build_trade_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _build_trade_story_input_impl(bundle_out, trade_lifecycle=trade_lifecycle, deps=_story_assembly_deps())

def render_bundle_markdown(out: Dict[str, Any]) -> str:
    story_contract = out.get("story_contract") if isinstance(out.get("story_contract"), dict) else {}
    lines: List[str] = []
    lines.append(f"# Aggregated Execution Bundle ({out.get('run_id')})")
    lines.append("")
    lines.append(f"- day: **{out.get('day')}**")
    lines.append(f"- story_anchor: **{story_contract.get('story_anchor') or '-'}**")
    lines.append(f"- story_type: **{story_contract.get('story_type') or '-'}**")
    lines.append(f"- execution_mode: **{story_contract.get('execution_mode_label') or '-'}**")
    lines.append("")
    sections = [
        ("Market Context", out.get("market_context_human")),
        ("Why This Symbol", out.get("scanner_reason_human")),
        ("Filters / Gates", out.get("filters_human")),
        ("Monitor / Trigger Reasoning", out.get("monitor_reason_human")),
        ("Guard / Approval", out.get("guard_reason_human")),
        ("Execution Outcome", out.get("execution_outcome_human")),
        ("Reporter Status", out.get("reporter_status_human")),
        ("Operator Conclusion", out.get("operator_conclusion_human")),
    ]
    for title, section in sections:
        data = section if isinstance(section, dict) else {}
        lines.append(f"## {title}")
        lines.append("")
        if data.get("summary"):
            lines.append(str(data.get("summary")))
            lines.append("")
        for bullet in list(data.get("bullets") or [])[:8]:
            lines.append(f"- {bullet}")
        lines.append("")
    lines.append("## Timeline")
    lines.append("")
    for row in list(out.get("timeline") or [])[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(f"- {row.get('step')}: {row.get('summary') or '-'}")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    for key, value in dict(out.get("artifacts") or {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def render_summary_markdown(out: Dict[str, Any]) -> str:
    bundles = out.get("bundles") if isinstance(out.get("bundles"), list) else []
    lines: List[str] = []
    lines.append(f"# Live Execution Bundles ({out.get('day')})")
    lines.append("")
    lines.append(f"- bundle_count: **{out.get('bundle_count')}**")
    lines.append(f"- canonical_trades_root: `{out.get('canonical_trades_root')}`")
    lines.append("")
    if not bundles:
        lines.append("No executed BUY/SELL runs were found for the selected day.")
        lines.append("")
        return "\n".join(lines)
    lines.append("## Bundles")
    lines.append("")
    for row in bundles:
        lines.append(
            f"- `{row.get('run_id')}` {row.get('action')} {row.get('symbol')} x{row.get('qty')} "
            f"story=`{row.get('story_type')}` report=`{row.get('trade_report_json_path')}`"
        )
    lines.append("")
    return "\n".join(lines)
