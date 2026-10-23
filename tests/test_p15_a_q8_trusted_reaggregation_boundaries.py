"""P1.5 DEV-A Q8 trusted reaggregation: ownership, ABI, effect and import boundaries of the new pure owner."""
from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.q8_trusted_reaggregation_projection_p15 as owner
import libs.reporting.q8_trusted_reaggregation as facade

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PRIOR = "3151be9f4262e2967338aadb0446a57351aa3956"
OWNER = "libs/reporting/evaluation/q8_trusted_reaggregation_projection_p15.py"
FACADE = "libs/reporting/q8_trusted_reaggregation.py"
EFFECT_NAMES = {"open", "print", "exec", "eval", "__import__", "input"}
EFFECT_ATTRS = {"read_text", "read_bytes", "write_text", "write_bytes", "mkdir", "exists", "glob", "unlink", "now",
                "utcnow", "today", "time", "getenv", "environ", "system", "popen", "dumps", "dump", "loads", "load"}
# quant_shadow_candidate_evaluation.py is a writable facade in the later approved quant-shadow readout packet (its decision
# logic is pinned by test_p15_a_q8_quant_shadow_readout_boundaries.py)
READ_ONLY = ("libs/reporting/q8_evaluation_contract.py", "libs/reporting/evaluation/__init__.py")
ALLOWED_CHANGES = {
    OWNER, FACADE,
    "tests/test_p15_a_q8_trusted_reaggregation_parity.py",
    "tests/test_p15_a_q8_trusted_reaggregation_boundaries.py",
    "tests/test_p15_a_q8_reporting_boundaries.py",  # exact path-only companion admission
    "tests/test_work_reporter_seed_migration.py",  # exact path-only companion admission
    "libs/reporting/alpha_research_board/builder.py",  # large-first Reporter wave (Tech Lead 6337591262)
    "libs/reporting/alpha_research_board/candidate_rows.py",
    "libs/reporting/alpha_research_board/board_assembly.py",
    "tests/test_p15_a_alpha_research_board_parity.py",
    "tests/test_p15_a_alpha_research_board_boundaries.py",
    "libs/reporting/evaluation/full_chain_component_review.py",  # large-first Reporter wave (Tech Lead 6335586418 / 6335924810)
    "libs/reporting/evaluation/full_chain_review_parts/__init__.py",
    "libs/reporting/evaluation/full_chain_review_parts/root_cause.py",
    "libs/reporting/evaluation/full_chain_review_parts/attribution.py",
    "libs/reporting/evaluation/full_chain_review_parts/component_decisions.py",
    "libs/reporting/evaluation/full_chain_review_parts/render.py",
    "tests/test_p15_a_full_chain_review_parity.py",
    "tests/test_p15_a_full_chain_review_boundaries.py",
    "libs/reporting/quant_shadow_candidate_evaluation.py",  # later approved Q8 packets (same branch)
    "libs/reporting/evaluation/quant_shadow_forward_readout_p15.py",
    "libs/reporting/evaluation/quant_shadow_render_p15.py",
    "tests/test_p15_a_q8_quant_shadow_readout_parity.py",
    "tests/test_p15_a_q8_quant_shadow_readout_boundaries.py",
    "libs/reporting/reporter_ai_review.py",  # wave A1 (Tech Lead 6335586418)
    "libs/reporting/reporter_ai_review_parts/__init__.py",
    "libs/reporting/reporter_ai_review_parts/prompting.py",
    "libs/reporting/reporter_ai_review_parts/compact_input.py",
    "libs/reporting/reporter_ai_review_parts/result_shaping.py",
    "libs/reporting/reporter_ai_review_parts/review_resolution.py",
    "tests/test_p15_a_reporter_ai_review_parity.py",
    "tests/test_p15_a_reporter_ai_review_boundaries.py",
    "libs/reporting/evaluation/quant_shadow_observation_projection_p15.py",
    "tests/test_p15_a_q8_quant_shadow_observation_parity.py",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.json",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.md",
}


def _git(*args) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8")


def _tree(path: str) -> ast.Module:
    return ast.parse((ROOT / path).read_text(encoding="utf-8"))


def test_owner_imports_only_stdlib_typing():
    imported = set()
    for node in ast.walk(_tree(OWNER)):
        if isinstance(node, ast.ImportFrom):
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert imported == {"__future__", "typing"}


def test_owner_has_no_io_clock_env_serialization_or_loader_inputs():
    found = []
    for node in ast.walk(_tree(OWNER)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in EFFECT_NAMES:
            found.append(node.func.id)
        if isinstance(node, ast.Attribute) and node.attr in EFFECT_ATTRS:
            found.append(node.attr)
        if isinstance(node, ast.arg) and node.arg in {"reports_root", "output_dir", "path", "payloads"}:
            found.append(node.arg)
    assert not found, found


def test_owner_reads_every_helper_and_trust_constant_through_the_facade():
    names = {n.id for n in ast.walk(_tree(OWNER)) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    forbidden = {"_iter_days", "load_quant_shadow_candidate_payloads", "build_quant_shadow_candidate_evaluation",
                 "TRUSTED_FORWARD_MIN_COUNT", "TRUSTED_FORWARD_MIN_COVERAGE", "DUPLICATE_RATE_MAX",
                 "PROMOTION_CANDIDATE_MIN_OBSERVED", "PROMOTION_CANDIDATE_MIN_DAYS"}
    assert not names & forbidden
    attrs = {n.attr for n in ast.walk(_tree(OWNER)) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "facade"}
    assert {"_fmt_pct", "_fmt_num", "_watchlist_rows", "TRUSTED_FORWARD_MIN_COUNT", "TRUSTED_FORWARD_MIN_COVERAGE",
            "DUPLICATE_RATE_MAX", "PROMOTION_CANDIDATE_MIN_OBSERVED", "PROMOTION_CANDIDATE_MIN_DAYS"} <= attrs


def test_owner_size_budget_and_facade_shrank():
    assert len((ROOT / OWNER).read_text(encoding="utf-8").splitlines()) <= 350
    base_lines = len(_git("show", f"{BASE_SHA}:{FACADE}").splitlines())
    assert len((ROOT / FACADE).read_text(encoding="utf-8").splitlines()) < base_lines // 2


def test_facade_keeps_every_base_name_and_signature():
    base_src = _git("show", f"{BASE_SHA}:{FACADE}")
    ns = types.ModuleType("_p15_q8_trusted_boundary_base")
    sys.modules[ns.__name__] = ns
    exec(compile(base_src, f"<base:{FACADE}>", "exec"), ns.__dict__)
    tree = ast.parse(base_src)
    names = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            names.add(node.name)
            assert str(inspect.signature(getattr(facade, node.name))) == str(inspect.signature(ns.__dict__[node.name])), node.name
        elif isinstance(node, ast.ImportFrom) and str(node.module).startswith("libs."):
            names.update(a.asname or a.name for a in node.names)
    assert not sorted(n for n in names if not hasattr(facade, n))
    for const in ("TRUSTED_FORWARD_MIN_COUNT", "TRUSTED_FORWARD_MIN_COVERAGE", "DUPLICATE_RATE_MAX",
                  "PROMOTION_CANDIDATE_MIN_OBSERVED", "PROMOTION_CANDIDATE_MIN_DAYS"):
        assert getattr(facade, const) == ns.__dict__[const]


def test_leaves_are_owner_objects_and_seam_wrappers_live_in_the_facade():
    for name in ("_fmt_pct", "_fmt_num", "_watchlist_rows"):
        assert getattr(facade, name) is getattr(owner, name)
    for name in ("render_q8_trusted_reaggregation_markdown", "build_q8_trusted_reaggregation", "write_q8_trusted_reaggregation", "_iter_days"):
        assert getattr(facade, name).__module__ == facade.__name__


def test_effects_stay_in_the_facade():
    defined = {n.name for n in _tree(FACADE).body if isinstance(n, ast.FunctionDef)}
    assert {"_iter_days", "build_q8_trusted_reaggregation", "write_q8_trusted_reaggregation"} <= defined
    called = {n.func.id for n in ast.walk(_tree(FACADE)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert {"load_quant_shadow_candidate_payloads", "build_quant_shadow_candidate_evaluation"} <= called
    src = (ROOT / FACADE).read_text(encoding="utf-8")
    assert "json.dumps(payload, ensure_ascii=False, indent=2)" in src and src.count("write_text(") == 2


def test_trust_policy_and_inputs_are_read_only_since_base():
    assert _git("diff", "--name-only", BASE_SHA, "--", *READ_ONLY).split() == []


def test_changes_since_accepted_checkpoint_stay_inside_the_allowlist():
    changed = set(_git("diff", "--name-only", PRIOR).split())
    changed |= set(_git("ls-files", "--others", "--exclude-standard", "--", "libs", "tests", "docs").split())
    assert changed <= ALLOWED_CHANGES, sorted(changed - ALLOWED_CHANGES)


@pytest.mark.parametrize("first", ["libs.reporting.q8_trusted_reaggregation", "libs.reporting.evaluation.pipeline",
                                   "libs.reporting.evaluation.q8_trusted_reaggregation_projection_p15"])
def test_fresh_import_has_no_cycle_and_writes_nothing(tmp_path, first):
    code = (
        "import importlib\n"
        f"importlib.import_module({first!r})\n"
        "importlib.import_module('libs.reporting.q8_trusted_reaggregation')\n"
        "print('OK')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run([sys.executable, *(["-O"] if sys.flags.optimize else []), "-c", code], cwd=tmp_path,
                          env=env, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert proc.stdout.strip() == "OK" and list(tmp_path.iterdir()) == []
