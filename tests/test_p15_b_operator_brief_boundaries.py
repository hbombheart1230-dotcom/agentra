"""Closed source move and preserved historical proofs for the new Brief stage."""
import ast
import builtins
import copy
import socket
import subprocess
from pathlib import Path

import pytest

from test_p15_b_operator_brief_pure_parity import (
    BASE, ROOT, INPUT, SECTIONS, INPUT_NAMES, SECTION_NAMES, original, facade,
)

PAIRS = (
    (INPUT, 'apps/operator_ui/data_access_brief_source_truth_p15.py', INPUT_NAMES),
    (SECTIONS, 'apps/operator_ui/data_access_brief_evidence_readout_p15.py', SECTION_NAMES),
)


def text(path, sha=BASE):
    return subprocess.check_output(['git', 'show', f'{sha}:{path}'], cwd=ROOT).decode('utf-8')


@pytest.mark.parametrize('source,owner,names', PAIRS)
def test_exact_body_transfer_builder_import_scope_and_reexports(source, owner, names):
    base = ast.parse(text(source))
    moved = {n.name: n for n in base.body if isinstance(n, ast.FunctionDef) and n.name in names}
    owned = ast.parse((ROOT / owner).read_text(encoding='utf-8'))
    assert {n.name for n in owned.body if isinstance(n, ast.FunctionDef)} == set(names)
    for node in owned.body:
        if isinstance(node, ast.FunctionDef):
            assert ast.dump(node) == ast.dump(moved[node.name])
        else:
            assert isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) or (
                isinstance(node, ast.ImportFrom) and node.module == '__future__')
    current = ast.parse((ROOT / source).read_text(encoding='utf-8'))
    module_name = owner[:-3].replace('/', '.')
    imports = [n for n in current.body if isinstance(n, ast.ImportFrom) and n.module == module_name]
    assert len(imports) == 1
    assert [(a.name, a.asname) for a in imports[0].names] == [(n, n) for n in names]
    restored = copy.deepcopy(current)
    index = restored.body.index(next(n for n in restored.body if isinstance(n, ast.ImportFrom) and n.module == module_name))
    restored.body[index:index + 1] = [moved[n] for n in names]
    assert ast.dump(restored) == ast.dump(base)
    import importlib
    old_module = importlib.import_module(source[:-3].replace('/', '.'))
    new_module = importlib.import_module(module_name)
    for name in names:
        assert getattr(old_module, name) is getattr(new_module, name)


def test_core_r3_and_legacy_gate_sources_stay_identical_to_checkpoint():
    for path in ('apps/operator_ui/data_access_core.py', 'apps/operator_ui/data_access_brief_compaction.py',
                 'scripts/refactor/shared_strategist_contracts.py', 'scripts/refactor/shared_role_contracts.py'):
        assert (ROOT / path).read_text(encoding='utf-8') == text(path)


def test_authentic_historical_ui_source_proof_still_runs_on_immutable_blobs():
    from scripts.refactor import shared_strategist_contracts as s
    historical = {p: s.git_source(pin, p) for p, pin in s.NEXT_RUNTIME.items()}
    assert s._verify_five_function_stage(historical) == frozenset(s.NEXT_RUNTIME)


def test_pure_builders_have_no_io_llm_or_process_effects(monkeypatch):
    from apps.operator_ui import data_access_brief_input_projection as inputs
    from apps.operator_ui import data_access_brief_sections_projection as sections
    import apps.operator_ui.data_access_core as core
    # Build oracle before blocking Git/file reads; the actual pure calls need none.
    expected = [(original(path), builder) for path, builder in (
        (INPUT, 'build_operator_brief_input'), (SECTIONS, 'build_operator_brief_sections'))]
    dependency = facade()
    def forbidden(*args, **kwargs):
        raise AssertionError('pure projection crossed an effect boundary')
    with monkeypatch.context() as m:
        m.setattr(builtins, 'open', forbidden)
        m.setattr(Path, 'open', forbidden)
        m.setattr(socket, 'socket', forbidden)
        m.setattr(subprocess, 'Popen', forbidden)
        m.setattr(core.LLMRouter, 'from_env', staticmethod(forbidden))
        m.setattr(core, '_save_operator_brief_input_artifact', forbidden)
        m.setattr(core, '_save_operator_brief_artifact', forbidden)
        for (base, builder), module in zip(expected, (inputs, sections)):
            assert getattr(module, builder)({}, facade=dependency) == getattr(base, builder)({}, facade=dependency)


@pytest.mark.parametrize('source,owner,names', PAIRS)
def test_changed_owner_body_is_rejected_by_exact_original_ast_oracle(source, owner, names):
    old = {n.name: n for n in ast.parse(text(source)).body if isinstance(n, ast.FunctionDef)}
    current = {n.name: n for n in ast.parse((ROOT / owner).read_text(encoding='utf-8')).body if isinstance(n, ast.FunctionDef)}
    for name in names:
        assert ast.dump(current[name]) == ast.dump(old[name])
        mutant = copy.deepcopy(current[name])
        mutant.body.insert(0, ast.parse("__import__('socket')").body[0])
        assert ast.dump(mutant) != ast.dump(old[name])


def test_readonly_get_html_escape_matches_historical_helpers(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    import apps.operator_ui.data_access as compat
    import apps.operator_ui.data_access_core as core
    import apps.operator_ui.main as main
    from apps.operator_ui.main import create_app
    from test_operator_ui import _FakeRouter, _make_config
    cfg = _make_config(tmp_path)
    monkeypatch.setattr(core.LLMRouter, 'from_env', staticmethod(lambda: _FakeRouter()))
    monkeypatch.setenv('OPENROUTER_DEFAULT_MODEL', 'stepfun/step-3.5-flash:free')
    # Hold artifact/cache state fixed; compare only BASE/current projection
    # through the actual unchanged GET/template boundary.
    label = '한글 <script>evil()</script> & "'
    live = core.build_current_snapshot_section
    payload = compat.load_operator_brief_detail(cfg, '20260316_005930_buy_run-1')
    detail = core.load_run_detail(cfg, 'run-1')
    def inject(fn):
        def call(*args, **kwargs):
            return fn(*args, **kwargs) | {'summary': label}
        return call
    client = TestClient(create_app(cfg))
    from apps.operator_ui import data_access_brief_sections_projection as sections
    current_facade = facade()
    current_facade.build_current_snapshot_section = inject(live)
    current = sections.build_operator_brief_sections(detail, facade=current_facade)
    monkeypatch.setattr(main, 'load_operator_brief_detail', lambda *_: payload | {'sections': current})
    actual = client.get('/reports/trade/20260316_005930_buy_run-1/brief')
    historical_facade = facade(True)
    historical_facade.build_current_snapshot_section = inject(original(SECTIONS).build_current_snapshot_section)
    historical = original(SECTIONS).build_operator_brief_sections(detail, facade=historical_facade)
    monkeypatch.setattr(main, 'load_operator_brief_detail', lambda *_: payload | {'sections': historical})
    expected = client.get('/reports/trade/20260316_005930_buy_run-1/brief')
    assert actual.status_code == expected.status_code == 200
    assert actual.content == expected.content
    assert '<script>evil()</script>' not in actual.text
    assert '&lt;script&gt;evil()&lt;/script&gt;' in actual.text
