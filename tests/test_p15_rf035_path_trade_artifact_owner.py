"""P15 RF-035: llm_artifacts trade_artifact_paths moved to llm_artifacts_trade_path_projection; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_path_projection as owner


def _both(*a, **k):
    return m.trade_artifact_paths(*a, **k), owner.trade_artifact_paths(*a, facade=m, **k)


def test_default_layout_and_key_order(tmp_path):
    root = tmp_path / "reports"
    a, b = _both(root, "2026-10-30", "TRD_1")
    assert a == b and list(a) == list(b)
    assert a["trade_root"] == root / "trades/2026-10-30/TRD_1" and a["entry_json"] == a["trade_root"] / "entry.json"
    assert a["legacy_trade_root"] == root / "trades/2026/10/TRD_1"
    assert a["monitor_evidence_json"] == a["monitor_timeline_json"] and a["monitor_evidence_json"] is not None
    assert len(a) == 57 and list(a)[:3] == ["trade_root", "legacy_trade_root", "reports_dir"]
    assert not root.exists()


def test_time_bucket_without_existing_dir(tmp_path):
    root = tmp_path / "reports"
    a, b = _both(root, "2026-10-30", "TRD_1", time_bucket="09")
    assert a == b and a["trade_root"] == root / "trades/2026-10-30/09/TRD_1"


def test_existing_dir_wins_and_prefer_existing_day_root(tmp_path):
    root = tmp_path / "reports"
    existing = root / "trades/2026-10-30/10/TRD_1"
    existing.mkdir(parents=True)
    a, b = _both(root, "2026-10-30", "TRD_1", time_bucket="09")
    assert a == b and a["trade_root"] == existing
    a, b = _both(root, "2026-10-30", "TRD_1", prefer_existing_day_root=True)
    assert a == b and a["trade_root"] == existing


def test_facade_find_trade_dir_seam(monkeypatch, tmp_path):
    fake = tmp_path / "fake_root"
    monkeypatch.setattr(m, "find_trade_dir", lambda root, tid: fake)
    a, b = _both(tmp_path / "reports", "2026-10-30", "TRD_1")
    assert a == b and a["trade_root"] is fake


def test_facade_day_root_seams(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "resolve_trade_day_root", lambda r, d: tmp_path / "resolved")
    monkeypatch.setattr(m, "canonical_trade_day_root", lambda r, d: tmp_path / "canon")
    a, b = _both(tmp_path / "reports", "D", "T1", prefer_existing_day_root=True)
    assert a == b and a["trade_root"] == tmp_path / "resolved/T1"
    a, b = _both(tmp_path / "reports", "D", "T1")
    assert a == b and a["trade_root"] == tmp_path / "canon/T1"


def test_blank_trade_id_and_path_required(tmp_path):
    a, b = _both(tmp_path / "reports", "D", "")
    assert a == b
    with pytest.raises(TypeError):
        m.trade_artifact_paths("reports", "2026-10-30", "T")
    with pytest.raises(TypeError):
        owner.trade_artifact_paths("reports", "2026-10-30", "T", facade=m)
