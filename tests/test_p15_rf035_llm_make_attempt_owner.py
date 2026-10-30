"""P15 RF-035: llm_artifacts make_attempt moved to llm_artifacts_attempt_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_attempt_projection as owner

import pytest

MSG = [{"role": "system", "content": "S"}, {"role": "user", "content": "U"}]


def _run(fn, **kw):
    base = dict(step="", messages=MSG, raw_response_text="r", parsed_output={"a": 1}, model="m", latency_ms="12.9")
    base.update(kw)
    if fn is owner.make_attempt:
        base["facade"] = m
    return fn(**base)


def _fns():
    return (m.make_attempt, owner.make_attempt)


def test_defaults_and_key_order():
    po = {"a": 1}
    for fn in _fns():
        out = _run(fn, parsed_output=po)
        assert out["step"] == "primary" and out["system_prompt"] == "S" and out["user_prompt"] == "U"
        assert out["latency_ms"] == 12 and out["parsed_output"] is po
        assert out["model_info"] == {"provider": "OpenRouter", "model": "m"}
        assert out["status"] == "ok" and out["llm_status"] == "ok" and out["role"] == ""
        assert list(out) == ["step", "role", "system_prompt", "user_prompt", "raw_response_text", "parsed_output", "model_info", "latency_ms", "status", "llm_status"]


def test_status_timeout_and_nondict_output():
    for fn in _fns():
        out = _run(fn, status="timeout", parsed_output="x")
        assert out["status"] == "timeout" and out["llm_status"] == "error" and out["parsed_output"] == {}


def test_meta_does_not_overwrite():
    for fn in _fns():
        out = _run(fn, meta={"role": "planner", "step": "override", "custom": 1})
        assert out["step"] == "primary" and out["role"] == "planner" and out["custom"] == 1
        assert list(out)[-1] == "custom"


def test_bad_latency_value_error():
    for fn in _fns():
        with pytest.raises(ValueError):
            _run(fn, latency_ms="bad")


def test_facade_seam(monkeypatch):
    monkeypatch.setattr(m, "split_prompt_messages", lambda msgs: ("SP", "UP"))
    monkeypatch.setattr(m, "normalize_llm_status", lambda v, *, default="fallback": "partial")
    for fn in _fns():
        out = _run(fn)
        assert out["system_prompt"] == "SP" and out["user_prompt"] == "UP" and out["status"] == "partial"
