"""P15 RF-035 (23h): daily_report_generator._iter_events moved to daily_report_generator_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import daily_report_generator as m
from libs.reporting import daily_report_generator_read_projection as owner


def _rows(p):
    return list(m._iter_events(p)), list(owner._iter_events(p, facade=m))


def test_missing_returns_empty_list(tmp_path):
    p = tmp_path / "nope.jsonl"
    assert m._iter_events(p) == [] and owner._iter_events(p, facade=m) == []
    assert _rows(p) == ([], [])


def test_rows_order_and_lazy_generator(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"event":1}\nBAD\n\n   \n{"event":2}\n[3]\n', encoding="utf-8")
    assert _rows(p) == ([{"event": 1}, {"event": 2}, [3]],) * 2
    for it in (m._iter_events(p), owner._iter_events(p, facade=m)):
        assert iter(it) is it
        assert next(it) == {"event": 1}


def test_lazy_open_deferred_until_iteration(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n', encoding="utf-8")
    its = (m._iter_events(p), owner._iter_events(p, facade=m))
    p.write_text('{"a":2}\n', encoding="utf-8")
    assert [list(i) for i in its] == [[{"a": 2}]] * 2


def test_facade_json_loads_seam(monkeypatch, tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n{"b":2}\n', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert _rows(p) == ([], [])
    monkeypatch.undo()
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": s})
    assert _rows(p)[0] == _rows(p)[1] == [{"patched": '{"a":1}'}, {"patched": '{"b":2}'}]
