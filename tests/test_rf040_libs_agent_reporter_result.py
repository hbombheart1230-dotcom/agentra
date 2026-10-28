"""RF-040 libs/agent C2/C3: Reporter._result / _build_reporter_input / generate_daily_report.

The report generator is monkeypatched and all paths live under tmp_path; no
runtime logs, reports tree, LLM or network is used. Explicit raises keep the
checks live under ``python -O``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import libs.reporting.daily_report_generator as drg
from libs.agent.reporter import Reporter
from libs.agent.reporter_outputs import ReporterOutput


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


_FEEDBACK = {"preset": True}


def test_build_reporter_input_surfaces_and_counts(tmp_path):
    payload = {"day": "D", "report_md_path": "a.md", "report_json_path": "a.json",
               "route_summary": {"r": 1}, "data_freshness": {"source_run_count": 3, "latest_run_id": "x"},
               "narrative_axis_policy": {"p": 1}}
    ri = Reporter()._build_reporter_input(mode="m", reports_root=str(tmp_path), payload=payload)
    _eq(ri.available_surfaces, ["markdown", "json", "route_summary", "data_freshness", "narrative_axis_policy"])
    _eq((ri.day, ri.source_run_count, ri.latest_run_id, ri.generation_mode, ri.flags), ("D", 3, "x", "deterministic", {"mode": "m"}))
    _eq((ri.reports_root, ri.canonical_report_root), (tmp_path, tmp_path))
    bare = Reporter()._build_reporter_input(mode="m", reports_root=tmp_path, payload={}, flags={"day": None})
    _eq((bare.available_surfaces, bare.flags, bare.narrative_axis_policy), ([], {"day": None}, None))


def test_result_warns_on_missing_provenance_and_paths(tmp_path):
    out = Reporter()._result(mode="m", payload={"strategist_feedback_packet": _FEEDBACK})
    _eq(out.warnings, ["missing_data_freshness", "missing_route_provenance",
                       "missing_report_json_path", "missing_report_md_path"])
    _eq(out.success, False)
    _eq(out.strategist_feedback_packet, _FEEDBACK)
    _eq((out.report_type, out.output_paths), ("m", {"md": "", "json": ""}))
    _eq(out.payload["mode"], "m")


def test_result_success_when_complete_and_paths_recorded(tmp_path):
    md, js = tmp_path / "reports" / "r.md", tmp_path / "reports" / "r.json"
    payload = {"day": "D", "generated_at": "T", "data_freshness": {"source_run_count": 2},
               "route_provenance": {"k": 1}, "strategist_feedback_packet": _FEEDBACK, "operator_packet": {"o": 1}}
    out = Reporter()._result(mode="daily_report", payload=payload, report_md_path=md, report_json_path=js)
    _eq((out.success, out.warnings), (True, []))
    _eq(out.output_paths, {"md": str(md), "json": str(js)})
    _eq((out.generated_at, out.operator_packet), ("T", {"o": 1}))
    _eq(out.summary_metadata["source_run_count"], 2)
    _eq(out.summary_metadata["reporter_input"]["reports_root"], str(tmp_path / "reports"))
    _eq(out.summary_metadata["available_surfaces"], ["markdown", "json", "data_freshness"])
    if not isinstance(out, ReporterOutput):
        raise AssertionError("must return ReporterOutput")


def test_generate_daily_report_uses_generator_and_reads_json(tmp_path, monkeypatch):
    seen = {}
    md, js = tmp_path / "out" / "d.md", tmp_path / "out" / "d.json"
    js.parent.mkdir()
    js.write_text(json.dumps({"day": "20261028", "data_freshness": {"a": 1}, "route_provenance": {"b": 1},
                              "strategist_feedback_packet": _FEEDBACK}), encoding="utf-8")

    def fake(events, root, day=None):
        seen.update(events=events, root=root, day=day)
        return md, js

    monkeypatch.setattr(drg, "generate_daily_report", fake)
    out = Reporter().generate_daily_report(event_log_path=str(tmp_path / "e.jsonl"), reports_root=str(tmp_path), day=" 20261028 ")
    _eq(seen, {"events": tmp_path / "e.jsonl", "root": tmp_path, "day": "20261028"})
    _eq((out.report_type, out.success, out.report_md_path, out.report_json_path), ("daily_report", True, str(md), str(js)))
    _eq(out.summary_metadata["reporter_input"]["flags"], {"day": "20261028"})
    _eq(Reporter().run(mode="daily_report", event_log_path=str(tmp_path / "e.jsonl"), reports_root=str(tmp_path)).report_type, "daily_report")


def test_generate_daily_report_with_missing_json_degrades_to_warnings(tmp_path, monkeypatch):
    monkeypatch.setattr(drg, "generate_daily_report", lambda e, r, day=None: (tmp_path / "m.md", tmp_path / "missing.json"))
    out = Reporter().generate_daily_report(reports_root=tmp_path)
    _eq(out.success, False)
    if "missing_data_freshness" not in out.warnings:
        raise AssertionError(out.warnings)
    _eq(out.payload["mode"], "daily_report")


def test_generator_exception_propagates(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("gen failed")

    monkeypatch.setattr(drg, "generate_daily_report", boom)
    with pytest.raises(RuntimeError):
        Reporter().generate_daily_report(reports_root=tmp_path)
