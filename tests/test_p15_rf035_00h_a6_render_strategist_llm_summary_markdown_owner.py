"""P15 RF-035 (00h): strategist_llm_summary.render_strategist_llm_summary_markdown moved to strategist_llm_summary_render_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
import hashlib

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_render_projection as owner


FIXTURES = json.loads("[{}, {\"llm_meta\": {\"day\": \"2026-10-30\", \"run_id\": \"R1\", \"model\": \"mdl\", \"status\": \"ok\"}, \"strategy_frame\": {\"playbook\": \"opening_gap\", \"selected_themes\": [\"반도체\", \"2차전지\"], \"rationale\": \"근거 문장\", \"tactical_strategy\": \"breakout\", \"strategy_scores\": {\"a\": 0.5, \"b\": \"1.5\", \"c\": \"bad\"}, \"rejected_strategy_reasons\": {\"x\": \"too late\"}, \"candidate_watch_policy\": {\"scope\": \"top3\"}}, \"strategy_detail\": {\"issues\": [\"i1\", \"i2\"], \"good_points\": [\"g1\"], \"recommended_actions\": [\"r1\"], \"validation_questions\": [\"q1\"]}, \"operator_readout\": {\"bullets\": [\"b1\", \"b2\"], \"policy_changes\": [\"p1\"]}, \"memory_usage\": {\"used\": true, \"lines\": [\"m1\"]}, \"news_usage\": {\"used\": false}, \"monitor_handoff\": {\"monitor_entry_policy\": \"hold\", \"entry_policy_action\": \"wait\", \"exit_guidance\": \"tight\", \"expected_hold_window\": \"1d\", \"invalidation_conditions\": [\"v1\"], \"monitor_focus_action\": \"watch\"}, \"strategy_horizon_feedback\": {\"x\": 1}, \"strategy_refresh_trace\": {\"refresh_action\": \"keep\", \"playbook_action\": \"keep\", \"selected_symbol_bias_action\": \"none\"}}, {\"stage_decision\": {\"is_stage_specific\": true}, \"stages\": [{\"stage_name\": \"s1\"}]}, {\"llm_meta\": {\"day\": \"d\"}, \"strategy_frame\": {\"playbook\": \"p\"}}, {\"llm_meta\": {\"day\": \"2026-10-30\", \"run_id\": \"R1\", \"model\": \"mdl\", \"status\": \"ok\"}, \"strategy_frame\": {\"playbook\": \"opening_gap\", \"selected_themes\": [\"반도체\", \"2차전지\"], \"rationale\": \"근거 문장\", \"tactical_strategy\": \"breakout\", \"strategy_scores\": {\"a\": 0.5, \"b\": \"1.5\", \"c\": \"bad\"}, \"rejected_strategy_reasons\": {\"x\": \"too late\"}, \"candidate_watch_policy\": {\"scope\": \"top3\", \"symbols\": [\"005930\"]}, \"pre_llm_playbook\": \"pre\", \"llm_requested_playbook\": \"req\", \"requested_playbook\": \"req2\", \"requested_playbook_source\": \"src\", \"final_playbook\": \"fin\"}, \"strategy_detail\": {\"pre_llm_playbook\": \"pre\", \"llm_requested_playbook\": \"req\", \"requested_playbook\": \"req2\", \"requested_playbook_source\": \"src\", \"final_playbook\": \"fin\", \"tactical_strategy\": \"breakout\", \"strategy_scores\": {\"a\": 0.5, \"b\": \"1.5\", \"c\": \"bad\"}, \"rejected_strategy_reasons\": {\"x\": \"too late\"}, \"candidate_watch_policy\": {\"scope\": \"top3\", \"symbols\": [\"005930\"]}}, \"operator_readout\": {\"bullets\": [\"b1\", \"b2\"], \"policy_changes\": [\"p1\"]}, \"memory_usage\": {\"status\": \"used\", \"count\": 2, \"items\": [{\"title\": \"m1\"}]}, \"news_usage\": {\"status\": \"used\", \"count\": 1, \"items\": [{\"title\": \"n1\"}]}, \"monitor_handoff\": {\"monitor_entry_policy\": \"hold\", \"entry_policy_action\": \"wait\", \"exit_guidance\": \"tight\", \"expected_hold_window\": \"1d\", \"invalidation_conditions\": [\"v1\"], \"monitor_focus_action\": \"watch\"}, \"strategy_horizon_feedback\": {\"x\": 1}, \"strategy_refresh_trace\": {\"refresh_action\": \"keep\", \"playbook_action\": \"keep\", \"selected_symbol_bias_action\": \"none\"}, \"quality_audit\": {\"market_regime_rail\": {\"rail_id\": \"r\"}}}]")
# sha256 of the output of the pre-move function for each fixture (captured from the original source)
GOLDEN = ['7861499ef584527ec7a565c36d8ae83b55a0a20d4726a04cb93a4ec3c25d72de', 'b63e6d4fe798bec5ff36568cf213bf0a966a11219227457c10c2fb30658155fa', 'a51621888b391b46fc56e6ed56d12eab7308ff2d981e3dcadca748995f80afb7', 'bd693cf2895160726437e18a08d7184a00be055c642fdce6d9c4ba433e119199', '08f37fb647ac2541c380a60f6d5d8e41d3a02a49fecc69e2120224a46a075b4d']


def _h(text):
    return hashlib.sha256(text.encode()).hexdigest()


@pytest.mark.parametrize("i", range(len(FIXTURES)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = FIXTURES[i]
    snap = copy.deepcopy(payload)
    a = m.render_strategist_llm_summary_markdown(payload)
    b = owner.render_strategist_llm_summary_markdown(payload, facade=m)
    assert a == b and _h(a) == GOLDEN[i] and payload == snap


def test_stage_specific_sentinel(monkeypatch):
    monkeypatch.setattr(m, "_render_stage_specific_summary_markdown_clean", lambda p: "STAGE_SENTINEL")
    payload = {"stage_decision": {"is_stage_specific": True}}
    assert m.render_strategist_llm_summary_markdown(payload) == owner.render_strategist_llm_summary_markdown(payload, facade=m) == "STAGE_SENTINEL"


def test_facade_helper_seams(monkeypatch):
    monkeypatch.setattr(m, "_as_dict", lambda v: {})
    a = m.render_strategist_llm_summary_markdown(FIXTURES[1])
    b = owner.render_strategist_llm_summary_markdown(FIXTURES[1], facade=m)
    assert a == b and a.startswith("# Strategist LLM Summary (-)")
    monkeypatch.undo()
    monkeypatch.setattr(m, "_bullet_lines", lambda items, empty="-": ["- SEAM"])
    a = m.render_strategist_llm_summary_markdown(FIXTURES[1])
    assert a == owner.render_strategist_llm_summary_markdown(FIXTURES[1], facade=m) and "- SEAM" in a


def test_shadowed_earlier_definition_untouched():
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(m))
    defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "render_strategist_llm_summary_markdown"]
    assert len(defs) == 2 and (defs[0].end_lineno - defs[0].lineno) > 100 and (defs[1].end_lineno - defs[1].lineno) <= 3
