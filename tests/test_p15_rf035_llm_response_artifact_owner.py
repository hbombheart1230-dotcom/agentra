"""P15 RF-035: llm_artifacts build_llm_response_artifact moved to llm_artifacts_attempt_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_attempt_projection as owner

import json

import pytest

FIXED = "2026-10-30T00:00:00+00:00"


def _call(fn, **kw):
    base = dict(component="scanner", run_id="R")
    base.update(kw)
    if fn is owner.build_llm_response_artifact:
        base["facade"] = m
    return fn(**base)


@pytest.fixture(autouse=True)
def _clock(monkeypatch):
    monkeypatch.setattr(m, "utc_now_iso", lambda: FIXED)


def _fns():
    return (m.build_llm_response_artifact, owner.build_llm_response_artifact)


def test_basic_attempt_projection():
    attempts = [{"system_prompt": "S", "user_prompt": "U", "parsed_output": {"x": 1}, "model_info": {"model": "m"}}]
    outs = [_call(fn, attempts=attempts) for fn in _fns()]
    assert json.dumps(outs[0]) == json.dumps(outs[1])
    out = outs[0]
    assert out["schema_version"] == "llm_response_artifact.v1" and out["saved_at"] == FIXED
    assert out["parsed_output"] == {"x": 1} and out["retry_count"] == 0
    assert out["model"] == "m" and out["system_prompt"] == "S" and out["user_prompt"] == "U"
    assert out["required_keys_missing"] == [] and out["repair_used"] is False


def test_status_timeout():
    for fn in _fns():
        out = _call(fn, status="timeout")
        assert out["status"] == "timeout" and out["llm_status"] == "error"


def test_meta_projection():
    meta = {"error": "oops", "token_usage": {"n": 1}, "repair_used": True}
    for fn in _fns():
        out = _call(fn, meta=meta)
        assert out["error"] == "oops" and out["token_usage"] == {"n": 1} and out["repair_used"] is True
        assert out["meta"] == meta and out["meta"] is not meta


def test_two_empty_attempts_retry_count():
    for fn in _fns():
        out = _call(fn, attempts=[{}, {}, "x"])
        assert out["retry_count"] == 1
        assert out["required_keys_expected"] == [] and out["required_keys_present"] == [] and out["required_keys_missing"] == []
        assert out["completeness_score"] == 0.0 and out["parse_mode"] == "none"


def test_metadata_sources_and_nested_identity():
    cfg = {"k": 1}
    attempt = {"parsed_output": {"p": 1}, "required_keys_missing": ["a"], "completeness_score": "0.5", "llm_execution_effective_config": cfg, "finish_reason": "stop"}
    for fn in _fns():
        out = _call(fn, attempts=[attempt], meta={"parse_mode": "json"})
        assert out["parse_mode"] == "json" and out["required_keys_missing"] == ["a"]
        assert out["completeness_score"] == 0.5 and out["finish_reason"] == "stop"
        assert out["llm_execution_effective_config"] == cfg and out["llm_execution_effective_config"] is not cfg
        assert out["parsed_output"] is attempt["parsed_output"]


def test_facade_seam(monkeypatch):
    monkeypatch.setattr(m, "utc_now_iso", lambda: "T2")
    monkeypatch.setattr(m, "canonical_llm_status", lambda v, *, default="fallback": "partial")
    for fn in _fns():
        out = _call(fn)
        assert out["saved_at"] == "T2" and out["llm_status"] == "partial"
