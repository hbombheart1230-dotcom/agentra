"""P15 RF-035 (23h): daily_report_generator._find_trade_dir moved to daily_report_generator_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import daily_report_generator as m
from libs.reporting import daily_report_generator_read_projection as owner


def _both(root, day, tid):
    return m._find_trade_dir(root, day, tid), owner._find_trade_dir(root, day, tid)


def test_direct_nested_missing(tmp_path):
    (tmp_path / "trades" / "2026-10-30" / "T1").mkdir(parents=True)
    assert _both(tmp_path, "2026-10-30", "T1") == (tmp_path / "trades/2026-10-30/T1",) * 2
    (tmp_path / "trades" / "2026-10-30" / "SYM" / "T2").mkdir(parents=True)
    assert _both(tmp_path, "2026-10-30", "T2") == (tmp_path / "trades/2026-10-30/SYM/T2",) * 2
    assert _both(tmp_path, "2026-10-30", "T9") == (None, None)
    assert _both(tmp_path, "2026-11-01", "T1") == (None, None)


def test_sorted_first_of_two_nested(tmp_path):
    for sym in ("B", "A"):
        (tmp_path / "trades" / "D" / sym / "T").mkdir(parents=True)
    assert _both(tmp_path, "D", "T") == (tmp_path / "trades/D/A/T",) * 2


def test_direct_priority_and_glob_metachar(tmp_path):
    (tmp_path / "trades" / "D" / "A" / "T").mkdir(parents=True)
    (tmp_path / "trades" / "D" / "T").mkdir(parents=True)
    assert _both(tmp_path, "D", "T") == (tmp_path / "trades/D/T",) * 2
    (tmp_path / "trades" / "E" / "X" / "T1").mkdir(parents=True)
    assert _both(tmp_path, "E", "T*") == (tmp_path / "trades/E/X/T1",) * 2
