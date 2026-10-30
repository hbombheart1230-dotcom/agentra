"""P15 RF-035 (00h): metrics_report_generator._iter_events moved to metrics_report_generator_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import metrics_report_generator as m
from libs.reporting import metrics_report_generator_read_projection as owner


def _rows(p):
    return list(m._iter_events(p)), list(owner._iter_events(p, facade=m))


def test_missing_is_plain_list(tmp_path):
    p = tmp_path / "nope.jsonl"
    assert m._iter_events(p) == [] and owner._iter_events(p, facade=m) == []
    assert _rows(p) == ([], [])


def test_dict_only_in_order(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n[2]\nBAD\n\n{"b":2}\n', encoding="utf-8")
    assert _rows(p) == ([{"a": 1}, {"b": 2}],) * 2


def test_lazy_and_json_loads_seam(monkeypatch, tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n{"b":2}\n', encoding="utf-8")
    calls = []
    real = json.loads
    monkeypatch.setattr(m.json, "loads", lambda s: (calls.append(s), real(s))[1])
    its = (m._iter_events(p), owner._iter_events(p, facade=m))
    assert calls == []
    assert [next(i) for i in its] == [{"a": 1}] * 2 and len(calls) == 2
    assert [list(i) for i in its] == [[{"b": 2}]] * 2 and len(calls) == 4


def test_loads_exception_skips(monkeypatch, tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text('{"a":1}\n', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert _rows(p) == ([], [])
