"""P15 RF-035 (00h): daily_report_generator._load_operator_summary_snapshot moved to daily_report_generator_operator_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import daily_report_generator as m
from libs.reporting import daily_report_generator_operator_projection as owner


def _both(events, out, day):
    return m._load_operator_summary_snapshot(events, out, day), owner._load_operator_summary_snapshot(events, out, day, facade=m)


def _patch(monkeypatch, tmp_path, calls):
    monkeypatch.setattr(m, "daily_artifact_paths", lambda out, day: {"operator_summary_json": tmp_path / "os.json", "operator_summary_md": tmp_path / "os.md"})

    def payload(events, out, **kw):
        calls.append((events, out, kw))
        return {"ok": 1}

    monkeypatch.setattr(m, "build_operator_daily_summary_payload", payload)
    monkeypatch.setattr(m, "build_operator_summary_snapshot_from_payload", lambda p: {"status": "ok", "payload": p})


def test_paths_and_args(monkeypatch, tmp_path):
    calls = []
    _patch(monkeypatch, tmp_path, calls)
    a, b = _both(tmp_path / "ev.jsonl", tmp_path / "out", "2026-10-30")
    assert a == b == {"status": "ok", "payload": {"ok": 1}, "report_json_path": str(tmp_path / "os.json"), "report_md_path": str(tmp_path / "os.md")}
    assert list(a) == ["status", "payload", "report_json_path", "report_md_path"]
    out = tmp_path / "out"
    assert calls[0] == calls[1] == (tmp_path / "ev.jsonl", out, dict(day="2026-10-30", metrics_report_dir=out / "metrics", m30_post_golive_dir=out / "milestones" / "m30_post_golive",
                                                                     m30_golive_dir=out / "milestones" / "m30_golive", m31_slo_incident_dir=out / "m31_slo_incident"))


def test_builder_exception_propagates(monkeypatch, tmp_path):
    calls = []
    _patch(monkeypatch, tmp_path, calls)

    def boom(*a, **k):
        raise RuntimeError("builder")

    monkeypatch.setattr(m, "build_operator_daily_summary_payload", boom)
    for fn in (lambda: m._load_operator_summary_snapshot(tmp_path, tmp_path, "d"), lambda: owner._load_operator_summary_snapshot(tmp_path, tmp_path, "d", facade=m)):
        with pytest.raises(RuntimeError, match="builder"):
            fn()


def test_snapshot_builder_seam(monkeypatch, tmp_path):
    calls = []
    _patch(monkeypatch, tmp_path, calls)
    monkeypatch.setattr(m, "build_operator_summary_snapshot_from_payload", lambda p: {"SEAM": True})
    a, b = _both(tmp_path, tmp_path, "d")
    assert a == b and a["SEAM"] is True
