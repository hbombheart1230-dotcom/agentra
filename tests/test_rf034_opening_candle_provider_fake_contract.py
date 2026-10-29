"""RF-034 C3: opening candle_provider with the Kiwoom history reader and state candle loader stubbed (no network, tmp only)."""
from __future__ import annotations

import json
import socket
from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.opening_rank1_shadow import candle_provider as cp

KST = timezone(timedelta(hours=9))
DAY = "2026-09-07"


@pytest.fixture(autouse=True)
def _deny(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)


def ep(h, m, day=DAY):
    y, mo, d = map(int, day.split("-"))
    return int(datetime(y, mo, d, h, m, tzinfo=KST).timestamp())


def row(h, m, close=100.0, day=DAY):
    return {"ts": ep(h, m, day), "close": close, "open": close, "volume": 1.0}


def test_historical_reference_rows_sorted_filtered_and_fail_soft(tmp_path):
    (tmp_path / "A.json").write_text(json.dumps({"rows": [{"ts": 30}, {"ts": 10}, {"ts": 0}, {"ts": -5}, "junk", {"ts": None}]}), encoding="utf-8")
    (tmp_path / "B.json").write_text("{bad", encoding="utf-8")
    (tmp_path / "C.json").write_text("[1]", encoding="utf-8")
    (tmp_path / "D.json").write_text(json.dumps({"rows": None}), encoding="utf-8")
    out = cp.load_historical_reference_rows(cache_root=tmp_path, symbols=("A", "B", "C", "D", "MISSING"))
    assert [r["ts"] for r in out["A"]] == [10, 30] and out["B"] == out["C"] == out["D"] == out["MISSING"] == []


def test_day_rows_filters_other_days_nonpositive_close_and_sorts():
    rows = [row(9, 5), row(9, 1), row(9, 2, close=0.0), row(9, 3, day="2026-09-08"), {"ts": 0, "close": 5}, {"ts": ep(9, 4), "close": None}]
    out = cp._day_rows(rows, DAY)
    assert [r["ts"] for r in out] == [ep(9, 1), ep(9, 5)]
    assert cp._day_rows([], DAY) == []


def test_close_complete_boundary_1520():
    assert cp._close_complete([]) is False
    assert cp._close_complete([row(15, 19)]) is False and cp._close_complete([row(15, 20)]) is True and cp._close_complete([row(15, 31)]) is True


@pytest.fixture
def fakes(monkeypatch):
    st = {"existing": {}, "history": {}, "history_calls": [], "reader_calls": 0, "existing_calls": []}

    def existing(**kw):
        st["existing_calls"].append(kw)
        return {k: list(v) for k, v in st["existing"].items()}

    class Reader:
        @classmethod
        def from_env(cls):
            st["reader_calls"] += 1
            return "READER"

    def hist(*, reader, symbol, minimum_epoch, cache_root, max_pages):
        st["history_calls"].append({"reader": reader, "symbol": symbol, "minimum_epoch": minimum_epoch, "cache_root": cache_root, "max_pages": max_pages})
        return list(st["history"].get(symbol, ([], {"status": "none"}))[0]), (st["history"].get(symbol) or ([], {"status": "none"}))[1]

    monkeypatch.setattr(cp, "load_existing_candles", existing)
    monkeypatch.setattr(cp, "KiwoomHistoricalMinuteReader", Reader)
    monkeypatch.setattr(cp, "load_or_fetch_symbol_history", hist)
    return st


def test_complete_state_candles_skip_history_entirely(tmp_path, fakes):
    fakes["existing"] = {"A": [row(9, 0), row(15, 20)]}
    candles, meta = cp.load_opening_candles(state_path=tmp_path / "s.json", day=DAY, symbols=("A",), allow_fresh_fetch=True, cache_root=tmp_path / "c")
    assert fakes["history_calls"] == [] and fakes["reader_calls"] == 0
    assert meta == {"state_or_current_fetch_symbol_count": 1, "historical_fallback_requested_symbols": [], "historical_fallback": {}, "complete_symbol_count": 1}
    assert fakes["existing_calls"][0]["run_id_prefix"] == "opening_rank1_shadow" and fakes["existing_calls"][0]["allow_fresh_fetch"] is True


def test_incomplete_symbol_falls_back_to_history_and_replaces_when_complete(tmp_path, fakes):
    fakes["existing"] = {"A": [row(9, 0, 100.0)], "B": [row(9, 0), row(15, 25)]}
    fakes["history"] = {"A": ([row(9, 0, 101.0), row(15, 21, 102.0), row(15, 21, 5.0, day="2026-09-06")], {"pages": 3})}
    candles, meta = cp.load_opening_candles(state_path=tmp_path / "s.json", day=DAY, symbols=("A", "B"), allow_fresh_fetch=True, cache_root=tmp_path / "c")
    assert [h["symbol"] for h in fakes["history_calls"]] == ["A"] and fakes["history_calls"][0]["reader"] == "READER" and fakes["reader_calls"] == 1
    assert fakes["history_calls"][0]["max_pages"] == 20 and fakes["history_calls"][0]["cache_root"] == tmp_path / "c"
    assert fakes["history_calls"][0]["minimum_epoch"] == ep(9, 0)
    assert [r["close"] for r in candles["A"]] == [101.0, 102.0]                          # other-day history row dropped
    assert meta["historical_fallback_requested_symbols"] == ["A"] and meta["historical_fallback"] == {"A": {"pages": 3}} and meta["complete_symbol_count"] == 2


def test_incomplete_history_does_not_replace_existing_partial_state_but_fills_empty(tmp_path, fakes):
    fakes["existing"] = {"A": [row(9, 0, 100.0)]}
    fakes["history"] = {"A": ([row(9, 0, 101.0), row(10, 0, 102.0)], {}), "B": ([row(9, 5, 7.0)], {})}
    candles, meta = cp.load_opening_candles(state_path=tmp_path / "s.json", day=DAY, symbols=("A", "B"), allow_fresh_fetch=True, cache_root=tmp_path / "c")
    assert [r["close"] for r in candles["A"]] == [100.0]                                 # partial history is not an upgrade over partial state
    assert [r["close"] for r in candles["B"]] == [7.0]                                   # but it fills a symbol with no state rows
    assert meta["complete_symbol_count"] == 0 and meta["state_or_current_fetch_symbol_count"] == 2


def test_no_fresh_fetch_means_no_reader_but_cache_history_still_consulted(tmp_path, fakes):
    fakes["existing"] = {"A": []}
    fakes["history"] = {"A": ([row(9, 0), row(15, 30)], {"source": "cache"})}
    candles, meta = cp.load_opening_candles(state_path=tmp_path / "s.json", day=DAY, symbols=("A",), allow_fresh_fetch=False, cache_root=tmp_path / "c")
    assert fakes["reader_calls"] == 0 and fakes["history_calls"][0]["reader"] is None
    assert len(candles["A"]) == 2 and meta["complete_symbol_count"] == 1 and meta["state_or_current_fetch_symbol_count"] == 1
    assert fakes["existing_calls"][0]["allow_fresh_fetch"] is False


def test_symbol_missing_from_state_is_treated_as_unresolved(tmp_path, fakes):
    fakes["existing"] = {}
    fakes["history"] = {}
    candles, meta = cp.load_opening_candles(state_path=tmp_path / "s.json", day=DAY, symbols=("Z",), allow_fresh_fetch=False, cache_root=tmp_path / "c")
    assert candles["Z"] == [] and meta["historical_fallback_requested_symbols"] == ["Z"]
