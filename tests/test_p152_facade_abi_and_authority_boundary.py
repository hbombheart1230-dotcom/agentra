"""P1.5.2 three public Reporting facade ABI and non-authority diff guard."""
import ast
import importlib
import subprocess
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
PIN="52508ade9d0d246fa4e848525fe62f2fe067acb7"
BEFORE="2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c"
FACADES=(
    "libs/reporting/trade_report_ai.py",
    "libs/reporting/trade_report_markdown_clean.py",
    "libs/reporting/trade_story_pipeline.py",
)

def source_before(path):
    return subprocess.check_output(["git","show",f"{PIN}:{path}"],text=True,encoding="utf-8-sig")

def declaration_map(code):
    nodes=ast.parse(code).body
    return {n.name:n for n in nodes if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}

@pytest.mark.parametrize("path",FACADES)
def test_public_signatures_and_names_unchanged(path):
    before=declaration_map(source_before(path))
    after=declaration_map((ROOT/path).read_text(encoding="utf-8-sig"))
    assert before.keys()==after.keys(),path
    for name,original in before.items():
        current=after[name]
        assert type(original)==type(current),(path,name,"declaration kind")
        if isinstance(original,(ast.FunctionDef,ast.AsyncFunctionDef)):
            for key in ("args","returns","decorator_list"):
                left=getattr(original,key)
                right=getattr(current,key)
                if isinstance(left,ast.AST) and isinstance(right,ast.AST):
                    equal=ast.dump(left,include_attributes=False)==ast.dump(right,include_attributes=False)
                elif isinstance(left,list) and isinstance(right,list):
                    equal=[ast.dump(v,include_attributes=False) for v in left]==[ast.dump(v,include_attributes=False) for v in right]
                else:
                    equal=left==right
                assert equal,(path,name,key)
    module=importlib.import_module(path[:-3].replace("/","."))
    assert all(callable(getattr(module,name,None)) for name in before),(path,"public callable inaccessible")

def test_changes_remain_reporting_only_with_no_trading_authority_files():
    changed=subprocess.check_output(["git","diff","--name-only","-z",BEFORE,"HEAD"]).decode().split("\0")
    files=[p for p in changed if p]
    assert files,"Expected a P1.5.2 reporting diff"
    allowed=("libs/reporting/","tests/","docs/","scripts/refactor/")
    for filename in files:
        if filename.startswith(".github/workflows/"):
            assert filename==".github/workflows/p152-r2c-residual-regression.yml",filename
        else:
            assert filename.startswith(allowed),f"Unexpected non-Reporting path mutated: {filename}"
