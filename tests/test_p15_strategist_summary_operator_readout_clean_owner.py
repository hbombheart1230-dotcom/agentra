"""P15: strategist_llm_summary ``_operator_readout_clean`` moved to strategist_llm_summary_readout.operator_readout_clean; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_readout as owner

GOLDEN = ["86872781ba8fe833474fecb23aa9042aa5ba6db1fb2c5a550452cad56e188efc", "65688a3dcb0f4539e6b0dc2053f02d06ca8ca8f2dcd61b5cad217c00019e4bd6", "9bd51bab2283a73b0c4a1074b1dccf83541eee4a2b7b2fcdf72a802fd0a90973", "c954e4f8aeb33e39c3945983b1a0aedd74ef6d1259c6be2005dde3f3eb37641c", "67f9095d5449c3f94eeca55ad90194ef291dd948f2982d6505793f53e3d133ce", "71adda2b8377d37f33a0e3c448ccade5f1f62b863aff709776d1304c5a7b030c", "86872781ba8fe833474fecb23aa9042aa5ba6db1fb2c5a550452cad56e188efc", "86872781ba8fe833474fecb23aa9042aa5ba6db1fb2c5a550452cad56e188efc"]

R1 = [
    ({}, None), ({}, {"is_stage_specific": True, "stage_name": "stage2", "decision": "BUY", "reason": "why"}), ({}, {"is_stage_specific": True}),
    ({"playbook": "pb", "selected_themes": ["a", "b", "c", "d"], "theme_strategy": {"selection_mode": "auto", "fallback_reason": "fb"}, "rationale": "r",
      "strategy_adjustment_directives": {"entry_policy_action": {"x": 1}, "monitor_focus_action": {"y": 1}, "refresh_action": {"z": 1}, "selected_symbol_bias_action": {"action": " None "}}}, None),
    ({"selected_themes": [], "rationale": "Best and Worst overlap here"}, None), ({"rationale": "best 및 worst", "selected_themes": ["t"]}, {}), ({"theme_strategy": "junk", "selected_themes": "abc"}, None),
    ({"selected_themes": 5}, None),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(R1)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = R1[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._operator_readout_clean(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.operator_readout_clean(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_clean_variant_keeps_its_own_korean_strings_distinct_from_the_original():
    clean = m._operator_readout_clean(*R1[1])
    assert clean["good_points"] == ["단계별 전략가 응답이 파싱됐습니다.", "이 단계는 시장 프레임이 아니므로 selected_themes 같은 1차 필드는 필수가 아닙니다."]
    assert clean["recommended_actions"] == ["시장 프레임 섹션이 아니라 단계별 decision 필드를 확인합니다."] and clean["issues"] == [] and clean["root_cause"] == "why"
    assert m._operator_readout_clean(*R1[2])["issues"] == ["단계별 응답의 reason이 비어 있습니다."]
    assert m._operator_readout_clean(*R1[1]) != m._operator_readout(*R1[1])


def test_clean_variant_theme_and_best_worst_rules():
    d = m._operator_readout_clean(*R1[3])
    assert d["headline"] == "pb / themes=a, b, c / mode=auto" and d["root_cause"] == "fb" and d["issues"] == ["성과 메모리 근거가 없어 특정 종목 영향 조정은 적용되지 않았습니다."]
    e = m._operator_readout_clean(*R1[4])
    assert e["issues"][1] == "전략 메모리에서 같은 플레이북이 best/worst에 동시에 잡혀 방향 신호가 혼합됩니다."
    assert m._operator_readout_clean(*R1[5])["root_cause"] == "best 및 worst" and "best/worst" in m._operator_readout_clean(*R1[5])["issues"][0]



def test_legacy_mojibake_literal_is_preserved_verbatim_in_the_owner_source():
    assert "best 諛?worst" in inspect.getsource(owner)


def test_facade_directive_use_time_patch_reaches_the_owner(monkeypatch):
    calls = []
    monkeypatch.setattr(m, "_directive", lambda payload, key: (calls.append(key), {})[1])
    m._operator_readout_clean({}, None)
    assert "selected_symbol_bias_action" in calls and "entry_policy_action" in calls


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._operator_readout_clean).splitlines()) <= 3
