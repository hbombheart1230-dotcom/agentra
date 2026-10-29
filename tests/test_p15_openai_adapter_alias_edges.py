"""P15 C02-1 (FAST-3): OpenAI chat response adapter decision/signal alias shapes. Fake _post_json only, no network."""
from __future__ import annotations

import copy
import json
import socket

import pytest

import libs.ai.providers.openai_provider as prov
from libs.ai.providers.openai_provider import OpenAIStrategist, StrategyInput

ENDPOINT = "https://example.invalid/v1/chat/completions"


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    monkeypatch.setattr(OpenAIStrategist, "_CB_STATE", {})

    def deny(*a, **k):
        raise AssertionError("real network/socket use")

    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def _decide(monkeypatch, content, *, calls=None):
    def post(url, headers, payload, timeout=15.0):
        if calls is not None:
            calls.append(payload)
        return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}

    monkeypatch.setattr(prov, "_post_json", post)
    x = StrategyInput(symbol="005930", market_snapshot={"price": 100}, portfolio_snapshot={"cash": 1}, risk_context={})
    snap = copy.deepcopy(x)
    d = OpenAIStrategist(api_key="k", endpoint=ENDPOINT, model="vendor/m", retry_max=0, retry_backoff_sec=0.0).decide(x)
    assert x == snap                                                         # input unchanged
    return d


@pytest.mark.parametrize("obj,rationale", [
    ({"decision": "NOOP", "reason": "risk_limit"}, "risk_limit"),
    ({"signal": "NOOP", "reason": "missing_data"}, "missing_data"),
])
def test_decision_and_signal_alias_noop(monkeypatch, obj, rationale):
    calls = []
    d = _decide(monkeypatch, json.dumps(obj), calls=calls)
    assert d.intent["action"] == "NOOP" and d.intent["qty"] == 0 and d.intent["price"] is None
    assert d.rationale == rationale
    assert d.meta["attempts"] == 1 and "error" not in d.meta and "adapter_fallback_reason" not in d.meta
    assert d.meta["endpoint_type"] == "chat_completions" and d.meta["model"] and len(calls) == 1


def test_signal_alias_valid_buy(monkeypatch):
    d = _decide(monkeypatch, json.dumps({"signal": "BUY", "symbol": "005930", "qty": 1, "price": 100, "order_type": "limit", "reason": "momentum"}))
    assert (d.intent["action"], d.intent["symbol"], d.intent["qty"], d.intent["price"], d.intent["order_type"]) == ("BUY", "005930", 1, 100.0, "limit")
    assert d.rationale == "momentum" and d.meta["attempts"] == 1 and "error" not in d.meta


def test_decision_alias_valid_sell_with_nested_rationale(monkeypatch):
    d = _decide(monkeypatch, json.dumps({"decision": "sell", "symbol": "005930", "qty": "2", "price": "99.5", "rationale": "exit"}))
    assert (d.intent["action"], d.intent["qty"], d.intent["price"]) == ("SELL", 2, 99.5) and d.rationale == "exit"


def test_signal_alias_buy_without_price_uses_market_snapshot_default(monkeypatch):
    d = _decide(monkeypatch, json.dumps({"signal": "BUY", "symbol": "005930", "qty": 1}))
    # default_price=market_snapshot.price=100 fills the missing limit price, so the order stays valid
    assert d.intent["action"] == "BUY" and d.intent["price"] == 100.0


@pytest.mark.parametrize("obj", [{"signal": []}, {"signal": {"x": 1}}, {"decision": []}, {"signal": ""}])
def test_unusable_alias_values_become_safe_noop_without_error(monkeypatch, obj):
    d = _decide(monkeypatch, json.dumps(obj))
    assert d.intent["action"] == "NOOP" and d.meta["attempts"] == 1 and "error" not in d.meta


def test_non_json_content_is_soft_noop_with_adapter_reason(monkeypatch):
    d = _decide(monkeypatch, "not json")
    assert d.intent["action"] == "NOOP" and d.intent["reason"] == "model_no_signal"
    assert d.rationale == "no_json_object_in_content" and d.meta["adapter_fallback_reason"] == "no_json_object" and d.meta["attempts"] == 1


def test_json_without_known_keys_is_missing_intent_action_noop(monkeypatch):
    d = _decide(monkeypatch, json.dumps({"foo": 1}))
    assert d.intent["action"] == "NOOP" and d.meta["adapter_fallback_reason"] == "missing_intent_action" and d.rationale == "missing_intent_action_in_json"


def test_circuit_state_is_untouched_by_soft_noops_and_success_is_recorded(monkeypatch):
    _decide(monkeypatch, "not json")
    _decide(monkeypatch, json.dumps({"signal": "NOOP"}))
    assert all(v == {"fail_count": 0.0, "open_until_epoch": 0.0} for v in OpenAIStrategist._CB_STATE.values())
