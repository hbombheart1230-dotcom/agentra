"""P1.5 DEV-A (wave A1): ownership, ABI, effect and import boundaries of libs/reporting/reporter_ai_review_parts."""
from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.reporter_ai_review as facade

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PRIOR = "508b3e97bbae4070be6d8eba457f163741cf6526"
FACADE = "libs/reporting/reporter_ai_review.py"
PARTS = "libs/reporting/reporter_ai_review_parts/"
OWNERS = {
    PARTS + "prompting.py": {"__future__", "json", "typing"},
    PARTS + "compact_input.py": {"__future__", "typing"},
    PARTS + "result_shaping.py": {"__future__", "typing"},
    PARTS + "review_resolution.py": {"__future__", "typing"},
}
# BASE functions moved behind facade wrappers (same name, same signature, facade passed to the owner *_impl)
MOVED = {"_normalize_llm_status", "_clip_str", "_list_str", "_dict_str", "_normalize_evidence_link_items", "_normalize_result",
         "_default_result", "_build_compact_input", "_build_messages"}
UNMOVED_IDENTICAL = {"_env_bool", "_strip_fenced_block", "_extract_json_object"}
EFFECT_NAMES = {"open", "print", "exec", "eval", "__import__", "input"}
EFFECT_ATTRS = {"read_text", "read_bytes", "write_text", "write_bytes", "mkdir", "exists", "glob", "unlink", "now", "utcnow", "today",
                "time", "getenv", "environ", "system", "popen", "dump", "load", "loads"}
LLM_AND_LEDGER = {"LLMRouter", "record_raw_input", "record_llm_prompt", "record_llm_response", "resolve_policy_llm_slot",
                  "resolve_policy_llm_execution_slot", "build_execution_profile_observability", "normalize_openrouter_model_name",
                  "parse_llm_json_response"}
ALLOWED_CHANGES = {
    FACADE, "libs/reporting/reporter_ai_review_parts/__init__.py", *OWNERS,
    "tests/test_p15_a_reporter_ai_review_parity.py", "tests/test_p15_a_reporter_ai_review_boundaries.py",
    "tests/test_work_reporter_seed_migration.py",  # exact path-only companion admission
    "libs/reporting/evaluation/full_chain_component_review.py",  # large-first Reporter wave (Tech Lead 6335586418 / 6335924810)
    "libs/reporting/evaluation/full_chain_review_parts/__init__.py",
    "libs/reporting/evaluation/full_chain_review_parts/root_cause.py",
    "libs/reporting/evaluation/full_chain_review_parts/attribution.py",
    "libs/reporting/evaluation/full_chain_review_parts/component_decisions.py",
    "libs/reporting/evaluation/full_chain_review_parts/render.py",
    "tests/test_p15_a_full_chain_review_parity.py",
    "tests/test_p15_a_full_chain_review_boundaries.py",
    "tests/test_p15_a_q8_reporting_boundaries.py", "tests/test_p15_a_q8_trusted_reaggregation_boundaries.py",
    "tests/test_p15_a_q8_quant_shadow_readout_boundaries.py",  # their allowlists name the new A-owned paths
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
def test_owner_is_effect_free_and_knows_no_llm_or_ledger(path):
    found, names = [], set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in EFFECT_NAMES:
            found.append(node.func.id)
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
            if node.attr in EFFECT_ATTRS and not (isinstance(node.value, ast.Name) and node.value.id == "json" and node.attr == "dumps"):
                found.append(node.attr)
        if isinstance(node, ast.Name):
            names.add(node.id)
    assert not found, found
    assert not names & LLM_AND_LEDGER, names & LLM_AND_LEDGER


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_helpers_come_from_the_facade_and_size_budget_holds(path):
    tree = _tree(path)
    own = set(_functions(tree))
    loads = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    stray = {n for n in loads if n.startswith("_") and n not in own and n != "__name__"}
    assert not stray, stray
    for name, fn in _functions(tree).items():
        if name.endswith("_impl"):
            assert fn.args.kwonlyargs and fn.args.kwonlyargs[-1].arg == "facade", name
    assert len((ROOT / path).read_text(encoding="utf-8-sig").splitlines()) <= 350


def test_review_orchestration_and_llm_boundary_stay_in_the_facade():
    funcs = _functions(_tree(FACADE))
    assert "build_ai_reporter_review" in funcs
    called = {n.func.id if isinstance(n.func, ast.Name) else n.func.attr for n in ast.walk(funcs["build_ai_reporter_review"]) if isinstance(n, ast.Call)}
    assert {"record_raw_input", "record_llm_prompt", "record_llm_response", "resolve_policy_llm_slot", "resolve_policy_llm_execution_slot",
            "normalize_openrouter_model_name", "from_env", "chat", "resolve", "parse_llm_json_response", "required_key_metadata",
            "_env_bool", "getenv"} <= called
    assert {"resolve_ai_review_enabled", "resolve_parse_mode", "resolve_parse_failure_reason"} <= called
    assert len((ROOT / FACADE).read_text(encoding="utf-8-sig").splitlines()) < len(_git("show", f"{BASE_SHA}:{FACADE}").splitlines()) - 200


def test_facade_keeps_every_base_name_signature_and_constant():
    base_src = _git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿")
    ns = types.ModuleType("_p15_reporter_ai_review_boundary_base")
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


def test_unmoved_helpers_are_ast_identical_and_moved_names_are_thin_wrappers():
    base_funcs = _functions(ast.parse(_git("show", f"{BASE_SHA}:{FACADE}").lstrip("﻿")))
    cur_funcs = _functions(_tree(FACADE))
    assert set(cur_funcs) == set(base_funcs)
    for name in UNMOVED_IDENTICAL:
        assert ast.dump(cur_funcs[name]) == ast.dump(base_funcs[name]), name
    source = (ROOT / FACADE).read_text(encoding="utf-8-sig")
    for name in MOVED:
        node = cur_funcs[name]
        assert len(node.body) == 1 and isinstance(node.body[0], ast.Return), name
        assert f"{name}_impl" in ast.get_source_segment(source, node) and "facade=_sys.modules[__name__]" in ast.get_source_segment(source, node)
        assert getattr(facade, name).__module__ == facade.__name__


def test_changes_since_previous_checkpoint_stay_inside_the_allowlist():
    changed = set(_git("diff", "--name-only", PRIOR).split())
    changed |= set(_git("ls-files", "--others", "--exclude-standard", "--", "libs", "tests", "docs").split())
    assert changed <= ALLOWED_CHANGES, sorted(changed - ALLOWED_CHANGES)


def test_llm_and_trust_modules_are_untouched_since_base():
    assert _git("diff", "--name-only", BASE_SHA, "--", "libs/llm", "libs/research/evidence_ledger.py", "libs/reporting/llm_artifacts.py").split() == []


@pytest.mark.parametrize("first", ["libs.reporting.reporter_ai_review", "libs.reporting.reporter_ai_review_parts.result_shaping",
                                   "libs.reporting.reporter_analysis", "libs.reporting"])
def test_fresh_import_has_no_cycle_and_wrappers_resolve(tmp_path, first):
    code = (
        "import importlib\n"
        f"importlib.import_module({first!r})\n"
        "m = importlib.import_module('libs.reporting.reporter_ai_review')\n"
        "assert m._clip_str('abcdef', max_len=5) == 'ab...'\n"
        "assert m._default_result(enabled=False, status='disabled')['llm_status'] == 'fallback'\n"
        "assert m._build_messages('d', {})[0]['role'] == 'system'\n"
        "print('OK')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run([sys.executable, *(["-O"] if sys.flags.optimize else []), "-c", code], cwd=tmp_path,
                          env=env, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert proc.stdout.strip() == "OK" and list(tmp_path.iterdir()) == []
