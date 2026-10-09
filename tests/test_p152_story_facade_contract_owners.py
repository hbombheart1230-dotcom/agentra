"""Story report contract display helpers maintain prior source and patchable seams."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_story_pipeline as api
from libs.reporting.trade_story_facade_parts import story_contracts as owner

BASE = "df57b57acf6380174189ed4b69b3f9f92c638d02"
PATH = "libs/reporting/trade_story_pipeline.py"
NAMES = ("slug", "feature_coverage", "normalized_feature_coverage",
         "confidence_label", "execution_mode_label", "classify_story_type",
         "build_story_id", "build_story_contract")


def former(name):
    src=subprocess.check_output(["git","show",f"{BASE}:{PATH}"],text=True,encoding="utf-8-sig")
    node=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name==name)
    ns=vars(api).copy()
    exec(compile(ast.Module(body=[node], type_ignores=[]),
                 "<pre-split-story-contract>", "exec"),ns)
    return node, ns[name]


@pytest.mark.parametrize("name", NAMES)
def test_display_contract_owner_ast_preserved(name):
    original,_=former(name)
    new=next(n for n in ast.parse(Path(owner.__file__).read_text(encoding="utf-8")).body
             if isinstance(n,ast.FunctionDef) and n.name==name+"_impl")
    assert ast.dump(ast.Module(body=original.body,type_ignores=[]),include_attributes=False)==\
           ast.dump(ast.Module(body=new.body,type_ignores=[]),include_attributes=False)
    assert len(Path(owner.__file__).read_text(encoding="utf-8").splitlines())<=350


@pytest.mark.parametrize("fn,examples", [
    ("slug", [(("",),{}), (("005930 KOSPI",),{"max_len":48})]),
    ("feature_coverage", [(({},),{}), (({"feature_snapshot":{"engine_ma20_gap":0.1}},),{})]),
    ("normalized_feature_coverage", [(({},{}),{}), (({"feature_coverage":{"present":2,"total":13}},{}),{})]),
    ("confidence_label", [((0.85,),{}), ((None,),{})]),
    ("execution_mode_label", [(({},),{}), (({"broker_env":"mock"},),{})]),
    ("classify_story_type", [(({},{}),{}), (({"action":"BUY"},{"execution_attempted":True,"execution_ok":True}),{})]),
    ("build_story_id", [(("2026-10-09",{"run_id":"r3","symbol":"005930","action":"BUY"}),{})]),
    ("build_story_contract", [(({},),{}), (({"execution":{"action":"SELL"},"executor":{"broker_env":"mock"}},),{})]),
])
def test_contract_result_matches_pre_split(fn,examples):
    _,before=former(fn)
    for args,kwargs in examples:
        assert getattr(api,fn)(*args,**kwargs)==before(*args,**kwargs)


def test_dependency_injection_uses_public_monkeypatch(monkeypatch):
    monkeypatch.setattr(api,"slug",lambda *a,**kw:"patched")
    assert api.build_story_id("2026-10-09",{})=="patched"
    monkeypatch.setattr(api,"classify_story_type",lambda *a,**kw:"simulation")
    assert api.build_story_contract({})["story_type"]=="simulation"
    monkeypatch.setattr(api,"safe_float",lambda *a,**kw:0.9)
    assert api.confidence_label(0)=="high"
