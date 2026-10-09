"""AI Reporter small text Owner pinned source and public monkeypatch parity."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_report_ai as facade
from libs.reporting.trade_report.ai_facade_parts import text_helpers as owner
PRE="9242d6e30c1c9917bf434bed99e7cca373876678"
SRC="libs/reporting/trade_report_ai.py"
NAMES=("_is_low_information_bullet","_count_hangul","_count_latin",
       "_first_nonempty_text","_has_evidence_payload","_as_action")
def before(name):
    s=subprocess.check_output(["git","show",f"{PRE}:{SRC}"],text=True,encoding="utf-8-sig")
    fn=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==name)
    env=vars(facade).copy()
    exec(compile(ast.Module(body=[fn],type_ignores=[]),"<old-ai-report>","exec"),env)
    return fn,env[name]
@pytest.mark.parametrize("name",NAMES)
def test_ast_body_and_size(name):
    old,_=before(name)
    new=next(x for x in ast.parse(Path(owner.__file__).read_text(encoding="utf-8")).body
             if isinstance(x,ast.FunctionDef) and x.name==name+"_impl")
    assert ast.dump(ast.Module(body=old.body,type_ignores=[]),include_attributes=False)==\
           ast.dump(ast.Module(body=new.body,type_ignores=[]),include_attributes=False)
    assert len(Path(owner.__file__).read_text(encoding="utf-8").splitlines())<=350
@pytest.mark.parametrize("name,args",[
("_is_low_information_bullet",("hold",)),("_count_hangul",("삼성 AI",)),
("_count_latin",("NVIDIA HBM",)),("_first_nonempty_text",("","report")),
("_has_evidence_payload",({"x":1},)),("_as_action",("NOOP",))])
def test_before_after_output_equal(name,args):
    _,old=before(name)
    assert getattr(facade,name)(*args)==old(*args)
def test_public_monkeypatch_dependencies(monkeypatch):
    monkeypatch.setattr(facade,"_safe_fullmatch",lambda *a,**kw:True)
    assert facade._is_low_information_bullet("xyz") is True
    log=[]
    monkeypatch.setattr(facade,"_clip",lambda x,**kw:(log.append(x) or str(x)))
    assert facade._as_action("noop")=="WAIT"
    assert log
