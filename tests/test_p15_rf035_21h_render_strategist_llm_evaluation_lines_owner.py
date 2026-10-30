"""P15 RF-035 (21h): strategist_llm_evaluation.render_strategist_llm_evaluation_lines moved to strategist_llm_evaluation_formatting; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_formatting as owner


def _both(payload):
    return m.render_strategist_llm_evaluation_lines(payload), owner.render_strategist_llm_evaluation_lines(payload, facade=m)


def test_empty_inputs():
    assert _both(None) == ([], [])
    assert _both({}) == ([], [])


def test_quality_line_and_exact_layout():
    payload = {"lane_selection_quality": "aligned_lane_selection", "selected_primary_tactic": "t", "selected_primary_lane": "opening", "closed_or_realized_sample_count": 4,
               "tactic_performance": [{"name": "t", "count": 4, "win_rate": 0.75, "avg_return_pct": 1.0}],
               "shadow_shape_diagnostics": {"candidate_count": 2, "opening_would_enter_count": 1},
               "overused_lane_or_tactic": "o", "underused_shadow_lane": "u", "call_effectiveness": {"status": "ok"}}
    snap = copy.deepcopy(payload)
    a, b = _both(payload)
    assert a == b and payload == snap
    assert a[:3] == ["", "## Strategist LLM Evaluation", ""] and len(a) == 8
    assert a[3] == "- Strategist lane quality: `aligned_lane_selection` / primary `t` (opening) / samples 4"
    assert a[4] == "- Strategist tactic performance: t (4, win 75.0%, avg 1.00%)"
    assert a[5] == "- Strategist shadow contrast: candidates 2, opening would-enter 1"
    assert a[6] == "- Strategist overused: o / underused shadow lane: u"
    assert a[7] == "- Strategist call effectiveness: ok"


def test_defaults_when_sparse():
    a, b = _both({"lane_selection_quality": "aligned_lane_selection"})
    assert a == b and "## Strategist LLM Evaluation" in a
    assert a[3] == "- Strategist lane quality: `aligned_lane_selection` / primary `none` (unavailable) / samples 0"
    assert a[4] == "- Strategist tactic performance: none" and a[7] == "- Strategist call effectiveness: not_available"


def test_facade_format_perf_seam(monkeypatch):
    monkeypatch.setattr(m, "_format_perf", lambda rows, **k: "SENTINEL")
    a, b = _both({"lane_selection_quality": "q"})
    assert a == b and "- Strategist tactic performance: SENTINEL" in a


def test_existing_format_perf_kept():
    assert owner._format_perf([{"name": "x", "count": 1}], facade=m) == "x (1, win 0.0%, avg 0.00%)"
