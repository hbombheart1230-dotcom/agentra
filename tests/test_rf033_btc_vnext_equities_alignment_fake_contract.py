"""RF-033 C3: BTC vnext equities/time_alignment with fake yfinance and a fake XNYS calendar (no network, no disk)."""
from __future__ import annotations

import socket
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

from libs.market.yfinance_support import DataSourceDependencyError
from libs.reporting.baseline_btc_woori_tech.vnext import equities as eq
from libs.reporting.baseline_btc_woori_tech.vnext import time_alignment as ta

UTC = timezone.utc


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)
    ta.session_context.cache_clear()
    yield
    ta.session_context.cache_clear()


# ---------- equities ----------

def test_expected_session_skips_weekend():
    assert eq.expected_session("2026-10-28") == "2026-10-27"   # Wed -> Tue
    assert eq.expected_session("2026-10-26") == "2026-10-23"   # Mon -> Fri
    assert eq.expected_session("2026-10-25") == "2026-10-23"   # Sun -> Fri


def _rows(*pairs):
    return [{"session": s, "close": c} for s, c in pairs]


def test_session_return_observed_and_definition():
    out = eq.session_return(_rows(("2026-10-26", 100.0), ("2026-10-27", 110.0)), "2026-10-28")
    assert out["status"] == "OBSERVED" and out["session"] == "2026-10-27" and out["previous_session"] == "2026-10-26"
    assert out["return_pct"] == pytest.approx(10.0)
    assert "auto_adjust=False" in out["definition"]


def test_session_return_unknown_reasons():
    # newest valid row is not the expected session (holiday / stale)
    out = eq.session_return(_rows(("2026-10-23", 1.0), ("2026-10-26", 2.0)), "2026-10-28")
    assert out == {"status": "UNKNOWN", "reason": "holiday_or_missing_expected_session", "expected_session": "2026-10-27"}
    # fewer than two rows
    assert eq.session_return(_rows(("2026-10-27", 1.0)), "2026-10-28")["reason"] == "holiday_or_missing_expected_session"
    # previous session more than 4 days older
    out = eq.session_return(_rows(("2026-10-20", 1.0), ("2026-10-27", 2.0)), "2026-10-28")
    assert out["reason"] == "invalid_previous_session"
    # non-positive / non-numeric closes and future rows are ignored
    out = eq.session_return(_rows(("2026-10-26", 0.0), ("2026-10-27", "x"), ("2026-10-29", 9.0)), "2026-10-28")
    assert out["status"] == "UNKNOWN"


class _Idx:
    """pandas.Timestamp stand-in: tz-aware datetime with to_pydatetime()."""

    def __init__(self, dt):
        self._dt = dt

    def to_pydatetime(self):
        return self._dt

    def timestamp(self):
        return self._dt.timestamp()


class _Frame:
    def __init__(self, items):
        self.items = items

    def iterrows(self):
        return iter(self.items)


class _Row(dict):
    pass


def _fake_yf(frames, log):
    class _T:
        def __init__(self, s):
            self.s = s

        def history(self, **kw):
            log.append((self.s, kw))
            f = frames[self.s]
            if isinstance(f, Exception):
                raise f
            return f

    return types.SimpleNamespace(Ticker=_T)


def _install_yf(monkeypatch, yf):
    import libs.market.yfinance_support as ys

    monkeypatch.setattr(ys, "require_yfinance", lambda: yf)


def _ny_frame(closes):
    base = datetime(2026, 10, 26, 21, 0, tzinfo=UTC)  # 17:00 NY (EDT/EST safe) -> same NY date
    return _Frame([(_Idx(base + timedelta(days=i)), _Row(Close=c)) for i, c in enumerate(closes)])


def test_fetch_equities_observed_and_per_ticker_failure(monkeypatch):
    log = []
    yf = _fake_yf({"COIN": _ny_frame([100.0, 110.0]), "MSTR": RuntimeError("x")}, log)
    _install_yf(monkeypatch, yf)
    out = eq.fetch_equities("2026-10-28")
    assert out["COIN"]["status"] == "OBSERVED" and out["COIN"]["source"] == "yfinance:COIN:1d"
    assert out["MSTR"] == {"status": "UNKNOWN", "reason": "RuntimeError"}
    assert [t for t, _ in log] == ["COIN", "MSTR"]
    assert log[0][1] == {"period": "1mo", "interval": "1d", "auto_adjust": False, "prepost": False, "timeout": 8}


def test_fetch_equities_missing_dependency_raises(monkeypatch):
    import libs.market.yfinance_support as ys

    def _missing():
        raise DataSourceDependencyError("yfinance")

    monkeypatch.setattr(ys, "require_yfinance", _missing)
    with pytest.raises(DataSourceDependencyError):
        eq.fetch_equities("2026-10-28")


def test_confirmation_matrix():
    def e(a, b):
        return {"COIN": {"status": "OBSERVED", "return_pct": a}, "MSTR": {"status": "OBSERVED", "return_pct": b}}

    assert eq.confirmation(e(6, 7), 3) == "STRONG"
    assert eq.confirmation(e(6, 4.9), 3) == "CONFIRM"
    assert eq.confirmation(e(-1, -2), 3) == "DIVERGENCE"
    assert eq.confirmation(e(1, -2), 3) == "MIXED"
    assert eq.confirmation(e(1, 2), 0) == "UNKNOWN"
    assert eq.confirmation(e(1, 2), None) == "UNKNOWN"
    assert eq.confirmation({"COIN": {"status": "UNKNOWN"}, "MSTR": {"status": "OBSERVED", "return_pct": 1}}, 3) == "UNKNOWN"
    assert eq.confirmation({}, 3) == "UNKNOWN"


# ---------- time_alignment ----------

class _Cal:
    def __init__(self, sessions, closes, prev):
        self.sessions, self.closes, self.prev = sessions, closes, prev

    def is_session(self, d):
        return d in self.sessions

    def previous_session(self, d):
        return _Prev(self.prev)

    def session_close(self, d):
        return _Ts(self.closes[d])


class _Prev(str):
    def date(self):
        return datetime.fromisoformat(str(self)).date()


class _Ts:
    def __init__(self, dt):
        self.dt = dt

    def timestamp(self):
        return self.dt.timestamp()

    def to_pydatetime(self):
        return self.dt


def _install_cal(monkeypatch, cal):
    mod = types.ModuleType("exchange_calendars")
    mod.get_calendar = lambda name: cal
    monkeypatch.setitem(sys.modules, "exchange_calendars", mod)


def _cal_for_tue(monkeypatch):
    closes = {
        "2026-10-27": datetime(2026, 10, 27, 20, 0, tzinfo=UTC),
        "2026-10-26": datetime(2026, 10, 26, 20, 0, tzinfo=UTC),
    }
    _install_cal(monkeypatch, _Cal({"2026-10-27", "2026-10-26"}, closes, "2026-10-26"))
    return closes


def test_session_context_holiday_is_unknown_not_replaced(monkeypatch):
    _install_cal(monkeypatch, _Cal(set(), {}, "x"))
    assert ta.session_context("2026-10-28") == {"status": "UNKNOWN", "reason": "US_MARKET_HOLIDAY", "expected_session": "2026-10-27"}


def test_session_context_available_overnight_and_gap_types(monkeypatch):
    closes = _cal_for_tue(monkeypatch)
    ctx = ta.session_context("2026-10-28")
    assert ctx["status"] == "AVAILABLE" and ctx["session"] == "2026-10-27" and ctx["previous_session"] == "2026-10-26"
    assert ctx["us_close_epoch"] == int(closes["2026-10-27"].timestamp())
    assert ctx["us_previous_close_epoch"] == int(closes["2026-10-26"].timestamp())
    target = ta.epoch("2026-10-28", "08:55")
    assert ctx["age_hours"] == pytest.approx((target - ctx["us_close_epoch"]) / 3600)
    assert ctx["gap_type"] == "OVERNIGHT"
    assert ctx["us_close_kst"].endswith("+09:00")


def test_session_context_weekend_and_extended_closure(monkeypatch):
    # Monday 2026-10-26 -> Friday session; weekday()==0 => WEEKEND
    closes = {"2026-10-23": datetime(2026, 10, 23, 20, 0, tzinfo=UTC)}
    _install_cal(monkeypatch, _Cal({"2026-10-23"}, closes, "2026-10-23"))
    assert ta.session_context("2026-10-26")["gap_type"] == "WEEKEND"
    ta.session_context.cache_clear()
    # Wednesday with a stale (>30h) previous close -> EXTENDED_CLOSURE
    stale = {"2026-10-27": datetime(2026, 10, 26, 0, 0, tzinfo=UTC)}
    _install_cal(monkeypatch, _Cal({"2026-10-27"}, stale, "2026-10-27"))
    assert ta.session_context("2026-10-28")["gap_type"] == "EXTENDED_CLOSURE"


def _equities(session="2026-10-27", prev="2026-10-26"):
    return {t: {"session": session, "previous_session": prev} for t in ("COIN", "MSTR")}


def test_capture_alignment_available_uses_exact_boundary_open(monkeypatch):
    closes = _cal_for_tue(monkeypatch)
    e_prev, e_end = int(closes["2026-10-26"].timestamp()), int(closes["2026-10-27"].timestamp())
    rows = [{"ts": e_prev, "open": 100.0}, {"ts": e_end, "open": 105.0}, {"ts": e_end + 300, "open": 999.0}]
    out = ta.capture_alignment("2026-10-28", _equities(), rows)
    assert out["status"] == "AVAILABLE" and out["reason"] == ""
    assert out["btc_equity_interval_return_pct"] == pytest.approx(5.0)
    assert out["us_close_btc_price"] == 105.0 and out["us_previous_close_btc_price"] == 100.0
    assert out["source"].endswith("exact_boundary_open")


def test_capture_alignment_failure_modes(monkeypatch):
    closes = _cal_for_tue(monkeypatch)
    e_prev, e_end = int(closes["2026-10-26"].timestamp()), int(closes["2026-10-27"].timestamp())
    # missing boundary row -> UNKNOWN with reason
    out = ta.capture_alignment("2026-10-28", _equities(), [{"ts": e_prev, "open": 100.0}])
    assert out["status"] == "UNKNOWN" and out["reason"] == "exact_US_close_BTC_reference_missing"
    # duplicate boundary rows are ambiguous -> None
    dup = [{"ts": e_prev, "open": 1.0}, {"ts": e_end, "open": 2.0}, {"ts": e_end, "open": 3.0}]
    assert ta.capture_alignment("2026-10-28", _equities(), dup)["status"] == "UNKNOWN"
    # non-positive open -> None
    bad = [{"ts": e_prev, "open": 0.0}, {"ts": e_end, "open": 2.0}]
    assert ta.capture_alignment("2026-10-28", _equities(), bad)["status"] == "UNKNOWN"
    # equity interval mismatch
    mm = ta.capture_alignment("2026-10-28", _equities(session="2026-10-23"), [])
    assert mm["status"] == "UNKNOWN" and mm["reason"] == "equity_interval_missing_or_mismatch"
    assert ta.capture_alignment("2026-10-28", {}, [])["reason"] == "equity_interval_missing_or_mismatch"


def test_capture_alignment_calendar_unavailable_and_holiday(monkeypatch):
    mod = types.ModuleType("exchange_calendars")

    def _boom(name):
        raise KeyError(name)

    mod.get_calendar = _boom
    monkeypatch.setitem(sys.modules, "exchange_calendars", mod)
    assert ta.capture_alignment("2026-10-28", {}, []) == {"status": "UNKNOWN", "reason": "calendar_unavailable:KeyError"}
    ta.session_context.cache_clear()
    _install_cal(monkeypatch, _Cal(set(), {}, "x"))
    assert ta.capture_alignment("2026-10-28", {}, [])["reason"] == "US_MARKET_HOLIDAY"


def test_fetch_alignment_uses_5m_history_and_maps_open(monkeypatch):
    closes = _cal_for_tue(monkeypatch)
    e_prev, e_end = closes["2026-10-26"], closes["2026-10-27"]
    frame = _Frame([(_Idx(e_prev), _Row(Open=100.0)), (_Idx(e_end), _Row(Open=110.0)), (_Idx(e_end + timedelta(minutes=5)), _Row())])
    log = []
    _install_yf(monkeypatch, _fake_yf({"BTC-USD": frame}, log))
    out = ta.fetch_alignment("2026-10-28", _equities())
    assert log == [("BTC-USD", {"period": "5d", "interval": "5m", "auto_adjust": False, "timeout": 8})]
    assert out["status"] == "AVAILABLE" and out["btc_equity_interval_return_pct"] == pytest.approx(10.0)


def test_fetch_alignment_missing_dependency_raises(monkeypatch):
    import libs.market.yfinance_support as ys

    def _missing():
        raise DataSourceDependencyError("yfinance")

    monkeypatch.setattr(ys, "require_yfinance", _missing)
    with pytest.raises(DataSourceDependencyError):
        ta.fetch_alignment("2026-10-28", {})


def test_project_alignment():
    out = ta.project_alignment({"us_close_btc_price": 100.0, "k": 1}, 110.0)
    assert out["btc_since_us_close_pct"] == pytest.approx(10.0) and out["k"] == 1
    assert ta.project_alignment(None, 110.0)["btc_since_us_close_pct"] is None
    src = {"us_close_btc_price": 100.0}
    ta.project_alignment(src, 110.0)
    assert "btc_since_us_close_pct" not in src
