"""P15 RF-035 (02h): trade_explain._utc_day moved to trade_explain_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from datetime import datetime as real_datetime, timezone

import pytest

from libs.reporting import trade_explain as m
from libs.reporting import trade_explain_scalar_projection as owner


def _both(ts):
    return m._utc_day(ts), owner._utc_day(ts, facade=m)


def test_epoch_seam(monkeypatch):
    monkeypatch.setattr(m, "_to_epoch", lambda ts: ts)
    assert _both(0) == ("1970-01-01", "1970-01-01")
    assert _both(86400) == ("1970-01-02", "1970-01-02")
    assert _both(None) == (None, None)


def test_call_time_lookup_and_real_epoch():
    calls = []
    orig = m._to_epoch
    m._to_epoch = lambda ts: (calls.append(ts), 3600)[1]
    try:
        assert _both("x") == ("1970-01-01", "1970-01-01") and calls == ["x", "x"]
    finally:
        m._to_epoch = orig
    assert _both("1970-01-02T00:00:00+00:00")[0] == _both("1970-01-02T00:00:00+00:00")[1]


def test_facade_datetime_and_timezone_seams(monkeypatch):
    seen = []

    class FakeDT(real_datetime):
        @classmethod
        def fromtimestamp(cls, e, tz=None):
            seen.append((e, tz))
            return real_datetime(2000, 1, 2, tzinfo=tz)

    class FakeTZ:
        utc = timezone.utc

    monkeypatch.setattr(m, "_to_epoch", lambda ts: 5)
    monkeypatch.setattr(m, "datetime", FakeDT)
    monkeypatch.setattr(m, "timezone", FakeTZ)
    assert _both("x") == ("2000-01-02", "2000-01-02") and seen == [(5, timezone.utc)] * 2
