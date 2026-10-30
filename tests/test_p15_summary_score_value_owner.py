"""P15: strategist_llm_summary _score_value moved to strategist_llm_summary_legacy_scores.score_value; parity with the pre-move body."""
from __future__ import annotations

import math

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_legacy_scores as owner


def test_values():
    for fn in (m._score_value, owner.score_value):
        assert fn("2.5") == 2.5 and fn(True) == 1.0
        assert fn("bad") == float("-inf") and fn(None) == float("-inf")
        assert math.isnan(fn(float("nan")))
        assert fn(float("inf")) == float("inf")


def test_score_label_facade_seam(monkeypatch):
    monkeypatch.setattr(m, "_score_value", lambda v: 7.0)
    assert m._score_label("zzz") == "7"
