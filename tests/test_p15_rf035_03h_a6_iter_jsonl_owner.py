"""P15 RF-035 (03h): report_source_helpers.iter_jsonl moved to report_source_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_read_projection as owner


def test_missing_is_plain_list(tmp_path):
    p = tmp_path / "nope.jsonl"
    assert m.iter_jsonl(p) == [] and owner.iter_jsonl(p, facade=m) == []


def test_dict_only_in_order_and_lazy(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n[2]\nBAD\n\n{"b":2}\n', encoding="utf-8")
    its = (m.iter_jsonl(p), owner.iter_jsonl(p, facade=m))
    for it in its:
        assert iter(it) is it
    assert [list(i) for i in its] == [[{"a": 1}, {"b": 2}]] * 2


def test_open_deferred_until_iteration(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n', encoding="utf-8")
    its = (m.iter_jsonl(p), owner.iter_jsonl(p, facade=m))
    p.write_text('{"a":2}\n', encoding="utf-8")
    assert [list(i) for i in its] == [[{"a": 2}]] * 2


def test_json_loads_patched_after_creation(monkeypatch, tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n{"b":2}\n', encoding="utf-8")
    its = (m.iter_jsonl(p), owner.iter_jsonl(p, facade=m))
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": s})
    assert [list(i) for i in its] == [[{"patched": '{"a":1}'}, {"patched": '{"b":2}'}]] * 2


def test_loads_exception_skips(monkeypatch, tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert list(m.iter_jsonl(p)) == [] and list(owner.iter_jsonl(p, facade=m)) == []
