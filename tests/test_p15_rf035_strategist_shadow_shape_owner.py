"""P15 RF-035: strategist_llm_evaluation._shadow_shape_diagnostics moved to strategist_llm_evaluation_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_projection as owner


ROWS = [
    {"reason": "breakout_late", "would_enter": "yes", "opening_momentum_probe_would_enter": True},
    {"reason": "volume_confirmation_missing", "would_enter": False},
]


def _both(rows):
    return m._shadow_shape_diagnostics(rows), owner._shadow_shape_diagnostics(rows, facade=m)


def test_values_and_key_order():
    a, b = _both(ROWS)
    assert a == b and list(a) == ["candidate_count", "by_shape", "would_enter_by_shape", "opening_would_enter_count"]
    assert a["candidate_count"] == 2 and a["opening_would_enter_count"] == 1
    assert {r["name"] for r in a["by_shape"]} == {"breakout", "volume_confirmation"}
    assert a["would_enter_by_shape"] == [{"name": "breakout", "count": 1}]


def test_empty():
    a, b = _both([])
    assert a == b == {"candidate_count": 0, "by_shape": [], "would_enter_by_shape": [], "opening_would_enter_count": 0}


def test_facade_bool_seam(monkeypatch):
    monkeypatch.setattr(m, "_bool", lambda v: False)
    a, b = _both(ROWS)
    assert a == b and a["would_enter_by_shape"] == [] and a["opening_would_enter_count"] == 0
