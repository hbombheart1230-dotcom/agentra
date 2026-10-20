"""Current-stage exact admission; historical shape gates retain their own oracle.

No golden is regenerated. Pins are the independently reviewed source SHAs.
"""
import ast
import copy
import inspect
import json
import subprocess
import sys
import types

import pytest

from scripts.refactor import shared_strategist_contracts as S


@pytest.fixture(scope="module", autouse=True)
def exact_current_stage_is_green_before_mutation_tests():
    S.verify_next_stage()
    S.verify_b_scope()


def test_current_source_restores_only_the_five_approved_definitions():
    assert S.verify_next_stage() == frozenset(S.NEXT_RUNTIME)
    S.verify_next_scope()
    assert S.historical_source(S.NODE) == S.git_source(S.HISTORICAL_STAGE, S.NODE)
    # Historical size/import rules remain on the old stage; no new global cap.
    assert len(S.historical_source(S.UI_SECTIONS).splitlines()) <= 350
    assert len((S.ROOT / S.UI_SECTIONS).read_text(encoding="utf-8").splitlines()) == 387


@pytest.mark.parametrize("path,name", [(p, n) for p, names in S.NEXT_MOVED.items() for n in names])
@pytest.mark.parametrize("kind", ["argument", "facade", "default"])
def test_each_new_wrapper_rejects_argument_facade_and_abi_mutations(path, name, kind):
    tree = ast.parse((S.ROOT / path).read_text(encoding="utf-8"))
    fn = S.functions(tree)[name]
    if kind == "argument":
        fn.body[0].value.args[0] = ast.Constant(value=None)
    elif kind == "facade":
        fn.body[0].value.keywords[0].value = ast.Constant(value=None)
    else:
        fn.args.defaults.append(ast.Constant(value=None))
    with pytest.raises(AssertionError, match="new-stage source"):
        S.verify_next_stage({path: ast.unparse(tree)})


@pytest.mark.parametrize("path", sorted(S.NEXT_RUNTIME))
@pytest.mark.parametrize("addition", ["import os", "__import__('os')", "State = {'authority': True}",
                                      "facade.LLMRouter.from_env()", "BROKER_PERMISSION = True"])
def test_no_import_time_effect_dynamic_import_state_llm_or_broker_addition(path, addition):
    source = (S.ROOT / path).read_text(encoding="utf-8")
    with pytest.raises(AssertionError, match="new-stage source"):
        S.verify_next_stage({path: source + "\n" + addition + "\n"})


@pytest.mark.parametrize("path", [S.NODE, S.UI_CORE])
def test_unmoved_function_change_cannot_hide_behind_historical_projection(path):
    tree = ast.parse((S.ROOT / path).read_text(encoding="utf-8"))
    fn = next(n for n in S.functions(tree).values() if n.name not in S.NEXT_MOVED[path])
    fn.body.insert(0, ast.parse("raise RuntimeError('unauthorized')").body[0])
    with pytest.raises(AssertionError):
        S.verify_next_stage({path: ast.unparse(tree)})


@pytest.mark.parametrize("path", ["libs/broker/rogue.py", "libs/supervisor/rogue.py", "libs/executor/rogue.py",
                                  "graphs/nodes/decide_trade.py", "tests/fixtures/p1_5_t4d_commander_ui/golden.json",
                                  "tests/test_uef9_formal_authority.py", "apps/operator_ui/main.py"])
def test_new_stage_has_no_prefix_or_authority_allowlist(path):
    for changed, untracked in (([path], []), ([], [path])):
        with pytest.raises(AssertionError):
            S.verify_next_scope(changed, untracked)


def _original_brief(name, core):
    tree = ast.parse(S.git_source(S.NEXT_BASE, S.UI_CORE))
    node = S.functions(tree)[name]
    ns = {}
    flags = __import__("__future__").annotations.compiler_flag
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<accepted brief BASE>", "exec", flags=flags), ns)
    original = types.FunctionType(ns[name].__code__, vars(core))
    original.__annotations__ = ns[name].__annotations__
    return original


@pytest.mark.parametrize("name", sorted(S.NEXT_MOVED[S.UI_CORE]))
def test_brief_ordered_json_markdown_exceptions_and_readonly_effects(name, tmp_path, monkeypatch):
    import apps.operator_ui.data_access_core as core
    import apps.operator_ui.data_access as compat
    from test_operator_ui import _make_config, _FakeRouter

    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(lambda: _FakeRouter()))
    detail = core.load_run_detail(_make_config(tmp_path), "run-1")  # existing synthetic UI fixture, no production data
    original, current = _original_brief(name, core), getattr(core, name)
    assert inspect.signature(original) == inspect.signature(current)
    assert getattr(compat, name) is current

    def forbidden(*args, **kwargs):
        raise AssertionError("pure brief projection attempted LLM/persistence")

    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(forbidden))
    monkeypatch.setattr(core, "_save_operator_brief_input_artifact", forbidden)
    monkeypatch.setattr(core, "_save_operator_brief_artifact", forbidden)
    for sample in (detail, {}, {"monitor": None}, {"scanner": {"decision_trace": []}}, None, []):
        before = copy.deepcopy(sample)
        def outcome(fn):
            try:
                value = fn(sample)
                return ("ok", json.dumps(value, ensure_ascii=False).encode("utf-8"), value)
            except Exception as exc:
                return ("exception", type(exc), str(exc))
        expected, actual = outcome(original), outcome(current)
        assert expected == actual
        assert sample == before
        if actual[0] == "ok" and name == "_build_operator_brief_sections":
            assert core._render_operator_brief_markdown({"status": "ok", "sections": expected[2]}).encode() == core._render_operator_brief_markdown({"status": "ok", "sections": actual[2]}).encode()

    # Rebind a helper during canonical extraction, proving lookup after entry.
    canonical = core._build_canonical_trade_brief_input
    def rebind(trade_report):
        monkeypatch.setattr(core, "_safe_int", lambda *args, **kwargs: 73)
        return canonical(trade_report)
    monkeypatch.setattr(core, "_build_canonical_trade_brief_input", rebind)
    assert original(detail) == current(detail)


def test_exact_admission_rejects_mutations_under_optimized_python():
    code = r"""from scripts.refactor import shared_strategist_contracts as s
p = s.UI_CORE
try:
    s.verify_next_stage({p: (s.ROOT / p).read_text(encoding='utf-8') + '\n__import__("os")\n'})
except AssertionError:
    pass
else:
    raise SystemExit('dynamic import accepted')
"""
    subprocess.run([sys.executable, "-O", "-c", code], cwd=S.ROOT, check=True)


@pytest.mark.parametrize("path", [S.NODE, S.UI_CORE, S.UI_INPUT, S.UI_SECTIONS])
def test_historical_view_never_hides_a_modified_current_blob(path, monkeypatch):
    from pathlib import Path
    read = Path.read_text
    def changed(p, *args, **kwargs):
        source = read(p, *args, **kwargs)
        return source + "\n__import__('os')\n" if p == S.ROOT / path else source
    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(AssertionError, match="new-stage source"):
        S.historical_source(path)
