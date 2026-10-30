"""P15 RF-035 (21h): strategist_llm_evaluation._result_pct moved to strategist_llm_evaluation_extra_projection; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_extra_projection as owner


@pytest.mark.parametrize("row,expected", [
    ({"truth_net_return_pct": "1.5"}, 1.5), ({"result_pct": "-2"}, -2.0), ({}, 0.0), ({"pnl_pct": 3}, 3.0),
    ({"truth_net_return_pct": "", "return_pct": "4"}, 4.0), ({"result_pct": "bad", "pnl_pct": 9}, 0.0), ({"truth_net_return_pct": 0, "result_pct": 5}, 0.0),
])
def test_values(row, expected):
    assert m._result_pct(row) == owner._result_pct(row, facade=m) == expected


def test_facade_float_seam_called_once(monkeypatch):
    calls = []
    monkeypatch.setattr(m, "_float", lambda v, d=0.0: (calls.append((v, d)), 7.0)[1])
    assert m._result_pct({"result_pct": "1"}) == 7.0
    assert owner._result_pct({"result_pct": "1"}, facade=m) == 7.0
    assert calls == [("1", 0.0), ("1", 0.0)]
