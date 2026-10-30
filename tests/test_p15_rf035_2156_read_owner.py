"""P15 RF-035 (2156): controlled_validation_daily._read moved to controlled_validation_daily_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import controlled_validation_daily as m
from libs.reporting import controlled_validation_daily_read_projection as owner


def _both(p):
    return m._read(p), owner._read(p, facade=m)


def test_values(tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"a": 1}', encoding="utf-8")
    lst = tmp_path / "l.json"
    lst.write_text("[1]", encoding="utf-8")
    bad = tmp_path / "b.json"
    bad.write_text("{oops", encoding="utf-8")
    binary = tmp_path / "bin.json"
    binary.write_bytes(b"\xff\xfe\x00")
    before = sorted(x.name for x in tmp_path.iterdir())
    assert _both(good) == ({"a": 1}, {"a": 1})
    for p in (lst, bad, binary, tmp_path / "missing.json", tmp_path):
        assert _both(p) == ({}, {})
    assert sorted(x.name for x in tmp_path.iterdir()) == before


def test_facade_json_seams(monkeypatch, tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"a": 1}', encoding="utf-8")

    def decode_error(_):
        raise json.JSONDecodeError("x", "", 0)

    monkeypatch.setattr(m.json, "loads", decode_error)
    assert _both(good) == ({}, {})
    monkeypatch.undo()

    def other_error(_):
        raise KeyError("x")

    monkeypatch.setattr(m.json, "loads", other_error)
    for fn in (lambda: m._read(good), lambda: owner._read(good, facade=m)):
        with pytest.raises(KeyError):
            fn()
