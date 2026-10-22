"""P1.5 DEV-A Q8: ownership, red-line, ABI and import boundaries of the quant-shadow forward readout and render owners."""
from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.quant_shadow_candidate_evaluation as facade

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PRIOR = "21a58fb09bc879e3b1a06098cc029b3c855e147e"
FACADE = "libs/reporting/quant_shadow_candidate_evaluation.py"
OWNERS = {
    "libs/reporting/evaluation/quant_shadow_forward_readout_p15.py": {"__future__", "collections", "typing"},
    "libs/reporting/evaluation/quant_shadow_render_p15.py": {"__future__", "typing"},
    "libs/reporting/evaluation/quant_shadow_observation_projection_p15.py": {"__future__", "collections", "typing"},
}
# BASE functions that moved into the owners (facade keeps a same-name, same-signature wrapper); `_mean` stays put
MOVED = {"_checkpoint_value", "_forward_outcome_summary", "_top_forward_groups", "_entry_lane_forward_outcomes",
         "_format_rows", "_format_forward_rows", "_format_scorecard_rows", "render_quant_shadow_candidate_evaluation_lines",
         # wave A-W1 (Tech Lead 6335238675): observation shape / diagnostic projections
         "_entry_shape", "_entry_shape_payload", "_below_vwap_reclaim_observation", "_below_vwap_reclaim_observation_payload",
         "_entry_lane_observation", "_entry_lane_observation_payload"}
RED_LINE = {"_evaluation_trust_gate", "_promotion_candidate", "_no_trade_scorecard", "_dedupe_candidates", "_shadow_readiness",
            "build_quant_shadow_candidate_evaluation", "_scorecard_rows", "_named_forward_rows", "_scorecard_return_signal"}
EFFECT_NAMES = {"open", "print", "exec", "eval", "__import__", "input"}
EFFECT_ATTRS = {"read_text", "read_bytes", "write_text", "write_bytes", "mkdir", "exists", "glob", "unlink", "now", "utcnow",
                "today", "time", "getenv", "environ", "system", "popen", "dumps", "dump", "loads", "load"}
READ_ONLY = ("libs/reporting/q8_evaluation_contract.py", "libs/reporting/quant_shadow_forward_outcomes.py",
             "libs/runtime/quant/entry_lane_observation.py", "libs/runtime/quant/vwap_reclaim_observation.py",
             "libs/reporting/evaluation/__init__.py")
ALLOWED_CHANGES = {
    FACADE, *OWNERS,
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
    "tests/test_p15_a_q8_reporting_boundaries.py",  # exact path-only companion admission
    "tests/test_p15_a_q8_trusted_reaggregation_boundaries.py",  # drops the facade from its read-only list (now writable)
    "tests/test_work_reporter_seed_migration.py",  # exact path-only companion admission
    "libs/reporting/evaluation/full_chain_component_review.py",  # large-first Reporter wave (Tech Lead 6335586418 / 6335924810)
    "libs/reporting/evaluation/full_chain_review_parts/__init__.py",
    "libs/reporting/evaluation/full_chain_review_parts/root_cause.py",
    "libs/reporting/evaluation/full_chain_review_parts/attribution.py",
    "libs/reporting/evaluation/full_chain_review_parts/component_decisions.py",
    "libs/reporting/evaluation/full_chain_review_parts/render.py",
    "tests/test_p15_a_full_chain_review_parity.py",
    "tests/test_p15_a_full_chain_review_boundaries.py",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.json",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.md",
}


def _git(*args) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8")


def _tree(path: str) -> ast.Module:
    return ast.parse((ROOT / path).read_text(encoding="utf-8"))


def _functions(tree: ast.Module) -> dict:
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_imports_only_stdlib(path):
    imported = set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.ImportFrom):
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert imported == OWNERS[path]


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_has_no_io_clock_env_serialization_or_loader_inputs(path):
    found = []
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in EFFECT_NAMES:
            found.append(node.func.id)
        if isinstance(node, ast.Attribute) and node.attr in EFFECT_ATTRS:
            found.append(node.attr)
        if isinstance(node, ast.arg) and node.arg in {"reports_root", "path", "payloads", "root"}:
            found.append(node.arg)
    assert not found, found


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_calls_only_facade_helpers_and_stays_within_budget(path):
    tree = _tree(path)
    loads = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    own = set(_functions(tree))
    forbidden = {n for n in loads if n.startswith("_") and n not in own and n not in {"__name__"}}
    assert not forbidden, forbidden
    assert all(a.arg == "facade" for f in _functions(tree).values() for a in f.args.kwonlyargs[-1:])
    assert len((ROOT / path).read_text(encoding="utf-8").splitlines()) <= 350


def test_facade_shrank_and_does_not_import_the_evaluation_package_at_module_level():
    base_lines = len(_git("show", f"{BASE_SHA}:{FACADE}").splitlines())
    assert len((ROOT / FACADE).read_text(encoding="utf-8").splitlines()) < base_lines - 300
    modules = [n.module for n in _tree(FACADE).body if isinstance(n, ast.ImportFrom)]
    # libs/reporting/evaluation/__init__ imports pipeline -> full_chain_component_review -> this facade: a top-level owner
    # import here would be an import cycle, so the wrappers import their owner at call time
    assert not [m for m in modules if str(m).startswith("libs.reporting.evaluation")]


def test_facade_keeps_every_base_name_signature_and_constant():
    base_src = _git("show", f"{BASE_SHA}:{FACADE}")
    ns = types.ModuleType("_p15_qsce_boundary_base")
    sys.modules[ns.__name__] = ns
    exec(compile(base_src, f"<base:{FACADE}>", "exec"), ns.__dict__)
    base_tree = ast.parse(base_src)
    for node in base_tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            assert hasattr(facade, node.name), node.name
            assert str(inspect.signature(getattr(facade, node.name))) == str(inspect.signature(ns.__dict__[node.name])), node.name
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assert getattr(facade, target.id) == ns.__dict__[target.id], target.id
        elif isinstance(node, ast.ImportFrom) and str(node.module).startswith("libs."):
            for alias in node.names:
                assert hasattr(facade, alias.asname or alias.name), alias.name


def test_red_line_and_every_unmoved_function_are_ast_identical_to_base():
    base_funcs = _functions(ast.parse(_git("show", f"{BASE_SHA}:{FACADE}")))
    cur_funcs = _functions(_tree(FACADE))
    assert RED_LINE <= set(base_funcs)
    assert set(cur_funcs) == set(base_funcs)
    for name, node in base_funcs.items():
        if name in MOVED:
            continue
        assert ast.dump(cur_funcs[name]) == ast.dump(node), name


def test_moved_names_are_thin_facade_wrappers_with_call_time_owner_import():
    for name in MOVED:
        node = _functions(_tree(FACADE))[name]
        assert node.__class__ is ast.FunctionDef and len(node.body) <= 3, name
        src = ast.get_source_segment((ROOT / FACADE).read_text(encoding="utf-8"), node)
        assert f"{name}_impl" in src and "facade=_sys.modules[__name__]" in src, name
        assert getattr(facade, name).__module__ == facade.__name__


def test_trust_policy_and_neighbours_are_read_only_since_base():
    assert _git("diff", "--name-only", BASE_SHA, "--", *READ_ONLY).split() == []


def test_changes_since_accepted_checkpoint_stay_inside_the_allowlist():
    changed = set(_git("diff", "--name-only", PRIOR).split())
    changed |= set(_git("ls-files", "--others", "--exclude-standard", "--", "libs", "tests", "docs").split())
    assert changed <= ALLOWED_CHANGES, sorted(changed - ALLOWED_CHANGES)


@pytest.mark.parametrize("first", [
    "libs.reporting.quant_shadow_candidate_evaluation", "libs.reporting.evaluation",
    "libs.reporting.evaluation.full_chain_component_review", "libs.reporting.evaluation.quant_shadow_render_p15",
    "libs.reporting.evaluation.quant_shadow_forward_readout_p15", "libs.reporting.q8_shadow_blocker_review",
    "libs.reporting.operator_period_summary",
])
def test_fresh_import_has_no_cycle_and_wrappers_resolve(tmp_path, first):
    code = (
        "import importlib\n"
        f"importlib.import_module({first!r})\n"
        "m = importlib.import_module('libs.reporting.quant_shadow_candidate_evaluation')\n"
        "assert m._format_rows([{'name': 'a', 'count': 1}]) == 'a (1)'\n"
        "assert m.render_quant_shadow_candidate_evaluation_lines({'candidate_count': 1})[1] == '## Quant Shadow Candidates'\n"
        "assert m._forward_outcome_summary([])['candidate_count'] == 0\n"
        "print('OK')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run([sys.executable, *(["-O"] if sys.flags.optimize else []), "-c", code], cwd=tmp_path,
                          env=env, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert proc.stdout.strip() == "OK" and list(tmp_path.iterdir()) == []
