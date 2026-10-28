"""RF-041 libs/ai/providers/openai_provider: response-shape helpers, usage parsing and the raw ``_post_json`` (fake urlopen only).

socket.connect is denied for the whole module and ``urllib.request.urlopen`` is replaced where the real HTTP helper is
exercised; ``OpenAIStrategist`` itself is never constructed. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import socket
import urllib.request

import pytest

from libs.ai.providers import openai_provider as op


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    def deny(*_a, **_k):
        raise AssertionError("real network attempted")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


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


def test_post_json_sends_headers_and_json_body_and_parses_the_reply(monkeypatch):
    seen = {}

    def fake(req, data=None, timeout=None):
        seen.update(url=req.full_url, method=req.get_method(), headers={k.lower(): v for k, v in req.header_items()}, data=json.loads(data.decode()), timeout=timeout)
        return _Resp(b'{"ok": true}')

    monkeypatch.setattr(urllib.request, "urlopen", fake)
    out = op._post_json("https://api.invalid/v1/chat/completions", {"Authorization": "Bearer k", "X-A": "b"}, {"model": "m", "msg": "한글"}, timeout=4.5)
    _eq(out, {"ok": True})
    _eq((seen["url"], seen["method"], seen["timeout"], seen["data"]), ("https://api.invalid/v1/chat/completions", "POST", 4.5, {"model": "m", "msg": "한글"}))
    _eq((seen["headers"]["authorization"], seen["headers"]["x-a"]), ("Bearer k", "b"))
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, data=None, timeout=None: _Resp(b""))
    _eq(op._post_json("https://api.invalid/x", {}, {}), {})                                  # an empty body is {} (not an error)
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, data=None, timeout=None: _Resp(b"not json"))
    with pytest.raises(json.JSONDecodeError):
        op._post_json("https://api.invalid/x", None, {})


def test_chat_endpoint_detection_and_fence_helpers():
    _eq([op._looks_like_chat_completions_endpoint(u) for u in ("https://a/v1/Chat/Completions", "https://a/v1/responses", "", None)], [True, False, False, False])
    _eq(op._extract_json_object('{"a": 1}'), {"a": 1})
    _eq(op._extract_json_object("no json here"), None)


@pytest.mark.parametrize("resp,expected", [
    ({}, ""), ({"choices": []}, ""), ({"choices": "x"}, ""),
    ({"choices": [{"message": {"content": "hello"}}]}, "hello"),
    ({"choices": [{"content": "flat"}]}, "flat"),
    ({"choices": ["junk"]}, ""),
    ({"choices": [{"message": {"content": ["a", {"text": "b"}, {"text": 5}, 7]}}]}, "ab"),
    ({"choices": [{"message": {"content": {"json": {"k": 1}}}}]}, ""),                      # dict content is not text
])
def test_extract_chat_content(resp, expected):
    _eq(op._extract_chat_content(resp), expected)


def test_message_finish_reason_and_truncation_detection():
    _eq(op._extract_chat_message({}), {})
    _eq(op._extract_chat_message({"choices": [{"message": {"content": "x"}}]}), {"content": "x"})
    _eq(op._extract_chat_message({"choices": [{"content": "flat"}]}), {"content": "flat"})
    _eq(op._extract_chat_message({"choices": ["junk"]}), {})
    _eq(op._extract_chat_finish_reason({}), "")
    _eq(op._extract_chat_finish_reason({"choices": [{"native_finish_reason": " LENGTH "}]}), "length")
    _eq(op._extract_chat_finish_reason({"choices": [{"finish_reason": "stop", "native_finish_reason": "length"}]}), "stop")
    truncated = {"choices": [{"finish_reason": "length", "message": {"content": "  ", "reasoning": "thinking..."}}]}
    _eq(op._chat_output_truncated_without_final_answer(truncated), True)
    _eq(op._chat_output_truncated_without_final_answer({"choices": [{"finish_reason": "length", "message": {"content": "answer", "reasoning": "r"}}]}), False)
    _eq(op._chat_output_truncated_without_final_answer({"choices": [{"finish_reason": "stop", "message": {"content": "", "reasoning": "r"}}]}), False)
    _eq(op._chat_output_truncated_without_final_answer({"choices": [{"finish_reason": "length", "message": {"content": "", "reasoning": ""}}]}), False)


@pytest.mark.parametrize("resp,expected", [
    ({}, None), ({"choices": []}, None), ({"choices": ["junk"]}, None),
    ({"choices": [{"message": {"parsed": {"a": 1}}}]}, {"a": 1}),
    ({"choices": [{"message": {"content": {"json": {"b": 2}}}}]}, {"b": 2}),
    ({"choices": [{"message": {"content": {"parsed": {"c": 3}}}}]}, {"c": 3}),
    ({"choices": [{"message": {"content": [5, {"json": {"d": 4}}]}}]}, {"d": 4}),
    ({"choices": [{"message": {"content": [{"parsed": {"e": 5}}]}}]}, {"e": 5}),
    ({"choices": [{"message": {"content": [{"input_json": {"f": 6}}]}}]}, {"f": 6}),
    ({"choices": [{"message": {"content": "plain text"}}]}, None),
    ({"choices": [{"message": {"tool_calls": [None, {"function": "x"}, {"function": {"arguments": {"g": 7}}}]}}]}, {"g": 7}),
    ({"choices": [{"message": {"tool_calls": [{"function": {"arguments": '{"h": 8}'}}]}}]}, {"h": 8}),
    ({"choices": [{"message": {"tool_calls": [{"function": {"arguments": "not json"}}]}}]}, None),
    ({"choices": [{"message": {"reasoning": 'thought {"i": 9} done'}}]}, {"i": 9}),
    ({"choices": [{"message": {"reasoning": "no object"}}]}, None),
])
def test_structured_object_extraction_priority(resp, expected):
    _eq(op._extract_chat_structured_object(resp), expected)


def test_usage_and_small_helpers():
    _eq((op._to_nonneg_int("5.9"), op._to_nonneg_int(-1), op._to_nonneg_int("x"), op._to_nonneg_int(None)), (5, None, None, None))
    _eq(op._extract_usage({}), {})
    _eq(op._extract_usage({"usage": "x"}), {})
    _eq(op._extract_usage({"usage": {"prompt_tokens": 3, "completion_tokens": "4"}}), {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7})
    _eq(op._extract_usage({"usage": {"prompt_tokens": 3, "total_tokens": 10}}), {"prompt_tokens": 3, "total_tokens": 10})
    _eq(op._extract_usage({"usage": {"completion_tokens": 2}}), {"completion_tokens": 2})
    _eq(op._extract_usage({"usage": {"prompt_tokens": -1, "completion_tokens": -2}}), {})
    _eq(op._safe_noop_intent(), {"action": "NOOP", "reason": "model_no_signal"})
    _eq(op._safe_noop_intent(""), {"action": "NOOP", "reason": "model_no_signal"})
    _eq(op._safe_noop_intent("why"), {"action": "NOOP", "reason": "why"})
