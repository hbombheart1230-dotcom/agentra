"""Daily report generator broker-closed symbol and residual position projections (moved verbatim from daily_report_generator).

``normalize_symbol`` is resolved on ``facade`` (the daily_report_generator module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _broker_closed_symbols_from_alignment(broker_alignment: Dict[str, Any] | None, *, facade: Any) -> set[str]:
    if not isinstance(broker_alignment, dict):
        return set()
    snapshot = broker_alignment.get("account_snapshot") if isinstance(broker_alignment.get("account_snapshot"), dict) else {}
    symbols = snapshot.get("day_trade_closed_symbols") if isinstance(snapshot.get("day_trade_closed_symbols"), list) else []
    out = {
        facade.normalize_symbol(symbol, allow_test_symbols=True)
        for symbol in symbols
        if facade.normalize_symbol(symbol, allow_test_symbols=True)
    }
    rows = snapshot.get("day_trade_diary_rows") if isinstance(snapshot.get("day_trade_diary_rows"), list) else []
    for row in rows:
        if not isinstance(row, dict) or not bool(row.get("closed_by_day_trade_diary")):
            continue
        symbol = facade.normalize_symbol(row.get("symbol"), allow_test_symbols=True)
        if symbol:
            out.add(symbol)
    return out


def _render_residual_positions_markdown(residual: Dict[str, Any]) -> List[str]:
    positions = residual.get("positions") if isinstance(residual.get("positions"), list) else []
    lines = ["", "## 장마감 잔여 보유 종목", ""]
    if not bool(residual.get("available")):
        lines.append("- 상태 스냅샷을 읽지 못해 잔여 보유 종목을 확인하지 못했습니다.")
        return lines
    if not positions:
        lines.append("- 장마감 기준 잔여 보유 종목이 없습니다.")
        return lines
    closeout = residual.get("closeout_state") if isinstance(residual.get("closeout_state"), dict) else {}
    reconciled = (
        residual.get("reconciled_closed_positions")
        if isinstance(residual.get("reconciled_closed_positions"), list)
        else []
    )
    closeout_mode = str(closeout.get("mode") or "").strip()
    closeout_reason = str(closeout.get("reason") or "").strip()
    if closeout_mode or closeout_reason:
        closeout_line = f"- closeout 상태: {closeout_mode or '-'} / {closeout_reason or '-'}"
        closeout_note = str(closeout.get("report_note") or "").strip()
        if closeout_note:
            closeout_line += f" ({closeout_note})"
        lines.append(closeout_line)
    if reconciled:
        symbols = ", ".join(
            str(row.get("symbol") or "").strip()
            for row in reconciled
            if isinstance(row, dict) and str(row.get("symbol") or "").strip()
        )
        if symbols:
            lines.append(f"- 장중 청산 확인: {symbols}는 당일 전량 매도 기록으로 잔여 보유에서 제외했습니다.")
    for row in positions:
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or "-")
        status = str(row.get("status") or "잔여 보유")
        qty = int(row.get("qty") or 0)
        avg_price = row.get("avg_price")
        current_price = row.get("current_price")
        pnl_ratio = row.get("account_pnl_ratio")
        reason = str(row.get("overnight_reason") or "").strip()
        decision_label = str(row.get("overnight_decision_label") or "").strip()
        price_text = f"평균 {avg_price:,.0f}" if isinstance(avg_price, (int, float)) and avg_price else "평균 -"
        current_text = f"현재 {current_price:,.0f}" if isinstance(current_price, (int, float)) and current_price else "현재 -"
        ratio_text = f" / 평가 손익률 {float(pnl_ratio) * 100:.2f}%" if isinstance(pnl_ratio, (int, float)) else ""
        detail = f"- {symbol}: {status} / {qty}주 / {price_text} / {current_text}{ratio_text}"
        if decision_label:
            detail += f" / 오버나이트 판단: {decision_label}"
        if reason and not bool(row.get("overnight_decision_missing")):
            detail += f" / 사유 {reason}"
        if bool(row.get("weekend_carry")):
            detail += f" / 주말 보유 {int(row.get('holding_gap_days') or 3)}일"
        lines.append(detail)
        if bool(row.get("weekend_carry")) and not bool(row.get("allow_weekend_carry")):
            lines.append("  - 주의: 금요일 carry 승인이라 주말 갭 리스크가 포함됩니다.")
        missing_detail = str(row.get("overnight_missing_detail") or "").strip()
        if bool(row.get("overnight_decision_missing")) and missing_detail:
            lines.append(f"  - 판단 기록 근거: {missing_detail}")
        signals = [str(x) for x in list(row.get("overnight_positive_signals") or []) if str(x or "").strip()]
        blockers = [str(x) for x in list(row.get("overnight_blockers") or []) if str(x or "").strip()]
        if signals:
            lines.append(f"  - 승인 근거: {', '.join(signals[:5])}")
        if blockers:
            lines.append(f"  - 차단/주의 근거: {', '.join(blockers[:5])}")
    return lines
