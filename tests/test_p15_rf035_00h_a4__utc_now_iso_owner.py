"""P15 RF-035 (00h): strategist_llm_summary._utc_now_iso moved to strategist_llm_summary_clock_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from datetime import datetime as real_datetime, timezone

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_clock_projection as owner


class _FakeDT(real_datetime):
    @classmethod
    def now(cls, tz=None):
        return real_datetime(2026, 10, 30, 0, 0, 0, tzinfo=tz)


def test_fixed_clock(monkeypatch):
    monkeypatch.setattr(m, "datetime", _FakeDT)
    assert m._utc_now_iso() == owner._utc_now_iso(facade=m) == "2026-10-30T00:00:00+00:00"


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
    assert m._utc_now_iso() == owner._utc_now_iso(facade=m) == "2026-01-02T03:04:05+00:00"
    assert seen == [timezone.utc, timezone.utc]


def test_real_clock_shape():
    for v in (m._utc_now_iso(), owner._utc_now_iso(facade=m)):
        assert v.endswith("+00:00") and "T" in v
