"""P15 A1: ``_latest_decision_trace_payload`` moved to live_execution_bundle_runner_decision_trace; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_decision_trace as owner

GOLDEN = ["44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "c3d7279c385dd8ea0d6f73145c26fa7619559e6ef991281facfbcd91a3681130", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "2702d31a05cf04f22a8691df208cdc0ae062b8d7ad7aec7972d0c4a44ed0957b", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"]

TRACE_ROWS = [
    {"stage": "decision_trace", "event": "agent_done", "payload": {"agent": "Scanner", "payload": {"n": 1, "nested": {"k": [1]}}}},
    {"stage": "decision_trace", "event": "agent_done", "payload": {"agent": " scanner ", "payload": {"n": 2, "nested": {"k": [2]}}}},
    {"stage": "other", "event": "agent_done", "payload": {"agent": "scanner", "payload": {"n": 99}}},
    {"stage": "decision_trace", "event": " agent_done ", "payload": {"agent": "STRATEGIST", "payload": {"s": 1}}},
    {"stage": "decision_trace", "event": "agent_done", "payload": "junk"},
    {"stage": "decision_trace", "event": "agent_done", "payload": {"agent": "scanner", "payload": "notdict"}},
]
TRACE_CASES = [([], "agent_done", "scanner"), (TRACE_ROWS, "agent_done", "scanner"), (TRACE_ROWS, "agent_done", " STRATEGIST "), (TRACE_ROWS, "nomatch", "scanner"), (TRACE_ROWS[:1], "agent_done", "SCANNER"), (TRACE_ROWS[4:], "agent_done", "scanner")]
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


@pytest.mark.parametrize("i", range(len(TRACE_CASES)))
def test_wrapper_and_owner_match_pre_move_golden_and_rows_unchanged(i):
    rows, event, agent = TRACE_CASES[i]
    snap = copy.deepcopy(rows)
    assert _safe(lambda: r._latest_decision_trace_payload(rows, event=event, agent=agent)) == GOLDEN[i]
    assert _safe(lambda: owner.latest_decision_trace_payload(rows, event=event, agent=agent)) == GOLDEN[i]
    assert rows == snap


def test_latest_matching_row_wins_case_and_whitespace_insensitive_agent():
    assert r._latest_decision_trace_payload([], event="agent_done", agent="scanner") == {}
    assert r._latest_decision_trace_payload(TRACE_ROWS, event="agent_done", agent="scanner") == {}      # newest matching row has a non-dict inner payload -> returns {} (first reverse match wins)
    got = r._latest_decision_trace_payload(TRACE_ROWS[:5], event="agent_done", agent="scanner")
    assert got["n"] == 2                                                         # newest row with a dict payload; older n=1 is ignored
    assert r._latest_decision_trace_payload(TRACE_ROWS, event="agent_done", agent=" STRATEGIST ") == {"s": 1}
    assert r._latest_decision_trace_payload(TRACE_ROWS, event="nomatch", agent="scanner") == {}
    assert r._latest_decision_trace_payload(TRACE_ROWS[4:], event="agent_done", agent="scanner") == {}


def test_result_is_a_shallow_copy():
    rows = [copy.deepcopy(TRACE_ROWS[0])]
    got = r._latest_decision_trace_payload(rows, event="agent_done", agent="scanner")
    assert got is not rows[0]["payload"]["payload"] and got == rows[0]["payload"]["payload"]
    assert got["nested"] is rows[0]["payload"]["payload"]["nested"]               # nested objects stay aliased
    got["added"] = 1
    assert "added" not in rows[0]["payload"]["payload"]


def test_non_dict_row_keeps_original_attribute_error():
    with pytest.raises(AttributeError):
        r._latest_decision_trace_payload(["junk"], event="e", agent="a")
    with pytest.raises(AttributeError):
        owner.latest_decision_trace_payload(["junk"], event="e", agent="a")


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.live_execution_bundle_runner import" not in src and "import live_execution_bundle_runner\n" not in src
    assert len(inspect.getsource(r._latest_decision_trace_payload).splitlines()) <= 3
