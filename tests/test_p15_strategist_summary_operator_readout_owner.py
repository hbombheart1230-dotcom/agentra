"""P15: strategist_llm_summary ``_operator_readout`` moved to strategist_llm_summary_readout.operator_readout; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_readout as owner

GOLDEN = ["007e1037594d615b07409da3555285bbe677ef945f5c64de4dccf610f7e00eb5", "d8dba21b322c0e6e47a1a1160f379fcc4084a572a7422506d0d261e48bd8d3b0", "4312005847809bf05fc9f34999cf18f684f7e538d2d4d9591c457cbe01c501d0", "84444050056614f97c98dec4803ff440a461e9f9dd800d3a9d9426c64a361036", "caab3205e7140bc1f73543023ff43f9a97d24f857c01b267ced64b982ffa8ca0", "cbac846a08f11cdca2e8569643a2487e5acf0b25e163517bafa694b8d12221cb", "007e1037594d615b07409da3555285bbe677ef945f5c64de4dccf610f7e00eb5", "007e1037594d615b07409da3555285bbe677ef945f5c64de4dccf610f7e00eb5"]

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
    assert _safe(lambda: m._operator_readout(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.operator_readout(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_stage_specific_and_market_frame_text():
    assert m._operator_readout({}, None)["root_cause"] == "전략가 출력의 rationale 확인 필요" and m._operator_readout({}, None)["headline"] == "unknown / theme=none"
    st = m._operator_readout({}, {"is_stage_specific": True, "stage_name": "stage2", "decision": "BUY", "reason": "why"})
    assert st == {"headline": "stage2 / decision=BUY", "good_points": ["Stage-specific strategist response was parsed.", "Market-frame fields such as selected_themes are not required for this stage."], "issues": [],
                  "root_cause": "why", "recommended_actions": ["Review the stage decision fields instead of the market-frame section."], "validation_questions": ["Confirm monitor/executor behavior followed the stage decision."]}
    empty = m._operator_readout({}, {"is_stage_specific": True})
    assert empty["headline"] == "stage_specific / decision=-" and empty["issues"] == ["stage-specific reason is empty"] and empty["root_cause"] == "stage-specific response did not include a reason"


def test_themes_directives_and_caps():
    full = m._operator_readout(*R1[3])
    assert full["headline"] == "pb / themes=a, b, c / mode=auto" and full["root_cause"] == "fb" and len(full["good_points"]) == 3
    assert full["issues"] == ["심볼 메모리 근거가 없어 특정 종목 편향 조정은 적용되지 않았습니다."]
    best = m._operator_readout(*R1[4])
    assert best["issues"][0].startswith("selected_themes가 비어 있어") and best["issues"][1].startswith("전략 메모리에서 같은 플레이북이") and len(best["recommended_actions"]) == 2


def test_facade_directive_use_time_patch_reaches_the_owner(monkeypatch):
    calls = []
    monkeypatch.setattr(m, "_directive", lambda payload, key: (calls.append(key), {"action": "none"} if key == "selected_symbol_bias_action" else {})[1])
    out = m._operator_readout({"selected_themes": ["a"]}, None)
    assert calls == ["selected_symbol_bias_action", "entry_policy_action", "monitor_focus_action", "refresh_action"] and any("심볼 메모리" in x for x in out["issues"])


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._operator_readout).splitlines()) <= 3
