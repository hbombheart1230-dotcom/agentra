"""V1-052 pilot: Scanner `candidate_risk` relocated to `libs/agents/scanner` with a module-identity shim.

Proves (offline, no Broker/LLM/IO): old/new import identity in both import orders (separate interpreters), byte-for-byte
body equality with the pinned BASE blob (line-ending normalized), exact frozen-output equality for 115 inputs executed
on the BASE body, use-time monkeypatch visibility through either path, the Scanner node consumer binding, a single
implementation and no rank owner added.
"""
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "p1_5_v1052_candidate_risk" / "cases.json"
OLD = "libs.runtime.scanner.candidate_risk"
NEW = "libs.agents.scanner.candidate_risk"
BASE_BLOB = "8dea30aebd811d8d9f214c8bca7bef8ea41fa3f9"


def _blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _run(code: str) -> str:
    return subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), check=True, capture_output=True, text=True,
                          env={**__import__("os").environ, "PYTHONPATH": str(ROOT)}).stdout.strip()


def test_body_is_byte_identical_to_the_pinned_base_blob():
    data = (ROOT / "libs/agents/scanner/candidate_risk.py").read_bytes().replace(b"\r\n", b"\n")
    assert _blob_sha1(data) == BASE_BLOB


def test_old_and_new_imports_are_the_same_module_object_in_both_orders():
    old_first = _run(f"import importlib; a=importlib.import_module('{OLD}'); b=importlib.import_module('{NEW}'); print(a is b)")
    new_first = _run(f"import importlib; b=importlib.import_module('{NEW}'); a=importlib.import_module('{OLD}'); print(a is b)")
    assert old_first == "True" and new_first == "True"
    pkg = _run("import libs.runtime.scanner.candidate_risk; import libs.runtime.scanner as p, "
               "libs.agents.scanner.candidate_risk as n; print(p.candidate_risk is n)")
    assert pkg == "True"
    from_form = _run("from libs.runtime.scanner import candidate_risk as a; "
                     "from libs.agents.scanner import candidate_risk as b; print(a is b)")
    assert from_form == "True"


def test_public_and_private_symbols_and_signature_are_shared():
    old, new = importlib.import_module(OLD), importlib.import_module(NEW)
    assert old is new
    for name in ("resolve_candidate_base_risk", "_optional_float", "_clamp", "_first_number"):
        assert getattr(old, name) is getattr(new, name)
    import inspect
    sig = inspect.signature(new.resolve_candidate_base_risk)
    assert list(sig.parameters) == ["candidate", "scanner_row", "features", "quote_metrics"]
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in sig.parameters.values())


def test_frozen_outputs_are_exactly_equal_for_every_case():
    doc = json.loads(FIX.read_text(encoding="utf-8"))
    assert doc["base_blob_sha1"] == BASE_BLOB and len(doc["cases"]) >= 100
    for old_path in (OLD, NEW):
        fn = importlib.import_module(old_path).resolve_candidate_base_risk
        for case in doc["cases"]:
            got = fn(**case["input"])
            assert got == case["output"], (old_path, case["input"])
            assert list(got) == list(case["output"]) and list(got["components"]) == list(case["output"]["components"])


def test_monkeypatch_is_use_time_and_visible_through_both_paths(monkeypatch):
    old, new = importlib.import_module(OLD), importlib.import_module(NEW)
    monkeypatch.setattr(old, "_clamp", lambda value, lower=0.0, upper=1.0: 0.5)
    assert new._clamp(9.0) == 0.5
    assert new.resolve_candidate_base_risk(scanner_row={"risk_score": 0.9})["risk_score"] == 0.5


def test_scanner_node_consumer_binds_the_canonical_function():
    node = importlib.import_module("graphs.nodes.scanner_node")
    new = importlib.import_module(NEW)
    assert node.resolve_candidate_base_risk is new.resolve_candidate_base_risk


def test_single_implementation_shim_without_code_and_no_rank_owner_added():
    shim = (ROOT / "libs/runtime/scanner/candidate_risk.py").read_text(encoding="utf-8")
    assert "def " not in shim and "resolve_candidate_base_risk" not in shim
    defs = []
    for p in list((ROOT / "libs").rglob("*.py")) + list((ROOT / "graphs").rglob("*.py")):
        if "def resolve_candidate_base_risk" in p.read_text(encoding="utf-8", errors="replace"):
            defs.append(p.relative_to(ROOT).as_posix())
    assert defs == ["libs/agents/scanner/candidate_risk.py"], defs
    names = sorted(p.name for p in (ROOT / "libs/agents/scanner").glob("*.py"))
    assert names == ["__init__.py", "candidate_risk.py"], names
    assert sorted(p.name for p in (ROOT / "libs/agents").iterdir() if p.is_dir() and p.name != "__pycache__") == ["scanner"]


def test_pilot_touches_no_forbidden_surface():
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", "860207682dc02080260e768587ac5f401f8c902a", "HEAD"],
                                  cwd=ROOT).decode().split(chr(0))
    forbidden = ("graphs/nodes/scanner_node.py", "graphs/nodes/execute_from_packet.py", "libs/execution/", "libs/supervisor/",
                 "libs/approval/", "libs/risk/", "libs/llm/", "libs/kiwoom/", "libs/runtime/commander/")
    for p in [x for x in out if x]:
        assert not p.startswith(forbidden), p
