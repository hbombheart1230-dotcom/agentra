"""P15 RF-035 (21h): strategist_llm_evaluation._quality_label moved to strategist_llm_evaluation_extra_projection; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_extra_projection as owner


def _rows(n, tactic="x", ret=-1.0):
    return [{"quant_tactic_id": tactic, "return_pct": ret} for _ in range(n)]


def _both(**kw):
    return m._quality_label(**kw), owner._quality_label(facade=m, **kw)


CASES = [
    (dict(rows=[], primary_tactic="x", shadow={}), "insufficient_trade_samples"),
    (dict(rows=_rows(3), primary_tactic="x", shadow={}), "poor_lane_selection"),
    (dict(rows=_rows(3, ret=1.0), primary_tactic="x", shadow={}), "aligned_lane_selection"),
    (dict(rows=_rows(3, ret=-0.3) + [{"quant_tactic_id": "x", "return_pct": 0.5}], primary_tactic="x", shadow={}), "weak_lane_selection"),
    (dict(rows=_rows(1, "vwap_reclaim_pullback", 0.0), primary_tactic="vwap_reclaim_pullback", shadow={"opening_would_enter_count": 2}), "missed_opening_momentum_possible"),
    (dict(rows=_rows(1), primary_tactic="", shadow={}), "review_sample_building"),
    (dict(rows=_rows(2), primary_tactic="x", shadow={"opening_would_enter_count": 1}), "review_sample_building"),
]


@pytest.mark.parametrize("kw,expected", CASES)
def test_branches(kw, expected):
    snap = copy.deepcopy(kw)
    a, b = _both(**kw)
    assert a == b == expected and kw == snap


def test_facade_helper_seams(monkeypatch):
    monkeypatch.setattr(m, "_result_pct", lambda row: -5.0)
    kw = dict(rows=_rows(3, ret=9.0), primary_tactic="x", shadow={})
    assert _both(**kw) == ("poor_lane_selection", "poor_lane_selection")
    monkeypatch.undo()
    monkeypatch.setattr(m, "_tactic", lambda row: "zzz")
    kw = dict(rows=_rows(3, ret=-1.0), primary_tactic="x", shadow={})
    # primary rows filtered out by the patched _tactic; falls back to all rows
    assert _both(**kw) == ("poor_lane_selection", "poor_lane_selection")
    monkeypatch.undo()
    monkeypatch.setattr(m, "_shape_from_tactic", lambda t: "pullback")
    kw = dict(rows=_rows(1, ret=0.0), primary_tactic="x", shadow={"opening_would_enter_count": 1})
    assert _both(**kw) == ("missed_opening_momentum_possible",) * 2


def test_keyword_only():
    for fn in (m._quality_label,):
        with pytest.raises(TypeError):
            fn([], "x", {})
