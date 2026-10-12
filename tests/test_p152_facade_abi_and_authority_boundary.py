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

# Stage-scoped scope guard (Fast Track). This historical gate is PINNED to the Wave A end commit so a
# legitimate later wave (B: graphs/nodes strategist/scanner/monitor, ...) never makes it fail; later waves
# carry their own scope + trading-authority gates (see tests/test_p154_wave_b_scope_and_authority_boundary.py).
WAVE_A_END = "318015a02b8378b0dbf7b0b24ec18c2786688d18"
WAVE_A_ALLOWED_PREFIXES = (
    "libs/reporting/", "tests/", "docs/", "scripts/refactor/",
    "apps/operator_ui/",          # P1.5.3 Operator UI/Brief first pass (Wave A / A2)
)
ALWAYS_FORBIDDEN_PREFIXES = (
    "apps/api/", "graphs/", "conftest.py", "Dockerfile", "docker-compose", "libs/execution/", "libs/broker/",
    "libs/supervisor/", "libs/executor/", "libs/runtime/", "libs/ai/", "libs/core/", "libs/agents/",
)


def _changed(base, head):
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", base, head]).decode().split(chr(0))
    return [p for p in out if p]


def test_wave_a_changes_stay_within_reporting_and_operator_ui_without_trading_authority_files():
    files = _changed(BEFORE, WAVE_A_END)
    assert files, "Expected a P1.5.2/Wave A diff"
    # Repository agent-entrypoint instructions are an explicit, bounded documentation-only exception.
    allowed_root_agent_docs = {"AGENTS.md", "CLAUDE.md"}
    for filename in files:
        if filename in allowed_root_agent_docs:
            continue
        if filename.startswith(".github/workflows/"):
            assert filename == ".github/workflows/p152-r2c-residual-regression.yml", filename
            continue
        assert not filename.startswith(ALWAYS_FORBIDDEN_PREFIXES), f"Forbidden path mutated: {filename}"
        assert filename.startswith(WAVE_A_ALLOWED_PREFIXES), f"Unexpected path mutated in Wave A: {filename}"
    assert any(f.startswith("apps/operator_ui/") for f in files), "Wave A must contain the Operator UI first pass"
    assert not any(f.startswith("apps/api/") or f == "conftest.py" or f.startswith("graphs/") for f in files)
