"""P15 RF-035: agent_pipeline_trace._latest_row moved to agent_pipeline_trace_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import agent_pipeline_trace as m
from libs.reporting import agent_pipeline_trace_scalar_projection as owner


def test_last_match_identity_and_no_match():
    rows = [{"stage": "a", "event": "e", "n": 1}, {"stage": "b", "event": "e"}, {"stage": " a ", "event": " e ", "n": 2}]
    snap = [dict(r) for r in rows]
    for fn in (m._latest_row, owner._latest_row):
        assert fn(rows, stage="a", event="e") is rows[2]
        assert fn(rows, stage="b", event="e") is rows[1]
        assert fn(rows, stage="z", event="e") == {}
        assert fn([], stage="a", event="e") == {}
    assert rows == snap


def test_stage_event_arguments_not_stripped():
    rows = [{"stage": "a", "event": "e"}]
    for fn in (m._latest_row, owner._latest_row):
        assert fn(rows, stage=" a", event="e") == {}


def test_malformed_row_exception_parity():
    for fn in (m._latest_row, owner._latest_row):
        with pytest.raises(AttributeError):
            fn(["x"], stage="a", event="e")


def test_keyword_only():
    for fn in (m._latest_row, owner._latest_row):
        with pytest.raises(TypeError):
            fn([], "a", "e")
