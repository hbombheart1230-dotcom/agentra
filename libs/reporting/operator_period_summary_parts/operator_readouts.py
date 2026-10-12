"""Operator summary readout and label fallback text (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _operator_readout_r3_impl(*, trade_count, avg_return_pct, win_rate, exit_counts, entry_counts, facade):
    positives: List[str] = []
    issues: List[str] = []
    actions: List[str] = []

    if trade_count > 0:
        positives.append("기간 내 체결/청산 기록이 운영 요약으로 연결됐습니다.")
    if entry_counts:
        positives.append("진입 패턴과 선택 사유가 집계 가능할 만큼 누적됐습니다.")
    if avg_return_pct < 0:
        issues.append("완료 거래 기준 평균 수익률이 음수입니다.")
    if win_rate < 0.2 and trade_count > 0:
        issues.append("승률이 낮아 현재 진입-청산 조합의 기대값 점검이 필요합니다.")
    if any(("peak_drawdown" in name or "고점 대비" in name) for name, _ in exit_counts.most_common(3)):
        issues.append("peak_drawdown 청산이 상위 반복 패턴입니다.")
        actions.append("peak_drawdown 발동 조건과 보유 유지 조건을 함께 재검토합니다.")
    if any(("breakout" in name or "돌파" in name) for name, _ in entry_counts.most_common(3)):
        actions.append("breakout 진입 후 유지 실패가 반복되는지 종목별로 분리해 봅니다.")
    if not actions:
        actions.append("기간 내 주요 손익 기여 종목과 exit 사유를 우선 검수합니다.")

    root_cause = "후보 포착 자체보다 진입 이후 보유/청산 밸런스가 성과를 제한하는 구조로 보입니다."
    if avg_return_pct >= 0:
        root_cause = "성과는 방어됐으나 반복 패턴이 유지되는지 다음 기간까지 확인이 필요합니다."

    return {
        "good_points": positives or ["집계 가능한 거래 표본이 아직 부족합니다."],
        "issues": issues or ["치명적인 반복 손실 패턴은 아직 집계되지 않았습니다."],
        "root_cause": root_cause,
        "recommended_actions": actions,
    }


def _operator_label_fallback_r3_impl(value, *, axis, facade):
    text = facade._text_value(value)
    if not text:
        return ""
    if not facade._looks_like_mojibake(text):
        return text
    lowered = text.lower()
    if "entry evidence was not captured" in lowered or "position context was inferred" in lowered:
        return ""
    if "pending exit lock" in lowered:
        return "pending_exit_lock"
    if "sell reconciled from kiwoom day trade diary" in lowered:
        return "broker_day_trade_diary_closed"
    if "broker day trade diary" in lowered:
        return "broker_day_trade_diary_closed"
    if "exit_trigger_not_captured" in lowered or "monitor_exit_trigger_not_captured" in lowered:
        return "monitor_exit_trigger_not_captured"
    if "sell_execution_confirmed" in lowered or "full_sell_quantity_reconciled" in lowered:
        return "monitor_exit_trigger_not_captured"
    if "intraday_low_break" in lowered or "?μ쨷" in text:
        return "intraday_low_break"
    if "vwap_breakdown" in lowered or "vwap ?댄깉" in lowered:
        return "vwap_breakdown"
    if "hard_stop" in lowered or "stop_loss" in lowered or "怨좎젙" in text or "?먯젅" in text:
        return "stop_loss"
    if "take_profit" in lowered or "?듭젅" in text:
        return "take_profit"
    if "vwap" in lowered and ("breakout" in lowered or "?뚰뙆" in text or "怨좎젏" in text):
        return "breakout_vwap_volume_confirmation"
    if "vwap" in lowered and ("pullback" in lowered or "?뚮" in text):
        return "pullback_vwap_volume_confirmation"
    if "breakout" in lowered or "?뚰뙆" in text:
        return "breakout"
    if "pullback" in lowered or "?뚮" in text:
        return "pullback"
    if axis == "exit":
        return "unreadable_exit_label"
    if axis == "entry":
        return "unreadable_entry_label"
    return "unreadable_operator_label"
