"""RF-033 C3: samsung forward_validation reaction_reader - checkpoints, open/close rules, forward windows, collector tri-state.

Pure functions plus tmp macro files; the Kiwoom index collector is replaced by in-memory stubs (no collector root I/O).
"""
from __future__ import annotations

import json
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import reaction_reader as rr

KST = timezone(timedelta(hours=9))
DAY = "2026-09-07"


def ep(h, m, s=0):
    return int(datetime(2026, 9, 7, h, m, s, tzinfo=KST).timestamp())


def c(ts, close, *, open_=None, high=None, low=None, volume=100.0):
    return {"ts": ts, "open": close if open_ is None else open_, "high": close if high is None else high, "low": close if low is None else low, "close": close, "volume": volume}


# ---------- helpers ----------

def test_number_pct_checkpoint_epoch():
    assert rr._number(None) is None and rr._number("") is None and rr._number("x") is None and rr._number("1.5") == 1.5
    assert rr._pct(110.0, 100.0) == 10.0 and rr._pct(None, 1.0) is None and rr._pct(1.0, 0.0) is None and rr._pct(1.0, None) is None
    assert rr._checkpoint_epoch(DAY, "09:00") == ep(9, 0) and rr._checkpoint_epoch(DAY, "CLOSE") == ep(15, 30)


def test_point_at_uses_first_row_at_or_after_epoch_within_lag():
    rows = [c(ep(9, 0), 1), c(ep(9, 5), 2), c(ep(9, 6, 40), 3)]
    assert rr._point_at(rows, ep(9, 5), 90)["close"] == 2
    assert rr._point_at(rows, ep(9, 5, 1), 90) is None                          # first row >= epoch is 09:06:40, 99s late > 90
    assert rr._point_at(rows, ep(9, 5, 1), 99)["close"] == 3
    assert rr._point_at(rows, ep(9, 5, 1), 98) is None                          # lag boundary 99s is exclusive of 98
    assert rr._point_at(rows, ep(9, 30), 90) is None and rr._point_at([], ep(9, 0), 90) is None


def test_opening_point_skips_zero_volume_placeholders_and_window_is_0900_to_0903():
    rows = [c(ep(8, 59), 1), c(ep(9, 0), 2, volume=0.0), c(ep(9, 1), 3, volume=5.0), c(ep(9, 2), 4)]
    assert rr._opening_point(rows, DAY)["close"] == 3
    assert rr._opening_point([c(ep(9, 3), 5)], DAY)["close"] == 5               # 09:03 inclusive
    assert rr._opening_point([c(ep(9, 3, 1), 5)], DAY) is None
    assert rr._opening_point([c(ep(9, 0), 5, volume=None)], DAY) is None
    assert rr._opening_point([c(ep(9, 0), 5, open_=0.0)], DAY) is None
    assert rr._opening_point([], DAY) is None


def test_close_point_is_last_row_in_closing_auction_window():
    rows = [c(ep(15, 19), 1), c(ep(15, 20), 2), c(ep(15, 30), 3), c(ep(15, 31), 4), c(ep(15, 31, 1), 5)]
    assert rr._close_point(rows, DAY)["close"] == 4                              # up to close+60s inclusive
    assert rr._close_point([c(ep(15, 19, 59), 1)], DAY) is None
    assert rr._close_point([c(ep(15, 20), 9)], DAY)["close"] == 9                # window start inclusive


def test_last_available_point_before_close_is_informational_and_bounded():
    rows = [c(ep(15, 15), 7)]
    r = rr._last_available_point_before_close(rows, DAY, max_lookback_sec=1800)
    assert r == {"ts": ep(15, 15), "price": 7.0, "lag_sec": 900}
    assert rr._last_available_point_before_close(rows, DAY, max_lookback_sec=899) is None
    assert rr._last_available_point_before_close([c(ep(15, 30, 30), 8)], DAY, max_lookback_sec=60) is None   # lag < 0 (after close)
    assert rr._last_available_point_before_close([], DAY, max_lookback_sec=60) is None


# ---------- forward window ----------

def test_forward_window_observed_pending_and_authoritative_close():
    rows = [c(100, 100.0), c(160, 110.0), c(220, 90.0)]
    w = rr._forward_window(rows, entry_ts=100, entry_price=100.0)
    assert w == {"status": "OBSERVED", "return_to_close_pct": -10.0, "mfe_pct": 10.0, "mae_pct": -10.0}
    assert rr._forward_window(rows, entry_ts=100, entry_price=None)["status"] == "PENDING"
    assert rr._forward_window(rows, entry_ts=100, entry_price=0.0)["status"] == "PENDING"
    assert rr._forward_window(rows, entry_ts=9999, entry_price=100.0)["status"] == "PENDING"       # no rows at/after entry
    auth = rr._forward_window(rows, entry_ts=100, entry_price=100.0, authoritative_close={"price": 120.0, "ts": 500})
    assert auth["return_to_close_pct"] == 20.0 and auth["mfe_pct"] == 20.0                        # authoritative close included in the extremes
    stale = rr._forward_window(rows, entry_ts=300, entry_price=100.0, authoritative_close={"price": 120.0, "ts": 299})
    assert stale["status"] == "PENDING"                                                           # close older than entry ignored
    only_close = rr._forward_window(rows, entry_ts=9999, entry_price=100.0, authoritative_close={"price": 120.0, "ts": 9999})
    assert only_close["status"] == "OBSERVED" and only_close["return_to_close_pct"] == 20.0


# ---------- stock reaction ----------

def _day_rows():
    return [c(ep(9, 0), 100.0, open_=100.0, high=101, low=99), c(ep(9, 3), 101.0, high=102), c(ep(9, 5), 102.0), c(ep(9, 10), 103.0), c(ep(9, 15), 104.0),
            c(ep(9, 30), 105.0, high=106), c(ep(10, 0), 106.0), c(ep(15, 25), 107.0, low=98), c(ep(15, 30), 108.0, high=109)]


TARGET = {"key": "samsung", "symbol": "005930", "kind": "stock"}


def test_stock_reaction_full_day():
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=_day_rows(), previous_close=98.0)
    assert out["evidence_status"] == "AVAILABLE" and out["opening_gap_pct"] == pytest.approx(2.040816, abs=1e-6)
    assert [out["points"][k]["status"] for k in rr.CHECKPOINTS] == ["OBSERVED"] * 8
    assert out["points"]["09:00"]["price"] == 100.0 and out["points"]["CLOSE"]["price"] == 108.0 and out["points"]["10:00"]["ts"] == ep(10, 0)
    assert out["points"]["09:05"]["return_from_previous_close_pct"] == pytest.approx((102 / 98 - 1) * 100, abs=1e-5)
    assert out["day_high"] == 109 and out["day_low"] == 98
    assert out["forward_windows"]["09:00"]["status"] == "OBSERVED" and out["forward_windows"]["09:00"]["return_to_close_pct"] == 8.0
    assert set(out["forward_windows"]) == set(rr.CHECKPOINTS[:-1]) and out["last_available_point_before_close"] is None
    assert out["source"] == "q10_current_day_minute_candles" and out["actual_open_policy"] == "first_positive_volume_candle_0900_to_0903"


def test_stock_reaction_without_close_marks_windows_partial_and_hides_close_return():
    rows = [r for r in _day_rows() if r["ts"] < ep(15, 20)]
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=rows, previous_close=98.0, last_available_lookback_sec=0)
    assert out["points"]["CLOSE"] == {"status": "PENDING", "price": None, "volume": None}
    w = out["forward_windows"]["09:00"]
    assert w["status"] == "PARTIAL" and w["return_to_close_pct"] is None and w["mfe_pct"] is not None
    assert out["last_available_point_before_close"] is None                       # opt-in only


def test_stock_reaction_empty_or_zero_ts_rows_is_insufficient_evidence():
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=[{"ts": 0, "close": 1}, {"ts": ep(9, 0), "close": None}], previous_close=None)
    assert out["evidence_status"] == "INSUFFICIENT_EVIDENCE" and out["opening_gap_pct"] is None and out["day_high"] is None and out["path"] == []


def test_stock_reaction_collector_override_tristate():
    rows = [r for r in _day_rows() if r["ts"] < ep(15, 20)]

    def override(label):
        if label == "09:30":
            return {"ts": ep(9, 30), "close": 777.0, "volume": None, "source": "q10_index_observation_collector", "capture_status": "AVAILABLE"}
        if label == "10:00":
            return {"integrity_failure": True, "reason": "late", "collector_status": "LATE_MISSED", "unverified_observation": {"price": 5.0}}
        return None

    out = rr._stock_reaction(day=DAY, target=TARGET, rows=rows, previous_close=100.0, collector_override=override)
    assert out["points"]["09:30"]["price"] == 777.0 and out["points"]["09:30"]["source"] == "q10_index_observation_collector"
    p = out["points"]["10:00"]
    assert p["status"] == "PENDING" and p["integrity_failure"] is True and p["integrity_reason"] == "late" and p["collector_status"] == "LATE_MISSED"
    assert p["unverified_observation"] == {"price": 5.0}                          # INVALID never falls back to the legacy 10:00 candle
    assert out["points"]["09:05"]["status"] == "OBSERVED"                          # ABSENT (None) -> legacy path


def test_close_override_is_the_single_authoritative_price_for_display_and_return():
    rows = [c(ep(9, 0), 100.0), c(ep(15, 25), 90.0)]
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=rows, previous_close=100.0,
                             collector_override=lambda label: {"ts": ep(15, 30), "close": 110.0, "source": "s", "capture_status": "AVAILABLE"} if label == "CLOSE" else None)
    assert out["points"]["CLOSE"]["price"] == 110.0 and out["forward_windows"]["09:00"]["return_to_close_pct"] == 10.0   # not 90 from legacy rows


# ---------- index timeline ----------

def _macro(root, name, generated_at, idx):
    d = root / DAY
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps({"generated_at": generated_at, "korea_indices": {"indices": idx}}), encoding="utf-8")


def test_load_index_timeline_parses_dedups_and_skips_bad(tmp_path):
    _macro(tmp_path, "a_macro_indicators.json", "2026-09-07T00:00:00Z", {"KOSPI": {"current": 100, "previous_close": 99, "high": 101}})
    _macro(tmp_path, "b_macro_indicators.json", "2026-09-07T00:00:00+00:00", {"KOSPI": {"current": 102}})            # same ts: later file wins
    _macro(tmp_path, "c_macro_indicators.json", "2026-09-07T00:05:00Z", {"KOSDAQ": {"current": 5}})                   # other index
    _macro(tmp_path, "d_macro_indicators.json", "garbage", {"KOSPI": {"current": 1}})
    (tmp_path / DAY / "e_macro_indicators.json").write_text("{bad", encoding="utf-8")
    _macro(tmp_path, "g_macro_indicators.json", "2026-09-07T00:10:00Z", {"KOSPI": {"current": 103, "open": 0, "volume": 7}})
    rows = rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI")
    assert [r["close"] for r in rows] == [102, 103] and rows[0]["open"] == 102 and rows[1]["open"] == 103 and rows[1]["volume"] == 7
    assert rows[0]["previous_close"] is None and rr.load_index_timeline(day="2026-01-01", macro_root=tmp_path, index_name="KOSPI") == []


# ---------- collector tri-state ----------

@pytest.fixture
def collector(monkeypatch):
    mod = types.ModuleType("libs.market.q10_index_observation_collector")
    state = {"obs": {}, "evidence": True}
    mod.observation_for_slot = lambda day, slot, root=None: state["obs"]
    mod._has_verification_evidence = lambda indices, **kw: state["evidence"]
    monkeypatch.setitem(sys.modules, "libs.market.q10_index_observation_collector", mod)
    return state


def _verified(price=2500.0):
    return {"availability": "AVAILABLE", "actual_observed_at_kst": "2026-09-07T09:30:05+09:00", "source": "kiwoom.ka20009",
            "indices": {"KOSPI": {"current": price, "market_observed_at": "2026-09-07T09:30:00+09:00"}}}


def test_collector_row_absent_only_when_never_attempted(collector):
    collector["obs"] = {"availability": "MISSING", "never_attempted": True}
    assert rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None) is None
    collector["obs"] = {"availability": "MISSING"}                                  # missing without never_attempted -> INVALID
    r = rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)
    assert r["integrity_failure"] is True and r["collector_status"] == "MISSING" and r["reason"] == "collector_observation_not_calculation_usable"


def test_collector_row_invalid_states_carry_unverified_observation(collector):
    collector["obs"] = {"availability": "LATE_MISSED", "error": "too late", "indices": {"KOSPI": {"current": 5.0}}, "source": "src"}
    r = rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)
    assert r["reason"] == "too late" and r["unverified_observation"]["price"] == 5.0 and r["unverified_observation"]["calculation_usable"] is False
    collector["obs"] = {"availability": "CORRUPT_STATE"}
    assert rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)["unverified_observation"] is None


def test_collector_row_verified_and_integrity_branches(collector):
    collector["obs"] = _verified(2500.0)
    r = rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)
    assert r["close"] == 2500.0 and r["open"] == 2500.0 and r["source"] == "q10_index_observation_collector" and r["capture_status"] == "AVAILABLE"
    assert r["ts"] == int(datetime(2026, 9, 7, 9, 30, tzinfo=KST).timestamp())
    collector["evidence"] = False
    assert rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)["reason"] == "verification_evidence_invalid"
    collector["evidence"] = True
    collector["obs"] = _verified()
    assert rr._collector_raw_row(day=DAY, index_name="KOSDAQ", slot="09:30", root=None)["reason"] == "index_component_not_present_in_verified_observation"


def test_collector_row_unparseable_observed_time_with_evidence_ok(collector):
    collector["obs"] = {**_verified(), "actual_observed_at_kst": "nope"}
    r = rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)
    assert r["integrity_failure"] is True and r["reason"] == "observed_timestamp_unparseable"


def test_collector_row_verified_without_market_timestamp_is_integrity_failure(collector):
    """Formerly a TypeError (int(None)); now an INVALID row so legacy fallback stays forbidden (P15 order 2)."""
    obs = _verified()
    obs["indices"]["KOSPI"].pop("market_observed_at")
    collector["obs"] = obs
    r = rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)
    assert r["integrity_failure"] is True and r["reason"] == "market_timestamp_missing" and r["collector_status"] == "AVAILABLE"


# ---------- index reaction & build ----------

def test_build_actual_reactions_routes_stocks_and_indices(tmp_path, collector):
    collector["obs"] = {"availability": "MISSING", "never_attempted": True}
    _macro(tmp_path, "a_macro_indicators.json", "2026-09-07T00:00:00Z", {"KOSPI": {"current": 2500, "previous_close": 2490, "open": 2495}})
    candle_map = {"005930": _day_rows(), "000660": _day_rows()}
    out = rr.build_actual_reactions(day=DAY, candle_map=candle_map, macro_root=tmp_path, signal_inputs={"samsung_previous_close": 98.0, "hynix_previous_close": 50.0})
    assert out["day"] == DAY and set(out["targets"]) == {"samsung", "sk_hynix", "kospi", "kosdaq"}
    assert out["targets"]["samsung"]["previous_close"] == 98.0 and out["targets"]["sk_hynix"]["previous_close"] == 50.0
    k = out["targets"]["kospi"]
    assert k["source"] == "kiwoom_ka20009_macro_snapshots" and k["previous_close"] == 2490.0
    assert out["targets"]["kosdaq"]["evidence_status"] == "INSUFFICIENT_EVIDENCE" and out["targets"]["kosdaq"]["previous_close"] is None
    assert out["targets"]["kosdaq"]["points"]["CLOSE"]["status"] == "PENDING"


def test_index_reaction_close_pending_exposes_last_available_point_but_not_as_close(tmp_path, collector):
    collector["obs"] = {"availability": "MISSING", "never_attempted": True}
    rows = [{"ts": ep(15, 15), "close": 2500.0, "open": 2500.0, "high": 2500.0, "low": 2500.0, "volume": None, "previous_close": 2490.0}]
    out = rr._index_reaction(day=DAY, target={"key": "kospi", "symbol": "KOSPI", "kind": "index"}, rows=rows)
    assert out["points"]["CLOSE"]["status"] == "PENDING" and out["last_available_point_before_close"] == {"ts": ep(15, 15), "price": 2500.0, "lag_sec": 900}


def test_index_reaction_close_invalid_collector_blocks_legacy_fallback(collector):
    collector["obs"] = {"availability": "LATE_MISSED", "error": "x", "indices": {}}
    rows = [{"ts": ep(15, 30), "close": 2500.0, "open": 2500.0, "high": 2500.0, "low": 2500.0, "volume": None, "previous_close": 2490.0}]
    out = rr._index_reaction(day=DAY, target={"key": "kospi", "symbol": "KOSPI", "kind": "index"}, rows=rows)
    assert out["points"]["CLOSE"]["status"] == "PENDING" and out["points"]["CLOSE"]["integrity_failure"] is True


def test_load_index_timeline_skips_non_object_json_and_keeps_reading(tmp_path):
    """Formerly an AttributeError aborting the whole timeline; now only the malformed file is skipped (P15 order 3)."""
    d = tmp_path / DAY
    d.mkdir()
    (d / "f_macro_indicators.json").write_text("[1]", encoding="utf-8")
    _macro(tmp_path, "g_macro_indicators.json", "2026-09-07T00:10:00Z", {"KOSPI": {"current": 7}})
    rows = rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI")
    assert [r["close"] for r in rows] == [7.0]


def test_last_available_lookback_bound_is_inclusive():
    rows = [c(ep(15, 15), 7)]
    assert rr._last_available_point_before_close(rows, DAY, max_lookback_sec=900)["lag_sec"] == 900


def test_opening_point_price_is_the_open_not_the_close():
    rows = [c(ep(9, 0), 105.0, open_=100.0)]
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=rows, previous_close=100.0)
    assert out["points"]["09:00"]["price"] == 100.0 and out["opening_gap_pct"] == 0.0
    assert rr._stock_reaction(day=DAY, target=TARGET, rows=[c(ep(9, 0), 105.0, open_=100.0), c(ep(9, 5), 106.0, open_=1.0)], previous_close=100.0)["points"]["09:05"]["price"] == 106.0


def test_close_window_start_and_end_are_exact():
    assert rr._close_point([c(ep(15, 20) - 1, 1)], DAY) is None and rr._close_point([c(ep(15, 20), 1)], DAY) is not None
    assert rr._close_point([c(ep(15, 31), 1)], DAY) is not None and rr._close_point([c(ep(15, 31) + 1, 1)], DAY) is None


def test_regular_session_range_for_day_high_low_ends_five_minutes_after_close():
    rows = [c(ep(9, 0), 100.0), c(ep(15, 35), 200.0, high=200.0), c(ep(15, 35, 1), 300.0, high=300.0), c(ep(8, 59), 1.0, low=1.0)]
    out = rr._stock_reaction(day=DAY, target=TARGET, rows=rows, previous_close=100.0)
    assert out["day_high"] == 200.0 and out["day_low"] == 100.0
