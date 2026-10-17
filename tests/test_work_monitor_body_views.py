"""Whole-module reconstruction, late dependency resolution and BASE-first views."""
import ast
import copy
import hashlib
import importlib
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/refactor"))
import work_monitor_current_tree as T
import work_monitor_body_replay as R

FROZEN = json.loads(R.FIXTURE.read_text(encoding="utf-8"))


def test_m002_frozen_inventory_and_independent_base_reproduction():
    fresh = R.produce()
    assert FROZEN["BASE"] == T.BASE
    assert FROZEN["source_sha256"] == fresh["source_sha256"]
    assert FROZEN["producer_sha256"] == fresh["producer_sha256"]
    assert FROZEN["records"] == fresh["records"]
    assert len(FROZEN["records"]) == 46
    assert len({r["id"] for r in FROZEN["records"]}) == 46


@pytest.mark.parametrize("path", R.PATHS)
def test_m002_complete_module_ast_and_signatures_and_no_authority(path):
    spec = T.BODY_MOVES[path]
    assert T.verified_current_source(path) == T.base_source(path)
    source = (ROOT / spec["owner"]).read_text(encoding="utf-8")
    assert len(source.splitlines()) <= 350
    tree = ast.parse(source)
    assert not any(isinstance(n, ast.Import) for n in tree.body)
    assert {n.module for n in tree.body if isinstance(n, ast.ImportFrom)} == {"__future__", "typing"}
    assert {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "facade"} <= {"_optional_float"}
    module = importlib.import_module(path[:-3].replace("/", "."))
    base = R.baseline(path)
    for name in spec["functions"]:
        assert inspect.signature(getattr(module, name)) == inspect.signature(getattr(base, name))
        assert getattr(module, name).__module__ == module.__name__


@pytest.mark.parametrize("row", FROZEN["records"], ids=lambda r: r["id"])
def test_m002_base_feature_result_exception_keys_mutation_and_aliases(row):
    module = importlib.import_module(row["path"][:-3].replace("/", "."))
    assert R.observe(getattr(module, row["function"]), row["input"]) == row["expected"]


@pytest.mark.parametrize("optimized", (False, True))
def test_m002_negative_complete_ast_protection_under_optimization(optimized, tmp_path):
    code = '''
import sys,ast
sys.path.insert(0,sys.argv[1])
import work_monitor_current_tree as T
def rejects(path,source,owners):
 try:T.verified_current_source(path,source=source,owners=owners)
 except AssertionError:return
 raise RuntimeError('false acceptance')
count=0
for path in T.BODY_MOVES:
 if path not in ('libs/runtime/monitor_exit/selected_snapshot.py','libs/runtime/monitor_entry_state.py'):continue
 target=T.BODY_MOVES[path]['owner'];src=(T.ROOT/path).read_text(encoding='utf-8');owner=(T.ROOT/target).read_text(encoding='utf-8')
 for bad in (src+'\\nraise RuntimeError("extra")\\n', src.replace('facade=_monitor_view_sys.modules[__name__]','facade=None',1), src+'\\n_hidden_authority=1\\n'):
  rejects(path,bad,{target:owner});count+=1
 rejects(path,src,{target:owner+'\\nimport os\\n'});count+=1
 tree=ast.parse(src)
 untouched=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name not in T.BODY_MOVES[path]['functions'])
 untouched.body.insert(0,ast.Raise(exc=ast.Call(func=ast.Name(id='RuntimeError',ctx=ast.Load()),args=[],keywords=[])))
 rejects(path,ast.unparse(ast.fix_missing_locations(tree)),{target:owner});count+=1
 tree=ast.parse(owner);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef));fn.body=[ast.Return(value=ast.Constant(None))]
 rejects(path,src,{target:ast.unparse(ast.fix_missing_locations(tree))});count+=1
if count!=12:raise RuntimeError(count)
print(count)
'''
    cmd = [sys.executable] + (["-O"] if optimized else []) + ["-c", code, str(ROOT / "scripts/refactor")]
    result = subprocess.run(cmd, cwd=tmp_path, env=dict(os.environ), text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "12"


def test_m002_late_converter_binding_and_reference_identity(monkeypatch):
    path = R.PATHS[1]
    current = importlib.import_module(path[:-3].replace("/", "."))
    base = R.baseline(path)
    for module in (current, base):
        calls = []
        def replacement(value):
            calls.append(value)
            if len(calls) == 1:
                module._optional_float = lambda v: 99
            return 7
        with monkeypatch.context() as patch:
            patch.setattr(module, "_optional_float", replacement)
            result = module.build_monitor_entry_state_snapshot({"metrics": {"volume_ratio": 1}})
            assert result["extended_from_vwap_pct"] == 7
            assert result["volume_ratio"] == 99
            assert len(calls) == 1
    payload = {"nested": [1]}
    entry = {"transition_readiness_score": payload}
    for module in (current, base):
        result = module.build_monitor_entry_transition_trace({}, entry)
        assert result["transition_readiness_score"] is payload
        result["transition_readiness_score"]["nested"].append(2)
        assert entry["transition_readiness_score"]["nested"][-1] == 2
