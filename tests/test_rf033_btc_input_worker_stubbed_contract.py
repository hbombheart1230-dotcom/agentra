"""RF-033 C3: BTC InputWorker.tick / start_input_worker with capture, providers and publisher stubbed (no network, no repo-relative reads)."""
from __future__ import annotations

import socket
from datetime import datetime

import pytest

from libs.reporting.baseline_btc_woori_tech import input_worker as iw
from libs.reporting.baseline_btc_woori_tech.vnext.contract import KST, epoch

DAY = "2026-10-28"
T0850, T0900, T0912 = epoch(DAY, "08:50"), epoch(DAY, "09:00"), epoch(DAY, "09:12")


@pytest.fixture(autouse=True)
def _deny(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)


@pytest.fixture
def st(monkeypatch):
    s = {"capture": {"btc_0855_capture_status": "CAPTURED"}, "rows": {"research_context": {"btc_usd_daily": [1], "woori_daily": [2]}}, "rows_calls": 0, "candle_calls": [], "published": [], "rows_exc": None}

    def merge(payload, *, day, root=None):
        assert day == DAY
        return dict(s["capture"])

    def rows(*, day, include_research_context=True):
        s["rows_calls"] += 1
        if s["rows_exc"]:
            raise s["rows_exc"]
        return s["rows"]

    def candles(*, day, state_path, allow_fresh_fetch):
        s["candle_calls"].append((day, state_path, allow_fresh_fetch))
        return [{"ts": T0900, "close": 1.0}]

    def publish(**kw):
        s["published"].append(kw)
        return {"ok": True}

    monkeypatch.setattr(iw, "merge_capture_into_signal_payload", merge)
    monkeypatch.setattr(iw, "load_btc_signal_rows", rows)
    monkeypatch.setattr(iw, "load_woori_candles", candles)
    monkeypatch.setattr(iw, "publish_input", publish)
    return s


def worker():
    return iw.InputWorker(DAY, "reports", "state.json")


def test_tick_publishes_signals_with_research_and_candles_after_open_when_captured(st):
    w = worker()
    out = w.tick(T0900)
    assert out == {"ok": True}
    kw = st["published"][0]
    assert kw["day"] == DAY and kw["reports_root"] == "reports" and kw["now_epoch"] == T0900 and kw["candles"] == [{"ts": T0900, "close": 1.0}]
    assert kw["signals"]["research_context"] == {"btc_usd_daily": [1], "woori_daily": [2]} and st["candle_calls"] == [(DAY, "state.json", True)]


def test_candles_not_loaded_before_0900_or_without_captured_status(st):
    worker().tick(T0900 - 1)
    assert st["candle_calls"] == [] and st["published"][0]["candles"] == []
    st["capture"] = {"btc_0855_capture_status": "MISSED"}
    worker().tick(T0900)
    assert st["candle_calls"] == [] and st["published"][1]["candles"] == []
    st["capture"] = {}
    worker().tick(T0900 + 100)
    assert st["candle_calls"] == []


def test_research_is_fetched_once_only_when_both_series_present(st):
    w = worker()
    w.tick(T0850); w.tick(T0850 + 15); w.tick(T0850 + 30)
    assert st["rows_calls"] == 1                                               # cached after a complete fetch
    st["rows"] = {"research_context": {"btc_usd_daily": [1], "woori_daily": []}}
    w2 = worker()
    w2.tick(T0850); w2.tick(T0850 + 15)
    assert st["rows_calls"] == 3 and w2.research is None                       # incomplete -> retried on every tick
    assert st["published"][-1]["signals"]["research_context"] == {}


def test_research_failure_is_swallowed_and_retried(st):
    st["rows_exc"] = RuntimeError("yf down")
    w = worker()
    w.tick(T0850); w.tick(T0850 + 15)
    assert st["rows_calls"] == 2 and w.research is None and len(st["published"]) == 2
    st["rows"] = {}
    st["rows_exc"] = None
    worker().tick(T0850)
    assert st["published"][-1]["signals"]["research_context"] == {}


def test_tick_propagates_publisher_failure(st, monkeypatch):
    monkeypatch.setattr(iw, "publish_input", lambda **kw: (_ for _ in ()).throw(ValueError("bad")))
    with pytest.raises(ValueError):
        worker().tick(T0850)


# ---------- loop ----------

class FakeClock:
    def __init__(self, epochs):
        self.epochs = list(epochs)

    def now(self, tz=None):
        return datetime.fromtimestamp(self.epochs.pop(0) if len(self.epochs) > 1 else self.epochs[0], tz or KST)


class _DT:
    clock: FakeClock

    @classmethod
    def now(cls, tz=None):
        return cls.clock.now(tz)


class SyncThread:
    def __init__(self, target, name, daemon):
        self.target, self.name, self.daemon = target, name, daemon

    def start(self):
        self.target()


def run_loop(monkeypatch, epochs, tick):
    _DT.clock = FakeClock(epochs)
    monkeypatch.setattr(iw, "datetime", _DT)
    monkeypatch.setattr(iw.threading, "Thread", SyncThread)
    waits = []

    class Ev:
        def __init__(self):
            self.n = 0

        def is_set(self):
            return False

        def wait(self, sec):
            waits.append(sec)
            self.n += 1
            if self.n > 5:
                raise RuntimeError("loop did not terminate")

        def set(self):
            pass

    monkeypatch.setattr(iw.threading, "Event", Ev)
    monkeypatch.setattr(iw.InputWorker, "tick", lambda self, now: tick(now))
    iw.start_input_worker(day=DAY, reports_root="r", state_path="s")
    return waits


def test_loop_skips_before_0850_ticks_inside_window_and_exits_after_0912(st, monkeypatch):
    ticks = []
    waits = run_loop(monkeypatch, [T0850 - 5, T0850, T0850 + 15, T0912, T0912 + 1], ticks.append)
    assert ticks == [T0850, T0850 + 15, T0912] and waits == [15, 15, 15, 15]          # 09:12:00 itself still ticks; +1s returns


def test_loop_exits_immediately_on_other_day(st, monkeypatch):
    ticks = []
    waits = run_loop(monkeypatch, [T0850 + 86400], ticks.append)
    assert ticks == [] and waits == []


def test_loop_survives_tick_errors_and_logs_exception_type(st, monkeypatch, capsys):
    def boom(now):
        raise KeyError("x")

    waits = run_loop(monkeypatch, [T0850, T0850 + 15, T0912 + 1], boom)
    assert capsys.readouterr().out.count("q12_input_delivery_error=KeyError") == 2 and waits == [15, 15]


def test_loop_exits_immediately_when_clock_is_on_a_previous_day_even_inside_the_time_window(st, monkeypatch):
    ticks = []
    waits = run_loop(monkeypatch, [T0850 - 86400 + 60], ticks.append)               # yesterday 08:51 KST
    assert ticks == [] and waits == []
