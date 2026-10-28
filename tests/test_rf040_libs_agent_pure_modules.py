"""RF-040 libs/agent C2/C3: pure strategist / intent_parser / router contracts.

Pure functions only; no IO, broker or state. Explicit raises keep the checks
live under ``python -O``.
"""
from __future__ import annotations

import pytest

from libs.agent.intent_parser import ParsedIntent, parse_nl
from libs.agent.router import RoutedCall, route
from libs.agent.strategist import Plan, Strategist


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_strategist_prefers_strategist_output_and_normalizes(monkeypatch):
    monkeypatch.setenv("TOP_N_CANDIDATES", "2")
    plan = Strategist().plan(context={
        "thesis": "t",
        "constraints": {"max": 1},
        "strategist_output": {"themes": [" a ", "a", "", "b"], "candidates": ["abc", "ABC", " x ", "y"]},
        "candidates": ["IGNORED"],
    })
    _eq(plan, Plan(thesis="t", constraints={"max": 1}, themes=["a", "b"], candidates=["ABC", "X"]))


def test_strategist_fallback_chain_and_defaults(monkeypatch):
    monkeypatch.delenv("TOP_N_CANDIDATES", raising=False)
    _eq(Strategist().plan(context={}), Plan(thesis="default_thesis", constraints={}, themes=[], candidates=[]))
    p = Strategist().plan(context={"top_themes": ["z"], "watchlist": ["a", "b", "c", "d", "e", "f"]})
    _eq(p.themes, ["z"])
    _eq(p.candidates, ["A", "B", "C", "D", "E"])  # default top-N is 5
    p = Strategist().plan(context={"candidate_symbols": ["q"], "watchlist_symbols": ["w"], "top_n_candidates": "0"})
    _eq(p.candidates, ["Q"])  # top_n floors at 1
    p = Strategist().plan(context={"watchlist_symbols": ["w"], "watchlist": ["v"]})
    _eq(p.candidates, ["W"])


def test_strategist_does_not_mutate_context_constraints():
    ctx = {"constraints": {"k": 1}}
    Strategist().plan(context=ctx).constraints["k"] = 2
    _eq(ctx["constraints"], {"k": 1})


def test_parse_nl_core_actions():
    _eq(parse_nl("005930 현재가"), ParsedIntent(action="QUOTE", symbol="005930"))
    _eq(parse_nl("005930 10주 매수 70000원 지정가"),
        ParsedIntent(action="BUY", symbol="005930", qty=10, price=70000, order_type="limit"))
    _eq(parse_nl("sell 005930 qty 2"),
        ParsedIntent(action="SELL", symbol="005930", qty=2, price=None, order_type="market"))
    _eq(parse_nl("주문조회 005930 1234567 20261028"),
        ParsedIntent(action="STATUS", symbol="005930", ord_no="1234567", ord_dt="20261028", qry_tp="3", mrkt_tp="0"))
    iid = "a" * 32
    _eq(parse_nl(f"승인 {iid}"), ParsedIntent(action="APPROVE", intent_id=iid))
    _eq(parse_nl("approve nothing"), ParsedIntent(action="APPROVE", intent_id=None))


@pytest.mark.parametrize("text", ["", None, "안녕하세요"])
def test_parse_nl_unknown_and_empty(text):
    _eq(parse_nl(text).action, "UNKNOWN")


def test_approve_takes_precedence_over_trade_words():
    _eq(parse_nl("매수 승인").action, "APPROVE")


def test_router_mapping_and_fallbacks():
    _eq(route(ParsedIntent(action="QUOTE", symbol="005930")), RoutedCall("market_quote", {"symbol": "005930"}))
    _eq(route(ParsedIntent(action="BUY", symbol="005930")).kwargs,
        {"side": "buy", "symbol": "005930", "qty": 1, "order_type": "market", "price": None})
    _eq(route(ParsedIntent(action="SELL", symbol="s", qty=3, price=9, order_type="limit")).kwargs,
        {"side": "sell", "symbol": "s", "qty": 3, "order_type": "limit", "price": 9})
    _eq(route(ParsedIntent(action="STATUS")).kwargs,
        {"ord_no": None, "symbol": None, "ord_dt": None, "qry_tp": "3", "mrkt_tp": "0"})
    _eq(route(ParsedIntent(action="APPROVE", intent_id="i")), RoutedCall("approve_intent", {"intent_id": "i"}))
    _eq(route(ParsedIntent(action="UNKNOWN")).tool, "help")


def test_routed_call_and_parsed_intent_are_frozen():
    with pytest.raises(Exception):
        ParsedIntent(action="BUY").action = "SELL"  # type: ignore[misc]
    with pytest.raises(Exception):
        RoutedCall("t", {}).tool = "x"  # type: ignore[misc]
