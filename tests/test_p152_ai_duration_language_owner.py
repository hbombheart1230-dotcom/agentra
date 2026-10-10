"""Owner37: AI Reporter duration and Korean particle display parity, pinned before source."""
import ast
import subprocess
from pathlib import Path

import pytest

import libs.reporting.trade_report_ai as api
from libs.reporting.trade_report.ai_facade_parts import duration_language as owner


BASE = "ef22bec761d7f2b01762cb17e3c6523b9df8040c"
FILE = "libs/reporting/trade_report_ai.py"
NAMES = ("_humanize_duration_text", "_holding_duration_label", "_korean_predicate", "_korean_euro_ro")


def original(name):
    source = subprocess.check_output(["git", "show", f"{BASE}:{FILE}"], text=True, encoding="utf-8-sig")
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = vars(api).copy()
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<pre-owner37>", "exec"), namespace)
    return node, namespace[name]


@pytest.mark.parametrize("name", NAMES)
def test_body_ast_unchanged(name):
    original_node, _ = original(name)
    current_node = next(
        n for n in ast.parse(Path(owner.__file__).read_text(encoding="utf-8")).body
        if isinstance(n, ast.FunctionDef) and n.name == name + "_impl"
    )
    assert ast.dump(ast.Module(body=original_node.body, type_ignores=[]), include_attributes=False) == ast.dump(
        ast.Module(body=current_node.body, type_ignores=[]), include_attributes=False
    )
    assert len(Path(owner.__file__).read_text(encoding="utf-8").splitlines()) <= 350


@pytest.mark.parametrize("name,args,kwargs", [
    ("_humanize_duration_text", ("01:02:03",), {}),
    ("_humanize_duration_text", ("12:34",), {}),
    ("_humanize_duration_text", ("1.5h",), {}),
    ("_humanize_duration_text", ("1.5m",), {}),
    ("_humanize_duration_text", ("no duration",), {}),
    ("_humanize_duration_text", ("",), {"fallback_seconds": 73}),
    ("_humanize_duration_text", ("",), {"fallback_seconds": "n/a"}),
    ("_holding_duration_label", ("00:01:30",), {}),
    ("_holding_duration_label", ("",), {}),
    ("_korean_predicate", ("정책",), {}),
    ("_korean_predicate", ("가",), {}),
    ("_korean_predicate", ("",), {}),
    ("_korean_predicate", ("선택",), {"noun_suffix":"으로"}),
    ("_korean_euro_ro", ("서울",), {}),
    ("_korean_euro_ro", ("부산",), {}),
    ("_korean_euro_ro", ("가",), {}),
    ("_korean_euro_ro", ("",), {}),
])
def test_output_equals_pinned_pre_owner37(name, args, kwargs):
    _, old = original(name)
    assert getattr(api, name)(*args, **kwargs) == old(*args, **kwargs)


def test_original_facade_patchable_dependencies(monkeypatch):
    monkeypatch.setattr(api, "_clip", lambda text, **kwargs: "02:10")
    assert api._humanize_duration_text("ignored") == "2분 10초"
    monkeypatch.setattr(api, "_safe_fullmatch", lambda pattern, text: None)
    assert api._humanize_duration_text("ignored") == "02:10"
    monkeypatch.setattr(api, "_humanize_duration_text", lambda text: "patched")
    assert api._holding_duration_label("anything") == "보유 시간은 patched였습니다."
