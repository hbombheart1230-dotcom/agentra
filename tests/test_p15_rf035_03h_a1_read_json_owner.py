"""P15 RF-035 (03h): report_source_helpers.read_json moved to report_source_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_read_projection as owner


def _both(p):
    return m.read_json(p), owner.read_json(p, facade=m)


def test_values(tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"ok": 1}', encoding="utf-8")
    lst = tmp_path / "l.json"
    lst.write_text("[]", encoding="utf-8")
    bad = tmp_path / "b.json"
    bad.write_text("{oops", encoding="utf-8")
    before = sorted(x.name for x in tmp_path.iterdir())
    assert _both(good) == ({"ok": 1}, {"ok": 1})
    assert _both(lst) == ({}, {}) and _both(bad) == ({}, {}) and _both(tmp_path / "missing.json") == ({}, {}) and _both(tmp_path) == ({}, {})
    assert sorted(x.name for x in tmp_path.iterdir()) == before


def test_returns_same_dict_object_from_loads(monkeypatch, tmp_path):
    good = tmp_path / "g.json"
    good.write_text("{}", encoding="utf-8")
    sentinel = {"k": 1}
    monkeypatch.setattr(m.json, "loads", lambda s: sentinel)
    a, b = _both(good)
    assert a is sentinel and b is sentinel


def test_facade_json_loads_seam(monkeypatch, tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"ok": 1}', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert _both(good) == ({}, {})
