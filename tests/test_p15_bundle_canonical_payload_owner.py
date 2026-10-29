"""P15 A3: ``_prefer_canonical_payload`` moved to live_execution_bundle_runner_canonical_payload; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_canonical_payload as owner

GOLDEN = ["ea2c2908c26bccd8ae989b11cd4ce354f0cc3361a8f78dd8f4f39c542a81dcd1", "7468c5669fe507fd51f4d214292909293b6b5bfad4d7867f2b9a43d3b9d454eb", "7ec9b032fb68912fc5f29c4fc41ddbf08f1bf11c42aaf845d9a4d6935ab89ac9", "a43801623f1df7fb4a669d78ba019e5f75fb6c55ceab3ca7ee3a046154b93b5b", "a1e4bffd44dcba82ceb0f7d7c5200230f367fd53f70c6ba12ed5f59e6ba2ddbf", "c523e8df1db87b1ce0bbe61ec4007ae69515d551158aecb7a7eb6d78e7eedc50", "5d27f454dee846319b9155c579e88672298ab836170608a1e5299b66f70666ef"]

CANON = [
    ({"artifacts": {"A": {"v": 1}}, "paths": {"A": " /p/a.json "}}, "A", {"f": 1}, dict(fallback_source="fb"), None),
    ({"artifacts": {"A": {"v": 1}}, "paths": {"A": "/p/a.json"}}, "A", {"f": 1, "v": 0}, dict(fallback_source="fb", normalized_payload={"n": 1}, normalized_path=" /n.json "), None),
    ({"artifacts": {"A": {}}, "paths": {"A": "/p/a.json"}}, "A", {"f": 1}, dict(fallback_source="fb", normalized_payload={}, normalized_path="/n"), None),
    ({"artifacts": {"A": {}}, "paths": {"A": "/p/a.json"}}, "A", {"f": 1}, dict(fallback_source=""), None),
    ({"artifacts": "junk", "paths": "junk"}, "A", None, dict(fallback_source="x"), None),
    ({}, "A", {"f": [1]}, dict(fallback_source="x", normalized_payload="junk"), None),
    ({"artifacts": {"A": {"v": [1]}}}, "A", {"v": 0, "k": 1}, dict(fallback_source="x"), None),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(CANON)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    sources, agent, fallback, kw, _ = CANON[i]
    snap = copy.deepcopy((sources, fallback, kw))
    assert _safe(lambda: r._prefer_canonical_payload(sources, agent, fallback, **kw)) == GOLDEN[i]
    assert _safe(lambda: owner.prefer_canonical_payload(sources, agent, fallback, facade=r, **kw)) == GOLDEN[i]
    assert (sources, fallback, kw) == snap


def test_priority_normalized_then_canonical_then_fallback():
    s0, a, f, kw, _ = CANON[1]
    assert r._prefer_canonical_payload(s0, a, f, **kw) == ({"f": 1, "v": 0, "n": 1}, "normalized_trade_artifact", " /n.json ")      # normalized beats canonical; path kept verbatim
    s, a, f, kw, _ = CANON[0]
    assert r._prefer_canonical_payload(s, a, f, **kw) == ({"f": 1, "v": 1}, "canonical", "/p/a.json")                                 # canonical path stripped
    s, a, f, kw, _ = CANON[2]
    assert r._prefer_canonical_payload(s, a, f, **kw) == ({"f": 1}, "fb", "/p/a.json")
    s, a, f, kw, _ = CANON[3]
    assert r._prefer_canonical_payload(s, a, f, **kw)[1] == "fallback"                                                                # empty fallback_source -> "fallback"


def test_malformed_sources_and_shallow_merge_aliasing():
    s, a, f, kw, _ = CANON[4]
    assert r._prefer_canonical_payload(s, a, f, **kw) == ({}, "x", "")
    s, a, f, kw, _ = CANON[5]
    out = r._prefer_canonical_payload(s, a, f, **kw)
    assert out == ({"f": [1]}, "x", "") and out[0] is not f and out[0]["f"] is f["f"]
    s, a, f, kw, _ = CANON[6]
    merged = r._prefer_canonical_payload(s, a, f, **kw)
    assert merged[0] == {"v": [1], "k": 1} and merged[0]["v"] is s["artifacts"]["A"]["v"] and merged[1:] == ("canonical", "")


def test_facade_has_meaningful_payload_seam(monkeypatch):
    seen = []
    monkeypatch.setattr(r, "_has_meaningful_payload", lambda v: (seen.append(v), False)[1])
    s, a, f, kw, _ = CANON[1]
    out = r._prefer_canonical_payload(s, a, f, **kw)
    assert out == ({"f": 1, "v": 0}, "fb", "/p/a.json") and seen == [kw["normalized_payload"], s["artifacts"]["A"]]


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.live_execution_bundle_runner import" not in src and "import live_execution_bundle_runner\n" not in src
    assert len(inspect.getsource(r._prefer_canonical_payload).splitlines()) <= 12
