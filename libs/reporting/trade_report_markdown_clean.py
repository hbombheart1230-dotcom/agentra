from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

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


def _same_day_current_result(report: Dict[str, Any]) -> Dict[str, Any]:
    truth_surface = _as_dict(report.get("truth_surface"))
    status = _as_dict(truth_surface.get("status"))
    status_text = str(status.get("status") or report.get("status") or "").strip().lower()
    if status_text != "closed":
        return {}
    pnl = _as_dict(truth_surface.get("pnl"))
    pnl_value = _num_opt(pnl.get("value"))
    pnl_pct = _num_opt(pnl.get("pct"))
    if pnl_value is None and pnl_pct is None:
        return {}
    classification_value = pnl_value if pnl_value is not None else pnl_pct
    if classification_value is None:
        return {}
    pct_text = ""
    if pnl_pct is not None:
        pct_percent = pnl_pct * 100.0 if abs(pnl_pct) <= 1.0 else pnl_pct
        pct_text = f"{pct_percent:.2f}"
    return {
        "classification": 1 if classification_value > 0 else (-1 if classification_value < 0 else 0),
        "pct_text": pct_text,
    }


def _markdown_diagnostics_deps() -> Dict[str, Any]:
    return {
        "action_label": _action_label,
        "as_dict": _as_dict,
        "authoritative_final_operator_summary": _authoritative_final_operator_summary,
        "first_present_impl": _first_present_impl,
        "listify": _listify,
        "looks_like_symbol_name_impl": _looks_like_symbol_name_impl,
        "metadata_value": _metadata_value,
        "normalize_evaluation_hold_duration": _normalize_evaluation_hold_duration,
        "resolve_trade_symbol_metadata": _resolve_trade_symbol_metadata,
        "strip_trailing_blanks": _strip_trailing_blanks,
        "summary_decimal": _summary_decimal,
        "summary_eval_sentence": _summary_eval_sentence,
        "summary_fact_text": _summary_fact_text,
        "summary_money": _summary_money,
        "summary_problem_label": _summary_problem_label,
        "summary_root_cause_label": _summary_root_cause_label,
        "translate_text": _translate_text,
    }

def _same_day_summary_from_texts(
    texts: Iterable[Any],
    fallback: str = "",
    current_result: Dict[str, Any] | None = None,
) -> str:
    return _same_day_summary_from_texts_impl(texts, fallback=fallback, current_result=current_result, deps=_markdown_diagnostics_deps())

def render_trade_report_markdown_clean(report: Dict[str, Any]) -> str:
    lines: List[str] = []

    trade_id = _clip(report.get("trade_id"), 80) or "-"
    action = _action_label(report.get("action"))
    symbol = _clip(report.get("symbol"), 32) or "해당 종목"
    status = _status_label(report.get("status"))
    story_type = _story_type_label(report.get("story_type"))
    execution_mode = _execution_mode_label(report.get("execution_mode_label"))

    lines.append(f"# AI 거래 리포트 ({trade_id})")
    lines.append("")
    lines.append(f"- 이번 거래는 {action} {symbol} 기준으로 정리했습니다.")
    lines.append(f"- 라이프사이클 상태는 {status}입니다.")
    lines.append(f"- 리포트 유형은 {story_type}입니다.")
    lines.append(f"- 실행 모드는 {execution_mode}입니다.")

    lines.extend(_section("생성 정보", _build_generation_info(report)))
    lines.extend(_section("Truth Surface", _build_truth_surface(report)))
    lines.extend(_section("전략가 프롬프트에서 직접 확인된 메모리", _build_prompt_proven_memory(report)))
    lines.extend(_section("거래 설명용 사후 복원 메모리", _build_reconstructed_trade_memory(report)))
    lines.extend(_section("실제로 적용된 결정론적 메모리 bias", _build_memory_application(report)))
    lines.extend(_section("시장 환경 요약", _build_market_context(report)))
    lines.extend(_section("전략가 요약", _build_strategist_summary(report)))
    lines.extend(_section("전략 보유 기간", _build_strategy_horizon_lines(report)))
    lines.extend(_section("통제 모의투자 레인 근거", _render_controlled_lane_report_lines(report)))
    lines.extend(_section("전략가 Refresh Trace", _build_strategist_refresh_trace(report)))
    lines.extend(_section("전략가 Quant Context 사용", _render_strategist_quant_context_usage_lines_impl(report)))
    lines.extend(_section("전략가 출력 근거", _build_strategist_output_surface(report)))
    lines.extend(_section("전술/퀀트 진단", _render_quant_tactic_report_lines_impl(report)))
    lines.extend(_section("선택된 종목 상세 분석", _build_symbol_selection(report)))
    lines.extend(_section("스캐너 후보 비교", _build_scanner_comparison(report)))
    lines.extend(_section("가드 승인 결과", _build_guard_approval(report)))
    lines.extend(_section("진입 상세 근거", _build_entry_decision(report)))
    lines.extend(_section("보유 경과", _build_holding_story(report)))
    lines.extend(_section("청산 판단 근거", _build_exit_decision(report)))
    post_exit_shadow_lines = _build_post_exit_shadow_summary_lines(report)
    if post_exit_shadow_lines:
        if str(post_exit_shadow_lines[0]).strip() == "### 매도 후 가격 추적 (관측-only)":
            post_exit_shadow_lines = post_exit_shadow_lines[2:]
        lines.extend(_section("매도 후 가격 추적 (관측-only)", post_exit_shadow_lines))
    lines.extend(_section("모니터 스냅샷", _build_monitor_snapshot(report)))
    lines.extend(_section("실행 결과", _build_execution_quality(report)))
    lines.extend(_section("결과 평가", _build_reporter_evaluation(report)))
    lines.extend(_section("보완 사안", _build_weaknesses(report)))
    lines.extend(_section("근거 출처", _build_provenance(report)))
    lines.extend(_section("전체 타임라인", _build_timeline(report)))
    lines.extend(_section("최종 운영 판단", _build_final_conclusion(report)))

    return "\n".join(_strip_trailing_blanks(lines)).strip() + "\n"


def _summary_render_deps() -> Dict[str, Any]:
    return {
        "RECOVERED_PARTIAL_ENTRY_NOTE": _RECOVERED_PARTIAL_ENTRY_NOTE,
        "RECOVERED_PARTIAL_EXIT_NOTE": _RECOVERED_PARTIAL_EXIT_NOTE,
        "action_label": _action_label,
        "applied_label": _applied_label,
        "as_dict": _as_dict,
        "authoritative_final_operator_summary": _authoritative_final_operator_summary,
        "authoritative_holding_duration_label": _authoritative_holding_duration_label,
        "build_post_exit_shadow_summary_lines": _build_post_exit_shadow_summary_lines,
        "build_strategy_horizon_lines": _build_strategy_horizon_lines,
        "build_summary_exit_trigger_lines": _build_summary_exit_trigger_lines,
        "build_trade_cost_analysis": _build_trade_cost_analysis,
        "carryover_context": _carryover_context,
        "clip": _clip,
        "dedupe": _dedupe,
        "enrich_exit_signal_snapshot_from_monitor": _enrich_exit_signal_snapshot_from_monitor,
        "ensure_sentence": _ensure_sentence,
        "entry_confidence_for_operator_summary": _entry_confidence_for_operator_summary,
        "entry_reason_line": _entry_reason_line,
        "entry_signal_metric_summary_lines": _entry_signal_metric_summary_lines,
        "entry_watch_summary_lines": _entry_watch_summary_lines,
        "execution_mode_label": _execution_mode_label,
        "extract_exit_signal_snapshot": _extract_exit_signal_snapshot,
        "fmt_pct": _fmt_pct,
        "get_truth_surface": _get_truth_surface,
        "is_not_captured": _is_not_captured,
        "is_post_entry_gate_text": _is_post_entry_gate_text,
        "is_recovered_partial_exit_report": _is_recovered_partial_exit_report,
        "korea_index_lines": _korea_index_lines,
        "listify": _listify,
        "memory_layers_text": _memory_layers_text,
        "metadata_value": _metadata_value,
        "normalize_entry_confidence_for_operator_summary": _normalize_entry_confidence_for_operator_summary,
        "normalize_exit_trigger_label": _normalize_exit_trigger_label,
        "num_opt": _num_opt,
        "operator_pnl_pct": _operator_pnl_pct,
        "playbook_label": _playbook_label,
        "pnl_basis_label": _pnl_basis_label,
        "render_controlled_lane_report_lines": _render_controlled_lane_report_lines,
        "render_quant_tactic_report_lines_impl": _render_quant_tactic_report_lines_impl,
        "resolve_entry_signal_snapshot": _resolve_entry_signal_snapshot,
        "resolve_market_context": _resolve_market_context,
        "resolve_trade_symbol_metadata": _resolve_trade_symbol_metadata,
        "risk_mode_label": _risk_mode_label,
        "same_day_current_result": _same_day_current_result,
        "same_day_summary_from_texts": _same_day_summary_from_texts,
        "sample_news_titles": _sample_news_titles,
        "sample_news_titles_for_symbol": _sample_news_titles_for_symbol,
        "selection_fallback_context": _selection_fallback_context,
        "status_label": _status_label,
        "story_type_label": _story_type_label,
        "strip_trailing_blanks": _strip_trailing_blanks,
        "theme_label": _theme_label,
        "trade_cost_analysis_lines": _trade_cost_analysis_lines,
        "translate_text": _translate_text,
        "translated_metadata": _translated_metadata,
    }

def _summary_input_deps() -> Dict[str, Any]:
    return {
        "RECOVERED_PARTIAL_ENTRY_NOTE": _RECOVERED_PARTIAL_ENTRY_NOTE,
        "RECOVERED_PARTIAL_EXIT_NOTE": _RECOVERED_PARTIAL_EXIT_NOTE,
        "action_label": _action_label,
        "as_dict": _as_dict,
        "authoritative_final_operator_summary": _authoritative_final_operator_summary,
        "authoritative_hold_duration_seconds": _authoritative_hold_duration_seconds,
        "authoritative_holding_duration_label": _authoritative_holding_duration_label,
        "build_trade_cost_analysis": _build_trade_cost_analysis,
        "carryover_context": _carryover_context,
        "clip": _clip,
        "compact_post_exit_shadow": _compact_post_exit_shadow,
        "enrich_exit_signal_snapshot_from_monitor": _enrich_exit_signal_snapshot_from_monitor,
        "entry_confidence_for_operator_summary": _entry_confidence_for_operator_summary,
        "entry_reason_line": _entry_reason_line,
        "entry_watch_execution_lines": _entry_watch_execution_lines,
        "execution_mode_label": _execution_mode_label,
        "extract_exit_signal_snapshot": _extract_exit_signal_snapshot,
        "fmt_pct": _fmt_pct,
        "get_truth_surface": _get_truth_surface,
        "is_not_captured": _is_not_captured,
        "is_recovered_partial_exit_report": _is_recovered_partial_exit_report,
        "listify": _listify,
        "metadata_value": _metadata_value,
        "normalize_exit_trigger_label": _normalize_exit_trigger_label,
        "num_opt": _num_opt,
        "operator_pnl_pct": _operator_pnl_pct,
        "playbook_label": _playbook_label,
        "post_exit_shadow_surface": _post_exit_shadow_surface,
        "quant_tactic_surface_impl": _quant_tactic_surface_impl,
        "resolve_entry_execution_visibility": _resolve_entry_execution_visibility,
        "resolve_entry_signal_snapshot": _resolve_entry_signal_snapshot,
        "resolve_market_context": _resolve_market_context,
        "resolve_trade_symbol_metadata": _resolve_trade_symbol_metadata,
        "risk_mode_label": _risk_mode_label,
        "same_day_current_result": _same_day_current_result,
        "same_day_summary_from_texts": _same_day_summary_from_texts,
        "sample_news_titles": _sample_news_titles,
        "sample_news_titles_for_symbol": _sample_news_titles_for_symbol,
        "selection_fallback_context": _selection_fallback_context,
        "status_label": _status_label,
        "story_type_label": _story_type_label,
        "strategy_horizon_report_surface": _strategy_horizon_report_surface,
        "theme_label": _theme_label,
        "translate_text": _translate_text,
        "translated_metadata": _translated_metadata,
        "truth_source_label": _truth_source_label,
    }

def render_trade_summary_markdown_clean(report: Dict[str, Any]) -> str:
    return _render_trade_summary_markdown_impl(report, deps=_summary_render_deps())

def build_trade_summary_input_clean(report: Dict[str, Any]) -> Dict[str, Any]:
    return _build_trade_summary_input_impl(report, deps=_summary_input_deps())

def render_trade_summary_markdown_with_evaluation_clean(
    report: Dict[str, Any],
    summary_report: Dict[str, Any],
) -> str:
    """Render ai_trade_summary.md with deterministic diagnostics before the LLM draft."""

    base = render_trade_summary_markdown_clean(report).rstrip()
    deterministic_section = _build_summary_deterministic_diagnostics_section(summary_report, report=report)
    llm_section = _build_summary_llm_evaluation_section(summary_report, report=report)
    section = list(deterministic_section)
    if deterministic_section and llm_section:
        section.append("")
    section.extend(llm_section)
    section = _strip_trailing_blanks(section)
    if not section:
        return base + "\n"
    marker = "\n---\n\n## 🧭 거래 개요"
    block = "\n".join(section)
    if marker in base:
        return base.replace(marker, f"\n{block}\n{marker}", 1).strip() + "\n"
    return f"{base}\n\n{block}\n"


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
    needles = ("진입 사유", "직전 고점", "vwap", "리바운드", "돌파", "rebound", "breakout")
    for raw in values:
        text = _translate_text(raw).strip()
        if not text or _is_post_entry_gate_text(text) or _is_entry_gate_status_text(text):
            continue
        lowered = text.lower()
        if any(needle in lowered for needle in needles):
            return text.rstrip(".")
    return ""


def _entry_confidence_line(values: Iterable[Any]) -> str:
    for raw in values:
        text = _translate_text(raw).strip()
        if not text or _is_post_entry_gate_text(text):
            continue
        lowered = text.lower()
        if "신뢰도" in text or "confidence" in lowered:
            return text.rstrip(".")
    return ""


def _normalize_entry_confidence_for_operator_summary(value: str, *, action: Any, buy_price: Any) -> str:
    text = str(value or "").strip()
    if (
        text
        and "미통과" in text
        and "진입 게이트" in text
        and str(action or "").strip() == "매도"
        and buy_price not in (None, "")
    ):
        return "진입 게이트 상세는 실제 BUY 체결 이후 사후 모니터 재평가와 혼재될 수 있어 확정 표시하지 않습니다"
    return text


def _entry_confidence_for_operator_summary(values: Iterable[Any], *, action: Any, buy_price: Any) -> str:
    return _normalize_entry_confidence_for_operator_summary(
        _entry_confidence_line(values),
        action=action,
        buy_price=buy_price,
    )


_RECOVERED_PARTIAL_EXIT_NOTE = "회수/partial 청산: 당일 진입 증거가 부족해 신규 진입 평가는 제외하고, 당일 청산 결과 중심으로 봅니다."
_RECOVERED_PARTIAL_ENTRY_NOTE = "당일 진입 증거가 부족해 신규 진입 판단은 평가하지 않습니다. 이 리포트는 보유/회수 포지션의 당일 청산 결과를 중심으로 봅니다."


def _is_recovered_partial_exit_report(report: Dict[str, Any]) -> bool:
    shared = _as_dict(report.get("shared_facts"))
    final = _as_dict(report.get("final_operator_conclusion"))
    status = str(report.get("status") or shared.get("status") or "").strip().lower()
    action_raw = str(final.get("current_action") or report.get("action") or shared.get("action") or "").strip()
    action_is_sell = action_raw.upper() == "SELL" or _action_label(action_raw) == "매도"
    if status != "partial" or not action_is_sell:
        return False

    explicit_markers = (
        bool(report.get("evidence_recovery_used"))
        or str(report.get("trade_origin") or "").strip().lower() == "recovered_partial"
        or str(report.get("lifecycle_completeness") or "").strip().lower() == "partial"
    )
    entry = _as_dict(report.get("entry_decision"))
    selection = _as_dict(report.get("why_this_symbol_was_chosen"))
    entry_text = " ".join([str(entry.get("summary") or "")] + [str(item or "") for item in _listify(entry.get("bullets"))]).lower()
    entry_missing = (
        "entry evidence was not captured" in entry_text
        or "entry execution evidence is incomplete" in entry_text
        or "진입 실행 근거가 불완전" in entry_text
        or "진입 근거가 미확인" in entry_text
    )
    selected_rank = _num_opt(selection.get("selected_rank"))
    universe_size = _num_opt(selection.get("universe_size"))
    scanner_empty = selected_rank == 0 and universe_size == 0
    return bool(explicit_markers or entry_missing or scanner_empty)


def _strategy_memory_deps() -> Dict[str, Any]:
    return {
        "action_label": _action_label,
        "as_dict": _as_dict,
        "badge": _badge,
        "carry_risk_label": _carry_risk_label,
        "carry_state_label": _carry_state_label,
        "dedupe": _dedupe,
        "duration_label_seconds": _duration_label_seconds,
        "failure_label": _failure_label,
        "first_report_path": _first_report_path,
        "fmt_pct": _fmt_pct,
        "format_kst_date": _format_kst_date,
        "format_kst_datetime": _format_kst_datetime,
        "humanize_reporter_source_label": _humanize_reporter_source_label,
        "listify": _listify,
        "memory_layers_text": _memory_layers_text,
        "memory_packet_state_line": _memory_packet_state_line,
        "memory_status_label": _memory_status_label,
        "metadata_value": _metadata_value,
        "monitor_delta_interpretation": _monitor_delta_interpretation,
        "monitor_phase_line": _monitor_phase_line,
        "num_opt": _num_opt,
        "parse_report_datetime": _parse_report_datetime,
        "playbook_label": _playbook_label,
        "policy_phase_line": _policy_phase_line,
        "policy_source_label": _policy_source_label,
        "reason_summary_line": _reason_summary_line,
        "resolve_prompt_proven_surface": _resolve_prompt_proven_surface,
        "same_policy_snapshot": _same_policy_snapshot,
        "scanner_phase_line": _scanner_phase_line,
        "to_kst": _to_kst,
    }

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
    surface = _strategy_horizon_report_surface_impl(
        report,
        as_dict=_as_dict,
        first_report_path=_first_report_path,
        compact_post_exit_shadow=_compact_post_exit_shadow,
        post_exit_shadow_surface=_post_exit_shadow_surface,
        carryover_context=_carryover_context,
        num_opt=_num_opt,
        duration_label_compact_fn=_duration_label_compact,
    )
    authoritative_hold_sec = _authoritative_hold_duration_seconds(report)
    if authoritative_hold_sec is not None:
        surface = dict(surface)
        surface["actual_hold_sec"] = authoritative_hold_sec
        surface["actual_hold_label"] = _duration_label_seconds(authoritative_hold_sec)
        surface["actual_hold_source"] = "entry_exit_execution_timestamps"
    return surface


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
    for path in paths:
        value = _get_report_path(root, path)
        if value not in (None, "", [], {}):
            return value
    return None


def _get_report_path(root: Any, path: str) -> Any:
    current = root
    for part in str(path or "").split("."):
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _parse_report_datetime(value: Any) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


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
    seconds = _num_opt(value)
    if seconds is None or seconds <= 0:
        return ""
    total = int(round(seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts: List[str] = []
    if days:
        parts.append(f"{days}일")
    if hours:
        parts.append(f"{hours}시간")
    if minutes:
        parts.append(f"{minutes}분")
    if seconds or not parts:
        parts.append(f"{seconds}초")
    return " ".join(parts)


def _authoritative_hold_duration_seconds(report: Dict[str, Any]) -> Optional[float]:
    """Resolve actual hold time from entry/exit execution timestamps first."""

    entry_ts = _first_report_path(
        report,
        [
            "fact_payload.trade.entry_execution_details.ts",
            "entry_execution_details.ts",
            "fact_payload.trade.entry_summary.ts",
            "entry_summary.ts",
        ],
    )
    exit_ts = _first_report_path(
        report,
        [
            "fact_payload.trade.exit_execution_details.ts",
            "fact_payload.trade.execution_details.ts",
            "exit_execution_details.ts",
            "execution_details.ts",
            "fact_payload.trade.exit_summary.ts",
            "exit_summary.ts",
        ],
    )
    entry_dt = _parse_report_datetime(entry_ts)
    exit_dt = _parse_report_datetime(exit_ts)
    if entry_dt is not None and exit_dt is not None and exit_dt >= entry_dt:
        return float((exit_dt - entry_dt).total_seconds())

    return _num_opt(
        _first_report_path(
            report,
            [
                "fact_payload.trade.exit_vs_strategy_intent.actual_hold_sec",
                "fact_payload.trade.canonical_agent_artifacts.monitor.exit_vs_strategy_intent.actual_hold_sec",
                "monitor_snapshot.exit_vs_strategy_intent.actual_hold_sec",
                "exit_vs_strategy_intent.actual_hold_sec",
                "shared_facts.exit_vs_strategy_intent.actual_hold_sec",
            ],
        )
    )


def _authoritative_holding_duration_label(report: Dict[str, Any]) -> str:
    return _duration_label_seconds(_authoritative_hold_duration_seconds(report))


def _carry_state_label(value: Any, *, weekend_carry: bool = False) -> str:
    key = str(value or "").strip().lower()
    labels = {
        "multi_session_stale": "전일/주말 이월 보유",
        "overnight_open": "오버나이트 보유",
        "eod_carry_approved": "장마감 이월 승인",
        "carry_overnight_approved": "오버나이트 승인",
        "overnight": "오버나이트 보유",
    }
    if key in labels:
        return labels[key]
    if weekend_carry:
        return "주말 이월 보유"
    return _metadata_value(value) if _metadata_value(value) != "-" else "오버나이트/이월 보유"


def _carry_risk_label(value: Any) -> str:
    key = str(value or "").strip().lower()
    labels = {
        "urgent_exit_review": "장기/주말 이월 후 우선 청산 검토",
        "exit_review": "청산 검토",
        "normal": "일반",
    }
    if key in labels:
        return labels[key]
    text = _metadata_value(value)
    return "" if text == "-" else text


def _translated_metadata(value: Any) -> str:
    return _metadata_value(_translate_text(value))


def _correct_final_operator_summary(summary: str, *, action: Any) -> str:
    text = str(summary or "").strip()
    action_label = str(action or "").strip()
    if not text:
        return ""
    if action_label == "매도":
        return re.sub(r"현재 판단은 진입 유지(?:입니다|이다)\.?", "현재 판단은 청산 완료입니다.", text, count=1)
    if action_label == "매수":
        return re.sub(r"현재 판단은 청산 완료(?:입니다|이다)\.?", "현재 판단은 진입 유지입니다.", text, count=1)
    return text


def _authoritative_final_operator_summary(
    report: Dict[str, Any],
    *,
    action: Any,
    fallback: str = "",
) -> str:
    """Keep the closed-trade conclusion on broker truth, not monitor marks."""

    shared = _as_dict(report.get("shared_facts"))
    truth = _get_truth_surface(report)
    pnl = _as_dict(truth.get("pnl"))
    truth_status = _as_dict(truth.get("status"))
    status = str(truth_status.get("status") or report.get("status") or shared.get("status") or "").lower()
    action_label = str(action or "").strip()
    pnl_value = _num_opt(pnl.get("value"))
    pnl_pct, _ = _operator_pnl_pct_impl(pnl, shared)
    if status != "closed" or action_label != "매도" or (pnl_value is None and pnl_pct is None):
        return _correct_final_operator_summary(fallback, action=action)

    symbol = _clip(report.get("symbol") or shared.get("symbol"), 32) or "해당 종목"
    duration = _authoritative_holding_duration_label(report)
    result_basis = pnl_value if pnl_value is not None else _num_opt(pnl_pct)
    result_label = "이익" if (result_basis or 0.0) > 0 else "손실" if (result_basis or 0.0) < 0 else "보합"
    details: List[str] = []
    if pnl_pct is not None:
        details.append(_fmt_pct(pnl_pct))
    if pnl_value is not None:
        details.append(f"{pnl_value:,.0f}원")
    detail_text = f" ({', '.join(details)})" if details else ""
    duration_text = f"{duration} 보유 후 " if duration else ""
    return (
        f"현재 판단은 청산 완료입니다. {symbol} 거래는 브로커 체결 기준 "
        f"{duration_text}{result_label}{detail_text}로 청산 완료됐습니다. "
        "모니터의 청산 전 시세 관측값은 실제 체결 손익과 구분합니다."
    )


def _selection_fallback_context(selection: Dict[str, Any], traded_symbol: Any = "") -> Dict[str, Any]:
    section = _as_dict(selection)
    trace = _as_dict(section.get("scanner_selection_trace"))
    selected_symbol = _metadata_value(
        traded_symbol
        or section.get("symbol")
        or trace.get("monitor_selected_symbol")
        or trace.get("selected_symbol")
    )
    top_pick = _metadata_value(section.get("scanner_top_pick_symbol") or trace.get("scanner_top_pick_symbol"))
    used = bool(section.get("monitor_fallback_used") or trace.get("monitor_fallback_used"))
    if not top_pick or top_pick == "-":
        used = False
    if top_pick and selected_symbol and top_pick == selected_symbol:
        used = False
    reason_raw = section.get("monitor_fallback_reason") or trace.get("monitor_fallback_reason") or trace.get("monitor_trigger_reason")
    reason = _translate_reason_phrase(str(reason_raw or "")) if reason_raw else ""
    return {
        "used": used,
        "selected_symbol": selected_symbol,
        "scanner_top_pick_symbol": top_pick if top_pick != "-" else "",
        "reason": reason,
        "selection_path": _metadata_value(section.get("selection_path") or trace.get("selection_path")),
    }


def _clip(value: Any, max_len: int = 200) -> str:
    text = str(value or "").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _listify(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


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
    return {
        "as_dict": _as_dict,
        "first_dict": _first_dict,
        "metadata_value": _metadata_value,
        "resolve_entry_monitor_artifact": _resolve_entry_monitor_artifact,
    }

def _resolve_entry_execution_visibility(report: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_entry_execution_visibility_impl(report, deps=_markdown_entry_visibility_deps())

def _first_dict(*items: Dict[str, Any]) -> Dict[str, Any]:
    for item in items:
        if isinstance(item, dict) and item:
            return item
    return {}


def _safe_read_json_object(path_value: Any) -> Dict[str, Any]:
    text = str(path_value or "").strip()
    if not text:
        return {}
    try:
        path = Path(text)
        if not path.exists() or not path.is_file():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _is_entry_monitor_artifact(payload: Dict[str, Any]) -> bool:
    if not payload:
        return False
    focus = _as_dict(payload.get("monitor_focus_context"))
    if bool(payload.get("entry_triggered")) or str(payload.get("entry_decision") or "").upper() == "BUY":
        return True
    if bool(focus.get("entry_triggered")) or str(focus.get("entry_decision") or "").upper() == "BUY":
        return True
    return False


def _canonical_monitor_from_trade_report_path(report: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    paths = _as_dict(report.get("paths"))
    report_path_text = str(paths.get("ai_trade_report_json") or "").strip()
    if not report_path_text or not run_id:
        return {}
    try:
        report_path = Path(report_path_text)
        parts = list(report_path.parts)
        idx = parts.index("trades")
        reports_root = Path(*parts[:idx])
        day = parts[idx + 1]
    except Exception:
        return {}
    return _safe_read_json_object(reports_root / "canonical" / day / run_id / "monitor.json")


def _canonical_monitor_from_section_provenance(report: Dict[str, Any]) -> Dict[str, Any]:
    provenance = _as_dict(report.get("section_provenance"))
    for key in ("entry_decision", "why_this_symbol_was_chosen", "market_context_at_entry"):
        row = _as_dict(provenance.get(key))
        artifact_path = str(row.get("artifact_path") or "").strip()
        if not artifact_path:
            continue
        monitor = _safe_read_json_object(Path(artifact_path).with_name("monitor.json"))
        if _is_entry_monitor_artifact(monitor):
            return monitor
    return {}


def _resolve_entry_monitor_artifact(report: Dict[str, Any]) -> Dict[str, Any]:
    fact_payload = _as_dict(report.get("fact_payload"))
    trade_payload = _as_dict(fact_payload.get("trade"))
    entry_summary = _as_dict(trade_payload.get("entry_summary"))
    entry_monitor = _as_dict(entry_summary.get("monitor_context"))
    if _is_entry_monitor_artifact(entry_monitor):
        return entry_monitor

    entry_run_id = str(entry_summary.get("run_id") or report.get("run_id") or "").strip()
    monitor = _canonical_monitor_from_trade_report_path(report, entry_run_id)
    if _is_entry_monitor_artifact(monitor):
        return monitor

    return _canonical_monitor_from_section_provenance(report)


def _rank_scope_text(row: Dict[str, Any]) -> str:
    if not row:
        return ""
    rank = row.get("max_priority_rank")
    runner_ups = row.get("max_runner_ups")
    if rank in (None, "") and runner_ups in (None, ""):
        return ""
    parts: List[str] = []
    if rank not in (None, ""):
        parts.append(f"rank<={rank}")
    if runner_ups not in (None, ""):
        parts.append(f"runner_ups={runner_ups}")
    return " / ".join(parts)


def _watch_scope_label(row: Dict[str, Any]) -> str:
    if not row:
        return ""
    rank = row.get("max_priority_rank")
    runner_ups = row.get("max_runner_ups")
    parts: List[str] = []
    if rank not in (None, ""):
        parts.append(f"{rank}위까지")
    if runner_ups not in (None, ""):
        parts.append(f"차순위 {runner_ups}개")
    return " / ".join(parts)


def _candidate_watch_reason_label(value: Any) -> str:
    reason = _metadata_value(value)
    if not reason or reason == "-":
        return ""
    mapping = {
        "open_position_present": "보유 포지션 존재",
        "cascade_disabled_by_entry_control": "지휘관 설정으로 차순위 확인 비활성",
        "candidate_watch_disabled": "후보 감시 비활성",
        "entry_control_disabled": "지휘관 진입 제어 비활성",
    }
    return mapping.get(reason, reason)


def _display_candidate_symbol(value: Any) -> str:
    symbol = _metadata_value(value)
    if not symbol or symbol == "-":
        return ""
    return symbol if re.fullmatch(r"\d{6}", symbol) else ""


def _candidate_cascade_symbols(cascade: Dict[str, Any]) -> set[str]:
    symbols: set[str] = set()

    def add(value: Any) -> None:
        symbol = _display_candidate_symbol(value)
        if symbol:
            symbols.add(symbol)

    for key in (
        "top_pick_symbol",
        "fallback_from_symbol",
        "fallback_to_symbol",
        "final_selected_symbol",
    ):
        add(cascade.get(key))
    for key in ("runner_up_symbols", "candidate_symbols"):
        for value in _listify(cascade.get(key)):
            add(value)
    for row in _listify(cascade.get("fallback_trace")):
        row_obj = _as_dict(row)
        add(row_obj.get("symbol"))
    return symbols


def _candidate_cascade_matches_trade(cascade: Dict[str, Any], traded_symbol: Any) -> bool:
    symbol = _display_candidate_symbol(traded_symbol)
    if not symbol or not cascade:
        return True
    cascade_symbols = _candidate_cascade_symbols(cascade)
    if not cascade_symbols:
        return True
    return symbol in cascade_symbols


def _markdown_signal_deps() -> Dict[str, Any]:
    return {
        "as_dict": _as_dict,
        "candidate_cascade_matches_trade": _candidate_cascade_matches_trade,
        "candidate_watch_reason_label": _candidate_watch_reason_label,
        "dedupe": _dedupe,
        "display_candidate_symbol": _display_candidate_symbol,
        "first_present_value": _first_present_value,
        "fmt_multiple": _fmt_multiple,
        "fmt_pct": _fmt_pct,
        "fmt_signed_pct": _fmt_signed_pct,
        "listify": _listify,
        "metadata_value": _metadata_value,
        "normalize_exit_trigger_label": _normalize_exit_trigger_label,
        "num_opt": _num_opt,
        "resolve_entry_execution_visibility": _resolve_entry_execution_visibility,
        "summary_money": _summary_money,
        "truth_source_label": _truth_source_label,
        "watch_scope_label": _watch_scope_label,
    }

def _entry_watch_execution_lines(report: Dict[str, Any], *, require_trade_symbol_match: bool = False) -> List[str]:
    return _entry_watch_execution_lines_impl(report, require_trade_symbol_match=require_trade_symbol_match, deps=_markdown_signal_deps())

def _entry_watch_summary_lines(report: Dict[str, Any], *, require_trade_symbol_match: bool = False) -> List[str]:
    return _entry_watch_summary_lines_impl(report, require_trade_symbol_match=require_trade_symbol_match, deps=_markdown_signal_deps())

def _has_payload(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _merge_preferred(primary: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(fallback or {})
    for key, value in (primary or {}).items():
        if _has_payload(value):
            merged[key] = value
    return merged


def _resolve_market_context(report: Dict[str, Any]) -> Dict[str, Any]:
    primary = _as_dict(report.get("market_context_at_entry"))
    fallback = _as_dict(report.get("market_context_human"))
    trace = _as_dict(report.get("strategist_trace_summary"))
    feedback = _as_dict(report.get("strategist_feedback_input"))
    merged = _merge_preferred(primary, fallback)

    for key in ("summary", "playbook", "themes", "headline_count", "news_query_count"):
        if not _has_payload(merged.get(key)) and _has_payload(trace.get(key)):
            merged[key] = trace.get(key)
    if not _has_payload(merged.get("regime")) and _has_payload(trace.get("market_regime")):
        merged["regime"] = trace.get("market_regime")
    if not _has_payload(merged.get("market_sentiment")) and _has_payload(trace.get("market_sentiment")):
        merged["market_sentiment"] = trace.get("market_sentiment")
    if not _has_payload(merged.get("global_sentiment_score")) and _has_payload(trace.get("global_sentiment_score")):
        merged["global_sentiment_score"] = trace.get("global_sentiment_score")
    if not _has_payload(merged.get("vix_level")) and _has_payload(trace.get("vix_level")):
        merged["vix_level"] = trace.get("vix_level")
    if not _has_payload(merged.get("korea_indices")) and _has_payload(trace.get("korea_indices")):
        merged["korea_indices"] = trace.get("korea_indices")
    if not _has_payload(merged.get("market_news_titles")) and _has_payload(merged.get("strategist_market_headlines")):
        merged["market_news_titles"] = merged.get("strategist_market_headlines")
    if not _has_payload(merged.get("candidate_news_titles")) and _has_payload(merged.get("strategist_symbol_headlines")):
        merged["candidate_news_titles"] = merged.get("strategist_symbol_headlines")
    if not _has_payload(merged.get("market_news_titles")) and _has_payload(report.get("strategist_market_headlines")):
        merged["market_news_titles"] = report.get("strategist_market_headlines")
    if not _has_payload(merged.get("candidate_news_titles")) and _has_payload(report.get("strategist_symbol_headlines")):
        merged["candidate_news_titles"] = report.get("strategist_symbol_headlines")
    if not _has_payload(merged.get("news_symbol_linkage")) and _has_payload(report.get("news_symbol_linkage")):
        merged["news_symbol_linkage"] = report.get("news_symbol_linkage")
    if not _has_payload(merged.get("news_query_targets")) and _has_payload(feedback.get("news_query_targets")):
        merged["news_query_targets"] = feedback.get("news_query_targets")
    if not _has_payload(merged.get("key_events")) and _has_payload(feedback.get("key_events")):
        merged["key_events"] = feedback.get("key_events")
    return merged


def _num_opt(value: Any) -> Optional[float]:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


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
    num = _num_opt(value)
    if num is None:
        return "-"
    sign = "+" if num > 0 else ""
    return f"{sign}{num * 100.0:.2f}%"


def _fmt_multiple(value: Any) -> str:
    num = _num_opt(value)
    if num is None:
        return "-"
    return f"{num:.2f}배"


def _korea_index_lines(context: Dict[str, Any]) -> List[str]:
    packet = _as_dict(context.get("korea_indices"))
    indices = _as_dict(packet.get("indices"))
    lines: List[str] = []
    for name in ("KOSPI", "KOSDAQ"):
        row = _as_dict(indices.get(name))
        if not row:
            continue
        current = _num_opt(row.get("current"))
        previous = _num_opt(row.get("previous_close"))
        change_pct = _num_opt(row.get("change_pct"))
        if current is None and previous is None and change_pct is None:
            continue
        pieces = [name]
        if current is not None:
            pieces.append(f"현재 {current:,.2f}")
        if previous is not None:
            pieces.append(f"전일 {previous:,.2f}")
        if change_pct is not None:
            pieces.append(f"등락률 {change_pct:+.2f}%")
        lines.append(" ".join(pieces))
    return lines


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
    num = _num_opt(value)
    if num is None:
        return "-"
    if abs(num) >= 100:
        return f"{num:,.0f}"
    return f"{num:,.2f}".rstrip("0").rstrip(".")


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
    text = _translate_text(value).strip().rstrip(".")
    if not text and fallback:
        text = _axis_label(fallback)
    text = re.sub(r"^Trigger type:\s*", "", text, flags=re.IGNORECASE).strip()
    patterns = [
        r"청산을 직접 촉발한 신호는\s*(.+?)(?:이었습니다|였습니다|입니다|\.|$)",
        r"핵심 청산 축은\s*(.+?)(?:,|\.|$)",
        r"우선 감시 축은\s*(.+?)(?:이었습니다|였습니다|입니다|\.|$)",
        r"청산 사유는\s*(.+?)(?:입니다|\.|$)",
        r"정규화된 청산 사유는\s*(.+?)(?:입니다|\.|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            text = match.group(1).strip()
            break
    text = text.replace("으로 청산", "").replace("로 청산", "").strip()
    if "고점 대비 하락폭" in text:
        return "고점 대비 하락폭 기준"
    label = _axis_label(text).strip().rstrip(".")
    fallback_label = _axis_label(fallback).strip().rstrip(".") if fallback else ""
    hold_labels = {"hold", "보유 유지", "보유 유지입니다", "현재 포지션 판단은 보유 유지입니다"}
    if label in hold_labels and fallback_label and fallback_label not in hold_labels:
        return fallback_label
    return label or _axis_label(fallback) or "-"


def _extract_exit_signal_snapshot(values: Iterable[Any]) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {}

    def _set_number(key: str, raw: Any) -> None:
        if key in snapshot:
            return
        num = _number_from_text(raw)
        if num is not None:
            snapshot[key] = num

    for raw in values:
        text = _translate_text(raw).strip()
        if not text:
            continue

        if "trigger" not in snapshot and any(
            token in text for token in ("촉발", "Trigger type", "핵심 청산 축", "우선 감시 축", "청산 사유", "peak_drawdown", "고점 대비")
        ):
            trigger = _normalize_exit_trigger_label(text)
            if trigger and trigger != "-":
                snapshot["trigger"] = trigger

        if match := re.search(
            r"현재가,\s*평균가,\s*고점 기준 값은\s*([+-]?[0-9,.]+)\s*/\s*([+-]?[0-9,.]+)\s*/\s*([+-]?[0-9,.]+)",
            text,
        ):
            _set_number("monitor_current_price", match.group(1))
            _set_number("position_avg_price", match.group(2))
            _set_number("peak_price", match.group(3))

        if match := re.search(r"현재가(?:는|:)?\s*([+-]?[0-9,.]+)", text):
            _set_number("monitor_current_price", match.group(1))
        if match := re.search(r"평균가(?:는|:)?\s*([+-]?[0-9,.]+)", text):
            _set_number("position_avg_price", match.group(1))
        if match := re.search(r"고점(?:은|:)?\s*([+-]?[0-9,.]+)", text):
            _set_number("peak_price", match.group(1))
        if match := re.search(r"확인 조건(?:은|:)?\s*([0-9]+\s*/\s*[0-9]+)", text):
            snapshot.setdefault("confirm_state", re.sub(r"\s+", "", match.group(1)))
        if match := re.search(r"현재 손익 변동(?:은|:)?\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*%", text):
            snapshot.setdefault("monitor_drawdown_pct_text", f"{match.group(1)}%")

    if snapshot:
        snapshot.setdefault("basis", "monitor_signal_snapshot")
        snapshot.setdefault("truth_note", "체결가와 실현손익은 Truth Surface 기준입니다.")
    return snapshot


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
    raw = html.unescape(_clip(text, 300))
    if not raw:
        return ""
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = raw.replace("NewsItem(title='", "")
    raw = raw.split("', url='", 1)[0]
    return re.sub(r"\s+", " ", raw).strip()


def _clean_news_title(text: Any) -> str:
    return _strip_html_tags(text).rstrip(".")


def _sample_news_titles(values: Any, limit: int = 2) -> List[str]:
    out: List[str] = []
    seen = set()
    for raw in _listify(values):
        cleaned = _clean_news_title(raw)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        out.append(cleaned)
        if len(out) >= limit:
            break
    return out


def _normalize_news_symbol(value: Any) -> str:
    if value is None:
        return ""
    match = re.search(r"\b(\d{6})\b", str(value))
    return match.group(1) if match else ""


def _news_symbol_from_item(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("symbol", "code", "stock_code", "ticker"):
            symbol = _normalize_news_symbol(value.get(key))
            if symbol:
                return symbol
        return ""
    raw = str(value or "")
    match = re.match(r"\s*(\d{6})\s*:", raw)
    if match:
        return match.group(1)
    match = re.search(r"\bsymbol=['\"]?(\d{6})['\"]?", raw)
    return match.group(1) if match else ""


def _sample_news_titles_for_symbol(symbol: Any, *sources: Any, limit: int = 2) -> List[str]:
    target = _normalize_news_symbol(symbol)
    untagged_fallback: List[Any] = []
    for source in sources:
        rows = _listify(source)
        if not rows:
            continue
        if not target:
            return _sample_news_titles(rows, limit=limit)
        matched: List[Any] = []
        has_detectable_symbol = False
        for row in rows:
            row_symbol = _news_symbol_from_item(row)
            if row_symbol:
                has_detectable_symbol = True
            if row_symbol == target:
                matched.append(row)
        if matched:
            return _sample_news_titles(matched, limit=limit)
        if not has_detectable_symbol and not untagged_fallback:
            # Curated symbol-only headline lists may omit the code prefix.
            untagged_fallback = rows
    if untagged_fallback:
        return _sample_news_titles(untagged_fallback, limit=limit)
    return []


def _mismatched_symbol_news_bullet(text: Any, symbol: Any) -> bool:
    target = _normalize_news_symbol(symbol)
    if not target:
        return False
    raw = str(text or "")
    if "대표 종목/섹터 뉴스" not in raw and "종목 뉴스" not in raw:
        return False
    symbols = set(re.findall(r"\b(\d{6})\s*:", raw))
    return bool(symbols and target not in symbols)


def _news_linkage_strength_label(value: Any) -> str:
    lowered = _clip(value, 40).lower()
    return {
        "weak": "약한 편이었습니다",
        "moderate": "보통 수준이었습니다",
        "strong": "강한 편이었습니다",
    }.get(lowered, _metadata_value(value) or "-")


def _badge(label: str, color: str) -> str:
    return f"**[{label}]**"


def _metadata_value(value: Any) -> str:
    raw = _clip(value, 240)
    lowered = raw.lower()
    if not raw:
        return ""
    if lowered in {"unknown", "not available", "not_available", "unavailable"}:
        return "확인되지 않음"
    if lowered in {"not captured", "not_captured"}:
        return "기록되지 않음"
    if lowered in {"allowed", "allow"}:
        return "허용"
    if lowered in {"approve", "approved"}:
        return "승인"
    if lowered == "broad_market_leaders":
        return "시장 대표주"
    if lowered == "illiquid_microcap":
        return "유동성 낮은 초소형주"
    if lowered == "headline_only_momentum":
        return "헤드라인 추격형 모멘텀"
    if lowered == "high_gap_speculative":
        return "갭 과열 투기형"
    if lowered == "neutral":
        return "중립"
    if lowered == "bullish":
        return "강세"
    if lowered == "bearish":
        return "약세"
    if lowered == "strong":
        return "강함"
    if lowered == "weak":
        return "약함"
    if lowered == "high":
        return "높음"
    if lowered == "medium":
        return "보통"
    if lowered == "low":
        return "낮음"
    return raw


def _story_type_label(value: Any) -> str:
    lowered = _clip(value, 80).lower()
    return {
        "simulation trade report": "시뮬레이션 거래 리포트",
        "simulation": "시뮬레이션 거래 리포트",
        "live trade report": "실거래 거래 리포트",
        "live": "실거래 거래 리포트",
    }.get(lowered, _metadata_value(value) or "-")


def _execution_mode_label(value: Any) -> str:
    lowered = _clip(value, 80).lower()
    return {
        "simulation (mock broker)": "시뮬레이션 (모의 브로커)",
        "real broker": "실브로커",
        "live": "실거래",
    }.get(lowered, _metadata_value(value) or "-")


def _action_label(value: Any) -> str:
    lowered = _clip(value, 40).upper()
    return {
        "BUY": "매수",
        "SELL": "매도",
        "HOLD": "보유 유지",
        "WAIT": "진입 보류",
    }.get(lowered, _metadata_value(value) or "-")


def _status_label(value: Any) -> str:
    lowered = _clip(value, 40).lower()
    return {
        "open": "열림",
        "closed": "종결",
        "ok": "정상",
    }.get(lowered, _metadata_value(value) or "-")


def _axis_label(value: Any) -> str:
    raw = _clip(value, 120)
    if raw.lower().startswith("sell was triggered because "):
        raw = raw[len("SELL was triggered because ") :].strip().rstrip(".")
    lowered = raw.lower().replace("-", "_").replace(" ", "_")
    mapping = {
        "hard_stop": "고정 손절 기준",
        "stop_loss": "고정 손절 기준",
        "adaptive_stop": "상황 적응형 손절 기준",
        "take_profit": "목표 수익 실현 기준",
        "partial_take_profit": "1차 일부 익절",
        "profit_ladder": "구간별 분할 익절",
        "risk/reward_take_profit": "손익비 익절",
        "risk_reward_take_profit": "손익비 익절",
        "vwap_extension_take_profit": "VWAP 과확장 익절",
        "resistance_take_profit": "저항권 익절",
        "volume_exhaustion_take_profit": "거래량 둔화 익절",
        "opening_gap_profit_take": "갭 추격 빠른 익절",
        "time_decay_profit_exit": "시간 경과 수익 보전",
        "trailing_stop": "추적 손절 기준",
        "vwap_breakdown": "VWAP 이탈",
        "peak_drawdown": "고점 대비 하락폭 기준",
        "prior_low_break": "직전 저점 이탈",
        "intraday_low_break": "장중 저점 이탈 기준",
        "below_vwap_reclaim_not_ready": "VWAP 재회복 미완료",
        "exit_trigger_not_captured": "모니터 청산 트리거 미확인",
        "monitor_exit_trigger_not_captured": "모니터 청산 트리거 미확인",
        "sell_execution_confirmed": "모니터 청산 트리거 미확인",
        "full_sell_quantity_reconciled": "모니터 청산 트리거 미확인",
        "confirmed_exit_signal": "청산 확인 신호",
        "defensive_exit": "방어적 청산 신호",
        "trend_breakdown": "추세 붕괴 기준",
        "volatility_expansion": "변동성 확장 기준",
        "no_trigger_yet": "아직 청산 신호가 확인되지 않음",
    }
    return mapping.get(lowered, raw or "-")


def _markdown_translation_deps() -> Dict[str, Any]:
    return {
        "action_label": _action_label,
        "axis_label": _axis_label,
        "clip": _clip,
        "metadata_value": _metadata_value,
        "translate_reason_phrase": _translate_reason_phrase,
    }

def _translate_text(text: Any) -> str:
    return _translate_text_impl(text, deps=_markdown_translation_deps())

def _bullet_lines(section: Dict[str, Any], *, skip_prefixes: Iterable[str] = ()) -> List[str]:
    lines: List[str] = []
    for raw in _listify(section.get("bullets")):
        text = _translate_text(raw)
        if not text:
            continue
        if _looks_corrupted(text):
            continue
        lowered = text.lower()
        if any(lowered.startswith(prefix.lower()) for prefix in skip_prefixes):
            continue
        lines.append(f"- {text}")
    return lines


def _section_summary(section: Dict[str, Any]) -> str:
    summary = _translate_text(section.get("summary"))
    if _looks_corrupted(summary):
        return ""
    return summary


def _build_generation_info(report: Dict[str, Any]) -> List[str]:
    generation = _as_dict(report.get("generation"))
    lines = [
        f"- 생성 상태: {_metadata_value(generation.get('status') or '-')}",
        f"- 생성 방식: {_metadata_value(generation.get('mode') or '-')}",
        f"- 사용 모델: {_metadata_value(generation.get('model') or '-')}",
    ]
    if report.get("generated_at"):
        lines.append(f"- 생성 시각: {_clip(report.get('generated_at'), 80)}")
    reason = _metadata_value(generation.get("reason"))
    if reason:
        lines.append(f"- 생성 사유: {reason}")
    return lines


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
    raw = _clip(value, 80).lower()
    mapping = {
        "daily": "당일",
        "weekly": "주간",
        "monthly": "월간",
        "symbol": "종목",
    }
    return mapping.get(raw, _metadata_value(value) or "-")


def _authority_label(value: Any) -> str:
    return "확정 기준" if value else "참고 기준"


def _risk_mode_label(value: Any) -> str:
    raw = _clip(value, 80).lower()
    return {
        "balanced": "균형형",
        "defensive": "방어형",
        "aggressive": "공격형",
        "normal": "보통",
    }.get(raw, _metadata_value(value) or "-")


def _theme_label(value: Any) -> str:
    raw = _clip(value, 120).lower()
    mapping = {
        "broad_market_leaders": "시장 대표주",
        "illiquid_microcap": "유동성 낮은 초소형주",
        "headline_only_momentum": "헤드라인 추격형 모멘텀",
        "high_gap_speculative": "갭 과열 투기형",
        "counter_trend_low_liquidity": "역추세 저유동성 종목",
        "defensive_assets": "방어 자산군",
    }
    return mapping.get(raw, _metadata_value(value) or "-")


def _policy_token_label(value: Any) -> str:
    raw = _clip(value, 120)
    lower = raw.lower()
    mapping = {
        "reclaim_gate_ok": "VWAP 재회복 확인",
        "extension_ok": "과열 이격 제한 통과",
        "confidence_ok": "신뢰도 기준 통과",
        "trend_regime=transition": "추세 전환 구간 확인",
        "structure_range_compression=moderate": "가격 압축이 중간 수준",
        "volume_ok": "거래량 확인",
        "breakout_ok": "돌파 확인",
        "pullback_ok": "눌림목 구조 확인",
        "failed_breakout=confirmed": "실패 돌파가 확인된 상태",
        "momentum_decay=strong": "모멘텀 둔화가 강한 상태",
        "vwap_reclaim_required": "VWAP 재회복 확인을 우선 조건으로 둠",
        "monitor_guidance:defensive_exit": "방어적 청산 안내 유지",
        "trade_aggressiveness:medium": "진입 강도는 중간 수준",
    }
    return mapping.get(lower, _metadata_value(value) or "-")


def _is_not_captured(value: Any) -> bool:
    raw = _clip(value, 80).lower()
    return raw in {"", "-", "not_captured", "not captured", "unknown", "unavailable"}


def _is_closed_trade_context(report: Dict[str, Any]) -> bool:
    status = _clip(report.get("status"), 20).lower()
    if status == "closed":
        return True
    shared = _as_dict(report.get("shared_facts"))
    monitor = _as_dict(report.get("monitor_snapshot"))
    action = _clip(shared.get("action") or report.get("action"), 20).upper()
    if action == "SELL" and monitor.get("trigger_type"):
        return True
    return False


def _memory_status_label(value: Any) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "ok": "정상 기록",
        "not_recorded": "미기록",
        "missing": "미기록",
        "empty": "비어 있음",
        "auto_ignored": "자동 제외",
        "error": "오류",
    }
    return mapping.get(raw, _metadata_value(value) or "-")


def _markdown_truth_surface_deps() -> Dict[str, Any]:
    return {
        "as_dict": _as_dict,
        "authority_label": _authority_label,
        "badge": _badge,
        "fmt_pct": _fmt_pct,
        "fmt_price": _fmt_price,
        "get_truth_surface": _get_truth_surface,
        "metadata_value": _metadata_value,
        "num_opt": _num_opt,
        "trade_cost_analysis_lines": _trade_cost_analysis_lines,
        "truth_source_label": _truth_source_label,
    }

def _build_truth_surface(report: Dict[str, Any]) -> List[str]:
    return _build_truth_surface_impl(report, deps=_markdown_truth_surface_deps())

def _memory_layers_text(values: Any, *, arrow: bool = False, humanize: bool = True) -> str:
    items = [str(x).strip() for x in _listify(values) if str(x).strip()]
    if not items:
        return "-"
    if humanize:
        items = [_memory_layer_label(x) for x in items]
    return " -> ".join(items) if arrow else ", ".join(items)


def _memory_packet_state_line(name: str, packet: Dict[str, Any]) -> str:
    status = _memory_status_label(packet.get("status") or "not_recorded")
    parts = [status]
    sample_day_count = packet.get("sample_day_count")
    if name in {"weekly", "monthly"} and sample_day_count not in (None, ""):
        parts.append(f"{sample_day_count}days")
    parts.append("활성" if packet.get("active") else "보조 참고")
    return f"{_memory_layer_label(name)}=" + ", ".join(parts)


def _on_off_label(value: Any) -> str:
    return "켜짐" if bool(value) else "꺼짐"


def _applied_label(value: Any) -> str:
    return "적용됨" if bool(value) else "미적용"


def _policy_phase_line(label: str, policy: Dict[str, Any]) -> str:
    active_layers = _memory_layers_text(policy.get("active_layers"))
    priority_order = _memory_layers_text(policy.get("priority_order"), arrow=True)
    scanner_bias = _on_off_label(policy.get("scanner_bias_enabled"))
    monitor_bias = _on_off_label(policy.get("monitor_bias_enabled"))
    symbol_override = _on_off_label(policy.get("symbol_memory_override_enabled"))
    application_mode = _metadata_value(policy.get("application_mode") or "-")
    return (
        f"- [{label}] 활성 레이어={active_layers}; 우선순위={priority_order}; "
        f"scanner bias={scanner_bias}; monitor bias={monitor_bias}; "
        f"symbol override={symbol_override}; 적용 모드={application_mode}."
    )


def _same_policy_snapshot(left: Dict[str, Any], right: Dict[str, Any]) -> bool:
    keys = (
        "active_layers",
        "priority_order",
        "scanner_bias_enabled",
        "monitor_bias_enabled",
        "symbol_memory_override_enabled",
        "application_mode",
    )
    return all(left.get(key) == right.get(key) for key in keys)


def _scanner_phase_line(scanner: Dict[str, Any]) -> str:
    source = _metadata_value(scanner.get("source") or "-")
    active_layers = _memory_layers_text(scanner.get("active_layers"))
    not_applied = _metadata_value(scanner.get("not_applied_reason") or "")
    suffix = f"; 미적용 사유={not_applied}" if not_applied else ""
    return (
        f"- [스캐너 적용 시점] captured={_on_off_label(scanner.get('captured'))}; "
        f"enabled={_on_off_label(scanner.get('enabled'))}; "
        f"applied={_applied_label(scanner.get('applied'))}; "
        f"active_layers={active_layers}; source={source}{suffix}."
    )


def _monitor_phase_line(monitor: Dict[str, Any]) -> str:
    source = _metadata_value(monitor.get("source") or "-")
    active_layers = _memory_layers_text(monitor.get("active_layers"))
    not_applied = _metadata_value(monitor.get("not_applied_reason") or "")
    suffix = f"; 미적용 사유={not_applied}" if not_applied else ""
    return (
        f"- [모니터 적용 시점] captured={_on_off_label(monitor.get('captured'))}; "
        f"enabled={_on_off_label(monitor.get('enabled'))}; "
        f"entry={_applied_label(monitor.get('applied'))}; "
        f"hold={_applied_label(monitor.get('hold_applied'))}; "
        f"exit={_applied_label(monitor.get('exit_applied'))}; "
        f"active_layers={active_layers}; source={source}{suffix}."
    )


def _playbook_label(value: Any) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "defensive": "방어형",
        "breakout": "돌파형",
        "pullback": "눌림목형",
        "reclaim": "재회복형",
        "leader": "주도주형",
        "balanced": "균형형",
        "normal": "정상",
        "neutral": "중립",
        "aggressive": "공격형",
    }
    return mapping.get(raw, _metadata_value(value) or "-")


def _monitor_guidance_label(value: Any) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "defensive_exit": "방어적 청산 안내",
        "normal_exit": "일반 청산 안내",
        "hold_bias": "보유 우선 안내",
    }
    return mapping.get(raw, _metadata_value(value) or "-")


def _scanner_bias_label(value: Any) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "leader": "주도주 우선",
        "balanced": "균형형",
        "defensive": "방어형",
    }
    return mapping.get(raw, _metadata_value(value) or "-")


def _policy_source_label(value: Any) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "monitor_memory_bias_adjusted": "메모리 조정 반영 정책",
        "baseline_monitor_policy": "기본 모니터 정책",
    }
    return mapping.get(raw, _metadata_value(value) or "-")


def _failure_label(value: Any) -> str:
    raw = _clip(value, 120)
    lower = raw.lower()
    if lower.startswith("playbook:"):
        return f"{_playbook_label(lower.split(':', 1)[1])} 전략 프레임 실패"
    return _metadata_value(value) or "-"


def _reason_tag_summary(tag: str) -> str:
    raw = _clip(tag, 160)
    lower = raw.lower()
    mapping = {
        "daily_strategy_memory_available": "당일 전략 메모리를 사용할 수 있었습니다",
        "daily_prefers_pullback_or_defensive": "당일 메모리는 눌림목/방어형 접근을 선호했습니다",
        "scanner_bias_disabled": "메모리 bias가 비활성화되어 점수 조정에 쓰이지 않았습니다",
        "monitor_bias_disabled": "메모리 bias가 비활성화되어 진입/청산 정책 조정에 쓰이지 않았습니다",
        "commander_monitor_status:stable": "모니터 상태는 안정적이었습니다",
        "commander_focus:exit_quality": "지휘관은 청산 품질 점검을 우선했습니다",
        "commander_focus:guard_blocks": "지휘관은 가드 차단 패턴 점검을 우선했습니다",
        "commander_focus:scanner_fit": "지휘관은 스캐너 적합도 점검을 우선했습니다",
        "symbol_blocker:unknown": "종목별 반복 차단 패턴은 아직 뚜렷하지 않았습니다",
    }
    if lower in mapping:
        return mapping[lower]
    if lower.startswith("daily_best:"):
        return f"당일 메모리는 {_playbook_label(lower.split(':', 1)[1])} 전략 프레임을 우세 신호로 봤습니다"
    if lower.startswith("daily_failure:playbook:"):
        return f"당일 메모리에는 {_playbook_label(lower.split(':', 2)[2])} 전략 프레임 실패 흔적이 남았습니다"
    if lower.startswith("commander_risk_posture:"):
        return f"지휘관 위험 자세는 {_playbook_label(lower.split(':', 1)[1])}이었습니다"
    if lower.startswith("symbol_playbook:"):
        return f"종목 메모리는 {_playbook_label(lower.split(':', 1)[1])} 접근 이력을 보였습니다"
    return _metadata_value(tag) or "-"


def _reason_summary_line(tags: List[Any], prefix: str) -> Optional[str]:
    phrases: List[str] = []
    seen = set()
    for raw in tags:
        text = _reason_tag_summary(str(raw))
        if text and text not in seen:
            seen.add(text)
            phrases.append(text)
    if not phrases:
        return None
    return f"- {prefix} {', '.join(phrases[:4])}."


def _reporter_source_label(source_reports: Dict[str, Any]) -> str:
    if source_reports.get("trade_reports"):
        return "same-day closed trade reports"
    if source_reports.get("reporter_analysis"):
        return "same-day reporter_analysis"
    if source_reports.get("metrics"):
        return "same-day metrics"
    if source_reports.get("trade_explain"):
        return "same-day trade explain"
    if source_reports.get("current_payload"):
        return "current payload"
    return "not_recorded"


def _humanize_reporter_source_label(source_reports: Dict[str, Any]) -> str:
    raw = _reporter_source_label(source_reports)
    mapping = {
        "same-day closed trade reports": "당일 닫힌 거래 리포트",
        "same-day reporter_analysis": "당일 reporter_analysis",
        "same-day metrics": "당일 metrics",
        "same-day trade explain": "당일 trade explain",
        "current payload": "현재 payload",
        "not_recorded": "기록되지 않은 소스",
    }
    return mapping.get(raw, _translate_text(raw))


def _resolve_prompt_proven_surface(memory: Dict[str, Any]) -> Dict[str, Any]:
    prompt = _as_dict(memory.get("prompt_proven"))
    if prompt:
        return prompt
    strategy_memory = _as_dict(memory.get("strategy_memory"))
    memory_packets = _as_dict(memory.get("memory_packets"))
    commander_memory_policy = _as_dict(memory.get("commander_memory_policy"))
    selected_symbol_memory = _as_dict(memory.get("selected_symbol_memory"))
    reporter_feedback_packet = _as_dict(memory.get("reporter_feedback_packet"))
    read_model_facts = _as_dict(memory.get("read_model_facts"))
    selected_trade_count = _num_opt(selected_symbol_memory.get("trade_count"))
    recent_trade_count = _num_opt(read_model_facts.get("recent_trade_count"))
    symbol_pattern_count = _num_opt(read_model_facts.get("symbol_pattern_count"))

    strategy_memory_present = bool(
        strategy_memory.get("present")
        or strategy_memory.get("status")
        or _listify(strategy_memory.get("best_playbooks"))
        or _listify(strategy_memory.get("worst_playbooks"))
        or _listify(strategy_memory.get("recent_failures"))
    )
    commander_memory_policy_present = bool(
        commander_memory_policy.get("present")
        or _listify(commander_memory_policy.get("active_layers"))
        or _listify(commander_memory_policy.get("priority_order"))
        or commander_memory_policy.get("application_mode")
    )
    selected_symbol_memory_present = bool(
        selected_symbol_memory.get("present")
        or (selected_trade_count is not None and selected_trade_count > 0)
        or selected_symbol_memory.get("dominant_playbook")
        or selected_symbol_memory.get("dominant_monitor_blocker")
    )
    reporter_feedback_present = bool(
        reporter_feedback_packet.get("present")
        or reporter_feedback_packet.get("available")
        or reporter_feedback_packet.get("status")
        or reporter_feedback_packet.get("confidence")
        or _as_dict(reporter_feedback_packet.get("source_reports"))
        or _as_dict(reporter_feedback_packet.get("trade_report_analysis"))
        or _listify(reporter_feedback_packet.get("recommendation"))
    )
    read_model_facts_present = bool(
        read_model_facts.get("present")
        or (recent_trade_count is not None and recent_trade_count > 0)
        or (symbol_pattern_count is not None and symbol_pattern_count > 0)
        or read_model_facts.get("daily_summary_present")
        or _listify(read_model_facts.get("symbols"))
    )
    return {
        "status": {
            "strategy_memory_present": strategy_memory_present,
            "memory_packets_present": bool(memory_packets),
            "commander_memory_policy_present": commander_memory_policy_present,
            "selected_symbol_memory_present": selected_symbol_memory_present,
            "reporter_feedback_present": reporter_feedback_present,
            "reporter_feedback_available": bool(reporter_feedback_packet.get("available")),
            "reporter_feedback_consumed": bool(reporter_feedback_packet.get("consumed")),
            "read_model_facts_present": read_model_facts_present,
        },
        "strategy_memory": strategy_memory,
        "memory_packets": memory_packets,
        "commander_memory_policy": commander_memory_policy,
        "selected_symbol_memory": selected_symbol_memory,
        "reporter_feedback_packet": reporter_feedback_packet,
        "read_model_facts": read_model_facts,
    }


def _resolve_reconstructed_memory_surface(memory: Dict[str, Any]) -> Dict[str, Any]:
    reconstructed = _as_dict(memory.get("reconstructed_trade_context"))
    if reconstructed:
        return reconstructed
    return {
        "status": {
            "selected_symbol_memory_rebuilt": False,
            "reporter_feedback_rebuilt": False,
            "memory_packets_rebuilt": False,
            "commander_memory_policy_rebuilt": False,
        },
        "selected_symbol_memory": dict(_as_dict(memory.get("selected_symbol_memory")), rebuilt=False, source="prompt_proven"),
        "reporter_feedback_packet": dict(_as_dict(memory.get("reporter_feedback_packet")), rebuilt=False, source="prompt_proven"),
        "memory_packets": {"rebuilt": False, "source": "prompt_proven"},
        "commander_memory_policy": dict(_as_dict(memory.get("commander_memory_policy")), rebuilt=False, source="prompt_proven"),
        "notes": [],
    }


def _build_prompt_proven_memory(report: Dict[str, Any]) -> List[str]:
    return _build_prompt_proven_memory_impl(report, deps=_strategy_memory_deps())

def _build_reconstructed_trade_memory(report: Dict[str, Any]) -> List[str]:
    memory = _as_dict(report.get("memory_surface"))
    if not memory:
        return []
    reconstructed = _resolve_reconstructed_memory_surface(memory)
    status = _as_dict(reconstructed.get("status"))
    selected = _as_dict(reconstructed.get("selected_symbol_memory"))
    reporter = _as_dict(reconstructed.get("reporter_feedback_packet"))
    policy = _as_dict(reconstructed.get("commander_memory_policy"))
    lines: List[str] = []
    symbol = _metadata_value(report.get("symbol") or selected.get("symbol") or "target_symbol")

    lines.append(f"- {_badge('사후 복원', '#7c3aed')} 실행 기록을 다시 읽어 {symbol} 거래 설명에 필요한 메모리만 보강했습니다.")

    if any(bool(status.get(key)) for key in status):
        lines.append(f"- 전략가 원본 프롬프트 밖의 거래 레벨 메모리를 기준으로 {symbol} 거래 문맥을 보강했습니다.")
    else:
        lines.append("- 이 거래는 전략가 프롬프트만으로 대부분 설명돼, 사후 메모리 복원은 크지 않았습니다.")

    if bool(status.get("selected_symbol_memory_rebuilt")) and selected.get("present"):
        trade_count = selected.get("trade_count") if selected.get("trade_count") not in (None, "") else "-"
        win_rate = selected.get("win_rate")
        lines.append(
            f"- {symbol} 종목 메모리는 저장된 종목 메모리에서 다시 읽었고, 과거 거래 {trade_count}건, 승률 {_fmt_pct(win_rate) if win_rate not in (None, '') else '-'}였습니다."
        )

    if bool(status.get("reporter_feedback_rebuilt")) and reporter.get("available"):
        source_label = _humanize_reporter_source_label(_as_dict(reporter.get("source_reports")))
        analysis = _as_dict(reporter.get("trade_report_analysis"))
        lines.append(
            f"- 당일 리포터 피드백은 {source_label}를 기준으로 다시 구성했고, 닫힌 거래 {analysis.get('closed_trade_count') if analysis.get('closed_trade_count') not in (None, '') else '-'}건 집계를 반영했습니다."
        )
        recommendation = ""
        for item in _listify(reporter.get("recommendation")):
            recommendation = _humanize_reporter_recommendation(item)
            if recommendation:
                break
        if recommendation:
            lines.append(f"- 사후 복원된 리포터 권고는 {_ensure_sentence(recommendation)}")

    if bool(status.get("memory_packets_rebuilt")):
        lines.append("- 전략가 원본 프롬프트에 메모리 묶음 세부 정보가 부족해, 실행 시점 메모리 묶음 문맥을 다시 구성했습니다.")
    if bool(status.get("commander_memory_policy_rebuilt")):
        lines.append(
            f"- 지휘관 메모리 정책도 실행 기록을 기준으로 다시 구성했고, 실제 반영 레이어는 {_memory_layers_text(policy.get('active_layers'))}으로 확인됐습니다."
        )

    if any(bool(status.get(key)) for key in status):
        lines.append("- 전략가 원본 프롬프트를 옮긴 내용이 아니라, 거래 설명용으로 사후 복원한 메모리 레이어입니다.")
    return lines

def _build_memory_application(report: Dict[str, Any]) -> List[str]:
    return _build_memory_application_impl(report, deps=_strategy_memory_deps())

def _market_context_structured_lines(context: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for raw in _listify(context.get("bullets")):
        raw_text = _clip(raw, 240)
        if not raw_text:
            continue
        lowered = raw_text.lower()
        if lowered.startswith("global sentiment "):
            value = raw_text.split(" ", 2)[-1].strip()
            lines.append(f"- 시장 심리 수치는 {value}입니다.")
            continue
        if lowered.startswith("global_sentiment score="):
            match = re.search(r"score=([-+]?\\d+(?:\\.\\d+)?)", raw_text, re.I)
            if match:
                lines.append(f"- 시장 심리 수치는 {match.group(1)}입니다.")
            continue
        if lowered.startswith("vix "):
            lines.append(f"- {raw_text}")
            continue
        if lowered.startswith("stress flags:"):
            flags = raw_text.split(":", 1)[1].strip()
            if flags:
                lines.append(f"- 스트레스 신호는 {flags}입니다.")
            continue
        if lowered.startswith("news input:"):
            match = re.search(
                r"(\d+)\s+headlines were considered across\s+(\d+)\s+targets\s+\((\d+)\s+market\s*/\s*(\d+)\s+candidate signals\)\.?",
                raw_text,
                re.I,
            )
            if match:
                lines.append(
                    f"- 뉴스 입력은 {match.group(2)}개 타깃에서 {match.group(1)}개 headline을 검토했고, 시장 {match.group(3)}건 / 후보 {match.group(4)}건 신호를 반영했습니다."
                )
            else:
                lines.append(f"- 뉴스 입력 요약: {raw_text.split(':', 1)[1].strip()}")
            continue
    return lines


def _market_context_summary_from_raw(summary: Any) -> str:
    raw = _clip(summary, 400)
    if not raw:
        return ""
    lowered = raw.lower()
    if "regime" not in lowered and "market sentiment" not in lowered and "playbook" not in lowered:
        return ""
    regime_match = re.search(r"([A-Za-z_-]+)\s+Regime", raw, re.I)
    sentiment_match = re.search(r"([A-Za-z_-]+)\s+Market Sentiment", raw, re.I)
    playbook_match = re.search(r"([A-Za-z_-]+)\s+playbook", raw, re.I)
    regime = regime_match.group(1) if regime_match else "-"
    sentiment = sentiment_match.group(1) if sentiment_match else "-"
    playbook = playbook_match.group(1) if playbook_match else "-"
    return f"- 시장 상태는 {regime}, 시장 심리는 {sentiment}, 선택 플레이북은 {playbook}입니다."


def _markdown_strategy_deps() -> Dict[str, Any]:
    return {
        "append_strategy_output_line": _append_strategy_output_line,
        "as_dict": _as_dict,
        "clip": _clip,
        "dedupe": _dedupe,
        "entry_watch_execution_lines": _entry_watch_execution_lines,
        "is_not_captured": _is_not_captured,
        "korea_index_lines": _korea_index_lines,
        "listify": _listify,
        "looks_corrupted": _looks_corrupted,
        "market_context_structured_lines": _market_context_structured_lines,
        "market_context_summary_from_raw": _market_context_summary_from_raw,
        "memory_layers_text": _memory_layers_text,
        "metadata_value": _metadata_value,
        "mismatched_symbol_news_bullet": _mismatched_symbol_news_bullet,
        "news_linkage_strength_label": _news_linkage_strength_label,
        "noun_predicate_was": _noun_predicate_was,
        "num_opt": _num_opt,
        "playbook_label": _playbook_label,
        "policy_token_label": _policy_token_label,
        "rank_scope_text": _rank_scope_text,
        "resolve_market_context": _resolve_market_context,
        "resolve_strategist_output_surface": _resolve_strategist_output_surface,
        "risk_mode_label": _risk_mode_label,
        "sample_news_titles": _sample_news_titles,
        "sample_news_titles_for_symbol": _sample_news_titles_for_symbol,
        "section_summary": _section_summary,
        "strategy_output_layer_bits": _strategy_output_layer_bits,
        "strategy_output_list_text": _strategy_output_list_text,
        "strategy_output_text": _strategy_output_text,
        "theme_label": _theme_label,
        "translate_text": _translate_text,
    }

def _build_market_context(report: Dict[str, Any]) -> List[str]:
    return _build_market_context_impl(report, deps=_markdown_strategy_deps())

def _build_strategist_summary(report: Dict[str, Any]) -> List[str]:
    return _build_strategist_summary_impl(report, deps=_markdown_strategy_deps())

def _resolve_strategist_output_surface(report: Dict[str, Any]) -> Dict[str, Any]:
    direct = _as_dict(report.get("strategist_output") or report.get("strategist_output_surface"))
    if direct:
        return direct
    strategist = _as_dict(report.get("strategist_summary"))
    nested = _as_dict(strategist.get("strategist_output"))
    if nested:
        return nested
    visibility = _resolve_entry_execution_visibility(report)
    proposal = _as_dict(visibility.get("strategy_candidate_watch_proposal"))
    entry_control = _as_dict(visibility.get("commander_entry_control"))
    if not proposal and not entry_control:
        return {}

    strategy_detail: Dict[str, Any] = {}
    tactical = _metadata_value(proposal.get("tactical_strategy"))
    if tactical and tactical != "-":
        strategy_detail["tactical_strategy"] = tactical
    if proposal:
        strategy_detail["candidate_watch_policy"] = proposal

    thesis: Dict[str, Any] = {}
    playbook = _metadata_value(
        strategist.get("selected_playbook")
        or strategist.get("playbook")
        or _as_dict(report.get("market_context")).get("selected_playbook")
    )
    risk_tone = _metadata_value(
        strategist.get("risk_tone")
        or _as_dict(report.get("market_context")).get("risk_mode")
        or _as_dict(report.get("market_context")).get("risk_tone")
    )
    if playbook and playbook != "-":
        thesis["selected_playbook"] = playbook
    if risk_tone and risk_tone != "-":
        thesis["risk_tone"] = risk_tone

    out: Dict[str, Any] = {}
    if thesis:
        out["strategy_thesis"] = thesis
    if strategy_detail:
        out["strategy_detail"] = strategy_detail
    return out


def _operatorize_strategist_output_text(value: Any) -> str:
    text = _metadata_value(value)
    if not text:
        return ""
    replacements = (
        ("defensive frame", "방어형 전략 프레임"),
        ("pullback frame", "눌림목 전략 프레임"),
        ("breakout frame", "돌파 전략 프레임"),
        (" with ", " / "),
        ("normal risk tone", "정상 위험 톤"),
        ("balanced risk tone", "균형 위험 톤"),
        ("conservative risk tone", "보수적 위험 톤"),
        ("monitor guidance is defensive_exit", "모니터 가이드는 defensive_exit"),
        ("neutral regime with neutral sentiment", "중립 체제와 중립 감정"),
        ("neutral regime / neutral sentiment", "중립 체제와 중립 감정"),
        ("Active memory layers: none", "활성 메모리 레이어 없음"),
        ("Active memory layers:", "활성 메모리 레이어:"),
        ("unused visible layers:", "미사용 표시 레이어:"),
        ("layer inactive", "레이어 비활성"),
        ("insufficient_trade_count", "거래 수 부족"),
        ("no_symbol", "종목 없음"),
        (
            "News was used for market/theme context and scanner guidance; it was not used as final symbol selection.",
            "뉴스는 시장/테마 맥락과 스캐너 가이드에 사용됐고, 최종 종목 선정 근거로는 사용되지 않았습니다.",
        ),
        (
            "Rank candidates by strategist frame fit, tape confirmation, and risk policy alignment.",
            "전략 프레임 적합도, 장중 확인, 리스크 정책 정합성 기준으로 후보를 정렬했습니다.",
        ),
        ("Entry is conditional on monitor gate confirmation.", "진입은 모니터 게이트 확인 조건부입니다."),
        (
            "Strategist permits only the strategy frame; scanner, monitor, supervisor, and executor still own downstream gates.",
            "전략가는 전략 프레임만 허용하며, 스캐너/모니터/슈퍼바이저/집행기가 후속 게이트를 소유합니다.",
        ),
        ("final_symbol_selection", "최종 종목 선택"),
        ("final_candidate_rank", "최종 후보 순위"),
        ("playbook=defensive", "playbook=방어형"),
        ("playbook=pullback", "playbook=눌림목"),
        ("playbook=breakout", "playbook=돌파"),
        ("risk=normal", "risk=정상"),
        ("status=ok", "status=정상"),
        ("liquidity", "유동성"),
        ("risk_penalty", "리스크 패널티"),
        ("low_volatility", "저변동성"),
        ("illiquid_microcap", "저유동성 소형주"),
        ("headline_only_momentum", "헤드라인 단독 모멘텀"),
        ("high_gap_speculative", "갭 급등 투기성"),
        ("VWAP reclaim", "VWAP 회복"),
        ("rebound confirmation", "리바운드 확인"),
        ("too_extended_from_vwap", "VWAP 대비 과확장"),
        ("breakout_without_volume", "거래량 없는 돌파"),
        ("risk_policy_block", "리스크 정책 차단"),
    )
    out = text
    for src, dst in replacements:
        out = out.replace(src, dst)
    return out


def _strategy_output_text(value: Any, *, max_len: int = 240) -> str:
    text = _operatorize_strategist_output_text(value)
    if not text or text == "-":
        return ""
    return _clip(text, max_len)


def _strategy_output_list_text(values: Any, *, limit: int = 4, sep: str = ", ") -> str:
    items: List[str] = []
    for raw in _listify(values):
        text = _strategy_output_text(raw, max_len=120)
        if not text or text in items:
            continue
        items.append(text)
        if len(items) >= max(1, int(limit)):
            break
    return sep.join(items)


def _strategy_output_layer_bits(layer_decisions: Any) -> str:
    decisions = _as_dict(layer_decisions)
    bits: List[str] = []
    for layer, row in list(decisions.items())[:4]:
        item = _as_dict(row)
        used = "used" if bool(item.get("used")) else "not_used"
        gate = _strategy_output_text(
            item.get("gate_reason") or item.get("reason") or item.get("status"),
            max_len=80,
        )
        bits.append(f"{layer}={used}" + (f"/{gate}" if gate else ""))
    return ", ".join(bits)


def _append_strategy_output_line(lines: List[str], label: str, text: str) -> None:
    clean = _clip(_operatorize_strategist_output_text(text), 320)
    if clean and not _looks_corrupted(clean):
        lines.append(f"- [{label}] {clean}")


def _resolve_strategy_refresh_trace(report: Dict[str, Any]) -> Dict[str, Any]:
    direct = _as_dict(report.get("strategist_refresh_trace"))
    if direct:
        return direct
    output = _resolve_strategist_output_surface(report)
    return _as_dict(output.get("strategy_refresh_trace"))


def _build_strategist_refresh_trace(report: Dict[str, Any]) -> List[str]:
    trace = _resolve_strategy_refresh_trace(report)
    if not trace:
        return []

    lines: List[str] = []
    summary = _strategy_output_text(trace.get("summary"), max_len=420)
    if summary:
        lines.append(summary)

    stage_rows = [row for row in _listify(trace.get("stages")) if isinstance(row, dict)]
    if stage_rows:
        for idx, row in enumerate(stage_rows[:4], start=1):
            label = _strategy_output_text(row.get("label"), max_len=80) or f"{idx}단계"
            stage_summary = _strategy_output_text(row.get("summary"), max_len=260)
            details: List[str] = []
            reason = _strategy_output_text(row.get("reason"), max_len=120)
            selected_symbol = _strategy_output_text(row.get("selected_symbol"), max_len=40)
            if row.get("requested") is not None:
                details.append(f"요청={bool(row.get('requested'))}")
            if row.get("evaluated") is not None:
                details.append(f"평가={bool(row.get('evaluated'))}")
            if row.get("effective") is not None:
                details.append(f"반영={bool(row.get('effective'))}")
            if selected_symbol:
                details.append(f"대상={selected_symbol}")
            if reason:
                details.append(f"사유={reason}")
            line = f"- [{label}] {stage_summary or '기록된 요약 없음'}"
            if details:
                line += f" ({'; '.join(details)})"
            lines.append(line)
    else:
        for raw in _listify(trace.get("bullets")):
            text = _strategy_output_text(raw, max_len=260)
            if text:
                lines.append(f"- {text}")

    delta_count = trace.get("policy_delta_count")
    delta_fields = _strategy_output_list_text(trace.get("policy_delta_fields"), limit=6)
    if delta_count is not None or delta_fields:
        delta_text = f"정책 delta count={delta_count if delta_count is not None else '-'}"
        if delta_fields:
            delta_text += f", fields={delta_fields}"
        lines.append(f"- [최종 정책 변화] {delta_text}")

    return _dedupe(lines)


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
    section = _as_dict(report.get("entry_decision"))
    lines: List[str] = []
    summary = _section_summary(section)
    if summary and not _looks_corrupted(summary):
        lines.append(summary)
    for bullet in _bullet_lines(section):
        lines.append(bullet)
    return _dedupe(lines)


def _build_guard_approval(report: Dict[str, Any]) -> List[str]:
    section = _as_dict(report.get("guard_approval_result"))
    lines: List[str] = []
    raw_summary = _clip(section.get("summary"), 120).strip().lower()
    summary = _section_summary(section)
    if summary and raw_summary not in {"guard", "approval", ""} and not _looks_corrupted(summary):
        lines.append(summary)
    repeated = {
        "- 가드 승인 결과를 정리했습니다.",
        "- 슈퍼바이저는 주문을 승인했습니다.",
        "- 가드 판단은 허용이었습니다.",
    }
    for bullet in _bullet_lines(section):
        if summary and bullet in repeated:
            continue
        lines.append(bullet)
    if not lines:
        lines.append("- 가드 승인 결과는 별도 예외 없이 통과했습니다.")
    return _dedupe(lines)

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
    truth = _get_truth_surface(report)
    price = _as_dict(truth.get("price"))
    pnl = _as_dict(truth.get("pnl"))
    lines: List[str] = []
    sell_price = price.get("broker_fill_price")
    if sell_price not in (None, ""):
        lines.append(f"- 브로커 체결 기준 가격은 {_fmt_price(sell_price)}였습니다.")
    if pnl.get("value") not in (None, "", "unavailable") and pnl.get("pct") not in (None, ""):
        lines.append(f"- 브로커 실현 손익은 {pnl.get('value')} / {_fmt_pct(pnl.get('pct'))} 기준으로 정리했습니다.")
    if pnl.get("broker_fee") not in (None, "") or pnl.get("broker_tax") not in (None, ""):
        lines.append(
            f"- 브로커 수수료/세금은 {pnl.get('broker_fee') if pnl.get('broker_fee') not in (None, '') else '-'} / "
            f"{pnl.get('broker_tax') if pnl.get('broker_tax') not in (None, '') else '-'}였습니다."
        )
    if _as_dict(report.get("execution_details")).get("broker_truth_source"):
        lines.append(f"- 체결 truth 소스는 {_metadata_value(_as_dict(report.get('execution_details')).get('broker_truth_source'))}였습니다.")
    lines.append(f"- 가격 truth 소스는 {_truth_source_label(price.get('price_truth_source'))}으로 확인했습니다.")
    lines.append(f"- 손익 truth 소스는 {_truth_source_label(pnl.get('pnl_truth_source'))}으로 확인했습니다.")
    return lines


def _humanize_reporter_recommendation(text: Any) -> str:
    raw = _clip(text, 240)
    if raw == "Same-day closed trades are loss-heavy; keep defensive entry posture until follow-through quality improves.":
        return "당일 닫힌 거래가 손실 쪽으로 기울어 있어, 추세 연속성 품질이 회복되기 전까지는 진입을 더 방어적으로 유지해야 합니다."
    if raw == "Cached strategist reuse is elevated; compare refresh cadence against fresh full-cycle opportunities.":
        return "기존 전략가 재사용 비중이 높아, 새 전체 재평가 경로를 얼마나 자주 허용할지 다시 점검해야 합니다."
    if raw == "Top blocker is confidence_ok; inspect whether this gate is dominating no-trade outcomes.":
        return "no-trade를 가장 많이 막은 축이 진입 게이트였으니, 이 gate가 과도하게 지배적인지 다시 점검해야 합니다."
    if raw == "Monitor-only share is high; review hold-management concentration before widening entry tuning.":
        return "모니터 단독 경로 비중이 높으니, 진입 조건을 넓히기 전에 보유 관리가 한쪽에 과도하게 쏠리지 않았는지 먼저 점검해야 합니다."
    return _translate_text(raw)

def _humanize_reporter_pattern(name: Any, detail: Any, value: Any) -> str:
    raw_name = _clip(name, 80)
    raw_detail = _clip(detail, 160)
    if raw_name == "freshness_status":
        return ""
    if raw_name == "closed_trade_count" or raw_detail.startswith("closed trade reports"):
        count = _num_opt(value)
        if count is None:
            match = re.search(r"(\d+)", raw_detail)
            count = float(match.group(1)) if match else None
        return f"당일 닫힌 거래는 {int(count)}건이었습니다." if count is not None else ""
    if raw_name == "avg_pnl_pct" or raw_detail.startswith("average same-day pnl pct"):
        pct = _num_opt(value)
        if pct is None:
            match = re.search(r"(-?\d+(?:\.\d+)?)", raw_detail)
            pct = float(match.group(1)) if match else None
        return f"당일 평균 손익률은 {_fmt_pct(pct)}였습니다." if pct is not None else ""
    if m := re.fullmatch(r"(monitor_only|cached_strategist|full_cycle)\s+(\d+)/(\d+)\s+runs", raw_detail, re.I):
        label = {
            "monitor_only": "모니터 단독 경로",
            "cached_strategist": "기존 전략가 재사용 경로",
            "full_cycle": "전체 재평가 경로",
        }.get(m.group(1).lower(), m.group(1))
        return f"{label}가 전체 {m.group(3)}회 중 {m.group(2)}회로 반복됐습니다."
    if m := re.fullmatch(r"(.+?)\s+(\d+)/(\d+)", raw_detail):
        return f"{m.group(1)} 패턴이 전체 {m.group(3)}회 중 {m.group(2)}회였습니다."
    if raw_detail:
        return _translate_text(raw_detail)
    return _translate_text(raw_name)


def _build_reporter_evaluation(report: Dict[str, Any]) -> List[str]:
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory = _as_dict(report.get("memory_surface"))
    packet = _as_dict(memory.get("reporter_feedback_packet"))
    lines: List[str] = []

    if packet.get("available"):
        truth = _get_truth_surface(report)
        pnl = _as_dict(truth.get("pnl"))
        pnl_value = _num_opt(pnl.get("value"))
        if pnl_value is not None:
            if pnl_value > 0:
                trade_result = "수익으로 마감한"
            elif pnl_value < 0:
                trade_result = "손실로 마감한"
            else:
                trade_result = "손익이 거의 없었던"
        else:
            trade_result = "손익을 직접 판단하기 어려운"

        analysis = _as_dict(packet.get("trade_report_analysis"))
        closed_count = analysis.get("closed_trade_count")
        win_count = analysis.get("win_count")
        loss_count = analysis.get("loss_count")
        avg_pnl_pct = analysis.get("avg_pnl_pct")
        source_label = _humanize_reporter_source_label(_as_dict(packet.get("source_reports")))
        lines.append(f"이번 거래는 {trade_result} 흐름이었고, 당일 리포터는 이를 같은 날 반복 패턴 속에서 보조 평가했습니다.")
        lines.append(
            f"- 리포터 소스는 {source_label}였고, 당일 닫힌 거래 {closed_count if closed_count not in (None, '') else '-'}건 중 "
            f"승리 {win_count if win_count not in (None, '') else '-'} / 손실 {loss_count if loss_count not in (None, '') else '-'}, "
            f"평균 손익률 {_fmt_pct(avg_pnl_pct)}였습니다."
        )
        pattern_rows: List[str] = []
        for item in _listify(packet.get("dominant_patterns"))[:3]:
            row = _as_dict(item)
            if row.get("name"):
                humanized = _humanize_reporter_pattern(row.get("name"), row.get("detail"), row.get("value"))
                if humanized:
                    pattern_rows.append(humanized.rstrip("."))
        if pattern_rows:
            lines.append(f"- 당일 반복 패턴 요약: {' / '.join(pattern_rows)}.")
        recommendation = _humanize_reporter_recommendation(_first_nonempty(_listify(packet.get("recommendation"))))
        if recommendation:
            lines.append(f"- 리포터 권고: {recommendation}")
        return lines

    summary = _section_summary(reporter_eval)
    if summary:
        lines.append(summary)
    for bullet in _bullet_lines(reporter_eval):
        lines.append(bullet)
    return _dedupe(lines)

def _build_weaknesses(report: Dict[str, Any]) -> List[str]:
    section = _as_dict(report.get("errors_weaknesses_improvement_points"))
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory = _as_dict(report.get("memory_surface"))
    reporter_packet = _as_dict(memory.get("reporter_feedback_packet"))
    reporter_ready = reporter_eval.get("status") == "ok" or reporter_packet.get("available")
    lines: List[str] = []
    summary = _section_summary(section)
    if summary:
        if summary == "Warnings and missing links were recorded for operator follow-up.":
            lines.append("운영자 후속 확인이 필요한 취약 지점을 정리했습니다.")
        else:
            lines.append(summary)
    for bullet in _bullet_lines(section):
        if reporter_ready and "동일 일자 리포터 분석이 아직 이 거래 생애주기에 연결되지 않았습니다." in bullet:
            continue
        lines.append(bullet)
    deduped = _dedupe(lines)
    if len(deduped) <= 3:
        return deduped
    compact = [deduped[0]]
    compact.extend(deduped[1:3])
    if len(deduped) > 3:
        compact.append("- 추가 취약 지점은 저장된 보완 사안 원문에 남겨 두었습니다.")
    return _dedupe(compact)


def _extract_metadata_from_texts(texts: Iterable[str]) -> List[str]:
    lines: List[str] = []
    for text in texts:
        raw = _clip(text, 240)
        if not raw:
            continue
        source_match = re.search(r"source=([A-Za-z0-9_.:/-]+)", raw)
        status_match = re.search(r"status=([A-Za-z0-9_.:/-]+)", raw)
        if source_match:
            lines.append(f"- 데이터 출처: {source_match.group(1)}")
        if status_match:
            lines.append(f"- 상태: {_metadata_value(status_match.group(1))}")
    return lines


def _build_provenance(report: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for section_name, row in _as_dict(report.get("section_provenance")).items():
        item = _as_dict(row)
        if item.get("source"):
            lines.append(f"- 데이터 출처: {_metadata_value(item.get('source'))}")
        if item.get("artifact_path"):
            lines.append(f"- 참조 경로: {item.get('artifact_path')}")
        if item.get("confidence"):
            lines.append(f"- 신뢰도: {_metadata_value(item.get('confidence'))}")
    texts: List[str] = []
    for key in ("market_context_at_entry", "strategist_summary", "why_this_symbol_was_chosen"):
        section = _as_dict(report.get(key))
        texts.extend([_clip(section.get("summary"), 400)])
        texts.extend(_listify(section.get("bullets")))
    lines.extend(_extract_metadata_from_texts(texts))
    generation = _as_dict(report.get("generation"))
    if generation.get("reason"):
        lines.append(f"- 생성 상태: {_metadata_value(generation.get('status') or '-')}")
        lines.append(f"- 생성 사유: {_metadata_value(generation.get('reason'))}")
    return _dedupe(lines)


def _build_timeline(report: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for row in _listify(report.get("full_timeline")):
        item = _as_dict(row)
        event = _clip(item.get("event"), 40).lower()
        desc = _clip(item.get("description"), 240)
        if not desc:
            continue
        if m := re.fullmatch(r"Entry BUY was executed by run (.+)\.", desc):
            lines.append(f"- 진입: run {m.group(1)}에서 매수 진입이 실행됐습니다.")
        elif m := re.fullmatch(r"Exit SELL was executed by run (.+)\.", desc):
            lines.append(f"- 청산: run {m.group(1)}에서 매도 청산이 실행됐습니다.")
        elif event == "entry":
            lines.append(f"- 진입: {_translate_text(desc)}")
        elif event == "exit":
            lines.append(f"- 청산: {_translate_text(desc)}")
        else:
            lines.append(f"- {_translate_text(desc)}")
    return lines


def _translate_watch_item(text: str) -> str:
    raw = _clip(text, 200)
    mapping = {
        "Lifecycle status: closed": "라이프사이클 상태 종결",
        "Monitor trigger changes": "모니터 트리거 변화",
        "Macro/news shifts": "거시 환경 및 뉴스 변화",
        "VWAP retest": "VWAP 재확인",
    }
    return mapping.get(raw, _translate_text(raw))


def _translate_reason_phrase(text: str) -> str:
    raw = _clip(text, 200).strip().strip(".")
    mapping = {
        "breakout above recent high with vwap structure confirmation": "직전 고점 돌파와 VWAP 구조 확인",
        "breakout above recent high with vwap hold and volume confirmation": "VWAP 유지와 거래량 확인이 있는 최근 고점 돌파",
        "pullback structure above vwap with volume confirmation": "VWAP 위 눌림목 구조와 거래량 확인",
        "pullback rebound above vwap with volume confirmation": "VWAP 위 되돌림 반등과 거래량 확인",
    }
    return mapping.get(raw.lower(), _translate_text(raw))


def _translate_invalidation_item(text: str) -> str:
    raw = _clip(text, 200)
    mapping = {
        "stop-loss breach": "손절 기준 이탈",
        "monitor and scanner divergence": "모니터와 스캐너 판단 발산",
        "negative macro regime shift": "거시 환경의 부정적 전환",
        "prior low break": "직전 저점 이탈",
    }
    return mapping.get(raw, _translate_text(raw))


def _ensure_sentence(text: str) -> str:
    raw = _clip(text, 240).strip()
    if not raw:
        return ""
    if raw.endswith(("?", "!", "요.", "입니다.", "였습니다.", "합니다.", "됩니다.", "다.", ".")):
        return raw
    return raw + "입니다."


def _noun_predicate_was(text: str) -> str:
    raw = _clip(text, 240).strip()
    if not raw:
        return "-"
    last = raw[-1]
    if "가" <= last <= "힣":
        base = ord(last) - ord("가")
        has_batchim = (base % 28) != 0
        return raw + ("이었습니다" if has_batchim else "였습니다")
    return raw + "이었습니다"


def _build_final_conclusion(report: Dict[str, Any]) -> List[str]:
    section = _as_dict(report.get("final_operator_conclusion"))
    shared = _as_dict(report.get("shared_facts"))
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory = _as_dict(report.get("memory_surface"))
    reporter_packet = _as_dict(memory.get("reporter_feedback_packet"))
    reporter_ready = reporter_eval.get("status") == "ok" or reporter_packet.get("available")
    status = _clip(report.get("status"), 20).lower()
    lines: List[str] = []
    summary = _section_summary(section)
    if summary:
        lines.append(summary)
    raw_summary = _clip(section.get("summary"), 240)
    if raw_summary and not summary and raw_summary not in lines:
        lines.append(raw_summary)
    if status == "closed":
        symbol = _metadata_value(shared.get("symbol") or report.get("symbol") or "해당 거래")
        buy_price = shared.get("broker_buy_price")
        sell_price = shared.get("broker_fill_price")
        if buy_price not in (None, "") and sell_price not in (None, ""):
            lines.append(
                f"현재 판단은 청산 완료입니다. {symbol} 거래는 매수 진입 후 매도 청산까지 기록됐고, "
                f"브로커 매수가/매도가는 {_fmt_price(buy_price)} / {_fmt_price(sell_price)}였습니다."
            )
        else:
            lines.append(f"현재 판단은 청산 완료입니다. {symbol} 거래는 매수 진입 후 매도 청산까지 기록됐습니다.")
        lines.append("- 현재 판단 액션은 매도입니다.")
    else:
        summary = _section_summary(section)
        if summary:
            lines.append(summary)
        lines.append(f"- 현재 판단 액션은 {_action_label(section.get('current_action') or report.get('action'))}입니다.")
    for item in _listify(section.get("watch_next")):
        translated = _translate_watch_item(_clip(item, 200))
        if translated:
            if reporter_ready and "동일 일자 리포터 분석 연계" in translated:
                continue
            lines.append(f"- 다음 확인 항목은 {_ensure_sentence(translated)}")
    for item in _listify(section.get("thesis_invalidation")):
        translated = _translate_invalidation_item(_clip(item, 200))
        if translated:
            lines.append(f"- 기존 판단이 무효화되는 조건은 {_ensure_sentence(translated)}")
    return _dedupe(lines)


def _first_nonempty(values: List[Any]) -> Any:
    for value in values:
        if _clip(value, 240):
            return value
    return ""


def _monitor_delta_interpretation(rows: List[Any]) -> str:
    notes: List[str] = []
    for raw in rows:
        row = _as_dict(raw)
        field = _clip(row.get("field"), 80)
        delta = _num_opt(row.get("delta"))
        if field == "breakout_buffer_pct" and delta is not None and delta > 0:
            notes.append("돌파 확인 버퍼를 키워 추격 진입을 더 보수적으로 막았습니다.")
        elif field == "max_extended_from_vwap_pct" and delta is not None and delta < 0:
            notes.append("VWAP 기준 과확장 추격 허용 범위를 줄여 현재 가격 부담이 큰 진입을 줄였습니다.")
        elif field == "volume_ratio_min" and delta is not None and delta > 0:
            notes.append("거래량 확인 기준을 높여 힘이 약한 종목 진입을 더 엄격하게 걸렀습니다.")
    return " ".join(notes[:3])


def _looks_corrupted(text: str) -> bool:
    if not text:
        return False
    if "?" in text:
        return True
    if any(0xF900 <= ord(ch) <= 0xFAFF for ch in text):
        return True
    weird_markers = ["?꾨", "留ㅻ", "媛먯", "鍮꾪", "湲곗", "蹂댁", "吏꾩", "嫄곕", "理쒖", "泥?궛", "??"]
    return sum(marker in text for marker in weird_markers) >= 2


def _dedupe(lines: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for line in lines:
        key = line.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(line)
    return out
