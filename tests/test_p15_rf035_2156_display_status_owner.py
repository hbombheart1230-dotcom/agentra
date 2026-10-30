"""P15 RF-035 (2156): controlled_validation_daily._display_evaluation_status moved to controlled_validation_daily_status_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from datetime import date, datetime as real_datetime, time as real_time, timezone

import pytest

from libs.reporting import controlled_validation_daily as m
from libs.reporting import controlled_validation_daily_status_projection as owner


class _FakeDT(real_datetime):
    fixed = real_datetime(2026, 10, 30, 9, 13)

    @classmethod
    def now(cls, tz=None):
        return cls.fixed.replace(tzinfo=tz) if tz else cls.fixed


def _both(**kw):
    return m._display_evaluation_status(**kw), owner._display_evaluation_status(facade=m, **kw)


def _kw(**o):
    base = dict(lane_id="BTC_WOORI", day="2026-10-29", status="INPUT_DELAY", reason="q12_candidate_input_stale")
    base.update(o)
    return base


def test_past_day_closed(monkeypatch):
    monkeypatch.setattr(m, "datetime", _FakeDT)
    assert _both(**_kw()) == (("WINDOW_CLOSED", "q12_opening_candidate_window_closed"),) * 2


def test_same_day_before_and_after_cutoff(monkeypatch):
    monkeypatch.setattr(m, "datetime", _FakeDT)
    _FakeDT.fixed = real_datetime(2026, 10, 30, 9, 10)
    assert _both(**_kw(day="2026-10-30")) == (("INPUT_DELAY", "q12_candidate_input_stale"),) * 2
    _FakeDT.fixed = real_datetime(2026, 10, 30, 9, 13)
    assert _both(**_kw(day="2026-10-30")) == (("WINDOW_CLOSED", "q12_opening_candidate_window_closed"),) * 2
    _FakeDT.fixed = real_datetime(2026, 10, 30, 9, 12)
    assert _both(**_kw(day="2026-10-30")) == (("INPUT_DELAY", "q12_candidate_input_stale"),) * 2
    assert _both(**_kw(day="2999-01-01")) == (("INPUT_DELAY", "q12_candidate_input_stale"),) * 2


def test_unchanged_paths(monkeypatch):
    monkeypatch.setattr(m, "datetime", _FakeDT)
    _FakeDT.fixed = real_datetime(2026, 10, 30, 9, 13)
    assert _both(**_kw(lane_id="Q10_INDEX")) == (("INPUT_DELAY", "q12_candidate_input_stale"),) * 2
    assert _both(**_kw(status="OK")) == (("OK", "q12_candidate_input_stale"),) * 2
    assert _both(**_kw(reason="other")) == (("INPUT_DELAY", "other"),) * 2
    assert _both(**_kw(day="not-a-date")) == (("INPUT_DELAY", "q12_candidate_input_stale"),) * 2


def test_keyword_only_and_docstring():
    with pytest.raises(TypeError):
        m._display_evaluation_status("BTC_WOORI", "d", "s", "r")
    assert "expected post-window expiry" in m._display_evaluation_status.__doc__
