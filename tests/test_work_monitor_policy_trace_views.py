"""Grouped policy-observation DTOs preserve policy authority at original owners."""
import ast
import copy
import importlib
import inspect
import json
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/refactor"))
import work_monitor_current_tree as T
import work_monitor_policy_trace_replay as R

FROZEN = json.loads(R.FIXTURE.read_text(encoding="utf-8"))


def test_m005_exact_inventory_producer_and_pinned_base_regeneration():
    fresh = R.produce()
    assert FROZEN["BASE"] == fresh["BASE"] == T.BASE
    for key in ("producer_sha256", "source_sha256", "records"):
        assert FROZEN[key] == fresh[key]
    assert len(FROZEN["records"]) == len({r["id"] for r in FROZEN["records"]}) == 53


@pytest.mark.parametrize("path,name", list(zip(R.PATHS, R.NAMES)))
def test_m005_complete_module_reconstruction_and_original_abi(path, name):
    assert T.verified_current_source(path) == T.base_source(path)
    module = importlib.import_module(path[:-3].replace("/", "."))
    assert inspect.signature(getattr(module, name)) == inspect.signature(getattr(R.baseline(path), name))
    assert getattr(module, name).__module__ == module.__name__


def test_m005_one_cohesive_owner_three_views_no_decision_authority():
    owner_path = T.BODY_MOVES[R.PATHS[0]]["owner"]
    assert {T.BODY_MOVES[p]["owner"] for p in R.PATHS} == {owner_path}
    source = (ROOT / owner_path).read_text(encoding="utf-8")
    assert len(source.splitlines()) <= 350
    tree = ast.parse(source)
    assert {n.name for n in tree.body if isinstance(n, ast.FunctionDef)} == set(R.NAMES) | {"annotate_entry_policy_fields", "annotate_entry_minute_metrics"}
    assert not any(isinstance(n, ast.Import) for n in tree.body)
    assert {n.module for n in tree.body if isinstance(n, ast.ImportFrom)} == {"typing", "__future__"}
    assert {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "facade"} == {"monitor_policy_adjustment_inputs", "summarize_monitor_policy_deltas", "_build_monitor_effective_policy_trace", "build_monitor_commander_memory_application_trace"}


@pytest.mark.parametrize("row", FROZEN["records"], ids=lambda r: r["id"])
def test_m005_exact_ordered_payload_source_precedence_exceptions_aliases_and_inputs(row):
    module = importlib.import_module(row["path"][:-3].replace("/", "."))
    assert R.observe(getattr(module, row["function"]), row["input"]) == row["expected"]


def test_m005_effective_trace_callback_order_and_return_aliases(monkeypatch):
    current = importlib.import_module(R.PATHS[1][:-3].replace("/", "."))
    logs = []
    for module in (current, R.baseline(R.PATHS[1])):
        calls = []
        adjustments, deltas = {"playbook": "synthetic"}, [{"field": "stop_loss_pct", "from": 0.1, "to": 0.2}]
        def inputs(frame):
            calls.append(["inputs", frame])
            return adjustments
        def diff(received, effective):
            calls.append(["diff", received, effective])
            return deltas
        with monkeypatch.context() as patch:
            patch.setattr(module, "monitor_policy_adjustment_inputs", inputs)
            patch.setattr(module, "summarize_monitor_policy_deltas", diff)
            frame, before, after = {"tag": 1}, {}, {"adjustments": ["mock"]}
            result = module.build_monitor_effective_policy_trace(received_policy=before, effective_policy=after, frame=frame, received_policy_source="mock")
            assert calls == [["inputs", frame], ["diff", before, after]]
            assert calls[0][1] is frame and calls[1][1] is before and calls[1][2] is after
            assert result["policy_adjustments"]["inputs"] is adjustments
            assert result["effective_policy_deltas"] is deltas
            logs.append(result)
    assert logs[0] == logs[1]


def test_m005_existing_facade_return_identity_and_ordered_mutations():
    current = importlib.import_module(R.PATHS[2][:-3].replace("/", "."))
    results = []
    class Traced(dict):
        def __setitem__(self, key, value):
            self.calls.append(key)
            super().__setitem__(key, value)
    for module in (current, R.baseline(R.PATHS[2])):
        payload = Traced(effective_policy_source_chain=["commander", "monitor"], policy_adjustment_summary="summary", policy_adjustment_reasoning="reason")
        payload.calls = []
        callbacks = []
        def build(**kwargs):
            callbacks.append(kwargs)
            return payload
        facade = types.SimpleNamespace(_build_monitor_effective_policy_trace=build)
        result = module.build_entry_effective_policy_trace({}, "mock", {}, {"applied": True}, {}, facade=facade)
        assert result is payload
        assert len(callbacks) == 1
        assert payload.calls == ["effective_policy_source_chain", "effective_policy_source", "policy_adjustment_summary", "policy_adjustment_reasoning"]
        assert result["effective_policy_source_chain"] == ["commander", "commander_memory_bias", "monitor"]
        results.append(dict(result))
    assert results[0] == results[1]


def test_m005_nested_policy_plan_aliases_are_shallow_not_deep_immutable():
    current = importlib.import_module(R.PATHS[0][:-3].replace("/", "."))
    for module in (current, R.baseline(R.PATHS[0])):
        nested = {"payload": [1]}
        kwargs = next(R.inputs(R.NAMES[0]))
        kwargs["strategist_plan"] = {"entry_plan": {"nested": nested}, "exit_plan": {"nested": nested}}
        result = module.build_monitor_policy_trace(**kwargs)
        assert result["policy_ref"]["entry_plan"] is result["timing_assessment"]["entry_plan"]
        assert result["policy_ref"]["entry_plan"]["nested"] is nested
        result["policy_ref"]["entry_plan"]["nested"]["payload"].append(2)
        assert kwargs["strategist_plan"]["entry_plan"]["nested"]["payload"] == [1, 2]


@pytest.mark.parametrize("optimized", (False, True))
def test_m005_full_scope_corruptions_fail_closed_normally_and_optimized(optimized, tmp_path):
    code = '''
import sys,ast
sys.path.insert(0,sys.argv[1]);import work_monitor_current_tree as T
paths=('libs/runtime/monitor_strategy_frame.py','libs/runtime/monitor_entry_policy_context.py','libs/runtime/monitor/entry_candidate_policy.py');count=0
for path in paths:
 target=T.BODY_MOVES[path]['owner'];src=(T.ROOT/path).read_text(encoding='utf-8');owner=(T.ROOT/target).read_text(encoding='utf-8')
 def reject(s,o):
  try:T.verified_current_source(path,source=s,owners={target:o})
  except AssertionError:return
  raise RuntimeError('false acceptance')
 reject(src+'\\nraise RuntimeError()\\n',owner);count+=1
 reject(src,owner.replace('facade._build_monitor_effective_policy_trace','facade.execute_order'));count+=1
 tree=T._tree(src);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name not in T.BODY_MOVES[path]['functions']);fn.body=[ast.Return(value=ast.Constant(None))]
 reject(ast.unparse(ast.fix_missing_locations(tree)),owner);count+=1
 reject(src,owner+'\\nimport os\\n');count+=1
if count!=12:raise RuntimeError(count)
print(count)
'''
    result = subprocess.run([sys.executable] + (["-O"] if optimized else []) + ["-c", code, str(ROOT / "scripts/refactor")], cwd=tmp_path, env=dict(os.environ), text=True, encoding="utf-8", capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "12"
