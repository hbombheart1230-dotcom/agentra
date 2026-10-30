"""P15 RF-035 (04h): symbol_trade_report._read_json moved to symbol_trade_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_read_projection as owner


def _both(p):
    return m._read_json(p), owner._read_json(p, facade=m)


def test_values(tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"ok": 1}', encoding="utf-8")
    lst = tmp_path / "l.json"
    lst.write_text("[1]", encoding="utf-8")
    bad = tmp_path / "b.json"
    bad.write_text("{oops", encoding="utf-8")
    before = sorted(x.name for x in tmp_path.iterdir())
    assert _both(good) == ({"ok": 1}, {"ok": 1})
    for p in (lst, bad, tmp_path / "missing.json", tmp_path):
        assert _both(p) == ({}, {})
    assert sorted(x.name for x in tmp_path.iterdir()) == before


def test_utf8_read(tmp_path):
    p = tmp_path / "u.json"
    p.write_text('{"k": "한글"}', encoding="utf-8")
    assert _both(p) == ({"k": "한글"}, {"k": "한글"})


def test_facade_json_loads_seam(monkeypatch, tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"ok": 1}', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert _both(good) == ({}, {})
    monkeypatch.undo()
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": True})
    assert _both(good) == ({"patched": True}, {"patched": True})
