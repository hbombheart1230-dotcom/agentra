from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


def render_trade_summary_markdown(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> str:
    _RECOVERED_PARTIAL_ENTRY_NOTE = deps["RECOVERED_PARTIAL_ENTRY_NOTE"]
    _RECOVERED_PARTIAL_EXIT_NOTE = deps["RECOVERED_PARTIAL_EXIT_NOTE"]
    _action_label = deps["action_label"]
    _applied_label = deps["applied_label"]
    _as_dict = deps["as_dict"]
    _authoritative_final_operator_summary = deps["authoritative_final_operator_summary"]
    _authoritative_hold_duration_seconds = deps["authoritative_hold_duration_seconds"]
    _authoritative_holding_duration_label = deps["authoritative_holding_duration_label"]
    _build_post_exit_shadow_summary_lines = deps["build_post_exit_shadow_summary_lines"]
    _build_strategy_horizon_lines = deps["build_strategy_horizon_lines"]
    _build_summary_exit_trigger_lines = deps["build_summary_exit_trigger_lines"]
    _build_trade_cost_analysis = deps["build_trade_cost_analysis"]
    _carryover_context = deps["carryover_context"]
    _clip = deps["clip"]
    _compact_decimal = deps["compact_decimal"]
    _compact_number = deps["compact_number"]
    _compact_post_exit_shadow = deps["compact_post_exit_shadow"]
    _compact_section = deps["compact_section"]
    _dedupe = deps["dedupe"]
    _enrich_exit_signal_snapshot_from_monitor = deps["enrich_exit_signal_snapshot_from_monitor"]
    _ensure_sentence = deps["ensure_sentence"]
    _entry_confidence_for_operator_summary = deps["entry_confidence_for_operator_summary"]
    _entry_reason_line = deps["entry_reason_line"]
    _entry_signal_metric_summary_lines = deps["entry_signal_metric_summary_lines"]
    _entry_watch_execution_lines = deps["entry_watch_execution_lines"]
    _entry_watch_summary_lines = deps["entry_watch_summary_lines"]
    _execution_mode_label = deps["execution_mode_label"]
    _extract_exit_signal_snapshot = deps["extract_exit_signal_snapshot"]
    _extract_run_id = deps["extract_run_id"]
    _first_matching_line = deps["first_matching_line"]
    _fmt_pct = deps["fmt_pct"]
    _get_truth_surface = deps["get_truth_surface"]
    _is_not_captured = deps["is_not_captured"]
    _is_post_entry_gate_text = deps["is_post_entry_gate_text"]
    _is_recovered_partial_exit_report = deps["is_recovered_partial_exit_report"]
    _korea_index_lines = deps["korea_index_lines"]
    _listify = deps["listify"]
    _memory_layers_text = deps["memory_layers_text"]
    _metadata_value = deps["metadata_value"]
    _money = deps["money"]
    _normalize_entry_confidence_for_operator_summary = deps["normalize_entry_confidence_for_operator_summary"]
    _normalize_exit_trigger_label = deps["normalize_exit_trigger_label"]
    _num_opt = deps["num_opt"]
    _operator_pnl_pct = deps["operator_pnl_pct"]
    _pick = deps["pick"]
    _playbook_label = deps["playbook_label"]
    _pnl_basis_label = deps["pnl_basis_label"]
    _policy_delta_lines = deps["policy_delta_lines"]
    _policy_deltas = deps["policy_deltas"]
    _post_exit_shadow_surface = deps["post_exit_shadow_surface"]
    _quant_tactic_surface_impl = deps["quant_tactic_surface_impl"]
    _render_controlled_lane_report_lines = deps["render_controlled_lane_report_lines"]
    _render_quant_tactic_report_lines_impl = deps["render_quant_tactic_report_lines_impl"]
    _resolve_entry_execution_visibility = deps["resolve_entry_execution_visibility"]
    _resolve_entry_signal_snapshot = deps["resolve_entry_signal_snapshot"]
    _resolve_market_context = deps["resolve_market_context"]
    _resolve_trade_symbol_metadata = deps["resolve_trade_symbol_metadata"]
    _risk_mode_label = deps["risk_mode_label"]
    _same_day_current_result = deps["same_day_current_result"]
    _same_day_summary = deps["same_day_summary"]
    _same_day_summary_from_texts = deps["same_day_summary_from_texts"]
    _sample_news_titles = deps["sample_news_titles"]
    _sample_news_titles_for_symbol = deps["sample_news_titles_for_symbol"]
    _section_texts = deps["section_texts"]
    _selected_rank = deps["selected_rank"]
    _selected_score = deps["selected_score"]
    _selection_fallback_context = deps["selection_fallback_context"]
    _status_label = deps["status_label"]
    _story_type_label = deps["story_type_label"]
    _strategy_horizon_report_surface = deps["strategy_horizon_report_surface"]
    _strip_trailing_blanks = deps["strip_trailing_blanks"]
    _theme_label = deps["theme_label"]
    _trade_cost_analysis_lines = deps["trade_cost_analysis_lines"]
    _translate_text = deps["translate_text"]
    _translated_metadata = deps["translated_metadata"]
    _truth_source_label = deps["truth_source_label"]
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

    positives = []
    broker_fill_present = truth_price.get("broker_fill_price") not in (None, "")
    realized_pnl_present = str(truth_pnl.get("value") or shared.get("pnl") or "").strip().lower() not in {
        "",
        "unavailable",
        "not_available",
        "none",
        "-",
    }
    if broker_fill_present and realized_pnl_present:
        positives.append("키움 체결가와 당일 실현손익 확보")
    elif broker_fill_present:
        positives.append("브로커 체결가 확보, 실현손익/비용은 확인 대기")
    if carryover_exit:
        positives.append("오버나이트/주말 이월 청산을 신규 선정 평가와 분리해 기록")
    elif recovered_partial_exit:
        positives.append("회수/partial 청산을 신규 진입 평가와 분리해 기록")
    elif rank_num is not None:
        positives.append(f"스캐너 순위 {int(rank_num)}위와 모니터 재평가 경로 기록")
    elif strategist or selection or entry or exit_decision:
        positives.append("전략 → 스캐너 → 모니터 판단 흐름 기록")
    if holding_duration_summary and not _is_not_captured(holding_duration_summary):
        positives.append(f"보유 시간 {holding_duration_summary}와 청산 트리거 기록")
    elif entry or exit_decision or memory_app:
        positives.append("진입/청산 근거 및 정책 추적 가능")
    if not positives:
        positives.append("핵심 거래 아티팩트가 보존됨")

    problems: List[str] = []
    monitor_line = _first_matching_line(combined_texts, ["monitor_only", "monitor-only", "monitor 단독"])
    if monitor_line:
        problems.append("당일 monitor_only 경로 비중 높음")
    if carryover_exit:
        problems.append("오늘 신규 진입이 아니라 전일/주말 이월 포지션으로 별도 해석 필요")
    if recovered_partial_exit:
        problems.append("당일 BUY 근거가 없어 신규 진입 품질 평가는 제외 필요")
    if cost_analysis.get("mock_cost_warning") and cost_drag_pct is not None:
        problems.append(f"모의투자 비용 드래그 {_fmt_pct(cost_drag_pct)} 별도 해석 필요")
    if selection_fallback_summary.get("used") or (rank_num is not None and rank_num > 1):
        if scanner_top_pick and scanner_top_pick != "-":
            problems.append(f"1순위 {scanner_top_pick} 보류 후 {symbol} {int(rank_num) if rank_num else '-'}위 재평가 진입")
        else:
            problems.append("1순위 탈락 후 차순위 재평가 진입 구조")
    if "pullback_not_mature" in entry_blob:
        problems.append("pullback 성숙도 부족으로 진입 보류 발생")
    if actual_peak_exit:
        problems.append("이번 청산이 peak_drawdown 축이라 confirm 조건 점검 필요")
    if not problems:
        problems.append("거래별 반복 패턴 판단을 위한 추가 표본 필요")

    monitor_memory = _as_dict(memory_app.get("monitor_memory_bias"))
    cause_lines: List[str] = []
    if carryover_exit:
        if carryover_context.get("estimated_entry_kst") and carryover_context.get("exit_kst"):
            cause_lines.append(
                f"{symbol}은 {carryover_context.get('estimated_entry_date_kst')} 보유분이 "
                f"{carryover_context.get('exit_date_kst')}에 청산된 이월 포지션입니다"
            )
        else:
            cause_lines.append(f"{symbol}은 오늘 신규 진입이 아니라 전일/주말 이월 보유분의 청산 결과입니다")
        if carryover_context.get("carry_risk_label"):
            cause_lines.append(f"런타임 상태는 {carryover_context.get('carry_state_label')} / {carryover_context.get('carry_risk_label')}로 기록됨")
    if recovered_partial_exit:
        cause_lines.append("보유/회수 포지션의 당일 SELL 결과이며, 신규 매수 선정·진입 판단과 같은 표본으로 보지 않습니다")
    for row in _listify(monitor_memory.get("applied_deltas")):
        row_obj = _as_dict(row)
        if str(row_obj.get("field") or "") == "breakout_buffer_pct" and (_num_opt(row_obj.get("delta")) or 0.0) > 0:
            cause_lines.append(
                "진입 정책은 breakout_buffer "
                f"{_compact_number(row_obj.get('from'))} → {_compact_number(row_obj.get('to'))}로 보수화됨"
            )
            break
    if actual_take_profit:
        cause_lines.append("청산은 목표 수익 실현 기준으로 실행됨")
    elif actual_peak_exit:
        cause_lines.append("청산은 peak_drawdown 축으로 실행됨")
    elif actual_hard_stop:
        cause_lines.append("청산은 고정 손절 기준으로 실행됨")
    if selection_fallback_summary.get("used") or (rank_num is not None and rank_num > 1):
        if scanner_top_pick and scanner_top_pick != "-":
            cause_lines.append(f"{scanner_top_pick} 보류 후 {symbol}에서 진입 조건이 충족됨")
        else:
            cause_lines.append("상위 후보 탈락 후 차순위 후보에서 진입이 성립됨")
    if cost_analysis.get("mock_cost_warning") and cost_drag_pct is not None:
        cause_lines.append(f"모의투자 수수료/세금이 손익률을 {_fmt_pct(cost_drag_pct)} 압박")
    if not cause_lines:
        cause_lines.append("진입/청산 구조의 반복성은 당일 패턴 섹션에서 추가 확인 필요")

    recommendations: List[str] = []
    if carryover_exit:
        recommendations.append("오버나이트 승인 시각/근거와 당일 청산 컨텍스트를 분리해 검증")
    if recovered_partial_exit:
        recommendations.append("회수/partial 청산은 완료 거래와 별도 집계해 승패와 평균 수익률을 확인")
    if cost_analysis.get("mock_cost_warning"):
        recommendations.append("모의투자 비용 기준과 실계좌 추정 비용 기준 분리 확인")
    if actual_peak_exit:
        recommendations.append("peak_drawdown activation/confirm 조건 점검")
    if "pullback_not_mature" in entry_blob:
        recommendations.append("pullback 조건 완화 또는 성숙도 판정 재검토")
    if selection_fallback_summary.get("used") or (rank_num is not None and rank_num > 1):
        recommendations.append("1순위 보류 사유와 차순위 진입 기대값 비교")
    if monitor_line:
        recommendations.append("monitor_only 비중이 높은 당일 route mix 점검")
    if (not holding_duration_summary or _is_not_captured(holding_duration_summary) or str(holding_duration_summary).strip() in {"0", "0s", "0초"}):
        recommendations.append("보유 구간 모니터 스냅샷 보강")
    if not recommendations:
        recommendations.append("동일 패턴 3건 이상 누적 후 정책 조정 여부 판단")
    recommendations = _dedupe([item for item in recommendations if item])[:4]

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
    lines.append(f"# AI 거래 리포트 ({trade_id})")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔴 운영 요약 (Operator Decision Summary)")
    lines.append("")
    lines.append(f"* 결과: **{result_text}**")
    lines.append(f"* 당일 성과(리포트 생성 시점 기준): **{same_day}**")
    lines.append("")
    lines.append("### ✔ 잘된 점")
    lines.append("")
    lines.extend(f"* {item}" for item in positives[:3])
    lines.append("")
    lines.append("### ❌ 문제점")
    lines.append("")
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(problems[:3], 1))
    lines.append("")
    lines.append("### 📌 원인 해석")
    lines.append("")
    lines.extend(f"* {item}" for item in cause_lines[:4])
    lines.append("")
    headline_focus = recommendations[0] if recommendations else problems[0]
    lines.append(f"👉 **{result_label} 거래; 핵심 점검: {headline_focus}**")
    lines.append("")
    lines.append("### 🛠 권고 액션 (우선순위)")
    lines.append("")
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(recommendations[:4], 1))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🧭 거래 개요")
    lines.append("")
    symbol_line = f"* 종목: {symbol}"
    if symbol_name:
        symbol_line += f" ({symbol_name})"
    lines.append(symbol_line)
    if symbol_theme:
        lines.append(f"* 테마: {symbol_theme}")
    lines.append(f"* 거래 유형: {story_type}")
    lines.append(f"* 상태: {status}")
    lines.append(f"* 실행 모드: {execution_mode}")
    controlled_lane_lines = _render_controlled_lane_report_lines(report)
    if controlled_lane_lines:
        lines.append("")
        lines.append("### 통제 모의투자 레인")
        lines.append("")
        lines.extend(controlled_lane_lines)
    if recovered_partial_exit:
        lines.append(f"* {_RECOVERED_PARTIAL_EXIT_NOTE}")
    if carryover_exit:
        lines.append(f"* 포지션 성격: {carryover_context.get('carry_state_label') or '오버나이트/이월 보유'}")
        if carryover_context.get("estimated_entry_kst") or carryover_context.get("exit_kst"):
            basis = carryover_context.get("date_basis") or "이월 보유 시간 기준"
            lines.append(
                f"* 날짜 기준: 보유 시작 {carryover_context.get('estimated_entry_kst') or '-'} / "
                f"청산 {carryover_context.get('exit_kst') or '-'} ({basis})"
            )
        if carryover_context.get("duration_label"):
            lines.append(f"* 이월 보유 시간: {carryover_context.get('duration_label')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📊 실행 결과 (Truth Surface)")
    lines.append("")
    lines.append(f"* 매수가 / 매도가: {_money(buy_price)} / {_money(exit_price)}{exit_price_note}")
    if pnl_num is None and pnl_pct_is_observation:
        lines.append("* 실현 손익: **확인 불가**")
    else:
        pnl_line = _money(pnl)
        if pnl_pct not in (None, ""):
            pnl_line = f"{pnl_line} ({_fmt_pct(pnl_pct)})"
        lines.append(f"* 실현 손익: **{pnl_line}**")
    fee_display = _money(_pick(shared.get("broker_fee"), truth_pnl.get("broker_fee")))
    tax_display = _money(_pick(shared.get("broker_tax"), truth_pnl.get("broker_tax")))
    lines.append(f"* 수수료 / 세금: {fee_display} / {tax_display}")
    lines.extend(_trade_cost_analysis_lines(report))
    lines.append(f"* 손익 기준: {_pnl_basis_label(truth_pnl, shared)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🧠 전략 및 시장 맥락")
    lines.append("")
    lines.append("### 시장 상태")
    lines.append("")
    lines.append(f"* {market_summary}")
    for korea_line in _korea_index_lines(market):
        lines.append(f"* 국내 지수: {korea_line}")
    if market.get("vix_level") not in (None, ""):
        lines.append(f"* VIX: {_compact_decimal(market.get('vix_level'))}")
    if market.get("market_sentiment"):
        lines.append(f"* 시장 심리: {_metadata_value(market.get('market_sentiment'))}")
    if carryover_exit:
        lines.append(
            f"* 날짜 주의: 위 시장/지수는 {carryover_context.get('exit_date_kst') or '청산일'} 청산 시점 컨텍스트입니다. "
            f"오버나이트 승인 판단은 {carryover_context.get('estimated_entry_date_kst') or '이전 거래일'} 기준과 분리해 봅니다."
        )
    lines.append("")
    lines.append("### 전략가 출력 요약")
    lines.append("")
    lines.append(f"* 플레이북: **{playbook or '-'}**")
    lines.append(f"* 리스크 톤: {risk_tone or '-'}")
    themes = [_theme_label(x) for x in _listify(market.get("themes") or market.get("preferred_themes")) if not _is_not_captured(x)]
    if themes:
        lines.append(f"* 핵심 테마: {', '.join(themes[:4])}")
    theme_source = _metadata_value(market.get("theme_source"))
    theme_status = _metadata_value(market.get("theme_source_status"))
    if theme_source and theme_source != "-":
        source_text = theme_source
        if theme_status and theme_status != "-":
            source_text += f" / {theme_status}"
        lines.append(f"* 테마 출처: {source_text}")
    if monitor_guide:
        lines.append(f"* 모니터 가이드: {monitor_guide}")
    strategy_horizon_lines = _build_strategy_horizon_lines(report, compact=True)
    if strategy_horizon_lines:
        lines.append("")
        lines.append("### 전략 보유 기간")
        lines.append("")
        lines.extend(strategy_horizon_lines)
    if entry_watch_lines and not carryover_exit:
        lines.append(f"* 후보 감시: {entry_watch_lines[0]}")
        if len(entry_watch_lines) > 1:
            lines.append(f"* 후보 선택: {entry_watch_lines[-1]}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📰 뉴스 및 컨텍스트")
    lines.append("")
    lines.append("### 시장 뉴스")
    lines.append("")
    if market_news:
        lines.extend(f"* {item}" for item in market_news)
    else:
        lines.append("* 표본 없음")
        lines.append("* 원천 위치: ai_trade_report_input.json의 market_context_at_entry.market_news_titles")
    lines.append("")
    lines.append(f"### 종목 뉴스 ({symbol})")
    lines.append("")
    if symbol_news:
        lines.extend(f"* {item}" for item in symbol_news)
    else:
        lines.append("* 표본 없음")
        lines.append(f"* 원천 위치: ai_trade_report_input.json의 market_context_at_entry.candidate_news_titles 중 {symbol} 항목")
    lines.append("")
    lines.append("👉 해석:")
    lines.append("")
    if carryover_exit:
        lines.append("* 종목은 오버나이트/주말 이월 포지션 청산 흐름")
        lines.append(f"* 전략은 {playbook or '-'} → **당일 신규 선정이 아니라 보유 포지션 청산 품질 중심으로 확인 필요**")
    elif recovered_partial_exit:
        lines.append("* 종목은 보유/회수 포지션 청산 흐름")
        lines.append(f"* 전략은 {playbook or '-'} → **신규 선정 평가가 아니라 청산 결과 중심으로 확인 필요**")
    else:
        lines.append(f"* 종목은 {_translated_metadata(selection.get('basis') or '후보 점수 우위')} 흐름")
        lines.append(f"* 전략은 {playbook or '-'} → **전략/종목 톤 정합성 점검 필요**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🎯 종목 선정 흐름")
    lines.append("")
    if carryover_exit:
        lines.append("* 선정 경로: 오버나이트/주말 이월 포지션 청산")
        if carryover_context.get("estimated_entry_kst"):
            lines.append(f"* 보유 시작 추정: {carryover_context.get('estimated_entry_kst')} ({carryover_context.get('date_basis')})")
        if carryover_context.get("duration_label"):
            lines.append(f"* 이월 보유 시간: {carryover_context.get('duration_label')}")
        if carryover_context.get("carry_state_label"):
            line = f"* 이월 상태: {carryover_context.get('carry_state_label')}"
            if carryover_context.get("carry_risk_label"):
                line += f" / {carryover_context.get('carry_risk_label')}"
            lines.append(line)
        if carryover_context.get("weekend_carry"):
            lines.append("* 주말 이월: 금요일 보유분이 월요일 청산까지 이어진 거래입니다.")
    elif recovered_partial_exit:
        lines.append("* 선정 경로: 보유/회수 포지션 청산")
        lines.append("* 스캐너 순위: 기록 없음")
    elif selection_fallback.get("used"):
        lines.append("* 선정 경로: 차순위 재평가")
        lines.append(f"* 재평가 순위: {_selected_rank(selection)}위")
        lines.append(f"* 재평가 점수: {_selected_score(selection)}")
    else:
        lines.append(f"* 스캐너 순위: {_selected_rank(selection)}위")
        lines.append(f"* 점수: {_selected_score(selection)}")
    if selection_reason:
        lines.append(f"* 선정 이유: {selection_reason}")
    if scanner_chart_fit:
        lines.append(
            "* Scanner chart-fit: "
            f"{_compact_decimal(scanner_chart_fit.get('score'), 3)} "
            f"/ {scanner_chart_fit.get('authority') or '-'}"
        )
    if selection_fallback.get("used"):
        top_pick = selection_fallback.get("scanner_top_pick_symbol") or "-"
        reason = selection_fallback.get("reason") or "모니터 조건 미충족"
        lines.append(f"* 스캐너 상위 후보 {top_pick} 보류 후 {symbol}이 재평가에서 실제 진입 후보로 확정됐습니다.")
        lines.append(f"* 모니터 확인 사유: {reason}")
        for metric_line in _entry_signal_metric_summary_lines(entry_signal_snapshot, prefix="모니터 확인 수치"):
            lines.append(f"* {metric_line}")
    if blocked_reason:
        lines.append(f"* {blocked_reason}")
    if not selection_fallback.get("used") and not recovered_partial_exit:
        for watch_line in entry_watch_lines[1:3]:
            lines.append(f"* {watch_line}")
    lines.append("")
    if carryover_exit:
        lines.append("👉 특징: **오늘 신규 선정 평가가 아니라 오버나이트/주말 이월 포지션의 청산 결과입니다**")
    elif recovered_partial_exit:
        lines.append("👉 특징: **신규 선정 평가가 아니라 회수 포지션의 청산 결과입니다**")
    else:
        lines.append("👉 특징: **강한 종목이어도 실제 진입 구조와 별도 검증 필요**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🚪 진입 판단")
    lines.append("")
    quant_compact_lines = _render_quant_tactic_report_lines_impl(report, compact=True)
    if quant_compact_lines:
        lines.extend(quant_compact_lines[:4])
    if entry_reason:
        lines.append(f"* 조건: {entry_reason}")
    if not selection_fallback.get("used") and not exit_only_report:
        lines.extend(f"* {item}" for item in entry_signal_metric_lines)
    if carryover_exit:
        lines.append("* 방식: 당일 신규 매수 평가 제외")
        if carryover_context.get("estimated_entry_kst"):
            lines.append("* 원 진입/보유 시작 시각은 리포트 입력의 actual_hold_sec와 청산 시각으로 역산했습니다.")
    elif recovered_partial_exit:
        lines.append("* 방식: 당일 신규 매수 평가 제외")
    else:
        lines.append("* 방식: 돌파/확인형 진입")
        if entry_confidence:
            lines.append(f"* {entry_confidence}")
    lines.append("")
    if carryover_exit:
        lines.append("👉 **신규 진입 판단이 아니라 이월 포지션 청산 리포트입니다.**")
    elif recovered_partial_exit:
        lines.append("👉 **신규 진입 판단이 아니라 회수 포지션 청산 리포트입니다.**")
    else:
        lines.append("👉 **threshold 근접 진입 여부 확인 필요**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ⏱ 보유 및 청산")
    lines.append("")
    if holding_duration and not _is_not_captured(holding_duration):
        lines.append(f"* 보유 시간: {holding_duration}")
    elif carryover_exit and carryover_context.get("duration_label"):
        lines.append(f"* 보유 시간: {carryover_context.get('duration_label')}")
    elif recovered_partial_exit:
        lines.append("* 보유 시간: 기록 없음")
    if carryover_exit and carryover_context.get("estimated_entry_kst"):
        lines.append(f"* 보유 시작 추정: {carryover_context.get('estimated_entry_kst')}")
    lines.append(f"* 청산가: {_money(exit_price)}{exit_price_note}")
    lines.append("")
    lines.append("### 청산 트리거")
    lines.append("")
    exit_trigger_lines = _build_summary_exit_trigger_lines(
        exit_trigger,
        exit_signal_snapshot,
        fallback_reason=shared.get("exit_reason"),
        buy_price=buy_price,
        exit_price=exit_price,
        pnl_pct=pnl_pct,
        truth_source=_pick(shared.get("pnl_truth_source"), truth_pnl.get("pnl_truth_source")),
    )
    if recovered_partial_exit and (_num_opt(pnl_pct) or 0.0) > 0.0 and exit_trigger_lines:
        trigger_text = exit_trigger_lines[0].replace("트리거:", "").strip()
        if trigger_text in {"Stop Loss", "stop_loss", "고정 손절 기준"}:
            trigger_text = "고정 손절 기준"
        exit_trigger_lines[0] = f"트리거: 모니터 신호명은 {trigger_text}이었지만 Truth Surface 기준 실현 결과는 이익입니다."
    lines.extend(f"* {item}" for item in exit_trigger_lines)
    if quant_compact_lines:
        for item in quant_compact_lines[4:8]:
            lines.append(item if item.startswith("* ") else f"* {item.lstrip('- ')}")
    lines.append("")
    lines.append("👉 수익 구간 진입 후 유지/청산 품질 점검 필요")
    shadow_lines = _build_post_exit_shadow_summary_lines(report)
    if shadow_lines:
        lines.append("")
        lines.extend(shadow_lines)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ⚙️ 정책 및 메모리 영향")
    lines.append("")
    lines.extend(_policy_delta_lines(memory_app) if memory_app else ["* 정책/메모리 영향은 상세 리포트에서 확인 필요"])
    lines.append("")
    lines.append("👉 **진입/청산 정책 조합의 손익비 영향 확인 필요**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔁 패턴 분석 (당일)")
    lines.append("")
    lines.append(f"* {same_day}")
    lines.append("")
    lines.append("### 반복 패턴")
    lines.append("")
    pattern_lines = [
        line
        for line in _listify(reporter_eval.get("bullets"))
        if any(token in str(line).lower() for token in ("monitor", "fallback", "blocker", "closed trade", "차순위"))
    ]
    if pattern_lines:
        lines.extend(f"* {_translate_text(line).rstrip('.')}" for line in pattern_lines[:4])
    else:
        lines.append("* 반복 패턴은 추가 집계 필요")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ 주요 리스크")
    lines.append("")
    default_risks = (
        ["이월 승인 근거와 당일 청산 판단의 날짜 혼선 가능성", "장기/주말 이월 상태에서 청산 우선순위 검증 필요"]
        if carryover_exit
        else ["전략 vs 종목 톤 미스매치", "scanner → monitor 정합성 저하 가능성"]
    )
    risk_lines = _dedupe(problems + default_risks)
    lines.extend(f"* {item}" for item in risk_lines[:4])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📌 보완 필요")
    lines.append("")
    lines.extend(f"* {item}" for item in recommendations[:4])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📎 근거 출처")
    lines.append("")
    lines.append("* canonical agent artifacts 기반")
    lines.append("* commander / strategist / scanner / monitor / executor / supervisor 로그")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🧾 타임라인")
    lines.append("")
    lines.append(f"* 진입 run: {_extract_run_id(timeline, 'entry')}")
    lines.append(f"* 청산 run: {_extract_run_id(timeline, 'exit')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔚 최종 판단")
    lines.append("")
    lines.append(f"* 상태: {status}")
    lines.append(f"* 액션: {action}")
    lines.append("")
    final_summary = _authoritative_final_operator_summary(
        report,
        action=action,
        fallback=(
            _ensure_sentence(_translate_text(final.get("summary")))
            if final.get("summary")
            else ""
        ),
    )
    if final_summary:
        lines.append(f"👉 **{final_summary}**")
        lines.append("")
    lines.append(f"👉 **{result_label} 원인은 단일 장애보다 진입/청산 구조와 정책 조합에서 우선 점검해야 합니다.**")
    return "\n".join(_strip_trailing_blanks(lines)).strip() + "\n"


def build_trade_summary_input(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _RECOVERED_PARTIAL_ENTRY_NOTE = deps["RECOVERED_PARTIAL_ENTRY_NOTE"]
    _RECOVERED_PARTIAL_EXIT_NOTE = deps["RECOVERED_PARTIAL_EXIT_NOTE"]
    _action_label = deps["action_label"]
    _applied_label = deps["applied_label"]
    _as_dict = deps["as_dict"]
    _authoritative_final_operator_summary = deps["authoritative_final_operator_summary"]
    _authoritative_hold_duration_seconds = deps["authoritative_hold_duration_seconds"]
    _authoritative_holding_duration_label = deps["authoritative_holding_duration_label"]
    _build_post_exit_shadow_summary_lines = deps["build_post_exit_shadow_summary_lines"]
    _build_strategy_horizon_lines = deps["build_strategy_horizon_lines"]
    _build_summary_exit_trigger_lines = deps["build_summary_exit_trigger_lines"]
    _build_trade_cost_analysis = deps["build_trade_cost_analysis"]
    _carryover_context = deps["carryover_context"]
    _clip = deps["clip"]
    _compact_decimal = deps["compact_decimal"]
    _compact_number = deps["compact_number"]
    _compact_post_exit_shadow = deps["compact_post_exit_shadow"]
    _compact_section = deps["compact_section"]
    _dedupe = deps["dedupe"]
    _enrich_exit_signal_snapshot_from_monitor = deps["enrich_exit_signal_snapshot_from_monitor"]
    _ensure_sentence = deps["ensure_sentence"]
    _entry_confidence_for_operator_summary = deps["entry_confidence_for_operator_summary"]
    _entry_reason_line = deps["entry_reason_line"]
    _entry_signal_metric_summary_lines = deps["entry_signal_metric_summary_lines"]
    _entry_watch_execution_lines = deps["entry_watch_execution_lines"]
    _entry_watch_summary_lines = deps["entry_watch_summary_lines"]
    _execution_mode_label = deps["execution_mode_label"]
    _extract_exit_signal_snapshot = deps["extract_exit_signal_snapshot"]
    _extract_run_id = deps["extract_run_id"]
    _first_matching_line = deps["first_matching_line"]
    _fmt_pct = deps["fmt_pct"]
    _get_truth_surface = deps["get_truth_surface"]
    _is_not_captured = deps["is_not_captured"]
    _is_post_entry_gate_text = deps["is_post_entry_gate_text"]
    _is_recovered_partial_exit_report = deps["is_recovered_partial_exit_report"]
    _korea_index_lines = deps["korea_index_lines"]
    _listify = deps["listify"]
    _memory_layers_text = deps["memory_layers_text"]
    _metadata_value = deps["metadata_value"]
    _money = deps["money"]
    _normalize_entry_confidence_for_operator_summary = deps["normalize_entry_confidence_for_operator_summary"]
    _normalize_exit_trigger_label = deps["normalize_exit_trigger_label"]
    _num_opt = deps["num_opt"]
    _operator_pnl_pct = deps["operator_pnl_pct"]
    _pick = deps["pick"]
    _playbook_label = deps["playbook_label"]
    _pnl_basis_label = deps["pnl_basis_label"]
    _policy_delta_lines = deps["policy_delta_lines"]
    _policy_deltas = deps["policy_deltas"]
    _post_exit_shadow_surface = deps["post_exit_shadow_surface"]
    _quant_tactic_surface_impl = deps["quant_tactic_surface_impl"]
    _render_controlled_lane_report_lines = deps["render_controlled_lane_report_lines"]
    _render_quant_tactic_report_lines_impl = deps["render_quant_tactic_report_lines_impl"]
    _resolve_entry_execution_visibility = deps["resolve_entry_execution_visibility"]
    _resolve_entry_signal_snapshot = deps["resolve_entry_signal_snapshot"]
    _resolve_market_context = deps["resolve_market_context"]
    _resolve_trade_symbol_metadata = deps["resolve_trade_symbol_metadata"]
    _risk_mode_label = deps["risk_mode_label"]
    _same_day_current_result = deps["same_day_current_result"]
    _same_day_summary = deps["same_day_summary"]
    _same_day_summary_from_texts = deps["same_day_summary_from_texts"]
    _sample_news_titles = deps["sample_news_titles"]
    _sample_news_titles_for_symbol = deps["sample_news_titles_for_symbol"]
    _section_texts = deps["section_texts"]
    _selected_rank = deps["selected_rank"]
    _selected_score = deps["selected_score"]
    _selection_fallback_context = deps["selection_fallback_context"]
    _status_label = deps["status_label"]
    _story_type_label = deps["story_type_label"]
    _strategy_horizon_report_surface = deps["strategy_horizon_report_surface"]
    _strip_trailing_blanks = deps["strip_trailing_blanks"]
    _theme_label = deps["theme_label"]
    _trade_cost_analysis_lines = deps["trade_cost_analysis_lines"]
    _translate_text = deps["translate_text"]
    _translated_metadata = deps["translated_metadata"]
    _truth_source_label = deps["truth_source_label"]
    """Build the compact deterministic input that a summary LLM may evaluate."""

    def _pick(*values: Any) -> Any:
        for value in values:
            if value not in (None, ""):
                return value
        return ""

    def _section_texts(*sections: Dict[str, Any]) -> List[str]:
        texts: List[str] = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            summary = _translate_text(section.get("summary")).strip()
            if summary:
                texts.append(summary)
            texts.extend(_translate_text(item).strip() for item in _listify(section.get("bullets")) if str(item or "").strip())
        return texts

    def _same_day_summary(section: Dict[str, Any]) -> str:
        return _same_day_summary_from_texts(
            _section_texts(section),
            current_result=_same_day_current_result(report),
        )

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

    def _policy_deltas(memory_bias: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for row in _listify(memory_bias.get("applied_deltas")) + _listify(memory_bias.get("exit_deltas")):
            row_obj = _as_dict(row)
            field = str(row_obj.get("field") or "").strip()
            if not field:
                continue
            rows.append(
                {
                    "field": field,
                    "from": row_obj.get("from"),
                    "to": row_obj.get("to"),
                    "delta": row_obj.get("delta"),
                }
            )
        return rows[:8]

    def _compact_section(section: Dict[str, Any], *, limit: int = 5) -> Dict[str, Any]:
        return {
            "summary": _translate_text(section.get("summary")).strip(),
            "bullets": [_translate_text(item).strip() for item in _listify(section.get("bullets"))[:limit] if str(item or "").strip()],
        }

    shared = _as_dict(report.get("shared_facts"))
    truth = _get_truth_surface(report)
    truth_price = _as_dict(truth.get("price"))
    truth_pnl = _as_dict(truth.get("pnl"))
    market = _resolve_market_context(report)
    strategist = _as_dict(report.get("strategist_summary"))
    trace_summary = _as_dict(report.get("strategist_trace_summary"))
    selection = _as_dict(report.get("why_this_symbol_was_chosen"))
    entry = _as_dict(report.get("entry_decision"))
    holding = _as_dict(report.get("holding_monitoring_story"))
    exit_decision = _as_dict(report.get("exit_decision"))
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory_app = _as_dict(report.get("memory_application_surface"))
    monitor = _as_dict(report.get("monitor_snapshot"))
    scanner_memory = _as_dict(memory_app.get("scanner_memory_bias"))
    monitor_memory = _as_dict(memory_app.get("monitor_memory_bias"))
    final = _as_dict(report.get("final_operator_conclusion"))
    trade_id = _clip(report.get("trade_id") or report.get("story_id"), 80)
    symbol = _clip(_pick(report.get("symbol"), shared.get("symbol")), 32)
    symbol_metadata = _resolve_trade_symbol_metadata(report, symbol)
    action_label = _action_label(_pick(final.get("current_action"), report.get("action"), shared.get("action")))
    recovered_partial_exit = _is_recovered_partial_exit_report(report)
    carryover_context = _carryover_context(report)
    carryover_exit = bool(carryover_context.get("is_carryover_exit"))
    exit_only_report = recovered_partial_exit or carryover_exit
    day = _clip(report.get("day") or shared.get("day"), 32)
    if not day:
        match = re.search(r"TRD_(\d{4})(\d{2})(\d{2})", trade_id)
        if match:
            day = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    pnl = _pick(truth_pnl.get("value"), shared.get("pnl"))
    pnl_pct, pnl_pct_is_observation = _operator_pnl_pct(truth_pnl, shared)
    pnl_num = _num_opt(pnl)
    pnl_label_basis = pnl_num if pnl_num is not None else _num_opt(pnl_pct)
    result_label = "breakeven"
    if pnl_label_basis is not None and pnl_label_basis > 0:
        result_label = "profit"
    elif pnl_label_basis is not None and pnl_label_basis < 0:
        result_label = "loss"
    truth_source_value = _pick(truth_pnl.get("pnl_truth_source"), shared.get("pnl_truth_source"))
    if pnl_num is None and pnl_pct_is_observation:
        truth_source_value = _pick(
            truth_price.get("price_truth_source"),
            shared.get("price_truth_source"),
            truth_source_value,
        )

    selection_trace = _as_dict(selection.get("scanner_selection_trace"))
    scanner_chart_fit = _as_dict(selection.get("scanner_chart_fit")) or _as_dict(selection_trace.get("scanner_chart_fit"))
    selection_fallback = _selection_fallback_context(selection, _clip(_pick(report.get("symbol"), shared.get("symbol")), 32))
    entry_signal_snapshot = _resolve_entry_signal_snapshot(report)
    selection_rank = _pick(selection.get("selected_rank"), selection_trace.get("selected_rank"), selection.get("scanner_rank"))
    selection_score = _pick(selection.get("score_total"), selection.get("selected_score"))
    if selection_score in (None, "") and selection_fallback.get("used"):
        selection_score = _pick(selection_trace.get("selected_score"), _as_dict(selection_trace.get("news_scanner_contribution")).get("selected_score_total"))
    if exit_only_report:
        selection_rank = None
        selection_score = ""
    selection_texts = _section_texts(selection)
    entry_texts = _section_texts(entry)
    exit_texts = _section_texts(exit_decision)
    exit_signal_snapshot = _extract_exit_signal_snapshot(exit_texts + _section_texts(holding))
    exit_signal_snapshot = _enrich_exit_signal_snapshot_from_monitor(exit_signal_snapshot, monitor)
    post_exit_shadow_summary = _compact_post_exit_shadow(_post_exit_shadow_surface(report))
    strategy_horizon_summary = _strategy_horizon_report_surface(report)
    authoritative_hold_sec = _authoritative_hold_duration_seconds(report)
    authoritative_hold_label = _authoritative_holding_duration_label(report)
    if authoritative_hold_sec is not None:
        strategy_horizon_summary = dict(strategy_horizon_summary)
        strategy_horizon_summary["actual_hold_sec"] = authoritative_hold_sec
        strategy_horizon_summary["actual_hold_label"] = authoritative_hold_label
        strategy_horizon_summary["actual_hold_source"] = "entry_exit_execution_timestamps"
    exit_trigger = _first_matching_line(
        _listify(exit_decision.get("bullets")),
        ["촉발", "트리거", "청산 사유", "peak_drawdown", "고점 대비"],
    )
    if not exit_trigger:
        exit_trigger = _first_matching_line(exit_texts, ["촉발", "트리거", "청산", "peak_drawdown", "고점 대비"])
    exit_trigger_label = _normalize_exit_trigger_label(
        exit_signal_snapshot.get("trigger") or exit_trigger,
        shared.get("exit_reason"),
    )
    reporter_texts = _section_texts(reporter_eval)
    combined_texts = _section_texts(market, strategist, selection, entry, holding, exit_decision, reporter_eval)
    combined_blob = "\n".join(combined_texts).lower()
    entry_execution_visibility = _resolve_entry_execution_visibility(report)
    entry_watch_lines = _entry_watch_execution_lines(
        report,
        require_trade_symbol_match=bool(selection_fallback.get("used")) or bool(exit_only_report),
    )
    broker_alignment = _as_dict(report.get("broker_alignment"))
    broker_alignment_summary = _as_dict(broker_alignment.get("summary"))
    broker_account_snapshot = _as_dict(broker_alignment.get("account_snapshot"))

    deterministic_positives: List[str] = []
    if truth_price.get("broker_fill_price") not in (None, "") or truth_pnl.get("value") not in (None, ""):
        deterministic_positives.append("broker_truth_available")
    if strategist or selection or entry or exit_decision:
        deterministic_positives.append("agent_decision_flow_available")
    if memory_app:
        deterministic_positives.append("policy_memory_surface_available")
    if carryover_exit:
        deterministic_positives.append("carryover_exit_accounted_separately")
    if recovered_partial_exit:
        deterministic_positives.append("recovered_partial_exit_accounted_separately")

    deterministic_problems: List[str] = []
    if "monitor_only" in combined_blob or "monitor-only" in combined_blob or "monitor 단독" in combined_blob:
        deterministic_problems.append("monitor_only_path_ratio_high")
    if recovered_partial_exit:
        deterministic_problems.append("entry_evidence_missing_for_recovered_partial_exit")
    if carryover_exit:
        deterministic_problems.append("carryover_exit_requires_separate_date_basis")
    if "peak_drawdown" in combined_blob or "고점 대비 하락폭" in combined_blob:
        deterministic_problems.append("peak_drawdown_exit_needs_review")
    rank_num = _num_opt(selection_rank)
    scanner_chart_fit_score = _num_opt(scanner_chart_fit.get("score")) if scanner_chart_fit else None
    if rank_num is not None and rank_num > 1:
        deterministic_problems.append("entered_lower_rank_after_top_candidate_block")
    if scanner_chart_fit_score is not None and scanner_chart_fit_score < 0.25:
        deterministic_problems.append("scanner_chart_fit_low")
    if "pullback" in combined_blob:
        deterministic_problems.append("pullback_condition_repeated")

    root_cause_candidates: List[str] = []
    for row in _listify(monitor_memory.get("applied_deltas")):
        row_obj = _as_dict(row)
        if str(row_obj.get("field") or "") == "breakout_buffer_pct" and (_num_opt(row_obj.get("delta")) or 0.0) > 0:
            root_cause_candidates.append("entry_was_tightened_by_breakout_buffer")
            break
    for row in _listify(monitor_memory.get("exit_deltas")):
        row_obj = _as_dict(row)
        if "peak_drawdown" in str(row_obj.get("field") or "") and (_num_opt(row_obj.get("delta")) or 0.0) < 0:
            root_cause_candidates.append("exit_was_tightened_by_peak_drawdown")
            break
    if rank_num is not None and rank_num > 1:
        root_cause_candidates.append("scanner_monitor_reassessment_after_top_rank_block")
    if scanner_chart_fit_score is not None and scanner_chart_fit_score < 0.25:
        root_cause_candidates.append("scanner_selected_candidate_had_weak_chart_fit")
    if recovered_partial_exit:
        root_cause_candidates.append("recovered_partial_exit_excludes_new_entry_assessment")
    if carryover_exit:
        root_cause_candidates.append("carryover_position_excludes_same_day_scanner_selection_assessment")

    validation_questions: List[str] = []
    if recovered_partial_exit:
        validation_questions.append("회수/partial 청산을 완료 거래와 별도 집계했을 때 당일 실현 성과가 어떻게 달라지는가?")
    if carryover_exit:
        validation_questions.append("오버나이트 승인 근거와 당일 청산 컨텍스트가 분리되어 집계됐는가?")
    if "peak_drawdown_exit_needs_review" in deterministic_problems:
        validation_questions.append("peak_drawdown activation/confirm 조건이 실제 손익비를 악화시키는가?")
    if "entered_lower_rank_after_top_candidate_block" in deterministic_problems:
        validation_questions.append("1순위 탈락 후 차순위 진입의 기대값이 충분한가?")
    if "scanner_chart_fit_low" in deterministic_problems:
        validation_questions.append("scanner_chart_fit_score가 낮은 후보가 다른 점수 축 때문에 선택됐는지 확인해야 하는가?")
    if not validation_questions:
        validation_questions.append("진입/청산 정책 조합이 당일 반복 손익 패턴과 일치하는가?")

    return {
        "schema_version": "ai_trade_summary_input.v1",
        "artifact_type": "ai_trade_summary_input",
        "source_artifact": "ai_trade_report.json",
        "trade": {
            "trade_id": trade_id,
            "day": day,
            "symbol": _clip(_pick(report.get("symbol"), shared.get("symbol")), 32),
            "symbol_name": str(symbol_metadata.get("symbol_name") or ""),
            "theme": str(symbol_metadata.get("theme") or ""),
            "themes": list(symbol_metadata.get("themes") or []),
            "status": _status_label(_pick(report.get("status"), shared.get("status"))),
            "story_type": _story_type_label(report.get("story_type")),
            "execution_mode": _execution_mode_label(report.get("execution_mode_label")),
            "action": action_label,
            "recovered_partial_exit": recovered_partial_exit,
            "carryover_exit": carryover_exit,
            "carryover_context": carryover_context,
            "entry_assessment_scope": (
                "excluded_carryover_exit"
                if carryover_exit
                else ("excluded_recovered_partial" if recovered_partial_exit else "normal")
            ),
        },
        "truth_surface": {
            "result_label": result_label,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "pnl_pct_text": _fmt_pct(pnl_pct),
            "buy_price": _pick(truth_price.get("broker_buy_price"), shared.get("broker_buy_price")),
            "sell_price": _pick(truth_price.get("broker_fill_price"), shared.get("broker_fill_price")),
            "monitor_sell_reference_price": _pick(
                truth_price.get("monitor_mark_price"),
                shared.get("monitor_mark_price"),
                exit_signal_snapshot.get("monitor_current_price"),
            ),
            "fee": _pick(shared.get("broker_fee"), truth_pnl.get("broker_fee")),
            "tax": _pick(shared.get("broker_tax"), truth_pnl.get("broker_tax")),
            "cost_analysis": _build_trade_cost_analysis(report),
            "truth_source": _truth_source_label(truth_source_value),
        },
        "same_day_context": {
            "summary": _same_day_summary(reporter_eval),
            "label": "당일 성과(리포트 생성 시점 기준)",
            "basis": "report_generation_time",
            "reporter_evaluation": _compact_section(reporter_eval, limit=6),
        },
        "broker_alignment": {
            "status": _metadata_value(broker_alignment.get("status")),
            "generated_at": _metadata_value(broker_alignment.get("generated_at")),
            "report_json_path": _metadata_value(broker_alignment.get("report_json_path")),
            "account_snapshot_path": _metadata_value(broker_account_snapshot.get("path")),
            "account_snapshot_status": _metadata_value(broker_account_snapshot.get("status")),
            "account_snapshot_api_call_count": broker_account_snapshot.get("api_call_count"),
            "account_snapshot_ok_count": broker_account_snapshot.get("ok_count"),
            "account_snapshot_error_count": broker_account_snapshot.get("error_count"),
            "local_total": broker_alignment_summary.get("local_total"),
            "broker_total": broker_alignment_summary.get("broker_total"),
            "matched_by_ord_no": broker_alignment_summary.get("matched_by_ord_no"),
            "missing_in_local_total": broker_alignment_summary.get("missing_in_local_total"),
            "missing_in_broker_total": broker_alignment_summary.get("missing_in_broker_total"),
            "error": _metadata_value(broker_alignment.get("error")),
        },
        "market_and_strategy": {
            "market_summary": _translate_text(market.get("summary")).strip(),
            "vix": market.get("vix_level"),
            "market_sentiment": _metadata_value(market.get("market_sentiment")),
            "playbook": _playbook_label(_pick(market.get("playbook"), market.get("selected_playbook"))),
            "risk_tone": _risk_mode_label(_pick(market.get("risk_tone"), trace_summary.get("risk_tone"), market.get("risk_mode"))),
            "monitor_guidance": _metadata_value(_pick(trace_summary.get("monitor_guidance"), market.get("monitor_guidance"))),
            "themes": [_theme_label(x) for x in _listify(market.get("themes")) if not _is_not_captured(x)],
            "preferred_themes": [_theme_label(x) for x in _listify(market.get("preferred_themes")) if not _is_not_captured(x)],
            "theme_source": _metadata_value(market.get("theme_source")),
            "theme_source_status": _metadata_value(market.get("theme_source_status")),
            "theme_strength_top_themes": [_theme_label(x) for x in _listify(market.get("theme_strength_top_themes")) if not _is_not_captured(x)],
            "market_news_titles": _sample_news_titles(market.get("market_news_titles") or report.get("strategist_market_headlines"), limit=4),
            "symbol_news_titles": _sample_news_titles_for_symbol(
                symbol,
                market.get("symbol_news_titles"),
                report.get("strategist_symbol_headlines"),
                market.get("candidate_news_titles"),
                limit=4,
            ),
        },
        "decision_flow": {
            "scanner_rank": selection_rank,
            "scanner_score": selection_score,
            "scanner_chart_fit": scanner_chart_fit,
            "scanner_chart_fit_score": scanner_chart_fit.get("score") if scanner_chart_fit else None,
            "scanner_chart_fit_authority": scanner_chart_fit.get("authority") if scanner_chart_fit else "",
            "scanner_rank_basis": (
                "carryover_exit_no_same_day_entry"
                if carryover_exit
                else "recovered_partial_no_entry_evidence"
                if recovered_partial_exit
                else ("monitor_fallback_reassessment" if selection_fallback.get("used") else "scanner_rank")
            ),
            "selection_path": (
                "carryover_exit"
                if carryover_exit
                else "recovered_partial_exit"
                if recovered_partial_exit
                else selection_fallback.get("selection_path") or _metadata_value(selection_trace.get("selection_path"))
            ),
            "scanner_top_pick_symbol": selection_fallback.get("scanner_top_pick_symbol"),
            "monitor_fallback_reason": selection_fallback.get("reason"),
            "selection_basis": (
                "오버나이트/주말 이월 포지션 청산"
                if carryover_exit
                else ("보유/회수 포지션 청산" if recovered_partial_exit else _translated_metadata(selection.get("basis")))
            ),
            "selection_blocker": (
                ""
                if exit_only_report
                else (
                f"스캐너 상위 후보 {selection_fallback.get('scanner_top_pick_symbol')} 보류 후 재평가"
                if selection_fallback.get("used")
                else _first_matching_line(selection_texts + entry_texts, ["1순위", "top pick", "blocked", "막혔"])
                )
            ),
            "entry_reason": (
                "오늘 신규 진입 판단이 아니라 전일/주말 이월 포지션입니다."
                if carryover_exit
                else (_RECOVERED_PARTIAL_ENTRY_NOTE if recovered_partial_exit else _entry_reason_line(entry_texts))
            ),
            "entry_confidence": _entry_confidence_for_operator_summary(
                entry_texts,
                action=action_label,
                buy_price=_pick(truth_price.get("broker_buy_price"), shared.get("broker_buy_price")),
            )
            if not exit_only_report
            else "",
            "entry_observation": entry_signal_snapshot,
            "holding_duration": authoritative_hold_label or _pick(
                shared.get("holding_duration"),
                report.get("hold_duration"),
                carryover_context.get("duration_label"),
            ),
            "exit_reason": exit_trigger_label,
            "exit_trigger": exit_trigger_label,
            "exit_trigger_basis": "monitor_signal_snapshot_not_realized_result",
            "exit_result_note": (
                "모니터 신호명과 별개로 Truth Surface 기준 실현 결과는 이익입니다."
                if recovered_partial_exit and (_num_opt(pnl_pct) or 0.0) > 0.0
                else ""
            ),
            "entry_execution_visibility": entry_execution_visibility,
            "entry_watch_summary_lines": entry_watch_lines,
            "recovered_partial_note": _RECOVERED_PARTIAL_EXIT_NOTE if recovered_partial_exit else "",
            "carryover_note": "오버나이트/주말 이월 포지션 청산은 당일 신규 스캐너 선정 평가에서 제외합니다." if carryover_exit else "",
            "carryover_context": carryover_context,
            "exit_observation": exit_signal_snapshot,
            "final_operator_summary": _authoritative_final_operator_summary(
                report,
                action=action_label,
                fallback=_translate_text(final.get("summary")).strip(),
            ),
        },
        "strategy_horizon": strategy_horizon_summary,
        "post_exit_shadow": post_exit_shadow_summary,
        "quant_tactic": _quant_tactic_surface_impl(report),
        "memory_and_policy": {
            "scanner_memory_applied": bool(scanner_memory.get("applied")),
            "monitor_memory_applied": bool(monitor_memory.get("applied")),
            "monitor_active_layers": list(monitor_memory.get("active_layers") or []),
            "monitor_policy_deltas": _policy_deltas(monitor_memory),
        },
        "deterministic_findings": {
            "positives": deterministic_positives,
            "problems": deterministic_problems,
            "root_cause_candidates": root_cause_candidates,
            "validation_questions": validation_questions,
            "raw_reporter_pattern_lines": [_translate_text(line).strip() for line in reporter_texts[:6] if line],
        },
        "llm_task": {
            "purpose": "Fill only the interpretation fields for ai_trade_summary evaluation.",
            "allowed_output_fields": [
                "conclusion",
                "root_cause",
                "priority_actions",
                "risk_notes",
                "validation_questions",
            ],
            "hard_constraints": [
                "Do not invent or modify prices, pnl, fees, taxes, timestamps, or order facts.",
                "Use truth_surface as immutable fact.",
                "Treat decision_flow.exit_observation as monitor_signal_snapshot only, not as broker fill or realized pnl.",
                "Treat strategy_horizon as strategy intent and observation-only report visibility; do not treat it as forced hold unless allow_behavior_change is true.",
                "Treat post_exit_shadow as observation-only evidence, not as a live behavior-change rule.",
                "If trade.carryover_exit is true, separate the original carry/overnight date basis from the current-day exit context.",
                "If evidence is weak, state that validation is required instead of asserting causality.",
                "Keep output operator-facing and concise.",
            ],
        },
    }


