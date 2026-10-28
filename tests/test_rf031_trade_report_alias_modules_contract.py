"""RF-031 C1: compatibility alias/shim modules are pure ``sys.modules`` aliases of their canonical modules.

Pure import/AST checks: nothing is executed beyond importing, no disk write, no network. The identity assertions
fail if a stub grows its own logic or its canonical target moves. Explicit raises keep them live under ``python -O``.
"""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    "libs.reporting.trade_report_ai_compact_helpers": "libs.reporting.trade_report.compact_helpers",
    "libs.reporting.trade_report_ai_llm": "libs.reporting.trade_report.llm",
    "libs.reporting.trade_report_ai_merge_policy": "libs.reporting.trade_report.merge_policy",
    "libs.reporting.trade_report_ai_prompting": "libs.reporting.trade_report.prompting",
    "libs.reporting.trade_report_ai_shared_facts": "libs.reporting.trade_report.shared_facts",
    "libs.reporting.trade_report_ai_summary_adapter": "libs.reporting.trade_report.summary_adapter",
    "libs.reporting.trade_report_markdown_monitor": "libs.reporting.trade_report_markdown.monitor",
    "libs.reporting.trade_report_markdown_scanner": "libs.reporting.trade_report_markdown.scanner",
}


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@pytest.mark.parametrize("legacy,canonical", sorted(ALIASES.items()))
def test_legacy_path_is_the_same_module_object_as_the_canonical_path(legacy, canonical):
    old = importlib.import_module(legacy)
    new = importlib.import_module(canonical)
    if old is not new:
        raise AssertionError(f"{legacy} must be the same module object as {canonical}")


def test_post_exit_shadow_shim_is_the_canonical_module_object():
    old = importlib.import_module("libs.reporting.trade_report_post_exit_shadow")
    new = importlib.import_module("libs.agents.reporter.narrative.trade_report_post_exit_shadow")
    if old is not new:
        raise AssertionError("post-exit shadow shim must alias the canonical module")


@pytest.mark.parametrize("legacy", sorted(ALIASES) + ["libs.reporting.trade_report_post_exit_shadow"])
def test_alias_stub_source_has_no_logic_of_its_own(legacy):
    path = ROOT / (legacy.replace(".", "/") + ".py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden = [type(n).__name__ for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef, ast.For, ast.While, ast.If, ast.Try))]
    _eq(forbidden, [])
    if sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "import_module") + \
       sum(1 for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))) < 1:
        raise AssertionError("stub must import its canonical module")
    if len(path.read_text(encoding="utf-8").splitlines()) > 12:
        raise AssertionError("alias stubs stay tiny")


def test_symbol_metadata_facade_reexports_the_same_objects_without_a_second_implementation():
    facade = importlib.import_module("libs.reporting.trade_report_symbol_metadata")
    pairs = {
        "resolve_trade_symbol_metadata": "libs.agents.reporter.read_models.symbol_metadata_resolution",
        "infer_symbol_name_from_report_text": "libs.agents.reporter.read_models.symbol_metadata_name_inference",
        "component_themes_for_symbol": "libs.agents.reporter.read_models.symbol_metadata_sources",
        "append_unique_text": "libs.agents.reporter.read_models.symbol_metadata_text",
        "SYMBOL_NAME_FALLBACKS": "libs.agents.reporter.read_models.symbol_metadata_fallbacks",
    }
    for name, module in pairs.items():
        if getattr(facade, name) is not getattr(importlib.import_module(module), name):
            raise AssertionError(name)
    tree = ast.parse((ROOT / "libs/reporting/trade_report_symbol_metadata.py").read_text(encoding="utf-8"))
    _eq([type(n).__name__ for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))], [])
