"""Run-detail BASE parity, effect ordering and targeted hostile mutations."""
from __future__ import annotations

import copy
from datetime import datetime
import inspect
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import apps.operator_ui.data_access_core as core
import apps.operator_ui.data_access_run_detail_projection as owner
from test_p15_operator_trade_index_projection import _bytes, _files, _original


@pytest.mark.parametrize("case", ["normal", "missing_run", "out_of_order", "canonical", "no_trace", "no_reporter", "stale_report", "noop", "blocked", "late_helper", "exception", "reporter_exception"])
def test_run_detail_matches_base_output_and_effect_order(case, tmp_path, monkeypatch):
    from test_operator_ui import _make_config, _write_jsonl
    cfg = _make_config(tmp_path)
    rows = [json.loads(line) for line in cfg.event_log_path.read_text(encoding="utf-8").splitlines()]
    if case == "missing_run":
        rows = []
    if case == "out_of_order":
        rows = list(reversed(rows)) + [dict(rows[2], payload={"playbook": "last-identical-timestamp"})]
    if case == "no_trace":
        rows = [row for row in rows if row["stage"] != "decision_trace"]
        next(row for row in rows if row["stage"] == "scanner")["payload"]["selected_candidate"] = {"symbol": "005930"}
    if case in {"noop", "blocked"}:
        for row in rows:
            if row["event"] == "verdict":
                row["payload"] = {"allowed": False, "reason": "noop_intent_skipped" if case == "noop" else "risk_guard"}
            if row["event"] == "execution":
                row["payload"] = {"allowed": False, "order": {"action": "NOOP", "symbol": ""}}
    _write_jsonl(cfg.event_log_path, rows)
    if case == "no_reporter":
        for path in (cfg.reports_root / "dev" / "analysis" / "reporter_analysis").glob("*.json"):
            path.unlink()
    if case == "stale_report":
        bundle = next(cfg.reports_root.rglob("aggregated_execution_bundle.json"))
        value = json.loads(bundle.read_text(encoding="utf-8"))
        value.update(run_id="old-run", linked_run_ids=["old-run"])
        bundle.write_text(json.dumps(value), encoding="utf-8")
        lifecycle = bundle.parent / "trade_lifecycle.json"
        lifecycle.write_text(json.dumps({"trade_id": value["trade_id"], "run_ids_all": ["old-run"]}), encoding="utf-8")
    if case == "canonical":
        monkeypatch.setattr(core, "load_run_canonical_sources", lambda *args: {
            "artifacts": {"strategist": {"playbook": "canonical", "llm_metadata_summary": {"model": "offline"}},
                "scanner": {"top_stock": "000660", "selected_symbol": "000660", "candidate_pool_after_filter": 7,
                            "selected_candidate": {"symbol": "000660", "why": "canonical"}},
                "monitor": {"monitor_reason": "canonical-reason"},
                "executor": {"order": {"action": "NOOP", "symbol": "000660"}}}})
    names = ("_iter_jsonl", "load_run_canonical_sources", "prefer_canonical_agent_payload",
        "load_recent_trades_for_day", "load_symbol_run_chain", "_trade_report_meta_for_run",
        "load_trade_report_payloads", "_read_json", "_normalize_execution_payload", "normalize_symbol",
        "_iso_to_display", "_reporter_snippet_for_run", "_count_stages", "_truncate_json",
        "_load_operator_brief_with_cache")
    funcs = {name: getattr(core, name) for name in names}
    before = _files(tmp_path)

    def run(fn):
        trace = []
        def wrapped(name):
            def call(*args, **kwargs):
                if name == "load_trade_report_payloads":
                    assert kwargs["read_json"] is core._read_json
                trace.append((name, repr(args), repr({k: (v.__name__ if callable(v) else v) for k, v in kwargs.items()})))
                if case == "exception" and name == "_normalize_execution_payload":
                    raise ValueError("synthetic canonical failure")
                if case == "reporter_exception" and name == "_reporter_snippet_for_run":
                    raise LookupError("synthetic reporter failure")
                if case == "late_helper" and name == "_iso_to_display":
                    def late(rows):
                        trace.append(("late_count_stages", repr(rows)))
                        return funcs["_count_stages"](rows)
                    monkeypatch.setattr(core, "_count_stages", late)
                if name == "_load_operator_brief_with_cache":
                    return {"offline": True, "role_order": list(args[1])}
                return funcs[name](*args, **kwargs)
            return call
        with monkeypatch.context() as patch:
            for name in funcs:
                patch.setattr(core, name, wrapped(name))
            try:
                result = fn(cfg, "run-1")
                value = ("value", _bytes(result))
            except Exception as exc:
                result = None
                value = ("exception", type(exc).__name__, str(exc))
        return value, trace, result
    expected = run(_original("load_run_detail"))
    actual = run(core.load_run_detail)
    assert actual[0] == expected[0], [key for key in (actual[2] or {}) if actual[2][key] != (expected[2] or {}).get(key)]
    assert actual[1] == expected[1], next(((i, a, b) for i, (a, b) in enumerate(zip(actual[1], expected[1])) if a != b), (len(actual[1]), len(expected[1])))
    assert _files(tmp_path) == before
    import apps.operator_ui.data_access as compat
    assert compat.load_run_detail is core.load_run_detail
    assert inspect.signature(core.load_run_detail) == inspect.signature(_original("load_run_detail"))
    if case == "exception":
        assert actual[0] == ("exception", "ValueError", "synthetic canonical failure")
    elif case == "reporter_exception":
        assert actual[0] == ("exception", "LookupError", "synthetic reporter failure")
        assert "_load_operator_brief_with_cache" not in [row[0] for row in actual[1]]
    else:
        assert actual[0][0] == "value"
    if case == "missing_run":
        assert actual[2] == {"run_id": "run-1", "found": False}
        assert [row[0] for row in actual[1]] == ["_iter_jsonl", "_iter_jsonl"]
    if case == "canonical":
        assert actual[2]["scanner"]["decision_trace"]["selected_symbol"] == "000660"
        assert actual[2]["monitor"]["decision_trace"]["monitor_reason"] == "canonical-reason"
    if case == "late_helper":
        assert any(row[0] == "late_count_stages" for row in actual[1])


def test_run_detail_real_offline_cache_artifact_and_llm_call_parity(tmp_path, monkeypatch):
    from test_operator_ui import _FakeRouter, _make_config
    cfg = _make_config(tmp_path)
    class FixedClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 3, 16, 2, 3, 4, tzinfo=tz)
    calls = []
    class OfflineRouter(_FakeRouter):
        def chat(self, *args, **kwargs):
            calls.append((repr(args), repr(kwargs)))
            return super().chat(*args, **kwargs)
    monkeypatch.setattr(core, "datetime", FixedClock)
    import libs.reporting.llm_artifacts as artifacts
    monkeypatch.setattr(artifacts, "datetime", FixedClock)
    monkeypatch.setattr(core, "time", SimpleNamespace(perf_counter=lambda: 1.0))
    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(lambda: OfflineRouter()))
    monkeypatch.setenv("OPENROUTER_DEFAULT_MODEL", "stepfun/step-3.5-flash:free")
    before = _files(tmp_path)
    stamps = {p: (tmp_path / p).stat().st_mtime_ns for p in before}
    def run(fn):
        calls.clear()
        value = _bytes(fn(cfg, "run-1"))
        cold_calls = list(calls)
        cold_files = _files(tmp_path)
        calls.clear()
        warm = _bytes(fn(cfg, "run-1"))
        return value, cold_calls, cold_files, warm, list(calls), _files(tmp_path)
    expected = run(_original("load_run_detail"))
    # Restore only this test's synthetic tree, never a real reports directory.
    for relative in _files(tmp_path).keys() - before.keys():
        (tmp_path / relative).unlink()
    for relative, content in before.items():
        (tmp_path / relative).write_bytes(content)
        os.utime(tmp_path / relative, ns=(stamps[relative], stamps[relative]))
    actual = run(core.load_run_detail)
    for i in (2, 5):
        assert actual[i].keys() == expected[i].keys()
        for relative, content in expected[i].items():
            assert actual[i][relative] == content, str(relative)
    assert actual == expected
    assert actual[1]  # A real offline generation path, not a stubbed cache wrapper.
    assert not actual[4]  # Warm cache does not cause an extra LLM request.


def _canonical_inputs():
    return dict(canonical_sources={"artifacts": {"scanner": {"selected_symbol": "000660", "selected_candidate": {"why": "new"}},
        "monitor": {"monitor_reason": "new"}}}, route_row={}, end_row={},
        strategist_summary={"playbook": "pure"}, scanner_summary={}, monitor_summary={}, verdict_payload={},
        execution_payload={}, strategist_llm={}, strategic_frame={},
        candidate_selection={"selected_symbol": "005930", "selected_candidate": {"why": "old", "retained": True}},
        entry_exit_decision={"monitor_reason": "old", "retained": True}, facade=core)


@pytest.mark.parametrize("missing_reporter", [False, True])
def test_synthetic_run_page_html_bytes_match_base(missing_reporter, tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    import apps.operator_ui.main as ui
    from test_operator_ui import _make_config
    cfg = _make_config(tmp_path)
    if missing_reporter:
        for path in (cfg.reports_root / "dev" / "analysis" / "reporter_analysis").glob("*.json"):
            path.unlink()
    monkeypatch.setattr(core, "_load_operator_brief_with_cache", lambda *args: {})
    client = TestClient(ui.create_app(cfg))
    monkeypatch.setattr(ui, "load_run_detail", _original("load_run_detail"))
    baseline = client.get("/runs/run-1")
    monkeypatch.setattr(ui, "load_run_detail", core.load_run_detail)
    candidate = client.get("/runs/run-1")
    assert baseline.status_code == candidate.status_code == 200
    assert candidate.content == baseline.content


@pytest.mark.parametrize("old,new", [(
    'load_run_canonical_sources(config.reports_root, str(run_id or ""), run_day)',
    'load_run_canonical_sources(config.reports_root, str(run_id or ""), "")'), (
    '_load_operator_brief_with_cache(config, detail)',
    '(_load_operator_brief_with_cache(config, detail), _load_operator_brief_with_cache(config, detail))[0]')])
def test_hostile_reader_argument_and_duplicate_brief_call_are_detected(old, new, tmp_path, monkeypatch):
    from test_operator_ui import _make_config
    cfg = _make_config(tmp_path)
    original = _original("load_run_detail")
    source = inspect.getsource(core.load_run_detail)
    assert source.count(old) == 1
    namespace = dict(vars(core))
    exec(compile(source.replace(old, new), "<hostile run IO mutant>", "exec"), namespace)
    canonical = core.load_run_canonical_sources
    trace = []
    def load(*args):
        trace.append(("canonical", args))
        return canonical(*args)
    def brief(*args):
        trace.append(("brief", _bytes(args[1])))
        return {}
    monkeypatch.setattr(core, "load_run_canonical_sources", load)
    monkeypatch.setattr(core, "_load_operator_brief_with_cache", brief)
    namespace.update(load_run_canonical_sources=load, _load_operator_brief_with_cache=brief)
    original(cfg, "run-1")
    expected = list(trace)
    trace.clear()
    namespace["load_run_detail"](cfg, "run-1")
    assert trace != expected


def test_canonical_projection_is_independent_effect_free_and_does_not_mutate_inputs(monkeypatch):
    inputs = _canonical_inputs()
    before = copy.deepcopy({k: v for k, v in inputs.items() if k != "facade"})
    def forbidden(*a, **kw):
        raise AssertionError("pure projection attempted IO/LLM")
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(core, "_iter_jsonl", forbidden)
    monkeypatch.setattr(core, "load_run_canonical_sources", forbidden)
    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(forbidden))
    result = owner._project_canonical_run(**inputs)
    assert result[15]["selected_candidate"] == {"why": "new", "retained": True}
    assert result[16] == {"monitor_reason": "new", "retained": True}
    assert {k: v for k, v in inputs.items() if k != "facade"} == before


@pytest.mark.parametrize("old,new", [(
    'elif scanner_provenance == "canonical":', 'elif False:'), (
    'elif monitor_provenance == "canonical":', 'elif False:'), (
    'strategic_frame = dict(strategist_summary or {})', 'strategic_frame = {}'), (
    'if not strategist_llm and isinstance', 'if False and isinstance')])
def test_hostile_canonical_and_trace_fallback_mutations_are_detected(old, new):
    source = Path(owner.__file__).read_text(encoding="utf-8")
    assert source.count(old) == 1
    namespace = dict(vars(owner))
    exec(compile(source.replace(old, new), "<hostile run-detail mutant>", "exec"), namespace)
    inputs = _canonical_inputs()
    inputs["strategist_summary"]["llm_metadata_summary"] = {"model": "offline"}
    assert _bytes(namespace["_project_canonical_run"](**inputs)) != _bytes(owner._project_canonical_run(**inputs))
