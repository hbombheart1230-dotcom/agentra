"""Story façade report-only human judgment owners, pre-split source parity."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_story_pipeline as api
from libs.reporting.trade_story_facade_parts import human_judgments as owner

BEFORE = "0da31c9e6bbcf1754e1b9b209878dca1c6eda9e3"
PATH = "libs/reporting/trade_story_pipeline.py"
NAMES = ("build_guard_reason_human", "build_reporter_status_human",
         "build_operator_conclusion_human")


def original(name):
    src = subprocess.check_output(["git", "show", f"{BEFORE}:{PATH}"],
                                  text=True, encoding="utf-8-sig")
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)
                and n.name == name)
    env = vars(api).copy()
    exec(compile(ast.Module(body=[node], type_ignores=[]),
                 "<p152-prior-story-human>", "exec"), env)
    return node, env[name]


@pytest.mark.parametrize("name", NAMES)
def test_old_body_ast_is_identical(name):
    prev, _ = original(name)
    impl = next(n for n in ast.parse(Path(owner.__file__).read_text(encoding="utf-8")).body
                if isinstance(n, ast.FunctionDef) and n.name == name+"_impl")
    assert ast.dump(ast.Module(body=prev.body, type_ignores=[]), include_attributes=False) == \
           ast.dump(ast.Module(body=impl.body, type_ignores=[]), include_attributes=False)
    assert len(Path(owner.__file__).read_text(encoding="utf-8").splitlines()) <= 350


@pytest.mark.parametrize("supervisor", [{}, {"supervisor_allow": True, "verdict": "approve",
                                             "symbol": "005930", "action": "BUY"},
                                     {"supervisor_allow": False, "supervisor_reason": "risk_cap"}])
def test_guard_human_pre_split_equal(supervisor):
    _, prev = original("build_guard_reason_human")
    assert api.build_guard_reason_human(supervisor) == prev(supervisor)


@pytest.mark.parametrize("r,day", [
    ({}, {}),
    ({"reporter_analysis_found": True, "reporter_analysis_summary": "PASS"}, {"ai_run_grade": "A"}),
    ({"reporter_analysis_day_file_found": True}, {"ai_summary": "pending"}),
])
def test_reporter_status_pre_split_equal(r, day):
    _, prev = original("build_reporter_status_human")
    assert api.build_reporter_status_human(r, day) == prev(r, day)


@pytest.mark.parametrize("action", ["BUY", "SELL", "HOLD", "WAIT"])
def test_operator_conclusion_pre_split_equal(action):
    _, prev = original("build_operator_conclusion_human")
    args=dict(execution={"action":action},scanner_reason_human={"summary":"scanner"},
              filters_human={"checks":[{"status":"FAIL"}]},
              monitor_reason_human={"summary":"monitor"},
              execution_outcome_human={"summary":"outcome"},
              reporter_status_human={"status":"pending"})
    assert api.build_operator_conclusion_human(**args) == prev(**args)


def test_reporter_normalizer_is_patched_at_call_time(monkeypatch):
    monkeypatch.setattr(api, "normalize_reporter_status_human",
                        lambda d: dict(d, patched=True))
    assert api.build_reporter_status_human({}, {})["patched"] is True
