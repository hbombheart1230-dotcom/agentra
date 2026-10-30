"""P15 RF-035 (21h): strategist_llm_summary._read_json moved to strategist_llm_summary_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_read_projection as owner


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
    a, b = _both(good)
    assert a == b == {"a": 1}
    assert _both(lst) == ({}, {}) and _both(bad) == ({}, {}) and _both(tmp_path / "missing.json") == ({}, {})
    assert sorted(x.name for x in tmp_path.iterdir()) == before


def test_returns_copy_type_dict(tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"a": {"n": 1}}', encoding="utf-8")
    a, b = _both(good)
    assert type(a) is dict and type(b) is dict and a is not b


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


def test_stage_meta_constant_stays_in_source():
    assert set(m._STAGE_META_BY_CALL_KIND) == {"selected_symbol_tactical_refresh", "stale_intraday_hold_review", "end_of_day_carry_review"}
