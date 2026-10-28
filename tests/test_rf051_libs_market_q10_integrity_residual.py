"""RF-051 residual: q10_observation_integrity branches (tmp-only, no market/broker IO)."""
from __future__ import annotations

import os

import pytest

from libs.market import q10_observation_integrity as qi

SCHED = 1_700_000_000


def _row(offset=10, **extra):
    from datetime import datetime, timezone

    ts = datetime.fromtimestamp(SCHED + offset, tz=timezone.utc).isoformat()
    row = {"current": 100.0, "market_observed_at": ts}
    row.update(extra)
    return row


def test_valid_price_rejects_non_numeric_and_none():
    for bad in (None, "abc", [], {}, float("nan"), float("inf"), 0, -1):
        if qi.valid_price({"current": bad}) is not False:
            raise AssertionError(bad)
    if qi.valid_price({}) is not False:
        raise AssertionError("missing key")
    if qi.valid_price({"current": "12.5"}) is not True:
        raise AssertionError("numeric string accepted")


def test_verified_components_rejects_observation_ahead_of_local_clock():
    rows = {"KOSPI": _row(offset=60)}
    # timestamp (SCHED+60) > observed_epoch + 5 -> rejected (line 77)
    if qi.verified_components(rows, scheduled_epoch=SCHED, observed_epoch=SCHED + 10, is_close=False) is not False:
        raise AssertionError("future market timestamp must be rejected")
    if qi.verified_components(rows, scheduled_epoch=SCHED, observed_epoch=SCHED + 60, is_close=False) is not True:
        raise AssertionError("same row accepted when observed is later")


def test_verified_components_close_requires_finalization_flag():
    base = {"KOSPI": _row()}
    kw = dict(scheduled_epoch=SCHED, observed_epoch=SCHED + 100, is_close=True)
    if qi.verified_components(base, **kw) is not False:
        raise AssertionError("close without finalized flag")
    for key in ("session_finalized", "close_finalized"):
        if qi.verified_components({"KOSPI": _row(**{key: True})}, **kw) is not True:
            raise AssertionError(key)
    if qi.verified_components({"KOSPI": _row(session_finalized="yes")}, **kw) is not False:
        raise AssertionError("truthy non-True flag must not count")


def test_atomic_write_cleans_temp_when_replace_fails(tmp_path, monkeypatch):
    target = tmp_path / "sub" / "m.json"

    def boom(src, dst):
        raise OSError("replace failed")

    monkeypatch.setattr(qi.os, "replace", boom)
    with pytest.raises(OSError):
        qi.atomic_write(target, "{}")
    leftovers = [p.name for p in target.parent.iterdir()]
    if leftovers:
        raise AssertionError(leftovers)
    if target.exists():
        raise AssertionError("target must not exist")
