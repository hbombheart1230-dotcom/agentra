"""Actual immutable-source parity of the four approved Operator Brief groups."""
from __future__ import annotations
import copy
from functools import lru_cache
import importlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import types

import pytest

BASE = "57e588d6b1281e69fa6d00ef4cc23246fca12501"
ROOT = Path(__file__).resolve().parents[1]
PREFIX = "apps/operator_ui/"
FROZEN = ["data_access_brief_canonical_input", "data_access_brief_compaction", "data_access_brief_sanitation",
          "data_access_brief_input_sections", "data_access_brief_monitor_sections", "data_access_brief_render_sections"]


@lru_cache(None)
def pinned(name):
    return subprocess.check_output(["git", "show", BASE + ":" + PREFIX + name + ".py"], cwd=ROOT).decode("utf-8")


@lru_cache(None)
def baseline(name):
    mod = types.ModuleType("batch05_base_" + name)
    exec(compile(pinned(name), "<immutable " + name + ">", "exec"), mod.__dict__)
    return mod


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def identity_graph(value):
    seen = {}
    def walk(v):
        if isinstance(v, (dict, list, tuple)):
            if id(v) in seen: return ("ref", seen[id(v)])
            tag = len(seen); seen[id(v)] = tag
            rows = [(k, walk(x)) for k, x in v.items()] if isinstance(v, dict) else [walk(x) for x in v]
            return (type(v).__name__, tag, rows)
        return v
    return walk(value)


def scenario_detail(case):
    detail = {"run_id": "run-\uac80\uc99d", "commander": {"mode": "observe", "phase": "entry", "path": "noop"},
              "strategist": {"summary": {"playbook": "defensive", "themes": ["\ubc18\ub3c4\uccb4"], "candidate_hints": ["AAA", "AAA", "BBB"]},
                  "evidence": {"raw_input": {"global_sentiment_inputs": {"score": -.4, "fear_index": {"level": 26}, "macro_moves": {"dxy_pct": .2, "tnx_delta": .01}}, "collected_market_news": [{"title": "\uc2dc\uc7a5 <news>"}]} }},
              "scanner": {"summary": {"universe_size": 12}, "decision_trace": {"selected_candidate": {"symbol": "AAA", "rank": 1, "score": .7, "why": "\ubc18\ub3c4\uccb4 strong", "score_breakdown": {"alpha": .7}}, "selected_symbol": "AAA"},
                  "feature_coverage": {"present": 2, "total": 3, "quality": "partial"}, "quote_metrics": {"quote_volume": 10, "quote_trading_value": 100}},
              "monitor": {"summary": {"reason": "NOOP", "entry_reason": "guard_denied"}, "decision_trace": {"thresholds_guards_used": {"stop_loss_pct": -.03}}},
              "supervisor": {"verdict": {"allowed": False, "reason": "blocked"}}, "executor": {"execution": {"action": "NOOP"}}, "reporter": {"found": False}}
    if case == "empty": return {}
    if case == "unknown": return {"run_id": "unknown", "monitor": None, "scanner": [], "supervisor": None}
    if case == "allow": detail["supervisor"]["verdict"] = {"allowed": True, "reason": "synthetic allowed"}
    if case == "no_selection": detail["scanner"]["decision_trace"] = {}
    if case == "long": detail["monitor"]["summary"]["reason"] = "\uc774\uc720" * 900
    if case == "malformed": detail["trade_report"] = {"report_data": "invalid"}; detail["scanner"]["feature_coverage"] = []
    if case == "missing": detail.pop("monitor"); detail.pop("strategist")
    if case == "repeat": detail["scanner"]["decision_trace"]["selected_candidate"]["why"] = "\ubc18\ub3c4\uccb4 \ubc18\ub3c4\uccb4"
    return detail


def run(case, version, monkeypatch):
    import apps.operator_ui.data_access_core as facade
    inp = baseline("data_access_brief_input_projection") if version == "base" else importlib.import_module("apps.operator_ui.data_access_brief_input_projection")
    sections = baseline("data_access_brief_sections_projection") if version == "base" else importlib.import_module("apps.operator_ui.data_access_brief_sections_projection")
    detail = scenario_detail(case)
    events = []
    canonical_impl = facade._build_canonical_trade_brief_input
    def canonical(report):
        events.append(("canonical", copy.deepcopy(report)))
        result = canonical_impl(report)
        if case in {"canonical", "filters", "stale", "stop", "nulls"}:
            result.update(symbol="BBB", selected_rank=2, market_context_summary="canonical preferred", monitor_summary="canonical guard", execution_summary="NOOP", themes=["canonical"], top_candidates=[{"symbol": "BBB", "rank": 2}, {"symbol": "BBB", "rank": 3}])
        if case == "filters": result.update(filter_bullets=["chart completeness filter: stale", "keep"], selection_bullets=["Chart / feature coverage: stale", "keep"], filter_rows=[{"name": "Chart completeness filter", "status": "STALE", "note": "old"}, {"name": "Risk gate", "status": "FAIL"}])
        if case == "stop": result.update(monitor_stop_policy_trace={"active_axis": "canonical", "stop": 0}, monitor_snapshot={"monitor_stop_policy_trace": {"active_axis": "snapshot", "keep": False}})
        if case == "nulls": result.update(why_selected=None, top_candidates=[], monitor_bullets=[], themes=[])
        return result
    with monkeypatch.context() as m:
        m.setattr(facade, "_build_canonical_trade_brief_input", canonical)
        for name in ["_clean_brief_text", "_safe_int", "_format_float", "_brief_build_stop_policy_trace", "_chart_filter_status_and_note"]:
            original = getattr(facade, name)
            def spy(*args, _name=name, _original=original, **kwargs):
                events.append((_name, copy.deepcopy(args), copy.deepcopy(kwargs)))
                if case == "exception" and _name == "_chart_filter_status_and_note": raise ValueError("synthetic chart")
                if case == "late" and _name == "_clean_brief_text":
                    m.setattr(facade, "_format_float", lambda v, n=2: "patched-float")
                return _original(*args, **kwargs)
            m.setattr(facade, name, spy)
        error = None
        try:
            prepared = inp.build_operator_brief_input(detail, facade=facade)
            views = sections.build_operator_brief_sections(detail, facade=facade)
            compact = facade._compact_operator_brief_input_for_llm(prepared)
            messages = facade._build_operator_brief_messages(compact)
            text = facade._sanitize_operator_brief_text("\ufeff <b>minute-candle</b>\x00 UNKNOWN \ud55c\uae00" + ("x"*1100 if case == "long" else ""))
            markdown = facade._render_operator_brief_markdown({"status": "fallback", "sections": views, "headline": "\uac80\uc99d"})
            value = (prepared, views, compact, messages, text, markdown)
        except ValueError as exc:
            if case != "exception": raise
            error = (type(exc).__name__, str(exc)); value = None
    return encoded(value), identity_graph(value), encoded(detail), encoded(events), error


CASES = ["empty", "unknown", "normal", "allow", "no_selection", "long", "malformed", "missing", "repeat", "canonical", "filters", "stale", "stop", "nulls", "exception", "late"]


@pytest.mark.parametrize("case", CASES)
def test_actual_base_json_markdown_prompt_alias_and_exception_parity(case, monkeypatch):
    original = run(case, "base", monkeypatch)
    assert run(case, "candidate", monkeypatch) == original


@pytest.mark.parametrize("name", FROZEN)
def test_frozen_owner_files_remain_exact_base_bytes(name):
    assert (ROOT / PREFIX / (name + ".py")).read_text(encoding="utf-8").replace("\r\n", "\n") == pinned(name)


@pytest.mark.parametrize("name", ["data_access_brief_input_projection", "data_access_brief_sections_projection", "data_access_brief_market_sections"])
def test_existing_callable_abi_and_frozen_builders_unchanged(name):
    import ast
    old = baseline(name)
    new = importlib.import_module("apps.operator_ui." + name)
    old_tree = ast.parse(pinned(name)); new_tree = ast.parse((ROOT/PREFIX/(name+'.py')).read_text(encoding='utf-8'))
    for n in old_tree.body:
        if isinstance(n, ast.FunctionDef):
            assert inspect.signature(getattr(new,n.name)) == inspect.signature(getattr(old,n.name))
            if n.name not in {"build_operator_brief_input", "build_operator_brief_sections"}:
                actual = next(f for f in new_tree.body if isinstance(f,ast.FunctionDef) and f.name == n.name)
                assert ast.dump(n) == ast.dump(actual)
