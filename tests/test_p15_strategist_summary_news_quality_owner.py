"""P15 A6: strategist_llm_summary ``_news_quality_audit`` moved to strategist_llm_summary_usage; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_usage as owner

GOLDEN = ["2e16b5c19bbd0fd574c41fd823f1a84e4c8faed3c7adea695476b6427798ac49", "ecc1209513f35ef40dfa40eaa71182cebda581ded1f2ddc7f2a38f9bdd3d544f", "ec7cd67d14691baa13bb27195b1063d4f6bac47945bf871a2439b08e518b6b2f", "93da601079f2888c0c59ff39c4069aae4ba679b3175cacd5f1d5945f33c6857a", "c92fa287272f504282e2477d9966775c9286fd7ac302635a07594278f8e98f5f", "EXC:ValueError", "2e16b5c19bbd0fd574c41fd823f1a84e4c8faed3c7adea695476b6427798ac49", "6eba729200efd6fdec9df5df108b28fef093c2101ffba2bb93cdf5116b9c8f3e", "EXC:AttributeError"]

AUDIT = [
    ({}, {}), ({"news_evidence_ranked": {"candidate_news_ranked": [1, 2], "market_news_ranked": [1]}}, {}),
    ({}, {"market_headline_count": 2, "candidate_headline_count": 3, "query_targets": list("abcdefghijkl"), "confidence": "High", "human_summary": "s", "market_effect": "m", "playbook_effect": "p", "scanner_guidance_effect": "g", "monitor_policy_effect": "x"}),
    ({}, {"market_headline_count": 2, "candidate_headline_count": 0, "query_targets": ["q"], "confidence": "low", "news_evidence_summary": "ev", "market_effect": "m"}),
    ({}, {"market_headline_count": 0, "candidate_headline_count": 4, "query_targets": ["q"], "confidence": "medium", "human_summary": "s", "market_effect": "m"}),
    ({}, {"market_headline_count": "bad"}), ({"news_evidence_ranked": "junk"}, {"query_targets": "x"}), ({}, {"confidence": "unknown", "market_headline_count": 1, "candidate_headline_count": 1}), ({}, None),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(AUDIT)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = AUDIT[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._news_quality_audit(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.news_quality_audit(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_status_issue_order_and_caps():
    f = m._news_quality_audit
    weak = f({}, {})
    assert weak["status"] == "weak" and weak["issues"] == ["news_headlines_missing", "news_query_targets_missing", "news_effect_trace_missing", "news_confidence_low_or_missing", "news_summary_missing"]
    assert list(weak) == ["schema_version", "status", "headline_count", "market_headline_count", "candidate_headline_count", "query_target_count", "query_targets", "confidence", "issues",
                          "market_effect", "playbook_effect", "scanner_guidance_effect", "monitor_policy_effect"] and weak["schema_version"] == "strategist_news_quality_audit.v1"
    ok = f(*AUDIT[2])
    assert ok["status"] == "ok" and ok["issues"] == [] and ok["headline_count"] == 5 and ok["query_target_count"] == 12 and len(ok["query_targets"]) == 10 and ok["confidence"] == "High"
    assert f(*AUDIT[3])["status"] == "partial" and "candidate_news_missing" in f(*AUDIT[3])["issues"] and "news_confidence_low_or_missing" in f(*AUDIT[3])["issues"]
    assert "market_news_missing" in f(*AUDIT[4])["issues"] and f(*AUDIT[4])["status"] == "partial"
    assert f(*AUDIT[1])["market_headline_count"] == 1 and f(*AUDIT[1])["candidate_headline_count"] == 2          # fall back to ranked list lengths


def test_original_exceptions():
    with pytest.raises(ValueError):
        m._news_quality_audit(*AUDIT[5])
    with pytest.raises(AttributeError):
        m._news_quality_audit(*AUDIT[8])


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_text", lambda v, d="-": "x")
    out = m._news_quality_audit({}, {"market_headline_count": 1, "candidate_headline_count": 1})
    assert out["confidence"] == "x" and "news_effect_trace_missing" not in out["issues"]
    monkeypatch.setattr(m, "_as_list", lambda v: ["q"] * 3)
    assert m._news_quality_audit({}, {})["query_target_count"] == 3


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._news_quality_audit).splitlines()) <= 3
