"""P15 C02-1: AI strategist factory / OpenAI provider / intent schema / decide_trade consumer edges (all fake, no network)."""
from __future__ import annotations

import copy
import socket
import urllib.error
from types import SimpleNamespace

import pytest

import libs.ai.providers.openai_provider as prov
from libs.ai import strategist_factory as factory
from libs.ai.intent_schema import normalize_intent
from libs.ai.strategist import BlockedStrategist, RuleStrategist, StrategyInput
from libs.ai.strategist_factory import StrategyV1Strategist
from libs.ai.providers.openai_provider import OpenAIStrategist

ENV_KEYS = ("AI_STRATEGIST_PROVIDER", "AI_STRATEGIST_API_KEY", "OPENROUTER_API_KEY", "AI_STRATEGIST_ENDPOINT", "AI_STRATEGIST_MODEL",
            "STRATEGIST_FRAME_USE_LLM", "STRATEGIST_FRAME_LLM_STRICT", "AI_STRATEGIST_CB_FAIL_THRESHOLD", "AI_STRATEGIST_CB_COOLDOWN_SEC",
            "AI_STRATEGIST_TIMEOUT_SEC", "AI_STRATEGIST_MAX_TOKENS", "AI_STRATEGIST_RETRY_MAX", "AI_STRATEGIST_RETRY_BACKOFF_SEC")


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    for k in ENV_KEYS:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("USE_STRATEGY_V1", "false")
    monkeypatch.setattr(OpenAIStrategist, "_CB_STATE", {})                      # global circuit state restored after each test

    def deny(*a, **k):
        raise AssertionError("real network/socket use")

    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def _x(price=70000):
    return StrategyInput(symbol="005930", market_snapshot={"price": price}, portfolio_snapshot={"cash": 2_000_000}, risk_context={})


def _strategist(**kw):
    base = dict(api_key="k", endpoint="https://example.invalid/custom", model="test-model", retry_max=0, retry_backoff_sec=0.0)
    base.update(kw)
    return OpenAIStrategist(**base)


# ---- (a) missing key/endpoint -----------------------------------------------------------------
@pytest.mark.parametrize("policy", [
    {"ai_strategist_provider": "openai"},
    {"ai_strategist_provider": "openai", "ai_strategist_api_key": "k"},
    {"ai_strategist_provider": "openai", "ai_strategist_endpoint": "https://e.invalid/x"},
])
def test_missing_key_or_endpoint_yields_blocked_strategist_and_noop(policy):
    s = factory.get_strategist_from_env(policy)
    assert type(s) is BlockedStrategist and s.reason == "strategist_llm_required" and s.error == "missing_api_key_or_endpoint"
    d = s.decide(_x())
    assert d.intent == {"action": "NOOP", "reason": "strategist_llm_required"}
    assert d.rationale == "strategist_llm_required:missing_api_key_or_endpoint"
    assert d.meta["blocked_reason"] == "strategist_llm_required" and d.meta["strict_required"] is True and d.meta["attempts"] == 0


def test_env_only_key_and_endpoint_are_honoured(monkeypatch):
    monkeypatch.setenv("AI_STRATEGIST_PROVIDER", "openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")                          # fallback key name
    monkeypatch.setenv("AI_STRATEGIST_ENDPOINT", "https://e.invalid/v1/chat/completions")
    s = factory.get_strategist_from_env({})
    assert type(s) is OpenAIStrategist and s.api_key == "or-key" and s.endpoint.endswith("/chat/completions")


# ---- (b) rule / legacy defaults and explicit opt-in -----------------------------------------------
def test_no_provider_and_no_endpoint_defaults_to_blocked_rule_mode():
    s = factory.get_strategist_from_env(None)
    assert type(s) is BlockedStrategist and s.error == "legacy_rule_runtime_disabled"


@pytest.mark.parametrize("policy,expected", [
    ({"strategist_provider": "rule"}, "legacy_rule_runtime_disabled"),
    ({"strategist_provider": "local", "allow_legacy_rule_runtime": "no"}, "legacy_rule_runtime_disabled"),
    ({"strategist_provider": "strategy_v1"}, "legacy_strategy_v1_runtime_disabled"),
    ({"strategist_provider": "v1", "allow_legacy_strategy_v1_runtime": "0"}, "legacy_strategy_v1_runtime_disabled"),
    ({"strategist_provider": "mystery"}, "unsupported_provider:mystery"),
])
def test_legacy_and_unknown_providers_stay_blocked_by_default(policy, expected):
    s = factory.get_strategist_from_env(policy)
    assert type(s) is BlockedStrategist and s.error == expected


def test_explicit_opt_in_creates_legacy_strategists():
    assert type(factory.get_strategist_from_env({"strategist_provider": "rule", "allow_legacy_rule_runtime": "true"})) is RuleStrategist
    nested = {"strategist_provider": "rule", "strategist": {"runtime": {"allow_legacy_rule": True}}}
    assert type(factory.get_strategist_from_env(nested)) is RuleStrategist
    assert type(factory.get_strategist_from_env({"strategist_provider": "strategy_v1", "allow_legacy_strategy_v1_runtime": "yes"})) is StrategyV1Strategist
    nested_v1 = {"strategist_provider": "v1", "strategist": {"runtime": {"allow_legacy_strategy_v1": "on"}}}
    assert type(factory.get_strategist_from_env(nested_v1)) is StrategyV1Strategist


# ---- (c) from_env fake construction success / failure ---------------------------------------------
def test_from_env_builds_strategist_from_policy_values():
    policy = {"ai_strategist_provider": "openai", "ai_strategist_api_key": "K", "ai_strategist_endpoint": "https://e.invalid/x",
              "ai_strategist_model": "vendor/model-x", "ai_strategist_timeout_sec": 7, "ai_strategist_max_tokens": 1024,
              "ai_strategist_retry_max": 3}
    s = factory.get_strategist_from_env(policy)
    assert type(s) is OpenAIStrategist and (s.api_key, s.endpoint) == ("K", "https://e.invalid/x")
    assert s.model and s.timeout_sec >= 1.0 and s.max_tokens is not None and s.max_tokens >= 256 and s.retry_max >= 0
    assert s.cb_fail_threshold == 0 and s.json_response_format is True


def test_from_env_circuit_env_values_and_bad_values(monkeypatch):
    policy = {"ai_strategist_provider": "openai", "ai_strategist_api_key": "K", "ai_strategist_endpoint": "https://e.invalid/x"}
    monkeypatch.setenv("AI_STRATEGIST_CB_FAIL_THRESHOLD", "3")
    monkeypatch.setenv("AI_STRATEGIST_CB_COOLDOWN_SEC", "30")
    s = OpenAIStrategist.from_env(policy)
    assert (s.cb_fail_threshold, s.cb_cooldown_sec) == (3, 30.0)
    monkeypatch.setenv("AI_STRATEGIST_CB_FAIL_THRESHOLD", "bad")
    monkeypatch.setenv("AI_STRATEGIST_CB_COOLDOWN_SEC", "bad")
    s = OpenAIStrategist.from_env(policy)
    assert (s.cb_fail_threshold, s.cb_cooldown_sec) == (prov.DEFAULT_CB_FAIL_THRESHOLD, prov.DEFAULT_CB_COOLDOWN_SEC)


def test_from_env_exception_becomes_blocked_with_error_text(monkeypatch):
    def boom(cls, policy=None):
        raise RuntimeError("boom")

    monkeypatch.setattr(OpenAIStrategist, "from_env", classmethod(boom))
    s = factory.get_strategist_from_env({"ai_strategist_provider": "openai", "ai_strategist_api_key": "K", "ai_strategist_endpoint": "https://e.invalid/x"})
    assert type(s) is BlockedStrategist and s.reason == "strategist_llm_failed" and s.error == "RuntimeError:boom"


# ---- (d) _post_with_retry -------------------------------------------------------------------------
def _sleepless(monkeypatch):
    sleeps = []
    monkeypatch.setattr(prov, "time", SimpleNamespace(time=lambda: 1000.0, sleep=lambda s: sleeps.append(s)))
    return sleeps


def test_retry_backoff_doubles_then_succeeds(monkeypatch):
    sleeps, calls = _sleepless(monkeypatch), []

    def post(url, headers, payload, timeout=15.0):
        calls.append(timeout)
        if len(calls) < 3:
            raise TimeoutError("slow")
        return {"ok": 1}

    monkeypatch.setattr(prov, "_post_json", post)
    out = _strategist(retry_max=2, retry_backoff_sec=0.5)._post_with_retry("u", {}, {}, timeout=9.0)
    assert out == ({"ok": 1}, 3) and sleeps == [0.5, 1.0] and calls == [9.0, 9.0, 9.0]


def test_retry_gives_up_after_max_attempts_and_reraises(monkeypatch):
    sleeps, calls = _sleepless(monkeypatch), []

    def post(*a, **k):
        calls.append(1)
        raise TimeoutError("slow")

    monkeypatch.setattr(prov, "_post_json", post)
    with pytest.raises(TimeoutError):
        _strategist(retry_max=1, retry_backoff_sec=0.25)._post_with_retry("u", {}, {}, timeout=1.0)
    assert len(calls) == 2 and sleeps == [0.25]


@pytest.mark.parametrize("exc,retryable", [
    (ValueError("x"), False), (KeyError("k"), False), (TimeoutError(), True), (urllib.error.URLError("down"), True),
    (urllib.error.HTTPError("u", 503, "m", {}, None), True), (urllib.error.HTTPError("u", 429, "m", {}, None), True),
    (urllib.error.HTTPError("u", 408, "m", {}, None), True), (urllib.error.HTTPError("u", 400, "m", {}, None), False),
    (urllib.error.HTTPError("u", 404, "m", {}, None), False),
])
def test_retryable_error_classification_drives_attempt_count(monkeypatch, exc, retryable):
    sleeps, calls = _sleepless(monkeypatch), []

    def post(*a, **k):
        calls.append(1)
        raise exc

    monkeypatch.setattr(prov, "_post_json", post)
    assert OpenAIStrategist._is_retryable_error(exc) is retryable
    with pytest.raises(type(exc)):
        _strategist(retry_max=2, retry_backoff_sec=0.1)._post_with_retry("u", {}, {}, timeout=1.0)
    assert len(calls) == (3 if retryable else 1) and len(sleeps) == (2 if retryable else 0)


def test_zero_backoff_never_sleeps(monkeypatch):
    sleeps = _sleepless(monkeypatch)
    n = []

    def post(*a, **k):
        n.append(1)
        if len(n) == 1:
            raise TimeoutError()
        return {}

    monkeypatch.setattr(prov, "_post_json", post)
    assert _strategist(retry_max=1, retry_backoff_sec=0.0)._post_with_retry("u", {}, {}, 1.0) == ({}, 2) and sleeps == []


# ---- (e) circuit breaker ---------------------------------------------------------------------------
def test_circuit_opens_blocks_calls_and_recovers_after_cooldown(monkeypatch):
    clock = {"now": 1000.0}
    monkeypatch.setattr(prov, "time", SimpleNamespace(time=lambda: clock["now"], sleep=lambda s: None))
    mode, calls = {"fail": True}, []

    def post(url, headers, payload, timeout=15.0):
        calls.append(1)
        if mode["fail"]:
            raise ValueError("bad gateway body")
        return {"intent": {"action": "NOOP", "reason": "risk_limit"}, "rationale": "ok"}

    monkeypatch.setattr(prov, "_post_json", post)
    s = _strategist(cb_fail_threshold=2, cb_cooldown_sec=60.0)
    d1 = s.decide(_x())
    assert d1.intent == {"action": "NOOP", "reason": "strategist_error"} and d1.meta["circuit_state"] == "closed" and d1.meta["circuit_fail_count"] == 1
    d2 = s.decide(_x())
    assert d2.meta["circuit_state"] == "open" and d2.meta["circuit_fail_count"] == 2 and d2.meta["circuit_open_until_epoch"] == 1060
    n = len(calls)
    d3 = s.decide(_x())
    assert d3.intent == {"action": "NOOP", "reason": "circuit_open"} and d3.meta["error_type"] == "CircuitOpen" and d3.meta["attempts"] == 0 and len(calls) == n
    clock["now"] = 1061.0
    mode["fail"] = False
    d4 = s.decide(_x())
    assert d4.intent["action"] == "NOOP" and d4.intent["reason"] != "circuit_open" and len(calls) == n + 1 and d4.meta["attempts"] == 1
    st = OpenAIStrategist._CB_STATE[s._cb_key(s._effective_model())]
    assert st == {"fail_count": 0.0, "open_until_epoch": 0.0}


def test_circuit_disabled_by_default_never_opens(monkeypatch):
    monkeypatch.setattr(prov, "_post_json", lambda *a, **k: (_ for _ in ()).throw(ValueError("x")))
    s = _strategist()
    for _ in range(5):
        d = s.decide(_x())
        assert d.intent["reason"] == "strategist_error" and d.meta["circuit_state"] == "closed" and d.meta["circuit_fail_count"] == 0


def test_missing_config_returns_noop_without_calling_http(monkeypatch):
    monkeypatch.setattr(prov, "_post_json", lambda *a, **k: pytest.fail("http called"))
    d = _strategist(api_key="").decide(_x())
    assert d.intent == {"action": "NOOP", "reason": "missing_config"} and d.meta["attempts"] == 0


def test_decide_parses_native_and_chat_shapes_and_normalizes(monkeypatch):
    seen = []

    def post(url, headers, payload, timeout=15.0):
        seen.append((url, payload))
        return {"intent": {"action": "buy_limit", "qty": "2", "price": "70100", "rationale": "r"}, "rationale": "because"}

    monkeypatch.setattr(prov, "_post_json", post)
    d = _strategist(max_tokens=512).decide(_x())
    assert d.intent["action"] == "BUY" and d.intent["symbol"] == "005930" and d.intent["qty"] == 2 and d.intent["price"] == 70100.0 and d.rationale == "because"
    assert seen[0][1]["max_tokens"] == 512 and "messages" not in seen[0][1] and seen[0][1]["input"]["symbol"] == "005930"
    chat = '{"action":"SELL","symbol":"005930","qty":1,"price":69900,"rationale":"take profit"}'
    monkeypatch.setattr(prov, "_post_json", lambda *a, **k: {"choices": [{"message": {"content": chat}, "finish_reason": "stop"}]})
    d = _strategist(endpoint="https://e.invalid/v1/chat/completions").decide(_x())
    assert d.intent["action"] == "SELL" and d.intent["price"] == 69900.0 and d.meta["endpoint_type"] == "chat_completions"
    monkeypatch.setattr(prov, "_post_json", lambda *a, **k: {"choices": [{"message": {"content": "no json here"}, "finish_reason": "stop"}]})
    d = _strategist(endpoint="https://e.invalid/v1/chat/completions").decide(_x())
    assert d.intent["action"] == "NOOP" and d.intent["reason"] == "model_no_signal" and d.meta["adapter_fallback_reason"] == "no_json_object"
    monkeypatch.setattr(prov, "_post_json", lambda *a, **k: {"intent": "not-an-object"})
    d = _strategist().decide(_x())
    assert d.intent["reason"] == "strategist_error" and d.meta["error_type"] == "ValueError"


# ---- (f) normalize_intent --------------------------------------------------------------------------
def test_normalize_valid_buy_sell_and_noop_without_mutating_input():
    raw = {"action": "buy", "symbol": "005930", "qty": "3", "price": "70000", "rationale": "why"}
    snap = copy.deepcopy(raw)
    out, rationale = normalize_intent(raw)
    assert raw == snap and rationale == "why"
    assert out == {"action": "BUY", "symbol": "005930", "qty": 3, "price": 70000.0, "order_type": "limit", "order_api_id": "ORDER_SUBMIT", "rationale": "why"}
    sell, _ = normalize_intent({"action": "SELL_MARKET", "code": "005930", "quantity": 2, "type": "market"})
    assert sell["action"] == "SELL" and sell["order_type"] == "market" and sell["price"] is None and sell["qty"] == 2
    noop, _ = normalize_intent({"action": "HOLD", "qty": 9, "price": 1})
    assert noop["action"] == "NOOP" and noop["qty"] == 0 and noop["price"] is None
    unk, _ = normalize_intent({"action": "YOLO"})
    assert unk["action"] == "NOOP"


@pytest.mark.parametrize("raw,reason", [
    ({"action": "BUY", "symbol": "005930", "qty": 0, "price": 1}, "invalid_intent_missing_symbol_or_qty"),
    ({"action": "BUY", "symbol": "005930", "qty": -3, "price": 1}, "invalid_intent_missing_symbol_or_qty"),
    ({"action": "BUY", "qty": 1, "price": 1}, "invalid_intent_missing_symbol_or_qty"),
    ({"action": "BUY", "symbol": "005930", "qty": 1}, "invalid_intent_missing_price_for_limit"),
    ({"action": "SELL", "symbol": "005930", "qty": 1, "price": 0}, "invalid_intent_missing_price_for_limit"),
    ({"action": "SELL", "symbol": "005930", "qty": 1, "price": -5}, "invalid_intent_missing_price_for_limit"),
])
def test_invalid_trade_intents_degrade_to_noop_with_reason(raw, reason):
    out, _ = normalize_intent(raw)
    assert out["action"] == "NOOP" and out["reason"] == reason


def test_defaults_are_used_for_missing_symbol_and_price_and_market_needs_no_price():
    out, _ = normalize_intent({"action": "BUY", "qty": 1}, default_symbol="005930", default_price=1234)
    assert out["action"] == "BUY" and out["symbol"] == "005930" and out["price"] == 1234.0
    m, _ = normalize_intent({"action": "BUY", "symbol": "005930", "qty": 1, "order_type": "market"})
    assert m["action"] == "BUY" and m["price"] is None


# ---- (g) decide_trade consumer ---------------------------------------------------------------------
class _FakeStrategist:
    def __init__(self, intent=None, exc=None, meta=None):
        self.intent, self.exc, self.meta, self.calls = intent, exc, meta or {}, []

    def decide(self, x):
        self.calls.append(x)
        if self.exc:
            raise self.exc
        return SimpleNamespace(intent=dict(self.intent), rationale="fake-rationale", meta=dict(self.meta))


def _state(strategist):
    return {"strategist": strategist, "market_snapshot": {"symbol": "005930", "price": 70000},
            "portfolio_snapshot": {"cash": 2_000_000, "open_positions": 0}}


def test_decide_trade_consumes_fake_strategist_without_orders_or_state_files(tmp_path, monkeypatch):
    from graphs.nodes.decide_trade import decide_trade
    monkeypatch.chdir(tmp_path)
    fake = _FakeStrategist(intent={"action": "BUY", "symbol": "005930", "qty": 1, "price": 70000, "order_type": "limit"})
    state = _state(fake)
    out = decide_trade(state)
    assert len(fake.calls) == 1 and fake.calls[0].symbol == "005930"
    pkt = out["decision_packet"]["intent"]
    assert (pkt["action"], pkt["symbol"], pkt["qty"], pkt["price"]) == ("BUY", "005930", 1, 70000.0)
    assert out["decision_trace"]["strategy"] == "_FakeStrategist"
    assert not any(k in out for k in ("order_result", "order_response", "broker_order"))
    assert [p for p in tmp_path.rglob("*") if p.is_file() and p.name.endswith((".json", ".db", ".sqlite"))] == []


def test_decide_trade_turns_strategist_exception_into_noop(tmp_path, monkeypatch):
    from graphs.nodes.decide_trade import decide_trade
    monkeypatch.chdir(tmp_path)
    out = decide_trade(_state(_FakeStrategist(exc=RuntimeError("model exploded"))))
    intent = out["decision_packet"]["intent"]
    assert intent["action"] == "NOOP" and intent["reason"] == "strategist_error"


def test_decide_trade_with_blocked_strategist_returns_noop(tmp_path, monkeypatch):
    from graphs.nodes.decide_trade import decide_trade
    monkeypatch.chdir(tmp_path)
    out = decide_trade(_state(BlockedStrategist(reason="strategist_llm_required", error="missing_api_key_or_endpoint")))
    assert out["decision_packet"]["intent"]["action"] == "NOOP"


def test_decide_trade_buy_with_invalid_price_is_downgraded_to_noop(tmp_path, monkeypatch):
    from graphs.nodes.decide_trade import decide_trade
    monkeypatch.chdir(tmp_path)
    out = decide_trade(_state(_FakeStrategist(intent={"action": "BUY", "symbol": "005930", "qty": 1, "price": 0, "order_type": "limit"})))
    assert out["decision_packet"]["intent"]["action"] == "NOOP"
