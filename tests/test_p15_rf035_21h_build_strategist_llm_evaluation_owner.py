"""P15 RF-035 (21h): strategist_llm_evaluation.build_strategist_llm_evaluation moved to strategist_llm_evaluation_build; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_build as owner


def _both(rows, shadow=()):
    return m.build_strategist_llm_evaluation(rows, shadow), owner.build_strategist_llm_evaluation(rows, shadow, facade=m)


KEYS = ["schema_version", "behavior_effect", "closed_or_realized_sample_count", "selected_primary_tactic", "selected_primary_lane", "tactic_performance",
        "shadow_shape_diagnostics", "lane_selection_quality", "overused_lane_or_tactic", "underused_shadow_lane", "call_effectiveness"]


def test_empty():
    a, b = _both([], [])
    assert a == b and list(a) == KEYS
    assert a["schema_version"] == "strategist_llm_evaluation.v1" and a["closed_or_realized_sample_count"] == 0
    assert a["selected_primary_tactic"] == "" and a["lane_selection_quality"] == "insufficient_trade_samples"
    assert a["selected_primary_lane"] == "unavailable" and a["underused_shadow_lane"] == ""
    assert a["call_effectiveness"] == {"status": "not_available", "reason": "strategist_llm_call_trace_not_linked_to_operator_summary"}


def test_closed_rows_and_shadow():
    rows = [{"status": "closed", "quant_tactic_id": "opening_gap_momentum", "return_pct": -1.0} for _ in range(3)] + [{"status": "open", "quant_tactic_id": "z"}]
    shadow = [{"candidates": [{"reason": "breakout_late", "would_enter": True}]}]
    snap = copy.deepcopy((rows, shadow))
    a, b = _both(rows, shadow)
    assert a == b and (rows, shadow) == snap
    assert a["closed_or_realized_sample_count"] == 3 and a["selected_primary_tactic"] == "opening_gap_momentum"
    assert a["selected_primary_lane"] == "opening" and a["lane_selection_quality"] == "poor_lane_selection"
    assert a["overused_lane_or_tactic"] == "opening_gap_momentum" and a["underused_shadow_lane"] == "breakout"


def test_opening_underused_and_default_shadow():
    shadow = [{"candidates": [{"reason": "zzz", "opening_momentum_probe_would_enter": True}]}]
    a, b = _both([], shadow)
    assert a == b and a["underused_shadow_lane"] == "opening"
    assert m.build_strategist_llm_evaluation([]) == owner.build_strategist_llm_evaluation([], facade=m)


def test_facade_seams(monkeypatch):
    calls = []
    monkeypatch.setattr(m, "_quality_label", lambda **kw: (calls.append(kw), "SENTINEL")[1])
    monkeypatch.setattr(m, "_closed_rows", lambda rows: [{"quant_tactic_id": "q", "return_pct": 1.0}])
    a, b = _both([{"x": 1}])
    assert a == b and a["lane_selection_quality"] == "SENTINEL" and a["closed_or_realized_sample_count"] == 1
    assert len(calls) == 2
