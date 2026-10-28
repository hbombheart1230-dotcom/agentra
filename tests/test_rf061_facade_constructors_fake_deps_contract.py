"""RF-061: ``ToolFacade.__init__`` (tool_facade and tool_schema) with every collaborator class replaced by a fake.

Module-level CompositeSkillRunner / TwoPhaseSupervisor / IntentStore / ApprovalService / Settings are
monkeypatched, so no catalog, event log, intent DB, Settings, Supervisor or broker is built. Also pins the
latest-row-wins / newest-first aggregation of ``list_intents`` on a tmp intents file. Explicit raises keep
the checks live under ``python -O``.
"""
from __future__ import annotations

import json

import pytest

from libs.tools import tool_facade as tf
from libs.tools import tool_schema as ts


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


class _Fake:
    def __init__(self, *a, **k):
        self.args, self.kwargs = a, k


def test_tool_facade_init_wires_collaborators_with_given_paths(monkeypatch, tmp_path):
    for name in ("CompositeSkillRunner", "TwoPhaseSupervisor", "IntentStore", "ApprovalService"):
        monkeypatch.setattr(tf, name, _Fake)
    path = tmp_path / "sub" / "intents.jsonl"
    f = tf.ToolFacade(catalog="c.jsonl", event_log="e.jsonl", intent_store=str(path))
    _eq((f.runner.kwargs, f.supervisor.args, f.intent_store.args, f.intent_store_path, f.approvals.args), (
        {"catalog_path": "c.jsonl", "event_log_path": "e.jsonl"}, (), (str(path),), path, (f.intent_store,)))
    _eq(list(tmp_path.iterdir()), [])                                      # constructing creates nothing on disk


def test_tool_schema_facade_init_uses_given_or_env_settings(monkeypatch):
    monkeypatch.setattr(ts, "CompositeSkillRunner", _Fake)
    monkeypatch.setattr(ts, "TwoPhaseSupervisor", _Fake)
    sentinel = object()
    f = ts.ToolFacade(settings=sentinel)
    _eq((f.s is sentinel, f.runner.kwargs["settings"] is sentinel, f.supervisor.kwargs["settings"] is sentinel), (True, True, True))
    built = []

    class FakeSettings:
        @staticmethod
        def from_env():
            built.append(1)
            return "env-settings"

    monkeypatch.setattr(ts, "Settings", FakeSettings)
    _eq(ts.ToolFacade().s, "env-settings")
    _eq(built, [1])


def _facade_with_rows(tmp_path, rows):
    f = tf.ToolFacade.__new__(tf.ToolFacade)
    f.intent_store_path = tmp_path / "intents.jsonl"
    f.intent_store_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return f


def test_list_intents_latest_row_per_id_wins_newest_first(tmp_path):
    rows = [
        {"ts": 1, "intent_id": "a", "intent": {"intent_id": "a", "action": "BUY"}},
        {"ts": 5, "intent": {"intent_id": "b", "action": "SELL"}},
        {"ts": 9, "intent_id": "a", "status": "rejected"},                 # marker row for a
        {"ts": 3, "note": "no id at all"},                                 # skipped
        {"ts": 2, "intent_id": "c", "intent": {"intent_id": "c"}},
    ]
    f = _facade_with_rows(tmp_path, rows)
    out = f.list_intents(limit=2)
    text = json.dumps(out, ensure_ascii=False, default=str)
    ids = [m for m in ("a", "b", "c") if f'"intent_id": "{m}"' in text]
    _eq(ids, ["a", "b"])                                                     # a (ts 9) then b (ts 5); c cut by the limit
    out_all = f.list_intents(limit=0)                                        # limit is floored at 1
    if '"intent_id": "a"' not in json.dumps(out_all, default=str):
        raise AssertionError(out_all)


def test_latest_row_prefers_the_newest_ts_and_ignores_other_ids(tmp_path):
    f = _facade_with_rows(tmp_path, [
        {"ts": 1, "intent_id": "a", "v": "old"},
        {"ts": 4, "intent_id": "b", "v": "other"},
        {"ts": 7, "intent": {"intent_id": "a"}, "v": "new"},
    ])
    _eq(f._latest_row("a")["v"], "new")
    _eq(f._latest_row("zzz"), None)


def test_older_rows_after_newer_ones_do_not_replace_the_latest(tmp_path):
    f = _facade_with_rows(tmp_path, [
        {"ts": 9, "intent_id": "a", "v": "newest"},
        {"ts": 2, "intent_id": "a", "v": "older"},
    ])
    _eq(f._latest_row("a")["v"], "newest")
    text = json.dumps(f.list_intents(limit=5), ensure_ascii=False, default=str)
    if "newest" not in text or "older" in text:
        raise AssertionError(text)
