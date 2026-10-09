"""P1.5.2 Markdown clean output-only labels: pinned AST/output and call-time seams."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_report_markdown_clean as api
from libs.reporting.trade_report.markdown_clean_parts import operator_labels, strategist_language

BASE="52508ade9d0d246fa4e848525fe62f2fe067acb7"
SOURCE="libs/reporting/trade_report_markdown_clean.py"
NAMES={
    operator_labels: ["_rank_scope_text","_watch_scope_label","_candidate_watch_reason_label","_story_type_label","_execution_mode_label","_action_label","_status_label","_axis_label","_risk_mode_label","_theme_label","_policy_token_label","_playbook_label","_monitor_guidance_label","_scanner_bias_label","_policy_source_label","_failure_label","_reporter_source_label","_humanize_reporter_source_label"],
    strategist_language: ["_operatorize_strategist_output_text","_strategy_output_text","_strategy_output_list_text"],
}
def old(name):
    source=subprocess.check_output(["git","show",f"{BASE}:{SOURCE}"],text=True,encoding="utf-8-sig")
    node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name==name)
    env=vars(api).copy()
    exec(compile(ast.Module(body=[node],type_ignores=[]),"<old-display-owner>","exec"),env)
    return node,env[name]

@pytest.mark.parametrize("module,name",[(mod,n) for mod,names in NAMES.items() for n in names])
def test_ast_and_owner_size(module,name):
    original,_=old(name)
    after=next(x for x in ast.parse(Path(module.__file__).read_text(encoding="utf-8")).body if isinstance(x,ast.FunctionDef) and x.name==name+"_impl")
    assert ast.dump(ast.Module(body=original.body,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=after.body,type_ignores=[]),include_attributes=False)
    assert len(Path(module.__file__).read_text(encoding="utf-8").splitlines())<=350

@pytest.mark.parametrize("name,value", [
    ("_rank_scope_text",{"max_priority_rank":2,"max_runner_ups":3}),
    ("_watch_scope_label",{"max_priority_rank":1}),
    ("_candidate_watch_reason_label","entry_control_disabled"),
    ("_story_type_label","simulation"),("_execution_mode_label","real broker"),
    ("_action_label","BUY"),("_status_label","closed"),("_axis_label","hard_stop"),
    ("_risk_mode_label","defensive"),("_theme_label","illiquid_microcap"),
    ("_policy_token_label","confidence_ok"),("_playbook_label","pullback"),
    ("_monitor_guidance_label","defensive_exit"),("_scanner_bias_label","leader"),
    ("_policy_source_label","baseline_monitor_policy"),("_failure_label","playbook:breakout"),
    ("_reporter_source_label",{"reporter_analysis":True}),
    ("_humanize_reporter_source_label",{"trade_reports":True}),
    ("_operatorize_strategist_output_text","defensive frame"),
    ("_strategy_output_text","pullback frame"),
    ("_strategy_output_list_text",["defensive frame","pullback frame"]),
])
def test_display_matches_old(name,value):
    _,original=old(name)
    assert getattr(api,name)(value)==original(value)

def test_call_time_patch_seams(monkeypatch):
    monkeypatch.setattr(api,"_metadata_value",lambda x:"PATCHED")
    assert api._candidate_watch_reason_label("unknown")=="PATCHED"
    monkeypatch.setattr(api,"_playbook_label",lambda x:"PATCHED")
    assert api._failure_label("playbook:unknown")=="PATCHED 전략 프레임 실패"
    monkeypatch.setattr(api,"_operatorize_strategist_output_text",lambda x:"PATCHED")
    assert api._strategy_output_text("anything")=="PATCHED"
    monkeypatch.setattr(api,"_reporter_source_label",lambda x:"not_recorded")
    assert api._humanize_reporter_source_label({})=="기록되지 않은 소스"
