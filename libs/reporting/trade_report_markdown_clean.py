from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from libs.reporting.trade_report.markdown_clean_parts.news_headlines import (
    _strip_html_tags_impl,
    _clean_news_title_impl,
    _sample_news_titles_impl,
    _normalize_news_symbol_impl,
    _news_symbol_from_item_impl,
    _sample_news_titles_for_symbol_impl,
    _mismatched_symbol_news_bullet_impl,
    _news_linkage_strength_label_impl,
)
from libs.reporting.trade_report.markdown_clean_parts.operator_labels import (
    _rank_scope_text_impl,
    _watch_scope_label_impl,
    _candidate_watch_reason_label_impl,
    _story_type_label_impl,
    _execution_mode_label_impl,
    _action_label_impl,
    _status_label_impl,
    _axis_label_impl,
    _risk_mode_label_impl,
    _theme_label_impl,
    _policy_token_label_impl,
    _playbook_label_impl,
    _monitor_guidance_label_impl,
    _scanner_bias_label_impl,
    _policy_source_label_impl,
    _failure_label_impl,
    _reporter_source_label_impl,
    _humanize_reporter_source_label_impl,
)
from libs.reporting.trade_report.markdown_clean_parts.strategist_language import (
    _operatorize_strategist_output_text_impl,
    _strategy_output_text_impl,
    _strategy_output_list_text_impl,
)
from libs.reporting.trade_report.markdown_clean_parts.summary_language import (
    _summary_problem_label_impl,
    _summary_root_cause_label_impl,
    _summary_fact_text_impl,
    _summary_eval_sentence_impl,
    _section_impl,
    _strip_trailing_blanks_impl,
    _is_post_entry_gate_text_impl,
    _normalize_evaluation_hold_duration_impl,
)
from libs.reporting.trade_report_markdown_truth import (
    build_truth_surface as _build_truth_surface_impl,
    boolish as _boolish_impl,
    build_trade_cost_analysis as _build_trade_cost_analysis_impl,
    extract_trade_quantity as _extract_trade_quantity_impl,
    first_present as _first_present_impl,
    get_truth_surface as _get_truth_surface_impl,
    infer_trade_quantity_from_costs as _infer_trade_quantity_from_costs_impl,
    operator_pnl_pct as _operator_pnl_pct_impl,
    pnl_basis_label as _pnl_basis_label_impl,
    trade_cost_analysis_lines as _trade_cost_analysis_lines_impl,
    truth_source_label as _truth_source_label_impl,
)
from libs.reporting.trade_report_markdown_scanner import (
    build_scanner_comparison as _build_scanner_comparison_impl,
    build_symbol_selection as _build_symbol_selection_impl,
    is_redundant_symbol_selection_line as _is_redundant_symbol_selection_line_impl,
    is_scanner_execution_mismatch_line as _is_scanner_execution_mismatch_line_impl,
    is_scanner_selection_label_line as _is_scanner_selection_label_line_impl,
)
from libs.reporting.trade_report_markdown_monitor import (
    build_exit_decision as _build_exit_decision_impl,
    build_holding_story as _build_holding_story_impl,
    build_monitor_snapshot as _build_monitor_snapshot_impl,
    closed_trade_monitor_preface as _closed_trade_monitor_preface_impl,
    normalize_monitor_story_line as _normalize_monitor_story_line_impl,
    parse_monitor_bullet as _parse_monitor_bullet_impl,
    price_source_label as _price_source_label_impl,
    price_source_policy_label as _price_source_policy_label_impl,
)
from libs.reporting.trade_report_markdown_strategy_memory import (
    carryover_context as _carryover_context_impl,
    build_prompt_proven_memory as _build_prompt_proven_memory_impl,
    build_memory_application as _build_memory_application_impl,
    build_strategy_horizon_lines as _build_strategy_horizon_lines_impl,
    duration_label_compact as _duration_label_compact_impl,
    hold_window_label as _hold_window_label_impl,
    strategy_horizon_alignment_label as _strategy_horizon_alignment_label_impl,
    strategy_horizon_label as _strategy_horizon_label_impl,
    strategy_horizon_reason_label as _strategy_horizon_reason_label_impl,
    strategy_horizon_report_surface as _strategy_horizon_report_surface_impl,
)
from libs.reporting.trade_report_symbol_metadata import (
    append_theme_values as _append_theme_values_impl,
    append_unique_text as _append_unique_text_impl,
    component_themes_for_symbol as _component_themes_for_symbol_impl,
    infer_symbol_name_from_report_text as _infer_symbol_name_from_report_text_impl,
    iter_nested_dicts as _iter_nested_dicts_impl,
    iter_trade_symbol_metadata_sources as _iter_trade_symbol_metadata_sources_impl,
    looks_like_symbol_name as _looks_like_symbol_name_impl,
    resolve_trade_symbol_metadata as _resolve_trade_symbol_metadata_impl,
    symbol_in_theme_components as _symbol_in_theme_components_impl,
)
from libs.reporting.trade_report_post_exit_shadow import (
    build_post_exit_shadow_summary_lines as _build_post_exit_shadow_summary_lines_impl,
    checkpoint_label as _checkpoint_label_impl,
    compact_post_exit_shadow as _compact_post_exit_shadow_impl,
    post_exit_shadow_surface as _post_exit_shadow_surface_impl,
)
from libs.reporting.quant_tactic_report import (
    quant_tactic_surface as _quant_tactic_surface_impl,
    render_quant_tactic_report_lines as _render_quant_tactic_report_lines_impl,
)
from libs.reporting.strategist_quant_context_report import (
    render_strategist_quant_context_usage_lines as _render_strategist_quant_context_usage_lines_impl,
)
from libs.reporting.controlled_mock_lane_report import (
    render_controlled_lane_report_lines as _render_controlled_lane_report_lines,
)
from libs.reporting.trade_report.markdown_summary import (
    build_trade_summary_input as _build_trade_summary_input_impl,
    render_trade_summary_markdown as _render_trade_summary_markdown_impl,
)
from libs.reporting.trade_report.markdown_diagnostics import (
    build_summary_deterministic_diagnostics_section as _build_summary_deterministic_diagnostics_section_impl,
    build_summary_llm_evaluation_section as _build_summary_llm_evaluation_section_impl,
    same_day_summary_from_texts as _same_day_summary_from_texts_impl,
)
from libs.reporting.trade_report.markdown_signals import (
    resolve_entry_execution_visibility as _resolve_entry_execution_visibility_impl,
    build_summary_exit_trigger_lines as _build_summary_exit_trigger_lines_impl,
    enrich_exit_signal_snapshot_from_monitor as _enrich_exit_signal_snapshot_from_monitor_impl,
    entry_signal_metric_summary_lines as _entry_signal_metric_summary_lines_impl,
    entry_watch_execution_lines as _entry_watch_execution_lines_impl,
    entry_watch_summary_lines as _entry_watch_summary_lines_impl,
    resolve_entry_signal_snapshot as _resolve_entry_signal_snapshot_impl,
)
from libs.reporting.trade_report.markdown_translation import (
    translate_text as _translate_text_impl,
)
from libs.reporting.trade_report.markdown_strategy import (
    build_market_context as _build_market_context_impl,
    build_strategist_output_surface as _build_strategist_output_surface_impl,
    build_strategist_summary as _build_strategist_summary_impl,
)
import sys as _r3_sys
from libs.reporting.trade_report.markdown_clean_r3_parts.bodies_01 import (
    _same_day_current_result_r3_impl,
    render_trade_report_markdown_clean_r3_impl,
    render_trade_summary_markdown_with_evaluation_clean_r3_impl,
    _is_recovered_partial_exit_report_r3_impl,
    _authoritative_hold_duration_seconds_r3_impl,
    _authoritative_final_operator_summary_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_r3_parts.bodies_02 import (
    _selection_fallback_context_r3_impl,
    _candidate_cascade_symbols_r3_impl,
    _resolve_market_context_r3_impl,
    _korea_index_lines_r3_impl,
    _normalize_exit_trigger_label_r3_impl,
    _extract_exit_signal_snapshot_r3_impl,
    _metadata_value_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_r3_parts.bodies_03 import (
    _reason_tag_summary_r3_impl,
    _resolve_prompt_proven_surface_r3_impl,
    _build_reconstructed_trade_memory_r3_impl,
    _market_context_structured_lines_r3_impl,
    _resolve_strategist_output_surface_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_r3_parts.bodies_04 import (
    _build_strategist_refresh_trace_r3_impl,
    _build_execution_quality_r3_impl,
    _humanize_reporter_pattern_r3_impl,
    _build_reporter_evaluation_r3_impl,
    _build_weaknesses_r3_impl,
    _build_provenance_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_r3_parts.bodies_05 import (
    _build_final_conclusion_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_dependency_maps import (
    _markdown_diagnostics_deps_r3_impl,
    _summary_render_deps_r3_impl,
    _summary_input_deps_r3_impl,
    _strategy_memory_deps_r3_impl,
    _markdown_entry_visibility_deps_r3_impl,
    _markdown_signal_deps_r3_impl,
    _markdown_translation_deps_r3_impl,
    _markdown_truth_surface_deps_r3_impl,
    _markdown_strategy_deps_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_operator_narrative import (
    _translate_watch_item_r3_impl,
    _translate_reason_phrase_r3_impl,
    _translate_invalidation_item_r3_impl,
    _humanize_reporter_recommendation_r3_impl,
    _bullet_lines_r3_impl,
    _section_summary_r3_impl,
    _build_entry_decision_r3_impl,
    _build_guard_approval_r3_impl,
    _build_timeline_r3_impl,
    _extract_metadata_from_texts_r3_impl,
    _monitor_delta_interpretation_r3_impl,
    _entry_reason_line_r3_impl,
    _entry_confidence_line_r3_impl,
    _normalize_entry_confidence_for_operator_summary_r3_impl,
    _correct_final_operator_summary_r3_impl,
    _reason_summary_line_r3_impl,
    _ensure_sentence_r3_impl,
    _noun_predicate_was_r3_impl,
    _first_nonempty_r3_impl,
    _market_context_summary_from_raw_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_parts.report_paths_and_time import (
    _get_report_path_r3_impl,
    _parse_report_datetime_r3_impl,
    _duration_label_seconds_r3_impl,
    _carry_state_label_r3_impl,
    _carry_risk_label_r3_impl,
    _strategy_horizon_report_surface_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_parts.memory_policy_phases import (
    _memory_layer_label_r3_impl,
    _memory_status_label_r3_impl,
    _memory_layers_text_r3_impl,
    _memory_packet_state_line_r3_impl,
    _policy_phase_line_r3_impl,
    _same_policy_snapshot_r3_impl,
    _scanner_phase_line_r3_impl,
    _monitor_phase_line_r3_impl,
    _resolve_reconstructed_memory_surface_r3_impl,
    _build_generation_info_r3_impl,
    _is_closed_trade_context_r3_impl,
    _strategy_output_layer_bits_r3_impl,
)
from libs.reporting.trade_report.markdown_clean_parts.monitor_artifact_resolution import (
    _safe_read_json_object_r3_impl,
    _is_entry_monitor_artifact_r3_impl,
    _canonical_monitor_from_trade_report_path_r3_impl,
    _canonical_monitor_from_section_provenance_r3_impl,
    _resolve_entry_monitor_artifact_r3_impl,
    _candidate_cascade_matches_trade_r3_impl,
)
from libs.agents.reporter.narrative.markdown_clean_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _first_report_path_r4_impl,
    _listify_r4_impl,
    _has_payload_r4_impl,
    _merge_preferred_r4_impl,
    _num_opt_r4_impl,
    _fmt_signed_pct_r4_impl,
    _summary_money_r4_impl,
    _resolve_strategy_refresh_trace_r4_impl,
    _looks_corrupted_r4_impl,
    _dedupe_r4_impl,
)


def _same_day_current_result(report: Dict[str, Any]) -> Dict[str, Any]:
    return _same_day_current_result_r3_impl(report, facade=_r3_sys.modules[__name__])


def _markdown_diagnostics_deps() -> Dict[str, Any]:
    return _markdown_diagnostics_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _same_day_summary_from_texts(
    texts: Iterable[Any],
    fallback: str = "",
    current_result: Dict[str, Any] | None = None,
) -> str:
    return _same_day_summary_from_texts_impl(texts, fallback=fallback, current_result=current_result, deps=_markdown_diagnostics_deps())

def render_trade_report_markdown_clean(report: Dict[str, Any]) -> str:
    return render_trade_report_markdown_clean_r3_impl(report, facade=_r3_sys.modules[__name__])


def _summary_render_deps() -> Dict[str, Any]:
    return _summary_render_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _summary_input_deps() -> Dict[str, Any]:
    return _summary_input_deps_r3_impl(facade=_r3_sys.modules[__name__])

def render_trade_summary_markdown_clean(report: Dict[str, Any]) -> str:
    return _render_trade_summary_markdown_impl(report, deps=_summary_render_deps())

def build_trade_summary_input_clean(report: Dict[str, Any]) -> Dict[str, Any]:
    return _build_trade_summary_input_impl(report, deps=_summary_input_deps())

def render_trade_summary_markdown_with_evaluation_clean(
    report: Dict[str, Any],
    summary_report: Dict[str, Any],
) -> str:
    """Render ai_trade_summary.md with deterministic diagnostics before the LLM draft."""
    return render_trade_summary_markdown_with_evaluation_clean_r3_impl(report, summary_report,
        facade=_r3_sys.modules[__name__])


def _summary_problem_label(value: Any) -> str:
    return _summary_problem_label_impl(value, _summary_eval_sentence=_summary_eval_sentence)


def _summary_root_cause_label(value: Any) -> str:
    return _summary_root_cause_label_impl(value, _summary_eval_sentence=_summary_eval_sentence)


def _summary_fact_text(value: Any) -> str:
    return _summary_fact_text_impl(value, _translate_text=_translate_text, re=re)


def _build_summary_deterministic_diagnostics_section(
    summary_report: Dict[str, Any],
    *,
    report: Dict[str, Any] | None = None,
) -> List[str]:
    return _build_summary_deterministic_diagnostics_section_impl(summary_report, report=report, deps=_markdown_diagnostics_deps())

def _build_summary_llm_evaluation_section(
    summary_report: Dict[str, Any],
    *,
    report: Dict[str, Any] | None = None,
) -> List[str]:
    return _build_summary_llm_evaluation_section_impl(summary_report, report=report, deps=_markdown_diagnostics_deps())

def _normalize_evaluation_hold_duration(text: str, report: Dict[str, Any]) -> str:
    return _normalize_evaluation_hold_duration_impl(text, report, _authoritative_holding_duration_label=_authoritative_holding_duration_label, re=re)


def _section(title: str, content: List[str]) -> List[str]:
    return _section_impl(title, content)


def _strip_trailing_blanks(lines: List[str]) -> List[str]:
    return _strip_trailing_blanks_impl(lines)


def _summary_eval_sentence(value: Any) -> str:
    return _summary_eval_sentence_impl(value, _translate_text=_translate_text, re=re, _ensure_sentence=_ensure_sentence)


def _is_post_entry_gate_text(value: Any) -> bool:
    return _is_post_entry_gate_text_impl(value, _translate_text=_translate_text)


def _is_entry_gate_status_text(value: Any) -> bool:
    text = _translate_text(value).strip()
    return bool(text and ("진입 게이트 상태" in text or "진입 게이트 점수" in text))


def _entry_reason_line(values: Iterable[Any]) -> str:
    return _entry_reason_line_r3_impl(values, facade=_r3_sys.modules[__name__])


def _entry_confidence_line(values: Iterable[Any]) -> str:
    return _entry_confidence_line_r3_impl(values, facade=_r3_sys.modules[__name__])


def _normalize_entry_confidence_for_operator_summary(value: str, *, action: Any, buy_price: Any) -> str:
    return _normalize_entry_confidence_for_operator_summary_r3_impl(value, action=action,
        buy_price=buy_price, facade=_r3_sys.modules[__name__])


def _entry_confidence_for_operator_summary(values: Iterable[Any], *, action: Any, buy_price: Any) -> str:
    return _normalize_entry_confidence_for_operator_summary(
        _entry_confidence_line(values),
        action=action,
        buy_price=buy_price,
    )


_RECOVERED_PARTIAL_EXIT_NOTE = "회수/partial 청산: 당일 진입 증거가 부족해 신규 진입 평가는 제외하고, 당일 청산 결과 중심으로 봅니다."
_RECOVERED_PARTIAL_ENTRY_NOTE = "당일 진입 증거가 부족해 신규 진입 판단은 평가하지 않습니다. 이 리포트는 보유/회수 포지션의 당일 청산 결과를 중심으로 봅니다."


def _is_recovered_partial_exit_report(report: Dict[str, Any]) -> bool:
    return _is_recovered_partial_exit_report_r3_impl(report, facade=_r3_sys.modules[__name__])


def _strategy_memory_deps() -> Dict[str, Any]:
    return _strategy_memory_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _carryover_context(report: Dict[str, Any]) -> Dict[str, Any]:
    return _carryover_context_impl(report, deps=_strategy_memory_deps())

def _strategy_horizon_label(value: Any) -> str:
    return _strategy_horizon_label_impl(value, metadata_value=_metadata_value)


def _strategy_horizon_reason_label(value: Any) -> str:
    return _strategy_horizon_reason_label_impl(value, metadata_value=_metadata_value)


def _strategy_horizon_alignment_label(value: Any) -> str:
    return _strategy_horizon_alignment_label_impl(value, metadata_value=_metadata_value)


def _duration_label_compact(value: Any) -> str:
    return _duration_label_compact_impl(value, num_opt=_num_opt)


def _hold_window_label(window: Dict[str, Any]) -> str:
    return _hold_window_label_impl(
        window,
        as_dict=_as_dict,
        duration_label_compact_fn=_duration_label_compact,
    )


def _strategy_horizon_report_surface(report: Dict[str, Any]) -> Dict[str, Any]:
    return _strategy_horizon_report_surface_r3_impl(report, facade=_r3_sys.modules[__name__])


def _build_strategy_horizon_lines(report: Dict[str, Any], *, compact: bool = False) -> List[str]:
    return _build_strategy_horizon_lines_impl(
        report,
        compact=compact,
        strategy_horizon_report_surface_fn=_strategy_horizon_report_surface,
        strategy_horizon_label_fn=_strategy_horizon_label,
        strategy_horizon_alignment_label_fn=_strategy_horizon_alignment_label,
        strategy_horizon_reason_label_fn=_strategy_horizon_reason_label,
        as_dict=_as_dict,
        axis_label=_axis_label,
        hold_window_label_fn=_hold_window_label,
        duration_label_compact_fn=_duration_label_compact,
    )


def _first_report_path(root: Dict[str, Any], paths: Iterable[str]) -> Any:
    return _first_report_path_r4_impl(root, paths, facade=_r3_sys.modules[__name__])


def _get_report_path(root: Any, path: str) -> Any:
    return _get_report_path_r3_impl(root, path, facade=_r3_sys.modules[__name__])


def _parse_report_datetime(value: Any) -> Optional[datetime]:
    return _parse_report_datetime_r3_impl(value, facade=_r3_sys.modules[__name__])


def _to_kst(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    return value.astimezone(timezone(timedelta(hours=9)))


def _format_kst_datetime(value: Optional[datetime]) -> str:
    kst = _to_kst(value)
    if kst is None:
        return ""
    return kst.strftime("%Y-%m-%d %H:%M KST")


def _format_kst_date(value: Optional[datetime]) -> str:
    kst = _to_kst(value)
    if kst is None:
        return ""
    return kst.strftime("%Y-%m-%d")


def _duration_label_seconds(value: Any) -> str:
    return _duration_label_seconds_r3_impl(value, facade=_r3_sys.modules[__name__])


def _authoritative_hold_duration_seconds(report: Dict[str, Any]) -> Optional[float]:
    """Resolve actual hold time from entry/exit execution timestamps first."""
    return _authoritative_hold_duration_seconds_r3_impl(report, facade=_r3_sys.modules[__name__])


def _authoritative_holding_duration_label(report: Dict[str, Any]) -> str:
    return _duration_label_seconds(_authoritative_hold_duration_seconds(report))


def _carry_state_label(value: Any, *, weekend_carry: bool = False) -> str:
    return _carry_state_label_r3_impl(value, weekend_carry=weekend_carry,
        facade=_r3_sys.modules[__name__])


def _carry_risk_label(value: Any) -> str:
    return _carry_risk_label_r3_impl(value, facade=_r3_sys.modules[__name__])


def _translated_metadata(value: Any) -> str:
    return _metadata_value(_translate_text(value))


def _correct_final_operator_summary(summary: str, *, action: Any) -> str:
    return _correct_final_operator_summary_r3_impl(summary, action=action,
        facade=_r3_sys.modules[__name__])


def _authoritative_final_operator_summary(
    report: Dict[str, Any],
    *,
    action: Any,
    fallback: str = "",
) -> str:
    """Keep the closed-trade conclusion on broker truth, not monitor marks."""
    return _authoritative_final_operator_summary_r3_impl(report, action=action, fallback=fallback,
        facade=_r3_sys.modules[__name__])


def _selection_fallback_context(selection: Dict[str, Any], traded_symbol: Any = "") -> Dict[str, Any]:
    return _selection_fallback_context_r3_impl(selection, traded_symbol,
        facade=_r3_sys.modules[__name__])


def _clip(value: Any, max_len: int = 200) -> str:
    text = str(value or "").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _listify(value: Any) -> List[Any]:
    return _listify_r4_impl(value, facade=_r3_sys.modules[__name__])


def _append_unique_text(out: List[str], value: Any, *, max_len: int = 80) -> None:
    _append_unique_text_impl(out, value, max_len=max_len, metadata_value=_metadata_value, translate_text=_translate_text)


def _append_theme_values(out: List[str], raw_theme: Any) -> None:
    _append_theme_values_impl(out, raw_theme, metadata_value=_metadata_value, translate_text=_translate_text)


def _iter_trade_symbol_metadata_sources(report: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    return _iter_trade_symbol_metadata_sources_impl(report)


def _symbol_in_theme_components(symbol: str, components: Any) -> bool:
    return _symbol_in_theme_components_impl(symbol, components)


def _iter_nested_dicts(value: Any, *, max_depth: int = 8) -> Iterable[Dict[str, Any]]:
    return _iter_nested_dicts_impl(value, max_depth=max_depth)


def _component_themes_for_symbol(report: Dict[str, Any], symbol: str) -> List[str]:
    return _component_themes_for_symbol_impl(
        report,
        symbol,
        metadata_value=_metadata_value,
        translate_text=_translate_text,
    )


def _infer_symbol_name_from_report_text(report: Dict[str, Any], symbol: str) -> str:
    return _infer_symbol_name_from_report_text_impl(
        report,
        symbol,
        metadata_value=_metadata_value,
        translate_text=_translate_text,
    )


def _resolve_trade_symbol_metadata(report: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    return _resolve_trade_symbol_metadata_impl(
        report,
        symbol,
        metadata_value=_metadata_value,
        translate_text=_translate_text,
    )

def _markdown_entry_visibility_deps() -> Dict[str, Any]:
    return _markdown_entry_visibility_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _resolve_entry_execution_visibility(report: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_entry_execution_visibility_impl(report, deps=_markdown_entry_visibility_deps())

def _first_dict(*items: Dict[str, Any]) -> Dict[str, Any]:
    for item in items:
        if isinstance(item, dict) and item:
            return item
    return {}


def _safe_read_json_object(path_value: Any) -> Dict[str, Any]:
    return _safe_read_json_object_r3_impl(path_value, facade=_r3_sys.modules[__name__])


def _is_entry_monitor_artifact(payload: Dict[str, Any]) -> bool:
    return _is_entry_monitor_artifact_r3_impl(payload, facade=_r3_sys.modules[__name__])


def _canonical_monitor_from_trade_report_path(report: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    return _canonical_monitor_from_trade_report_path_r3_impl(report, run_id,
        facade=_r3_sys.modules[__name__])


def _canonical_monitor_from_section_provenance(report: Dict[str, Any]) -> Dict[str, Any]:
    return _canonical_monitor_from_section_provenance_r3_impl(report,
        facade=_r3_sys.modules[__name__])


def _resolve_entry_monitor_artifact(report: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_entry_monitor_artifact_r3_impl(report, facade=_r3_sys.modules[__name__])


def _rank_scope_text(row: Dict[str, Any]) -> str:
    return _rank_scope_text_impl(row)

def _watch_scope_label(row: Dict[str, Any]) -> str:
    return _watch_scope_label_impl(row)

def _candidate_watch_reason_label(value: Any) -> str:
    return _candidate_watch_reason_label_impl(value, _metadata_value=_metadata_value)

def _display_candidate_symbol(value: Any) -> str:
    symbol = _metadata_value(value)
    if not symbol or symbol == "-":
        return ""
    return symbol if re.fullmatch(r"\d{6}", symbol) else ""


def _candidate_cascade_symbols(cascade: Dict[str, Any]) -> set[str]:
    return _candidate_cascade_symbols_r3_impl(cascade, facade=_r3_sys.modules[__name__])


def _candidate_cascade_matches_trade(cascade: Dict[str, Any], traded_symbol: Any) -> bool:
    return _candidate_cascade_matches_trade_r3_impl(cascade, traded_symbol,
        facade=_r3_sys.modules[__name__])


def _markdown_signal_deps() -> Dict[str, Any]:
    return _markdown_signal_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _entry_watch_execution_lines(report: Dict[str, Any], *, require_trade_symbol_match: bool = False) -> List[str]:
    return _entry_watch_execution_lines_impl(report, require_trade_symbol_match=require_trade_symbol_match, deps=_markdown_signal_deps())

def _entry_watch_summary_lines(report: Dict[str, Any], *, require_trade_symbol_match: bool = False) -> List[str]:
    return _entry_watch_summary_lines_impl(report, require_trade_symbol_match=require_trade_symbol_match, deps=_markdown_signal_deps())

def _has_payload(value: Any) -> bool:
    return _has_payload_r4_impl(value, facade=_r3_sys.modules[__name__])


def _merge_preferred(primary: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    return _merge_preferred_r4_impl(primary, fallback, facade=_r3_sys.modules[__name__])


def _resolve_market_context(report: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_market_context_r3_impl(report, facade=_r3_sys.modules[__name__])


def _num_opt(value: Any) -> Optional[float]:
    return _num_opt_r4_impl(value, facade=_r3_sys.modules[__name__])


def _fmt_price(value: Any) -> str:
    num = _num_opt(value)
    if num is None:
        return "-"
    return f"{num:.2f}"


def _fmt_pct(value: Any) -> str:
    num = _num_opt(value)
    if num is None:
        return "-"
    return f"{num * 100.0:.2f}%"


def _fmt_signed_pct(value: Any) -> str:
    return _fmt_signed_pct_r4_impl(value, facade=_r3_sys.modules[__name__])


def _fmt_multiple(value: Any) -> str:
    num = _num_opt(value)
    if num is None:
        return "-"
    return f"{num:.2f}배"


def _korea_index_lines(context: Dict[str, Any]) -> List[str]:
    return _korea_index_lines_r3_impl(context, facade=_r3_sys.modules[__name__])


def _operator_pnl_pct(truth_pnl: Dict[str, Any], shared: Dict[str, Any]) -> tuple[Any, bool]:
    return _operator_pnl_pct_impl(truth_pnl, shared)


def _first_present(*values: Any) -> Any:
    return _first_present_impl(*values)


def _extract_trade_quantity(report: Dict[str, Any]) -> Optional[float]:
    return _extract_trade_quantity_impl(report, as_dict=_as_dict, num_opt=_num_opt)


def _infer_trade_quantity_from_costs(
    *,
    buy_price: Any,
    sell_price: Any,
    pnl: Any,
    fee: Any,
    tax: Any,
) -> Optional[float]:
    return _infer_trade_quantity_from_costs_impl(
        buy_price=buy_price,
        sell_price=sell_price,
        pnl=pnl,
        fee=fee,
        tax=tax,
        num_opt=_num_opt,
    )


def _build_trade_cost_analysis(report: Dict[str, Any]) -> Dict[str, Any]:
    return _build_trade_cost_analysis_impl(
        report,
        as_dict=_as_dict,
        num_opt=_num_opt,
        get_truth_surface_fn=_get_truth_surface,
        extract_trade_quantity_fn=_extract_trade_quantity,
    )


def _trade_cost_analysis_lines(report: Dict[str, Any], *, bullet: str = "*") -> List[str]:
    return _trade_cost_analysis_lines_impl(
        report,
        bullet=bullet,
        build_trade_cost_analysis_fn=_build_trade_cost_analysis,
        fmt_pct=_fmt_pct,
        summary_money=_summary_money,
    )


def _post_exit_shadow_surface(report: Dict[str, Any]) -> Dict[str, Any]:
    return _post_exit_shadow_surface_impl(report)


def _checkpoint_label(value: str) -> str:
    return _checkpoint_label_impl(value)


def _compact_post_exit_shadow(shadow: Dict[str, Any]) -> Dict[str, Any]:
    return _compact_post_exit_shadow_impl(shadow)


def _build_post_exit_shadow_summary_lines(report: Dict[str, Any]) -> List[str]:
    return _build_post_exit_shadow_summary_lines_impl(
        report,
        summary_money=_summary_money,
        fmt_pct=_fmt_pct,
        metadata_value=_metadata_value,
        num_opt=_num_opt,
    )

def _summary_money(value: Any) -> str:
    return _summary_money_r4_impl(value, facade=_r3_sys.modules[__name__])


def _summary_decimal(value: Any, digits: int = 3) -> str:
    num = _num_opt(value)
    if num is None:
        return "-"
    return f"{num:.{max(0, int(digits))}f}".rstrip("0").rstrip(".")


def _first_present_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _resolve_entry_signal_snapshot(report: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_entry_signal_snapshot_impl(report, deps=_markdown_signal_deps())

def _entry_signal_metric_summary_lines(snapshot: Dict[str, Any], *, prefix: str = "진입 수치") -> List[str]:
    return _entry_signal_metric_summary_lines_impl(snapshot, prefix=prefix, deps=_markdown_signal_deps())

def _number_from_text(value: Any) -> Optional[float]:
    text = str(value or "").replace(",", "").strip()
    return _num_opt(text)


def _normalize_exit_trigger_label(value: Any, fallback: Any = "") -> str:
    return _normalize_exit_trigger_label_r3_impl(value, fallback, facade=_r3_sys.modules[__name__])


def _extract_exit_signal_snapshot(values: Iterable[Any]) -> Dict[str, Any]:
    return _extract_exit_signal_snapshot_r3_impl(values, facade=_r3_sys.modules[__name__])


def _enrich_exit_signal_snapshot_from_monitor(
    snapshot: Dict[str, Any],
    monitor: Dict[str, Any],
) -> Dict[str, Any]:
    return _enrich_exit_signal_snapshot_from_monitor_impl(snapshot, monitor, deps=_markdown_signal_deps())

def _build_summary_exit_trigger_lines(
    exit_trigger: Any,
    exit_signal_snapshot: Dict[str, Any],
    *,
    fallback_reason: Any = "",
    buy_price: Any = "",
    exit_price: Any = "",
    pnl_pct: Any = "",
    truth_source: Any = "",
) -> List[str]:
    return _build_summary_exit_trigger_lines_impl(
        exit_trigger,
        exit_signal_snapshot,
        fallback_reason=fallback_reason,
        buy_price=buy_price,
        exit_price=exit_price,
        pnl_pct=pnl_pct,
        truth_source=truth_source,
        deps=_markdown_signal_deps(),
    )

def _strip_html_tags(text: Any) -> str:
    return _strip_html_tags_impl(text, html=html, re=re, _clip=_clip)

def _clean_news_title(text: Any) -> str:
    return _clean_news_title_impl(text, _strip_html_tags=_strip_html_tags)

def _sample_news_titles(values: Any, limit: int = 2) -> List[str]:
    return _sample_news_titles_impl(values, limit=limit, _listify=_listify, _clean_news_title=_clean_news_title)

def _normalize_news_symbol(value: Any) -> str:
    return _normalize_news_symbol_impl(value, re=re)

def _news_symbol_from_item(value: Any) -> str:
    return _news_symbol_from_item_impl(value, re=re, _normalize_news_symbol=_normalize_news_symbol)

def _sample_news_titles_for_symbol(symbol: Any, *sources: Any, limit: int = 2) -> List[str]:
    return _sample_news_titles_for_symbol_impl(
        symbol, *sources, limit=limit, _normalize_news_symbol=_normalize_news_symbol,
        _listify=_listify, _sample_news_titles=_sample_news_titles,
        _news_symbol_from_item=_news_symbol_from_item,
    )

def _mismatched_symbol_news_bullet(text: Any, symbol: Any) -> bool:
    return _mismatched_symbol_news_bullet_impl(text, symbol, re=re, _normalize_news_symbol=_normalize_news_symbol)

def _news_linkage_strength_label(value: Any) -> str:
    return _news_linkage_strength_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _badge(label: str, color: str) -> str:
    return f"**[{label}]**"


def _metadata_value(value: Any) -> str:
    return _metadata_value_r3_impl(value, facade=_r3_sys.modules[__name__])


def _story_type_label(value: Any) -> str:
    return _story_type_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _execution_mode_label(value: Any) -> str:
    return _execution_mode_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _action_label(value: Any) -> str:
    return _action_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _status_label(value: Any) -> str:
    return _status_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _axis_label(value: Any) -> str:
    return _axis_label_impl(value, _clip=_clip)

def _markdown_translation_deps() -> Dict[str, Any]:
    return _markdown_translation_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _translate_text(text: Any) -> str:
    return _translate_text_impl(text, deps=_markdown_translation_deps())

def _bullet_lines(section: Dict[str, Any], *, skip_prefixes: Iterable[str] = ()) -> List[str]:
    return _bullet_lines_r3_impl(section, skip_prefixes=skip_prefixes,
        facade=_r3_sys.modules[__name__])


def _section_summary(section: Dict[str, Any]) -> str:
    return _section_summary_r3_impl(section, facade=_r3_sys.modules[__name__])


def _build_generation_info(report: Dict[str, Any]) -> List[str]:
    return _build_generation_info_r3_impl(report, facade=_r3_sys.modules[__name__])


def _get_truth_surface(report: Dict[str, Any]) -> Dict[str, Any]:
    return _get_truth_surface_impl(report, as_dict=_as_dict)


def _truth_source_label(value: Any) -> str:
    return _truth_source_label_impl(value, clip=_clip, metadata_value=_metadata_value)


def _boolish(value: Any) -> bool:
    return _boolish_impl(value)


def _pnl_basis_label(truth_pnl: Dict[str, Any], shared: Dict[str, Any]) -> str:
    return _pnl_basis_label_impl(
        truth_pnl,
        shared,
        clip=_clip,
        metadata_value=_metadata_value,
        truth_source_label_fn=_truth_source_label,
    )


def _memory_layer_label(value: Any) -> str:
    return _memory_layer_label_r3_impl(value, facade=_r3_sys.modules[__name__])


def _authority_label(value: Any) -> str:
    return "확정 기준" if value else "참고 기준"


def _risk_mode_label(value: Any) -> str:
    return _risk_mode_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _theme_label(value: Any) -> str:
    return _theme_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _policy_token_label(value: Any) -> str:
    return _policy_token_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _is_not_captured(value: Any) -> bool:
    raw = _clip(value, 80).lower()
    return raw in {"", "-", "not_captured", "not captured", "unknown", "unavailable"}


def _is_closed_trade_context(report: Dict[str, Any]) -> bool:
    return _is_closed_trade_context_r3_impl(report, facade=_r3_sys.modules[__name__])


def _memory_status_label(value: Any) -> str:
    return _memory_status_label_r3_impl(value, facade=_r3_sys.modules[__name__])


def _markdown_truth_surface_deps() -> Dict[str, Any]:
    return _markdown_truth_surface_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _build_truth_surface(report: Dict[str, Any]) -> List[str]:
    return _build_truth_surface_impl(report, deps=_markdown_truth_surface_deps())

def _memory_layers_text(values: Any, *, arrow: bool = False, humanize: bool = True) -> str:
    return _memory_layers_text_r3_impl(values, arrow=arrow, humanize=humanize,
        facade=_r3_sys.modules[__name__])


def _memory_packet_state_line(name: str, packet: Dict[str, Any]) -> str:
    return _memory_packet_state_line_r3_impl(name, packet, facade=_r3_sys.modules[__name__])


def _on_off_label(value: Any) -> str:
    return "켜짐" if bool(value) else "꺼짐"


def _applied_label(value: Any) -> str:
    return "적용됨" if bool(value) else "미적용"


def _policy_phase_line(label: str, policy: Dict[str, Any]) -> str:
    return _policy_phase_line_r3_impl(label, policy, facade=_r3_sys.modules[__name__])


def _same_policy_snapshot(left: Dict[str, Any], right: Dict[str, Any]) -> bool:
    return _same_policy_snapshot_r3_impl(left, right, facade=_r3_sys.modules[__name__])


def _scanner_phase_line(scanner: Dict[str, Any]) -> str:
    return _scanner_phase_line_r3_impl(scanner, facade=_r3_sys.modules[__name__])


def _monitor_phase_line(monitor: Dict[str, Any]) -> str:
    return _monitor_phase_line_r3_impl(monitor, facade=_r3_sys.modules[__name__])


def _playbook_label(value: Any) -> str:
    return _playbook_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _monitor_guidance_label(value: Any) -> str:
    return _monitor_guidance_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _scanner_bias_label(value: Any) -> str:
    return _scanner_bias_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _policy_source_label(value: Any) -> str:
    return _policy_source_label_impl(value, _clip=_clip, _metadata_value=_metadata_value)

def _failure_label(value: Any) -> str:
    return _failure_label_impl(value, _clip=_clip, _playbook_label=_playbook_label, _metadata_value=_metadata_value)

def _reason_tag_summary(tag: str) -> str:
    return _reason_tag_summary_r3_impl(tag, facade=_r3_sys.modules[__name__])


def _reason_summary_line(tags: List[Any], prefix: str) -> Optional[str]:
    return _reason_summary_line_r3_impl(tags, prefix, facade=_r3_sys.modules[__name__])


def _reporter_source_label(source_reports: Dict[str, Any]) -> str:
    return _reporter_source_label_impl(source_reports)

def _humanize_reporter_source_label(source_reports: Dict[str, Any]) -> str:
    return _humanize_reporter_source_label_impl(source_reports, _reporter_source_label=_reporter_source_label, _translate_text=_translate_text)

def _resolve_prompt_proven_surface(memory: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_prompt_proven_surface_r3_impl(memory, facade=_r3_sys.modules[__name__])


def _resolve_reconstructed_memory_surface(memory: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_reconstructed_memory_surface_r3_impl(memory, facade=_r3_sys.modules[__name__])


def _build_prompt_proven_memory(report: Dict[str, Any]) -> List[str]:
    return _build_prompt_proven_memory_impl(report, deps=_strategy_memory_deps())

def _build_reconstructed_trade_memory(report: Dict[str, Any]) -> List[str]:
    return _build_reconstructed_trade_memory_r3_impl(report, facade=_r3_sys.modules[__name__])

def _build_memory_application(report: Dict[str, Any]) -> List[str]:
    return _build_memory_application_impl(report, deps=_strategy_memory_deps())

def _market_context_structured_lines(context: Dict[str, Any]) -> List[str]:
    return _market_context_structured_lines_r3_impl(context, facade=_r3_sys.modules[__name__])


def _market_context_summary_from_raw(summary: Any) -> str:
    return _market_context_summary_from_raw_r3_impl(summary, facade=_r3_sys.modules[__name__])


def _markdown_strategy_deps() -> Dict[str, Any]:
    return _markdown_strategy_deps_r3_impl(facade=_r3_sys.modules[__name__])

def _build_market_context(report: Dict[str, Any]) -> List[str]:
    return _build_market_context_impl(report, deps=_markdown_strategy_deps())

def _build_strategist_summary(report: Dict[str, Any]) -> List[str]:
    return _build_strategist_summary_impl(report, deps=_markdown_strategy_deps())

def _resolve_strategist_output_surface(report: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_strategist_output_surface_r3_impl(report, facade=_r3_sys.modules[__name__])


def _operatorize_strategist_output_text(value: Any) -> str:
    return _operatorize_strategist_output_text_impl(value, _metadata_value=_metadata_value)

def _strategy_output_text(value: Any, *, max_len: int = 240) -> str:
    return _strategy_output_text_impl(value, max_len=max_len, _operatorize_strategist_output_text=_operatorize_strategist_output_text, _clip=_clip)

def _strategy_output_list_text(values: Any, *, limit: int = 4, sep: str = ", ") -> str:
    return _strategy_output_list_text_impl(values, limit=limit, sep=sep, _listify=_listify, _strategy_output_text=_strategy_output_text)

def _strategy_output_layer_bits(layer_decisions: Any) -> str:
    return _strategy_output_layer_bits_r3_impl(layer_decisions, facade=_r3_sys.modules[__name__])


def _append_strategy_output_line(lines: List[str], label: str, text: str) -> None:
    clean = _clip(_operatorize_strategist_output_text(text), 320)
    if clean and not _looks_corrupted(clean):
        lines.append(f"- [{label}] {clean}")


def _resolve_strategy_refresh_trace(report: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_strategy_refresh_trace_r4_impl(report, facade=_r3_sys.modules[__name__])


def _build_strategist_refresh_trace(report: Dict[str, Any]) -> List[str]:
    return _build_strategist_refresh_trace_r3_impl(report, facade=_r3_sys.modules[__name__])


def _build_strategist_output_surface(report: Dict[str, Any]) -> List[str]:
    return _build_strategist_output_surface_impl(report, deps=_markdown_strategy_deps())

def _is_scanner_execution_mismatch_line(value: Any) -> bool:
    return _is_scanner_execution_mismatch_line_impl(value, metadata_value=_metadata_value)


def _is_scanner_selection_label_line(value: Any) -> bool:
    return _is_scanner_selection_label_line_impl(value, metadata_value=_metadata_value)


def _is_redundant_symbol_selection_line(value: Any) -> bool:
    return _is_redundant_symbol_selection_line_impl(value, metadata_value=_metadata_value)


def _build_symbol_selection(report: Dict[str, Any]) -> List[str]:
    return _build_symbol_selection_impl(
        report,
        as_dict=_as_dict,
        listify=_listify,
        metadata_value=_metadata_value,
        selection_fallback_context=_selection_fallback_context,
        num_opt=_num_opt,
        translate_text=_translate_text,
        looks_corrupted=_looks_corrupted,
        translate_reason_phrase=_translate_reason_phrase,
        clip=_clip,
        section_summary=_section_summary,
        dedupe=_dedupe,
    )


def _build_scanner_comparison(report: Dict[str, Any]) -> List[str]:
    return _build_scanner_comparison_impl(
        report,
        as_dict=_as_dict,
        listify=_listify,
        metadata_value=_metadata_value,
        section_summary=_section_summary,
        looks_corrupted=_looks_corrupted,
        num_opt=_num_opt,
        clip=_clip,
        translate_text=_translate_text,
        translate_reason_phrase=_translate_reason_phrase,
        dedupe=_dedupe,
    )

def _build_entry_decision(report: Dict[str, Any]) -> List[str]:
    return _build_entry_decision_r3_impl(report, facade=_r3_sys.modules[__name__])


def _build_guard_approval(report: Dict[str, Any]) -> List[str]:
    return _build_guard_approval_r3_impl(report, facade=_r3_sys.modules[__name__])

def _parse_monitor_bullet(text: str) -> Optional[str]:
    return _parse_monitor_bullet_impl(
        text,
        action_label=_action_label,
        axis_label=_axis_label,
        metadata_value=_metadata_value,
        translate_text=_translate_text,
    )


def _normalize_monitor_story_line(text: str, *, closed_trade: bool = False) -> Optional[str]:
    return _normalize_monitor_story_line_impl(
        text,
        closed_trade=closed_trade,
        clip=_clip,
        parse_monitor_bullet_fn=_parse_monitor_bullet,
        looks_corrupted=_looks_corrupted,
    )


def _closed_trade_monitor_preface(report: Dict[str, Any]) -> List[str]:
    return _closed_trade_monitor_preface_impl(
        report,
        is_closed_trade_context=_is_closed_trade_context,
        get_truth_surface=_get_truth_surface,
        as_dict=_as_dict,
        badge=_badge,
        fmt_price=_fmt_price,
        fmt_pct=_fmt_pct,
    )


def _build_holding_story(report: Dict[str, Any]) -> List[str]:
    return _build_holding_story_impl(
        report,
        as_dict=_as_dict,
        section_summary=_section_summary,
        is_closed_trade_context=_is_closed_trade_context,
        listify=_listify,
        clip=_clip,
        normalize_monitor_story_line_fn=_normalize_monitor_story_line,
        action_label=_action_label,
        dedupe=_dedupe,
        num_opt=_num_opt,
        axis_label=_axis_label,
        fmt_price=_fmt_price,
        fmt_pct=_fmt_pct,
    )

def _build_exit_decision(report: Dict[str, Any]) -> List[str]:
    return _build_exit_decision_impl(
        report,
        as_dict=_as_dict,
        section_summary=_section_summary,
        is_closed_trade_context=_is_closed_trade_context,
        closed_trade_monitor_preface_fn=_closed_trade_monitor_preface,
        listify=_listify,
        clip=_clip,
        translate_text=_translate_text,
        axis_label=_axis_label,
        action_label=_action_label,
        normalize_monitor_story_line_fn=_normalize_monitor_story_line,
        fmt_pct=_fmt_pct,
        dedupe=_dedupe,
    )


def _build_monitor_snapshot(report: Dict[str, Any]) -> List[str]:
    return _build_monitor_snapshot_impl(
        report,
        as_dict=_as_dict,
        resolve_entry_execution_visibility=_resolve_entry_execution_visibility,
        entry_watch_execution_lines=_entry_watch_execution_lines,
        axis_label=_axis_label,
        fmt_pct=_fmt_pct,
        listify=_listify,
        price_source_label=_price_source_label,
        price_source_policy_label=_price_source_policy_label,
    )


def _price_source_label(value: Any) -> str:
    return _price_source_label_impl(value, clip=_clip, metadata_value=_metadata_value)


def _price_source_policy_label(value: Any) -> str:
    return _price_source_policy_label_impl(value, clip=_clip)

def _build_execution_quality(report: Dict[str, Any]) -> List[str]:
    return _build_execution_quality_r3_impl(report, facade=_r3_sys.modules[__name__])


def _humanize_reporter_recommendation(text: Any) -> str:
    return _humanize_reporter_recommendation_r3_impl(text, facade=_r3_sys.modules[__name__])

def _humanize_reporter_pattern(name: Any, detail: Any, value: Any) -> str:
    return _humanize_reporter_pattern_r3_impl(name, detail, value, facade=_r3_sys.modules[__name__])


def _build_reporter_evaluation(report: Dict[str, Any]) -> List[str]:
    return _build_reporter_evaluation_r3_impl(report, facade=_r3_sys.modules[__name__])

def _build_weaknesses(report: Dict[str, Any]) -> List[str]:
    return _build_weaknesses_r3_impl(report, facade=_r3_sys.modules[__name__])


def _extract_metadata_from_texts(texts: Iterable[str]) -> List[str]:
    return _extract_metadata_from_texts_r3_impl(texts, facade=_r3_sys.modules[__name__])


def _build_provenance(report: Dict[str, Any]) -> List[str]:
    return _build_provenance_r3_impl(report, facade=_r3_sys.modules[__name__])


def _build_timeline(report: Dict[str, Any]) -> List[str]:
    return _build_timeline_r3_impl(report, facade=_r3_sys.modules[__name__])


def _translate_watch_item(text: str) -> str:
    return _translate_watch_item_r3_impl(text, facade=_r3_sys.modules[__name__])


def _translate_reason_phrase(text: str) -> str:
    return _translate_reason_phrase_r3_impl(text, facade=_r3_sys.modules[__name__])


def _translate_invalidation_item(text: str) -> str:
    return _translate_invalidation_item_r3_impl(text, facade=_r3_sys.modules[__name__])


def _ensure_sentence(text: str) -> str:
    return _ensure_sentence_r3_impl(text, facade=_r3_sys.modules[__name__])


def _noun_predicate_was(text: str) -> str:
    return _noun_predicate_was_r3_impl(text, facade=_r3_sys.modules[__name__])


def _build_final_conclusion(report: Dict[str, Any]) -> List[str]:
    return _build_final_conclusion_r3_impl(report, facade=_r3_sys.modules[__name__])


def _first_nonempty(values: List[Any]) -> Any:
    return _first_nonempty_r3_impl(values, facade=_r3_sys.modules[__name__])


def _monitor_delta_interpretation(rows: List[Any]) -> str:
    return _monitor_delta_interpretation_r3_impl(rows, facade=_r3_sys.modules[__name__])


def _looks_corrupted(text: str) -> bool:
    return _looks_corrupted_r4_impl(text, facade=_r3_sys.modules[__name__])


def _dedupe(lines: List[str]) -> List[str]:
    return _dedupe_r4_impl(lines, facade=_r3_sys.modules[__name__])
