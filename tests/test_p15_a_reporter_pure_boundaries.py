"""P1.5 DEV-A A1-A4 structural contract for the four Reporter operational projection owners.

Owners are effect-free (stdlib-only imports, no I/O/clock/env/external policy references, no ``facade`` attribute
stores), contain exactly the moved code, and each facade keeps BASE (d7ab8294) declaration order, signatures and
every untouched function (incl. pinned R3 ledger wrappers) AST-identical; only the designated orchestrators changed.
"""
from __future__ import annotations

import ast
import subprocess
import types
from collections import Counter
from pathlib import Path

import pytest

import libs.agents.reporter.read_models.metrics_projection as metrics_proj
import libs.agents.reporter.read_models.period_summary_projection as period_proj
import libs.agents.reporter.read_models.operator_daily_projection as visibility_proj
import libs.agents.reporter.read_models.phase_health_text_rendering as health_proj

ROOT = Path(__file__).resolve().parents[1]
BASE = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
A2_VIEWS = {"_build_policy_aware_gating_deadness", "_build_policy_source_summary", "_compact_run_view", "_build_suspicious_flags",
            "_persisted_monitor_surfaces"}
A2_TEXT = {"_render_text_table", "_render_compact_run_table", "_render_reclaim_table", "render_phase_5_2_5_3_runtime_health_text",
           "render_policy_surface_quality_summary_text", "render_chart_structure_decision_hint_summary_text"}
A2_MOVED = tuple(sorted(A2_VIEWS | A2_TEXT))
A2_EXTRA_OWNER = {"_persisted_monitor_surfaces", "_extract_run_health_surfaces", "_assemble_run_health", "build_runtime_health_aggregate"}
RM = "libs/agents/reporter/read_models/"
SIBLING = "libs.agents.reporter.read_models"
OWNERS = {
    RM + "operator_daily_projection.py": ({"build_daily_summary_readout"}, {"__future__", "json", "typing"}),
    RM + "operator_run_context_projection.py": ({"build_run_contexts"}, {"__future__", "typing"}),
    RM + "phase_health_projection.py": ({"_extract_run_health_surfaces", "_assemble_run_health", "build_runtime_health_aggregate"},
                                        {"__future__", "collections", "typing"}),
    RM + "phase_health_policy_views.py": (set(A2_VIEWS), {"__future__", "collections", "typing"}),
    RM + "phase_health_text_rendering.py": (set(A2_TEXT), {"__future__", "json", "typing"}),
    RM + "period_summary_projection.py": ({"runtime_activity_from_q9_windows", "runtime_activity_from_daily_payload",
                                           "runtime_activity_not_available", "runtime_activity_from_live_summary",
                                           "apply_critical_closeout_readout"}, {"__future__", "typing"}),
    RM + "metrics_projection.py": ({"aggregate_day_metrics"}, {"__future__", "collections", "typing", SIBLING}),
    RM + "metrics_summary_projection.py": ({"assemble_metrics_summary"}, {"__future__", "typing"}),
    RM + "metrics_event_fold.py": ({"new_llm_fold", "fold_llm_result"}, {"__future__", "collections", "typing"}),
}
FACADES = {
    "libs/reporting/operator_visibility.py": {"build_operator_daily_summary_payload", "_build_run_contexts"},
    "libs/reporting/phase_runtime_health.py": set(A2_MOVED) | {"_persisted_monitor_surfaces", "_extract_run_health", "build_phase_5_2_5_3_runtime_health"},
    "libs/reporting/operator_period_summary.py": {"_runtime_activity_payload", "build_operator_daily_summary_artifact_payload"},
    "libs/reporting/metrics_report_generator.py": {"generate_metrics_report"},
}
EFFECT_NAMES = {"open", "read_text", "write_text", "read_bytes", "write_bytes", "mkdir", "iterdir", "glob", "rglob", "exists", "stat",
                "unlink", "getenv", "environ", "now", "utcnow", "today", "_utc_now_iso", "_read_json", "_iter_jsonl", "iter_json_array",
                "iter_jsonl_events", "resolve_runtime_write_path", "build_commander_route_summary", "_iter_run_dirs",
                "normalize_monitor_entry_policy_schema", "_latest_live_summary_payload", "_load_or_build_metrics",
                "_find_day_artifact", "build_policy_surface_quality_snapshot", "load_quant_shadow_candidate_payloads", "Path"}


def _tree(path, sha=None):
    src = subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT).decode("utf-8-sig") if sha else \
        (ROOT / path).read_text(encoding="utf-8-sig")
    return ast.parse(src)


@pytest.mark.parametrize("path", sorted(OWNERS))
def test_owner_is_effect_free_and_holds_exactly_the_moved_code(path):
    names, allowed_imports = OWNERS[path]
    tree = _tree(path)
    imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | \
        {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert imports == allowed_imports
    assert {n.name for n in tree.body if isinstance(n, ast.FunctionDef)} == names
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and not (isinstance(n.value, ast.Name) and n.value.id == "facade")}
    assert not used & EFFECT_NAMES, sorted(used & EFFECT_NAMES)
    stores = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
              and n.value.id == "facade" and not isinstance(n.ctx, ast.Load)]
    assert not stores
    body_strings = [c for f in tree.body if isinstance(f, ast.FunctionDef) for c in ast.walk(f)
                    if isinstance(c, ast.Constant) and isinstance(c.value, str) and "facade." in c.value]
    assert not body_strings
    assert len((ROOT / path).read_text(encoding="utf-8").splitlines()) <= 350


@pytest.mark.parametrize("path", sorted(FACADES))
def test_facade_declarations_untouched_except_designated_orchestrators(path):
    base, cur = _tree(path, BASE), _tree(path)
    bdefs = [n for n in base.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    cdefs = [n for n in cur.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    assert [n.name for n in bdefs] == [n.name for n in cdefs]
    changed = []
    for b, c in zip(bdefs, cdefs):
        if isinstance(b, ast.FunctionDef):
            assert ast.dump(b.args) == ast.dump(c.args) and ast.dump(b.returns or ast.Constant(None)) == \
                ast.dump(c.returns or ast.Constant(None)), c.name
            assert [ast.dump(d) for d in b.decorator_list] == [ast.dump(d) for d in c.decorator_list]
        if ast.dump(b) != ast.dump(c):
            changed.append(c.name)
    assert set(changed) == FACADES[path]
    for c in cdefs:
        if c.name in A2_MOVED and path.endswith("phase_runtime_health.py"):
            assert len(c.body) == 1 and any(f"{m}.{c.name}(" in ast.unparse(c.body[0]) for m in ("_health_views", "_health_text"))
    other = [ast.dump(n) for n in base.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]
    assert other == [ast.dump(n) for n in cur.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]


@pytest.mark.parametrize("path,keep", [
    ("libs/reporting/operator_visibility.py", ("_build_run_contexts(", "_iter_jsonl(", "_load_or_build_metrics(", "_find_day_artifact(",
                                               "build_policy_surface_quality_snapshot(", "for row in day_rows")),
    ("libs/reporting/operator_period_summary.py", ("iter_json_array(", "_latest_live_summary_payload(", "_read_json(",
                                                   "load_quant_shadow_candidate_payloads(", "_utc_now_iso()")),
    ("libs/reporting/metrics_report_generator.py", ("resolve_runtime_write_path(", "iter_jsonl_events(", "build_commander_route_summary(",
                                                    "_utc_now_iso()", "write_text(")),
])
def test_effects_traversal_and_writes_remain_in_facade(path, keep):
    src = ast.unparse(_tree(path))
    for k in keep:
        assert k in src, k


def test_owners_are_callable_with_stub_facades():
    stub = types.SimpleNamespace(_safe_int=lambda v, d=0: int(v) if str(v).lstrip("-").isdigit() else d,
                                 _safe_list_of_str=lambda v: [str(x) for x in v] if isinstance(v, list) else [])
    assert period_proj.runtime_activity_from_daily_payload(source_payload={"events": "4", "symbols_observed": [1, 2]}, facade=stub) == {
        "source": "daily_report_payload", "events": 4, "approvals": 0, "blocks": 0, "symbols_observed_count": 2,
        "generated_symbol_report_count": 0}
    summary = {"residual_positions": {"closeout_operational_risk": {"severity": "Critical", "unresolved_symbols": ["A"]}},
               "operator_readout": {"issues": ["x"]}}
    period_proj.apply_critical_closeout_readout(summary=summary, facade=stub)
    assert summary["operator_readout"]["issues"][0].startswith("CRITICAL closeout issue") and summary["operator_readout"]["root_cause"]
    rows = [{"run_id": "r1", "reason": "a\nb", "policy_aware_gating": {"applied": True}}]
    assert health_proj._render_text_table(rows, facade=stub) == \
        __import__("libs.reporting.phase_runtime_health", fromlist=["x"])._render_text_table(rows)
    acc = metrics_proj.aggregate_day_metrics(day_rows=[], facade=types.SimpleNamespace(
        _latency_summary=lambda rows: {}, _numeric_summary=lambda v: {"n": len(v)}))
    assert acc["run_ids"] == set() and acc["llm_success_rate"] == 0.0 and isinstance(acc["blocks_by_reason"], Counter)
    assert visibility_proj.build_daily_summary_readout.__code__.co_kwonlyargcount >= 25
