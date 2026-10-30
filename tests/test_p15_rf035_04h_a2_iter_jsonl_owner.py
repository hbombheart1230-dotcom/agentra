"""P15 RF-035 (04h): symbol_trade_report._iter_jsonl moved to symbol_trade_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_read_projection as owner


def test_missing_plain_list(tmp_path):
    p = tmp_path / "nope.jsonl"
    assert m._iter_jsonl(p) == [] and owner._iter_jsonl(p, facade=m) == []


def test_dict_only_lazy_and_deferred_open(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n[2]\nBAD\n\n{"b":2}\n', encoding="utf-8")
    its = (m._iter_jsonl(p), owner._iter_jsonl(p, facade=m))
    for it in its:
        assert iter(it) is it
    p.write_text('{"a":9}\n', encoding="utf-8")
    assert [list(i) for i in its] == [[{"a": 9}]] * 2


def test_json_loads_patched_after_creation(monkeypatch, tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n{"b":2}\n', encoding="utf-8")
    its = (m._iter_jsonl(p), owner._iter_jsonl(p, facade=m))
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": s})
    assert [list(i) for i in its] == [[{"patched": '{"a":1}'}, {"patched": '{"b":2}'}]] * 2


def test_loads_exception_skips(monkeypatch, tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert list(m._iter_jsonl(p)) == [] and list(owner._iter_jsonl(p, facade=m)) == []
