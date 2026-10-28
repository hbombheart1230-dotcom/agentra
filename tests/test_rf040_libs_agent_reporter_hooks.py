"""RF-040 libs/agent C2/C3: remaining Reporter generators and commander hooks.

Every libs.reporting generator is monkeypatched; outputs live under tmp_path.
The hooks must stay report-only (no execution/route/threshold authority).
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json

import pytest

import libs.reporting.metrics_report_generator as mrg
import libs.reporting.operator_visibility as ov
import libs.reporting.trade_explain as te
from libs.agent import reporter as rep
from libs.agent.reporter import Reporter
from libs.agent.reporter_outputs import ReporterOutput

_FB = {"strategist_feedback_packet": {"p": 1}}


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({**_FB, **payload}), encoding="utf-8")
    return path


def test_operator_summary_default_subdirs_and_day(tmp_path, monkeypatch):
    seen = {}
    js = _json(tmp_path / "o.json", {"day": "D"})

    def fake(events, root, **kw):
        seen.update(events=events, root=root, **kw)
        return tmp_path / "o.md", js

    monkeypatch.setattr(ov, "generate_operator_daily_summary", fake)
    out = Reporter().generate_operator_summary(event_log_path=tmp_path / "e", report_dir=tmp_path / "r", day=" D ")
    _eq(seen["day"], "D")
    _eq(seen["metrics_report_dir"], tmp_path / "r" / "metrics")
    _eq(seen["m30_post_golive_dir"], tmp_path / "r" / "milestones" / "m30_post_golive")
    _eq(seen["m30_golive_dir"], tmp_path / "r" / "milestones" / "m30_golive")
    _eq(seen["m31_slo_incident_dir"], tmp_path / "r" / "milestones" / "m31_slo_incident")
    _eq((out.report_type, out.report_json_path), ("operator_summary", str(js)))


def test_trade_explain_clamps_limits_and_uses_official_dir(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(te, "official_trade_explain_report_dir", lambda root: root / "official")

    def fake(events, target, **kw):
        seen.update(target=target, **kw)
        return tmp_path / "t.md", tmp_path / "t.json", {"day": "D", **_FB}

    monkeypatch.setattr(te, "generate_trade_explain_report", fake)
    out = Reporter().generate_trade_explain(event_log_path=tmp_path / "e", reports_root=tmp_path, max_executions=0, max_sell_pairs=-5)
    _eq((seen["target"], seen["max_executions"], seen["max_sell_pairs"]), (tmp_path / "official", 1, 1))
    _eq(out.summary_metadata["reporter_input"]["flags"], {"day": None, "max_executions": 1, "max_sell_pairs": 1})
    Reporter().generate_trade_explain(event_log_path=tmp_path / "e", report_dir=tmp_path / "custom")
    _eq(seen["target"], tmp_path / "custom")


def test_metrics_report_reports_root_depends_on_dir_name(tmp_path, monkeypatch):
    monkeypatch.setattr(mrg, "generate_metrics_report", lambda e, d, day=None: (d / "m.md", _json(d / "m.json", {})))
    a = Reporter().generate_metrics_report(report_dir=tmp_path / "metrics")
    b = Reporter().generate_metrics_report(report_dir=tmp_path / "other")
    _eq(a.summary_metadata["reporter_input"]["reports_root"], str(tmp_path))
    _eq(b.summary_metadata["reporter_input"]["reports_root"], str(tmp_path / "other"))


@pytest.mark.parametrize("name,mode", [("generate_run_card_report", "run_cards"), ("generate_decision_story_report", "decision_story")])
def test_run_cards_and_decision_story_clamp_and_md_only(tmp_path, monkeypatch, name, mode):
    seen = {}

    def fake(events, out_dir, **kw):
        seen.update(kw)
        return tmp_path / "c.md", {"day": "D", **_FB}

    monkeypatch.setattr(ov, name, fake)
    method = getattr(Reporter(), "generate_" + mode)
    out = method(event_log_path=tmp_path / "e", report_dir=tmp_path / "out", max_runs=-3, trade_only=0)
    _eq(seen, {"day": None, "max_runs": 0, "trade_only": False})
    _eq(out.report_type, mode)
    _eq(out.report_json_path, "")
    if "missing_report_json_path" not in out.warnings:
        raise AssertionError(out.warnings)


def test_hooks_disabled_and_reserved_do_not_generate(tmp_path, monkeypatch):
    r = Reporter()

    def boom(*a, **k):
        raise AssertionError("generator must not run")

    for n in ("generate_operator_summary", "generate_daily_report", "generate_metrics_report"):
        monkeypatch.setattr(r, n, boom)
    for hook, name in ((r.maybe_generate_intraday_summary, "intraday_summary"), (r.maybe_generate_eod_reports, "eod_reports")):
        d = hook()
        _eq((d["hook_name"], d["status"], d["enabled"], d["executed"]), (name, "disabled", False, False))
        s = hook(enabled=True, day=" 20261028 ")
        _eq((s["status"], s["reason"], s["executed"], s["day"]), ("reserved", "report_generation_disabled", False, "20261028"))
    for h in (d, s):
        _eq((h["execution_authority"], h["route_override_authority"], h["threshold_override_authority"], h["report_only"]), (False, False, False, True))


def test_intraday_and_eod_generated_paths(tmp_path, monkeypatch):
    r = Reporter()

    def make(mode, md, js, warn):
        return ReporterOutput(report_type=mode, output_paths={"md": md, "json": js}, warnings=warn, data_freshness={"f": 1})

    monkeypatch.setattr(r, "generate_operator_summary", lambda **kw: make("operator_summary", "o.md", "o.json", ["w1"]))
    monkeypatch.setattr(r, "generate_daily_report", lambda **kw: make("daily_report", "d.md", "", ["w2"]))
    monkeypatch.setattr(r, "generate_metrics_report", lambda **kw: make("metrics_report", "", "m.json", []))
    i = r.maybe_generate_intraday_summary(enabled=True, emit_reports=True)
    _eq((i["status"], i["executed"], i["report_type"], i["generated_reports"], i["warnings"], i["data_freshness"]),
        ("generated", True, "operator_summary", ["operator_summary"], ["w1"], {"f": 1}))
    e = r.maybe_generate_eod_reports(enabled=True, emit_reports=True, reports_root=tmp_path)
    _eq(e["output_paths"], {"daily_report_md": "d.md", "operator_summary_json": "o.json", "operator_summary_md": "o.md", "metrics_report_json": "m.json"})
    _eq((e["report_type"], e["generated_reports"]), ("eod_bundle", ["daily_report", "operator_summary", "metrics_report"]))
    _eq(e["warnings"], ["w2", "w1"])


def test_strategist_feedback_hook(tmp_path, monkeypatch):
    r = Reporter()
    off = r.maybe_generate_strategist_feedback()
    _eq((off["status"], off["strategist_feedback_packet"], off["strategist_feedback_reserved"]), ("disabled", None, True))
    seen = {}

    def fake(**kw):
        seen.update(kw)
        return {"packet": 1}

    monkeypatch.setattr(rep, "build_strategist_feedback_packet", fake)
    on = r.maybe_generate_strategist_feedback(enabled=True, day=" D ", reports_root=tmp_path)
    _eq(seen, {"mode": "strategist_feedback", "payload": {"day": "D"}, "reports_root": tmp_path, "day": "D"})
    _eq((on["status"], on["executed"], on["strategist_feedback_packet"], on["execution_authority"]), ("generated", True, {"packet": 1}, False))
