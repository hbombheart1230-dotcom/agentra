"""AST, text parity and dynamic seam tests for Markdown-clean output helpers."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_report_markdown_clean as legacy
from libs.reporting.trade_report.markdown_clean_parts import summary_language as owner

PINNED="007e7c2ff757181048bac6d467ff76ec9f4ddce1"
FILE="libs/reporting/trade_report_markdown_clean.py"
NAMES=("_summary_problem_label","_summary_root_cause_label","_summary_fact_text",
       "_summary_eval_sentence","_section","_strip_trailing_blanks",
       "_is_post_entry_gate_text","_normalize_evaluation_hold_duration")


def original(name):
    text=subprocess.check_output(["git","show",f"{PINNED}:{FILE}"],
                                 text=True,encoding="utf-8-sig")
    node=next(n for n in ast.parse(text).body
              if isinstance(n,ast.FunctionDef) and n.name==name)
    scope=vars(legacy).copy()
    exec(compile(ast.Module(body=[node],type_ignores=[]),"<pre-owner30>","exec"),scope)
    return node,scope[name]


@pytest.mark.parametrize("name",NAMES)
def test_body_ast_matches_original(name):
    before,_=original(name)
    after=next(n for n in ast.parse(Path(owner.__file__).read_text(encoding="utf-8")).body
               if isinstance(n,ast.FunctionDef) and n.name==name+"_impl")
    assert ast.dump(ast.Module(body=before.body,type_ignores=[]),include_attributes=False)==\
           ast.dump(ast.Module(body=after.body,type_ignores=[]),include_attributes=False)
    assert len(Path(owner.__file__).read_text(encoding="utf-8").splitlines())<=350


@pytest.mark.parametrize("name,args",[
    ("_summary_eval_sentence",("결정론적 진단 확인",)),
    ("_summary_problem_label",("monitor_only_path_ratio_high",)),
    ("_summary_root_cause_label",("entry_was_tightened_by_breakout_buffer",)),
    ("_summary_fact_text",("내용  입니다..",)),
    ("_section",("요약",["설명"])),
    ("_strip_trailing_blanks",(["a","","","b"],)),
    ("_is_post_entry_gate_text",("post-entry check",)),
    ("_normalize_evaluation_hold_duration",("5분 동안 보유",{})),
])
def test_pinned_report_only_text_exact(name,args):
    _,prior=original(name)
    assert getattr(legacy,name)(*args)==prior(*args)


def test_public_facade_monkeypatch_bindings(monkeypatch):
    monkeypatch.setattr(legacy,"_summary_eval_sentence",lambda value:"PATCHED")
    assert legacy._summary_problem_label("other")=="PATCHED"
    monkeypatch.setattr(legacy,"_translate_text",lambda value:"post-entry")
    assert legacy._is_post_entry_gate_text("anything") is True
