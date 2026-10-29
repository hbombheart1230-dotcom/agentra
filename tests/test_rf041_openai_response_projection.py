"""P15 A2 (RF-041): OpenAI chat response projection moved to openai_response_projection; parity with the pre-move provider helpers."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

import libs.ai.providers.openai_provider as op
from libs.ai.providers import openai_response_projection as owner

GOLDEN_SHA = "d30660f54242dc7c88341fe96b1e90326d658e168b2f81578dfd6cc8d236df30"   # sha256 of all helper outputs computed with the pre-move openai_provider (HEAD 11435b1b)

RESPS = [
    {}, {"choices": []}, {"choices": "x"}, {"choices": ["junk"]},
    {"choices": [{"message": {"content": "plain text"}}]},
    {"choices": [{"content": "flat"}]},
    {"choices": [{"message": {"content": [{"text": "a"}, "b", {"x": 1}, {"text": 5}, {"text": "c"}]}}]},
    {"choices": [{"message": {"content": 5}}]},
    {"choices": [{"message": {"parsed": {"action": "BUY"}}}]},
    {"choices": [{"message": {"content": {"json": {"a": 1}}}}]},
    {"choices": [{"message": {"content": {"parsed": {"b": 2}}}}]},
    {"choices": [{"message": {"content": [{"json": {"c": 3}}]}}]},
    {"choices": [{"message": {"content": ["s", {"input_json": {"d": 4}}]}}]},
    {"choices": [{"message": {"content": "", "tool_calls": ["x", {"function": "no"}, {"function": {"arguments": {"e": 5}}}]}}]},
    {"choices": [{"message": {"content": "", "tool_calls": [{"function": {"arguments": "```json\n{\"f\": 6}\n```"}}]}}]},
    {"choices": [{"message": {"content": "", "tool_calls": [{"function": {"arguments": "not json"}}]}}]},
    {"choices": [{"message": {"content": "", "reasoning": "thinking {\"g\": 7} done"}}]},
    {"choices": [{"message": {"content": "", "reasoning": "no object"}}]},
    {"choices": [{"message": {"content": "", "reasoning": "chain of thought"}, "finish_reason": "length"}]},
    {"choices": [{"message": {"content": "answer", "reasoning": "r"}, "finish_reason": "length"}]},
    {"choices": [{"message": {"content": "", "reasoning": ""}, "finish_reason": "length"}]},
    {"choices": [{"message": {"content": "", "reasoning": "r"}, "native_finish_reason": " LENGTH "}]},
    {"choices": [{"message": {"content": "", "reasoning": "r"}, "finish_reason": "stop"}]},
    {"choices": [{"message": {"content": ["x"], "reasoning": "r"}, "finish_reason": "length"}]},
]
USAGES = [{}, {"usage": "x"}, {"usage": {"prompt_tokens": 3, "completion_tokens": "4"}}, {"usage": {"prompt_tokens": 3, "total_tokens": 10}},
          {"usage": {"completion_tokens": 2}}, {"usage": {"prompt_tokens": -1, "completion_tokens": -2}}, {"usage": {"prompt_tokens": "x", "total_tokens": 1.9}},
          {"usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 99}}, {"usage": {}}]
NONNEG = [None, "", "5", 5.9, -1, "x", "nan", float("inf"), True, [], 0]


def _j(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr)


def test_facade_helpers_match_pre_move_golden_for_all_fixtures():
    snap = copy.deepcopy((RESPS, USAGES))
    out = {"content": [op._extract_chat_content(r) for r in RESPS], "message": [op._extract_chat_message(r) for r in RESPS],
           "finish": [op._extract_chat_finish_reason(r) for r in RESPS], "trunc": [op._chat_output_truncated_without_final_answer(r) for r in RESPS],
           "struct": [op._extract_chat_structured_object(r) for r in RESPS], "usage": [op._extract_usage(r) for r in USAGES],
           "nonneg": [op._to_nonneg_int(v) for v in NONNEG]}
    assert (RESPS, USAGES) == snap                                              # inputs never mutated
    assert hashlib.sha256(_j(out).encode()).hexdigest() == GOLDEN_SHA


def test_owner_functions_equal_facade_wrappers():
    for r in RESPS:
        assert owner.extract_chat_content(r) == op._extract_chat_content(r)
        assert owner.extract_chat_message(r) == op._extract_chat_message(r)
        assert owner.extract_chat_finish_reason(r) == op._extract_chat_finish_reason(r)
        assert owner.chat_output_truncated_without_final_answer(r, facade=op) == op._chat_output_truncated_without_final_answer(r)
        assert owner.extract_chat_structured_object(r, facade=op) == op._extract_chat_structured_object(r)
    for u in USAGES:
        assert owner.extract_usage(u, facade=op) == op._extract_usage(u)
    for v in NONNEG:
        assert owner.to_nonneg_int(v) == op._to_nonneg_int(v)


def test_spot_values_text_structured_tool_call_reasoning_usage_none():
    assert op._extract_chat_content(RESPS[6]) == "abc" and op._extract_chat_content(RESPS[7]) == "" and op._extract_chat_content({}) == ""
    assert op._extract_chat_structured_object(RESPS[8]) == {"action": "BUY"} and op._extract_chat_structured_object(RESPS[9]) == {"a": 1}
    assert op._extract_chat_structured_object(RESPS[12]) == {"d": 4} and op._extract_chat_structured_object(RESPS[13]) == {"e": 5}
    assert op._extract_chat_structured_object(RESPS[14]) == {"f": 6} and op._extract_chat_structured_object(RESPS[15]) is None
    assert op._extract_chat_structured_object(RESPS[16]) == {"g": 7} and op._extract_chat_structured_object(RESPS[17]) is None
    assert op._chat_output_truncated_without_final_answer(RESPS[18]) is True and op._chat_output_truncated_without_final_answer(RESPS[19]) is False
    assert op._chat_output_truncated_without_final_answer(RESPS[20]) is False and op._chat_output_truncated_without_final_answer(RESPS[21]) is True
    assert op._extract_usage(USAGES[2]) == {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7} and op._extract_usage(USAGES[0]) == {}
    assert op._extract_usage(USAGES[7]) == {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 99}


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(op, "_extract_json_object", lambda text: {"patched": text})
    assert op._extract_chat_structured_object(RESPS[14]) == {"patched": RESPS[14]["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]}
    monkeypatch.setattr(op, "_to_nonneg_int", lambda v: 7)
    assert op._extract_usage({"usage": {"prompt_tokens": "x"}}) == {"prompt_tokens": 7, "completion_tokens": 7, "total_tokens": 7}
    monkeypatch.setattr(op, "_extract_chat_finish_reason", lambda r: "length")
    assert op._chat_output_truncated_without_final_answer(RESPS[22]) is True
    monkeypatch.setattr(op, "_extract_chat_message", lambda r: {"content": "", "reasoning": "r"})
    assert op._chat_output_truncated_without_final_answer({}) is True


def test_owner_does_not_import_the_facade_and_wrappers_are_thin():
    src = inspect.getsource(owner)
    assert "openai_provider" not in src.replace("``libs.ai.providers.openai_provider``", "").replace("openai_provider)", "")
    for name in ("_extract_chat_content", "_extract_chat_message", "_extract_chat_finish_reason", "_chat_output_truncated_without_final_answer",
                 "_extract_chat_structured_object", "_extract_usage", "_to_nonneg_int"):
        assert len(inspect.getsource(getattr(op, name)).splitlines()) <= 2
