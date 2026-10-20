"""P1.5 CODE BATCH 01 DEV-A: Reporter analysis read-model projection.

The BASE ``generate_reporter_analysis_report`` (exec'd from the pinned BASE blob against the LIVE facade globals) and the
current facade are run on identical bounded temp inputs. JSON/Markdown bytes, return value, LLM call count/arguments,
memory/ledger write order and degraded fallbacks must match. Every effect (LLM, strategy memory, evidence ledger) is a
recording fake, so no production path is written. The extracted projection is also called directly with stub facades.
"""
from __future__ import annotations

import ast
import copy
import json
import subprocess
import types
from pathlib import Path

import pytest

import libs.reporting.reporter_analysis as ra
from libs.agents.reporter.read_models import analysis_report_projection as proj

ROOT = Path(__file__).resolve().parents[1]
BASE = "4b0c3e0b5f8f24fa3c10d9082b85fab63f15c4c3"
DAY = "2026-03-10"


def _base_generate():
    src = subprocess.check_output(["git", "show", f"{BASE}:libs/reporting/reporter_analysis.py"], cwd=ROOT).decode("utf-8-sig")
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "generate_reporter_analysis_report")
    ns = dict(ra.__dict__)
    exec(compile("from __future__ import annotations\n" + ast.get_source_segment(src, node), "<base-generate>", "exec"), ns)
    f = ns["generate_reporter_analysis_report"]
    ref = types.FunctionType(f.__code__, ra.__dict__, f.__name__, f.__defaults__, f.__closure__)
    ref.__kwdefaults__ = f.__kwdefaults__
    return ref


def _write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def _events(tmp: Path, extra=()) -> Path:
    ev = tmp / "events.jsonl"
    _write_jsonl(ev, [*extra,
        {"run_id": "r1", "ts": f"{DAY}T00:00:00+00:00", "stage": "strategist", "event": "summary",
         "payload": {"themes": ["semiconductor"], "report_focus": ["Check monitor exit quality"]}},
        {"run_id": "r1", "ts": f"{DAY}T00:00:01+00:00", "stage": "scanner", "event": "summary",
         "payload": {"top_stock": "005930", "top_score": 0.91}},
        {"run_id": "r1", "ts": f"{DAY}T00:00:02+00:00", "stage": "decision_trace", "event": "snapshot",
         "payload": {"agent": "monitor", "payload": {"entry_reason": "entry_signal", "monitor_reason": "hold"}}},
        {"run_id": "r1", "ts": f"{DAY}T00:00:03+00:00", "stage": "execute_from_packet", "event": "verdict",
         "payload": {"allowed": False, "reason": "risk_limit"}},
        {"run_id": "r1", "ts": f"{DAY}T00:00:04+00:00", "stage": "monitor", "event": "summary",
         "payload": {"min_hold_blocked": True, "monitor_reason": "hold"}},
        {"run_id": "r1", "ts": f"{DAY}T00:00:05+00:00", "stage": "decision", "event": "trace",
         "payload": {"decision_packet": {"intent": {"action": "BUY", "symbol": "005930", "qty": 1, "reason": "entry"}}}},
    ])
    return ev


AI_OK = {"enabled": True, "status": "ok", "model": "fake", "ai_summary": "summary",
         "ai_findings": ["Monitor held through risk_limit", "unlinked finding"],
         "ai_root_causes": ["risk_limit blocked entries"], "ai_improvement_suggestions": ["Tune monitor exits"],
         "ai_run_grade": "B", "ai_agent_evaluations": {"monitor": {"grade": "B"}},
         "ai_evidence_links": {"findings": [["intent_flow_analysis"], ["nonexistent_key"]], "root_causes": "bogus",
                               "improvements": [{"keys": ["monitor_evaluation"]}]}}


def _run(fn, tmp: Path, monkeypatch, *, ai, memory="ok", bridge="ok", events_present=True, flags=False, extra=(),
         threshold=120, ai_enabled=True):
    """Run ``fn`` with recording fakes for every effect; return (json bytes, md bytes, out, effect log)."""
    log = []
    for name in ("EVIDENCE_LEDGER_PATH", "STRATEGY_MEMORY_PATH", "STRATEGY_MEMORY_DAILY_DIR"):
        monkeypatch.setenv(name, str(tmp / "never_written" / name))

    def fake_ai(**kw):
        log.append(("llm", kw["day"], kw["enabled"], kw["model"], kw["temperature"], kw["max_tokens"],
                    sorted(kw["reporter_output"]), sorted(kw["reporter_output"]["ai_evidence_catalog"])))
        if isinstance(ai, Exception):
            raise ai
        return copy.deepcopy(ai)

    def fake_memory(*, run_id, reporter_output):
        log.append(("memory", run_id, sorted(reporter_output)))
        if memory == "raise":
            raise OSError("disk full")
        return {"run_id": run_id, "timestamp": "T0", "_strategy_memory_meta": {"strategy_memory_path": "mem.jsonl"}}

    def fake_raw(**kw):
        log.append(("raw_input", kw["run_id"], kw["stage"], kw["raw_input"]["day_row_count"]))

    def fake_bridge(**kw):
        log.append(("bridge", kw["run_id"], json.dumps(kw["decision_link"], sort_keys=True), sorted(kw["parsed_output"])))
        if bridge == "raise":
            raise RuntimeError("ledger down")

    monkeypatch.setattr(ra, "build_ai_reporter_review", fake_ai)
    monkeypatch.setattr(ra, "save_strategy_feedback", fake_memory)
    monkeypatch.setattr(ra, "record_raw_input", fake_raw)
    monkeypatch.setattr(ra, "record_decision_bridge", fake_bridge)
    ev = _events(tmp, extra) if events_present else tmp / "missing_events.jsonl"
    reports_root = tmp / "reports"
    md, js, out = fn(ev, reports_root / "reporter_analysis", day=DAY, reports_root=reports_root,
                     ai_review_enabled=ai_enabled, ai_review_model="fake", ai_review_temperature=0.1, ai_review_max_tokens=10,
                     rapid_cycle_threshold_sec=threshold,
                     generate_decision_story=flags, generate_run_cards=flags)
    return js.read_bytes(), md.read_bytes(), json.dumps(out, ensure_ascii=False), log


UNICODE_ROWS = (
    {"run_id": "r2", "ts": f"{DAY}T00:00:06+00:00", "stage": "strategist", "event": "summary",
     "payload": {"themes": ["반도체", "AI 🚀"], "report_focus": ["모니터 청산 품질 점검"]}},
    {"run_id": "r2", "ts": f"{DAY}T00:00:06+00:00", "stage": "strategist", "event": "summary",
     "payload": {"themes": ["반도체", "AI 🚀"], "report_focus": ["모니터 청산 품질 점검"]}},  # exact duplicate
    {"run_id": "r0", "ts": "2026-03-09T23:59:59+00:00", "stage": "execute_from_packet", "event": "verdict",
     "payload": {"allowed": False, "reason": "전일 이벤트"}},  # cross-day: must be filtered identically
    {"run_id": "r2", "ts": f"{DAY}T00:00:07+00:00", "stage": "noop", "event": "noop", "payload": {}},
)


SCENARIOS = {
    "ai_ok_with_links": dict(ai=AI_OK),
    "ai_exception_fallback": dict(ai=RuntimeError("llm boom")),
    "ai_empty_payload": dict(ai=None),
    "ai_partial_payload": dict(ai={"status": "ok", "ai_findings": ["only finding"]}),
    "memory_and_bridge_fail": dict(ai=AI_OK, memory="raise", bridge="raise"),
    "missing_event_log": dict(ai=AI_OK, events_present=False),
    "story_and_cards_enabled": dict(ai=AI_OK, flags=True),
    "ai_disabled": dict(ai={"enabled": False, "status": "disabled"}, ai_enabled=False),
    "unicode_cross_day_duplicate_rows": dict(ai=AI_OK, threshold=0, extra=UNICODE_ROWS),
}


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_current_facade_matches_base_bytes_effects_and_order(scenario, tmp_path, monkeypatch):
    base = _run(_base_generate(), tmp_path / "w", monkeypatch, **SCENARIOS[scenario])
    cur = _run(ra.generate_reporter_analysis_report, tmp_path / "w", monkeypatch, **SCENARIOS[scenario])
    assert cur == base
    js_bytes, _md, _out, log = cur
    assert [e[0] for e in log] == ["raw_input", "llm", "memory", "bridge"]
    assert not (tmp_path / "w" / "never_written").exists()
    doc = json.loads(js_bytes)
    assert doc["schema_version"] == "reporter_analysis.v1"
    if scenario == "ai_exception_fallback":
        assert doc["ai_review"]["status"] == "error" and doc["ai_review"]["reason"] == "ai_review_exception:llm boom"
    if scenario == "memory_and_bridge_fail":
        assert doc["strategy_memory_record"]["error"] == "strategy_memory_save_failed:disk full"


@pytest.mark.parametrize("flags", [False, True])
def test_exists_checks_keep_base_position_and_short_circuit(flags, tmp_path, monkeypatch):
    seqs = []
    for fn in (_base_generate(), ra.generate_reporter_analysis_report):
        seq = []
        real_exists, real_cat = Path.exists, ra._build_ai_evidence_catalog
        monkeypatch.setattr(Path, "exists", lambda p, _s=seq, _r=real_exists: (
            _s.append(("exists", p.name)) if p.name.startswith(("decision_story_", "run_cards_")) else None, _r(p))[1])
        monkeypatch.setattr(ra, "_safe_int", lambda v, d=0, _s=seq, _o=ra._safe_int: (_s.append(("int", v)), _o(v, d))[1])
        monkeypatch.setattr(ra, "_build_ai_evidence_catalog", lambda out, _s=seq, _r=real_cat: (_s.append(("cat",)), _r(out))[1])
        _run(fn, tmp_path / "w", monkeypatch, ai=AI_OK, flags=flags)
        monkeypatch.undo()
        seqs.append(seq)
    assert seqs[0] == seqs[1]
    # daily-operator _safe_int pair, then (only when enabled) the two existence checks, then the evidence catalog
    head = seqs[1][:seqs[1].index(("cat",)) + 1]
    checks = [("exists", f"decision_story_{DAY}.md"), ("exists", f"run_cards_{DAY}.md")] if flags else []
    assert [e[0] for e in head[-3 - len(checks):-1 - len(checks)]] == ["int", "int"]
    assert head[-1 - len(checks):] == checks + [("cat",)]


def test_late_monkeypatch_of_facade_helpers_is_honoured_like_base(tmp_path, monkeypatch):
    results = []
    for fn in (_base_generate(), ra.generate_reporter_analysis_report):
        calls = []
        monkeypatch.setattr(ra, "_hydrate_ai_evidence_details", lambda t, l, c, _c=calls: (_c.append(("hyd", list(t), l)), [{"h": len(t)}])[1])
        monkeypatch.setattr(ra, "_build_ai_evidence_catalog", lambda out, _c=calls: (_c.append(("cat", len(out))), {"k": {"v": 1}})[1])
        orig_int = ra._safe_int.__wrapped__ if hasattr(ra._safe_int, "__wrapped__") else ra._safe_int
        monkeypatch.setattr(ra, "_safe_int", lambda v, d=0, _c=calls, _o=orig_int: (_c.append(("int", v)), _o(v, d) + 7)[1])
        _js, _md, out, _log = _run(fn, tmp_path / "w", monkeypatch, ai=AI_OK)
        monkeypatch.undo()
        results.append((calls, out))
    assert results[0] == results[1]
    calls, out = results[1]
    assert [c[0] for c in calls if c[0] in ("cat", "hyd")] == ["cat", "hyd", "hyd", "hyd"]
    doc = json.loads(out)
    assert doc["ai_findings_detailed"] == [{"h": 2}] and doc["ai_evidence_catalog"] == {"k": {"v": 1}}
    assert doc["daily_operator_report"]["trades_executed"] >= 7


class _StubFacade:
    def __init__(self):
        self.calls = []

    def _safe_int(self, v, default=0):
        self.calls.append(("int", v))
        return int(v) if isinstance(v, int) else default

    def _build_ai_evidence_catalog(self, out):
        self.calls.append(("cat", list(out)))
        return {"intent_flow_analysis": {"label": "flow"}}

    def _ensure_min_ai_review_payload(self, *, out, ai_review):
        self.calls.append(("ensure", sorted(ai_review)))
        return {**ai_review, "ai_summary": ai_review.get("ai_summary") or "fallback summary"}

    def _hydrate_ai_evidence_details(self, texts, links, catalog):
        self.calls.append(("hyd", list(texts), links))
        return [{"text": t, "links": links} for t in texts]


def _base_kwargs(**over):
    kw = {k: {} for k in ("trade_summary", "decision_chains", "decision_trace_chain_summary", "trade_decision",
                         "strategy_frame_summary", "strategist_eval", "scanner_eval", "monitor_eval", "supervisor_activity",
                         "intent_flow", "strategy_eff", "overtrading", "daily_operator", "incident", "market_context",
                         "ds_obj", "rc_obj")}
    kw.update(target_day=DAY, improvement_suggestions=["s"], report_views={"operator_facing_summary": {"o": 1}},
              report_focus_targets=("t1",), trade_js=Path("a.json"), trade_md=Path("a.md"), op_js=Path("b.json"),
              op_md=Path("b.md"), generate_decision_story=0, generate_run_cards="yes", ds_md=Path("ds.md"),
              rc_md=Path("rc.md"), path_exists=lambda p: True, js_path=Path("r.json"), md_path=Path("r.md"))
    kw.update(over)
    return kw


def test_projection_is_independently_callable_with_explicit_inputs():
    fac = _StubFacade()
    out = proj.build_base_report(**_base_kwargs(ds_obj={"story_total": "3"}), facade=fac)
    assert list(out)[:2] == ["schema_version", "day"] and list(out)[-1] == "ai_evidence_catalog"
    assert out["schema_version"] == "reporter_analysis.v1" and out["developer_facing_summary"] == {}
    assert out["report_focus_targets"] == ["t1"] and out["source_reports"]["decision_story_total"] == 3
    assert out["source_reports"]["decision_story_enabled"] is False and out["source_reports"]["run_cards_enabled"] is True
    assert fac.calls == [("cat", list(out)[:-1])]
    daily = proj.build_daily_operator_report(
        op_obj={"trading_activity_summary": {"executions_total": 4, "blocked_total": "x", "strategy_counts": dict.fromkeys("abcdefg", 1)}},
        market_context={"m": 1}, incident={"incidents": [{"type": "halt"}, "junk", {"no_type": 1}]}, facade=fac)
    assert daily == {"market_context": {"m": 1}, "trades_executed": 4, "trades_blocked": 0,
                     "major_decisions": list("abcde"), "anomalies": ["halt", None]}
    assert proj.build_daily_operator_report(op_obj={"trading_activity_summary": ["bad"]}, market_context={}, incident={},
                                            facade=fac)["major_decisions"] == []


def test_ai_projection_keeps_evidence_links_and_degraded_fallback():
    fac = _StubFacade()
    out = {"ai_evidence_catalog": {"k": {}}}
    proj.apply_ai_review_projection(out, None, facade=fac)
    assert out["ai_summary"] == "fallback summary" and out["ai_run_grade"] == "N/A" and out["ai_evidence_links"] == {}
    assert out["ai_findings_detailed"] == [] and [c[0] for c in fac.calls] == ["ensure", "hyd", "hyd", "hyd"]
    fac.calls.clear()
    proj.apply_ai_review_projection(out, copy.deepcopy(AI_OK), facade=fac)
    assert [c[2] for c in fac.calls if c[0] == "hyd"] == [[["intent_flow_analysis"], ["nonexistent_key"]], "bogus",
                                                          [{"keys": ["monitor_evaluation"]}]]
    assert list(out)[-3:] == ["ai_findings_detailed", "ai_root_causes_detailed", "ai_improvement_suggestions_detailed"]
    err = proj.ai_review_error_payload(ValueError("x"), enabled=None, model=None)
    assert err["enabled"] is False and err["model"] == "" and err["reason"] == "ai_review_exception:x"
    assert "ai_evidence_links" not in err and err["ai_run_grade"] == "N/A"


def test_projection_hostile_inputs_fail_like_base_instead_of_masking():
    fac = _StubFacade()
    with pytest.raises((TypeError, ValueError)):
        proj.apply_ai_review_projection({"ai_evidence_catalog": {}}, {"ai_evidence_links": ["not", "a", "dict"]}, facade=fac)
    with pytest.raises(KeyError):
        proj.apply_ai_review_projection({}, {}, facade=fac)  # catalog must exist (built by build_base_report)
    with pytest.raises(TypeError):
        proj.build_base_report(**_base_kwargs())  # facade is an explicit required dependency


def test_projection_module_has_no_io_llm_or_effect_imports():
    tree = ast.parse((ROOT / "libs/agents/reporter/read_models/analysis_report_projection.py").read_text(encoding="utf-8"))
    mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | \
        {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert mods == {"__future__", "typing"}
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not names & {"open", "write_text", "read_text", "exists", "mkdir", "build_ai_reporter_review",
                        "save_strategy_feedback", "record_decision_bridge", "record_raw_input"}


def _gen_node(src):
    return next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "generate_reporter_analysis_report")


def test_facade_generate_signature_and_delegation_are_kept():
    base_src = subprocess.check_output(["git", "show", f"{BASE}:libs/reporting/reporter_analysis.py"], cwd=ROOT).decode("utf-8-sig")
    cur_src = (ROOT / "libs/reporting/reporter_analysis.py").read_text(encoding="utf-8-sig")
    base, cur = _gen_node(base_src), _gen_node(cur_src)
    assert ast.dump(cur.args) == ast.dump(base.args) and ast.dump(cur.returns) == ast.dump(base.returns)
    assert ast.get_docstring(cur) == ast.get_docstring(base)
    seg = ast.get_source_segment(cur_src, cur)
    for name in ("build_daily_operator_report", "build_base_report", "ai_review_error_payload", "apply_ai_review_projection"):
        assert f"_analysis_projection.{name}(" in seg
    assert ra._analysis_projection is proj
    assert len(seg.splitlines()) < len(ast.get_source_segment(base_src, base).splitlines())


BUILDERS = ("_build_trade_decision_summaries", "_build_intent_flow_analysis", "_build_strategy_effectiveness",
            "_extract_report_focus_targets", "_build_overtrading_diagnostics", "_build_incident_postmortem",
            "_build_market_context", "_build_strategy_frame_summary", "_build_decision_chains",
            "_build_decision_trace_chain_summary", "_build_trade_summary_section", "_build_strategist_evaluation",
            "_build_scanner_evaluation", "_build_monitor_evaluation", "_build_supervisor_activity",
            "_build_improvement_suggestions", "_build_report_views", "_build_ai_evidence_catalog")


def _spy_builders(monkeypatch, seq, *, override=None):
    for name in BUILDERS:
        real = getattr(ra, name)

        def spy(*a, _n=name, _r=real, **k):
            seq.append(_n)
            if override and _n == override[0]:
                return override[1]
            return _r(*a, **k)
        monkeypatch.setattr(ra, name, spy)


def test_section_builders_run_in_base_order_and_honour_late_patch(tmp_path, monkeypatch):
    results = []
    for fn in (_base_generate(), ra.generate_reporter_analysis_report):
        seq = []
        _spy_builders(monkeypatch, seq, override=("_build_market_context", {"regime": "패치됨"}))
        res = _run(fn, tmp_path / "w", monkeypatch, ai=AI_OK, extra=UNICODE_ROWS)
        monkeypatch.undo()
        results.append((seq, res))
    assert results[0] == results[1]
    seq, (js, _md, _out, _log) = results[1]
    assert seq == list(BUILDERS)
    doc = json.loads(js)
    assert doc["market_context"] == {"regime": "패치됨"} == doc["daily_operator_report"]["market_context"]


@pytest.mark.parametrize("threshold", ["not-a-number", None])
def test_invalid_threshold_raises_at_the_base_point(threshold, tmp_path, monkeypatch):
    outcomes = []
    for fn in (_base_generate(), ra.generate_reporter_analysis_report):
        seq = []
        _spy_builders(monkeypatch, seq)
        with pytest.raises((ValueError, TypeError)) as exc:
            _run(fn, tmp_path / "w", monkeypatch, ai=AI_OK, threshold=threshold)
        monkeypatch.undo()
        outcomes.append((type(exc.value), str(exc.value), seq))
    assert outcomes[0] == outcomes[1]
    assert outcomes[1][2] == list(BUILDERS[:4])  # raised before overtrading; no LLM/memory/bridge/write afterwards
    assert not list((tmp_path / "w" / "reports" / "reporter_analysis").glob("reporter_analysis_*"))


def test_section_projection_is_independently_callable():
    calls = []

    class Fac:
        def __getattr__(self, name):
            def f(*a, **k):
                calls.append(name)
                return {"from": name}
            return f
    sec = proj.build_analysis_sections(day_rows=[], trade_obj={}, trade_decision={}, intent_flow={}, target_day=DAY,
                                       rapid_cycle_threshold_sec="5", facade=Fac())
    assert calls == list(BUILDERS[2:17])
    assert list(sec) == ["strategy_eff", "report_focus_targets", "overtrading", "incident", "market_context",
                         "strategy_frame_summary", "decision_chains", "decision_trace_chain_summary", "trade_summary",
                         "strategist_eval", "scanner_eval", "monitor_eval", "supervisor_activity",
                         "improvement_suggestions", "report_views"]
    with pytest.raises(ValueError):
        proj.build_analysis_sections(day_rows=[], trade_obj={}, trade_decision={}, intent_flow={}, target_day=DAY,
                                     rapid_cycle_threshold_sec="x", facade=Fac())
