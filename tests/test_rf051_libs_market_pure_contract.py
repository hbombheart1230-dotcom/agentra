"""RF-051 libs/market C2/C3: sanity, observation-integrity and yfinance_support contracts.

Pure / tmp_path only: ``yfinance`` is never imported for real (it is replaced in
``sys.modules`` by a fake or by ``None``), no network, no operational path.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import logging
import os
import sys
import types
from datetime import datetime, timezone

import pytest

from libs.market import q10_observation_integrity as qi
from libs.market import yfinance_support as ys
from libs.market.korea_index_sanity import EXTREME_CHANGE_PCT, VERY_EXTREME_CHANGE_PCT, korea_index_sanity


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _codes(out):
    return [(w["index"], w["code"], w["severity"]) for w in out["warnings"]]


def test_sanity_thresholds_and_ok_status():
    _eq((EXTREME_CHANGE_PCT, VERY_EXTREME_CHANGE_PCT), (6.0, 10.0))
    ok = korea_index_sanity({"indices": {"KOSPI": {"change_pct": 5.99}, "KOSDAQ": {"change_pct": -5.99}}})
    _eq((ok["status"], ok["warning_count"], ok["warnings"], ok["extreme_move_requires_confirmation"]), ("ok", 0, [], False))
    out = korea_index_sanity({"indices": {"KOSPI": {"change_pct": 6.0}, "KOSDAQ": {"change_pct": "-10"}, "KOSPI200": {"change_pct": 9.99}}})
    _eq(_codes(out), [("KOSPI", "extreme_index_change_pct", "warning"), ("KOSDAQ", "extreme_index_change_pct", "critical"),
                      ("KOSPI200", "extreme_index_change_pct", "warning")])
    _eq((out["status"], out["warning_count"], out["extreme_move_requires_confirmation"]), ("warning", 3, True))


def test_sanity_ignores_unknown_indices_and_unparsable_change():
    out = korea_index_sanity({"indices": {"NASDAQ": {"change_pct": 50}, "KOSPI": {"change_pct": "n/a"}, "KOSDAQ": {"change_pct": None}, "KOSPI200": {}}})
    _eq(out["status"], "ok")
    for bad in ({}, {"indices": None}, {"indices": "x"}, {"indices": {"KOSPI": "notmapping"}}):
        _eq(korea_index_sanity(bad)["warning_count"], 0)


def test_sanity_high_low_and_current_range_checks_need_change_pct():
    row = {"change_pct": 1.0, "high": 90, "low": 100}
    out = korea_index_sanity({"indices": {"KOSPI": dict(row, current=95)}})
    _eq(_codes(out), [("KOSPI", "index_high_below_low", "critical"), ("KOSPI", "index_current_outside_high_low", "warning")])
    _eq(out["warnings"][0]["requires_confirmation"], True)
    in_range = korea_index_sanity({"indices": {"KOSPI": {"change_pct": 1.0, "current": 100.05, "high": 100.0, "low": 99.0}}})
    _eq(in_range["warning_count"], 0)  # within the 0.1% tolerance
    above = korea_index_sanity({"indices": {"KOSPI": {"change_pct": 1.0, "current": 100.2, "high": 100.0, "low": 99.0}}})
    _eq(_codes(above), [("KOSPI", "index_current_outside_high_low", "warning")])
    below = korea_index_sanity({"indices": {"KOSPI": {"change_pct": 1.0, "current": 98.8, "high": 100.0, "low": 99.0}}})
    _eq(_codes(below), [("KOSPI", "index_current_outside_high_low", "warning")])
    # without change_pct the row is skipped entirely, even with an inverted range
    _eq(korea_index_sanity({"indices": {"KOSPI": {"high": 90, "low": 100}}})["warning_count"], 0)
    # non-positive high/low disable the range checks
    _eq(korea_index_sanity({"indices": {"KOSPI": {"change_pct": 1.0, "high": 0, "low": 5, "current": 99}}})["warning_count"], 0)


def test_sanity_does_not_mutate_input():
    packet = {"indices": {"KOSPI": {"change_pct": 20.0}}}
    before = repr(packet)
    korea_index_sanity(packet)
    _eq(repr(packet), before)


@pytest.mark.parametrize("row,ok", [
    ({"current": 1}, True), ({"current": "2.5"}, True), ({"current": 0}, False), ({"current": -1}, False),
    ({"current": float("nan")}, False), ({"current": float("inf")}, False), ({"current": None}, False),
    ({}, False), ({"current": "x"}, False),
])
def test_valid_price(row, ok):
    _eq(qi.valid_price(row), ok)


def test_market_epoch_requires_timezone_and_prefers_market_observed_at():
    t = "2026-10-28T00:00:00+00:00"
    epoch = datetime(2026, 10, 28, tzinfo=timezone.utc).timestamp()
    _eq(qi.market_epoch({"market_observed_at": t}), epoch)
    _eq(qi.market_epoch({"market_observed_at": "2026-10-28T00:00:00Z"}), epoch)
    _eq(qi.market_epoch({"quote_timestamp": t}), epoch)
    _eq(qi.market_epoch({"market_observed_at": t, "quote_timestamp": "2000-01-01T00:00:00+00:00"}), epoch)
    _eq(qi.market_epoch({"market_observed_at": "2026-10-28T00:00:00"}), None)  # naive -> not evidence
    for bad in ({}, {"market_observed_at": "garbage"}, {"market_observed_at": None}):
        _eq(qi.market_epoch(bad), None)


def _row(offset, **extra):
    base = 1_000_000.0
    iso = datetime.fromtimestamp(base + offset, tz=timezone.utc).isoformat()
    return {"current": 100.0, "market_observed_at": iso, **extra}


def test_verified_components_window_and_close_finalization():
    sched = 1_000_000
    good = {"KOSPI": _row(0), "KOSDAQ": _row(90)}
    _eq(qi.verified_components(good, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=False), True)
    _eq(qi.verified_components({}, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=False), False)
    _eq(qi.verified_components({"A": _row(-1)}, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=False), False)   # before schedule
    _eq(qi.verified_components({"A": _row(91)}, scheduled_epoch=sched, observed_epoch=sched + 200, is_close=False), False)   # beyond 90 s
    _eq(qi.verified_components({"A": _row(60)}, scheduled_epoch=sched, observed_epoch=sched + 54, is_close=False), False)    # after observation +5 s
    _eq(qi.verified_components({"A": _row(60)}, scheduled_epoch=sched, observed_epoch=sched + 55, is_close=False), True)
    _eq(qi.verified_components({"A": _row(0, current=0)}, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=False), False)
    _eq(qi.verified_components({"A": {"current": 5}}, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=False), False)
    # close requires every row to carry an explicit True finalization flag
    _eq(qi.verified_components({"A": _row(0)}, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=True), False)
    _eq(qi.verified_components({"A": _row(0, session_finalized=True), "B": _row(0, close_finalized=True)}, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=True), True)
    _eq(qi.verified_components({"A": _row(0, session_finalized="true")}, scheduled_epoch=sched, observed_epoch=sched + 100, is_close=True), False)


def test_atomic_write_creates_dirs_replaces_and_leaves_no_tmp(tmp_path):
    p = tmp_path / "a" / "b" / "m.json"
    qi.atomic_write(p, "one")
    qi.atomic_write(p, "두번째")
    _eq(p.read_text(encoding="utf-8"), "두번째")
    _eq(sorted(x.name for x in p.parent.iterdir()), ["m.json"])


def test_atomic_write_failure_keeps_old_content_and_cleans_tmp(tmp_path, monkeypatch):
    p = tmp_path / "m.json"
    qi.atomic_write(p, "old")
    monkeypatch.setattr(qi.os, "replace", lambda a, b: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        qi.atomic_write(p, "new")
    _eq(p.read_text(encoding="utf-8"), "old")
    _eq(sorted(x.name for x in tmp_path.iterdir()), ["m.json"])


def test_manifest_lock_creates_lock_file_next_to_manifest_and_is_reusable(tmp_path):
    p = tmp_path / "sub" / "manifest.json"
    for _ in range(2):  # released on exit, so a second sequential acquisition must not block
        with qi.manifest_lock(p):
            _eq((tmp_path / "sub" / "manifest.lock").exists(), True)
    with pytest.raises(RuntimeError):
        with qi.manifest_lock(p):
            raise RuntimeError("body error propagates and still releases the lock")
    with qi.manifest_lock(p):
        pass


def test_dependency_error_message_and_reason():
    e = ys.DataSourceDependencyError("yfinance", "ImportError: x")
    _eq((e.package, e.reason), ("yfinance", "dependency_missing:yfinance"))
    for token in ("dependency_missing:yfinance", "requirements.txt", "[ImportError: x]"):
        if token not in str(e):
            raise AssertionError((token, str(e)))
    _eq(ys.DEPENDENCY_MISSING_REASON, "dependency_missing:yfinance")
    _eq(isinstance(e, RuntimeError), True)
    _eq("[" in str(ys.DataSourceDependencyError()), False)


def test_missing_yfinance_is_explicit_everywhere(monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "yfinance", None)  # `import yfinance` raises ImportError, no real import / network
    monkeypatch.setattr(ys, "_REPORTED", set())
    with pytest.raises(ys.DataSourceDependencyError):
        ys.require_yfinance()
    st = ys.yfinance_dependency_status()
    _eq((st["available"], st["version"], st["reason"]), (False, None, "dependency_missing:yfinance"))
    with caplog.at_level(logging.ERROR, logger=ys.__name__):
        _eq(ys.try_yfinance("comp_a"), None)
        _eq(ys.try_yfinance("comp_a"), None)   # once per component per process
        _eq(ys.try_yfinance("comp_b"), None)
    msgs = [r.getMessage() for r in caplog.records if "DATA_SOURCE_DEPENDENCY_MISSING" in r.getMessage()]
    _eq(len(msgs), 2)
    if "component=comp_a" not in msgs[0] or "component=comp_b" not in msgs[1]:
        raise AssertionError(msgs)


def test_present_yfinance_fake_is_returned_without_logging(monkeypatch, caplog):
    fake = types.ModuleType("yfinance")
    fake.__version__ = "9.9.9"
    monkeypatch.setitem(sys.modules, "yfinance", fake)
    monkeypatch.setattr(ys, "_REPORTED", set())
    with caplog.at_level(logging.ERROR, logger=ys.__name__):
        if ys.require_yfinance() is not fake or ys.try_yfinance("c") is not fake:
            raise AssertionError("fake module must be returned")
    _eq(caplog.records, [])
    _eq(ys.yfinance_dependency_status(), {"available": True, "version": "9.9.9", "reason": ""})
    fake2 = types.ModuleType("yfinance")
    monkeypatch.setitem(sys.modules, "yfinance", fake2)
    _eq(ys.yfinance_dependency_status()["version"], None)  # empty version string -> None
