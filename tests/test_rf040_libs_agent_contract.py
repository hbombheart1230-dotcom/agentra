"""RF-040 libs/agent C2/C3 contract: import surface, executor shadowing, intent mapping.

Pure/mocked only: no broker, supervisor, network or state is touched.
"""
from __future__ import annotations

import importlib
import pathlib

import pytest

import libs.agent as agent_pkg
from libs.agent.executor import AgentExecutor, ExecutorAgent


class _FakeAgent:
    def __init__(self):
        self.calls = []

    def submit_order_intent(self, **kw):
        self.calls.append(kw)
        return {"decision": {"status": "ok"}, "kw": kw}


def _raise_if_not_ok(cond, msg):
    # Explicit raise so the contract holds under ``python -O`` (asserts stripped).
    if not cond:
        raise AssertionError(msg)


def test_public_surface_is_pinned():
    _raise_if_not_ok(
        agent_pkg.__all__
        == ["Commander", "CommandResult", "Strategist", "Plan", "Scanner",
            "Monitor", "Reporter", "AgentExecutor"],
        agent_pkg.__all__,
    )
    for name in agent_pkg.__all__:
        _raise_if_not_ok(getattr(agent_pkg, name) is not None, name)


def test_executor_package_shadows_legacy_module_file():
    mod = importlib.import_module("libs.agent.executor")
    path = pathlib.Path(mod.__file__)
    _raise_if_not_ok(path.name == "__init__.py" and path.parent.name == "executor", str(path))
    _raise_if_not_ok(mod.__all__ == ["ExecutorAgent", "AgentExecutor"], mod.__all__)
    _raise_if_not_ok(agent_pkg.AgentExecutor is AgentExecutor, "re-export identity")
    _raise_if_not_ok(ExecutorAgent.__module__ == "libs.agent.executor.executor_agent", ExecutorAgent.__module__)


def test_standard_intent_shape_maps_to_submit_order_intent():
    fake = _FakeAgent()
    out = AgentExecutor(executor_agent=fake).submit(
        intent={"side": "buy", "symbol": "005930", "qty": "3", "price": "70000"},
        approval_mode="auto",
        execution_enabled=True,
    )
    _raise_if_not_ok(fake.calls == [dict(
        side="buy", symbol="005930", qty=3, order_type="market", price=70000,
        rationale="", approval_mode="auto", execution_enabled=True)], fake.calls)
    _raise_if_not_ok(out["decision"]["status"] == "ok", out)


def test_action_intent_shape_maps_and_defaults_are_safe():
    fake = _FakeAgent()
    AgentExecutor(executor_agent=fake).submit(
        intent={"action": "sell", "symbol": "AAPL", "qty": 1, "order_type": "limit", "price": 5, "rationale": "r"},
    )
    call = fake.calls[0]
    _raise_if_not_ok(call["side"] == "sell" and call["order_type"] == "limit" and call["price"] == 5, call)
    # Safety defaults: manual approval, execution disabled.
    _raise_if_not_ok(call["approval_mode"] == "manual" and call["execution_enabled"] is False, call)


@pytest.mark.parametrize("intent", [
    {},
    {"action": "HOLD", "symbol": "X", "qty": 1},
    {"action": "BUY", "symbol": "X"},
    {"side": "buy", "symbol": "X"},
])
def test_unsupported_intent_is_rejected_without_calling_agent(intent):
    fake = _FakeAgent()
    out = AgentExecutor(executor_agent=fake).submit(intent=intent)
    _raise_if_not_ok(fake.calls == [], fake.calls)
    _raise_if_not_ok(out == {"decision": {"status": "rejected", "reason": "Unsupported intent shape", "intent": intent}}, out)


def test_non_numeric_qty_raises_and_does_not_call_agent():
    fake = _FakeAgent()
    with pytest.raises(ValueError):
        AgentExecutor(executor_agent=fake).submit(intent={"side": "buy", "symbol": "X", "qty": "abc"})
    _raise_if_not_ok(fake.calls == [], fake.calls)


def test_legacy_monitor_update_is_noop():
    from libs.agent import Monitor
    _raise_if_not_ok(Monitor().update(intents=[], decisions=[], executions=[], context={}) is None, "noop")
