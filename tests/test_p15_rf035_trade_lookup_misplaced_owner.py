"""P15 RF-035: llm_artifacts misplaced_trade_day_root moved to llm_artifacts_trade_lookup; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_lookup as owner


def _both(root, day):
    return m.misplaced_trade_day_root(root, day), owner.misplaced_trade_day_root(root, day, facade=m)


def test_blank_and_found_and_none(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    assert _both(reports, "") == (None, None)
    assert _both(reports, None) == (None, None)
    assert _both(reports, "2026-10-30") == (None, None)
    (tmp_path / "2026-10-30" / "TRD_1").mkdir(parents=True)
    assert _both(reports, " 2026-10-30 ") == (tmp_path / "2026-10-30",) * 2


def test_non_reports_root_without_match(tmp_path):
    root = tmp_path / "x"
    (root / "trades" / "D").mkdir(parents=True)
    (root / "D").mkdir()
    assert _both(root, "trades") == (None, None)


def test_facade_seams(monkeypatch, tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (tmp_path / "D" / "TRD_1").mkdir(parents=True)
    monkeypatch.setattr(m, "_looks_like_trade_day_dir", lambda p: False)
    assert _both(reports, "D") == (None, None)
    monkeypatch.undo()
    monkeypatch.setattr(m, "canonical_trade_day_root", lambda r, d: tmp_path / "D")
    assert _both(reports, "D") == (None, None)
    monkeypatch.undo()
    monkeypatch.setattr(m, "_repo_root_from_reports_root", lambda r: tmp_path / "elsewhere")
    assert _both(reports, "D") == (None, None)
