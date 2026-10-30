"""P15 RF-035 (03h): report_source_helpers.epoch_to_iso moved to report_source_clock_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from datetime import datetime as real_datetime, timezone

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_clock_projection as owner


def _both(v):
    return m.epoch_to_iso(v), owner.epoch_to_iso(v, facade=m)


@pytest.mark.parametrize("v,expected", [(86400, "1970-01-02T00:00:00+00:00"), ("86400.9", "1970-01-02T00:00:00+00:00"), ("bad", ""), (0, ""), (-1, ""), (None, ""), (float("nan"), "")])
def test_values(v, expected):
    assert _both(v) == (expected, expected)


def test_facade_datetime_seam(monkeypatch):
    class FakeDT(real_datetime):
        @classmethod
        def fromtimestamp(cls, n, tz=None):
            return real_datetime(2000, 1, 2, 3, 4, 5, tzinfo=tz)

    monkeypatch.setattr(m, "datetime", FakeDT)
    assert _both(5) == ("2000-01-02T03:04:05+00:00",) * 2
