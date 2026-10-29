"""P15: strategist_llm_summary ``_quality_audit_lines`` moved to strategist_llm_summary_quality_lines.quality_audit_lines; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_quality_lines as owner

GOLDEN = ["ca6e7bd3733bde95dbe935a9c6fb296058e499143db28f6914228cbc436a6317", "a5fe878644a1d8d0723d0afefa82a7c1c8e8bdaf9c6fb8e660245a494b49129a", "ca6e7bd3733bde95dbe935a9c6fb296058e499143db28f6914228cbc436a6317", "93db174e80cad8ed891e984ee4a6133f68eb19b92d9649eaa53d9c196704bf6e", "6a6c042a2bc7670a0d3478df8999313c7824984f04cbcb423122e340e718ef2f", "EXC:AttributeError"]

LINES = [
    {}, {"market_regime_rail": {"market_regime": "bull", "market_regime_rail": "ok", "risk_score": 3, "metrics": {"kospi_pct": 1.2, "kosdaq_pct": -0.3, "breadth_score": 0.5}, "issues": ["i1", "", "i2"]},
         "news_quality_audit": {"status": "ok", "headline_count": 5, "market_headline_count": 2, "candidate_headline_count": 3, "query_target_count": 4, "issues": []},
         "risk_off_exception_policy": {"risk_off_active": True, "allowed_exception_conditions": ["c1", "c2"], "instruction": "지시"}, "risk_off_exception_conditions": ["rc"],
         "news_event_intelligence": {"behavior_effect": "obs", "trading_action_allowed": False, "input_summary": {"event_count": 7}, "theme_watchlist": [{"theme": "t%d" % i} for i in range(8)], "symbol_watchlist": ["s1", {"symbol": "s2"}, 5, None, {"symbol": ""}]},
         "news_event_intelligence_usage": {"status": "used", "reason": "r"}, "strategist_output_quality_audit": {"status": "watch", "decision": "BUY", "confidence": 0.8, "final_playbook": "fp", "tactical_strategy": "ts", "issues": ["x"]}},
    {"market_regime_rail": "junk", "news_event_intelligence": {"theme_watchlist": "junk", "symbol_watchlist": [None, {}]}}, {"news_event_intelligence": {"trading_action_allowed": None}},
    {"strategist_output_quality_audit": {"confidence": 0, "issues": ["", "  "]}}, None,
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(LINES)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = LINES[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._quality_audit_lines(a)) == GOLDEN[i]
    assert _safe(lambda: owner.quality_audit_lines(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_exact_empty_and_full_sections():
    empty = m._quality_audit_lines({})
    assert empty[:5] == ["## Input/Output Quality Audit", "", "### Market Regime Rail", "", "- market_regime: -"] and empty[-1] == "" and len(empty) == 47
    assert "- behavior_effect: observation_only" in empty and "- trading_action_allowed: False" in empty and "- event_count: 0" in empty
    full = m._quality_audit_lines(LINES[1])
    assert len(full) == 47 and "- issues: i1, i2" in full and "- theme_watchlist: t0, t1, t2, t3, t4, t5" in full               # watchlist cap 6
    assert "- symbol_watchlist: s1, s2, 5" in full                                                                              # str/dict mix, blank skipped
    assert "- instruction: 지시" in full and "- allowed_exception_conditions: c1, c2" in full and "- confidence: 0.8" in full
    assert [x for x in full if x.startswith("### ")] == ["### Market Regime Rail", "### News Quality", "### Risk-Off Exceptions", "### News Event Intelligence", "### Strategist Output Quality"]
    assert m._quality_audit_lines(LINES[4])[-2] == "- issues: -" and "- confidence: 0" in m._quality_audit_lines(LINES[4])


def test_malformed_inputs_and_none_error():
    assert len(m._quality_audit_lines(LINES[2])) == 47
    with pytest.raises(AttributeError):
        m._quality_audit_lines(None)


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_text", lambda v, d="-": "TXT")
    out = m._quality_audit_lines({})
    assert "- market_regime: TXT" in out and "- status: TXT" in out
    monkeypatch.setattr(m, "_as_dict", lambda v: {"risk_off_active": "PATCHED"})
    assert "- risk_off_active: PATCHED" in m._quality_audit_lines({})


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._quality_audit_lines).splitlines()) <= 3
