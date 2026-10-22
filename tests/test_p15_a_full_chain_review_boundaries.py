"""P1.5 DEV-A (large-first Reporter wave): ownership, ABI, effect and import boundaries of full_chain_review_parts."""
from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.full_chain_component_review as facade

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PRIOR = "924d8180021356c2e6e70814b7c4c970a884fadf"
FACADE = "libs/reporting/evaluation/full_chain_component_review.py"
PARTS = "libs/reporting/evaluation/full_chain_review_parts/"
OWNERS = {
    PARTS + "root_cause.py": {"__future__", "typing"},
    PARTS + "attribution.py": {"__future__", "collections", "typing"},
    PARTS + "component_decisions.py": {"__future__", "typing"},
    PARTS + "render.py": {"__future__", "json", "typing"},
}
MOVED = {"_topk_metric", "_classify_root_cause", "_role_metrics", "_paired_role_deltas", "_selection_availability", "_q9_role_row",
         "_decision_window_attribution", "_attribution_component", "_scanner_decision", "_unavailable_component",
         "render_full_chain_component_review"}
# stay in the facade on purpose: _q9_decision_candidate_rows attaches forward outcomes (reads state), build/write are the orchestration and file I/O
UNMOVED_IDENTICAL = {"_number", "_behavior_metric_eligible", "_q9_decision_candidate_rows", "build_full_chain_component_review",
                     "write_full_chain_component_review"}
STDLIB_IN_OWNERS = {"Any", "Mapping", "defaultdict", "json"}
EFFECT_NAMES = {"open", "print", "exec", "eval", "__import__", "input"}
EFFECT_ATTRS = {"read_text", "read_bytes", "write_text", "write_bytes", "mkdir", "exists", "glob", "unlink", "now", "utcnow", "today",
                "time", "getenv", "environ", "system", "popen", "dump", "load", "loads"}
UNTOUCHED = ("libs/reporting/evaluation/contracts.py", "libs/reporting/evaluation/loss_decomposition.py", "libs/reporting/evaluation/scanner_quality.py",
             "libs/reporting/evaluation/metrics.py", "libs/reporting/evaluation/agent_effectiveness_scorecard.py",
             "libs/reporting/evaluation/stage2_authority", "libs/reporting/evaluation/daily_uef_pipeline.py", "libs/reporting/evaluation/uef5",
             "libs/reporting/evaluation/canonical", "libs/reporting/q8_evaluation_contract.py", "libs/reporting/quant_shadow_forward_outcomes.py",
             "libs/reporting/evaluation/__init__.py")
ALLOWED_CHANGES = {
    FACADE, PARTS + "__init__.py", *OWNERS,
    "tests/test_p15_a_full_chain_review_parity.py", "tests/test_p15_a_full_chain_review_boundaries.py",
    "tests/test_work_reporter_seed_migration.py",  # exact path-only companion admission
    "libs/reporting/alpha_research_board/builder.py",  # large-first Reporter wave (Tech Lead 6337591262)
    "libs/reporting/alpha_research_board/candidate_rows.py",
    "libs/reporting/alpha_research_board/board_assembly.py",
    "tests/test_p15_a_alpha_research_board_parity.py",
    "tests/test_p15_a_alpha_research_board_boundaries.py",
    "tests/test_p15_a_reporter_ai_review_boundaries.py", "tests/test_p15_a_q8_reporting_boundaries.py",
    "tests/test_p15_a_q8_trusted_reaggregation_boundaries.py", "tests/test_p15_a_q8_quant_shadow_readout_boundaries.py",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.json",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.md",
}


def _git(*args) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8")


def _tree(path: str) -> ast.Module:
    return ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))


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
def test_owner_is_effect_free_and_knows_no_loader_or_state(path):
    found, names = [], set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in EFFECT_NAMES:
            found.append(node.func.id)
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
            if node.attr in EFFECT_ATTRS:
                found.append(node.attr)
        if isinstance(node, ast.Name):
            names.add(node.id)
        if isinstance(node, ast.arg) and node.arg in {"reports_root", "output_dir", "path", "cost_profile_path"}:
            found.append(node.arg)
    assert not found, found
    assert not names & {"attach_forward_outcomes", "load_quant_shadow_candidate_payloads_for_range", "load_broker_cost_profile", "_load_trade_models",
                        "build_scanner_quality_review", "Path"}, names


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_reads_every_facade_name_through_the_facade_and_stays_in_budget(path):
    facade_names = set()
    for node in _tree(FACADE).body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            facade_names.update((a.asname or a.name).split(".")[0] for a in node.names)
        elif isinstance(node, ast.FunctionDef):
            facade_names.add(node.name)
        elif isinstance(node, ast.Assign):
            facade_names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    facade_names -= STDLIB_IN_OWNERS | {"annotations"}
    tree = _tree(path)
    bare = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} & facade_names
    assert not bare, bare
    for name, fn in _functions(tree).items():
        assert name.endswith("_impl") and fn.args.kwonlyargs and fn.args.kwonlyargs[-1].arg == "facade", name
    assert len((ROOT / path).read_text(encoding="utf-8").splitlines()) <= 350


def test_facade_shrank_and_keeps_orchestration_and_effects():
    base_lines = len(_git("show", f"{BASE_SHA}:{FACADE}").splitlines())
    now_lines = len((ROOT / FACADE).read_text(encoding="utf-8").splitlines())
    assert now_lines < base_lines * 0.55, (base_lines, now_lines)
    source = (ROOT / FACADE).read_text(encoding="utf-8")
    for needle in ("load_quant_shadow_candidate_payloads_for_range(", "load_broker_cost_profile(", "os.getenv(", "attach_forward_outcomes(", "write_text("):
        assert needle in source, needle


def test_facade_keeps_every_base_name_signature_and_constant():
    base_src = _git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿")
    ns = types.ModuleType("libs.reporting.evaluation._p15_full_chain_boundary_base")
    ns.__package__ = "libs.reporting.evaluation"
    sys.modules[ns.__name__] = ns
    exec(compile(base_src, f"<base:{FACADE}>", "exec"), ns.__dict__)
    for node in ast.parse(base_src).body:
        if isinstance(node, ast.FunctionDef):
            assert hasattr(facade, node.name), node.name
            assert str(inspect.signature(getattr(facade, node.name))) == str(inspect.signature(ns.__dict__[node.name])), node.name
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assert getattr(facade, target.id) == ns.__dict__[target.id], target.id
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert hasattr(facade, alias.asname or alias.name), alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                assert hasattr(facade, (alias.asname or alias.name).split(".")[0]), alias.name
    assert facade.DecisionClass is ns.DecisionClass or [m.value for m in facade.DecisionClass] == [m.value for m in ns.DecisionClass]


def test_unmoved_functions_are_ast_identical_and_moved_names_are_thin_facade_wrappers():
    base_funcs = _functions(ast.parse(_git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿")))
    cur_funcs = _functions(_tree(FACADE))
    assert set(cur_funcs) == set(base_funcs)
    assert MOVED | UNMOVED_IDENTICAL == set(base_funcs)
    for name in UNMOVED_IDENTICAL:
        assert ast.dump(cur_funcs[name]) == ast.dump(base_funcs[name]), name
    source = (ROOT / FACADE).read_text(encoding="utf-8")
    for name in MOVED:
        node = cur_funcs[name]
        segment = ast.get_source_segment(source, node)
        assert len(node.body) == 1 and isinstance(node.body[0], ast.Return), name
        assert f"{name}_impl(" in segment and "facade=_sys.modules[__name__]" in segment, name
        assert getattr(facade, name).__module__ == facade.__name__


def test_new_owners_keep_the_dropped_q9_row_key_contract():
    """The review opts in to dropping these Q9 row keys, so no module on its path may mention them (the existing source scan
    in test_closeout_memory_bounds only lists the facade, not the new owners)."""
    import re

    import libs.reporting.quant_shadow_candidate_evaluation as qsce

    assert qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN
    for path in [FACADE, *OWNERS]:
        text = (ROOT / path).read_text(encoding="utf-8")
        for key in qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN:
            assert not re.search(rf"""["']{key}["']""", text), (path, key)


def test_contract_consumers_and_trust_modules_are_untouched_since_base():
    assert _git("diff", "--name-only", BASE_SHA, "--", *UNTOUCHED).split() == []


def test_changes_since_previous_checkpoint_stay_inside_the_allowlist():
    changed = set(_git("diff", "--name-only", PRIOR).split())
    changed |= set(_git("ls-files", "--others", "--exclude-standard", "--", "libs", "tests", "docs").split())
    assert changed <= ALLOWED_CHANGES, sorted(changed - ALLOWED_CHANGES)


@pytest.mark.parametrize("first", [
    "libs.reporting.evaluation.full_chain_component_review", "libs.reporting.evaluation",
    "libs.reporting.evaluation.full_chain_review_parts.render", "libs.reporting.evaluation.full_chain_review_parts.attribution",
    "libs.reporting.evaluation.agent_effectiveness_scorecard", "libs.reporting.evaluation.stage2_authority.pipeline",
    "libs.reporting.evaluation.pipeline",
])
def test_fresh_import_has_no_cycle_and_wrappers_resolve(tmp_path, first):
    code = (
        "import importlib\n"
        f"importlib.import_module({first!r})\n"
        "m = importlib.import_module('libs.reporting.evaluation.full_chain_component_review')\n"
        "assert m._number('1.5') == 1.5 and m._topk_metric({}, top_k=1, horizon='+30m') == {}\n"
        "assert m.render_full_chain_component_review({}).startswith('#')\n"
        "assert m._unavailable_component(question='q', missing_comparison='m', availability={})['decision']\n"
        "print('OK')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run([sys.executable, *(["-O"] if sys.flags.optimize else []), "-c", code], cwd=tmp_path,
                          env=env, capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert proc.stdout.strip() == "OK" and list(tmp_path.iterdir()) == []
