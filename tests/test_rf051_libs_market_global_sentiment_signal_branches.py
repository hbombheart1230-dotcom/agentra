"""RF-051: compute_global_sentiment_signal branches with every fetcher faked (socket denied)."""
from __future__ import annotations

import socket
import sys
import types

import pytest

from libs.market import global_sentiment as gs

_REAL_EXTENDED = gs._fetch_extended_macro_indicators   # the autouse fixture fakes the module attribute


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    def deny(*_a, **_k):
        raise AssertionError("real network attempted")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.delenv("DRY_RUN", raising=False)
    monkeypatch.setattr(gs, "_is_dry_run", lambda: False)
    monkeypatch.setattr(gs, "_fetch_extended_macro_indicators", lambda *a, **k: {"fake": True})
    monkeypatch.setattr(gs, "_fetch_korea_index_inputs", lambda s, p: None)
    monkeypatch.setattr(gs, "_fetch_inputs", lambda p: None)


def _krx(monkeypatch, func):
    mod = types.ModuleType("libs.read.krx_night_futures_reader")
    mod.fetch_krx_night_futures_packet = func
    monkeypatch.setitem(sys.modules, "libs.read.krx_night_futures_reader", mod)


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_mock_value_valid_clamped_and_invalid_falls_back():
    ok = gs.compute_global_sentiment_signal({"mock_global_sentiment": 5}, {})
    _eq((ok["status"], ok["source"], ok["score"]), ("ok", "mock_global_sentiment", 1.0))
    bad = gs.compute_global_sentiment_signal({"mock_global_sentiment": "abc"}, {})
    _eq((bad["status"], bad["reason"], bad["score"]), ("fallback", "invalid_mock_value", 0.0))


def test_dry_run_is_neutral_fallback_without_fetching(monkeypatch):
    monkeypatch.setattr(gs, "_is_dry_run", lambda: True)

    def boom(*_a, **_k):
        raise AssertionError("must not fetch in dry run")

    monkeypatch.setattr(gs, "_fetch_inputs", boom)
    out = gs.compute_global_sentiment_signal({}, {})
    _eq((out["status"], out["source"], out["reason"], out["score"]), ("fallback", "dry_run_policy", "dry_run_neutral", 0.0))


def test_us_fetch_failed_without_korea_indices_is_unavailable_and_krx_exception_recorded(monkeypatch):
    def krx_fail():
        raise RuntimeError("krx down")

    _krx(monkeypatch, krx_fail)
    out = gs.compute_global_sentiment_signal({}, {})
    _eq((out["status"], out["reason"], out["source"]), ("unavailable", "fetch_failed", "yfinance"))
    krx = out["krx_night_futures"]
    _eq((krx["status"], krx["source"], krx["reason"], krx["trading_action_allowed"]), ("unavailable", "exception", "krx down", False))


def test_us_fetch_failed_but_korea_indices_available_uses_korea_score(monkeypatch):
    _krx(monkeypatch, lambda: {"status": "ok"})
    monkeypatch.setattr(gs, "_fetch_korea_index_inputs", lambda s, p: {
        "source": "fake.kiwoom", "indices": {"KOSPI": {"change_pct": 1.0}, "KOSDAQ": {"change_pct": 1.0}},
        "average_change_pct": 1.0, "breadth": 0.2,
    })
    out = gs.compute_global_sentiment_signal({}, {})
    _eq((out["status"], out["reason"], out["source"]), ("ok", "us_fetch_failed_korea_indices_available", "fake.kiwoom"))
    if not 0 < out["score"] <= 1:
        raise AssertionError(out["score"])
    _eq(out["krx_night_futures"], {"status": "ok"})


def test_korea_bond_provider_exception_is_swallowed_in_extended_indicators(monkeypatch):
    from libs.market import korea_bond_yields as kb

    calls = []

    def broken(policy=None):
        calls.append(1)
        raise RuntimeError("provider bug")

    monkeypatch.setattr(kb, "fetch_korea_bond_yield_overrides", broken)
    out = _REAL_EXTENDED({}, {}, inputs=None, korea_indices=None, krx_night_futures={})
    _eq(calls, [1])                      # provider was consulted and its exception did not escape
    if not isinstance(out, dict):
        raise AssertionError(type(out))


def test_existing_dict_override_is_not_replaced_by_bond_provider(monkeypatch):
    from libs.market import korea_bond_yields as kb

    monkeypatch.setattr(kb, "fetch_korea_bond_yield_overrides", lambda policy=None: {
        "kr_3y_yield": {"status": "ok", "current": 9.9},
        "kr_10y_yield": "not-a-dict",
    })
    policy = {"macro_indicator_overrides": {"kr_3y_yield": {"status": "ok", "current": 1.1}}}
    out = _REAL_EXTENDED({}, policy, inputs=None, korea_indices=None, krx_night_futures={})
    text = repr(out)
    if "1.1" not in text or "9.9" in text:
        raise AssertionError(text)                      # explicit override wins over the provider value
