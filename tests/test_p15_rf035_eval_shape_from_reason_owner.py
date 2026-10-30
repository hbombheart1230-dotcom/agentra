"""P15 RF-035: strategist_llm_evaluation._shape_from_reason moved to strategist_llm_evaluation_rows; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_rows as owner


@pytest.mark.parametrize("reason,axis,expected", [
    ("breakout_late", "", "breakout"), ("", "pullback_structure", "pullback"), ("", "", "other"),
    ("pullback_not_mature", "", "pullback"), ("below_vwap_reclaim_not_ready", "", "vwap_reclaim"), ("", "vwap_relationship", "vwap_reclaim"),
    ("volume_insufficient", "", "volume_confirmation"), ("", "breakout_readiness", "breakout"), ("none", "unknown", "other"),
    ("pullback_below_vwap_reclaim_not_ready", "vwap_relationship", "pullback"),
])
def test_values(reason, axis, expected):
    assert m._shape_from_reason(reason, axis) == owner._shape_from_reason(reason, axis, facade=m) == expected


def test_facade_text_seam(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "_text", lambda v: (seen.append(v), "breakout_x")[1] if v == "r" else "")
    assert m._shape_from_reason("r", "a") == "breakout"
    assert owner._shape_from_reason("r", "a", facade=m) == "breakout"
    assert seen == ["r", "r"]
