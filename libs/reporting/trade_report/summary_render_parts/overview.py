from __future__ import annotations

from typing import Any


def append_summary_overview(
    *,
    lines: Any, _RECOVERED_PARTIAL_EXIT_NOTE: Any, _fmt_pct: Any, _money: Any,
    _pick: Any, _pnl_basis_label: Any, _render_controlled_lane_report_lines: Any, _trade_cost_analysis_lines: Any,
    buy_price: Any, carryover_context: Any, carryover_exit: Any, cause_lines: Any,
    execution_mode: Any, exit_price: Any, exit_price_note: Any, pnl: Any,
    pnl_num: Any, pnl_pct: Any, pnl_pct_is_observation: Any, positives: Any,
    problems: Any, recommendations: Any, recovered_partial_exit: Any, report: Any,
    result_label: Any, result_text: Any, same_day: Any, shared: Any,
    status: Any, story_type: Any, symbol: Any, symbol_name: Any,
    symbol_theme: Any, trade_id: Any, truth_pnl: Any,
) -> None:
    """Append canonical Markdown section text in the original statement order."""
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
