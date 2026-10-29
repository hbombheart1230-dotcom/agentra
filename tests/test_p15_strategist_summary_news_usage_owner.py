"""P15 A5: strategist_llm_summary ``_news_usage_from_canonical`` moved to strategist_llm_summary_usage; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_usage as owner

GOLDEN = ["0d7bf8069a6dfc956c05b3370dc5ac1b21767fdd5ba2ffd12602ff76e6427156", "955e431fc62a0373b58436228b1b683ce0cd1d7f789e7518c9ed9684f47443a9", "893f1673281766117c45cb106e2bb700682a455342764a51b74617197ca1aa57", "45e8acebe9b14f3b6b48c444864cc6365445ec3521b6daec1b3f130774c3efb7", "a0509ab37bcced024b47753cdf57d375d61a82e1a66c1ee26886e073f577addb", "EXC:ValueError", "EXC:ValueError", "b3e1f2f81fa4e28134ee1236c8f1e48b7392af4e1b074b7897743c184811dfa6", "8216c47f0d1a23a991068afbc3b168cfd6b89db4d2e4a8b851e8a2a36bad5f27", "ccfd689a3febd1ba57d56e5d5760ce08f803cc4c82b3b2698f2789b453b5ca3f", "0d7bf8069a6dfc956c05b3370dc5ac1b21767fdd5ba2ffd12602ff76e6427156"]

NEWS = [
    {}, {"news_usage_trace": {"query_targets": ["q1"], "market_headlines_used": ["m1", "m2", "m3", "m4"], "candidate_headlines_used": ["c1"], "human_summary": "s", "market_effect": "me", "playbook_effect": "pe", "scanner_guidance_effect": "sg", "monitor_policy_effect": "mp", "confidence": "high"},
         "news_context": {"market_headline_count": 99, "candidate_headline_count": 99, "headline_count": 5}, "news_evidence_summary": "ev", "news_query_reasoning": "qr"},
    {"news_context": {"market_headline_count": "4", "candidate_headline_count": 0, "summary": "ctx"}, "candidate_news_sample": {"A": {"count": 2}, "B": {"count": "x"}, "C": "junk"}, "news_query_targets": ["t"]},
    {"news_context": {"headline_count": 10, "market_signal_total": 4}}, {"news_context": {"headline_count": 3, "market_signal_total": 9}}, {"news_context": {"headline_count": "x"}}, {"news_context": {"market_headline_count": "bad"}},
    {"news_evidence_summary": "only"}, {"news_usage_trace": {"query_targets": []}, "news_query_targets": ["fallback"]}, {"market_news_sample": {"A": {"count": 1}}, "news_context": {}}, {"news_usage_trace": "junk", "news_context": []},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(NEWS)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = NEWS[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._news_usage_from_canonical(a)) == GOLDEN[i]
    assert _safe(lambda: owner.news_usage_from_canonical(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_count_precedence_split_and_caps():
    f = m._news_usage_from_canonical
    d = f({})
    assert d["available"] is False and d["market_headline_count"] == 0 and d["candidate_headline_count"] == 0 and d["confidence"] == ""
    a = f(NEWS[1])
    assert a["market_headline_count"] == 4 and a["candidate_headline_count"] == 1 and a["market_headlines_sample"] == ["m1", "m2", "m3"] and a["confidence"] == "high" and a["available"] is True
    b = f(NEWS[2])
    assert b["market_headline_count"] == 4 and b["candidate_headline_count"] == 2 and b["query_targets"] == ["t"] and b["confidence"] == "medium" and b["human_summary"] == "ctx"   # sample-map fallback; bad counts ignored
    assert (f(NEWS[3])["market_headline_count"], f(NEWS[3])["candidate_headline_count"]) == (4, 6)                                                                              # headline_count split by market_signal_total
    assert (f(NEWS[4])["market_headline_count"], f(NEWS[4])["candidate_headline_count"]) == (9, 0)
    assert f(NEWS[8])["query_targets"] == ["fallback"]


def test_original_exceptions_for_non_numeric_counts():
    for bad in (NEWS[5], NEWS[6]):
        with pytest.raises(ValueError):
            m._news_usage_from_canonical(bad)


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_headline_count_from_sample_map", lambda v: 11)
    out = m._news_usage_from_canonical(NEWS[9])
    assert out["market_headline_count"] == 11 and out["candidate_headline_count"] == 11


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._news_usage_from_canonical).splitlines()) <= 3
