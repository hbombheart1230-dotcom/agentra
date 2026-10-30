"""P15 RF-035: agent_pipeline_trace._utc_day moved to agent_pipeline_trace_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import agent_pipeline_trace as m
from libs.reporting import agent_pipeline_trace_scalar_projection as owner


def _both(ts):
    return m._utc_day(ts), owner._utc_day(ts, facade=m)


def test_epoch_seam(monkeypatch):
    monkeypatch.setattr(m, "_to_epoch", lambda ts: ts)
    assert _both(0) == ("1970-01-01", "1970-01-01")
    assert _both(86400) == ("1970-01-02", "1970-01-02")
    assert _both(None) == (None, None)


def test_none_from_to_epoch(monkeypatch):
    monkeypatch.setattr(m, "_to_epoch", lambda ts: None)
    assert _both("x") == (None, None)


def test_call_time_lookup_and_real_epoch():
    calls = []
    orig = m._to_epoch
    m._to_epoch = lambda ts: (calls.append(ts), 3600)[1]
    try:
        assert _both("anything") == ("1970-01-01", "1970-01-01")
        assert calls == ["anything", "anything"]
    finally:
        m._to_epoch = orig
    assert _both("1970-01-02T00:00:00+00:00")[0] == _both("1970-01-02T00:00:00+00:00")[1]
