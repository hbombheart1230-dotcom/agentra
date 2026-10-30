"""P15 RF-035 (21h): strategist_llm_evaluation._tactic moved to strategist_llm_evaluation_extra_projection; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_extra_projection as owner


@pytest.mark.parametrize("row,expected", [
    ({"quant_tactic_id": "opening_gap_momentum"}, "opening_gap_momentum"), ({"tactical_strategy": "breakout"}, "breakout"), ({}, ""),
    ({"quant_tactic_id": "a", "tactical_strategy": "b"}, "a"), ({"quant_tactic_id": "none", "tactical_strategy": "b"}, ""), ({"quant_tactic_id": "", "tactical_strategy": " b "}, "b"),
])
def test_values(row, expected):
    assert m._tactic(row) == owner._tactic(row, facade=m) == expected


def test_facade_text_seam(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "_text", lambda v: (seen.append(v), "T")[1])
    assert m._tactic({"quant_tactic_id": "q"}) == "T" and owner._tactic({"quant_tactic_id": "q"}, facade=m) == "T"
    assert seen == ["q", "q"]
