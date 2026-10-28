"""RF-040 libs/agent C2/C3: reporter DTOs and pure Reporter helpers.

tmp_path / in-memory only; no report generators, LLM or runtime files are run.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path
from types import SimpleNamespace

import pytest

from libs.agent import reporter as rep
from libs.agent.reporter import Reporter, _normalize_trade_reporter_policy, _validate_trade_read_model
from libs.agent.reporter_inputs import ReporterInput
from libs.agent.reporter_outputs import ReporterOutput


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_reporter_input_defaults_and_to_dict_copies():
    ri = ReporterInput(day="20261028", reports_root=Path("r"), canonical_report_root=Path("c"),
                       run_ids=["a"], route_summary={"k": 1}, narrative_axis_policy={"p": 1})
    d = ri.to_dict()
    _eq(d["reports_root"], "r")
    _eq((d["generation_mode"], d["source_run_count"], d["latest_run_id"]), ("deterministic", 0, ""))
    d["run_ids"].append("z")
    d["route_summary"]["k"] = 2
    _eq(ri.run_ids, ["a"])
    _eq(ri.route_summary, {"k": 1})
    _eq(ReporterInput("d", Path("a"), Path("b")).to_dict()["narrative_axis_policy"], None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ri.day = "x"  # type: ignore[misc]


def test_reporter_output_mapping_contract():
    out = ReporterOutput(report_type="daily_report", output_paths={"md": "a.md"},
                         payload={"day": "20261028", "report_json_path": "p.json"})
    _eq(out.mode, "daily_report")
    _eq((out.report_md_path, out.report_json_path), ("a.md", "p.json"))
    _eq(out["day"], "20261028")
    _eq(out.get("missing", 7), 7)
    _eq(out.get("success"), True)
    _eq(len(out), len(list(iter(out))))
    _eq(out.to_dict()["narrative_axis_policy"], None)
    with pytest.raises(KeyError):
        out["nope"]
    # day falls back to summary_metadata, paths default to empty strings
    bare = ReporterOutput(report_type="x", summary_metadata={"day": "D"})
    _eq((bare["day"], bare.report_md_path, bare.report_json_path), ("D", "", ""))


def test_reporter_build_summarizes_without_side_effects():
    plan = SimpleNamespace(thesis="t")
    out = Reporter().build(run_id="r", context={"b": 1, "a": 2}, plan=plan, intents=[{"i": 1}, {"i": 2}],
                           decisions=[], executions=[{"e": 1}])
    _eq(out, {"run_id": "r", "plan": {"thesis": "t"}, "intents_count": 2, "decisions_count": 0,
              "executions_count": 1, "latest_intent": {"i": 2}, "latest_decision": {},
              "latest_execution": {"e": 1}, "context_keys": ["a", "b"]})
    _eq(Reporter().build(run_id="r", context={}, plan="p", intents=[], decisions=[], executions=[])["plan"], "p")


def test_hook_result_is_report_only_with_no_authority():
    h = Reporter()._hook_result(hook_name="strategist_feedback", enabled=1, status="ok", day=" 20261028 ",
                                strategist_feedback_packet={"a": 1})
    for k in ("execution_authority", "route_override_authority", "threshold_override_authority"):
        _eq(h[k], False)
    _eq((h["report_only"], h["strategist_feedback_reserved"], h["enabled"], h["day"]), (True, True, True, "20261028"))
    _eq(h["strategist_feedback_packet"], {"a": 1})
    other = Reporter()._hook_result(hook_name="eod", enabled=False, status="skipped", day="  ")
    _eq((other["day"], other["strategist_feedback_reserved"], other["strategist_feedback_packet"]), (None, False, None))


def test_read_json_tolerates_missing_bad_and_non_dict(tmp_path):
    r = Reporter()
    _eq(r._read_json(tmp_path / "nope.json"), {})
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    (tmp_path / "list.json").write_text("[1]", encoding="utf-8")
    (tmp_path / "ok.json").write_text('{"a": 1}', encoding="utf-8")
    _eq((r._read_json(tmp_path / "bad.json"), r._read_json(tmp_path / "list.json")), ({}, {}))
    _eq(r._read_json(tmp_path / "ok.json"), {"a": 1})


def test_guess_reports_root_and_path_helpers():
    r = Reporter()
    _eq(r._guess_reports_root(None), Path("."))
    _eq(r._guess_reports_root(Path("x/reports/2026/a.md")), Path("x/reports"))
    _eq(r._guess_reports_root(Path("x/y/a.md")), Path("x/y"))
    _eq(r._guess_reports_root(Path("x/y")), Path("x/y"))
    _eq(r._path("a/b"), Path("a/b"))
    _eq(r._normalize_day(None), None)


def test_run_rejects_unknown_mode_and_wraps_non_output_result(monkeypatch):
    r = Reporter()
    with pytest.raises(ValueError):
        r.run(mode="nope")
    monkeypatch.setattr(r, "generate_metrics_report", lambda **kw: {"x": kw})
    _eq(r.run(mode=" metrics_report ", a=1), {"mode": "metrics_report", "payload": {"x": {"a": 1}}})
    sentinel = ReporterOutput(report_type="daily_report")
    monkeypatch.setattr(r, "generate_daily_report", lambda **kw: sentinel)
    if r.run(mode="daily_report") is not sentinel:
        raise AssertionError("ReporterOutput must pass through unchanged")


def test_trade_policy_and_read_model_validation():
    _eq(_normalize_trade_reporter_policy(None), {"model": "", "execution_profile": {}})
    _eq(_normalize_trade_reporter_policy({"model": " m ", "execution_profile": {"a": 1}}), {"model": "m", "execution_profile": {"a": 1}})
    _eq(_normalize_trade_reporter_policy({"execution_profile": "bad"})["execution_profile"], {})
    _eq(_validate_trade_read_model({}), {"ok": False, "reason": "trade_read_model_missing"})
    _eq(_validate_trade_read_model("x"), {"ok": False, "reason": "trade_read_model_missing"})
    _eq(_validate_trade_read_model({"facts": {}})["reason"], "trade_read_model_facts_missing")
    _eq(_validate_trade_read_model({"facts": {"a": 1}})["reason"], "trade_read_model_provenance_missing")
    _eq(_validate_trade_read_model({"facts": {"a": 1}, "provenance": {"b": 1}}), {"ok": True, "reason": ""})
    if not hasattr(rep, "run_reporter_agent"):
        raise AssertionError("run_reporter_agent entrypoint must remain")
