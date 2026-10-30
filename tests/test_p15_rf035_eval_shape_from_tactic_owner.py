"""P15 RF-035: strategist_llm_evaluation._shape_from_tactic moved to strategist_llm_evaluation_rows; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_rows as owner


@pytest.mark.parametrize("tactic,expected", [
    ("opening_gap_momentum", "opening"), ("defensive_observe", "defensive"), ("", "unavailable"), ("theme_leader_pullback", "vwap_reclaim"),
    ("opening_range_breakout", "breakout"), ("lower_vwap_rebound_probe", "lower_rebound"), ("custom_x", "custom_x"), (None, "unavailable"), ("unknown", "unavailable"),
])
def test_values(tactic, expected):
    assert m._shape_from_tactic(tactic) == owner._shape_from_tactic(tactic, facade=m) == expected


def test_facade_text_seam(monkeypatch):
    monkeypatch.setattr(m, "_text", lambda v: "defensive_observe")
    assert m._shape_from_tactic("zzz") == "defensive"
    assert owner._shape_from_tactic("zzz", facade=m) == "defensive"
