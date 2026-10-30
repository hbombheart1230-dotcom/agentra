"""P15 RF-035: strategist_llm_evaluation._top_counter moved to strategist_llm_evaluation_rows; parity with the pre-move body."""
from __future__ import annotations

from collections import Counter

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_rows as owner


def test_values_and_immutability():
    c = Counter({"x": 3, "y": 1})
    snap = dict(c)
    for fn in (m._top_counter, owner._top_counter):
        assert fn(c) == [{"name": "x", "count": 3}, {"name": "y", "count": 1}]
        assert fn(c, limit=1) == [{"name": "x", "count": 3}]
        assert fn(Counter()) == []
        assert fn(Counter({"": 5, "a": 1})) == [{"name": "a", "count": 1}]
        assert fn(c, limit=0) == []
    assert dict(c) == snap


def test_stable_ties_and_keyword_only():
    c = Counter()
    for k in ("b", "a", "c"):
        c[k] += 2
    for fn in (m._top_counter, owner._top_counter):
        assert [r["name"] for r in fn(c)] == ["b", "a", "c"]
        with pytest.raises(TypeError):
            fn(c, 1)
