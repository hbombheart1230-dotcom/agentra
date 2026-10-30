"""P15 RF-035 (02h): trade_explain._iter_jsonl moved to trade_explain_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import trade_explain as m
from libs.reporting import trade_explain_read_projection as owner


def _both(p):
    return m._iter_jsonl(p), owner._iter_jsonl(p, facade=m)


def test_missing_and_rows(tmp_path):
    assert _both(tmp_path / "nope.jsonl") == ([], [])
    p = tmp_path / "t.jsonl"
    p.write_text('{"a":1}\n[2]\nBAD\n\n{"b":2}\n', encoding="utf-8")
    a, b = _both(p)
    assert a == b == [{"a": 1}, {"b": 2}] and isinstance(a, list)


def test_open_error_propagates_and_loads_seam(monkeypatch, tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    for fn in (lambda: m._iter_jsonl(d), lambda: owner._iter_jsonl(d, facade=m)):
        with pytest.raises(OSError):
            fn()
    p = tmp_path / "t.jsonl"
    p.write_text('{"a":1}\n', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert _both(p) == ([], [])
    monkeypatch.undo()
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": s})
    assert _both(p)[0] == _both(p)[1] == [{"patched": '{"a":1}'}]
