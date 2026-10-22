"""P1.5 DEV-A (large-first Reporter wave): ownership, ABI, effect-order and import boundaries of the alpha research board split."""
from __future__ import annotations

import ast
import builtins
import inspect
import os
import subprocess
import symtable
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.alpha_research_board.builder as facade

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PRIOR = "fbcf2b003472f487ff21c7abac36b6415264435a"
PKG = "libs/reporting/alpha_research_board/"
FACADE = PKG + "builder.py"
OWNERS = {PKG + "candidate_rows.py": {"__future__", "typing"}, PKG + "board_assembly.py": {"__future__", "typing"}}
MOVED = {"_candidate", "_q12_hypothesis_metric", "_feature_candidates", "_fresh_change", "_opening_rows", "_broad_opening", "_latent", "_btc_woori",
         "_attention_order"}
# stay in the facade: file reads / globbing (_prospective_concentrations), daily artifact reads (_large_cap_candidate), all writes
UNMOVED_IDENTICAL = {"_prospective_concentrations", "_large_cap_candidate", "write_alpha_research_board"}
# every call that reads files, builds a review from files, consults the clock or canonicalizes: their order inside the orchestrator is the contract
EFFECT_CALLS = ("load_json", "_prospective_concentrations", "build_risk_high_sensitivity", "_large_cap_candidate", "build_remaining_candidate_reviews",
                "build_short_alpha_discriminator", "build_immediate_opening_runtime_validation", "canonicalize_board", "now", "exists")
EFFECT_NAMES = {"open", "print", "exec", "eval", "__import__", "input"}
EFFECT_ATTRS = {"read_text", "read_bytes", "write_text", "write_bytes", "mkdir", "exists", "glob", "unlink", "now", "utcnow", "today", "time", "getenv",
                "environ", "system", "popen", "dump", "load", "loads", "dumps"}
UNTOUCHED = (PKG + "contracts.py", PKG + "canonical.py", PKG + "loaders.py", PKG + "report.py", PKG + "sensitivity.py", PKG + "remaining_reviews.py",
             PKG + "runtime_validation.py", PKG + "large_cap_review.py", PKG + "__init__.py", "libs/reporting/short_alpha_discriminator",
             "libs/reporting/evaluation/daily_uef_pipeline.py", "libs/reporting/closeout_maintenance.py", "scripts/research/run_alpha_research_board.py")
ALLOWED_CHANGES = {
    FACADE, *OWNERS,
    "tests/test_p15_a_alpha_research_board_parity.py", "tests/test_p15_a_alpha_research_board_boundaries.py",
    "tests/test_work_reporter_seed_migration.py",  # exact path-only companion admission
    "tests/test_p15_a_full_chain_review_boundaries.py", "tests/test_p15_a_reporter_ai_review_boundaries.py", "tests/test_p15_a_q8_reporting_boundaries.py",
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


def _global_reads(path: str, name: str) -> set:
    source = (ROOT / path).read_text(encoding="utf-8-sig")
    table = next(c for c in symtable.symtable(source, path, "exec").get_children() if c.get_name() == name)
    found = set()

    def walk(t):
        found.update(s.get_name() for s in t.get_symbols() if s.is_global() and s.is_referenced())
        for child in t.get_children():
            walk(child)

    walk(table)
    return {n for n in found if not hasattr(builtins, n)}


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_imports_only_stdlib_typing(path):
    imported = set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.ImportFrom):
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert imported == OWNERS[path]


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_is_effect_free_and_has_no_loader_or_path_input(path):
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
        if isinstance(node, ast.arg) and node.arg in {"reports_root", "output_dir", "path"}:
            found.append(node.arg)
    assert not found, found
    assert not names & {"load_json", "Path", "datetime", "build_risk_high_sensitivity", "build_remaining_candidate_reviews", "canonicalize_board",
                        "build_short_alpha_discriminator", "build_large_cap_daily_review"}, names


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_reads_module_names_only_through_the_facade_and_stays_in_budget(path):
    for name, fn in _functions(_tree(path)).items():
        reads = _global_reads(path, name)
        if name.endswith("_impl"):
            assert fn.args.kwonlyargs and fn.args.kwonlyargs[-1].arg == "facade", name
        assert not reads, (name, reads)  # every module-level name is read as facade.<name> (an attribute), or is a typing annotation
    assert len((ROOT / path).read_text(encoding="utf-8").splitlines()) <= 350


def test_facade_shrank_and_keeps_all_file_and_clock_effects():
    base_lines = len(_git("show", f"{BASE_SHA}:{FACADE}").splitlines())
    now_lines = len((ROOT / FACADE).read_text(encoding="utf-8").splitlines())
    assert now_lines < base_lines * 0.6, (base_lines, now_lines)
    source = (ROOT / FACADE).read_text(encoding="utf-8")
    for needle in ("datetime.now(timezone.utc)", ".glob(", "write_text(", "mkdir(", "load_json(", "canonicalize_board("):
        assert needle in source, needle


def _effect_sequence(tree: ast.Module) -> list:
    fn = _functions(tree)["build_alpha_research_board"]
    calls = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            target = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if target in EFFECT_CALLS:
                calls.append((node.lineno, node.col_offset, target))
    return [name for _l, _c, name in sorted(calls)]


def test_orchestrator_keeps_the_exact_order_of_every_read_build_clock_and_canonicalize_call():
    base_tree = ast.parse(_git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿"))
    expected = _effect_sequence(base_tree)
    actual = _effect_sequence(_tree(FACADE))
    assert expected and actual == expected, (expected, actual)
    assert expected.count("load_json") == 2 and expected[-1] == "canonicalize_board" and "now" in expected


def test_effect_order_check_detects_a_swapped_or_missing_call():
    expected = _effect_sequence(ast.parse(_git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿")))
    source = (ROOT / FACADE).read_text(encoding="utf-8-sig")
    reviews = "    remaining_reviews = build_remaining_candidate_reviews("
    short = "    short_alpha_review = build_short_alpha_discriminator("
    assert source.count(reviews) == 1 and source.count(short) == 1
    # swap the two builders' relative position by renaming the first to a call that appears later in the function
    swapped = source.replace(reviews, "    _early = build_short_alpha_discriminator(reports_root=reports_root, through_day=through_day)\n" + reviews, 1)
    assert _effect_sequence(ast.parse(swapped)) != expected
    dropped = source.replace("    return canonicalize_board(", "    return dict(", 1)
    assert _effect_sequence(ast.parse(dropped)) != expected


def test_facade_keeps_every_base_name_signature_and_constant():
    base_src = _git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿")
    ns = types.ModuleType(f"libs.reporting.alpha_research_board._p15_boundary_base")
    ns.__package__ = "libs.reporting.alpha_research_board"
    sys.modules[ns.__name__] = ns
    exec(compile(base_src, f"<base:{FACADE}>", "exec"), ns.__dict__)
    for node in ast.parse(base_src).body:
        if isinstance(node, ast.FunctionDef):
            assert hasattr(facade, node.name), node.name
            assert str(inspect.signature(getattr(facade, node.name))) == str(inspect.signature(ns.__dict__[node.name])), node.name
        elif isinstance(node, (ast.ImportFrom, ast.Import)):
            for alias in node.names:
                assert hasattr(facade, (alias.asname or alias.name).split(".")[0]), alias.name
    for const in ("SCHEMA_VERSION", "LIVE_RESEARCH_COST_PCT", "SETTLED_FINDINGS", "SOURCE_PATHS", "TRACKS"):
        assert getattr(facade, const) is ns.__dict__[const] or getattr(facade, const) == ns.__dict__[const], const


def test_unmoved_functions_are_ast_identical_and_moved_names_are_thin_facade_wrappers():
    base_funcs = _functions(ast.parse(_git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿")))
    cur_funcs = _functions(_tree(FACADE))
    assert MOVED | UNMOVED_IDENTICAL | {"build_alpha_research_board"} == set(base_funcs)
    assert set(base_funcs) <= set(cur_funcs)
    for name in UNMOVED_IDENTICAL:
        assert ast.dump(cur_funcs[name]) == ast.dump(base_funcs[name]), name
    source = (ROOT / FACADE).read_text(encoding="utf-8")
    for name in MOVED:
        node = cur_funcs[name]
        segment = ast.get_source_segment(source, node)
        assert len(node.body) == 1 and isinstance(node.body[0], ast.Return), name
        assert f"{name}_impl(" in segment and "facade=_sys.modules[__name__]" in segment, name
        assert getattr(facade, name).__module__ == facade.__name__


def test_contracts_canonicalization_siblings_and_uef_consumers_are_untouched_since_base():
    assert _git("diff", "--name-only", BASE_SHA, "--", *UNTOUCHED).split() == []


def test_changes_since_previous_checkpoint_stay_inside_the_allowlist():
    changed = set(_git("diff", "--name-only", PRIOR).split())
    changed |= set(_git("ls-files", "--others", "--exclude-standard", "--", "libs", "tests", "docs").split())
    assert changed <= ALLOWED_CHANGES, sorted(changed - ALLOWED_CHANGES)


@pytest.mark.parametrize("first", [
    "libs.reporting.alpha_research_board", "libs.reporting.alpha_research_board.builder", "libs.reporting.alpha_research_board.candidate_rows",
    "libs.reporting.alpha_research_board.board_assembly", "libs.reporting.alpha_research_board.canonical",
    "libs.reporting.evaluation.daily_uef_pipeline", "libs.reporting.closeout_maintenance",
])
def test_fresh_import_has_no_cycle_and_wrappers_resolve(tmp_path, first):
    code = (
        "import importlib\n"
        f"importlib.import_module({first!r})\n"
        "m = importlib.import_module('libs.reporting.alpha_research_board.builder')\n"
        "assert m._attention_order([{'candidate_id': 'b', 'board_bucket': 'CLOSED'}, {'candidate_id': 'a', 'board_bucket': 'ACTION_REVIEW'}]) == ['a', 'b']\n"
        "assert m._candidate(candidate_id='x', track_id='t', discriminator='d', target_horizon='h', source_status='s', board_bucket='b', owner='o', evidence_note='e', next_action='n', source_keys=[])['candidate_id'] == 'x'\n"
        "assert callable(m.build_alpha_research_board) and callable(m.write_alpha_research_board)\n"
        "print('OK')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run([sys.executable, *(["-O"] if sys.flags.optimize else []), "-c", code], cwd=tmp_path,
                          env=env, capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert proc.stdout.strip() == "OK" and list(tmp_path.iterdir()) == []
