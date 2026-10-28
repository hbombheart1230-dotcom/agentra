"""RF-031 trade_report_ai: hard-timeout router wrapper, env flag and formatting helpers (fake router, no LLM, no network)."""
from __future__ import annotations

import threading

import pytest

from libs.reporting import trade_report_ai as t


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


class _Router:
    def __init__(self, value="ok", exc=None, delay=0.0):
        self.value, self.exc, self.delay, self.calls = value, exc, delay, []
        self.gate = threading.Event()

    def chat(self, role, messages, policy=None):
        self.calls.append((role, messages, policy))
        if self.delay:
            self.gate.wait(self.delay)
        if self.exc:
            raise self.exc
        return self.value


def test_no_timeout_calls_the_router_directly_and_passes_the_value_through():
    router = _Router(value="direct")
    for timeout in (None, "", 0):
        _eq(t._router_chat_with_hard_timeout(router, "role", [{"k": 1}], policy={"p": 1}, hard_timeout_sec=timeout), "direct")
    _eq(router.calls[0], ("role", [{"k": 1}], {"p": 1}))


def test_timeout_wrapper_returns_string_value_and_empty_for_none():
    _eq(t._router_chat_with_hard_timeout(_Router(value="text"), "r", [], hard_timeout_sec=5), "text")
    _eq(t._router_chat_with_hard_timeout(_Router(value=None), "r", [], hard_timeout_sec=5), "")
    _eq(t._router_chat_with_hard_timeout(_Router(value=123), "r", [], hard_timeout_sec=5), "123")


def test_timeout_wrapper_reraises_the_router_exception_unchanged():
    boom = ValueError("router failed")
    with pytest.raises(ValueError) as exc:
        t._router_chat_with_hard_timeout(_Router(exc=boom), "r", [], hard_timeout_sec=5)
    if exc.value is not boom:
        raise AssertionError("the original exception object must be re-raised")


def test_hard_timeout_raises_timeouterror_and_floors_the_budget_at_a_tenth_of_a_second():
    router = _Router(delay=5.0)
    try:
        with pytest.raises(TimeoutError, match=r"hard timeout after 0\.1s"):
            t._router_chat_with_hard_timeout(router, "r", [], hard_timeout_sec=0.001)
    finally:
        router.gate.set()                                                   # release the daemon worker thread


@pytest.mark.parametrize("raw,default,expected", [(None, True, True), (None, False, False), ("1", False, True), ("TRUE", False, True),
                                                  (" yes ", False, True), ("on", False, True), ("off", True, False), ("", True, False), ("2", True, False)])
def test_env_bool(monkeypatch, raw, default, expected):
    monkeypatch.delenv("RF031_FLAG", raising=False)
    if raw is not None:
        monkeypatch.setenv("RF031_FLAG", raw)
    _eq(t._env_bool("RF031_FLAG", default=default), expected)


def test_number_formatting_helpers():
    # pct_points takes already-scaled points (unlike markdown_clean._fmt_signed_pct, which takes a ratio)
    _eq([t._format_pct_points(v) for v in (1.234, -0.5, None, "x", "2")], ["+1.23%", "-0.50%", "-", "-", "+2.00%"])
    _eq([t._fmt_num(v) for v in (1.23456, "2", None, "x")], ["1.235", "2.000", "-", "-"])
    _eq(t._fmt_num(1.23456, digits=1), "1.2")


def test_entry_gate_score_relation_uses_a_1e6_tolerance():
    _eq(t._entry_gate_score_relation(1.0, 1.0), "동일했습니다")
    _eq(t._entry_gate_score_relation(1.0000001, 1.0), "동일했습니다")
    _eq(t._entry_gate_score_relation(2, 1), "상회했습니다")
    _eq(t._entry_gate_score_relation(1, 2), "하회했습니다")
