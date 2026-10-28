"""RF-033 C3: baseline_btc_woori_tech.data_provider with a fake yfinance (no network, no disk).

``require_yfinance`` is replaced by an in-memory fake and ``merge_capture_into_signal_payload`` by an identity stub,
so the Ticker/history path and the capture-root read are never reached for real.
"""
from __future__ import annotations

import socket
from datetime import datetime, timedelta, timezone

import pytest

from libs.market.yfinance_support import DataSourceDependencyError
from libs.reporting.baseline_btc_woori_tech import data_provider as dp
from libs.reporting.baseline_btc_woori_tech import point_in_time_capture as pit

KST = timezone(timedelta(hours=9))
DAY = "2026-10-28"


@pytest.fixture(autouse=True)
def _deny_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)
    dp._DAILY_RESEARCH_CACHE.clear()
    yield
    dp._DAILY_RESEARCH_CACHE.clear()


class _Row(dict):
    pass


class _Frame:
    def __init__(self, items, empty=None):
        self._items = items
        self.empty = (not items) if empty is None else empty

    def iterrows(self):
        return iter(self._items)


class _Ticker:
    log: list = []

    def __init__(self, symbol, frames):
        self.symbol = symbol
        self._frames = frames

    def history(self, period, interval):
        _Ticker.log.append((self.symbol, period, interval))
        f = self._frames[self.symbol]
        if isinstance(f, Exception):
            raise f
        return f


class _YF:
    def __init__(self, frames):
        self.frames = frames

    def Ticker(self, symbol):  # noqa: N802 - mirrors yfinance API
        return _Ticker(symbol, self.frames)


def _install(monkeypatch, frames):
    _Ticker.log = []
    monkeypatch.setattr(dp, "require_yfinance", lambda: _YF(frames))


def _kst(h, m=0, day=DAY):
    y, mo, d = map(int, day.split("-"))
    return datetime(y, mo, d, h, m, tzinfo=KST)


def _minute_frame(start, n, base=100.0, step=1.0):
    return _Frame([(start + timedelta(minutes=i), _Row(Close=base + i * step, Open=base, High=base + 1, Low=base - 1, Volume=5)) for i in range(n)])


def test_yf_rows_filters_days_and_dedups_and_sorts(monkeypatch):
    old = _kst(10, day="2026-10-20")
    ok = _kst(9, 0)
    items = [
        (old, _Row(Close=50.0)),                       # outside {day, day-1} -> dropped
        (ok + timedelta(minutes=1), _Row(Close=2.0)),  # later, appears first
        (ok, _Row(Close=1.0, Open=0.0, High=0.0, Low=0.0, Volume=None)),
        (ok, _Row(Close=1.5)),                         # duplicate epoch: last wins
        (ok + timedelta(minutes=2), _Row(Close=0.0)),  # close<=0 dropped
        (ok + timedelta(minutes=3), _Row(Close=None)),  # None -> 0 -> dropped
        ("not-a-datetime", _Row(Close=9.0)),           # skipped
        (datetime(2026, 10, 28, 0, 30), _Row(Close=3.0)),  # naive -> UTC (09:30 KST)
    ]
    _install(monkeypatch, {"T": _Frame(items)})
    rows = dp._yf_rows("T", day=DAY)
    assert [r["close"] for r in rows] == [1.5, 2.0, 3.0]
    assert [r["ts"] for r in rows] == sorted(r["ts"] for r in rows)
    first = rows[0]
    assert first["raw_ts"] == "20261028090000"
    assert first["open"] == 1.5 and first["high"] == 1.5 and first["low"] == 1.5 and first["volume"] == 0.0
    assert _Ticker.log == [("T", "2d", "1m")]


def test_yf_rows_restrict_flag_and_period_passthrough(monkeypatch):
    old = _kst(10, day="2026-10-20")
    _install(monkeypatch, {"T": _Frame([(old, _Row(Close=7.0))])})
    assert dp._yf_rows("T", day=DAY) == []
    rows = dp._yf_rows("T", day=DAY, period="max", interval="1d", restrict_to_recent_days=False)
    assert [r["close"] for r in rows] == [7.0]
    assert _Ticker.log[-1] == ("T", "max", "1d")


def test_yf_rows_degrades_to_empty(monkeypatch):
    _install(monkeypatch, {"E": RuntimeError("boom"), "N": None, "Z": _Frame([]), "I": _Frame([("x", None)], empty=False)})
    assert dp._yf_rows("E", day=DAY) == []          # history raised
    assert dp._yf_rows("N", day=DAY) == []          # None frame
    assert dp._yf_rows("Z", day=DAY) == []          # empty frame
    # row without .get -> AttributeError in the loop is swallowed, but non-datetime index skips first
    bad = _Frame([(_kst(9), object())], empty=False)
    _install(monkeypatch, {"B": bad})
    assert dp._yf_rows("B", day=DAY) == []


def test_yf_rows_missing_dependency_is_explicit(monkeypatch):
    def _missing():
        raise DataSourceDependencyError("yfinance", "ImportError: x")

    monkeypatch.setattr(dp, "require_yfinance", _missing)
    with pytest.raises(DataSourceDependencyError):
        dp._yf_rows("T", day=DAY)


def test_momentum_rows_skips_first_five_and_computes_changes():
    start = _kst(9, 0)
    rows = [{"ts": int((start + timedelta(minutes=i)).timestamp()), "raw_ts": str(i), "close": 100.0 + i} for i in range(8)]
    out = dp._momentum_rows(rows, source="s")
    assert [o["raw_ts"] for o in out] == ["5", "6", "7"]
    o5 = out[0]
    assert o5["source"] == "s" and o5["price"] == 105.0
    assert o5["momentum_5m_pct"] == round((105 / 100 - 1) * 100, 6)
    assert o5["momentum_15m_pct"] is None and o5["momentum_60m_pct"] is None and o5["momentum_24h_pct"] is None
    assert o5["momentum_since_krx_open_pct"] == round((105 / 100 - 1) * 100, 6)


def test_momentum_rows_before_krx_open_has_no_open_anchor():
    start = _kst(7, 0)
    rows = [{"ts": int((start + timedelta(minutes=i)).timestamp()), "close": 10.0 + i} for i in range(7)]
    out = dp._momentum_rows(rows, source="s")
    assert out and all(o["momentum_since_krx_open_pct"] is None for o in out)
    assert dp._momentum_rows([], source="s") == []


def test_load_btc_signal_rows_happy_path_with_stubbed_capture(monkeypatch):
    start = _kst(9, 0)
    frames = {
        "BTC-USD": _minute_frame(start, 8, 100.0),
        "COIN": _minute_frame(start, 8, 200.0),
        "KRW=X": _minute_frame(start, 8, 1000.0, 0.0),
        "069500.KS": _Frame([]),
    }
    _install(monkeypatch, frames)
    seen = {}

    def _merge(payload, *, day, root=None):
        seen["day"] = day
        seen["keys"] = sorted(payload["sources"])
        out = dict(payload)
        out["available_sources"] = ["btc_krw", "btc_usd"]
        out["btc_0855_capture_reused"] = True
        out["btc_0855_capture_status"] = "ok"
        return out

    monkeypatch.setattr(pit, "merge_capture_into_signal_payload", _merge)
    out = dp.load_btc_signal_rows(day=DAY, include_research_context=False)
    assert seen == {"day": DAY, "keys": ["btc_krw", "btc_usd", "coinbase_proxy"]}
    assert out["schema_version"] == "baseline_btc_signal_rows.v2"
    assert out["available"] is True and out["available_sources"] == ["btc_krw", "btc_usd"]
    assert out["fallback_reason"] == "" and out["data_source_error"] == ""
    assert out["btc_0855_capture_reused"] is True and out["btc_0855_capture_status"] == "ok"
    assert out["research_context_requested"] is False
    rc = out["research_context"]
    assert rc["btc_usd_daily"] == [] and rc["woori_daily"] == [] and rc["behavior_effect"] == "observation_only"
    # derived KRW = USD close * fx close (fx constant 1000)
    assert out["sources"]["btc_krw"][0]["price"] == pytest.approx(105.0 * 1000.0)
    assert out["sources"]["btc_krw"][0]["source"] == "derived:BTC-USD*KRW=X"
    assert out["sources"]["coinbase_proxy"][0]["source"] == "yfinance:COIN"
    # only the three intraday tickers were requested
    assert {t for t, _, _ in _Ticker.log} == {"BTC-USD", "COIN", "KRW=X"}


def test_load_btc_signal_rows_research_context_and_cache(monkeypatch):
    daily = _Frame([(_kst(0, 0, day="2026-10-10"), _Row(Close=11.0))])
    frames = {"BTC-USD": _Frame([]), "COIN": _Frame([]), "KRW=X": _Frame([]), dp.TARGET_TICKER: daily}
    _install(monkeypatch, frames)
    monkeypatch.setattr(pit, "merge_capture_into_signal_payload", lambda payload, *, day, root=None: dict(payload))
    out = dp.load_btc_signal_rows(day=DAY)
    assert out["available"] is False and out["fallback_reason"] == "btc_and_crypto_proxy_unavailable"
    assert out["research_context"]["woori_daily"][0]["close"] == 11.0
    n_calls = len(_Ticker.log)
    # mutate the returned copy: cache must hand out independent dicts
    out["research_context"]["woori_daily"][0]["close"] = -1.0
    again = dp.load_btc_signal_rows(day=DAY)
    assert again["research_context"]["woori_daily"][0]["close"] == 11.0
    daily_calls = [c for c in _Ticker.log[n_calls:] if c[2] == "1d"]
    assert daily_calls == []  # served from _DAILY_RESEARCH_CACHE
    assert ("BTC-USD", "max", "1d") in [c for c in _Ticker.log if c[2] == "1d"]


def test_load_btc_signal_rows_dependency_missing_is_carried_not_raised(monkeypatch, caplog):
    def _missing():
        raise DataSourceDependencyError("yfinance")

    monkeypatch.setattr(dp, "require_yfinance", _missing)
    monkeypatch.setattr(pit, "merge_capture_into_signal_payload", lambda payload, *, day, root=None: dict(payload))
    with caplog.at_level("ERROR"):
        out = dp.load_btc_signal_rows(day=DAY)
    assert out["available"] is False
    assert out["fallback_reason"] == "dependency_missing:yfinance"
    assert out["data_source_error"] == "dependency_missing:yfinance"
    assert out["research_context"]["btc_usd_daily"] == [] and out["research_context"]["woori_daily"] == []
    assert "DATA_SOURCE_DEPENDENCY_MISSING" in caplog.text
