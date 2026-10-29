"""P15: strategist_llm_summary ``_stage_decision_from_payload`` moved to strategist_llm_summary_decision.stage_decision_from_payload; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_decision as owner

GOLDEN = ["2b1f6e5bfd5b61913057d5b0d4e2a84bd393170a4eab34b2f35c88f2818bd637", "2b1f6e5bfd5b61913057d5b0d4e2a84bd393170a4eab34b2f35c88f2818bd637", "cfa16bc2f0e8f6d6820df50371f007b41dcb25a161a6ea8dcbbf002bbee15d73", "3c51295880257c7712ed0bc377c6e4a791f9feaf72b2c10fcc345d048f62add0", "1a2402564791fa2d7aff117344b4ef6ffbb7811d814172f8dbf5b4248e1a9ca1", "577999a75445b8b561b746839512aaa31916d545638a26b98b532a3876053366", "624d3a8a4fce2768bb820b4459c2632aa074035a6732c35fd739b644340e60f3", "6651e1e7cebdbc02f0d8cdb9e6dba234767fb7906b2ceeb1506970c824bec7e2"]

STAGE = [
    ({}, {}, None), ({"stage_index": 1}, {"call_kind": "market_strategy_frame"}, None),
    ({"selected_symbol_tactical_review": {"selected_symbol_decision": "KEEP", "target_symbol": "A", "target_rank": 2, "runner_up_order": ["B"], "monitor_instruction": {"m": 1}, "entry_policy_delta": {"e": 1}, "commander_actionability": {"c": 1}, "confidence": 0, "reason": "rr", "monitor_adjustment": {"ma": 1}},
      "priority_exit_triggers": ["t1"], "exit_pressure": " high ", "thesis_status": "ok", "next_check_minutes": 5, "payload_extra": 1, "candidate_watch_policy": {"reason": "cw"}, "strategy_refresh_trace": {"summary": "sum"}},
     {"call_kind": "selected_symbol_tactical_refresh"}, None),
    ({"hold_review_decision": "EXIT", "confidence": 0.4, "reason": "pr", "commander_actionability": "act", "runner_up_order": ["Z"]}, {"call_kind": "stale_intraday_hold_review"}, None),
    ({"carry_review_decision": "CARRY", "confidence": 0}, {"call_kind": "end_of_day_carry_review"}, {"stage_index": "bad"}), ({"stage_index": "bad"}, {"call_kind": "stale_intraday_hold_review"}, None),
    ({"tactical_refresh_decision": "T", "decision": "D"}, {"call_kind": "unknown", "stage_index": 3}, None), ({"commander_actionability": {}}, {"call_kind": "selected_symbol_tactical_refresh"}, "junk"),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(STAGE)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = STAGE[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._stage_decision_from_payload(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.stage_decision_from_payload(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_market_frame_early_return_and_stage_specific_fields():
    assert m._stage_decision_from_payload({}, {}, None) == {"is_stage_specific": False}
    assert m._stage_decision_from_payload({"stage_index": 1}, {"call_kind": "market_strategy_frame"}, None) == {"is_stage_specific": False}
    s2 = m._stage_decision_from_payload(*STAGE[2])
    assert s2["is_stage_specific"] is True and s2["stage_index"] == 2 and s2["decision"] == "KEEP" and s2["target_symbol"] == "A" and s2["target_rank"] == 2 and s2["confidence"] == 0
    assert s2["runner_up_order"] == ["B"] and s2["monitor_instruction"] == {"m": 1} and s2["commander_actionability"] == {"c": 1} and s2["reason"] == "rr"
    assert s2["raw_payload_keys"] == sorted(STAGE[2][0]) and s2["exit_pressure"] == "high"
    s3 = m._stage_decision_from_payload(*STAGE[3])
    assert s3["decision"] == "EXIT" and s3["commander_actionability"] == {"value": "act"} and s3["confidence"] == 0.4 and s3["runner_up_order"] == ["Z"]
    s4 = m._stage_decision_from_payload(*STAGE[4])
    assert s4["decision"] == "CARRY" and s4["stage_index"] == 0 and s4["confidence"] == 0 and s4["call_kind"] == "end_of_day_carry_review"
    assert m._stage_decision_from_payload(*STAGE[6])["decision"] == "T"                                                                         # tactical_refresh_decision beats decision


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_stage_meta", lambda p, r, mt: {"call_kind": "patched_kind", "stage_index": 9, "stage_name": "SN", "stage_component": "SC"})
    out = m._stage_decision_from_payload({}, {}, None)
    assert out["call_kind"] == "patched_kind" and out["stage_index"] == 9 and out["stage_name"] == "SN" and out["stage_component"] == "SC"
    monkeypatch.setattr(m, "_first_dict", lambda *v: {"patched": 1})
    assert m._stage_decision_from_payload({}, {}, None)["monitor_instruction"] == {"patched": 1}


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._stage_decision_from_payload).splitlines()) <= 8
