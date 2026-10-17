"""Display-only extraction: actual exit priority/decision authority remains BASE."""
import ast
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
import work_monitor_observation_replay as R

PATH, NAMES = R.SPECS["m004"]
FROZEN = json.loads((ROOT / "tests/fixtures/work_monitor/m004.json").read_text(encoding="utf-8"))


def test_m004_full_module_including_priority_and_hard_soft_emergency_contracts():
    assert T.verified_current_source(PATH) == T.base_source(PATH)
    owner = (ROOT / T.BODY_MOVES[PATH]["owner"]).read_text(encoding="utf-8")
    assert len(owner.splitlines()) <= 350
    tree = ast.parse(owner)
    assert not any(isinstance(n, ast.Import) for n in tree.body)
    assert {n.module for n in tree.body if isinstance(n, ast.ImportFrom)} == {"typing", "__future__"}
    assert {n.name for n in tree.body if isinstance(n, ast.FunctionDef)} == set(NAMES)
    assert {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "facade"} == {"to_float", "_is_trueish"}


def test_m004_full_inventory_and_unmodified_numeric_base_closure():
    fresh = R.produce("m004")
    assert FROZEN["BASE"] == T.BASE
    for key in ("producer_sha256", "source_sha256", "records"):
        assert FROZEN[key] == fresh[key]
    assert len(FROZEN["records"]) == len({r["id"] for r in FROZEN["records"]}) == 97
    assert (ROOT / "libs/runtime/monitor_exit/numeric.py").read_text(encoding="utf-8") == T.base_source("libs/runtime/monitor_exit/numeric.py")


@pytest.mark.parametrize("row", FROZEN["records"], ids=lambda r: r["id"])
def test_m004_label_list_order_values_exceptions_and_input_aliases(row):
    current = importlib.import_module(PATH[:-3].replace("/", "."))
    base = R.baseline("m004")
    assert inspect.signature(getattr(current, row["function"])) == inspect.signature(getattr(base, row["function"]))
    assert R.observe(getattr(current, row["function"]), row["input"]) == row["expected"]


def test_m004_use_time_mid_call_patch_and_callback_order(monkeypatch):
    current = importlib.import_module(PATH[:-3].replace("/", "."))
    all_logs = []
    for module in (current, R.baseline("m004")):
        calls = []
        def float_first(value):
            calls.append(["float_first", value])
            module.to_float = lambda v: calls.append(["float_later", v]) or 0
            return 1
        def trueish(value):
            calls.append(["trueish", value])
            return True
        with monkeypatch.context() as patch:
            patch.setattr(module, "to_float", float_first)
            patch.setattr(module, "_is_trueish", trueish)
            result = module.monitor_watch_axes({"hard_stop_pct": 1, "cost_aware_profit_floor_enabled": "on"})
            assert result == ["Hard stop"]
            all_logs.append(calls)
    assert all_logs[0] == all_logs[1]
    assert all_logs[0][:4] == [["float_first", 1], ["float_later", None], ["float_later", None], ["trueish", "on"]]


@pytest.mark.parametrize("optimized", (False, True))
def test_m004_policy_and_priority_negative_corruptions(optimized, tmp_path):
    code = '''
import sys,ast
sys.path.insert(0,sys.argv[1]);import work_monitor_current_tree as T
path='libs/runtime/monitor_exit/reasons.py';target=T.BODY_MOVES[path]['owner'];src=(T.ROOT/path).read_text(encoding='utf-8');owner=(T.ROOT/target).read_text(encoding='utf-8')
def reject(s,o):
 try:T.verified_current_source(path,source=s,owners={target:o})
 except AssertionError:return
 raise RuntimeError('false PASS')
for name in ('exit_reason_priority','is_emergency_exit_reason','is_hard_exit_reason','is_soft_profit_exit_reason'):
 tree=ast.parse(src);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);fn.body=[ast.Return(value=ast.Constant(None))];reject(ast.unparse(ast.fix_missing_locations(tree)),owner)
reject(src,owner.replace('facade.to_float','facade.execute_order'))
reject(src+'\\nraise RuntimeError()\\n',owner)
print('6 rejected')
'''
    result = subprocess.run([sys.executable] + (["-O"] if optimized else []) + ["-c", code, str(ROOT / "scripts/refactor")], cwd=tmp_path, env=dict(os.environ), text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "6 rejected"
