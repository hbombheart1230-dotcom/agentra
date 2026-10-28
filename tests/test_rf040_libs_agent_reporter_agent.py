"""RF-040 libs/agent C2/C3: run_reporter_agent and analyze_event_logs (mocked).

build_trade_read_model / build_separated_report / generate_reporter_analysis_report
are monkeypatched, so no LLM call, network or runtime file is touched.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import libs.reporting.fact_narrative_report as fnr
import libs.reporting.reporter_analysis as ra
import libs.reporting.trade_read_model as trm
from libs.agent.reporter import Reporter, run_reporter_agent


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _boom_builder(*a, **k):
    raise AssertionError("separated report (LLM) must not be built")


def test_read_model_exception_degrades_without_building_report(monkeypatch, tmp_path):
    def raising(path):
        raise RuntimeError("bad dir")

    monkeypatch.setattr(trm, "build_trade_read_model", raising)
    monkeypatch.setattr(fnr, "build_separated_report", _boom_builder)
    out = run_reporter_agent(str(tmp_path))
    _eq(out["status"], "degraded")
    _eq(out["narrative"], {"status": "error", "source": "llm", "based_on": "fact_payload",
                           "reason": "trade_read_model_exception", "error": "bad dir"})
    _eq(out["metadata"], {"trade_id": "", "symbol": "", "trade_dir": str(tmp_path), "generated_by": "reporter_agent_v1"})
    _eq((out["facts"], out["provenance"]), ({}, {}))


def test_invalid_read_model_skips_llm(monkeypatch, tmp_path):
    monkeypatch.setattr(trm, "build_trade_read_model", lambda p: {"trade_id": "T", "symbol": "S", "facts": {}, "provenance": {"p": 1}})
    monkeypatch.setattr(fnr, "build_separated_report", _boom_builder)
    out = run_reporter_agent(tmp_path)
    _eq(out["status"], "degraded")
    _eq(out["narrative"]["reason"], "trade_read_model_facts_missing")
    _eq(out["narrative"]["llm_call_skipped"], True)
    _eq((out["metadata"]["trade_id"], out["metadata"]["symbol"], out["provenance"]), ("T", "S", {"p": 1}))


def test_valid_model_passes_policy_and_maps_status(monkeypatch, tmp_path):
    model = {"trade_id": "T0", "facts": {"trade_id": "T1", "symbol": "S"}, "provenance": {"p": 1}, "context": {"c": 1}}
    monkeypatch.setattr(trm, "build_trade_read_model", lambda p: model)
    seen = {}
    narr = {"status": "dry_run"}

    def fake(**kw):
        seen.update(kw)
        return {"narrative": dict(narr)}

    monkeypatch.setattr(fnr, "build_separated_report", fake)
    out = run_reporter_agent(str(tmp_path), policy={"model": " m ", "execution_profile": {"x": 1}})
    _eq((seen["model"], seen["execution_profile"]), ("m", {"x": 1}))
    _eq(out["status"], "ok")
    _eq(out["metadata"], {"trade_id": "T1", "symbol": "S", "trade_dir": str(tmp_path), "generated_by": "reporter_agent_v1"})
    _eq((out["facts"], out["context"]), ({"trade_id": "T1", "symbol": "S"}, {"c": 1}))
    for st, want in (("ok", "ok"), ("SKIPPED", "ok"), ("error", "degraded"), ("", "degraded")):
        narr["status"] = st
        _eq(run_reporter_agent(str(tmp_path))["status"], want)
    run_reporter_agent(str(tmp_path))
    _eq((seen["model"], seen["execution_profile"]), (None, None))  # empty policy -> None


def test_non_dict_narrative_is_degraded(monkeypatch, tmp_path):
    monkeypatch.setattr(trm, "build_trade_read_model", lambda p: {"facts": {"a": 1}, "provenance": {"p": 1}})
    monkeypatch.setattr(fnr, "build_separated_report", lambda **kw: {"narrative": "text"})
    out = run_reporter_agent(str(tmp_path))
    _eq((out["status"], out["narrative"]), ("degraded", {}))


def test_analyze_event_logs_clamps_and_conditional_intents_path(monkeypatch, tmp_path):
    seen = {}

    def fake(events, report_dir, **kw):
        seen.update(events=events, report_dir=report_dir, **kw)
        return "md", "js", {"ok": True}

    monkeypatch.setattr(ra, "generate_reporter_analysis_report", fake)
    intents = tmp_path / "intents.jsonl"
    out = Reporter().analyze_event_logs(event_log_path=tmp_path / "e", report_dir=tmp_path / "r", intents_path=intents,
                                        reports_root=tmp_path, rapid_cycle_threshold_sec=0, ai_review_max_tokens=10)
    _eq(out, {"ok": True})
    _eq((seen["intents_path"], seen["rapid_cycle_threshold_sec"], seen["ai_review_max_tokens"]), (None, 1, 256))
    intents.write_text("", encoding="utf-8")
    Reporter().analyze_event_logs(event_log_path=tmp_path / "e", report_dir=tmp_path / "r", intents_path=intents, reports_root=tmp_path)
    _eq((seen["intents_path"], seen["rapid_cycle_threshold_sec"], seen["ai_review_max_tokens"]), (intents, 120, 900))


def test_run_wraps_reporter_analysis_dict_into_output(monkeypatch, tmp_path):
    r = Reporter()
    monkeypatch.setattr(r, "analyze_event_logs", lambda **kw: {"report_md_path": str(tmp_path / "a.md"), "report_json_path": str(tmp_path / "a.json"),
                                                               "data_freshness": {"f": 1}, "route_provenance": {"r": 1},
                                                               "strategist_feedback_packet": {"p": 1}})
    out = r.run(mode="reporter_analysis")
    _eq((out.report_type, out.success, out.warnings), ("reporter_analysis", True, []))
    _eq(out.output_paths, {"md": str(tmp_path / "a.md"), "json": str(tmp_path / "a.json")})
