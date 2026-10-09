from __future__ import annotations

from typing import Any


def append_summary_decision_lifecycle(
    *,
    lines: Any, _build_post_exit_shadow_summary_lines: Any, _build_summary_exit_trigger_lines: Any, _compact_decimal: Any,
    _entry_signal_metric_summary_lines: Any, _is_not_captured: Any, _money: Any, _num_opt: Any,
    _pick: Any, _render_quant_tactic_report_lines_impl: Any, _selected_rank: Any, _selected_score: Any,
    blocked_reason: Any, buy_price: Any, carryover_context: Any, carryover_exit: Any,
    entry_confidence: Any, entry_reason: Any, entry_signal_metric_lines: Any, entry_signal_snapshot: Any,
    entry_watch_lines: Any, exit_only_report: Any, exit_price: Any, exit_price_note: Any,
    exit_signal_snapshot: Any, exit_trigger: Any, holding_duration: Any, pnl_pct: Any,
    recovered_partial_exit: Any, report: Any, scanner_chart_fit: Any, selection: Any,
    selection_fallback: Any, selection_reason: Any, shared: Any, symbol: Any,
    truth_pnl: Any,
) -> None:
    """Append canonical Markdown section text in the original statement order."""
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
