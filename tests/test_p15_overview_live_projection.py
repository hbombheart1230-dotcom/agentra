"""Focused live-overview semantics and exact BASE behavior; no invented goldens."""
from __future__ import annotations

import ast
import copy
import inspect
import json
from pathlib import Path
import subprocess
import types

import pytest

import apps.operator_ui.data_access_core as core
from apps.operator_ui.data_access_overview_projection import project_live_overview

BASE = "4b0c3e0b5f8f24fa3c10d9082b85fab63f15c4c3"
ROOT = Path(__file__).resolve().parents[1]
DAY = "2026-03-16"


def _inputs(**updates):
    values = dict(latest_day=DAY, today_rows=[], daily={}, operator_summary={}, reporter={},
                  reconciliation={}, executive={}, health={}, trading={}, recon_summary={},
                  trade_summary={}, all_today_trades=[], traded_symbol_summary=[],
                  overtrading_warning={"level": "normal"}, facade=core)
    values.update(updates)
    return values


def _verdict(allowed, reason, **extra):
    return dict(ts=DAY + "T01:00:00+00:00", stage="execute_from_packet", event="verdict",
                payload=dict(allowed=allowed, reason=reason), **extra)


def test_strict_boolean_noop_priority_and_no_input_mutation():
    rows = [dict(ts=DAY, stage="commander_router", event="route"),
            _verdict(True, "noop_intent_skipped"), _verdict(False, "noop_intent_skipped"),
            _verdict(None, "noop_intent_skipped"), _verdict(False, "guard"),
            _verdict(False, ""), _verdict(1, "not_a_boolean"), _verdict(0, "not_a_boolean"),
            _verdict(False, "previous_day", ts_kst="2026-03-15T23:59:00+09:00"),
            dict(ts=DAY, stage="execute_from_packet", event="verdict", payload=[])]
    inputs = _inputs(today_rows=rows, operator_summary={"present": True})
    before = copy.deepcopy({k: v for k, v in inputs.items() if k != "facade"})
    result = project_live_overview(**inputs)
    assert result.daily["approvals"] == 1  # True wins even with a NOOP reason
    assert result.daily["blocks"] == 2  # NOOP is classified before allowed=False
    assert "approved=1, blocked=2, noop=2" in result.executive["summary_lines"][0]
    assert before == {k: v for k, v in inputs.items() if k != "facade"}


def test_day_selection_action_order_stale_reporter_and_reconciliation():
    rows = [_verdict(False, "z_guard"), _verdict(False, "a_guard"),
            dict(ts=DAY, stage="commander_router", event="route")]
    trades = [{"action": " sell ", "symbol": "BBB"}, {"action": "BUY", "symbol": "AAA"}]
    reporter = {"ai_review": {"status": " OK ", "evidence": ["keep"]}, "trade_summary": {"trade_count": 0}}
    inp = _inputs(today_rows=rows, all_today_trades=trades, traded_symbol_summary=[{"symbol": "BBB"}, {"symbol": "AAA"}],
                  reporter=reporter, trade_summary=reporter["trade_summary"], operator_summary={"present": True},
                  executive={"summary_lines": ["old"], "system_status": "GREEN"},
                  reconciliation={"summary": {"local_total": 0}}, recon_summary={"broker_total": 1})
    result = project_live_overview(**inp)
    assert list(result.daily["decision_actions"]) == ["SELL", "BUY"]
    assert result.executive["summary_lines"][1] == "Top guard block: a_guard"
    assert result.executive["summary_lines"][-1] == "old"
    assert result.reporter["ai_review"]["status"] == "snapshot"
    assert reporter["ai_review"]["status"] == " OK "
    assert result.trade_summary["symbols_traded"] == ["BBB", "AAA"]
    assert result.recon_summary["pending"] is True
    assert result.recon_summary["broker_total"] == 1


@pytest.mark.parametrize("latest_day", ["", DAY])
def test_absent_day_and_missing_reports_fallback(latest_day):
    result = project_live_overview(**_inputs(latest_day=latest_day, overtrading_warning={"level": "high"}))
    if latest_day:
        assert result.executive == {"system_status": "UNKNOWN", "summary_lines": []}
        assert result.health["recommended_action"] == ["review same-day overtrading warning: high"]
        assert result.reporter["ai_review"]["status"] == "not_generated_yet"
    else:
        assert result.daily == result.reporter == result.executive == {}


def test_fresh_reports_and_maximum_reconciliation_precedence_are_preserved():
    trading = {"run_total": 3, "executions_total": 3, "blocked_total": 0}
    daily = {"events": 3, "approvals": 3}
    reporter = {"trade_summary": {"trade_count": 3, "symbols_traded": ["A"]}, "ai_review": {"status": "ok"}}
    recon = {"summary": {"local_total": 0, "broker_total": 3, "matched_by_ord_no": 0}}
    inp = _inputs(operator_summary={"present": True}, trading=trading, daily=daily, reporter=reporter,
                  trade_summary=reporter["trade_summary"], reconciliation=recon, recon_summary=recon["summary"],
                  all_today_trades=[{"action": "BUY"}], traded_symbol_summary=[{"symbol": "A"}])
    result = project_live_overview(**inp)
    assert result.daily is daily and result.trading is trading and result.reporter is reporter
    assert result.reconciliation is recon  # max(broker_total) prevents a false stale override


@pytest.fixture(scope="module")
def original_overview():
    source = subprocess.check_output(["git", "show", BASE + ":apps/operator_ui/data_access_core.py"], cwd=ROOT).decode("utf-8")
    fn = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "load_overview")
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<pinned overview BASE>", "exec",
                 flags=__import__("__future__").annotations.compiler_flag), ns)
    result = types.FunctionType(ns["load_overview"].__code__, vars(core))
    result.__annotations__ = ns["load_overview"].__annotations__
    return result


@pytest.mark.parametrize("case", ["missing", "stale", "fresh", "no_day", "out_of_order", "late_helper", "exception"])
def test_full_facade_matches_base_json_order_reader_calls_and_exceptions(case, original_overview, tmp_path, monkeypatch):
    from test_operator_ui import _FakeRouter, _make_config
    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(lambda: _FakeRouter()))
    cfg = _make_config(tmp_path)
    if case == "missing":
        for path in (cfg.reports_root / "daily").rglob("*.json"):
            path.unlink()  # only the test's existing synthetic fixture
    if case == "no_day":
        monkeypatch.setattr(core, "_latest_event_day", lambda path: None)
    if case == "stale":
        # Existing fixture reports are stale relative to this extra historical event.
        with cfg.event_log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(_verdict(False, "hostile_guard")) + "\n")
    if case == "out_of_order":
        rows = cfg.event_log_path.read_text(encoding="utf-8").splitlines()
        cfg.event_log_path.write_text("\n".join(reversed(rows)) + "\n", encoding="utf-8")
    funcs = {n: getattr(core, n) for n in ("_latest_event_day", "_read_daily_artifact_day", "_read_exact_day",
             "load_strategy_memory_timeline", "load_recent_trades_for_day", "load_latest_strategist_prompt_summary",
             "_iter_jsonl", "load_recent_runs", "_safe_int", "_event_day")}
    def run(fn):
        trace = []
        def wrapped(name):
            def call(*args, **kwargs):
                trace.append((name, repr(args), repr(kwargs)))
                if name == "_event_day" and case == "late_helper":
                    def late(*a, **kw):
                        trace.append(("late_safe_int", repr(a), repr(kw)))
                        return funcs["_safe_int"](*a, **kw)
                    monkeypatch.setattr(core, "_safe_int", late)
                if name == "_safe_int" and case == "exception":
                    raise LookupError("overview synthetic failure")
                return funcs[name](*args, **kwargs)
            return call
        for name in funcs:
            monkeypatch.setattr(core, name, wrapped(name))
        try:
            result = ("value", json.dumps(fn(cfg), ensure_ascii=False).encode("utf-8"))
        except Exception as exc:
            result = ("exception", type(exc).__name__, str(exc))
        return result, trace
    assert inspect.signature(core.load_overview) == inspect.signature(original_overview)
    import apps.operator_ui.data_access as compat
    assert compat.load_overview is core.load_overview
    expected = run(original_overview)
    actual = run(core.load_overview)
    assert actual == expected
    if case == "exception":
        assert actual[0] == ("exception", "LookupError", "overview synthetic failure")
    else:
        assert actual[0][0] == "value"
    if case == "late_helper":
        assert any(row[0] == "late_safe_int" for row in actual[1])


def test_projection_never_reads_files_or_calls_llm(monkeypatch):
    inputs = _inputs(today_rows=[_verdict(False, "noop_intent_skipped")])
    def forbidden(*args, **kwargs):
        raise AssertionError("pure projection attempted an effect")
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(core, "_iter_jsonl", forbidden)
    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(forbidden))
    result = project_live_overview(**inputs)
    assert result.trading["blocked_total"] == 0
    assert result.reporter["ai_review"]["status"] == "not_generated_yet"


@pytest.mark.parametrize("old,new", [
    ("if allowed is True:", "if allowed:"),
    ('if reason == "noop_intent_skipped":', "if False:"),
    ('row.get("ts_kst") or row.get("ts")', 'row.get("ts") or row.get("ts_kst")'),
    ("if latest_day and live_snapshot_mismatch:", "if False:"),
])
def test_hostile_classification_day_and_stale_mutations_change_the_real_projection(old, new):
    import apps.operator_ui.data_access_overview_projection as owner
    source = Path(owner.__file__).read_text(encoding="utf-8")
    assert source.count(old) == 1
    namespace = dict(vars(owner))
    exec(compile(source.replace(old, new), "<in-memory overview negative>", "exec"), namespace)
    inputs = _inputs(today_rows=[_verdict(1, "not_boolean"), _verdict(False, "noop_intent_skipped"),
                        _verdict(False, "wrong_day", ts_kst="2026-03-15T23:59:00+09:00")],
                    operator_summary={"present": True}, reporter={"trade_summary": {"trade_count": 0}},
                    all_today_trades=[{"action": "BUY"}])
    expected = project_live_overview(**inputs)
    actual = namespace["project_live_overview"](**inputs)
    assert json.dumps(actual, ensure_ascii=False) != json.dumps(expected, ensure_ascii=False)
