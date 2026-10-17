"""Empty DTO parity, whole source protection, capability traps and late callbacks."""
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

BATCH = "m003"
PATH, NAMES = R.SPECS[BATCH]
FROZEN = json.loads((ROOT / "tests/fixtures/work_monitor/m003.json").read_text(encoding="utf-8"))


def test_m003_full_module_ast_including_all_guard_and_threshold_bodies():
    assert T.verified_current_source(PATH) == T.base_source(PATH)
    owner = (ROOT / T.BODY_MOVES[PATH]["owner"]).read_text(encoding="utf-8")
    assert len(owner.splitlines()) <= 350
    tree = ast.parse(owner)
    assert not any(isinstance(n, ast.Import) for n in tree.body)
    assert {n.module for n in tree.body if isinstance(n, ast.ImportFrom)} == {"typing", "__future__"}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "facade"}
    assert attrs == R.RECLAIM | {"_build_monitor_signal_evidence"}
    assert "_empty_human_chart_buy_guard" not in T.BODY_MOVES[PATH]["functions"]
    assert "_empty_human_chart_entry_setup" not in T.BODY_MOVES[PATH]["functions"]


def test_m003_exact_frozen_inventory_reproduces_from_base():
    fresh = R.produce(BATCH)
    assert FROZEN["BASE"] == fresh["BASE"] == T.BASE
    for key in ("producer_sha256", "source_sha256", "records"):
        assert FROZEN[key] == fresh[key]
    assert len(FROZEN["records"]) == len({r["id"] for r in FROZEN["records"]}) == 14


@pytest.mark.parametrize("row", FROZEN["records"], ids=lambda r: r["id"])
def test_m003_exact_result_errors_keys_and_mutation(row):
    module = importlib.import_module(PATH[:-3].replace("/", "."))
    base = R.baseline(BATCH)
    assert inspect.signature(getattr(module, row["function"])) == inspect.signature(getattr(base, row["function"]))
    assert R.observe(getattr(module, row["function"]), row["input"]) == row["expected"]


def test_m003_fresh_nested_containers_each_call_and_no_policy_authority():
    owner = importlib.import_module(T.BODY_MOVES[PATH]["owner"][:-3].replace("/", "."))
    base = R.baseline(BATCH)
    class ClosedFacade:
        def __getattr__(self, name):
            if name in R.RECLAIM | {"_build_monitor_signal_evidence"}:
                return getattr(base, name)
            raise AssertionError("policy/Broker/guard/effect capability access: " + name)
    def ids(value):
        out = {id(value)} if isinstance(value, (dict, list)) else set()
        for child in value.values() if isinstance(value, dict) else value if isinstance(value, list) else []:
            out |= ids(child)
        return out
    for name in NAMES:
        fn = getattr(owner, name)
        left, right = fn(facade=ClosedFacade()), fn(facade=ClosedFacade())
        assert ids(left).isdisjoint(ids(right))


def test_m003_use_time_builder_and_constant_identity(monkeypatch):
    current = importlib.import_module(PATH[:-3].replace("/", "."))
    for module in (current, R.baseline(BATCH)):
        calls, marker = [], {"nested": [1]}
        def callback(**kwargs):
            calls.append(kwargs)
            return marker
        with monkeypatch.context() as patch:
            patch.setattr(module, "_build_monitor_signal_evidence", callback)
            assert module._empty_monitor_signal_evidence(score_threshold=7) is marker
            assert len(calls) == 1 and calls[0]["score_threshold"] == 7
            assert len(calls[0]) == 28
            for name in R.RECLAIM:
                patch.setattr(module, name, marker)
            result = module._empty_monitor_policy_aware_gating()
            assert result["reclaim_tuning_version"] is marker
            assert result["reclaim_tuning_scope"] is marker
            assert result["reclaim_near_ready_distance_min"] is marker


@pytest.mark.parametrize("optimized", (False, True))
def test_m003_full_module_and_owner_mutations_fail_closed(optimized, tmp_path):
    code = '''
import sys,ast
sys.path.insert(0,sys.argv[1]);import work_monitor_current_tree as T
path='libs/runtime/intraday_monitor_signals.py';target=T.BODY_MOVES[path]['owner']
src=(T.ROOT/path).read_text(encoding='utf-8');owner=(T.ROOT/target).read_text(encoding='utf-8')
def reject(s,o):
 try:T.verified_current_source(path,source=s,owners={target:o})
 except AssertionError:return
 raise RuntimeError('false PASS')
reject(src+'\\nraise RuntimeError()\\n',owner)
reject(src,owner+'\\nimport os\\n')
reject(src,owner.replace('facade._build_monitor_signal_evidence','facade.execute_order'))
for name in ('_empty_human_chart_buy_guard','_empty_human_chart_entry_setup','_build_monitor_signal_evidence'):
 tree=ast.parse(src);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);fn.body=[ast.Return(value=ast.Constant(None))]
 reject(ast.unparse(ast.fix_missing_locations(tree)),owner)
reject(src.replace('_RECLAIM_NEAR_READY_DISTANCE_MIN_BASE = -0.0015','_RECLAIM_NEAR_READY_DISTANCE_MIN_BASE = -9'),owner)
print('7 rejected')
'''
    cmd = [sys.executable] + (["-O"] if optimized else []) + ["-c", code, str(ROOT / "scripts/refactor")]
    result = subprocess.run(cmd, cwd=tmp_path, env=dict(os.environ), text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "7 rejected"
