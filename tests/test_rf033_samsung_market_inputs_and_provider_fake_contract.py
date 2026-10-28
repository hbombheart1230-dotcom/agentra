"""RF-033 C3: samsung_hynix market_inputs (fake yfinance) and data_provider macro readers (tmp only).

No network (socket connect denied), yfinance replaced via ``require_yfinance`` in the owner module, files only under tmp_path.
"""
from __future__ import annotations

import json
import socket
from datetime import datetime, timedelta, timezone

import pytest

from libs.market.yfinance_support import DataSourceDependencyError
from libs.reporting.baseline_samsung_hynix import data_provider as dp
from libs.reporting.baseline_samsung_hynix.forward_validation import market_inputs as mi

UTC = timezone.utc
AS_OF = datetime(2026, 10, 28, 0, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _deny_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)


class _Idx(datetime):
    pass


class _Row(dict):
    pass


class _Frame:
    def __init__(self, items):
        self.items = items

    def iterrows(self):
        return iter(self.items)


def _daily_frame(closes, start=datetime(2026, 10, 15, tzinfo=UTC)):
    return _Frame([(start + timedelta(days=i), _Row(Close=c, Volume=10)) for i, c in enumerate(closes)])


def _intraday_frame(last_epoch_dt, closes):
    n = len(closes)
    return _Frame([(last_epoch_dt - timedelta(minutes=5 * (n - 1 - i)), _Row(Close=c)) for i, c in enumerate(closes)])


class _FakeYF:
    def __init__(self, hist, fast=None):
        self.hist, self.fast, self.calls = hist, fast or {}, []

    def Ticker(self, symbol):  # noqa: N802
        outer = self

        class _T:
            @property
            def fast_info(self):
                v = outer.fast.get(symbol)
                if isinstance(v, Exception):
                    raise v
                return {"previous_close": v}

            def history(self, **kw):
                outer.calls.append((symbol, kw["period"], kw["interval"], kw.get("prepost"), kw.get("auto_adjust")))
                f = outer.hist.get((symbol, kw["interval"]))
                if isinstance(f, Exception):
                    raise f
                return f if f is not None else _Frame([])

        return _T()


def _install(monkeypatch, yf):
    monkeypatch.setattr(mi, "require_yfinance", lambda: yf)


# ---------- _rows ----------

def test_rows_filters_nonpositive_and_formats(monkeypatch):
    items = [(AS_OF, _Row(Close=0.0)), (AS_OF + timedelta(days=1), _Row(Close="x")), (AS_OF + timedelta(days=2), _Row(Close=5.0, Volume=""))]
    yf = _FakeYF({("T", "1d"): _Frame(items)})
    _install(monkeypatch, yf)
    rows = mi.YFinanceLeadMarketProvider._rows("T", period="10d", interval="1d")
    assert len(rows) == 1 and rows[0]["close"] == 5.0 and rows[0]["volume"] is None
    assert rows[0]["epoch"] == int((AS_OF + timedelta(days=2)).timestamp())
    assert rows[0]["timestamp"].startswith("2026-10-30")
    assert yf.calls == [("T", "10d", "1d", False, False)]


def test_rows_degrades_on_history_error_and_bad_frame(monkeypatch):
    _install(monkeypatch, _FakeYF({("E", "1d"): RuntimeError("x"), ("B", "1d"): object()}))
    assert mi.YFinanceLeadMarketProvider._rows("E", period="1d", interval="1d") == []
    assert mi.YFinanceLeadMarketProvider._rows("B", period="1d", interval="1d") == []  # no iterrows


def test_rows_plain_index_without_isoformat(monkeypatch):
    _install(monkeypatch, _FakeYF({("P", "1d"): _Frame([(7, _Row(Close=2.0))])}))
    r = mi.YFinanceLeadMarketProvider._rows("P", period="1d", interval="1d")
    assert r == [{"timestamp": "7", "epoch": 0, "close": 2.0, "volume": None}]


def test_missing_dependency_is_explicit_everywhere(monkeypatch):
    def _missing():
        raise DataSourceDependencyError("yfinance")

    monkeypatch.setattr(mi, "require_yfinance", _missing)
    p = mi.YFinanceLeadMarketProvider()
    for call in (lambda: p._rows("T", period="1d", interval="1d"), lambda: p._daily("T"), lambda: p._quote_previous_close("T"), lambda: p.capture(as_of=AS_OF)):
        with pytest.raises(DataSourceDependencyError):
            call()


# ---------- _daily ----------

def test_daily_available_returns_and_three_day_base(monkeypatch):
    _install(monkeypatch, _FakeYF({("T", "1d"): _daily_frame([100.0, 110.0, 121.0, 133.1])}))
    d = mi.YFinanceLeadMarketProvider()._daily("T")
    assert d["status"] == "AVAILABLE" and d["observation_count"] == 4
    assert d["current"] == 133.1 and d["previous"] == 121.0
    assert d["return_pct"] == pytest.approx(10.0, abs=1e-4)
    assert d["three_day_return_pct"] == pytest.approx(33.1, abs=1e-4)
    # fewer than 4 rows -> no three-day base
    _install(monkeypatch, _FakeYF({("T", "1d"): _daily_frame([100.0, 110.0, 121.0])}))
    assert mi.YFinanceLeadMarketProvider()._daily("T")["three_day_return_pct"] is None


def test_daily_unavailable_with_fewer_than_two_rows(monkeypatch):
    _install(monkeypatch, _FakeYF({("T", "1d"): _daily_frame([100.0])}))
    assert mi.YFinanceLeadMarketProvider()._daily("T") == {
        "status": "UNAVAILABLE", "ticker": "T", "source": "yfinance", "reason": "daily_history_missing"}


# ---------- intraday ----------

def _intraday_yf(age_sec, *, fast, closes=(10.0, 11.0)):
    last = AS_OF - timedelta(seconds=age_sec)
    future = _Row(Close=999.0)
    frame = _intraday_frame(last, list(closes))
    frame.items.append((AS_OF + timedelta(minutes=5), future))  # after as_of -> must be excluded
    return _FakeYF({("NQ=F", "1d"): _daily_frame([100.0, 110.0]), ("NQ=F", "5m"): frame}, fast={"NQ=F": fast})


def test_intraday_uses_quote_previous_close_and_excludes_future_rows(monkeypatch):
    _install(monkeypatch, _intraday_yf(60, fast=10.0))
    o = mi.YFinanceLeadMarketProvider()._intraday_vs_previous_close("NQ=F", as_of=AS_OF)
    assert o["status"] == "AVAILABLE" and o["current"] == 11.0
    assert o["previous_close"] == 10.0 and o["previous_close_source"] == "yfinance.fast_info"
    assert o["return_pct"] == pytest.approx(10.0) and o["snapshot_age_sec"] == 60
    assert o["max_snapshot_age_sec"] == 15 * 60


def test_intraday_falls_back_to_daily_latest_when_quote_missing_or_raises(monkeypatch):
    for fast in (None, RuntimeError("x")):
        _install(monkeypatch, _intraday_yf(60, fast=fast))
        o = mi.YFinanceLeadMarketProvider()._intraday_vs_previous_close("NQ=F", as_of=AS_OF)
        assert o["previous_close_source"] == "daily_latest_fallback" and o["previous_close"] == 110.0


def test_intraday_stale_boundary_is_exclusive_at_900s(monkeypatch):
    _install(monkeypatch, _intraday_yf(900, fast=10.0))
    assert mi.YFinanceLeadMarketProvider()._intraday_vs_previous_close("NQ=F", as_of=AS_OF)["status"] == "AVAILABLE"
    _install(monkeypatch, _intraday_yf(901, fast=10.0))
    o = mi.YFinanceLeadMarketProvider()._intraday_vs_previous_close("NQ=F", as_of=AS_OF)
    assert o["status"] == "UNAVAILABLE" and o["reason"] == "point_in_time_quote_stale" and o["snapshot_age_sec"] == 901


def test_intraday_unavailable_when_daily_or_rows_missing(monkeypatch):
    _install(monkeypatch, _FakeYF({("NQ=F", "1d"): _daily_frame([100.0]), ("NQ=F", "5m"): _intraday_frame(AS_OF, [1.0])}))
    o = mi.YFinanceLeadMarketProvider()._intraday_vs_previous_close("NQ=F", as_of=AS_OF)
    assert o["reason"] == "point_in_time_quote_missing"
    _install(monkeypatch, _FakeYF({("NQ=F", "1d"): _daily_frame([100.0, 101.0])}))
    assert mi.YFinanceLeadMarketProvider()._intraday_vs_previous_close("NQ=F", as_of=AS_OF)["reason"] == "point_in_time_quote_missing"


# ---------- capture ----------

def test_capture_keys_adr_fallback_and_unavailable(monkeypatch):
    yf = _FakeYF({("HXSCL", "1d"): _daily_frame([10.0, 11.0])})
    _install(monkeypatch, yf)
    obs = mi.YFinanceLeadMarketProvider().capture(as_of=AS_OF)
    assert set(obs) == set(mi.YFinanceLeadMarketProvider.DAILY_TICKERS) | {"hynix_adr"} | set(mi.YFinanceLeadMarketProvider.INTRADAY_TICKERS)
    assert obs["hynix_adr"]["ticker"] == "HXSCL"  # first ADR ticker had no data, second used
    assert obs["sox"]["status"] == "UNAVAILABLE"
    assert mi.all_observations_unavailable({k: v for k, v in obs.items() if k != "hynix_adr"}) is True
    assert mi.all_observations_unavailable(obs) is False


def test_capture_adr_unavailable_when_both_missing(monkeypatch):
    _install(monkeypatch, _FakeYF({}))
    obs = mi.YFinanceLeadMarketProvider().capture(as_of=AS_OF)
    assert obs["hynix_adr"] == {"status": "UNAVAILABLE", "source": "yfinance", "reason": "hynix_adr_unavailable", "tickers_tried": ["HXSCF", "HXSCL"]}
    assert mi.all_observations_unavailable(obs) is True
    assert mi.all_observations_unavailable({"x": "not-a-mapping"}) is True


# ---------- pure helpers ----------

def test_number_and_return_pct():
    assert mi._number(None) is None and mi._number("") is None and mi._number("x") is None and mi._number("2.5") == 2.5
    assert mi._return_pct(None, 1.0) is None and mi._return_pct(1.0, 0.0) is None and mi._return_pct(1.0, None) is None
    assert mi._return_pct(110.0, 100.0) == 10.0


def test_flatten_signal_inputs_us10y_scaling_and_pass_through():
    obs = {
        "sox": {"return_pct": 1.5}, "vix": {"return_pct": "2"}, "usdkrw_0850": {"return_pct": -0.5},
        "us10y": {"current": 42.5, "previous": 42.0},
        "sk_hynix": {"return_pct": 3.0, "three_day_return_pct": 5.0, "current": 200000.0},
        "samsung": {"return_pct": -1.0, "current": 70000.0},
    }
    f = mi.flatten_signal_inputs(obs)
    assert f["sox_return_pct"] == 1.5 and f["vix_change_pct"] == 2.0 and f["usdkrw_0850_change_pct"] == -0.5
    assert f["us10y_yield_change"] == 0.05  # values >10 are quoted x10 -> divisor 10
    assert f["hynix_previous_day_return_pct"] == 3.0 and f["hynix_3d_cumulative_return_pct"] == 5.0
    assert f["hynix_previous_close"] == 200000.0 and f["samsung_previous_day_return_pct"] == -1.0 and f["samsung_previous_close"] == 70000.0
    assert f["nvidia_return_pct"] is None and f["us10y_yield_change_unit"] == "percentage_point"
    f2 = mi.flatten_signal_inputs({"us10y": {"current": 4.5, "previous": 4.0}})
    assert f2["us10y_yield_change"] == 0.5
    f3 = mi.flatten_signal_inputs({"us10y": {"current": 4.5}, "sk_hynix": "bad"})
    assert f3["us10y_yield_change"] is None and f3["hynix_previous_close"] is None


def test_detect_samsung_specific_event(tmp_path):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"mock_news_items": {
        "a": {"title": "삼성전자 HBM 공급", "symbols": []},
        "b": {"title": "Other earnings", "symbols": ["005930"]},
        "c": {"title": "Other earnings", "symbols": ["000660"]},
        "d": {"title": "삼성전자 인사", "symbols": []},
        "e": "not-a-mapping",
    }}), encoding="utf-8")
    out = mi.detect_samsung_specific_event(state, day="2026-10-28")
    assert out["samsung_specific_event"] is True and out["matched_headlines"] == ["삼성전자 HBM 공급", "Other earnings"]
    assert out["day"] == "2026-10-28" and out["source"] == "runtime_state_news"
    # list-form news_items, symbol field
    state.write_text(json.dumps({"news_items": [{"headline": "FOUNDRY win", "symbol": "005930"}]}), encoding="utf-8")
    assert mi.detect_samsung_specific_event(state, day="d")["matched_headlines"] == ["FOUNDRY win"]
    # missing/corrupt/non-mapping state -> no event
    assert mi.detect_samsung_specific_event(tmp_path / "none.json", day="d")["samsung_specific_event"] is False
    state.write_text("{bad", encoding="utf-8")
    assert mi.detect_samsung_specific_event(state, day="d")["samsung_specific_event"] is False
    state.write_text("[1]", encoding="utf-8")
    assert mi.detect_samsung_specific_event(state, day="d")["matched_headlines"] == []


# ---------- data_provider macro readers ----------

def _macro(root, day, name, generated_at, kospi):
    d = root / day
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps({"generated_at": generated_at, "index_moves": {"kospi_pct": kospi}}), encoding="utf-8")


def test_load_market_change_pct(tmp_path):
    d = tmp_path / "2026-10-28"
    d.mkdir()
    (d / "latest.json").write_text(json.dumps({"index_moves": {"kospi_pct": "1.25"}}), encoding="utf-8")
    assert dp.load_market_change_pct(day="2026-10-28", macro_root=tmp_path) == 1.25
    assert dp.load_market_change_pct(day="2026-10-29", macro_root=tmp_path) is None
    (d / "latest.json").write_text("[1]", encoding="utf-8")
    assert dp.load_market_change_pct(day="2026-10-28", macro_root=tmp_path) is None
    (d / "latest.json").write_text(json.dumps({"index_moves": "x"}), encoding="utf-8")
    assert dp.load_market_change_pct(day="2026-10-28", macro_root=tmp_path) is None


def test_load_market_timeline_sorts_dedups_and_skips_bad(tmp_path):
    day = "2026-10-28"
    _macro(tmp_path, day, "0900_macro_indicators.json", "2026-10-28T00:00:00Z", 1.0)
    _macro(tmp_path, day, "0905_macro_indicators.json", "2026-10-28T00:05:00+00:00", 2.0)
    _macro(tmp_path, day, "0906_macro_indicators.json", "2026-10-28T00:05:00+00:00", 3.0)  # same ts: later file wins
    _macro(tmp_path, day, "0800_macro_indicators.json", "garbage", 9.0)
    (tmp_path / day / "0700_macro_indicators.json").write_text("{bad", encoding="utf-8")
    (tmp_path / day / "0710_macro_indicators.json").write_text("[1]", encoding="utf-8")
    (tmp_path / day / "ignored.json").write_text("{}", encoding="utf-8")
    tl = dp.load_market_timeline(day=day, macro_root=tmp_path)
    assert [r["kospi_pct"] for r in tl] == [1.0, 3.0]
    assert [r["ts"] for r in tl] == sorted(r["ts"] for r in tl)
    assert tl[1]["source_path"].endswith("0906_macro_indicators.json")
    assert dp.load_market_timeline(day="2026-01-01", macro_root=tmp_path) == []


def test_market_snapshot_at_and_common_as_of():
    tl = [{"ts": 100, "kospi_pct": 1.0, "source_path": "a"}, {"ts": 200, "kospi_pct": 2.0, "source_path": "b"}]
    assert dp.market_snapshot_at(tl, epoch=99) == {"available": False, "reason": "point_in_time_market_snapshot_missing",
                                                   "snapshot_epoch": None, "snapshot_age_sec": None, "kospi_pct": None}
    s = dp.market_snapshot_at(tl, epoch=250)
    assert s["available"] is True and s["snapshot_epoch"] == 200 and s["snapshot_age_sec"] == 50 and s["kospi_pct"] == 2.0 and s["source_path"] == "b"
    assert dp.market_snapshot_at(tl, epoch=100)["snapshot_epoch"] == 100  # inclusive
    assert dp.common_as_of_epoch({}) == 0
    assert dp.common_as_of_epoch({"a": [{"ts": 5}], "b": []}) == 0
    assert dp.common_as_of_epoch({"a": [{"ts": 0}]}) == 0
    c = {"a": [{"ts": 10}, {"ts": 30}], "b": [{"ts": 20}]}
    assert dp.common_as_of_epoch(c) == 20
    assert dp.common_as_of_epoch(c, requested_epoch=15) == 15
    assert dp.common_as_of_epoch(c, requested_epoch=99) == 20
