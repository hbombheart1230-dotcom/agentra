"""P15 RF-035 (03h): report_source_helpers.utc_now_iso moved to report_source_clock_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from datetime import datetime as real_datetime, timezone

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_clock_projection as owner


class _FakeDT(real_datetime):
    @classmethod
    def now(cls, tz=None):
        return real_datetime(2026, 10, 31, 3, 0, 0, 123456, tzinfo=tz)


def test_fixed_clock_seconds_only(monkeypatch):
    monkeypatch.setattr(m, "datetime", _FakeDT)
    assert m.utc_now_iso() == owner.utc_now_iso(facade=m) == "2026-10-31T03:00:00+00:00"


def test_facade_timezone_seam(monkeypatch):
    seen = []

    class FakeDT(real_datetime):
        @classmethod
        def now(cls, tz=None):
            seen.append(tz)
            return real_datetime(2026, 1, 2, 3, 4, 5, tzinfo=tz)

    class FakeTZ:
        utc = timezone.utc

    monkeypatch.setattr(m, "datetime", FakeDT)
    monkeypatch.setattr(m, "timezone", FakeTZ)
    assert m.utc_now_iso() == owner.utc_now_iso(facade=m) == "2026-01-02T03:04:05+00:00" and seen == [timezone.utc] * 2


def test_real_clock_shape():
    for v in (m.utc_now_iso(), owner.utc_now_iso(facade=m)):
        assert v.endswith("+00:00") and "." not in v
