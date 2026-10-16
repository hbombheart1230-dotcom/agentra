"""V3-055: five Scanner read-only projection modules relocated to `libs/agents/scanner/projections` with identity shims.

Per module (offline, no Broker/LLM/network): body byte-identical to the pinned BASE blob (line-ending normalized), the
shim passes the same strict source-AST verifier used for the V2 shims (hard-coded mapping, never read from the shim),
old/new imports are one module object in every import order (fresh interpreters), shared objects, use-time monkeypatch,
exactly one body, and the Scanner node binding. 218 cases (caller inputs recorded on the pinned BASE tree while the
existing Scanner/quant/Q9 tests ran, plus edge inputs) must be reproduced exactly, including JSON key order.
"""
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
BASE = "9735c81c29f5aaf2b98a44a03b9c73e30b473f19"
FIX = ROOT / "tests" / "fixtures" / "p1_5_v3055_scanner_projections" / "cases.json"
MODULES = {
    "candidate_context_projection": "15fd6fc26a511cf648d886e9c7668e8b019f13e0",
    "control_eligibility": "d47013045a37b97a6a1b5d50e067934b628d3251",
    "output_payloads": "fe5e34d58aecb7972adc02e0faa8c89eeb8555f0",
    "output_snapshots": "02ef48a408338fcb010e82241ef2c694b039979e",
    "selection_evidence_projection": "bf20e9af5ec4988e7fef831b0cbb3e44644f6914",
}
OLD, NEW = "libs.runtime.scanner.{}", "libs.agents.scanner.projections.{}"
_spec = importlib.util.spec_from_file_location("_wave_b_gate_v3", ROOT / "tests" / "test_p154_wave_b_moved_bodies.py")
WB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WB)


def _blob(data):
    import hashlib
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _run(code):
    return subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), check=True, capture_output=True, text=True,
                          env={**os.environ, "PYTHONPATH": str(ROOT)}).stdout.strip()


@pytest.mark.parametrize("name,blob", sorted(MODULES.items()))
def test_body_is_byte_identical_to_the_pinned_base_blob(name, blob):
    data = (ROOT / f"libs/agents/scanner/projections/{name}.py").read_bytes().replace(b"\r\n", b"\n")
    assert _blob(data) == blob


@pytest.mark.parametrize("name", sorted(MODULES))
def test_shim_passes_the_strict_ast_verifier_and_rejects_mutations(name):
    legacy, canonical = f"libs/runtime/scanner/{name}.py", f"libs/agents/scanner/projections/{name}.py"
    good = (ROOT / legacy).read_text(encoding="utf-8")
    assert WB._verify_identity_shim_source(good, legacy, canonical) == canonical
    for bad in (good + "\nraise RuntimeError(1)\n", good + "\nimport subprocess\n",
                good.replace(f"projections import {name}", "projections import control_eligibility" if name != "control_eligibility" else "projections import output_payloads"),
                good.replace("libs.agents.scanner.projections", "libs.agents.scanner.context")):
        with pytest.raises(AssertionError):
            WB._verify_identity_shim_source(bad, legacy, canonical)


@pytest.mark.parametrize("name", sorted(MODULES))
def test_old_and_new_paths_are_one_module_object_in_every_import_order(name):
    o, n = OLD.format(name), NEW.format(name)
    assert _run(f"import importlib; a=importlib.import_module('{o}'); b=importlib.import_module('{n}'); print(a is b)") == "True"
    assert _run(f"import importlib; b=importlib.import_module('{n}'); a=importlib.import_module('{o}'); print(a is b)") == "True"
    assert _run(f"from libs.runtime.scanner import {name} as a; from libs.agents.scanner.projections import {name} as b; "
                f"import libs.runtime.scanner as p; print(a is b and p.{name} is b)") == "True"


@pytest.mark.parametrize("name", sorted(MODULES))
def test_objects_signatures_and_use_time_monkeypatch_are_shared(name, monkeypatch):
    old, new = importlib.import_module(OLD.format(name)), importlib.import_module(NEW.format(name))
    assert old is new
    funcs = [k for k, v in vars(new).items() if inspect.isfunction(v) and v.__module__ == new.__name__]
    assert funcs
    for k in funcs:
        assert getattr(old, k) is getattr(new, k)
    marker = object()
    monkeypatch.setattr(old, funcs[0], marker)
    assert getattr(new, funcs[0]) is marker


@pytest.mark.parametrize("name", sorted(MODULES))
def test_shim_has_no_code_and_exactly_one_body_exists(name):
    new = importlib.import_module(NEW.format(name))
    first = next(k for k, v in vars(new).items() if inspect.isfunction(v) and v.__module__ == new.__name__)
    base = subprocess.run(["git", "grep", "-l", f"def {first}(", BASE, "--", "libs", "graphs"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split()
    base = {x.split(":", 1)[1] for x in base}
    hits = {p.relative_to(ROOT).as_posix() for p in list((ROOT / "libs").rglob("*.py")) + list((ROOT / "graphs").rglob("*.py"))
            if f"def {first}(" in p.read_text(encoding="utf-8", errors="replace")}
    assert hits == (base - {f"libs/runtime/scanner/{name}.py"}) | {f"libs/agents/scanner/projections/{name}.py"}, hits
    assert f"libs/runtime/scanner/{name}.py" in base


def test_scanner_node_binds_the_canonical_functions():
    import ast
    node = importlib.import_module("graphs.nodes.scanner_node")
    tree = ast.parse((ROOT / "graphs/nodes/scanner_node.py").read_text(encoding="utf-8-sig"))
    bound = 0
    for imp in [n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("libs.runtime.scanner.")]:
        name = imp.module.rsplit(".", 1)[1]
        if name not in MODULES:
            continue
        new = importlib.import_module(NEW.format(name))
        for alias in imp.names:
            assert getattr(node, alias.asname or alias.name) is getattr(new, alias.name), alias.name
            bound += 1
    assert bound >= 10


def test_recorded_base_cases_are_reproduced_exactly_through_both_paths():
    doc = json.loads(FIX.read_text(encoding="utf-8"))
    assert len(doc["cases"]) == 218 and doc["base_commit"] == BASE
    for path in (OLD, NEW):
        for case in doc["cases"]:
            fn = getattr(importlib.import_module(path.format(case["mod"])), case["fn"])
            try:
                got = {"ok": json.loads(json.dumps(fn(*json.loads(json.dumps(case["args"])),
                                                       **json.loads(json.dumps(case["kwargs"]))), ensure_ascii=False, default=repr))}
            except Exception as exc:  # noqa: BLE001
                got = {"exc": type(exc).__name__, "msg": str(exc)[:160]}
            assert got == case["result"], (path, case["fn"])
            assert json.dumps(got, ensure_ascii=False) == json.dumps(case["result"], ensure_ascii=False), (case["fn"], "key order")


def test_target_tree_discipline_and_no_forbidden_surface():
    assert sorted(p.name for p in (ROOT / "libs/agents/scanner/projections").glob("*.py")) == \
        sorted(["__init__.py"] + [f"{m}.py" for m in MODULES])
    import p15_agent_tree_allowlist as AL
    assert AL.actual_dirs(ROOT / "libs/agents") == set(AL.AGENT_PACKAGES)
    assert AL.actual_dirs(ROOT / "libs/agents/scanner") == set(AL.SCANNER_PACKAGES)  # exact, versioned ownership
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", BASE, "HEAD"], cwd=ROOT).decode().split(chr(0))
    forbidden = ("graphs/nodes/scanner_node.py", "graphs/nodes/execute_from_packet.py", "graphs/commander_runtime.py",
                 "libs/execution/", "libs/supervisor/", "libs/approval/", "libs/risk/", "libs/llm/", "libs/kiwoom/",
                 "libs/runtime/commander/", "apps/", "config/", "deploy/",
                 "libs/runtime/scanner/selection_output_projection.py", "libs/runtime/scanner/score_feature_projection.py",
                 "libs/runtime/scanner/score_policy_projection.py", "libs/runtime/scanner/theme_filter.py",
                 "libs/runtime/scanner/practical_filters.py", "libs/agents/scanner/candidate_risk.py", "libs/agents/scanner/context/")
    for p in [x for x in out if x]:
        assert not p.startswith(forbidden), p


def test_t3_current_owner_gate_follows_only_exact_verified_shims(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("_p159_gate", ROOT / "tests" / "test_p159_current_owner_contract_gates.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    assert set(gate.V3_SHIM_ALLOWLIST) == {"libs/runtime/scanner/candidate_context_projection.py",
                                           "libs/runtime/scanner/selection_evidence_projection.py"}
    for legacy, canonical in gate.V3_SHIM_ALLOWLIST.items():
        assert gate._follow(legacy) == canonical
    assert gate._follow("libs/runtime/scanner/output_payloads.py") == "libs/runtime/scanner/output_payloads.py"
    legacy = "libs/runtime/scanner/candidate_context_projection.py"
    good = (ROOT / legacy).read_text(encoding="utf-8")
    for bad in (good + "\nraise RuntimeError(123)\n", good + "\nimport subprocess\n",
                good.replace("projections import candidate_context_projection", "projections import control_eligibility")):
        fake = tmp_path / "root"
        (fake / legacy).parent.mkdir(parents=True, exist_ok=True)
        (fake / legacy).write_text(bad, encoding="utf-8")
        monkeypatch.setattr(gate, "ROOT", fake)
        with pytest.raises(AssertionError):
            gate._follow(legacy)
