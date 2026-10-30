"""P15 RF-035 (00h): market_regime_rail_review.load_latest_macro_snapshot moved to market_regime_rail_review_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import market_regime_rail_review as m
from libs.reporting import market_regime_rail_review_read_projection as owner


def _both(day, root):
    return m.load_latest_macro_snapshot(day, root=root), owner.load_latest_macro_snapshot(day, root=root, facade=m)


def test_missing_and_invalid(tmp_path):
    path = tmp_path / "2026-10-30" / "latest.json"
    exp = {"available": False, "path": str(path), "error": "macro_snapshot_unavailable"}
    assert _both("2026-10-30", tmp_path) == (exp, exp)
    path.parent.mkdir()
    path.write_text("{bad", encoding="utf-8")
    assert _both("2026-10-30", tmp_path) == (exp, exp)


def test_valid_and_day_truncation(tmp_path):
    path = tmp_path / "2026-10-30" / "latest.json"
    path.parent.mkdir()
    path.write_text('{"x": 1}', encoding="utf-8")
    exp = {"x": 1, "available": True, "path": str(path)}
    a, b = _both("2026-10-30T12:00", tmp_path)
    assert a == b == exp and list(a) == ["x", "available", "path"]


def test_default_root_signature():
    import inspect
    from pathlib import Path
    assert inspect.signature(m.load_latest_macro_snapshot).parameters["root"].default == Path("data/logs/macro_indicators")
    assert inspect.signature(m.load_latest_macro_snapshot).parameters["root"].kind is inspect.Parameter.KEYWORD_ONLY


def test_facade_json_loads_seam_and_non_dict(monkeypatch, tmp_path):
    path = tmp_path / "D" / "latest.json"
    path.parent.mkdir()
    path.write_text("[1]", encoding="utf-8")
    for fn in (lambda: m.load_latest_macro_snapshot("D", root=tmp_path), lambda: owner.load_latest_macro_snapshot("D", root=tmp_path, facade=m)):
        with pytest.raises(TypeError):
            fn()
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": True})
    exp = {"patched": True, "available": True, "path": str(path)}
    assert _both("D", tmp_path) == (exp, exp)
