"""P15 RF-035: llm_artifacts build_compact_input_artifact moved to llm_artifacts_compact_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_compact_projection as owner

FIXED = "2026-10-30T00:00:00+00:00"


def _call(fn, **kw):
    base = dict(component="c", run_id="R")
    base.update(kw)
    if fn is owner.build_compact_input_artifact:
        base["facade"] = m
    return fn(**base)


def _fns():
    return (m.build_compact_input_artifact, owner.build_compact_input_artifact)


def test_counts_and_ratio(monkeypatch):
    monkeypatch.setattr(m, "utc_now_iso", lambda: FIXED)
    compact = {"a": 1}
    for fn in _fns():
        out = _call(fn, source_input={"a": 1, "b": 2}, compact_input=compact)
        assert out["source_char_count"] == 16 and out["compact_input_char_count"] == 8
        assert out["reduction_ratio"] == 0.5 and out["saved_at"] == FIXED
        assert out["compact_input"] is compact and out["schema_version"] == "llm_compact_input.v1"
        assert list(out)[-1] == "compact_input"


def test_invalid_inputs():
    for fn in _fns():
        out = _call(fn, source_input=None, compact_input="x")
        assert out["compact_input"] == {} and out["reduction_ratio"] == 0.0
        assert out["source_char_count"] == 2 and out["compact_input_char_count"] == 2


def test_negative_ratio_clamped_and_story_id():
    for fn in _fns():
        out = _call(fn, source_input={}, compact_input={"a": 1, "bb": 22}, story_id="", trade_id="T", source_artifact_path=None)
        assert out["reduction_ratio"] == 0.0
        assert out["story_id"] == "T" and out["trade_id"] == "T" and out["source_artifact_path"] == ""


def test_facade_seams(monkeypatch):
    monkeypatch.setattr(m, "utc_now_iso", lambda: "T9")
    calls = []
    import json
    real = json.dumps
    monkeypatch.setattr(m.json, "dumps", lambda *a, **k: (calls.append(1), real(*a, **k))[1])
    for fn in _fns():
        calls.clear()
        out = _call(fn)
        assert out["saved_at"] == "T9" and len(calls) == 2
