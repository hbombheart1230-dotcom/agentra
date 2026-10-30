"""P15 RF-035 (23h): daily_report_generator._broker_closed_symbols_from_alignment moved to daily_report_generator_trade_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import daily_report_generator as m
from libs.reporting import daily_report_generator_trade_projection as owner


def _both(x):
    return m._broker_closed_symbols_from_alignment(x), owner._broker_closed_symbols_from_alignment(x, facade=m)


def test_none_and_non_dict():
    assert _both(None) == (set(), set())
    assert _both([1]) == (set(), set())
    assert _both({}) == (set(), set())
    assert _both({"account_snapshot": "x"}) == (set(), set())


def test_symbols_and_diary_rows(monkeypatch):
    monkeypatch.setattr(m, "normalize_symbol", lambda s, allow_test_symbols=False: str(s or "").upper())
    payload = {"account_snapshot": {"day_trade_closed_symbols": ["aaa", "", None], "day_trade_diary_rows": [
        {"symbol": "bbb", "closed_by_day_trade_diary": True}, {"symbol": "ccc"}, "x", {"symbol": "ddd", "closed_by_day_trade_diary": False}, {"symbol": "", "closed_by_day_trade_diary": True}]}}
    snap = copy.deepcopy(payload)
    assert _both(payload) == ({"AAA", "BBB"},) * 2 and payload == snap


def test_facade_seam_called_with_allow_test_symbols(monkeypatch):
    calls = []
    monkeypatch.setattr(m, "normalize_symbol", lambda s, allow_test_symbols=False: (calls.append((s, allow_test_symbols)), "X")[1])
    payload = {"account_snapshot": {"day_trade_closed_symbols": ["a"], "day_trade_diary_rows": [{"symbol": "b", "closed_by_day_trade_diary": True}]}}
    assert _both(payload) == ({"X"},) * 2
    assert calls[:3] == [("a", True), ("a", True), ("b", True)] and len(calls) == 6


def test_real_normalize_symbol_parity():
    payload = {"account_snapshot": {"day_trade_closed_symbols": ["005930", "bad symbol"], "day_trade_diary_rows": [{"symbol": "000660", "closed_by_day_trade_diary": True}]}}
    a, b = _both(payload)
    assert a == b
