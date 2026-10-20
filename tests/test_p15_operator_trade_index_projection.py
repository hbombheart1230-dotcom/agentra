"""Pinned BASE differential checks using only synthetic, isolated report files."""
from __future__ import annotations

import ast
import copy
import inspect
import json
import os
from pathlib import Path
import subprocess
import types

import pytest

import apps.operator_ui.data_access_core as core
import apps.operator_ui.data_access_trade_index_projection as owner

BASE = "c0c3f808967dc921a956d01a879fe489674cad71"
ROOT = Path(__file__).resolve().parents[1]


def _original(name):
    source = subprocess.check_output(
        ["git", "show", BASE + ":apps/operator_ui/data_access_core.py"], cwd=ROOT
    ).decode("utf-8")
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<pinned BATCH02 BASE>", "exec",
                 flags=__import__("__future__").annotations.compiler_flag), namespace)
    fn = types.FunctionType(namespace[name].__code__, vars(core))
    fn.__annotations__ = namespace[name].__annotations__
    return fn


def _bytes(value):
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


def _files(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("case", ["normal", "empty", "ties", "priority", "missing_report", "mtime", "late_helper", "exception"])
def test_index_matches_base_bytes_aliases_probes_and_exceptions(case, tmp_path, monkeypatch):
    from test_operator_ui import _make_config, _write_json
    cfg = _make_config(tmp_path)
    first = next(cfg.reports_root.rglob("aggregated_execution_bundle.json"))
    bundle = json.loads(first.read_text(encoding="utf-8"))
    if case in {"ties", "priority"}:
        bundle.update(linked_run_ids=["shared", "shared", ""], run_id="shared")
        _write_json(first, bundle)
        other = first.parent.parent / "second-story" / (
            "lifecycle_bundle.json" if case == "priority" else first.name)
        second = dict(bundle, trade_id="second-story", ts="2000-01-01T00:00:00Z" if case == "priority" else bundle["ts"])
        _write_json(other, second)
        # First visited is the newer filesystem candidate. Equal logical times
        # must allow the second candidate to replace it (>=, not >).
        os.utime(first, (2000000000, 2000000000))
        os.utime(other, (1900000000, 1900000000))
    if case == "missing_report":
        for name in ("trade_report.json", "trade_report.md"):
            (first.parent / name).unlink(missing_ok=True)
    if case == "mtime":
        bundle.pop("ts")
        _write_json(first, bundle)
        os.utime(first, (1900000000, 1900000000))
    if case == "empty":
        monkeypatch.setattr(core, "iter_trade_day_roots", lambda root: [])
    names = ("iter_trade_day_roots", "iter_trade_dirs", "_read_json", "_trade_paths_from_bundle",
             "_existing_trade_path", "_trim_text", "_to_epoch", "normalize_symbol",
             "_normalize_ai_report_diagnostics", "_short_run_id", "_story_type_label",
             "_story_type_badge_class", "_report_status_label")
    funcs = {name: getattr(core, name) for name in names}
    exists, stat = Path.exists, Path.stat
    before = _files(tmp_path)

    def run(fn):
        trace = []
        def wrapped(name):
            def call(*args, **kwargs):
                trace.append((name, repr(args), repr(kwargs)))
                if case == "exception" and name == "_trim_text":
                    raise LookupError("synthetic index failure")
                if case == "late_helper" and name == "_trim_text":
                    def late(value):
                        trace.append(("late_short_run_id", value))
                        return funcs["_short_run_id"](value)
                    monkeypatch.setattr(core, "_short_run_id", late)
                return funcs[name](*args, **kwargs)
            return call
        with monkeypatch.context() as patch:
            for name in funcs:
                patch.setattr(core, name, wrapped(name))
            def probe(path):
                trace.append(("exists", str(path)))
                return exists(path)
            def metadata(path, *args, **kwargs):
                trace.append(("stat", str(path), repr(args), repr(kwargs)))
                return stat(path, *args, **kwargs)
            patch.setattr(Path, "exists", probe)
            patch.setattr(Path, "stat", metadata)
            try:
                result = fn(cfg)
                for record in result["by_story_id"].values():
                    for rid in record["linked_run_ids"]:
                        selected = result["by_run_id"].get(rid)
                        if selected and selected["trade_id"] == record["trade_id"]:
                            assert selected is record
                value = ("value", _bytes(result))
            except Exception as exc:
                result = None
                value = ("exception", type(exc).__name__, str(exc))
        return value, trace, result

    expected = run(_original("_trade_report_index"))
    actual = run(core._trade_report_index)
    assert actual[:2] == expected[:2]
    assert before == _files(tmp_path)
    assert inspect.signature(core._trade_report_index) == inspect.signature(_original("_trade_report_index"))
    if case == "exception":
        assert actual[0] == ("exception", "LookupError", "synthetic index failure")
    else:
        assert actual[0][0] == "value"
    if case in {"ties", "priority"}:
        assert actual[2]["by_run_id"]["shared"]["trade_id"] == "second-story"
    if case == "mtime":
        assert next(iter(actual[2]["by_story_id"].values()))["ts_epoch"] == 1900000000
    if case == "late_helper":
        assert any(row[0] == "late_short_run_id" for row in actual[1])


def test_index_projection_accepts_preread_inputs_without_effects_or_mutation(monkeypatch):
    def forbidden(*a, **kw):
        raise AssertionError("projection attempted IO/LLM")
    for name in ("open", "exists", "stat"):
        monkeypatch.setattr(Path, name, forbidden)
    monkeypatch.setattr(core, "_read_json", forbidden)
    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(forbidden))
    bundle = {"run_id": "run", "linked_run_ids": ["duplicate", "duplicate"]}
    lifecycle = {"run_ids_all": ["entry"], "entry": {"run_id": "entry"}, "exit": {"run_id": "exit"}}
    before = copy.deepcopy((bundle, lifecycle))
    identity = owner._project_trade_identity(bundle=bundle, lifecycle=lifecycle, paths={}, bundle_path=Path("story/bundle.json"))
    assert identity[3] == ["duplicate", "duplicate", "entry", "exit", "run"]
    assert (bundle, lifecycle) == before
    record = {"_path_priority": 2, "ts_epoch": 4}
    by_run, by_story = {"run": {"_path_priority": 1}}, {}
    saved = copy.deepcopy((by_run, by_story))
    updates, stories = owner._project_trade_indexes(story_id="story", linked_run_ids=identity[3],
        by_run_id=by_run, by_story_id=by_story, record=record)
    assert updates["run"] is stories["story"] is record
    assert (by_run, by_story) == saved


@pytest.mark.parametrize("old,new", [(
    '>= int(current.get("ts_epoch") or 0)', '> int(current.get("ts_epoch") or 0)'), (
    '>= int(current_story.get("ts_epoch") or 0)', '> int(current_story.get("ts_epoch") or 0)'), (
    'int(record.get("_path_priority") or 0) >', 'int(record.get("_path_priority") or 0) <'), (
    'for rid in (entry.get("run_id"), exit_ctx.get("run_id")):', 'for rid in ():')])
def test_hostile_index_mutations_are_detected(old, new):
    source = Path(owner.__file__).read_text(encoding="utf-8")
    assert old in source
    namespace = dict(vars(owner))
    exec(compile(source.replace(old, new), "<hostile index mutant>", "exec"), namespace)
    if "for rid" in old:
        inputs = dict(bundle={}, lifecycle={"entry": {"run_id": "entry"}, "exit": {"run_id": "exit"}}, paths={}, bundle_path=Path("story/bundle.json"))
        assert namespace["_project_trade_identity"](**inputs) != owner._project_trade_identity(**inputs)
    else:
        current = {"_path_priority": 1, "ts_epoch": 9, "marker": "old"}
        record = {"_path_priority": 2 if " >" in old else 1, "ts_epoch": 9, "marker": "new"}
        inputs = dict(story_id="s", linked_run_ids=["r"], by_run_id={"r": current}, by_story_id={"s": current}, record=record)
        assert namespace["_project_trade_indexes"](**inputs) != owner._project_trade_indexes(**inputs)
