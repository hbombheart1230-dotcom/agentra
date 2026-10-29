"""P15 order 1: _stock_reaction MOVE to stock_reaction.py - parity with pre-extraction frozen output (no I/O, no network).

EXPECTED is the JSON produced by the pre-extraction reaction_reader._stock_reaction for the six scenarios below
(captured at A HEAD 8bdbd5ab before the move).
"""
from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import reaction_reader as rr
from libs.reporting.baseline_samsung_hynix.forward_validation import stock_reaction as sr

KST = timezone(timedelta(hours=9))
DAY = "2026-09-07"
TARGET = {"key": "samsung", "symbol": "005930", "kind": "stock"}
EXPECTED = json.loads(r'''{"close_override_vs_legacy":{"actual_open_policy":"first_positive_volume_candle_0900_to_0903","day_high":100.0,"day_high_return_pct":0.0,"day_low":90.0,"day_low_return_pct":-10.0,"evidence_status":"AVAILABLE","forward_windows":{"09:00":{"mae_pct":-10.0,"mfe_pct":10.0,"return_to_close_pct":10.0,"status":"OBSERVED"},"09:03":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:05":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:10":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:15":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:30":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"10:00":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"}},"last_available_point_before_close":null,"opening_gap_pct":0.0,"path":[{"close":100.0,"high":100.0,"low":100.0,"open":100.0,"ts":1788739200,"volume":100.0},{"close":90.0,"high":90.0,"low":90.0,"open":90.0,"ts":1788762300,"volume":100.0}],"points":{"09:00":{"price":100.0,"return_from_previous_close_pct":0.0,"status":"OBSERVED","ts":1788739200,"volume":100.0},"09:03":{"price":null,"status":"PENDING","volume":null},"09:05":{"price":null,"status":"PENDING","volume":null},"09:10":{"price":null,"status":"PENDING","volume":null},"09:15":{"price":null,"status":"PENDING","volume":null},"09:30":{"price":null,"status":"PENDING","volume":null},"10:00":{"price":null,"status":"PENDING","volume":null},"CLOSE":{"capture_status":"AVAILABLE","price":110.0,"return_from_previous_close_pct":10.0,"source":"q10_index_observation_collector","status":"OBSERVED","ts":1788762600,"volume":null}},"previous_close":100.0,"source":"q10_current_day_minute_candles","target":{"key":"samsung","kind":"stock","symbol":"005930"}},"close_pending":{"actual_open_policy":"first_positive_volume_candle_0900_to_0903","day_high":105.0,"day_high_return_pct":5.0,"day_low":100.0,"day_low_return_pct":0.0,"evidence_status":"AVAILABLE","forward_windows":{"09:00":{"mae_pct":0.0,"mfe_pct":5.0,"return_to_close_pct":null,"status":"PARTIAL"},"09:03":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:05":{"mae_pct":0.0,"mfe_pct":3.960396,"return_to_close_pct":null,"status":"PARTIAL"},"09:10":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:15":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:30":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"10:00":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"}},"last_available_point_before_close":null,"opening_gap_pct":0.0,"path":[{"close":100.0,"high":100.0,"low":100.0,"open":100.0,"ts":1788739200,"volume":100.0},{"close":101.0,"high":101.0,"low":101.0,"open":101.0,"ts":1788739500,"volume":100.0},{"close":105.0,"high":105.0,"low":105.0,"open":105.0,"ts":1788746400,"volume":100.0}],"points":{"09:00":{"price":100.0,"return_from_previous_close_pct":0.0,"status":"OBSERVED","ts":1788739200,"volume":100.0},"09:03":{"price":null,"status":"PENDING","volume":null},"09:05":{"price":101.0,"return_from_previous_close_pct":1.0,"status":"OBSERVED","ts":1788739500,"volume":100.0},"09:10":{"price":null,"status":"PENDING","volume":null},"09:15":{"price":null,"status":"PENDING","volume":null},"09:30":{"price":null,"status":"PENDING","volume":null},"10:00":{"price":null,"status":"PENDING","volume":null},"CLOSE":{"price":null,"status":"PENDING","volume":null}},"previous_close":100.0,"source":"q10_current_day_minute_candles","target":{"key":"samsung","kind":"stock","symbol":"005930"}},"collector_invalid":{"actual_open_policy":"first_positive_volume_candle_0900_to_0903","day_high":103.0,"day_high_return_pct":3.0,"day_low":100.0,"day_low_return_pct":0.0,"evidence_status":"AVAILABLE","forward_windows":{"09:00":{"mae_pct":0.0,"mfe_pct":3.0,"return_to_close_pct":3.0,"status":"OBSERVED"},"09:03":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:05":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:10":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:15":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:30":{"mae_pct":0.0,"mfe_pct":1.980198,"return_to_close_pct":1.980198,"status":"OBSERVED"},"10:00":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"}},"last_available_point_before_close":null,"opening_gap_pct":0.0,"path":[{"close":100.0,"high":100.0,"low":100.0,"open":100.0,"ts":1788739200,"volume":100.0},{"close":101.0,"high":101.0,"low":101.0,"open":101.0,"ts":1788741000,"volume":100.0},{"close":102.0,"high":102.0,"low":102.0,"open":102.0,"ts":1788742800,"volume":100.0},{"close":103.0,"high":103.0,"low":103.0,"open":103.0,"ts":1788762300,"volume":100.0}],"points":{"09:00":{"price":100.0,"return_from_previous_close_pct":0.0,"status":"OBSERVED","ts":1788739200,"volume":100.0},"09:03":{"price":null,"status":"PENDING","volume":null},"09:05":{"price":null,"status":"PENDING","volume":null},"09:10":{"price":null,"status":"PENDING","volume":null},"09:15":{"price":null,"status":"PENDING","volume":null},"09:30":{"price":101.0,"return_from_previous_close_pct":1.0,"status":"OBSERVED","ts":1788741000,"volume":100.0},"10:00":{"collector_status":"LATE_MISSED","integrity_failure":true,"integrity_reason":"late","price":null,"status":"PENDING","unverified_observation":{"price":5.0},"volume":null},"CLOSE":{"price":103.0,"return_from_previous_close_pct":3.0,"status":"OBSERVED","ts":1788762300,"volume":100.0}},"previous_close":100.0,"source":"q10_current_day_minute_candles","target":{"key":"samsung","kind":"stock","symbol":"005930"}},"denominator_zero":{"actual_open_policy":"first_positive_volume_candle_0900_to_0903","day_high":103.0,"day_high_return_pct":null,"day_low":100.0,"day_low_return_pct":null,"evidence_status":"AVAILABLE","forward_windows":{"09:00":{"mae_pct":0.0,"mfe_pct":3.0,"return_to_close_pct":3.0,"status":"OBSERVED"},"09:03":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:05":{"mae_pct":0.0,"mfe_pct":1.980198,"return_to_close_pct":1.980198,"status":"OBSERVED"},"09:10":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:15":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:30":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"10:00":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"}},"last_available_point_before_close":null,"opening_gap_pct":null,"path":[{"close":100.0,"high":100.0,"low":100.0,"open":100.0,"ts":1788739200,"volume":100.0},{"close":101.0,"high":101.0,"low":101.0,"open":101.0,"ts":1788739500,"volume":100.0},{"close":103.0,"high":103.0,"low":103.0,"open":103.0,"ts":1788762300,"volume":100.0}],"points":{"09:00":{"price":100.0,"return_from_previous_close_pct":null,"status":"OBSERVED","ts":1788739200,"volume":100.0},"09:03":{"price":null,"status":"PENDING","volume":null},"09:05":{"price":101.0,"return_from_previous_close_pct":null,"status":"OBSERVED","ts":1788739500,"volume":100.0},"09:10":{"price":null,"status":"PENDING","volume":null},"09:15":{"price":null,"status":"PENDING","volume":null},"09:30":{"price":null,"status":"PENDING","volume":null},"10:00":{"price":null,"status":"PENDING","volume":null},"CLOSE":{"price":103.0,"return_from_previous_close_pct":null,"status":"OBSERVED","ts":1788762300,"volume":100.0}},"previous_close":0.0,"source":"q10_current_day_minute_candles","target":{"key":"samsung","kind":"stock","symbol":"005930"}},"empty":{"actual_open_policy":"first_positive_volume_candle_0900_to_0903","day_high":null,"day_high_return_pct":null,"day_low":null,"day_low_return_pct":null,"evidence_status":"INSUFFICIENT_EVIDENCE","forward_windows":{"09:00":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:03":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:05":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:10":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:15":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:30":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"10:00":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"}},"last_available_point_before_close":null,"opening_gap_pct":null,"path":[],"points":{"09:00":{"price":null,"status":"PENDING","volume":null},"09:03":{"price":null,"status":"PENDING","volume":null},"09:05":{"price":null,"status":"PENDING","volume":null},"09:10":{"price":null,"status":"PENDING","volume":null},"09:15":{"price":null,"status":"PENDING","volume":null},"09:30":{"price":null,"status":"PENDING","volume":null},"10:00":{"price":null,"status":"PENDING","volume":null},"CLOSE":{"price":null,"status":"PENDING","volume":null}},"previous_close":null,"source":"q10_current_day_minute_candles","target":{"key":"samsung","kind":"stock","symbol":"005930"}},"zero_volume_open":{"actual_open_policy":"first_positive_volume_candle_0900_to_0903","day_high":104.0,"day_high_return_pct":6.122449,"day_low":100.0,"day_low_return_pct":2.040816,"evidence_status":"AVAILABLE","forward_windows":{"09:00":{"mae_pct":0.0,"mfe_pct":2.970297,"return_to_close_pct":2.970297,"status":"OBSERVED"},"09:03":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:05":{"mae_pct":0.0,"mfe_pct":1.960784,"return_to_close_pct":1.960784,"status":"OBSERVED"},"09:10":{"mae_pct":0.0,"mfe_pct":0.970874,"return_to_close_pct":0.970874,"status":"OBSERVED"},"09:15":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"09:30":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"},"10:00":{"mae_pct":null,"mfe_pct":null,"return_to_close_pct":null,"status":"PENDING"}},"last_available_point_before_close":null,"opening_gap_pct":3.061224,"path":[{"close":100.0,"high":100.0,"low":100.0,"open":100.0,"ts":1788739200,"volume":0.0},{"close":101.0,"high":101.0,"low":101.0,"open":101.0,"ts":1788739260,"volume":5.0},{"close":102.0,"high":102.0,"low":102.0,"open":102.0,"ts":1788739500,"volume":100.0},{"close":103.0,"high":103.0,"low":103.0,"open":103.0,"ts":1788739800,"volume":100.0},{"close":104.0,"high":104.0,"low":104.0,"open":104.0,"ts":1788762300,"volume":100.0}],"points":{"09:00":{"price":101.0,"return_from_previous_close_pct":3.061224,"status":"OBSERVED","ts":1788739260,"volume":5.0},"09:03":{"price":null,"status":"PENDING","volume":null},"09:05":{"price":102.0,"return_from_previous_close_pct":4.081633,"status":"OBSERVED","ts":1788739500,"volume":100.0},"09:10":{"price":103.0,"return_from_previous_close_pct":5.102041,"status":"OBSERVED","ts":1788739800,"volume":100.0},"09:15":{"price":null,"status":"PENDING","volume":null},"09:30":{"price":null,"status":"PENDING","volume":null},"10:00":{"price":null,"status":"PENDING","volume":null},"CLOSE":{"price":104.0,"return_from_previous_close_pct":6.122449,"status":"OBSERVED","ts":1788762300,"volume":100.0}},"previous_close":98.0,"source":"q10_current_day_minute_candles","target":{"key":"samsung","kind":"stock","symbol":"005930"}}}''')


def ep(h, m, s=0):
    return int(datetime(2026, 9, 7, h, m, s, tzinfo=KST).timestamp())


def c(ts, close, *, open_=None, high=None, low=None, volume=100.0):
    return {"ts": ts, "open": close if open_ is None else open_, "high": close if high is None else high, "low": close if low is None else low, "close": close, "volume": volume}


def _override(kind):
    if kind == "verified_close":
        return lambda label: {"ts": ep(15, 30), "close": 110.0, "source": "q10_index_observation_collector", "capture_status": "AVAILABLE"} if label == "CLOSE" else None
    if kind == "invalid_1000_absent_0930":
        return lambda label: {"integrity_failure": True, "reason": "late", "collector_status": "LATE_MISSED", "unverified_observation": {"price": 5.0}} if label == "10:00" else None
    return None


SCENARIOS = {
    "empty": dict(rows=[], previous_close=None),
    "zero_volume_open": dict(rows=[c(ep(9, 0), 100.0, volume=0.0), c(ep(9, 1), 101.0, volume=5.0), c(ep(9, 5), 102.0), c(ep(9, 10), 103.0), c(ep(15, 25), 104.0)], previous_close=98.0),
    "close_override_vs_legacy": dict(rows=[c(ep(9, 0), 100.0), c(ep(15, 25), 90.0)], previous_close=100.0, override="verified_close"),
    "close_pending": dict(rows=[c(ep(9, 0), 100.0), c(ep(9, 5), 101.0), c(ep(11, 0), 105.0)], previous_close=100.0, lookback=1800),
    "collector_invalid": dict(rows=[c(ep(9, 0), 100.0), c(ep(9, 30), 101.0), c(ep(10, 0), 102.0), c(ep(15, 25), 103.0)], previous_close=100.0, override="invalid_1000_absent_0930"),
    "denominator_zero": dict(rows=[c(ep(9, 0), 100.0), c(ep(9, 5), 101.0), c(ep(15, 25), 103.0)], previous_close=0.0),
}


def _run(name, fn):
    s = SCENARIOS[name]
    return fn(day=DAY, target=TARGET, rows=s["rows"], previous_close=s["previous_close"], last_available_lookback_sec=s.get("lookback", 0), collector_override=_override(s.get("override")))


def _norm(value):
    return json.loads(json.dumps(value, sort_keys=True, default=str))


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_wrapper_output_equals_frozen_pre_extraction_output(name):
    assert _norm(_run(name, rr._stock_reaction)) == EXPECTED[name]


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_owner_called_directly_with_facade_equals_wrapper(name):
    s = SCENARIOS[name]
    direct = sr.stock_reaction_impl(day=DAY, target=TARGET, rows=s["rows"], previous_close=s["previous_close"], last_available_lookback_sec=s.get("lookback", 0),
                                    collector_override=_override(s.get("override")), facade=rr)
    assert _norm(direct) == EXPECTED[name]


def test_semantics_called_out_by_the_order_hold():
    z = EXPECTED["zero_volume_open"]
    assert z["points"]["09:00"]["ts"] == ep(9, 1) and z["points"]["09:00"]["price"] == 101.0                # first positive-volume candle, not the 09:00 placeholder
    o = EXPECTED["close_override_vs_legacy"]
    assert o["points"]["CLOSE"]["price"] == 110.0 and o["forward_windows"]["09:00"]["return_to_close_pct"] == 10.0   # one authoritative CLOSE (not legacy 90)
    p = EXPECTED["close_pending"]
    assert p["points"]["CLOSE"]["status"] == "PENDING" and all(w["return_to_close_pct"] is None for w in p["forward_windows"].values() if w["status"] == "PARTIAL")
    assert p["last_available_point_before_close"] is None and p["points"]["CLOSE"]["price"] is None               # last row (11:00) is beyond the 1800s lookback; never substituted for CLOSE
    i = EXPECTED["collector_invalid"]
    assert i["points"]["10:00"]["status"] == "PENDING" and i["points"]["10:00"]["integrity_failure"] is True and i["points"]["09:30"]["status"] == "OBSERVED"
    d = EXPECTED["denominator_zero"]
    assert d["opening_gap_pct"] is None and d["points"]["09:05"]["return_from_previous_close_pct"] is None
    e = EXPECTED["empty"]
    assert e["evidence_status"] == "INSUFFICIENT_EVIDENCE" and e["path"] == [] and e["day_high"] is None


def test_wrapper_delegates_to_owner_and_passes_the_facade_module(monkeypatch):
    seen = {}

    def spy(**kw):
        seen.update(kw)
        return {"spied": True}

    monkeypatch.setattr(rr, "stock_reaction_impl", spy)
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=[], previous_close=1.0, last_available_lookback_sec=5, collector_override="X")
    assert out == {"spied": True} and seen["facade"] is sys.modules[rr.__name__] and seen["last_available_lookback_sec"] == 5 and seen["collector_override"] == "X"
    assert set(seen) == {"day", "target", "rows", "previous_close", "last_available_lookback_sec", "collector_override", "facade"}


def test_facade_helpers_are_resolved_at_call_time_so_monkeypatch_still_works(monkeypatch):
    monkeypatch.setattr(rr, "_pct", lambda current, base: 12345.0)
    out = _run("zero_volume_open", rr._stock_reaction)
    assert out["opening_gap_pct"] == 12345.0


def test_owner_module_has_no_facade_import_no_io_and_is_small():
    path = Path(sr.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not any("reaction_reader" in (m or "") for m in imported) and imported <= {"__future__", "typing"}
    assert len(path.read_text(encoding="utf-8").splitlines()) <= 350
    assert len(Path(rr.__file__).read_text(encoding="utf-8").splitlines()) < 467                       # facade LOC actually decreased


def test_last_available_point_is_informational_only_when_within_lookback():
    rows = [c(ep(9, 0), 100.0), c(ep(15, 15), 103.0)]
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=rows, previous_close=100.0, last_available_lookback_sec=1800)
    assert out["last_available_point_before_close"] == {"ts": ep(15, 15), "price": 103.0, "lag_sec": 900}
    assert out["points"]["CLOSE"] == {"status": "PENDING", "price": None, "volume": None} and out["forward_windows"]["09:00"]["return_to_close_pct"] is None
