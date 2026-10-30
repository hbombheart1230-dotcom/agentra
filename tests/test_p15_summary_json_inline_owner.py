"""P15: strategist_llm_summary _json_inline moved to strategist_llm_summary_json_projection.json_inline; parity with the pre-move body."""
from __future__ import annotations

import json

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_json_projection as owner


class Odd:
    def __str__(self):
        return "fallback"


def test_values():
    for fn in (m._json_inline, owner.json_inline):
        assert fn({"한글": 1, "b": 2}) == '{"b": 2, "한글": 1}'
        assert fn([1, None]) == "[1, null]"
        assert fn(Odd()) == "fallback"


def test_dumps_exception_falls_back(monkeypatch):
    def bad(*a, **k):
        raise ValueError("x")

    monkeypatch.setattr(json, "dumps", bad)
    for fn in (m._json_inline, owner.json_inline):
        assert fn([1]) == "[1]"
