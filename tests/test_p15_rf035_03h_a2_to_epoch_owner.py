"""P15 RF-035 (03h): report_source_helpers.to_epoch moved to report_source_clock_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from datetime import datetime as real_datetime, timezone

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_clock_projection as owner


def _both(ts):
    return m.to_epoch(ts), owner.to_epoch(ts, facade=m)


@pytest.mark.parametrize("v,expected", [
    (None, 0), ("", 0), ("  ", 0), (5, 5), (5.9, 5), ("12.7", 12), ("1970-01-02T00:00:00Z", 86400), ("1970-01-02T00:00:00+00:00", 86400),
    ("1970-01-02T00:00:00", 86400), ("bad", 0), ("1970-01-02T09:00:00+09:00", 86400), (True, 1), ("1e3", 1000),
])
def test_values(v, expected):
    assert _both(v) == (expected, expected)


def test_nan_inf_strings():
    for v in ("nan", "inf", "-inf"):
        a = _both(v)
        assert a[0] == a[1]


def test_facade_seams(monkeypatch):
    seen = []

    class FakeDT(real_datetime):
        @classmethod
        def fromisoformat(cls, s):
            seen.append(s)
            return real_datetime(1970, 1, 3)

    class FakeTZ:
        utc = timezone.utc

    monkeypatch.setattr(m, "datetime", FakeDT)
    monkeypatch.setattr(m, "timezone", FakeTZ)
    assert _both("2020-01-01T00:00:00Z") == (172800, 172800)
    assert seen == ["2020-01-01T00:00:00+00:00"] * 2
