"""P15 RF-035: strategist_llm_evaluation._tactic_performance moved to strategist_llm_evaluation_projection; parity with the pre-move body."""
from __future__ import annotations

import copy

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_projection as owner


ROWS = [
    {"quant_tactic_id": "opening_gap_momentum", "result_pct": 2},
    {"quant_tactic_id": "opening_gap_momentum", "result_pct": -1},
    {"tactical_strategy": "defensive_observe", "result_pct": 0},
    {"quant_tactic_id": "", "result_pct": 9},
]


def _both(rows):
    return m._tactic_performance(rows), owner._tactic_performance(rows, facade=m)


def test_values_order_and_immutability():
    snap = copy.deepcopy(ROWS)
    a, b = _both(ROWS)
    assert a == b and ROWS == snap
    assert a[0] == {"name": "opening_gap_momentum", "shape": "opening", "count": 2, "win_count": 1, "loss_count": 1, "win_rate": 0.5, "avg_return_pct": 0.5}
    assert a[1]["name"] == "defensive_observe" and a[1]["count"] == 1 and a[1]["shape"] == "defensive"
    assert list(a[0]) == ["name", "shape", "count", "win_count", "loss_count", "win_rate", "avg_return_pct"]


def test_empty_and_stable_ties():
    assert _both([]) == ([], [])
    rows = [{"quant_tactic_id": "b", "result_pct": 1}, {"quant_tactic_id": "a", "result_pct": 1}]
    a, b = _both(rows)
    assert a == b and [r["name"] for r in a] == ["b", "a"]


def test_facade_result_pct_seam(monkeypatch):
    monkeypatch.setattr(m, "_result_pct", lambda row: 5.0)
    a, b = _both(ROWS)
    assert a == b and a[0]["avg_return_pct"] == 5.0 and a[0]["win_count"] == 2
