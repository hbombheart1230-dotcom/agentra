"""RF-051 libs/market/global_sentiment: input-fetch helpers, offline.

Covers what the existing global_sentiment tests leave unexercised (measured with
coverage: lines 115-169, 178-198, 449-496): Korea-index normalization/selection,
the yfinance close-pair reader, the ``_fetch_inputs`` assembly and the macro
indicator log writer. ``yfinance`` is a recording fake in ``sys.modules`` (no
network); the Kiwoom reader class is replaced by a fake; log output goes to
tmp_path. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import sys
import types

import pandas as pd
import pytest

from libs.market import global_sentiment as gs
from libs.market import yfinance_support as ys


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _idx(**rows):
    return {"indices": rows}


def test_normalize_packet_filters_names_and_computes_breadth_and_average():
    raw = _idx(KOSPI={"change_pct": 1.0, "rising": 600, "falling": 200, "unchanged": 200},
               KOSDAQ={"change_pct": "-0.5", "rising": "100", "falling": 300},
               NASDAQ={"change_pct": 9}, KOSPI200={})
    out = gs._normalize_korea_index_packet(raw)
    _eq(sorted(out["indices"]), ["KOSDAQ", "KOSPI"])        # unknown names and empty rows dropped
    _eq((out["rising"], out["falling"], out["unchanged"]), (700, 500, 200))
    _eq(out["breadth"], (700 - 500) / 1400)
    _eq(out["average_change_pct"], (1.0 - 0.5) / 2)
    _eq((out["source"], out["status"]), ("provided", "ok"))
    kept = gs._normalize_korea_index_packet({**raw, "source": "kiwoom", "status": "stale"})
    _eq((kept["source"], kept["status"]), ("kiwoom", "stale"))   # setdefault never overrides
    # no breadth counts -> falls back to the packet's own breadth / average
    fb = gs._normalize_korea_index_packet({"indices": {"KOSPI": {}}, "breadth": 0.3})
    _eq(fb, None)
    fb2 = gs._normalize_korea_index_packet({"indices": {"KOSPI": {"x": 1}}, "breadth": 0.3, "average_change_pct": 7})
    _eq((fb2["breadth"], fb2["average_change_pct"]), (0.3, 7))
    for bad in (None, {}, {"indices": {}}, "x", {"indices": {"NASDAQ": {"a": 1}}}):
        _eq(gs._normalize_korea_index_packet(bad), None)


def test_compute_korea_raw_weights_and_defaults():
    _eq(gs._compute_korea_raw(None, w_kospi=0.5, w_kosdaq=0.5), 0.0)
    _eq(gs._compute_korea_raw(_idx(KOSPI={"change_pct": 2.0}, KOSDAQ={"change_pct": -1.0}), w_kospi=1.0, w_kosdaq=2.0), 0.02 - 0.02)
    got = gs._compute_korea_raw(_idx(KOSPI={"change_pct": 2.0}, KOSDAQ={"change_pct": "bad"}), w_kospi=0.5, w_kosdaq=9.0)
    _eq(got, 0.5 * 0.02)


def test_pct_change_and_close_pair_edge_cases():
    _eq(gs._pct_change(None), None)
    _eq(gs._pct_change((0.0, 5.0)), None)
    _eq(gs._pct_change((100.0, 110.0)), pytest.approx(0.1))
    _eq(gs._as_float("x", 3.0), 3.0)


def _fake_yf(monkeypatch, frames):
    fake = types.ModuleType("yfinance")
    calls = []

    class Ticker:
        def __init__(self, symbol):
            self.symbol = symbol
            calls.append(symbol)

        def history(self, period, interval):
            f = frames[self.symbol]
            if isinstance(f, Exception):
                raise f
            return f

    fake.Ticker = Ticker
    monkeypatch.setitem(sys.modules, "yfinance", fake)
    return calls


def test_last2_closes_reads_last_two_non_nan_values(monkeypatch):
    calls = _fake_yf(monkeypatch, {
        "A": pd.DataFrame({"Close": [1.0, float("nan"), 2.0, 3.5]}),
        "ONE": pd.DataFrame({"Close": [1.0]}),
        "EMPTY": pd.DataFrame({"Close": []}),
        "BOOM": RuntimeError("net"),
        "NONE": None,
    })
    _eq(gs._fetch_last2_closes_yfinance("A"), (2.0, 3.5))
    for sym in ("ONE", "EMPTY", "BOOM", "NONE"):
        _eq(gs._fetch_last2_closes_yfinance(sym), None)       # every failure is a quiet None
    _eq(calls, ["A", "ONE", "EMPTY", "BOOM", "NONE"])


def test_last2_closes_returns_none_and_logs_when_yfinance_missing(monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "yfinance", None)
    monkeypatch.setattr(ys, "_REPORTED", set())
    import logging
    with caplog.at_level(logging.ERROR, logger=ys.__name__):
        _eq(gs._fetch_last2_closes_yfinance("A"), None)
    if not any("DATA_SOURCE_DEPENDENCY_MISSING component=global_sentiment" in r.getMessage() for r in caplog.records):
        raise AssertionError("missing dependency must be logged explicitly")


def test_fetch_inputs_requires_core_series_and_defaults_vix(monkeypatch):
    pairs = {"^GSPC": (100.0, 101.0), "^IXIC": (200.0, 198.0), "^DJI": (300.0, 303.0), "^VIX": (20.0, 22.0),
             "DX-Y.NYB": (100.0, 99.0), "^TNX": (45.0, 46.0)}
    seen = []

    def fake(ticker):
        seen.append(ticker)
        return pairs.get(ticker)

    monkeypatch.setattr(gs, "_fetch_last2_closes_yfinance", fake)
    inp = gs._fetch_inputs({})
    _eq(seen, ["^GSPC", "^IXIC", "^DJI", "^VIX", "DX-Y.NYB", "^TNX"])
    _eq((round(inp.sp500_ret, 6), round(inp.nasdaq_ret, 6), round(inp.vix_ret, 6), inp.vix_level, round(inp.tnx_delta, 6)),
        (0.01, -0.01, 0.1, 22.0, 0.1))
    # VIX is optional (defaults 0/0) ...
    pairs["^VIX"] = None
    v = gs._fetch_inputs({})
    _eq((v.vix_ret, v.vix_level), (0.0, 0.0))
    # ... but any missing core series makes the whole input unavailable
    for core in ("^GSPC", "^IXIC", "^DJI", "DX-Y.NYB", "^TNX"):
        saved = pairs[core]
        pairs[core] = None
        _eq(gs._fetch_inputs({}), None)
        pairs[core] = saved
    # policy tickers override the defaults
    seen.clear()
    gs._fetch_inputs({"sentiment_ticker_sp500": "SPY", "sentiment_ticker_vix": "VXX"})
    _eq((seen[0], seen[3]), ("SPY", "VXX"))


class _FakeReader:
    packet = None
    boom = False

    @classmethod
    def from_env(cls):
        if cls.boom:
            raise RuntimeError("no credentials")
        return cls()

    def get_index_packet(self):
        return _FakeReader.packet


def _patch_reader(monkeypatch):
    mod = types.ModuleType("libs.read.kiwoom_market_index_reader")
    mod.KiwoomMarketIndexReader = _FakeReader
    monkeypatch.setitem(sys.modules, "libs.read.kiwoom_market_index_reader", mod)
    _FakeReader.packet, _FakeReader.boom = None, False


def test_korea_index_inputs_state_keys_win_in_order_and_disable_switches(monkeypatch):
    _patch_reader(monkeypatch)
    monkeypatch.delenv("KOREA_INDEX_CONTEXT_ENABLED", raising=False)
    _FakeReader.packet = _idx(KOSPI={"change_pct": 9.0})
    state = {"korea_indices": _idx(KOSPI={"change_pct": 1.0}), "mock_korea_indices": _idx(KOSPI={"change_pct": 2.0})}
    _eq(gs._fetch_korea_index_inputs(state, {})["indices"]["KOSPI"]["change_pct"], 2.0)    # mock_korea_indices first
    _eq(gs._fetch_korea_index_inputs({"korea_indices": _idx(KOSPI={"change_pct": 1.0})}, {})["indices"]["KOSPI"]["change_pct"], 1.0)
    _eq(gs._fetch_korea_index_inputs({"korea_index_context": {"indices": {}}}, {})["indices"]["KOSPI"]["change_pct"], 9.0)   # empty packet skipped -> reader
    for flag in ("0", "false", "No", "n", "OFF"):
        _eq(gs._fetch_korea_index_inputs({}, {"use_korea_indices": flag}), None)
    monkeypatch.setenv("KOREA_INDEX_CONTEXT_ENABLED", "off")
    _eq(gs._fetch_korea_index_inputs({}, {}), None)
    _eq(gs._fetch_korea_index_inputs({}, {"use_korea_indices": "true"})["indices"]["KOSPI"]["change_pct"], 9.0)  # policy beats env


def test_korea_index_inputs_reader_failures_are_none(monkeypatch):
    _patch_reader(monkeypatch)
    monkeypatch.delenv("KOREA_INDEX_CONTEXT_ENABLED", raising=False)
    _FakeReader.boom = True
    _eq(gs._fetch_korea_index_inputs({}, {}), None)
    _FakeReader.boom = False
    _FakeReader.packet = {"indices": {}}
    _eq(gs._fetch_korea_index_inputs({}, {}), None)


def test_macro_indicator_log_writes_latest_and_stamped_file_only_outside_pytest(tmp_path, monkeypatch):
    payload = {"schema_version": "macro_indicators.v1", "k": "한글"}
    root = tmp_path / "logs"
    # inside pytest (PYTEST_CURRENT_TEST set) the writer is a no-op
    gs._write_macro_indicator_log(payload, policy={"macro_indicator_log_root": str(root)})
    _eq(root.exists(), False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    for off in ("0", "false", "no", "n", "off"):
        gs._write_macro_indicator_log(payload, policy={"macro_indicator_log_enabled": off, "macro_indicator_log_root": str(root)})
    _eq(root.exists(), False)
    monkeypatch.setenv("MACRO_INDICATOR_LOG_ENABLED", "false")
    gs._write_macro_indicator_log(payload, policy={"macro_indicator_log_root": str(root)})
    _eq(root.exists(), False)
    gs._write_macro_indicator_log(payload, policy={"macro_indicator_log_enabled": "true", "macro_indicator_log_root": str(root)})   # policy beats env
    days = list(root.iterdir())
    _eq(len(days), 1)
    names = sorted(p.name for p in days[0].iterdir())
    _eq(len(names), 2)
    _eq("latest.json" in names, True)
    stamped = [n for n in names if n != "latest.json"][0]
    if not stamped.endswith("_macro_indicators.json") or len(stamped) != len("HHMMSS_macro_indicators.json"):
        raise AssertionError(stamped)
    body = (days[0] / "latest.json").read_text(encoding="utf-8")
    _eq(json.loads(body), payload)
    if "한글" not in body:
        raise AssertionError("ensure_ascii=False expected")
    # unwritable root is swallowed silently
    blocker = tmp_path / "file_not_dir"
    blocker.write_text("x", encoding="utf-8")
    gs._write_macro_indicator_log(payload, policy={"macro_indicator_log_enabled": "true", "macro_indicator_log_root": str(blocker / "sub")})
