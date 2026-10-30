"""P15 RF-035 (02h): trade_explain.official_trade_explain_report_dir moved to trade_explain_path_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from libs.reporting import trade_explain as m
from libs.reporting import trade_explain_path_projection as owner


def _both(root):
    return m.official_trade_explain_report_dir(root), owner.official_trade_explain_report_dir(root, facade=m)


def test_path_and_no_mkdir(tmp_path):
    root = tmp_path / "reports"
    a, b = _both(root)
    assert a == b == root / "dev" / "analysis" / "trade_explain" and not root.exists()
    assert _both(str(root)) == (a, a)


def test_facade_constant_seam(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR", Path("custom") / "x")
    a, b = _both(tmp_path)
    assert a == b == tmp_path / "custom" / "x"
