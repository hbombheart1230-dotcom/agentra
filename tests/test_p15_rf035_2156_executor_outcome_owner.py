"""P15 RF-035 (2156): controlled_validation_daily._executor_broker_outcome moved to controlled_validation_daily_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import controlled_validation_daily as m
from libs.reporting import controlled_validation_daily_read_projection as owner


def _both(root, day, run):
    return m._executor_broker_outcome(root, day, run), owner._executor_broker_outcome(root, day, run, facade=m)


def _write(root, day, run, payload):
    d = root / "canonical" / day / run
    d.mkdir(parents=True)
    (d / "executor.json").write_text(json.dumps(payload), encoding="utf-8")


def test_blank_and_artifact(tmp_path):
    empty = {"broker_outcome": "", "submission_attempts": 0}
    assert _both(tmp_path, "2026-10-30", "") == (empty, empty)
    assert _both(tmp_path, "2026-10-30", "missing") == (empty, empty)
    _write(tmp_path, "2026-10-30", "r1", {"broker_outcome": "REJECTED", "submission_attempts": "2"})
    expected = {"broker_outcome": "REJECTED", "submission_attempts": 2}
    assert _both(tmp_path, "2026-10-30", "r1") == (expected, expected)
    assert list(expected) == ["broker_outcome", "submission_attempts"]


def test_invalid_count(tmp_path):
    _write(tmp_path, "d", "r2", {"broker_outcome": "X", "submission_attempts": "many"})
    assert _both(tmp_path, "d", "r2") == ({"broker_outcome": "X", "submission_attempts": 0},) * 2
    _write(tmp_path, "d", "r3", {"broker_outcome": None, "submission_attempts": None})
    assert _both(tmp_path, "d", "r3") == ({"broker_outcome": "", "submission_attempts": 0},) * 2


def test_facade_read_spy(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(m, "_read", lambda p: (seen.append(p), {"broker_outcome": "SPY", "submission_attempts": 1})[1])
    a, b = _both(tmp_path, "d", "r")
    assert a == b == {"broker_outcome": "SPY", "submission_attempts": 1}
    assert len(seen) == 2 and seen[0] == tmp_path / "canonical" / "d" / "r" / "executor.json"
