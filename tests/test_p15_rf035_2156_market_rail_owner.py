"""P15 RF-035 (2156): strategist_llm_summary._market_rail_from_canonical moved to strategist_llm_summary_market_rail; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_market_rail as owner


def _run(canonical, monkeypatch):
    seen = []
    monkeypatch.setattr(m, "classify_market_regime_rail", lambda packet: (seen.append(copy.deepcopy(packet)), {"sentinel": True})[1])
    a = m._market_rail_from_canonical(canonical)
    b = owner._market_rail_from_canonical(canonical, facade=m)
    return a, b, seen


def test_primary_signal(monkeypatch):
    canonical = {"generated_at": "t", "global_sentiment_signal": {"score": 0.7, "status": "ok", "source": "s", "index_moves": {"KOSPI": 1}}}
    snap = copy.deepcopy(canonical)
    a, b, seen = _run(canonical, monkeypatch)
    assert a == b == {"sentinel": True} and canonical == snap
    assert seen[0] == seen[1]
    pkt = seen[0]
    assert pkt["generated_at"] == "t" and pkt["global_sentiment"] == {"score": 0.7, "status": "ok", "source": "s"}
    assert pkt["index_moves"] == {"KOSPI": 1} and pkt["korea_indices"] == {} and pkt["macro_moves"] == {}
    assert list(pkt) == ["generated_at", "global_sentiment", "index_moves", "korea_indices", "macro_moves"]


def test_fallback_market_context_and_saved_at(monkeypatch):
    canonical = {"saved_at": "s", "market_context": {"global_signal": {"score": 1, "macro_moves": {"USD": 2}}}}
    a, b, seen = _run(canonical, monkeypatch)
    assert seen[0] == seen[1] and seen[0]["generated_at"] == "s" and seen[0]["global_sentiment"]["score"] == 1
    assert seen[0]["macro_moves"] == {"USD": 2}


def test_empty_and_real_classifier():
    pkt_empty = m._market_rail_from_canonical({})
    assert pkt_empty == owner._market_rail_from_canonical({}, facade=m)
