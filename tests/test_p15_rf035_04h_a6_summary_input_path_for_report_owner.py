"""P15 RF-035 (04h): symbol_trade_report._summary_input_path_for_report moved to symbol_trade_path_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from pathlib import Path, PurePosixPath

import pytest

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_path_projection as owner


def _both(p):
    return m._summary_input_path_for_report(p), owner._summary_input_path_for_report(p, facade=m)


def test_values_and_no_files(tmp_path):
    assert _both(Path("/tmp/a.md")) == (Path("/tmp/ai_trade_summary_input.json"),) * 2
    assert _both("rel/x.md") == (Path("rel/ai_trade_summary_input.json"),) * 2
    before = sorted(str(x) for x in tmp_path.rglob("*"))
    _both(tmp_path / "r.md")
    assert sorted(str(x) for x in tmp_path.rglob("*")) == before


def test_facade_path_seam(monkeypatch):
    seen = []

    def fake_path(p):
        seen.append(p)
        return PurePosixPath(p)

    monkeypatch.setattr(m, "Path", fake_path)
    a, b = _both("/z/q.md")
    assert a == b == PurePosixPath("/z/ai_trade_summary_input.json") and seen == ["/z/q.md"] * 2


def test_empty_name_exception_parity():
    outcomes = []
    for fn in (lambda: m._summary_input_path_for_report(Path("")), lambda: owner._summary_input_path_for_report(Path(""), facade=m)):
        try:
            outcomes.append(("ok", str(fn())))
        except Exception as exc:
            outcomes.append((type(exc).__name__, str(exc)))
    assert outcomes[0] == outcomes[1]
