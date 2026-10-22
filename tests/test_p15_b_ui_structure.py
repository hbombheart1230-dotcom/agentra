"""Operator UI folder restructuring: pinned runtime parity and closed boundaries."""
import ast
import copy
import inspect
import json
import subprocess
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
import apps.operator_ui.data_access_core as core
from scripts.refactor import shared_strategist_contracts as S

BASE = "51bb7130b2ba627be50800fa89c6108dd1a5018c"


def original(name):
    source = S.git_source(BASE, S.UI_CORE)
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {}
    exec(compile("from __future__ import annotations\n" + ast.get_source_segment(source, node), "<real51bbBASE>", "exec"), ns)
    fn = ns[name]
    result = types.FunctionType(fn.__code__, core.__dict__, name, fn.__defaults__, fn.__closure__)
    result.__kwdefaults__ = fn.__kwdefaults__
    result.__annotations__ = dict(fn.__annotations__)
    return result


def outcome(fn, *args):
    try:
        return ("value", json.dumps(fn(*args), ensure_ascii=False, separators=(",", ":")))
    except Exception as exc:
        return ("exception", type(exc).__name__, str(exc))


@pytest.mark.parametrize("router_name", ["_FakeRouter", "_RepairRouter", "unavailable", "error", "empty"])
def test_whole_brief_loader_real_base_output_calls_and_artifact_boundary(router_name, monkeypatch):
    import test_operator_ui as fixtures
    detail = {"run_id": "unicode-관측", "started_at": "2026-03-16T12:00:00+09:00", "trade_report": {}}
    def run(fn):
        trace = []
        router = fixtures._FakeRouter() if router_name not in {"_RepairRouter"} else fixtures._RepairRouter()
        if router_name == "unavailable": router.client = None
        real_chat = router.chat
        def chat(*args, **kwargs):
            trace.append(("chat", copy.deepcopy(args), copy.deepcopy(kwargs)))
            if router_name == "error": raise ValueError("offline diagnostic")
            if router_name == "empty": return ""
            return real_chat(*args, **kwargs)
        router.chat = chat
        with monkeypatch.context() as m:
            m.setattr(core.LLMRouter, "from_env", lambda: router)
            m.setattr(core.time, "perf_counter", lambda: 42.0)
            m.setattr(core, "_save_operator_brief_input_artifact", lambda *args: trace.append(("save_input", copy.deepcopy(args))))
            def artifact(**kwargs):
                trace.append(("artifact", copy.deepcopy(kwargs)))
                return kwargs
            m.setattr(core, "build_llm_response_artifact", artifact)
            return outcome(fn, copy.deepcopy(detail)), trace
    assert inspect.signature(core._load_operator_brief) == inspect.signature(original("_load_operator_brief"))
    expected = run(original("_load_operator_brief"))
    actual = run(core._load_operator_brief)
    assert actual == expected
    assert actual[0][0] == "value"
    assert actual[1][-1][0] == "artifact"


@pytest.mark.parametrize("path", [S.UI_CORE, S.UI_STRUCTURE_RESPONSE, S.UI_STRUCTURE_RUN])
def test_structure_rejects_body_argument_import_or_authority_mutations(path):
    assert S.verify_ui_structure()
    text = (S.ROOT / path).read_text(encoding="utf-8")
    for changed in (text + "\n__import__('socket')\n", text + "\nSTATE = {'orders': True}\n", None):
        with pytest.raises(AssertionError):
            S.verify_ui_structure({path: changed})
    if path == S.UI_CORE:
        assert "_project_run_inputs(all_rows, evidence_rows" in text
        with pytest.raises(AssertionError, match="core body/import/ABI"):
            S.verify_ui_structure({path: text.replace("_project_run_inputs(all_rows, evidence_rows", "_project_run_inputs(evidence_rows, all_rows")})


@pytest.mark.parametrize("path", ["libs/broker/new.py", "apps/operator_ui/read_models/unapproved.py", ".github/workflows/new.yml", "tests/fixtures/modified.json"])
def test_structure_has_no_prefix_grant(path):
    assert S.verify_ui_structure()
    with pytest.raises(AssertionError, match="unexpected/missing path"):
        S.verify_ui_structure({path: "WRITE = True"})


def test_core_unmoved_definitions_and_original_declarations_remain():
    old = ast.parse(S.git_source(BASE, S.UI_CORE))
    now = ast.parse((S.ROOT / S.UI_CORE).read_text(encoding="utf-8"))
    olddefs = {n.name:n for n in old.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    newdefs = {n.name:n for n in now.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    assert olddefs.keys() == newdefs.keys()
    for name in olddefs:
        if name not in {"_load_operator_brief", "load_run_detail"}:
            assert ast.dump(olddefs[name]) == ast.dump(newdefs[name]), name
    assert S.verify_b_sources() == S.B_RUNTIME
    assert len(S.verify_b_composed()) == 29  # Historical named view, after NEW actual-source proof.
