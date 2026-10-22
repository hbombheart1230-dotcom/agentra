"""P1.5 DEV-A Q8: ownership, ABI and effect boundaries of the three Q8 pure owners.

Owners must stay stdlib/contract-only and effect-free; facades keep every BASE module-level name,
public signature, file read/write, clock-free loader call and the AST-pinned closeout functions.
"""
from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.q8_historical_aggregation_p15 as agg_owner
import libs.reporting.evaluation.q8_historical_render_p15 as render_owner
import libs.reporting.evaluation.q8_shadow_readout_p15 as readout_owner
import libs.reporting.q8_historical_review as hist
import libs.reporting.q8_lane_decision_table as lane
import libs.reporting.q8_shadow_blocker_review as shadow

ROOT = Path(__file__).resolve().parents[1]
BASE = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PRIOR = "e3dca2a08601fc90a63eb3ec84fb85d39d4848e1"
OWNERS = {
    "libs/reporting/evaluation/q8_historical_aggregation_p15.py": {"__future__", "collections", "dataclasses", "typing"},
    "libs/reporting/evaluation/q8_historical_render_p15.py": {"__future__", "typing"},
    "libs/reporting/evaluation/q8_shadow_readout_p15.py": {"__future__", "typing"},
}
FACADES = {
    "libs/reporting/q8_historical_review.py": hist,
    "libs/reporting/q8_shadow_blocker_review.py": shadow,
    "libs/reporting/q8_lane_decision_table.py": lane,
}
EFFECT_NAMES = {"open", "print", "exec", "eval", "__import__", "input"}
EFFECT_ATTRS = {"read_text", "read_bytes", "write_text", "write_bytes", "mkdir", "exists", "glob", "unlink",
                "now", "utcnow", "today", "time", "getenv", "environ", "system", "popen"}
# quant_shadow_candidate_evaluation.py left this list when the later approved quant-shadow readout packet made it a writable
# facade; its decision logic is pinned by the AST-identity check in test_p15_a_q8_quant_shadow_readout_boundaries.py
READ_ONLY = ("libs/reporting/q8_evaluation_contract.py",
             "libs/reporting/quant_shadow_forward_outcomes.py", "libs/runtime/quant/vwap_reclaim_observation.py",
             "libs/reporting/evaluation/__init__.py")
ALLOWED_CHANGES = set(OWNERS) | set(FACADES) | {
    "tests/test_p15_a_q8_historical_pure_parity.py",
    "tests/test_p15_a_q8_reporting_boundaries.py",
    "tests/test_work_reporter_seed_migration.py",  # approved: exact Q8 path registration in the Reporter scope gate
    "libs/reporting/q8_trusted_reaggregation.py",
    "libs/reporting/evaluation/q8_trusted_reaggregation_projection_p15.py",
    "tests/test_p15_a_q8_trusted_reaggregation_parity.py",
    "tests/test_p15_a_q8_trusted_reaggregation_boundaries.py",
    "libs/reporting/quant_shadow_candidate_evaluation.py",
    "libs/reporting/evaluation/quant_shadow_forward_readout_p15.py",
    "libs/reporting/evaluation/quant_shadow_render_p15.py",
    "tests/test_p15_a_q8_quant_shadow_readout_parity.py",
    "tests/test_p15_a_q8_quant_shadow_readout_boundaries.py",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.json",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.md",
}


def _git(*args) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8")


def _tree(path: str) -> ast.Module:
    return ast.parse((ROOT / path).read_text(encoding="utf-8"))


def _top_names(tree: ast.Module) -> set:
    """Own definitions plus project (``libs.*``) imports; stdlib helper imports are not facade ABI."""
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.ImportFrom) and str(node.module).startswith("libs."):
            names.update(a.asname or a.name for a in node.names)
    return names


def _exec_base(path: str, src: str):
    name = "_p15_q8_boundary_base_" + Path(path).stem
    module = types.ModuleType(name)
    sys.modules[name] = module
    exec(compile(src, f"<base:{path}>", "exec"), module.__dict__)
    return module.__dict__


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_imports_are_stdlib_or_read_only_contract(path):
    imported = set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.ImportFrom):
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert imported == OWNERS[path]


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_has_no_io_clock_env_or_dynamic_code(path):
    found = []
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in EFFECT_NAMES:
            found.append(node.func.id)
        if isinstance(node, ast.Attribute) and node.attr in EFFECT_ATTRS:
            found.append(node.attr)
        if isinstance(node, ast.arg) and node.arg in {"reports_root", "docs_root", "path"}:
            found.append(node.arg)
    assert not found, (path, found)


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_size_budget(path):
    assert len((ROOT / path).read_text(encoding="utf-8").splitlines()) <= 350


@pytest.mark.parametrize("path", sorted(FACADES))
def test_facade_keeps_every_base_name_public_api_and_signature(path):
    base_src = _git("show", f"{BASE}:{path}")
    base_tree = ast.parse(base_src)
    module = FACADES[path]
    missing = sorted(name for name in _top_names(base_tree) if not hasattr(module, name))
    assert not missing, missing
    base_ns = _exec_base(path, base_src)
    assert module.__all__ == base_ns["__all__"]
    for node in base_tree.body:  # every BASE function/class, private ones included, keeps its call signature
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            assert str(inspect.signature(getattr(module, node.name))) == str(inspect.signature(base_ns[node.name])), node.name


# BASE names whose bodies call other BASE helpers are facade-defined wrappers (patchable seams, owner impl gets
# ``facade=``); helper-free leaves and the accumulator classes are the owner objects re-exported unchanged.
WRAPPERS = {
    hist: ("_pct_from_ratio", "_decision_for_reclaim_subtype", "_aggregate_return_rows", "render_q8_historical_review_markdown"),
    shadow: ("_checkpoint_values", "_decision_for_row", "_summarize_group"),
    lane: ("_forward_rows", "_counts_by_name", "_reason_summary", "_verdict", "build_q8_lane_decision_table"),
}
LEAVES = {
    hist: (agg_owner, ("GroupAccumulator", "ForwardAccumulator", "_float", "_int", "_text", "_avg", "_weighted_avg")),
    shadow: (readout_owner, ("_text", "_to_float", "_bool", "_avg")),
    lane: (readout_owner, ("_rows", "_float", "_int", "_text")),
}


def test_seam_wrappers_live_in_facades_and_leaves_are_reexported_owner_objects():
    for module, names in WRAPPERS.items():
        for name in names:
            assert getattr(module, name).__module__ == module.__name__, (module.__name__, name)
    for module, (owner, names) in LEAVES.items():
        for name in names:
            assert getattr(module, name) is getattr(owner, name), (module.__name__, name)
    assert getattr(hist, "_md_table") is render_owner._md_table
    import libs.reporting.q8_evaluation_contract as contract

    assert lane.TRUSTED_FORWARD_MIN_COVERAGE is contract.TRUSTED_FORWARD_MIN_COVERAGE
    assert not hasattr(readout_owner, "TRUSTED_FORWARD_MIN_COVERAGE")  # read only through the facade


def test_effects_and_pinned_closeout_functions_stay_in_facades():
    defined = {path: {n.name for n in _tree(path).body if isinstance(n, ast.FunctionDef)} for path in FACADES}
    assert {"_read_json", "_write_json", "_write_md", "_iter_days", "_iter_quant_shadow_candidate_rows", "_extract_trade_rows",
            "_daily_summary_rows", "_aggregate_shadow_summaries", "_pattern_rows_from_daily_summaries",
            "build_q8_historical_review_payload", "write_q8_historical_review"} <= defined["libs/reporting/q8_historical_review.py"]
    # test_closeout_payload_projection.py pins these two by AST in this exact file
    assert {"_candidate_rows", "generate_q8_shadow_blocker_review", "build_q8_shadow_blocker_review",
            "render_q8_shadow_blocker_review_markdown"} <= defined["libs/reporting/q8_shadow_blocker_review.py"]
    assert {"build_q8_lane_decision_table", "render_q8_lane_decision_table_markdown", "write_q8_lane_decision_table",
            "_fmt_pct"} <= defined["libs/reporting/q8_lane_decision_table.py"]
    owner_defs = set().union(*({n.name for n in _tree(p).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))} for p in OWNERS))
    assert not owner_defs & {"_candidate_rows", "build_q8_shadow_blocker_review", "build_q8_lane_decision_table"}


def test_trust_gate_and_inputs_are_read_only_since_base():
    changed = _git("diff", "--name-only", BASE, "--", *READ_ONLY).split()
    assert changed == []


def test_changes_since_prior_checkpoint_stay_inside_the_q8_allowlist():
    changed = set(_git("diff", "--name-only", PRIOR).split())
    changed |= set(_git("ls-files", "--others", "--exclude-standard", "--", "libs", "tests", "docs").split())
    assert changed <= ALLOWED_CHANGES, sorted(changed - ALLOWED_CHANGES)


@pytest.mark.parametrize("first", [
    "libs.reporting.q8_historical_review", "libs.reporting.q8_shadow_blocker_review", "libs.reporting.q8_lane_decision_table",
    "libs.reporting.evaluation.cumulative_improvement_review", "libs.reporting.operator_period_summary",
])
def test_fresh_import_has_no_cycle_and_writes_nothing(tmp_path, first):
    code = (
        "import importlib, sys\n"
        f"importlib.import_module({first!r})\n"
        "for m in ('libs.reporting.q8_historical_review', 'libs.reporting.q8_shadow_blocker_review', 'libs.reporting.q8_lane_decision_table'):\n"
        "    importlib.import_module(m)\n"
        "print('OK')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run([sys.executable, *(["-O"] if sys.flags.optimize else []), "-c", code], cwd=tmp_path,
                          env=env, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert proc.stdout.strip() == "OK"
    assert list(tmp_path.iterdir()) == []
