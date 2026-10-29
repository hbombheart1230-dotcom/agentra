"""P15 A4: strategist_llm_summary ``_memory_usage_from_canonical`` moved to strategist_llm_summary_usage; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_usage as owner

GOLDEN = ["6be40fa398e7547e3b3f0a0e610f87bd4be6508b6d2a116fc210fbd8a1d65b2a", "6be40fa398e7547e3b3f0a0e610f87bd4be6508b6d2a116fc210fbd8a1d65b2a", "3aebfc63ba686662b7c3408665e3e1dc608240bcb1255907ddac9f703d3df341", "980ef0b1466993bf201e5326793dceebb2100ebb3ba38eed38d4ac4250303045", "6be40fa398e7547e3b3f0a0e610f87bd4be6508b6d2a116fc210fbd8a1d65b2a", "980ef0b1466993bf201e5326793dceebb2100ebb3ba38eed38d4ac4250303045", "72e9240200743ee8560f24b0f6dbaa3163092682ff777067380241c0a21daab6"]

MEMORY = [
    {}, {"memory_usage_trace": {}}, {"memory_usage_trace": {"active_layers": ["daily"], "priority_order": ["daily", "weekly"], "human_summary": " 요약 ", "applied_to_strategy": {"a": 1}, "scanner_application": {"s": 1}, "monitor_application": {"m": 1},
        "layer_decisions": {"weekly": {"status": "ok", "active": 1, "used": 0, "confidence": 0.5, "effect": "e", "reason": "r", "gate_reason": "g", "operator_summary": {"available": 1, "status": "s", "trade_count": 3}},
                            "daily": {"status": "ok"}, "monthly": {}, "symbol": "junk", "ignored": {"status": "x"}}},
     "memory_packet_visibility": {"reporter_feedback_packet": {"v": 1}, "selected_symbol_memory": {"v": 2}, "commander_refresh_context": {"v": 3}}},
    {"memory_packet_visibility": {"reporter_feedback_packet": "junk"}}, {"memory_usage_trace": "junk", "memory_packet_visibility": []}, {"memory_usage_trace": {"layer_decisions": []}}, {"memory_usage_trace": {"layer_decisions": {"daily": {"operator_summary": "junk"}}}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(MEMORY)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = MEMORY[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._memory_usage_from_canonical(a)) == GOLDEN[i]
    assert _safe(lambda: owner.memory_usage_from_canonical(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_default_layers_order_and_visibility():
    empty = m._memory_usage_from_canonical({})
    assert empty["available"] is False and empty["layer_decisions"] == {} and empty["human_summary"] == "" and list(empty["memory_packet_visibility"]) == ["reporter_feedback_packet", "selected_symbol_memory", "commander_refresh_context"]
    full = m._memory_usage_from_canonical(MEMORY[2])
    assert full["available"] is True and list(full["layer_decisions"]) == ["daily", "weekly"]            # fixed layer order; empty/non-dict rows skipped; unknown layer ignored
    assert full["layer_decisions"]["weekly"]["operator_summary"] == {"available": True, "status": "s", "artifact_path": "", "trade_count": 3, "closed_trade_count": None, "win_rate": None, "avg_return_pct": None}
    assert full["layer_decisions"]["weekly"]["active"] is True and full["layer_decisions"]["weekly"]["used"] is False
    assert full["human_summary"] == "요약" and full["priority_order"] == ["daily", "weekly"]
    assert m._memory_usage_from_canonical(MEMORY[3])["available"] is True and m._memory_usage_from_canonical(MEMORY[4])["available"] is False


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_compact_operator_summary", lambda v: "COMPACT")
    out = m._memory_usage_from_canonical(MEMORY[2])
    assert out["layer_decisions"]["weekly"]["operator_summary"] == "COMPACT" and out["layer_decisions"]["daily"]["operator_summary"] == "COMPACT"
    monkeypatch.setattr(m, "_text", lambda v, d="-": "T")
    assert m._memory_usage_from_canonical(MEMORY[2])["human_summary"] == "T"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._memory_usage_from_canonical).splitlines()) <= 3
