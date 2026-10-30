"""P15 RF-035: llm_artifacts list_misplaced_trade_day_roots moved to llm_artifacts_trade_lookup; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_lookup as owner


def _both(root):
    return m.list_misplaced_trade_day_roots(root), owner.list_misplaced_trade_day_roots(root, facade=m)


def test_exclusion_and_legacy(tmp_path):
    reports = tmp_path / "reports"
    (reports / "trades" / "2026-10-30").mkdir(parents=True)
    (tmp_path / "2026-10-30" / "TRD_1").mkdir(parents=True)
    a, b = _both(reports)
    assert a == b == []
    (tmp_path / "2026-10-29" / "TRD_1").mkdir(parents=True)
    a, b = _both(reports)
    assert a == b == [tmp_path / "2026-10-29"]


def test_no_canonical_root_and_no_legacy(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    a, b = _both(reports)
    assert a == b == []


def test_shape_false(monkeypatch, tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (tmp_path / "2026-10-29" / "TRD_1").mkdir(parents=True)
    monkeypatch.setattr(m, "_looks_like_trade_day_dir", lambda p: False)
    a, b = _both(reports)
    assert a == b == []
