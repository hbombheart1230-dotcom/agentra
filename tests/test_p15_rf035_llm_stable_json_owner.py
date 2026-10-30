"""P15 RF-035: llm_artifacts _json_stable_text moved to llm_artifacts_hash_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_hash_projection as owner

import json


def test_values():
    for call in (lambda p: m._json_stable_text(p), lambda p: owner.json_stable_text(p, facade=m)):
        assert call({"b": 1, "a": "한"}) == '{"a":"한","b":1}'
        assert call([2, 1]) == "[2,1]"
        assert call(None) == "" and call(0) == "" and call("abc") == "abc"


def test_facade_json_dumps_seam(monkeypatch):
    calls = []
    real = json.dumps

    def spy(*a, **k):
        calls.append(k)
        return real(*a, **k)

    monkeypatch.setattr(m.json, "dumps", spy)
    m._json_stable_text({"a": 1})
    owner.json_stable_text({"a": 1}, facade=m)
    assert len(calls) == 2 and all(c.get("sort_keys") is True and c.get("separators") == (",", ":") for c in calls)
