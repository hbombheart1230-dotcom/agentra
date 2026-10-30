"""P15: strategist_llm_summary ``_render_stage_specific_summary_markdown_clean`` moved to strategist_llm_summary_stage_markdown.render_stage_specific_summary_markdown_clean; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_stage_markdown as owner

GOLDEN = ["9740b0728704abb610af6dd0ad9b66d612140407d0f7f2dd9398242e762d4155", "EXC:AttributeError", "e7047df7de9a71682fb685504a4e779b6b65db8d6fc261be120679a9b71a2a5e", "8e75a20626814b4b2eeafad0dcf4545e1fd11c1f224f6073266e30c1e6bdaa8f", "9740b0728704abb610af6dd0ad9b66d612140407d0f7f2dd9398242e762d4155", "52b6c275aae00c503c16f99e8b2b758edeaad225413259026cdd3888200b4f1d"]

STAGE_MD = [
    {}, None,
    {"llm_meta": {"day": "2026-10-20", "status": "ok", "model": "m/x", "stage_component": "sc", "run_id": "r1", "saved_at": "t"}, "operator_readout": {"headline": "헤드", "root_cause": "원인", "good_points": ["g1", "g2"], "issues": ["i1"], "recommended_actions": ["a1"]},
     "stage_decision": {"stage_index": 2, "stage_name": "stage2", "call_kind": "selected_symbol_tactical_refresh", "stage_component": "", "decision": "KEEP", "target_symbol": "005930", "target_rank": 1, "runner_up_order": ["B", "C"], "confidence": 0.6,
                        "exit_pressure": "low", "thesis_status": "intact", "next_check_minutes": 5, "priority_exit_triggers": ["t1", "t2"], "monitor_instruction": {"z": [1], "a": {"k": "한글"}, "m": None}, "entry_policy_delta": {"b": 1, "a": 2},
                        "commander_actionability": {"value": "act"}, "reason": "이유"},
     "strategy_detail": {"final_playbook": "fp", "tactical_strategy": "ts", "pre_llm_playbook": "pre", "requested_playbook": "req", "requested_playbook_source": "src", "candidate_watch_policy": {"max_priority_rank": 3, "max_runner_ups": 2, "cascade_enabled": False}},
     "market_regime_rail": {"market_regime": "bull"}, "source_response_json": "r.json", "source_canonical_strategist_json": "c.json", "generated_at": "g"},
    {"stage_decision": {"stage_index": 3}, "llm_meta": {"stage_component": "meta_sc"}, "strategy_detail": {}}, {"stage_decision": "junk", "operator_readout": "junk", "strategy_detail": []},
    {"stage_decision": {"stage_index": 4, "runner_up_order": "abc", "priority_exit_triggers": [None, 0], "monitor_instruction": {}, "entry_policy_delta": {"x": float("inf")}}, "operator_readout": {"good_points": "str"}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(STAGE_MD)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = STAGE_MD[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._render_stage_specific_summary_markdown_clean(a)) == GOLDEN[i]
    assert _safe(lambda: owner.render_stage_specific_summary_markdown_clean(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_populated_stage_markdown_sections_sorted_keys_and_utf8():
    text = m._render_stage_specific_summary_markdown_clean(STAGE_MD[2])
    lines = text.split("\n")
    assert lines[0] == "# Strategist LLM Summary (2026-10-20)" and text.endswith("\n") and lines[-1] == ""
    assert [x for x in lines if x.startswith("#")] == ["# Strategist LLM Summary (2026-10-20)", "## 단계별 전략가 LLM 출력", "### 결정", "### 모니터 지시", "### 진입 정책 delta", "### 지휘관 적용 가능성", "### 사유",
        "## Canonical 전략 컨텍스트", "## Input/Output Quality Audit", "### Market Regime Rail", "### News Quality", "### Risk-Off Exceptions", "### News Event Intelligence", "### Strategist Output Quality",
        "## 운영 점검", "### 잘 된 점", "### 문제점", "### 권고 액션", "## 근거"]
    assert lines.index('- a: {"k": "한글"}') < lines.index("- m: null") < lines.index("- z: [1]")                      # monitor_instruction keys sorted, ensure_ascii=False JSON
    assert "- playbook_flow: pre -> req -> fp (source=src)" in lines and "- candidate_watch: 3위까지 / 차순위 2개 / cascade 비활성" in lines
    assert "- runner_up_order: B, C" in lines and "- stage component: sc" in lines and '- value: "act"' in lines
    assert "- 요약: **헤드**" in lines and "- g1" in lines and "- run_id: `r1`" in lines


def test_empty_payload_uses_dash_fallbacks_and_meta_component_fallback():
    empty = m._render_stage_specific_summary_markdown_clean({})
    assert empty.split("\n")[0] == "# Strategist LLM Summary (-)" and empty.count("- -") >= 4 and "- candidate_watch: -" in empty and "- run_id: ``" in empty
    meta = m._render_stage_specific_summary_markdown_clean(STAGE_MD[3])
    assert "- stage component: meta_sc" in meta and "- 단계: 3 / -" in meta
    with pytest.raises(AttributeError):
        m._render_stage_specific_summary_markdown_clean(None)


def test_facade_helper_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_playbook_flow_label", lambda d: "FLOW")
    monkeypatch.setattr(m, "_watch_scope_label_clean", lambda w: "WATCH")
    monkeypatch.setattr(m, "_quality_audit_lines", lambda p: ["## QA", ""])
    monkeypatch.setattr(m, "_bullet_lines", lambda items: ["- BULLET"])
    out = m._render_stage_specific_summary_markdown_clean(STAGE_MD[2])
    assert "- playbook_flow: FLOW" in out and "- candidate_watch: WATCH" in out and "## QA" in out and out.count("- BULLET") == 3 and "Input/Output Quality Audit" not in out
    monkeypatch.setattr(m, "_json_inline", lambda v: "J")
    assert "- a: J" in m._render_stage_specific_summary_markdown_clean(STAGE_MD[2])


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._render_stage_specific_summary_markdown_clean).splitlines()) <= 3
