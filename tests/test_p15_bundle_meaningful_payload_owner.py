"""P15 A2: ``_has_meaningful_payload`` moved to live_execution_bundle_runner_meaningful_payload; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_meaningful_payload as owner

GOLDEN = ["fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b", "b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b", "b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b", "fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b", "b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b", "b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b", "fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa", "b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b"]

MEANINGFUL = [None, [], {}, {"x": []}, {"x": {}}, {"x": {"y": {}}}, {"x": {"y": 0}}, {"x": False}, {"x": ""}, {"x": [None, {}, 0]}, {"x": [None, {}, []]}, {"a": None, "b": {"c": [[], {"d": "v"}]}}, "str", 5, {"x": {"y": {"z": []}}, "w": " "}]
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


@pytest.mark.parametrize("i", range(len(MEANINGFUL)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = MEANINGFUL[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: r._has_meaningful_payload(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.has_meaningful_payload(payload, facade=r)) == GOLDEN[i]
    assert payload == snap


def test_explicit_truth_table_including_current_quirks():
    f = r._has_meaningful_payload
    assert [f(v) for v in (None, [], {}, {"x": []}, {"x": {}}, "str", 5)] == [False] * 7
    assert f({"x": ""}) is False
    # current behavior (pinned, not endorsed): any non-empty nested dict, 0 and False count as meaningful via the generic value check
    assert f({"x": {"y": {}}}) is True and f({"x": {"y": 0}}) is True and f({"x": False}) is True and f({"x": [None, {}, 0]}) is True
    assert f({"x": [None, {}, []]}) is True                                       # a non-empty list differs from every empty marker
    assert f({"a": None, "b": {"c": [[], {"d": "v"}]}}) is True and f({"x": {"y": {"z": []}}, "w": " "}) is True


def test_short_circuit_order_and_facade_recursion_seam(monkeypatch):
    seen = []
    monkeypatch.setattr(r, "_has_meaningful_payload", lambda v: (seen.append(v), True)[1])
    assert owner.has_meaningful_payload({"first": {"inner": 1}, "second": {"never": 1}}, facade=r) is True
    assert seen == [{"inner": 1}]                                                  # returned on the first nested hit
    seen.clear()
    monkeypatch.setattr(r, "_has_meaningful_payload", lambda v: (seen.append(v), False)[1])
    assert owner.has_meaningful_payload({"a": {}, "b": {"x": 1}}, facade=r) is True       # {} is not "meaningful" by itself; {"x":1} -> falls to value check
    assert seen == [{}, {"x": 1}] or seen == [{"x": 1}]


def test_deeply_nested_empty_structures_follow_the_same_rule():
    assert r._has_meaningful_payload({"x": {"k": {"deep": [{}]}}}) is True      # non-empty dict value is never equal to the empty markers
    assert r._has_meaningful_payload({"x": {"k": {}}, "y": []}) is True
    assert r._has_meaningful_payload({"x": [], "y": {}, "z": None, "w": ""}) is False


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.live_execution_bundle_runner import" not in src and "import live_execution_bundle_runner\n" not in src
    assert len(inspect.getsource(r._has_meaningful_payload).splitlines()) <= 3
