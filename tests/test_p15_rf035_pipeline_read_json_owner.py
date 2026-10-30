"""P15 RF-035: agent_pipeline_trace._read_json moved to agent_pipeline_trace_read_projection; parity with the pre-move body."""
from __future__ import annotations

import json

from libs.reporting import agent_pipeline_trace as m
from libs.reporting import agent_pipeline_trace_read_projection as owner


def _both(p):
    return m._read_json(p), owner._read_json(p, facade=m)


def test_values_and_no_writes(tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"a": 1}', encoding="utf-8")
    lst = tmp_path / "l.json"
    lst.write_text("[1]", encoding="utf-8")
    bad = tmp_path / "b.json"
    bad.write_text("{oops", encoding="utf-8")
    before = sorted(x.name for x in tmp_path.iterdir())
    assert _both(good) == ({"a": 1}, {"a": 1})
    assert _both(lst) == ({}, {})
    assert _both(bad) == ({}, {})
    assert _both(tmp_path / "missing.json") == ({}, {})
    assert sorted(x.name for x in tmp_path.iterdir()) == before


def test_facade_json_loads_seam(monkeypatch, tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"a": 1}', encoding="utf-8")

    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr(m.json, "loads", boom)
    assert _both(good) == ({}, {})
    monkeypatch.undo()
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": True})
    assert _both(good) == ({"patched": True}, {"patched": True})
