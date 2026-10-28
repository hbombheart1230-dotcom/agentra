"""RF-061 libs/tools C2/C3: package surface, env helpers and tool_schema mapping.

Read-only/mocked: ``tool_facade.ToolFacade`` order paths (Step5C) are NOT
exercised; ``tool_schema.ToolFacade`` is built via ``__new__`` with a fake
runner so no skill, supervisor, broker or file is touched. Explicit raises keep
the checks live under ``python -O``.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

import libs.tools as tools_pkg
from libs.tools import tool_facade as tf
from libs.tools import tool_schema as ts


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_package_exports_tool_facade_not_tool_schema_class():
    _eq(tools_pkg.__all__, ["ToolFacade"])
    if tools_pkg.ToolFacade is not tf.ToolFacade:
        raise AssertionError("package must re-export tool_facade.ToolFacade")
    if tools_pkg.ToolFacade is ts.ToolFacade:
        raise AssertionError("tool_schema.ToolFacade must stay a distinct class")


@pytest.mark.parametrize("val,expected", [
    (None, "real"), ("", "real"), (" MOCK ", "mock"), ("Real", "real"),
])
def test_mode_default_and_normalization(monkeypatch, val, expected):
    if val is None:
        monkeypatch.delenv("KIWOOM_MODE", raising=False)
    else:
        monkeypatch.setenv("KIWOOM_MODE", val)
    _eq(tf._mode(), expected)


@pytest.mark.parametrize("val,expected", [
    (None, False), ("", False), ("false", False), ("0", False), ("no", False),
    ("1", True), ("TRUE", True), (" yes ", True), ("y", True), ("on", True),
])
def test_execution_enabled_is_off_unless_explicitly_truthy(monkeypatch, val, expected):
    if val is None:
        monkeypatch.delenv("EXECUTION_ENABLED", raising=False)
    else:
        monkeypatch.setenv("EXECUTION_ENABLED", val)
    _eq(tf._execution_enabled(), expected)


@pytest.mark.parametrize("approval,legacy,expected", [
    (None, None, "manual"),
    ("auto", None, "auto"),
    (" MANUAL ", "true", "manual"),   # APPROVAL_MODE wins over AUTO_APPROVE
    ("bogus", "auto", "auto"),        # invalid APPROVAL_MODE falls through
    (None, "manual", "manual"),
    (None, "on", "auto"),
    (None, "false", "manual"),
    (None, "garbage", "manual"),
])
def test_approval_mode_priority(monkeypatch, approval, legacy, expected):
    for k, v in (("APPROVAL_MODE", approval), ("AUTO_APPROVE", legacy)):
        if v is None:
            monkeypatch.delenv(k, raising=False)
        else:
            monkeypatch.setenv(k, v)
    _eq(tf._approval_mode(), expected)


def test_unwrap_intent_shapes():
    inner = {"intent_id": "i"}
    if tf._unwrap_intent({"ts": 1, "intent": inner}) is not inner:
        raise AssertionError("wrapped record must unwrap to inner dict")
    raw = {"symbol": "X"}
    if tf._unwrap_intent(raw) is not raw:
        raise AssertionError("raw dict passes through")
    _eq(tf._unwrap_intent({"intent": "notdict"}), {"intent": "notdict"})
    for bad in (None, [], "s", 3):
        _eq(tf._unwrap_intent(bad), None)


def test_new_run_id_is_32_hex_and_unique():
    a, b = tf._new_run_id(), tf._new_run_id()
    _eq(len(a), 32)
    int(a, 16)
    if a == b:
        raise AssertionError("run ids must be unique")


@dataclass
class _Out:
    ok: bool


class _Runner:
    def __init__(self, out):
        self.out, self.calls = out, []

    def run(self, *, run_id, skill, args):
        self.calls.append((run_id, skill, args))
        return self.out


def _schema_facade(out):
    f = ts.ToolFacade.__new__(ts.ToolFacade)
    f.runner = _Runner(out)
    return f


def test_schema_dump_dataclass_vs_passthrough():
    _eq(ts._dump(_Out(True)), {"ok": True})
    _eq(ts._dump({"a": 1}), {"a": 1})
    _eq(ts._dump(None), None)


def test_schema_market_quote_and_status_mapping():
    f = _schema_facade(_Out(True))
    q = f.market_quote(symbol="005930", run_id="r")
    _eq(q, {"run_id": "r", "result": {"ok": True}})
    s = f.order_status(ord_no="1", symbol="S", ord_dt="20261028", run_id="r2")
    _eq(s["run_id"], "r2")
    _eq(f.runner.calls, [
        ("r", "market.quote", {"symbol": "005930"}),
        ("r2", "order.status", {"ord_no": "1", "symbol": "S", "ord_dt": "20261028", "qry_tp": "3"}),
    ])


def test_schema_order_execute_market_vs_limit_args_and_intent_id():
    f = _schema_facade(_Out(True))
    f.order_execute(intent={"action": "sell", "symbol": "S", "qty": "2", "order_type": " MKT ", "price": 9, "intent_id": "iid"}, run_id="r")
    f.order_execute(intent={"symbol": "S", "qty": None, "order_type": "limit", "price": 7}, run_id="r")
    (_, skill1, a1), (_, skill2, a2) = f.runner.calls
    _eq(skill1, "order.place")
    _eq(a1, {"side": "sell", "symbol": "S", "qty": 2, "price": "", "trde_tp": "3", "order_type": "mkt", "intent_id": "iid"})
    _eq(a2, {"side": "buy", "symbol": "S", "qty": 0, "price": 7, "trde_tp": "0", "order_type": "limit", "intent_id": ""})


def test_schema_order_execute_non_numeric_qty_raises_before_runner():
    f = _schema_facade(_Out(True))
    with pytest.raises(ValueError):
        f.order_execute(intent={"symbol": "S", "qty": "abc"})
    _eq(f.runner.calls, [])


class _FakeSupervisor:
    def __init__(self):
        self.calls = []

    def create_intent(self, intent):
        self.calls.append(intent)
        return _Out(True)


def test_schema_order_place_intent_maps_side_and_forwards_to_a_fake_supervisor_only():
    # tool_schema.ToolFacade is dormant; here the supervisor is a fake, so no TwoPhaseSupervisor/ApprovalService/broker
    # path (Step5C SAFETY_HOLD) is constructed or executed.
    f = _schema_facade(_Out(True))
    f.supervisor = _FakeSupervisor()
    out = f.order_place_intent(side="BUY", symbol="005930", qty=3, price=70000)
    _eq(out, {"decision": {"ok": True}})
    f.order_place_intent(side="anything-else", symbol="X", qty=1, order_type="limit")
    _eq(f.supervisor.calls, [
        {"action": "BUY", "symbol": "005930", "qty": 3, "order_type": "market", "price": 70000},
        {"action": "SELL", "symbol": "X", "qty": 1, "order_type": "limit", "price": None},     # any non-"buy" side becomes SELL
    ])
    _eq(f.runner.calls, [])    # the skill runner is never touched by intent creation
