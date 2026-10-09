from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .summary_parts.findings import collect_deterministic_summary_findings
from .summary_parts.render_diagnostics import collect_render_diagnostics
from .summary_input_parts.main_builder import build_trade_summary_input_impl
from .summary_input_parts.broker_alignment import build_broker_alignment
from .summary_input_parts.market_and_strategy import build_market_and_strategy
from .summary_input_parts.decision_flow import build_decision_flow


from .summary_render_parts.overview import append_summary_overview
from .summary_render_parts.market_news import append_summary_market_news
from .summary_render_parts.decision_lifecycle import append_summary_decision_lifecycle
from .summary_render_parts.closing import append_summary_closing



def render_trade_summary_markdown(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> str:
    _RECOVERED_PARTIAL_ENTRY_NOTE = deps["RECOVERED_PARTIAL_ENTRY_NOTE"]
    _RECOVERED_PARTIAL_EXIT_NOTE = deps["RECOVERED_PARTIAL_EXIT_NOTE"]
    _action_label = deps["action_label"]
    _applied_label = deps["applied_label"]
    _as_dict = deps["as_dict"]
    _authoritative_final_operator_summary = deps["authoritative_final_operator_summary"]
    _authoritative_holding_duration_label = deps["authoritative_holding_duration_label"]
    _build_post_exit_shadow_summary_lines = deps["build_post_exit_shadow_summary_lines"]
    _build_strategy_horizon_lines = deps["build_strategy_horizon_lines"]
    _build_summary_exit_trigger_lines = deps["build_summary_exit_trigger_lines"]
    _build_trade_cost_analysis = deps["build_trade_cost_analysis"]
    _carryover_context = deps["carryover_context"]
    _clip = deps["clip"]
    _dedupe = deps["dedupe"]
    _enrich_exit_signal_snapshot_from_monitor = deps["enrich_exit_signal_snapshot_from_monitor"]
    _ensure_sentence = deps["ensure_sentence"]
    _entry_confidence_for_operator_summary = deps["entry_confidence_for_operator_summary"]
    _entry_reason_line = deps["entry_reason_line"]
    _entry_signal_metric_summary_lines = deps["entry_signal_metric_summary_lines"]
    _entry_watch_summary_lines = deps["entry_watch_summary_lines"]
    _execution_mode_label = deps["execution_mode_label"]
    _extract_exit_signal_snapshot = deps["extract_exit_signal_snapshot"]
    _fmt_pct = deps["fmt_pct"]
    _get_truth_surface = deps["get_truth_surface"]
    _is_not_captured = deps["is_not_captured"]
    _is_post_entry_gate_text = deps["is_post_entry_gate_text"]
    _is_recovered_partial_exit_report = deps["is_recovered_partial_exit_report"]
    _korea_index_lines = deps["korea_index_lines"]
    _listify = deps["listify"]
    _memory_layers_text = deps["memory_layers_text"]
    _metadata_value = deps["metadata_value"]
    _normalize_entry_confidence_for_operator_summary = deps["normalize_entry_confidence_for_operator_summary"]
    _normalize_exit_trigger_label = deps["normalize_exit_trigger_label"]
    _num_opt = deps["num_opt"]
    _operator_pnl_pct = deps["operator_pnl_pct"]
    _playbook_label = deps["playbook_label"]
    _pnl_basis_label = deps["pnl_basis_label"]
    _render_controlled_lane_report_lines = deps["render_controlled_lane_report_lines"]
    _render_quant_tactic_report_lines_impl = deps["render_quant_tactic_report_lines_impl"]
    _resolve_entry_signal_snapshot = deps["resolve_entry_signal_snapshot"]
    _resolve_market_context = deps["resolve_market_context"]
    _resolve_trade_symbol_metadata = deps["resolve_trade_symbol_metadata"]
    _risk_mode_label = deps["risk_mode_label"]
    _same_day_current_result = deps["same_day_current_result"]
    _same_day_summary_from_texts = deps["same_day_summary_from_texts"]
    _sample_news_titles = deps["sample_news_titles"]
    _sample_news_titles_for_symbol = deps["sample_news_titles_for_symbol"]
    _selection_fallback_context = deps["selection_fallback_context"]
    _status_label = deps["status_label"]
    _story_type_label = deps["story_type_label"]
    _strip_trailing_blanks = deps["strip_trailing_blanks"]
    _theme_label = deps["theme_label"]
    _trade_cost_analysis_lines = deps["trade_cost_analysis_lines"]
    _translate_text = deps["translate_text"]
    _translated_metadata = deps["translated_metadata"]
    """Render the short operator-facing summary next to ai_trade_report.md."""

    def _pick(*values: Any) -> Any:
        for value in values:
            if value not in (None, ""):
                return value
        return ""

    def _money(value: Any) -> str:
        num = _num_opt(value)
        if num is None:
            return "-"
        if abs(num) >= 100:
            return f"{num:,.0f}"
        return f"{num:,.2f}".rstrip("0").rstrip(".")

    def _compact_number(value: Any) -> str:
        num = _num_opt(value)
        if num is not None:
            rendered = f"{num:.6f}".rstrip("0").rstrip(".")
            return rendered or "0"
        text = str(value if value is not None else "").strip()
        return _metadata_value(text) or "-"

    def _compact_decimal(value: Any, digits: int = 2) -> str:
        num = _num_opt(value)
        if num is None:
            return _metadata_value(value) or "-"
        return f"{num:.{digits}f}"

    def _first_matching_line(values: Iterable[Any], needles: Iterable[str]) -> str:
        lowered_needles = [needle.lower() for needle in needles]
        for raw in values:
            text = _translate_text(raw).strip()
            if not text:
                continue
            lowered = text.lower()
            if any(needle in lowered for needle in lowered_needles):
                return text.rstrip(".")
        return ""

    def _section_texts(*sections: Dict[str, Any]) -> List[str]:
        texts: List[str] = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            if section.get("summary"):
                texts.append(str(section.get("summary") or ""))
            texts.extend(str(item or "") for item in _listify(section.get("bullets")))
        return texts

    def _same_day_summary(section: Dict[str, Any]) -> str:
        return _same_day_summary_from_texts(
            _section_texts(section),
            fallback="당일 성과 집계는 리포터 평가 섹션에서 확인 필요",
            current_result=_same_day_current_result(report),
        )

    def _selected_score(selection: Dict[str, Any]) -> str:
        score = _pick(selection.get("score_total"), selection.get("selected_score"))
        trace = _as_dict(selection.get("scanner_selection_trace"))
        selected_symbol = str(_pick(selection.get("symbol"), report.get("symbol"), trace.get("monitor_selected_symbol"), trace.get("selected_symbol")) or "").strip()
        if score in (None, "") and _selection_fallback_context(selection, selected_symbol).get("used"):
            news = _as_dict(trace.get("news_scanner_contribution"))
            score = _pick(trace.get("selected_score"), news.get("selected_score_total"))
        if score in (None, ""):
            for row in _listify(trace.get("ranked_candidates")):
                row_obj = _as_dict(row)
                if str(row_obj.get("symbol") or "").strip() == selected_symbol:
                    score = _pick(row_obj.get("score_total"), row_obj.get("score"))
                    break
        num = _num_opt(score)
        return f"{num:.3f}" if num is not None else "-"

    def _selected_rank(selection: Dict[str, Any]) -> str:
        trace = _as_dict(selection.get("scanner_selection_trace"))
        rank = _pick(selection.get("selected_rank"), trace.get("selected_rank"), selection.get("scanner_rank"))
        return str(rank) if rank not in (None, "") else "-"

    def _extract_run_id(timeline: Iterable[Any], event_name: str) -> str:
        for row in timeline:
            row_obj = _as_dict(row)
            event = str(_pick(row_obj.get("event"), row_obj.get("step")) or "").lower()
            if event_name not in event:
                continue
            direct = _pick(row_obj.get("run_id"), row_obj.get("id"))
            if direct:
                return str(direct)
            desc = str(_pick(row_obj.get("description"), row_obj.get("summary")) or "")
            match = re.search(r"\brun\s+([0-9a-f]{8,64})\b", desc, flags=re.IGNORECASE)
            if match:
                return match.group(1)
        return "-"

    def _policy_delta_lines(memory_app: Dict[str, Any]) -> List[str]:
        monitor = _as_dict(memory_app.get("monitor_memory_bias"))
        scanner = _as_dict(memory_app.get("scanner_memory_bias"))
        lines_out = [
            f"* 스캐너 메모리: {_applied_label(scanner.get('applied'))}",
            f"* 모니터 메모리: {_applied_label(monitor.get('applied'))}"
            + (f" ({_memory_layers_text(monitor.get('active_layers'))} 레벨)" if monitor.get("active_layers") else ""),
        ]
        deltas: List[str] = []
        for row in _listify(monitor.get("applied_deltas")) + _listify(monitor.get("exit_deltas")):
            row_obj = _as_dict(row)
            field = str(row_obj.get("field") or "").strip()
            if not field:
                continue
            before = row_obj.get("from")
            after = row_obj.get("to")
            deltas.append(f"* {field}: {_compact_number(before)} → {_compact_number(after)}")
        if deltas:
            lines_out.append("")
            lines_out.append("### 정책 변화")
            lines_out.extend(deltas[:4])
        return lines_out

    shared = _as_dict(report.get("shared_facts"))
    truth = _get_truth_surface(report)
    truth_price = _as_dict(truth.get("price"))
    truth_pnl = _as_dict(truth.get("pnl"))
    market = _resolve_market_context(report)
    strategist = _as_dict(report.get("strategist_summary"))
    selection = _as_dict(report.get("why_this_symbol_was_chosen"))
    entry = _as_dict(report.get("entry_decision"))
    holding = _as_dict(report.get("holding_monitoring_story"))
    exit_decision = _as_dict(report.get("exit_decision"))
    execution = _as_dict(report.get("execution_quality"))
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory_app = _as_dict(report.get("memory_application_surface"))
    monitor = _as_dict(report.get("monitor_snapshot"))
    entry_signal_snapshot = _resolve_entry_signal_snapshot(report)
    entry_signal_metric_lines = _entry_signal_metric_summary_lines(entry_signal_snapshot)
    final = _as_dict(report.get("final_operator_conclusion"))
    timeline = _listify(report.get("full_timeline") if isinstance(report.get("full_timeline"), list) else report.get("timeline"))

    trade_id = _clip(report.get("trade_id") or report.get("story_id"), 80) or "-"
    symbol = _clip(_pick(report.get("symbol"), shared.get("symbol")), 32) or "-"
    symbol_metadata = _resolve_trade_symbol_metadata(report, symbol)
    symbol_name = str(symbol_metadata.get("symbol_name") or "").strip()
    symbol_theme = str(symbol_metadata.get("theme") or "").strip()
    status = _status_label(_pick(report.get("status"), shared.get("status")))
    story_type = _story_type_label(report.get("story_type"))
    execution_mode = _execution_mode_label(report.get("execution_mode_label"))
    action = _action_label(_pick(final.get("current_action"), report.get("action"), shared.get("action")))

    pnl = _pick(truth_pnl.get("value"), shared.get("pnl"))
    pnl_pct, pnl_pct_is_observation = _operator_pnl_pct(truth_pnl, shared)
    pnl_num = _num_opt(pnl)
    pnl_label_basis = pnl_num if pnl_num is not None else _num_opt(pnl_pct)
    result_label = "보합"
    if pnl_label_basis is not None and pnl_label_basis > 0:
        result_label = "이익"
    elif pnl_label_basis is not None and pnl_label_basis < 0:
        result_label = "손실"
    result_basis_label = " 관측" if pnl_num is None and pnl_pct_is_observation else ""
    result_text = (
        f"{result_label}{result_basis_label} ({_fmt_pct(pnl_pct)})"
        if pnl_pct not in (None, "")
        else result_label
    )

    same_day = _same_day_summary(reporter_eval)
    combined_texts = _section_texts(market, strategist, selection, entry, holding, exit_decision, reporter_eval)
    combined_blob = "\n".join(combined_texts).lower()
    entry_blob = "\n".join(_section_texts(selection, entry)).lower()
    exit_blob = "\n".join(_section_texts(exit_decision, holding)).lower()
    cost_analysis = _build_trade_cost_analysis(report)
    cost_drag_pct = _num_opt(cost_analysis.get("cost_drag_pct"))
    holding_duration_summary = _authoritative_holding_duration_label(report) or _pick(
        shared.get("holding_duration"), report.get("hold_duration"), ""
    )
    rank_num = _num_opt(_selected_rank(selection))
    selection_fallback_summary = _selection_fallback_context(selection, symbol)
    scanner_top_pick = _metadata_value(selection_fallback_summary.get("scanner_top_pick_symbol"))
    recovered_partial_exit = _is_recovered_partial_exit_report(report)
    carryover_context = _carryover_context(report)
    carryover_exit = bool(carryover_context.get("is_carryover_exit"))
    exit_only_report = recovered_partial_exit or carryover_exit
    if exit_only_report:
        rank_num = None
    normalized_exit_reason = _normalize_exit_trigger_label(shared.get("exit_reason"), "")
    actual_take_profit = normalized_exit_reason == "목표 수익 실현 기준"
    actual_peak_exit = (
        normalized_exit_reason == "고점 대비 하락폭 기준"
        or (
            not normalized_exit_reason
            and (
                "peak_drawdown" in exit_blob
                or "고점 대비 하락폭 기준" in exit_blob
                or "고점 대비 하락폭으로 청산" in exit_blob
                or "고점 대비 하락폭 축" in exit_blob
            )
        )
    )
    actual_hard_stop = normalized_exit_reason == "고정 손절 기준"

    positives, problems, cause_lines, recommendations = collect_render_diagnostics(
        truth_price=truth_price,
        truth_pnl=truth_pnl,
        shared=shared,
        carryover_exit=carryover_exit,
        recovered_partial_exit=recovered_partial_exit,
        rank_num=rank_num,
        strategist=strategist,
        selection=selection,
        entry=entry,
        exit_decision=exit_decision,
        holding_duration_summary=holding_duration_summary,
        memory_app=memory_app,
        combined_texts=combined_texts,
        cost_analysis=cost_analysis,
        cost_drag_pct=cost_drag_pct,
        selection_fallback_summary=selection_fallback_summary,
        scanner_top_pick=scanner_top_pick,
        symbol=symbol,
        entry_blob=entry_blob,
        carryover_context=carryover_context,
        actual_take_profit=actual_take_profit,
        actual_peak_exit=actual_peak_exit,
        actual_hard_stop=actual_hard_stop,
        deps=deps, compact_number=_compact_number, first_matching_line=_first_matching_line,
    )

    market_news = _sample_news_titles(
        market.get("market_news_titles") or report.get("strategist_market_headlines"),
        limit=2,
    )
    symbol_news = _sample_news_titles_for_symbol(
        symbol,
        market.get("symbol_news_titles"),
        report.get("strategist_symbol_headlines"),
        market.get("candidate_news_titles"),
        limit=2,
    )
    market_summary = _translate_text(market.get("summary")) or "시장 요약은 상세 리포트에서 확인 필요"
    playbook = _playbook_label(_pick(market.get("playbook"), market.get("selected_playbook")))
    trace_summary = _as_dict(report.get("strategist_trace_summary"))
    risk_tone = _risk_mode_label(_pick(market.get("risk_tone"), trace_summary.get("risk_tone"), market.get("risk_mode")))
    monitor_guide = _metadata_value(_pick(trace_summary.get("monitor_guidance"), market.get("monitor_guidance"), ""))
    selection_reason = _translate_text(selection.get("basis") or "").strip()
    if not selection_reason:
        selection_reason = _first_matching_line(_listify(selection.get("bullets")), ["거래대금", "거래량", "모멘텀", "선정"])
    selection_trace = _as_dict(selection.get("scanner_selection_trace"))
    scanner_chart_fit = _as_dict(selection.get("scanner_chart_fit")) or _as_dict(selection_trace.get("scanner_chart_fit"))
    selection_fallback = _selection_fallback_context(selection, symbol)
    entry_watch_lines = _entry_watch_summary_lines(
        report,
        require_trade_symbol_match=bool(selection_fallback.get("used")) or bool(exit_only_report),
    )
    blocked_reason = ""
    if not selection_fallback.get("used"):
        blocked_reason = _first_matching_line(_listify(selection.get("bullets")) + _listify(entry.get("bullets")), ["1순위", "top pick", "막혔", "blocked"])
    entry_reason = _entry_reason_line(_listify(entry.get("bullets")))
    if not entry_reason:
        entry_reason = _entry_reason_line([entry.get("summary")])
    entry_confidence = _entry_confidence_for_operator_summary(
        _listify(entry.get("bullets")),
        action=action,
        buy_price=_pick(truth_price.get("broker_buy_price"), shared.get("broker_buy_price")),
    )
    if not entry_confidence and "신뢰도" in str(entry.get("summary") or ""):
        entry_summary_text = _translate_text(entry.get("summary")).rstrip(".")
        if not _is_post_entry_gate_text(entry_summary_text):
            entry_confidence = _normalize_entry_confidence_for_operator_summary(
                entry_summary_text,
                action=action,
                buy_price=_pick(truth_price.get("broker_buy_price"), shared.get("broker_buy_price")),
            )
    if carryover_exit:
        selection_reason = "오버나이트/주말 이월 포지션 청산"
        blocked_reason = ""
        entry_reason = "오늘 신규 진입 판단이 아니라 전일/주말 이월 포지션입니다."
        entry_confidence = ""
    elif recovered_partial_exit:
        selection_reason = "보유/회수 포지션 청산"
        blocked_reason = ""
        entry_reason = _RECOVERED_PARTIAL_ENTRY_NOTE
        entry_confidence = ""
    holding_duration = _authoritative_holding_duration_label(report) or _pick(
        shared.get("holding_duration"), report.get("hold_duration"), ""
    )
    exit_signal_texts = _section_texts(exit_decision) + _section_texts(holding)
    exit_signal_snapshot = _extract_exit_signal_snapshot(exit_signal_texts)
    exit_signal_snapshot = _enrich_exit_signal_snapshot_from_monitor(exit_signal_snapshot, monitor)
    exit_trigger = _first_matching_line(_listify(exit_decision.get("bullets")), ["촉발", "트리거", "청산 사유", "고점 대비"])
    if not exit_trigger:
        exit_trigger = _first_matching_line(_section_texts(exit_decision), ["촉발", "트리거", "청산 사유", "고점 대비"])
    exit_price = _pick(truth_price.get("broker_fill_price"), shared.get("broker_fill_price"))
    buy_price = _pick(truth_price.get("broker_buy_price"), shared.get("broker_buy_price"))
    monitor_exit_reference_price = _pick(
        truth_price.get("monitor_mark_price"),
        shared.get("monitor_mark_price"),
        exit_signal_snapshot.get("monitor_current_price"),
    )
    exit_price_note = ""
    if exit_price in (None, "") and monitor_exit_reference_price not in (None, ""):
        exit_price_note = f" (체결가 미확정, 모니터 기준 {_money(monitor_exit_reference_price)})"

    lines: List[str] = []
    append_summary_overview(
        lines=lines, _RECOVERED_PARTIAL_EXIT_NOTE=_RECOVERED_PARTIAL_EXIT_NOTE, _fmt_pct=_fmt_pct, _money=_money,
        _pick=_pick, _pnl_basis_label=_pnl_basis_label, _render_controlled_lane_report_lines=_render_controlled_lane_report_lines, _trade_cost_analysis_lines=_trade_cost_analysis_lines,
        buy_price=buy_price, carryover_context=carryover_context, carryover_exit=carryover_exit, cause_lines=cause_lines,
        execution_mode=execution_mode, exit_price=exit_price, exit_price_note=exit_price_note, pnl=pnl,
        pnl_num=pnl_num, pnl_pct=pnl_pct, pnl_pct_is_observation=pnl_pct_is_observation, positives=positives,
        problems=problems, recommendations=recommendations, recovered_partial_exit=recovered_partial_exit, report=report,
        result_label=result_label, result_text=result_text, same_day=same_day, shared=shared,
        status=status, story_type=story_type, symbol=symbol, symbol_name=symbol_name,
        symbol_theme=symbol_theme, trade_id=trade_id, truth_pnl=truth_pnl,
    )
    append_summary_market_news(
        lines=lines, _build_strategy_horizon_lines=_build_strategy_horizon_lines, _compact_decimal=_compact_decimal, _is_not_captured=_is_not_captured,
        _korea_index_lines=_korea_index_lines, _listify=_listify, _metadata_value=_metadata_value, _theme_label=_theme_label,
        _translated_metadata=_translated_metadata, carryover_context=carryover_context, carryover_exit=carryover_exit, entry_watch_lines=entry_watch_lines,
        market=market, market_news=market_news, market_summary=market_summary, monitor_guide=monitor_guide,
        playbook=playbook, recovered_partial_exit=recovered_partial_exit, report=report, risk_tone=risk_tone,
        selection=selection, symbol=symbol, symbol_news=symbol_news,
    )
    append_summary_decision_lifecycle(
        lines=lines, _build_post_exit_shadow_summary_lines=_build_post_exit_shadow_summary_lines, _build_summary_exit_trigger_lines=_build_summary_exit_trigger_lines, _compact_decimal=_compact_decimal,
        _entry_signal_metric_summary_lines=_entry_signal_metric_summary_lines, _is_not_captured=_is_not_captured, _money=_money, _num_opt=_num_opt,
        _pick=_pick, _render_quant_tactic_report_lines_impl=_render_quant_tactic_report_lines_impl, _selected_rank=_selected_rank, _selected_score=_selected_score,
        blocked_reason=blocked_reason, buy_price=buy_price, carryover_context=carryover_context, carryover_exit=carryover_exit,
        entry_confidence=entry_confidence, entry_reason=entry_reason, entry_signal_metric_lines=entry_signal_metric_lines, entry_signal_snapshot=entry_signal_snapshot,
        entry_watch_lines=entry_watch_lines, exit_only_report=exit_only_report, exit_price=exit_price, exit_price_note=exit_price_note,
        exit_signal_snapshot=exit_signal_snapshot, exit_trigger=exit_trigger, holding_duration=holding_duration, pnl_pct=pnl_pct,
        recovered_partial_exit=recovered_partial_exit, report=report, scanner_chart_fit=scanner_chart_fit, selection=selection,
        selection_fallback=selection_fallback, selection_reason=selection_reason, shared=shared, symbol=symbol,
        truth_pnl=truth_pnl,
    )
    append_summary_closing(
        lines=lines, _authoritative_final_operator_summary=_authoritative_final_operator_summary, _dedupe=_dedupe, _ensure_sentence=_ensure_sentence,
        _extract_run_id=_extract_run_id, _listify=_listify, _policy_delta_lines=_policy_delta_lines, _translate_text=_translate_text,
        action=action, carryover_exit=carryover_exit, final=final, memory_app=memory_app,
        problems=problems, recommendations=recommendations, report=report, reporter_eval=reporter_eval,
        result_label=result_label, same_day=same_day, status=status, timeline=timeline,
    )
    return "\n".join(_strip_trailing_blanks(lines)).strip() + "\n"




def build_trade_summary_input(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    """Keep public identity and call-time monkeypatchable dependency boundaries."""
    return build_trade_summary_input_impl(
        report, deps=deps,
        collect_deterministic_summary_findings=collect_deterministic_summary_findings,
        build_broker_alignment=build_broker_alignment,
        build_market_and_strategy=build_market_and_strategy,
        build_decision_flow=build_decision_flow,
    )
