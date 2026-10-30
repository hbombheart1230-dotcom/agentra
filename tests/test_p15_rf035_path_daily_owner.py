"""P15 RF-035: llm_artifacts daily_artifact_paths moved to llm_artifacts_path_projection; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_path_projection as owner


KEYS = ["root_dir", "daily_root", "daily_report_json", "daily_report_md", "daily_summary_json", "daily_summary_md", "daily_report_llm_response_json", "operator_summary_json", "operator_summary_md", "trade_index_json", "legacy_daily_json", "legacy_daily_md", "root_daily_json", "root_daily_md"]


def _both(root, day):
    return m.daily_artifact_paths(root, day), owner.daily_artifact_paths(root, day, facade=m)


def test_values_and_key_order():
    a, b = _both(Path("reports"), " 2026-10-30 ")
    assert a == b and list(a) == list(b) == KEYS
    assert a["root_dir"] == Path("reports/operator_summary/daily/2026-10-30")
    assert a["daily_report_json"].name == "daily_report.json"
    assert a["legacy_daily_json"] == Path("reports/operator_summary/daily/daily_2026-10-30.json")
    assert a["root_daily_md"] == Path("reports/operator_summary/daily_2026-10-30.md")


def test_facade_root_seam(monkeypatch):
    monkeypatch.setattr(m, "operator_summary_artifact_root", lambda r: Path("fake"))
    a, b = _both(Path("reports"), "D")
    assert a == b and a["root_dir"] == Path("fake/daily/D")
