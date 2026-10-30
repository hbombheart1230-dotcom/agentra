"""P15 RF-035: llm_artifacts resolve_trade_day_root moved to llm_artifacts_trade_lookup; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_lookup as owner


def _both(root, day):
    return m.resolve_trade_day_root(root, day), owner.resolve_trade_day_root(root, day, facade=m)


def test_canonical_exists_and_spy_not_called(monkeypatch, tmp_path):
    reports = tmp_path / "reports"
    (reports / "trades" / "D").mkdir(parents=True)
    calls = []
    monkeypatch.setattr(m, "misplaced_trade_day_root", lambda r, d: calls.append(1))
    assert _both(reports, "D") == (reports / "trades" / "D",) * 2
    assert calls == []


def test_fallback_and_primary(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    assert _both(reports, "D") == (reports / "trades" / "D",) * 2
    (tmp_path / "D" / "TRD_1").mkdir(parents=True)
    assert _both(reports, "D") == (tmp_path / "D",) * 2


def test_facade_seams(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "canonical_trade_day_root", lambda r, d: tmp_path / "missing")
    fb = tmp_path / "fb"
    monkeypatch.setattr(m, "misplaced_trade_day_root", lambda r, d: fb)
    assert _both(tmp_path, "D") == (fb, fb)
