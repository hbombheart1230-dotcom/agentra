"""Explicitly locally mutating (not pure) annotations preserve input/effect order."""
import ast
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
import work_monitor_annotation_replay as R

FROZEN = json.loads(R.FIXTURE.read_text(encoding="utf-8"))


def test_m008_entire_original_module_and_grouped_owner_ast():
    assert T.verified_current_source(R.SOURCE) == T.base_source(R.SOURCE)
    owner = ROOT / T.BODY_MOVES[R.SOURCE]["owner"]
    assert len(owner.read_text(encoding="utf-8").splitlines()) <= 350
    module = importlib.import_module(R.SOURCE[:-3].replace("/", "."))
    base = R.baseline()
    for name in R.NAMES:
        assert inspect.signature(getattr(module, name)) == inspect.signature(getattr(base, name))


def test_m008_frozen_base_only_inventory_and_helper_provenance():
    fresh = R.produce()
    for key in ("BASE", "producer_sha256", "source_sha256", "records"):
        assert FROZEN[key] == fresh[key]
    assert len(FROZEN["records"]) == len({r["id"] for r in FROZEN["records"]}) == 43


@pytest.mark.parametrize("row", FROZEN["records"], ids=lambda r: r["id"])
def test_m008_result_order_partial_mutation_exception_and_callback_parity(row):
    module = importlib.import_module(R.SOURCE[:-3].replace("/", "."))
    assert R.observe(getattr(module, row["function"]), row["input"], feature=True) == row["expected"]


def test_m008_original_input_identity_and_existing_nested_aliases():
    current = importlib.import_module(R.SOURCE[:-3].replace("/", "."))
    for module in (current, R.baseline()):
        nested = {"existing": [1]}
        entry = {"metrics": nested}
        meta = {"minute_snapshot_age_minutes": 2}
        result = module.annotate_entry_minute_metrics(entry, "mock", [{"ts": "fixed"}], meta, {})
        assert result is None
        assert entry["metrics"] is nested and entry["minute_fetch_meta"] is meta
        entry["minute_fetch_meta"]["new"] = 3
        assert meta["new"] == 3


def test_m008_callback_alias_and_exception_preserve_partial_annotation():
    current = importlib.import_module(R.SOURCE[:-3].replace("/", "."))
    outcomes = []
    for module in (current, R.baseline()):
        values = next(R.inputs(R.NAMES[0]))
        shared = {"nested": [1]}
        result = module.annotate_entry_policy_fields(**values, facade=types.SimpleNamespace(build_monitor_commander_memory_application_trace=lambda **kw: shared))
        assert result is None
        entry = values["entry_info"]
        left, right = entry["commander_memory_application_trace"], entry["monitor_memory_application_trace"]
        assert left is not right and left is not shared
        assert left["nested"] is right["nested"] is shared["nested"]
        left["nested"].append(2)
        assert shared["nested"] == [1, 2]
        values = next(R.inputs(R.NAMES[0]))
        failure = RuntimeError("synthetic callback failure")
        def fail(**kw):
            raise failure
        try:
            module.annotate_entry_policy_fields(**values, facade=types.SimpleNamespace(build_monitor_commander_memory_application_trace=fail))
        except RuntimeError as exc:
            assert exc is failure
        else:
            raise AssertionError("callback exception swallowed")
        assert "monitor_memory_bias_observed_deltas" in values["entry_info"]
        assert "commander_memory_application_trace" not in values["entry_info"]
        outcomes.append(values)
    assert outcomes[0] == outcomes[1]


@pytest.mark.parametrize("optimized", (False, True))
def test_m008_body_and_extra_effect_corruptions_fail_closed(optimized, tmp_path):
    code = '''
import sys,ast
sys.path.insert(0,sys.argv[1]);import work_monitor_current_tree as T
path='libs/runtime/monitor/entry_candidate_annotation.py';target=T.BODY_MOVES[path]['owner'];src=(T.ROOT/path).read_text(encoding='utf-8');owner=(T.ROOT/target).read_text(encoding='utf-8')
def reject(s,o):
 try:T.verified_current_source(path,source=s,owners={target:o})
 except AssertionError:return
 raise RuntimeError('false PASS')
reject(src+'\\nraise RuntimeError()\\n',owner)
reject(src,owner.replace('facade.build_monitor_commander_memory_application_trace','facade.execute_order'))
reject(src,owner.replace('return None','return entry_info',1))
reject(src,owner+'\\nimport os\\n')
print('4 rejected')
'''
    result = subprocess.run([sys.executable] + (["-O"] if optimized else []) + ["-c", code, str(ROOT / "scripts/refactor")], cwd=tmp_path, env=dict(os.environ), text=True, encoding="utf-8", capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "4 rejected"
