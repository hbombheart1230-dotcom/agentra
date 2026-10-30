"""P15 RF-035 (23h): daily_report_generator._render_residual_positions_markdown moved to daily_report_generator_trade_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import daily_report_generator as m
from libs.reporting import daily_report_generator_trade_projection as owner


def _both(x):
    return m._render_residual_positions_markdown(x), owner._render_residual_positions_markdown(x)


def test_unavailable_and_empty():
    h = ["", "## 장마감 잔여 보유 종목", ""]
    assert _both({"available": False}) == (h + ["- 상태 스냅샷을 읽지 못해 잔여 보유 종목을 확인하지 못했습니다."],) * 2
    assert _both({"available": True, "positions": []}) == (h + ["- 장마감 기준 잔여 보유 종목이 없습니다."],) * 2
    assert _both({}) == (h + ["- 상태 스냅샷을 읽지 못해 잔여 보유 종목을 확인하지 못했습니다."],) * 2


def test_position_row_formatting_and_weekend_warning():
    residual = {"available": True, "positions": [{"symbol": "005930", "status": "보유", "qty": 2, "avg_price": 1000, "current_price": 1100,
                "account_pnl_ratio": 0.1, "weekend_carry": True, "holding_gap_days": 3, "overnight_decision_label": "carry", "overnight_reason": "ok",
                "overnight_positive_signals": ["a", "b"], "overnight_blockers": ["x", ""]}, "bad-row"],
                "closeout_state": {"mode": "m", "reason": "r", "report_note": "n"}, "reconciled_closed_positions": [{"symbol": "000660"}, {"symbol": ""}]}
    snap = copy.deepcopy(residual)
    a, b = _both(residual)
    assert a == b and residual == snap
    text = "\n".join(a)
    assert "2주" in text and "평가 손익률 10.00%" in text and "평균 1,000" in text and "현재 1,100" in text
    assert "주말 보유 3일" in text and "주의: 금요일 carry 승인이라 주말 갭 리스크가 포함됩니다." in text
    assert "- closeout 상태: m / r (n)" in text and "장중 청산 확인: 000660는" in text
    assert "승인 근거: a, b" in text and "차단/주의 근거: x" in text and "오버나이트 판단: carry" in text and "사유 ok" in text


def test_missing_decision_detail_and_defaults():
    residual = {"available": True, "positions": [{"overnight_decision_missing": True, "overnight_missing_detail": "d", "overnight_reason": "hidden"}]}
    a, b = _both(residual)
    assert a == b and a[-2] == "- -: 잔여 보유 / 0주 / 평균 - / 현재 -" and a[-1] == "  - 판단 기록 근거: d"


def test_invalid_qty_raises_same():
    residual = {"available": True, "positions": [{"symbol": "x", "qty": "invalid"}]}
    for fn in (m._render_residual_positions_markdown, owner._render_residual_positions_markdown):
        with pytest.raises(ValueError):
            fn(residual)
