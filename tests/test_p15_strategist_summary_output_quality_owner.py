"""P15: strategist_llm_summary ``_strategist_output_quality_audit`` moved to strategist_llm_summary_decision.strategist_output_quality_audit; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_decision as owner

GOLDEN = ["6d7102fd41033ae04b437fcbb1323454c30415fe90a18658f84db150b9b1a3a3", "a02be3702f72c0d6e90b8046a98da1bdc040e023fbe8b253ce0be545f8c2b7f6", "987fc6954056ee6e01ed3f7ff25c2d6f83db07da1900d06ad8e0fcb02114c7fa", "a9ec4d7ae80d6a5c9c4d665e5a703763404d64d795ee14d5ff028f86318fc439", "5f6b834adafc1a5d9e90534bc4f62692fd7ee2ee7d320ad2f5d60d140ffb29e3", "EXC:AttributeError", "EXC:AttributeError"]

AUDIT = [
    dict(payload={}, canonical={}, stage_decision={}, strategy_detail={}, market_rail={}, news_quality={}),
    dict(payload={"decision": "BUY", "confidence": 0.7}, canonical={"memory_usage_trace": {"active_layers": ["daily"]}}, stage_decision={"is_stage_specific": False}, strategy_detail={"final_playbook": "pb", "tactical_strategy": "ts", "candidate_watch_policy": {"a": 1}},
         market_rail={"market_regime": "bull", "market_regime_rail": "rail_ok"}, news_quality={"status": "ok"}),
    dict(payload={}, canonical={"memory_usage_trace": {"active_layers": ["daily"]}}, stage_decision={"is_stage_specific": True, "decision": "HOLD", "confidence": 0, "monitor_instruction": {"x": 1}}, strategy_detail={}, market_rail={"market_regime_rail": "macro_packet_unavailable"}, news_quality={"status": "weak"}),
    dict(payload={"decision": "d"}, canonical={"memory_usage_trace": {}, "memory_packet_visibility": {"x": 1}}, stage_decision={"is_stage_specific": True, "decision": "", "entry_policy_delta": {}}, strategy_detail={"final_playbook": "p"}, market_rail={"market_regime_rail": "r"}, news_quality={"status": "ok"}),
    dict(payload={"decision": "d", "confidence": ""}, canonical={}, stage_decision={}, strategy_detail={"final_playbook": "p", "tactical_strategy": "t"}, market_rail={"market_regime_rail": "r"}, news_quality={"status": "ok"}),
    dict(payload=None, canonical={}, stage_decision={}, strategy_detail={}, market_rail={}, news_quality={}), dict(payload={}, canonical={}, stage_decision=None, strategy_detail={}, market_rail={}, news_quality={}),
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
    assert _safe(lambda: m._strategist_output_quality_audit(**a)) == GOLDEN[i]
    assert _safe(lambda: owner.strategist_output_quality_audit(facade=m, **a)) == GOLDEN[i]
    assert a == snap


def test_status_boundaries_and_issue_order():
    f = lambda i: m._strategist_output_quality_audit(**AUDIT[i])
    assert f(1)["status"] == "ok" and f(1)["issues"] == [] and f(1)["schema_version"] == "strategist_output_quality_audit.v1"
    assert list(f(1)) == ["schema_version", "status", "issues", "decision", "confidence", "final_playbook", "tactical_strategy", "market_regime", "market_regime_rail", "candidate_watch_policy_present", "memory_available",
                          "memory_active_layers", "news_quality_status"]
    assert f(2)["status"] == "watch" and f(2)["issues"] == ["market_regime_rail_missing", "news_quality_not_ok"]                                  # 2 issues -> watch
    assert f(3)["status"] == "needs_review" and f(3)["issues"] == ["confidence_missing", "stage_control_fields_missing", "memory_active_layers_empty"]
    assert f(0)["status"] == "needs_review" and len(f(0)["issues"]) == 8 and f(0)["issues"][0] == "decision_missing" and f(0)["issues"][-1] == "memory_trace_missing_or_disabled"
    assert f(2)["confidence"] == 0                                                                                                              # 0 is a real confidence, not missing


def test_original_attribute_errors_for_none_inputs():
    for i in (5, 6):
        with pytest.raises(AttributeError):
            m._strategist_output_quality_audit(**AUDIT[i])


def test_facade_memory_helper_use_time_patch_reaches_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_memory_usage_from_canonical", lambda c: {"available": True, "active_layers": ["x"]})
    out = m._strategist_output_quality_audit(**AUDIT[0])
    assert out["memory_available"] is True and out["memory_active_layers"] == ["x"] and "memory_trace_missing_or_disabled" not in out["issues"]


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._strategist_output_quality_audit).splitlines()) <= 12
