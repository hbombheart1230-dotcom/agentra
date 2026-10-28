"""RF-050 libs/llm/openrouter_client: request shape, env wiring, error mapping and text extraction (fake urlopen only).

``urllib.request.urlopen`` is replaced and socket.connect is denied for the whole module, so a regression that
reaches OpenRouter fails loudly. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import io
import json
import socket
import urllib.error
import urllib.request

import pytest

from libs.llm import openrouter_client as oc


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    def deny(*_a, **_k):
        raise AssertionError("real network attempted")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    for name in ("OPENROUTER_API_KEY", "AI_STRATEGIST_API_KEY", "OPENROUTER_BASE_URL", "OPENROUTER_HTTP_REFERER",
                 "OPENROUTER_TIMEOUT_SEC", "AI_STRATEGIST_TIMEOUT_SEC"):
        monkeypatch.delenv(name, raising=False)


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


class _Resp:
    def __init__(self, body):
        self._b = body

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_config_requires_an_api_key():
    with pytest.raises(ValueError):
        oc.OpenRouterClient(oc.OpenRouterConfig(api_key=""))


def test_from_env_prefers_openrouter_key_then_strategist_key_and_reads_overrides(monkeypatch):
    _eq(oc.OpenRouterClient.from_env(), None)                                   # no key -> no client
    monkeypatch.setenv("AI_STRATEGIST_API_KEY", " strat-key ")
    c = oc.OpenRouterClient.from_env()
    _eq((c.cfg.api_key, c.cfg.base_url, c.cfg.timeout_sec, c.cfg.x_title, c.cfg.http_referer), ("strat-key", oc.DEFAULT_BASE_URL, 15, oc.DEFAULT_X_TITLE, None))
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "  ")
    monkeypatch.setenv("AI_STRATEGIST_TIMEOUT_SEC", "9")
    monkeypatch.setenv("OPENROUTER_HTTP_REFERER", "https://ref.invalid")
    c2 = oc.OpenRouterClient.from_env()
    _eq((c2.cfg.api_key, c2.cfg.base_url, c2.cfg.timeout_sec, c2.cfg.http_referer), ("or-key", oc.DEFAULT_BASE_URL, 9, "https://ref.invalid"))
    monkeypatch.setenv("OPENROUTER_TIMEOUT_SEC", "4")
    _eq(oc.OpenRouterClient.from_env().cfg.timeout_sec, 4)                      # OPENROUTER_TIMEOUT_SEC wins over the strategist one


def test_chat_completions_builds_the_expected_request_and_parses_json(monkeypatch):
    seen = {}

    def fake_urlopen(req, timeout):
        seen.update(url=req.full_url, method=req.get_method(), data=json.loads(req.data.decode()), headers=dict(req.header_items()), timeout=timeout)
        return _Resp(json.dumps({"choices": [{"message": {"content": "hi"}}]}).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    client = oc.OpenRouterClient(oc.OpenRouterConfig(api_key="k", base_url="https://or.invalid/api/v1/", http_referer="https://ref.invalid", x_title="T", timeout_sec=7))
    payload = {"model": "m", "messages": [{"role": "user", "content": "x"}], "__timeout_sec": 3}
    out = client.chat_completions(payload)
    _eq(out["choices"][0]["message"]["content"], "hi")
    _eq((seen["url"], seen["method"], seen["timeout"]), ("https://or.invalid/api/v1/chat/completions", "POST", 3))
    _eq("__timeout_sec" in seen["data"], False)                                 # the private timeout key never reaches the wire
    _eq(seen["data"]["model"], "m")
    h = {k.lower(): v for k, v in seen["headers"].items()}
    _eq((h["authorization"], h["content-type"], h["http-referer"], h["x-title"]), ("Bearer k", "application/json", "https://ref.invalid", "T"))
    _eq("__timeout_sec" in payload, False)                                      # the caller's dict is mutated (popped) - current contract
    client.cfg.http_referer = None
    client.cfg.x_title = None
    client.chat_completions({"model": "m"})
    h2 = {k.lower() for k in seen["headers"]}
    _eq(("http-referer" in h2, "x-title" in h2, seen["timeout"]), (False, False, 7))   # default timeout comes from the config


def test_http_and_url_errors_are_mapped_to_openrouter_error(monkeypatch):
    client = oc.OpenRouterClient(oc.OpenRouterConfig(api_key="k"))

    def http_error(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {}, io.BytesIO(b'{"error":"rate"}'))

    monkeypatch.setattr(urllib.request, "urlopen", http_error)
    with pytest.raises(oc.OpenRouterError, match=r'HTTPError 429: \{"error":"rate"\}'):
        client.chat_completions({"model": "m"})

    def http_error_no_body(req, timeout):
        class _Broken(io.BytesIO):
            def read(self, *a):
                raise OSError("unreadable")

        raise urllib.error.HTTPError(req.full_url, 500, "Server Boom", {}, _Broken(b""))

    monkeypatch.setattr(urllib.request, "urlopen", http_error_no_body)
    with pytest.raises(oc.OpenRouterError, match="HTTPError 500: Server Boom"):
        client.chat_completions({"model": "m"})

    def url_error(req, timeout):
        raise urllib.error.URLError("dns down")

    monkeypatch.setattr(urllib.request, "urlopen", url_error)
    with pytest.raises(oc.OpenRouterError, match="URLError"):
        client.chat_completions({"model": "m"})

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: _Resp(b"not json"))
    with pytest.raises(json.JSONDecodeError):
        client.chat_completions({"model": "m"})                                   # malformed body is NOT wrapped in OpenRouterError


@pytest.mark.parametrize("resp,expected", [
    ({}, ""),
    ({"choices": []}, ""),
    ({"choices": [{"text": "plain"}]}, "plain"),
    ({"choices": [{"message": "junk"}]}, ""),
    ({"choices": [{"message": {"parsed": {"a": 1}}}]}, '{"a": 1}'),
    ({"choices": [{"message": {"content": "  "}, "text": " "}]}, ""),
    ({"choices": [{"message": {"content": "hello"}}]}, "hello"),
    ({"choices": [{"message": {"content": {"json": {"k": "한글"}}}}]}, '{"k": "한글"}'),
    ({"choices": [{"message": {"content": ["a", {"text": "b"}, 5, {"parsed": {"z": 1}}]}}]}, '{"z": 1}'),
    ({"choices": [{"message": {"content": ["a", {"text": "b"}, 5]}}]}, "ab"),
    ({"choices": [{"message": {"content": None, "tool_calls": [None, {"function": "x"}, {"function": {"arguments": '{"q":1}'}}]}}]}, '{"q":1}'),
    ({"choices": [{"message": {"tool_calls": [{"function": {"arguments": {"q": 2}}}]}}]}, '{"q": 2}'),
    ({"choices": [{"message": {"reasoning": "because"}}]}, "because"),
    ({"choices": [{"message": {}}], "output_text": "from output_text"}, "from output_text"),
    ({"choices": [{"message": {}}], "output": [{"content": [{"text": "x"}, {"text": "y"}]}, "junk", {"content": "bad"}]}, "xy"),
    ({"choices": [{"message": {}}], "output": [{"content": []}]}, ""),
])
def test_extract_text_precedence_and_fallbacks(resp, expected):
    _eq(oc.OpenRouterClient.extract_text(resp), expected)
