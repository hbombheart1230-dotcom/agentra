"""P15: strategist_llm_summary ``_memory_usage_lines_clean`` moved to strategist_llm_summary_usage_lines.memory_usage_lines_clean; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_usage_lines as owner

GOLDEN = ["7634c3b881c41c033873bf3c8b86294f627353f2f35e9f0365e87982120a19dd", "7634c3b881c41c033873bf3c8b86294f627353f2f35e9f0365e87982120a19dd", "118e3dbf80d0e4a41c4d2873c39d309daaa2d3aa7d9dd70b968accd7296560ff", "e624714ab7e4ee73dfb9690bf7693456e5de73bdc23eca6361bfea4c19f682d5", "e624714ab7e4ee73dfb9690bf7693456e5de73bdc23eca6361bfea4c19f682d5", "734e55f2ebfecc6ae098b9848b898ace86ae1c8b4d89bf8ddbd67b360eff6617", "16f7cfa9d017002ea382219967d4d9711d51849c28eeb08ab55ded8679877c74"]

MEMORY = [
    {}, {"available": False, "human_summary": "x"},
    {"available": True, "active_layers": ["daily", "weekly"], "priority_order": ["daily", "weekly", "symbol"], "human_summary": " 요약 ", "applied_to_strategy": {"playbook_effect": "pe", "risk_posture_effect": "re", "scanner_guidance_effect": "se", "monitor_policy_effect": "me"},
     "layer_decisions": {"daily": {"used": True, "status": "ok", "effect": "e1", "operator_summary": {"trade_count": 3, "win_rate": 0.5, "avg_return_pct": 1.2}},
                         "weekly": {"used": False, "status": " s ", "effect": "", "operator_summary": {"trade_count": 0}}, "monthly": {}, "symbol": {"used": 1, "status": "x", "effect": "y", "operator_summary": {"win_rate": 0, "avg_return_pct": None}}, "extra": {"used": 1}}},
    {"available": True}, {"available": True, "active_layers": "junk", "priority_order": 5, "applied_to_strategy": "junk", "layer_decisions": [1]},
    {"available": True, "layer_decisions": {"daily": {"operator_summary": "junk"}, "symbol": "junk"}}, {"available": 1, "active_layers": [1, None, "z"]},
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
    assert _safe(lambda: m._memory_usage_lines_clean(a)) == GOLDEN[i]
    assert _safe(lambda: owner.memory_usage_lines_clean(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_exact_lines_and_layer_order():
    f = m._memory_usage_lines_clean
    assert f({}) == ["- 메모리 사용 trace: -"] and f({"available": False, "human_summary": "x"}) == ["- 메모리 사용 trace: -"]
    assert f(MEMORY[2]) == ["- 활성 레이어: daily, weekly", "- 우선순위: daily -> weekly -> symbol", "- 요약: 요약", "- 전략 반영: playbook=pe, risk=re",
                            "- scanner/monitor 반영: scanner=se, monitor=me", "- daily: used=True status=ok effect=e1 (trades=3, win_rate=0.5, avg_return_pct=1.2)",
                            "- weekly: used=False status=s effect= (trades=0)", "- symbol: used=1 status=x effect=y (win_rate=0)"]          # monthly/extra skipped; zero metrics kept
    assert f(MEMORY[3]) == ["- 활성 레이어: -", "- 우선순위: -", "- 요약: -"] and f(MEMORY[4]) == f(MEMORY[3])
    assert f(MEMORY[5])[-1] == "- daily: used=None status= effect=" and f(MEMORY[6])[0] == "- 활성 레이어: 1, None, z"


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_as_list", lambda v: ["PATCHED"])
    assert m._memory_usage_lines_clean({"available": True})[0] == "- 활성 레이어: PATCHED"
    monkeypatch.setattr(m, "_text", lambda v, d="-": "TXT")
    assert m._memory_usage_lines_clean({"available": True})[2] == "- 요약: TXT"
    monkeypatch.setattr(m, "_as_dict", lambda v: {"playbook_effect": "P"})
    assert any("playbook=TXT" in line for line in m._memory_usage_lines_clean({"available": True}))


def test_clean_and_normal_memory_callers_stay_separate_functions():
    assert m._memory_usage_lines_clean is not m._memory_usage_lines and owner.memory_usage_lines_clean is not owner.memory_usage_lines
    assert m._memory_usage_lines_clean(MEMORY[2]) == m._memory_usage_lines(MEMORY[2])              # identical today, but each keeps its own body


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._memory_usage_lines_clean).splitlines()) <= 3
