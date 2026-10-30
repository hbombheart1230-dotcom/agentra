"""P15 RF-035: strategist_llm_evaluation._shadow_rows moved to strategist_llm_evaluation_rows; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_rows as owner


def test_values_and_copies():
    cand = {"symbol": "A"}
    payloads = [{"candidates": [cand, 3, None]}, None, "x", {"candidates": None}, {"candidates": [{"symbol": "B"}]}]
    for out in (m._shadow_rows(payloads), owner._shadow_rows(payloads, facade=m)):
        assert out == [{"symbol": "A"}, {"symbol": "B"}]
        assert out[0] is not cand
    assert cand == {"symbol": "A"}


def test_empty_and_tuple_candidates():
    for call in (lambda p: m._shadow_rows(p), lambda p: owner._shadow_rows(p, facade=m)):
        assert call([]) == []
        assert call([{"candidates": ({"k": 1},)}]) == [{"k": 1}]
        assert call([{"candidates": []}]) == []
