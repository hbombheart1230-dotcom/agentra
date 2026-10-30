"""P15 RF-035 (02h): trade_explain._report_inventory moved to trade_explain_inventory_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from libs.reporting import trade_explain as m
from libs.reporting import trade_explain_inventory_projection as owner


def _both(day, root):
    return m._report_inventory(day, root), owner._report_inventory(day, root, facade=m)


def test_missing_and_order(tmp_path):
    assert _both("2026-10-30", tmp_path / "reports") == ([], [])
    reports = tmp_path / "reports"
    op = reports / "operator_summary"
    for rel in (op / "daily" / "2026-10-30" / "operator_summary.md", reports / "metrics" / "metrics_2026-10-30.md", reports / "live_watch" / "live_watch_latest.md", reports / "run_cards" / "run_cards_2026-10-30.md"):
        rel.parent.mkdir(parents=True, exist_ok=True)
        rel.write_text("x", encoding="utf-8")
    a, b = _both("2026-10-30", reports)
    assert a == b == [str(op / "daily/2026-10-30/operator_summary.md"), str(reports / "run_cards/run_cards_2026-10-30.md"), str(reports / "metrics/metrics_2026-10-30.md"), str(reports / "live_watch/live_watch_latest.md")]


def test_legacy_daily_paths_and_no_writes(tmp_path):
    reports = tmp_path / "reports"
    op = reports / "operator_summary"
    (op / "daily").mkdir(parents=True)
    (op / "daily" / "daily_D.md").write_text("x", encoding="utf-8")
    before = sorted(str(x) for x in tmp_path.rglob("*"))
    a, b = _both("D", reports)
    assert a == b == [str(op / "daily" / "daily_D.md")] and sorted(str(x) for x in tmp_path.rglob("*")) == before


def test_facade_operator_root_seam(monkeypatch, tmp_path):
    fake = tmp_path / "fakeop"
    (fake / "daily" / "D").mkdir(parents=True)
    (fake / "daily" / "D" / "daily_report.md").write_text("x", encoding="utf-8")
    monkeypatch.setattr(m, "operator_summary_artifact_root", lambda r: fake)
    a, b = _both("D", tmp_path / "reports")
    assert a == b == [str(fake / "daily" / "D" / "daily_report.md")]
