"""P15 A1: strategist_llm_summary ``_infer_call_kind`` moved to strategist_llm_summary_stage; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_stage as owner

GOLDEN = ["12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "2659efe5502f101c13c3d4f2b330ba7bc6969f33ce5aee8377560e7470bf30b4", "0f4657778ae14ff7aeeb2c2190ede79099aa9c4e8a9e54829462f0e92af659e5", "1fb680aa1ed965bc09f024abd808fad41e7fa0bb2e1ec39e8f237d653d56b456", "d41280b1fc319f212c9afd66d0d0d6e4394345ad446a53162bcc60bb1c2f88da", "cd9e7b905c01bad5a7934ebeaf480a7f4fbec80caf944b931195e353d97db74f", "b1a42f592999914c45d674af3e64bcd9271f00cbcf0dd335ef4cb7e20bce6673", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "d41280b1fc319f212c9afd66d0d0d6e4394345ad446a53162bcc60bb1c2f88da", "d41280b1fc319f212c9afd66d0d0d6e4394345ad446a53162bcc60bb1c2f88da", "d41280b1fc319f212c9afd66d0d0d6e4394345ad446a53162bcc60bb1c2f88da", "cd9e7b905c01bad5a7934ebeaf480a7f4fbec80caf944b931195e353d97db74f", "b1a42f592999914c45d674af3e64bcd9271f00cbcf0dd335ef4cb7e20bce6673", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "d10a4bc9e0c1fa4e8f3d7ce2512b8756e47ca5fa451f373c39a1431bb88db49f"]

KIND = [
    ({}, {}, None), ({"call_kind": "p"}, {"call_kind": "r"}, {"call_kind": "s"}), ({"call_kind": "p"}, {}, {"call_kind": "s"}), ({"call_kind": " p "}, {}, None),
    ({}, {"stage_component": "strategist_stage2_selected_symbol"}, None), ({}, {}, {"stage_component": "strategist_stage3_hold_review"}), ({}, {"component": "strategist_stage4_carry_review"}, None),
    ({}, {"stage_component": "other"}, None), ({"selected_symbol_decision": {}}, {}, None), ({"target_symbol": "A"}, {}, None), ({"runner_up_order": []}, {}, None),
    ({"hold_review_decision": 0}, {}, None), ({"carry_review_decision": ""}, {}, None), ({"selected_symbol_decision": None}, {}, None), ({}, {}, "junk"), ({}, {"call_kind": 5}, None),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(KIND)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = KIND[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._infer_call_kind(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.infer_call_kind(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_explicit_priority_component_mapping_and_payload_fallback():
    k = m._infer_call_kind
    assert k({}, {}, None) == "" and k({"call_kind": "p"}, {"call_kind": "r"}, {"call_kind": "s"}) == "r" and k({"call_kind": "p"}, {}, {"call_kind": "s"}) == "s" and k({"call_kind": " p "}, {}, None) == "p"
    assert k({}, {"stage_component": "strategist_stage2_selected_symbol"}, None) == "selected_symbol_tactical_refresh"
    assert k({}, {}, {"stage_component": "strategist_stage3_hold_review"}) == "stale_intraday_hold_review"
    assert k({}, {"component": "strategist_stage4_carry_review"}, None) == "end_of_day_carry_review"
    assert k({}, {"stage_component": "other"}, None) == ""
    assert k({"selected_symbol_decision": {}}, {}, None) == k({"target_symbol": "A"}, {}, None) == k({"runner_up_order": []}, {}, None) == "selected_symbol_tactical_refresh"
    assert k({"hold_review_decision": 0}, {}, None) == "stale_intraday_hold_review" and k({"carry_review_decision": ""}, {}, None) == "end_of_day_carry_review"
    assert k({"selected_symbol_decision": None}, {}, None) == ""


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "_as_dict", lambda v: (seen.append("dict"), {"call_kind": "from_patch"})[1])
    assert m._infer_call_kind({}, {}, "ignored") == "from_patch" and seen == ["dict"]
    monkeypatch.setattr(m, "_text", lambda v, d="-": "T")
    assert m._infer_call_kind({}, {}, None) == "T"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._infer_call_kind).splitlines()) <= 3
