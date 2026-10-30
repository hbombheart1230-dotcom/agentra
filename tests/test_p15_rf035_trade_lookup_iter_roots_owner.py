"""P15 RF-035: llm_artifacts iter_trade_day_roots moved to llm_artifacts_trade_lookup; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_lookup as owner


def _both(root):
    return m.iter_trade_day_roots(root), owner.iter_trade_day_roots(root, facade=m)


def _tree(tmp_path):
    reports = tmp_path / "reports"
    for d in ("2026-10-30", "2026-10-29"):
        (reports / "trades" / d).mkdir(parents=True)
    (tmp_path / "2026-10-28" / "TRD_1").mkdir(parents=True)
    (tmp_path / "2026-10-30" / "TRD_9").mkdir(parents=True)
    return reports


def test_canonical_then_legacy_deduped(tmp_path):
    reports = _tree(tmp_path)
    a, b = _both(reports)
    assert a == b
    assert [p.name for p in a] == ["2026-10-29", "2026-10-30", "2026-10-28"]
    assert a[2] == tmp_path / "2026-10-28"


def test_shape_false_omits_legacy(monkeypatch, tmp_path):
    reports = _tree(tmp_path)
    monkeypatch.setattr(m, "_looks_like_trade_day_dir", lambda p: False)
    a, b = _both(reports)
    assert a == b and [p.name for p in a] == ["2026-10-29", "2026-10-30"]


def test_missing_repo_root_exception_preserved(tmp_path):
    reports = tmp_path / "gone" / "reports"
    for fn in (lambda: m.iter_trade_day_roots(reports), lambda: owner.iter_trade_day_roots(reports, facade=m)):
        with pytest.raises(FileNotFoundError):
            fn()
