"""P1.5.2 AI facade pure narrative labels: original AST, output and patch tests."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_report_ai as api
from libs.reporting.trade_report.ai_facade_parts import market_labels, scanner_labels

BASE="183924bdbe2e51723987436b45a48d0e849724db"
FILE="libs/reporting/trade_report_ai.py"
NAMES={
    market_labels: ["_market_token_label","_theme_token_label","_theme_text","_theme_linkage_label","_risk_mode_label","_strategy_constraint_label","_strategy_constraint_text","_scanner_bias_label","_scanner_bias_text"],
    scanner_labels: ["_scanner_source_label","_scanner_source_text","_scanner_score_driver_label","_scanner_chart_feature_label","_scanner_check_name_label","_scanner_check_status_label","_entry_reason_label","_decision_chain_label","_execution_mode_label","_entry_path_label","_entry_gate_state_label","_entry_gate_name_label"],
}
def old(name):
    text=subprocess.check_output(["git","show",f"{BASE}:{FILE}"],text=True,encoding="utf-8-sig")
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
    glob=vars(api).copy()
    exec(compile(ast.Module(body=[node],type_ignores=[]),"<prior-ai-label>","exec"),glob)
    return node,glob[name]

@pytest.mark.parametrize("owner,name",[(module,name) for module,names in NAMES.items() for name in names])
def test_exact_function_body_and_small_owner(owner,name):
    prev,_=old(name)
    curr=next(n for n in ast.parse(Path(owner.__file__).read_text(encoding="utf-8")).body if isinstance(n,ast.FunctionDef) and n.name==name+"_impl")
    assert ast.dump(ast.Module(body=prev.body,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=curr.body,type_ignores=[]),include_attributes=False)
    assert len(Path(owner.__file__).read_text(encoding="utf-8").splitlines())<=350

@pytest.mark.parametrize("name,value",[
    ("_market_token_label","bullish"),("_theme_token_label","semiconductor_leaders"),
    ("_theme_text",["semiconductor_leaders","broad_market_leaders"]),
    ("_theme_linkage_label",["semiconductor_leaders"]),
    ("_risk_mode_label","balanced"),("_strategy_constraint_label","defensive_assets"),
    ("_strategy_constraint_text",["defensive_assets","high_beta_leaders"]),
    ("_scanner_bias_label","prefer_volume_confirmation"),
    ("_scanner_bias_text",{"active_biases":["prefer_volume_confirmation"],"bias_strength":"high"}),
    ("_scanner_source_label","top_value"),("_scanner_source_text",["top_value","top_volume"]),
    ("_scanner_score_driver_label","volume_surge"),
    ("_scanner_chart_feature_label","engine_adx14"),
    ("_scanner_check_name_label","liquidity filter"),
    ("_scanner_check_status_label","PASS"),
    ("_entry_reason_label","breakout_confirmed"),
    ("_decision_chain_label","hard_stop"),("_execution_mode_label","simulation"),
    ("_entry_path_label","breakout_path"),("_entry_gate_state_label",True),
    ("_entry_gate_name_label","reclaim"),
])
def test_display_same_as_pre_split(name,value):
    _,prev=old(name)
    assert getattr(api,name)(value)==prev(value)

def test_patchable_facade_helper_path(monkeypatch):
    monkeypatch.setattr(api,"_clip",lambda value,**kwargs:"modified")
    assert api._market_token_label("unknown")=="modified"
    monkeypatch.setattr(api,"_theme_token_label",lambda item:"PATCHED")
    assert "PATCHED" in api._theme_text(["a"])
    monkeypatch.setattr(api,"_scanner_source_label",lambda item:"PATCHED")
    assert api._scanner_source_text(["top_value"])=="PATCHED"
    monkeypatch.setattr(api,"_scanner_bias_label",lambda item:"PATCHED")
    assert "PATCHED" in api._scanner_bias_text({"active_biases":["leader"]})
