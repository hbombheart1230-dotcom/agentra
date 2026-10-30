"""P15 RF-035 (03h): report_source_helpers.utc_day moved to report_source_clock_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_clock_projection as owner


def _both(ts):
    return m.utc_day(ts), owner.utc_day(ts, facade=m)


def test_epoch_seam(monkeypatch):
    monkeypatch.setattr(m, "to_epoch", lambda ts: ts)
    assert _both(86400) == ("1970-01-02", "1970-01-02")
    assert _both(0) == ("", "")
    assert _both(-5) == ("", "")


def test_real_values():
    assert _both("1970-01-02T00:00:00Z") == ("1970-01-02", "1970-01-02")
    assert _both(None) == ("", "")
    assert _both("bad") == ("", "")


def test_exception_parity(monkeypatch):
    def boom(ts):
        raise RuntimeError("x")

    monkeypatch.setattr(m, "to_epoch", boom)
    for fn in (lambda: m.utc_day(1), lambda: owner.utc_day(1, facade=m)):
        with pytest.raises(RuntimeError):
            fn()
