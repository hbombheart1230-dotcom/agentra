"""P15 RF-035 (23h): market_regime_rail_review.render_market_regime_rail_markdown moved to market_regime_rail_review_markdown_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import market_regime_rail_review as m
from libs.reporting import market_regime_rail_review_markdown_projection as owner


def _both(rail, day="2026-10-30"):
    return m.render_market_regime_rail_markdown(rail, day=day), owner.render_market_regime_rail_markdown(rail, day=day, facade=m)


def test_empty_rail():
    a, b = _both({})
    assert a == b and a.startswith("# Market Regime Rail Review (2026-10-30)\n\nThis report is read-only evaluation output.")
    assert "- behavior_effect: `evaluation_only`" in a and "- rail_id: `not_available`" in a and "- kospi_pct: **0.0000**" in a
    assert a.endswith("## Q8 Review Focus\n")


def test_full_rail_bytes():
    rail = {"rail_id": "r", "rail_confidence": "high", "source": "s", "rationale": "why", "market_inputs": {"kospi_pct": 1.23456, "krx_night_futures_status": "ok", "krx_night_futures_pressure": "up"},
            "market_input_sanity": {"warnings": [{"code": "C", "index": "KOSPI", "change_pct": 9.5, "severity": "high"}] + ["x"] * 10, "extreme_move_requires_confirmation": True},
            "expected_tactical_behavior": ["a", "b"], "q8_review_focus": ["f"]}
    snap = copy.deepcopy(rail)
    a, b = _both(rail)
    assert a == b and rail == snap
    assert "- kospi_pct: **1.2346**" in a and "- krx_night_futures_status: `ok`" in a and "- krx_night_futures_pressure: `up`" in a
    assert "## Market Input Sanity" in a and "- status: `warning`" in a and "- extreme_move_requires_confirmation: `True`" in a
    assert "- warning: `C` KOSPI change_pct=9.5000 severity=`high`" in a
    assert a.index("## Expected Tactical Behavior") < a.index("- a") < a.index("## Q8 Review Focus") < a.index("- `f`")
    assert a.endswith("- `f`\n")


def test_invalid_numeric_raises_same():
    for call in (lambda: m.render_market_regime_rail_markdown({"market_inputs": {"kospi_pct": "bad"}}, day="d"),
                 lambda: owner.render_market_regime_rail_markdown({"market_inputs": {"kospi_pct": "bad"}}, day="d", facade=m)):
        with pytest.raises(ValueError):
            call()


def test_keyword_only_day():
    with pytest.raises(TypeError):
        m.render_market_regime_rail_markdown({}, "d")


def test_facade_mapping_seam(monkeypatch):
    class Never:
        pass

    monkeypatch.setattr(m, "Mapping", Never)
    a, b = _both({"market_inputs": {"kospi_pct": 5}})
    assert a == b and "- kospi_pct: **0.0000**" in a
