"""Reporter whole-role project: relocated pure owners under ``libs/agents/reporter`` with strict identity shims.

Per registered module (offline, no Broker/LLM/network/production reads): body byte-identical to the pinned runtime BASE
blob, legacy shim passes the strict source-AST verifier (hard-coded mapping) and rejects mutations, one module object in
every import order, shared objects/late-bound monkeypatch, exactly one body, <=350 LOC, and BASE-first replay cases
(results, exception types, key order, mutation and alias flags) reproduced through BOTH paths.
"""
import gzip
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
BASE = "d773709ba2f70471fad9badba4f92400f7818319"  # pinned runtime BASE (blobs, replay)
START = "eeb742a33b16f6271ff364a904e187b470561c7e"  # activation commit (docs only over BASE); scope diff origin
FIX = ROOT / "tests" / "fixtures" / "work_reporter" / "seed_cases.json.gz"
# legacy module -> (canonical subpackage, pinned BASE blob)
REGISTRY = {
    "narrative_axes": ("narrative", "8eee2c502ed8f1646c0008e7979a6c438a01972a"),
    "trade_fallback_text": ("narrative", "de225b4556c9780ec84a7a3ee321c8659aea9373"),
    "reasoning_trace": ("narrative", "0807b9f3a94238f73c7617e1e0e8d8f514e9e676"),
    "trade_execution_outcome_text": ("narrative", "ca7ff430a44cea2dcbf2a1a1b3adccde13b354c1"),
    "chart_structure_decision_hint_summary": ("read_models", "16a5d887bc3a49efb6280cb6ea1693f9c3255949"),
    "policy_surface_summary": ("read_models", "4a3aa078fefa2e83fac1d0b610a2b667befb851c"),
    "report_metadata": ("read_models", "d0fffd0097d55f37d1038bf20bb79bd8780ed654"),
    "trade_reporter_status_text": ("narrative", "ce3578e8d2e6e7036a9f1f48085516a73905fca3"),
    "truth_source_labels": ("narrative", "5a30f3df03c13468b8c81e083212d4063fd0ea0d"),
    "trade_pnl_estimate": ("read_models", "614f79242d78f4cdd536062bc0f0fe49c067c9ba"),
}
REPORTER_PACKAGES = {"narrative", "read_models"}  # exact, versioned by this project (shared allowlist is Work-owned)
OLD, NEW = "libs.reporting.{}", "libs.agents.reporter.{}.{}"

_spec = importlib.util.spec_from_file_location("_wave_b_gate_reporter", ROOT / "tests" / "test_p154_wave_b_moved_bodies.py")
WB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WB)


def _blob(data):
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _run(code):
    return subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), check=True, capture_output=True, text=True,
                          env={**os.environ, "PYTHONPATH": str(ROOT)}).stdout.strip()


def _paths(name):
    sub = REGISTRY[name][0]
    return f"libs/reporting/{name}.py", f"libs/agents/reporter/{sub}/{name}.py"


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_body_is_byte_identical_to_the_pinned_base_blob(name):
    _, canonical = _paths(name)
    data = (ROOT / canonical).read_bytes().replace(b"\r\n", b"\n")
    assert _blob(data) == REGISTRY[name][1]
    assert len(data.decode("utf-8").splitlines()) <= 350


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_shim_passes_the_strict_ast_verifier_and_rejects_mutations(name):
    legacy, canonical = _paths(name)
    sub = REGISTRY[name][0]
    good = (ROOT / legacy).read_text(encoding="utf-8")
    assert WB._verify_identity_shim_source(good, legacy, canonical) == canonical
    other = next(n for n in sorted(REGISTRY) if n != name)
    for bad in (good + "\nraise RuntimeError(1)\n", good + "\nimport subprocess\n",
                good.replace(f"{sub} import {name}", f"{sub} import {other}"),
                good.replace(f"libs.agents.reporter.{sub}", "libs.agents.reporter.context"),
                good.replace("as _canonical", "as canonical"), good.replace("import sys as _sys", "import sys")):
        with pytest.raises(AssertionError):
            WB._verify_identity_shim_source(bad, legacy, canonical)


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_old_and_new_paths_are_one_module_object_in_every_import_order(name):
    sub = REGISTRY[name][0]
    o, n = OLD.format(name), NEW.format(sub, name)
    assert _run(f"import importlib; a=importlib.import_module('{o}'); b=importlib.import_module('{n}'); print(a is b)") == "True"
    assert _run(f"import importlib; b=importlib.import_module('{n}'); a=importlib.import_module('{o}'); print(a is b)") == "True"
    assert _run(f"from libs.reporting import {name} as a; from libs.agents.reporter.{sub} import {name} as b; "
                f"import libs.reporting as p; print(a is b and p.{name} is b)") == "True"


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_objects_signatures_and_use_time_monkeypatch_are_shared(name, monkeypatch):
    sub = REGISTRY[name][0]
    old, new = importlib.import_module(OLD.format(name)), importlib.import_module(NEW.format(sub, name))
    assert old is new
    funcs = [k for k, v in vars(new).items() if inspect.isfunction(v) and v.__module__ == new.__name__]
    assert funcs
    for k in funcs:
        assert getattr(old, k) is getattr(new, k)
    marker = object()
    monkeypatch.setattr(old, funcs[0], marker)
    assert getattr(new, funcs[0]) is marker


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_shim_has_no_code_and_exactly_one_body_exists(name):
    sub = REGISTRY[name][0]
    new = importlib.import_module(NEW.format(sub, name))
    legacy, canonical = _paths(name)
    funcs = [k for k, v in vars(new).items() if inspect.isfunction(v) and v.__module__ == new.__name__]
    sources = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8", errors="replace")
               for p in list((ROOT / "libs").rglob("*.py")) + list((ROOT / "graphs").rglob("*.py"))}
    unique = 0
    for fn in funcs:  # names that were defined ONLY in this module at BASE must now be defined ONLY in the canonical body
        base = subprocess.run(["git", "grep", "-l", f"def {fn}(", BASE, "--", "libs", "graphs"], cwd=ROOT,
                              capture_output=True, text=True).stdout.split()
        base = {x.split(":", 1)[1] for x in base}
        assert legacy in base
        if base != {legacy}:
            continue
        unique += 1
        assert {p for p, s in sources.items() if f"def {fn}(" in s} == {canonical}, fn
    assert unique >= 1


def test_recorded_base_cases_are_reproduced_exactly_through_both_paths():
    doc = json.loads(gzip.decompress(FIX.read_bytes()))
    cases = doc["cases"]
    assert len(cases) == 1216
    sys.path.insert(0, str(ROOT / "scripts" / "refactor"))
    try:
        import work_reporter_capture as cap
    finally:
        sys.path.pop(0)
    assert {c["mod"] for c in cases} == {OLD.format(n) for n in REGISTRY} == set(cap.MODULES)
    got = cap.compute()  # drives the LEGACY import path of every module
    assert json.dumps(got, ensure_ascii=False, separators=(",", ":")) == json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    # canonical path: same module objects, so same functions
    for n, (sub, _b) in REGISTRY.items():
        assert importlib.import_module(OLD.format(n)) is importlib.import_module(NEW.format(sub, n))


def test_target_tree_discipline_and_no_forbidden_surface():
    base = ROOT / "libs/agents/reporter"
    assert {p.name for p in base.iterdir() if p.is_dir() and p.name != "__pycache__"} == REPORTER_PACKAGES
    for sub in REPORTER_PACKAGES:
        assert sorted(p.name for p in (base / sub).glob("*.py")) == \
            sorted(["__init__.py"] + [f"{n}.py" for n, (s, _b) in REGISTRY.items() if s == sub]), sub
    out = [x for x in subprocess.check_output(["git", "diff", "--name-only", "-z", START, "HEAD"], cwd=ROOT).decode().split(chr(0)) if x]
    allowed_exact = {f"libs/reporting/{n}.py" for n in REGISTRY}
    allowed_prefix = ("libs/agents/reporter/", "tests/test_work_reporter_", "tests/fixtures/work_reporter/",
                      "scripts/refactor/work_reporter_", "docs/refactor/work_projects/evidence/reporter/",
                      "docs/refactor/work_projects/")
    for p in out:
        assert p in allowed_exact or p.startswith(allowed_prefix), p
