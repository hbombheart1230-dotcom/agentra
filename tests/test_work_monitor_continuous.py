"""Continuous Monitor gates: exact scope, BASE bytes, real read callbacks, negatives."""
import ast
import copy
import hashlib
import importlib
import importlib.util
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
import work_monitor_continuous_replay as R

FROZEN = json.loads(R.FIXTURE.read_text(encoding="utf-8"))
PAIRS = list(T.WHOLE_MOVES.items())


@pytest.mark.parametrize("old,new", PAIRS, ids=[Path(a).stem for a, _ in PAIRS])
def test_m001_base_blob_signatures_import_authority_and_exact_three_statement_shim(old, new):
    source = T.verified_current_source(old)
    assert source == T.base_source(old)
    data = source.encode("utf-8")
    assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == \
        subprocess.check_output(["git", "rev-parse", f"{T.BASE}:{old}"], cwd=ROOT, text=True).strip()
    assert len(source.splitlines()) <= 350
    tree = ast.parse(source)
    assert all(n.module in ("__future__", "typing") for n in tree.body if isinstance(n, ast.ImportFrom))
    assert not any(isinstance(n, ast.Import) for n in tree.body)
    mod = importlib.import_module(new[:-3].replace("/", "."))
    baseline = R.baseline_module(old)
    for n in tree.body:
        if isinstance(n, ast.FunctionDef):
            assert inspect.signature(getattr(mod, n.name)) == inspect.signature(getattr(baseline, n.name))


@pytest.mark.parametrize("old,new", PAIRS, ids=[Path(a).stem for a, _ in PAIRS])
@pytest.mark.parametrize("order", ("old-first", "new-first"))
def test_m001_fresh_import_package_private_identity_patch_and_pickle(old, new, order, tmp_path):
    old, new = old[:-3].replace("/", "."), new[:-3].replace("/", ".")
    code = """
import importlib,inspect,pickle,sys
old,new,order=sys.argv[1:]
a,b=(old,new) if order=='old-first' else (new,old)
x=importlib.import_module(a);y=importlib.import_module(b)
if x is not y:raise AssertionError('identity')
for p in (old,new):
 parent,name=p.rsplit('.',1)
 if getattr(importlib.import_module(parent),name) is not x:raise AssertionError('package identity')
marker=object();x._private_probe=marker
if y._private_probe is not marker:raise AssertionError('private patch')
y.public_probe=marker
if x.public_probe is not marker:raise AssertionError('reverse patch')
for name,value in vars(x).items():
 if getattr(y,name) is not value:raise AssertionError(name)
 if inspect.isfunction(value) and value.__module__==x.__name__:
  if pickle.loads(pickle.dumps(value)) is not value:raise AssertionError('canonical pickle')
  legacy_pickle=b'c'+old.encode()+b'\\n'+name.encode()+b'\\n.'
  if pickle.loads(legacy_pickle) is not value:raise AssertionError('legacy pickle')
"""
    env = dict(os.environ, PYTHONPATH=str(ROOT), TEMP=str(tmp_path), TMP=str(tmp_path),
               PYTHONPYCACHEPREFIX=str(tmp_path / "pycache"))
    result = subprocess.run([sys.executable, "-c", code, old, new, order], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("optimized", (False, True))
def test_m001_shim_and_canonical_body_mutations_fail_closed_even_python_O(optimized, tmp_path):
    code = """
import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1]+'/scripts/refactor')
import work_monitor_current_tree as t
count=0
for old,new in t.WHOLE_MOVES.items():
 good=(t.ROOT/old).read_text(encoding='utf-8');t.strict_shim(good,old,new)
 for bad in (good+'\\nimport os\\n',good+'\\nraise RuntimeError()\\n',good.replace('= _canonical','= object()')):
  try:t.verified_current_source(old,source=bad)
  except AssertionError:count+=1
  else:raise RuntimeError('bad shim passed')
 try:t.verified_current_source(old,owners={new:t.base_source(old)+'\\nextra = 1\\n'})
 except AssertionError:count+=1
 else:raise RuntimeError('changed canonical body passed')
try:t.strict_shim('','libs/runtime/unknown.py','libs/agents/monitor/projections/unknown.py')
except AssertionError:count+=1
else:raise RuntimeError('unregistered pair passed')
if count!=13:raise RuntimeError(count)
print(count)
"""
    env = dict(os.environ, TEMP=str(tmp_path), TMP=str(tmp_path), PYTHONPYCACHEPREFIX=str(tmp_path / "pycache"))
    result = subprocess.run([sys.executable] + (["-O"] if optimized else []) + ["-c", code, str(ROOT)],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "13"


def test_m001_fixture_exact_inventory_and_producer_provenance():
    assert FROZEN["BASE"] == T.BASE
    assert FROZEN["producer_source_sha256"] == hashlib.sha256(Path(R.__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    expected = set()
    for old, _new in PAIRS:
        assert FROZEN["source_sha256"][old] == hashlib.sha256(T.base_source(old).encode()).hexdigest()
        base = R.baseline_module(old)
        for fn in (n.name for n in ast.parse(T.base_source(old)).body if isinstance(n, ast.FunctionDef)):
            for variant, _inp in R.inputs_for(fn, getattr(base, fn)):
                expected.add(Path(old).stem + ":" + fn + ":" + variant)
    assert len(FROZEN["records"]) == len(expected) == 59
    assert {r["id"] for r in FROZEN["records"]} == expected
    assert R.FIXTURE.stat().st_size < 256 * 1024


def test_retained_graph_utf8_bom_is_preserved_not_stripped_by_the_proof():
    path = "graphs/nodes/monitor_node.py"
    actual = T.verified_current_source(path).encode("utf-8")
    expected = subprocess.check_output(["git", "show", f"{T.BASE}:{path}"], cwd=ROOT)
    assert actual == expected
    assert actual.startswith(b"\xef\xbb\xbf") == expected.startswith(b"\xef\xbb\xbf")


@pytest.mark.parametrize("record", FROZEN["records"], ids=lambda r: r["id"])
def test_m001_results_key_order_exceptions_input_aliases_and_real_callback_order(record):
    new = T.WHOLE_MOVES[record["legacy"]]
    mod = importlib.import_module(new[:-3].replace("/", "."))
    assert R.observe(getattr(mod, record["function"]), record["input"]) == record["expected"]


def test_m001_private_monkeypatch_before_and_mid_call_and_threshold_alias_are_unchanged():
    # Compare real call order as the converter replaces itself mid-call.
    old = "libs/runtime/monitor_exit/order_lifecycle.py"
    current = importlib.import_module(T.WHOLE_MOVES[old][:-3].replace("/", "."))
    results = []
    for mod in (R.baseline_module(old), current):
        calls = []
        original = mod._to_int
        def first(value):
            calls.append(["first", value])
            mod._to_int = lambda v: calls.append(["next", v]) or int(v)
            return int(value)
        try:
            mod._to_int = first
            result = mod.derive_order_lifecycle({"filled_qty": 1, "order_qty": 3, "remaining_qty": 2})
            results.append((result, calls))
        finally:
            mod._to_int = original
    assert results[0] == results[1]
    payload = importlib.import_module("libs.agents.monitor.projections.observability")
    kw = {k: {} for k in inspect.signature(payload.build_monitor_exit_payload).parameters}
    nested = {"stop_loss_pct": 0.02, "nested": []}
    kw["decision"] = {"thresholds": nested}
    out = payload.build_monitor_exit_payload(**kw)
    assert out["thresholds"] is nested
    assert out["final_exit_thresholds"] is not nested
    assert out["final_exit_thresholds"]["nested"] is nested["nested"]
    out["thresholds"]["nested"].append(1)
    assert kw["decision"]["thresholds"]["nested"] == [1]
