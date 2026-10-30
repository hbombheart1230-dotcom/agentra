"""P15 RF-035: llm_artifacts _looks_like_trade_day_dir moved to llm_artifacts_trade_lookup; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_lookup as owner


def _both(p):
    return m._looks_like_trade_day_dir(p), owner._looks_like_trade_day_dir(p)


def test_shapes(tmp_path):
    assert _both(tmp_path / "missing") == (False, False)
    f = tmp_path / "file"
    f.write_text("x")
    assert _both(f) == (False, False)
    day = tmp_path / "day"
    day.mkdir()
    assert _both(day) == (False, False)
    (day / "TRD_1").mkdir()
    assert _both(day) == (True, True)
    d2 = tmp_path / "d2"
    (d2 / "bucket" / "TRD_2").mkdir(parents=True)
    assert _both(d2) == (True, True)
    d3 = tmp_path / "d3"
    (d3 / "bucket" / "other").mkdir(parents=True)
    assert _both(d3) == (False, False)


def test_oserror_swallowed(monkeypatch, tmp_path):
    (tmp_path / "TRD_1").mkdir()

    def boom(self):
        raise OSError("x")

    monkeypatch.setattr(Path, "iterdir", boom)
    assert _both(tmp_path) == (False, False)
