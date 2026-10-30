"""P15 RF-035: agent_pipeline_trace._iter_jsonl moved to agent_pipeline_trace_read_projection; parity with the pre-move body."""
from __future__ import annotations

import json

import pytest

from libs.reporting import agent_pipeline_trace as m
from libs.reporting import agent_pipeline_trace_read_projection as owner


def _both(p):
    return m._iter_jsonl(p), owner._iter_jsonl(p, facade=m)


def test_missing_and_rows(tmp_path):
    assert _both(tmp_path / "nope.jsonl") == ([], [])
    p = tmp_path / "t.jsonl"
    p.write_text('{"a":1}\ninvalid\n[2]\n\n   \n{"b":2}\n', encoding="utf-8")
    a, b = _both(p)
    assert a == b == [{"a": 1}, {"b": 2}]
    assert isinstance(a, list) and a is not b


def test_unicode_and_open_error(tmp_path):
    p = tmp_path / "u.jsonl"
    p.write_text('{"k":"한글"}\n', encoding="utf-8")
    assert _both(p)[0] == [{"k": "한글"}]
    d = tmp_path / "dir"
    d.mkdir()
    for fn in (lambda: m._iter_jsonl(d), lambda: owner._iter_jsonl(d, facade=m)):
        with pytest.raises(OSError):
            fn()


def test_facade_json_loads_seam(monkeypatch, tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text('{"a":1}\n{"b":2}\n{"c":3}\n', encoding="utf-8")
    real = json.loads
    calls = []

    def flaky(line):
        calls.append(line)
        if '"b"' in line:
            raise ValueError("bad")
        return real(line)

    monkeypatch.setattr(m.json, "loads", flaky)
    a, b = _both(p)
    assert a == b == [{"a": 1}, {"c": 3}] and len(calls) == 6
