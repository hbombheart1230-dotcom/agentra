"""Differential tests against immutable e328 source, not generated golden data."""
import copy
import functools
import inspect
import json
import subprocess
import types
from pathlib import Path

import pytest

import apps.operator_ui.data_access_core as core
from apps.operator_ui import data_access_brief_input_projection as inputs
from apps.operator_ui import data_access_brief_sections_projection as sections
from test_operator_ui import _FakeRouter, _make_config

BASE = 'e328d7801763a65e6c2c50c90edd693ff685ef95'
ROOT = Path(__file__).resolve().parents[1]
INPUT = 'apps/operator_ui/data_access_brief_input_projection.py'
SECTIONS = 'apps/operator_ui/data_access_brief_sections_projection.py'
INPUT_NAMES = (
    'brief_input_candidate_hints_market_headlines',
    'brief_input_scanner_selection_trace',
    'brief_input_canonical_monitor_snapshot_stop_policy_t',
    'brief_input_commander_applied_policy_monitor_applied',
)
SECTION_NAMES = (
    'build_current_snapshot_section', 'build_strategist_evidence_section',
    'build_monitor_guard_snapshot_section', 'build_entry_timing_section',
    'build_position_monitor_reasoning_section', 'build_exit_plan_section',
    'build_ai_trade_report_section',
)
ALL_NAMES = INPUT_NAMES + SECTION_NAMES


@functools.lru_cache(maxsize=None)
def original(path):
    source = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
    module = types.ModuleType('immutable_brief_' + Path(path).stem)
    exec(compile(source, f'<{BASE}:{path}>', 'exec'), vars(module))
    return module


def facade(historical=False, calls=None, captured=None):
    obj = types.SimpleNamespace(**vars(core))
    for path, current, names in ((INPUT, inputs, INPUT_NAMES), (SECTIONS, sections, SECTION_NAMES)):
        for name in names:
            setattr(obj, name, getattr(original(path) if historical else current, name))
    if calls is not None or captured is not None:
        for name, fn in list(vars(obj).items()):
            if not inspect.isfunction(fn):
                continue
            def record(*args, _name=name, _fn=fn, **kwargs):
                if calls is not None:
                    calls.append(_name)
                if captured is not None and _name in ALL_NAMES:
                    captured[_name] = (copy.deepcopy(args), copy.deepcopy({k: v for k, v in kwargs.items() if k != 'facade'}))
                return _fn(*args, **kwargs)
            setattr(obj, name, record)
    return obj


@pytest.fixture
def detail(tmp_path, monkeypatch):
    monkeypatch.setattr(core.LLMRouter, 'from_env', staticmethod(lambda: _FakeRouter()))
    value = core.load_run_detail(_make_config(tmp_path), 'run-1')
    # Existing synthetic fixture, enriched with observable zero/False/Unicode data.
    value['run_id'] = '한글-0-<script>alert("x")</script>'
    value['monitor'].setdefault('summary', {}).update({'current_price': 0, 'entry_evaluated': False})
    return value


def outcome(fn, value, dependency):
    try:
        result = fn(value, facade=dependency)
        return ('ok', json.dumps(result, ensure_ascii=False).encode('utf-8'), result)
    except Exception as exc:
        return ('error', type(exc), str(exc))


@pytest.mark.parametrize('path,module,builder', [(INPUT, inputs, 'build_operator_brief_input'), (SECTIONS, sections, 'build_operator_brief_sections')])
@pytest.mark.parametrize('kind', ['fixture', 'empty', 'null-monitor', 'invalid-scanner', 'none', 'list'])
def test_builder_bytes_errors_input_and_call_order_match_base(path, module, builder, kind, detail):
    sample = {'fixture': detail, 'empty': {}, 'null-monitor': {'monitor': None},
              'invalid-scanner': {'scanner': {'decision_trace': []}}, 'none': None, 'list': []}[kind]
    before = copy.deepcopy(sample)
    old_calls, new_calls = [], []
    expected = outcome(getattr(original(path), builder), copy.deepcopy(sample), facade(True, old_calls))
    actual = outcome(getattr(module, builder), sample, facade(False, new_calls))
    assert actual == expected
    assert new_calls == old_calls
    assert sample == before
    if actual[0] == 'ok' and module is sections:
        render = core._render_operator_brief_markdown
        assert render({'status': 'ok', 'sections': actual[2]}).encode('utf-8') == render({'status': 'ok', 'sections': expected[2]}).encode('utf-8')


@pytest.mark.parametrize('name', ALL_NAMES)
def test_each_public_helper_signature_bytes_and_reference_semantics(name, detail):
    captured = {}
    f = facade(captured=captured)
    # Force scanner fallback construction to exercise the second source helper.
    detail['scanner']['decision_trace'] = {}
    inputs.build_operator_brief_input(detail, facade=f)
    sections.build_operator_brief_sections(detail, facade=f)
    assert name in captured
    args, kwargs = captured[name]
    current = getattr(inputs if name in INPUT_NAMES else sections, name)
    previous = getattr(original(INPUT if name in INPUT_NAMES else SECTIONS), name)
    assert inspect.signature(current) == inspect.signature(previous)
    if 'facade' in inspect.signature(current).parameters:
        kwargs['facade'] = facade()
    before = copy.deepcopy({k: v for k, v in kwargs.items() if k != 'facade'})
    expected = previous(*args, **kwargs)
    actual = current(*args, **kwargs)
    assert json.dumps(actual, ensure_ascii=False).encode() == json.dumps(expected, ensure_ascii=False).encode()
    assert {k: v for k, v in kwargs.items() if k != 'facade'} == before
    # Compare aliases into the actual argument graph, not only equal values.
    if isinstance(actual, dict):
        original_objects = list(args) + [v for k, v in kwargs.items() if k != 'facade']
        for key in actual:
            for obj in original_objects:
                assert (actual[key] is obj) == (expected[key] is obj)


@pytest.mark.parametrize('value', [None, False, 0, '', '한글 <b>& "', 'BUY', 'WAIT'])
def test_zero_null_false_and_unicode_fallback_is_not_reinterpreted(value):
    previous = original(SECTIONS).build_current_snapshot_section
    kwargs = dict.fromkeys(inspect.signature(previous).parameters, value)
    assert sections.build_current_snapshot_section(**kwargs) == previous(**kwargs)
    expected = original(INPUT).brief_input_commander_applied_policy_monitor_applied
    args = ({'applied_policy': {'limit': value}}, {}, {}, {})
    assert inputs.brief_input_commander_applied_policy_monitor_applied(*args, facade=facade()) == expected(*args, facade=facade())


def test_mid_call_dependency_rebinding_and_exception_parity():
    def run(fn, explode=False):
        f = facade()
        calls = []
        def first(rows, **kwargs):
            calls.append('first')
            def second(rows, **kwargs):
                calls.append('rebound')
                if explode:
                    raise ValueError('정확한 예외 <&>')
                return ['둘째']
            f._brief_collect_top_headlines = second
            return ['첫째']
        f._brief_collect_top_headlines = first
        try:
            result = fn({}, {}, {}, {}, {}, {}, {}, {}, facade=f)
            return result, calls
        except Exception as exc:
            return type(exc), str(exc), calls
    old = original(INPUT).brief_input_candidate_hints_market_headlines
    new = inputs.brief_input_candidate_hints_market_headlines
    assert run(new) == run(old)
    assert run(new)[1] == ['first', 'rebound']
    assert run(new, True) == run(old, True)


@pytest.mark.parametrize('value', [None, False, 0, '', '한글 <&>'])
def test_monitor_trace_precedence_and_policy_reference_identity(value):
    artifact = {'metric': 1, 'selected': 1}
    summary = {'metric': 2, 'selected': value}
    trace = {'metric': 3, 'flag': False}
    canonical = {'monitor_stop_policy_trace': {'canonical': 4},
                 'monitor_snapshot': {'monitor_stop_policy_trace': {'snapshot': 5}}}
    before = copy.deepcopy((artifact, summary, trace, canonical))
    def run(fn):
        f = facade()
        observed = []
        def capture(merged):
            observed.append(copy.deepcopy(merged))
            return merged
        f._brief_build_stop_policy_trace = capture
        return fn(artifact, summary, trace, canonical, facade=f), observed
    previous = original(INPUT).brief_input_canonical_monitor_snapshot_stop_policy_t
    expected = run(previous)
    actual = run(inputs.brief_input_canonical_monitor_snapshot_stop_policy_t)
    assert actual == expected
    assert actual[1] == [{'metric': 3, 'selected': value, 'flag': False}]
    assert actual[0][0] is canonical['monitor_snapshot']['monitor_stop_policy_trace']
    assert actual[0][1] is canonical['monitor_stop_policy_trace']
    assert (artifact, summary, trace, canonical) == before


@pytest.mark.parametrize('name,path,module,builder', [
    ('brief_input_candidate_hints_market_headlines', INPUT, inputs, 'build_operator_brief_input'),
    ('build_current_snapshot_section', SECTIONS, sections, 'build_operator_brief_sections'),
])
def test_wrong_owner_output_mutation_is_detected_after_green_baseline(name, path, module, builder, detail):
    expected = outcome(getattr(original(path), builder), detail, facade(True))
    assert expected[0] == 'ok'
    assert outcome(getattr(module, builder), detail, facade()) == expected
    bad = facade()
    fn = getattr(bad, name)
    def corrupt(*args, **kwargs):
        value = fn(*args, **kwargs)
        if isinstance(value, tuple):
            return (['WRONG-CANDIDATE'],) + value[1:]
        return value | {'summary': 'WRONG-EVIDENCE'}
    setattr(bad, name, corrupt)
    assert outcome(getattr(module, builder), detail, bad) != expected
    assert outcome(getattr(module, builder), detail, facade()) == expected
