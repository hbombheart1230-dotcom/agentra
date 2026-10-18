"""Worker-owned Monitor relocation proof; existing shared gates remain untouched."""
import ast
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
SPEC = importlib.util.spec_from_file_location("work_monitor_contracts", ROOT / "scripts/refactor/work_monitor_contracts.py")
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)
MAPS = C.ledger()["maps"]
FROZEN = json.loads(C.FIXTURE.read_text(encoding="utf-8"))
START = "eeb742a33b16f6271ff364a904e187b470561c7e"


def _module(path):
    return path[:-3].replace("/", ".")


def _shim(row):
    parent, name = _module(row["destination"]).rsplit(".", 1)
    return f"import sys as _sys\nfrom {parent} import {name} as _canonical\n_sys.modules[__name__] = _canonical\n"


def _statements(source):
    body = ast.parse(source).body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    return ast.dump(ast.Module(body=body, type_ignores=[]), include_attributes=False)


@pytest.mark.parametrize("row", MAPS, ids=lambda r: Path(r["source"]).stem)
def test_whole_base_blob_and_exact_shim(row):
    source = C.git_bytes(row["source"])
    canonical = (ROOT / row["destination"]).read_bytes().replace(b"\r\n", b"\n")
    assert canonical == source
    blob = hashlib.sha1(b"blob " + str(len(canonical)).encode() + b"\0" + canonical).hexdigest()
    assert blob == row["base_blob"]
    assert _statements((ROOT / row["source"]).read_text(encoding="utf-8")) == _statements(_shim(row))
    assert len(canonical.splitlines()) <= 350
    tree = ast.parse(canonical)
    assert all(not isinstance(n, ast.Import) for n in tree.body)
    assert all(n.module == "__future__" for n in tree.body if isinstance(n, ast.ImportFrom))
    for name in row["symbols"]:
        assert inspect.signature(getattr(C.base_module(row), name)) == inspect.signature(
            getattr(importlib.import_module(_module(row["destination"])), name))


@pytest.mark.parametrize("old_first", [True, False], ids=["old-first", "new-first"])
@pytest.mark.parametrize("row", MAPS, ids=lambda r: Path(r["source"]).stem)
def test_fresh_process_module_package_private_identity_and_bidirectional_patch(row, old_first, tmp_path):
    old, new = _module(row["source"]), _module(row["destination"])
    first, second = (old, new) if old_first else (new, old)
    code = """
import importlib,sys
first,second,old,new=sys.argv[1:]
a=importlib.import_module(first); b=importlib.import_module(second)
if a is not b or sys.modules[old] is not sys.modules[new]: raise AssertionError('module identity')
for path in (old,new):
    parent,name=path.rsplit('.',1)
    if getattr(importlib.import_module(parent),name) is not a: raise AssertionError('package identity')
marker=object(); a._work_private_marker=marker
if b._work_private_marker is not marker: raise AssertionError('private patch')
b.work_public_marker=marker
if a.work_public_marker is not marker: raise AssertionError('reverse public patch')
for name,obj in vars(a).items():
    if getattr(b,name) is not obj: raise AssertionError(name)
"""
    run = tmp_path / "child"
    run.mkdir()
    env = dict(os.environ, TEMP=str(run), TMP=str(run), PYTHONPYCACHEPREFIX=str(run / "pycache"), PYTHONPATH=str(ROOT))
    result = subprocess.run([sys.executable, "-c", code, first, second, old, new], cwd=run,
                            env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("optimized", [False, True], ids=["normal", "python-O"])
def test_shared_strict_verifier_rejects_extra_import_raise_and_wrong_target(optimized, tmp_path):
    # Call the existing verifier without editing it or importing a candidate shim.
    code = """
import importlib.util,json,sys
from pathlib import Path
r=Path(sys.argv[1]); d=json.loads((r/'docs/refactor/work_projects/evidence/monitor/path_ledger.json').read_text())
s=importlib.util.spec_from_file_location('wb',r/'tests/test_p154_wave_b_moved_bodies.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
count=0
for row in d['maps']:
    src=(r/row['source']).read_text(); dst=row['destination']
    m._verify_identity_shim_source(src,row['source'],dst)
    for bad in (src+'\\nimport os\\n',src+'\\nraise RuntimeError()\\n',src.replace('= _canonical','= object()')):
        try: m._verify_identity_shim_source(bad,row['source'],dst)
        except AssertionError: count+=1
        else: raise RuntimeError('fail-open strict shim verifier')
if count!=33: raise RuntimeError(count)
print(count)
"""
    env = dict(os.environ, TEMP=str(tmp_path), TMP=str(tmp_path), PYTHONPYCACHEPREFIX=str(tmp_path / "pycache"),
               PYTHONPATH=str(ROOT))
    args = [sys.executable] + (["-O"] if optimized else [])
    proc = subprocess.run(args + ["-c", code, str(ROOT)], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip() == "33"


def test_frozen_inventory_and_baseline_provenance_are_fail_closed():
    assert FROZEN["base_sha"] == C.BASE
    assert FROZEN["producer"]["tool_sha256"] == hashlib.sha256(Path(C.__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    expected = set()
    for row in MAPS:
        data = C.git_bytes(row["source"])
        assert FROZEN["source_sha256"][row["source"]] == hashlib.sha256(data).hexdigest()
        base = C.base_module(row)
        for name in row["symbols"]:
            for variant, _inp in C.cases_for(getattr(base, name)):
                expected.add(Path(row["source"]).stem + ":" + name + ":" + variant)
    records = FROZEN["records"]
    assert len(records) == len(expected) == 108
    assert {r["id"] for r in records} == expected
    assert {r["source"] for r in records} == {r["source"] for r in MAPS}
    assert C.FIXTURE.stat().st_size < 256 * 1024


@pytest.mark.parametrize("record", FROZEN["records"], ids=lambda r: r["id"])
def test_frozen_result_exception_key_order_mutation_alias_and_callback_order(record):
    row = next(r for r in MAPS if r["source"] == record["source"])
    fn = getattr(importlib.import_module(_module(row["destination"])), record["function"])
    assert C.observe(fn, record["input"]) == record["expected"]


def test_fixture_recomputes_only_from_immutable_base_not_feature():
    for row in MAPS:
        base = C.base_module(row)
        for r in (r for r in FROZEN["records"] if r["source"] == row["source"]):
            assert C.observe(getattr(base, r["function"]), r["input"]) == r["expected"]


def test_use_time_facade_binding_and_existing_input_mutation():
    row = next(r for r in MAPS if r["source"].endswith("/signal_explanation.py"))
    fn = getattr(importlib.import_module(_module(row["destination"])), row["symbols"][0])
    kw = C.default_kwargs(fn)
    facade = C.StubFacade()
    kw["score_breakdown"] = {"a": 0.0}
    trace = kw["grouped_logic_trace"]
    assert fn(**kw, facade=facade) is None
    assert trace is kw["grouped_logic_trace"] and trace["score_passed"] is False
    facade._to_float = lambda value: 10.0
    assert fn(**kw, facade=facade) is None
    assert trace["score_passed"] is True


def test_handoff_mutates_exact_callback_result_and_preserves_nested_alias():
    mod = importlib.import_module("libs.agents.monitor.projections.scanner_monitor_handoff_projection")
    fn = mod.build_scanner_monitor_handoff_for_cycle
    kw = C.default_kwargs(fn)
    callback_result = {"shared": []}
    facade = C.StubFacade()
    facade.build_scanner_monitor_handoff_surface = lambda **kwargs: callback_result
    result = fn(**kw, facade=facade)
    assert result is callback_result
    assert list(result) == ["shared", "monitor_selected_symbol", "entry_candidate_cascade"]
    assert result["entry_candidate_cascade"] is not kw["entry_candidate_cascade"]


def test_all_retained_role_owners_and_protected_runtime_stay_byte_identical():
    spec = importlib.util.spec_from_file_location("monitor_current_tree", ROOT / "scripts/refactor/work_monitor_current_tree.py")
    current = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(current)
    for row in C.ledger()["responsibility_register"]:
        if "base_blob" not in row or row["disposition"] == "MOVE":
            continue
        data = current.verified_current_source(row["path"]).encode("utf-8")
        assert data == C.git_bytes(row["path"]), row["path"]
    paths = ["graphs", "apps", "libs/execution", "libs/kiwoom", "libs/llm", "libs/risk", "libs/supervisor",
             "libs/agents/scanner", "libs/agents/strategist", "libs/runtime/scanner", "libs/runtime/strategist",
             "libs/reporting", ".github", "sitecustomize.py", "conftest.py", "tests/fixtures/p1_5_t4b_monitor"]
    sys.path.insert(0, str(ROOT / "scripts/refactor"))
    import shared_role_contracts as shared
    assert subprocess.check_output(["git", "diff", "--name-only", START, shared.MONITOR, "--", *paths], cwd=ROOT).strip() == b""
    # S5.current_contract supplies only the exact two Owners + node, gated by
    # an independently evidenced admission pin; all other paths stay protected.
    shared.verify_runtime()
