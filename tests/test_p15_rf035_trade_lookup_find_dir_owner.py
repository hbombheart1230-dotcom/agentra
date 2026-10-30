"""P15 RF-035: llm_artifacts find_trade_dir moved to llm_artifacts_trade_lookup; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_lookup as owner


def _both(root, tid):
    return m.find_trade_dir(root, tid), owner.find_trade_dir(root, tid, facade=m)


def test_blank_direct_nested_missing(tmp_path):
    (tmp_path / "TRD_A").mkdir()
    (tmp_path / "09" / "TRD_B").mkdir(parents=True)
    for tid in ("", "  ", None):
        assert _both(tmp_path, tid) == (None, None)
    assert _both(tmp_path, " TRD_A ") == (tmp_path / "TRD_A", tmp_path / "TRD_A")
    assert _both(tmp_path, "TRD_B") == (tmp_path / "09" / "TRD_B",) * 2
    assert _both(tmp_path, "TRD_Z") == (None, None)


def test_facade_iter_seam_returns_same_object(monkeypatch, tmp_path):
    fake = tmp_path / "x" / "TRD_F"
    monkeypatch.setattr(m, "iter_trade_dirs", lambda root: [fake])
    a, b = _both(tmp_path, "TRD_F")
    assert a is fake and b is fake
