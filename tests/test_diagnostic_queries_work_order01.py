"""Source Work Order01: synthetic events only, no runtime or broker execution."""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

NAMES = ['query_commander_resilience_events', 'query_strategist_llm_events',
         'query_trade_reason_chain', 'query_m25_notification_events']
REPO = Path(__file__).resolve().parents[1]
TRADE = importlib.import_module('scripts.diagnostics.query_trade_reason_chain')


@pytest.mark.parametrize('name', NAMES)
def test_readers_preserve_missing_empty_malformed_unicode_duplicates_order(tmp_path, name):
    module = importlib.import_module('scripts.diagnostics.' + name)
    reader = module._iter_rows if 'm25' in name else module._load_jsonl
    path = tmp_path / 'events.jsonl'
    assert reader(path) == []
    path.write_text('', encoding='utf-8')
    assert reader(path) == []
    rows = [{'tag': '한글'}, {'tag': 'second'}, {'tag': '한글'}]
    path.write_text('\n  \n{broken\n[]\n123\n"text"\nnull\n' +
                    '\n'.join(json.dumps(r, ensure_ascii=False) for r in rows), encoding='utf-8')
    assert reader(path) == rows
    assert list(tmp_path.iterdir()) == [path]  # day=None creates no cache
    assert importlib.import_module('scripts.' + name) is module


@pytest.mark.parametrize('value,expected', [
    (0, True), ('0', True), ('0.0', True), (1, False), ('-1', False),
    (0.5, False), ('0.5', False), ('-0.5', False), ('ok', True),
    ('success', True), ('accepted', True), ('error', False), ('failed', False),
    ('rejected', False), (None, None), ('', None), ('NaN', False), ('Infinity', False),
    ('1e-9999', False), ('-1e-9999', False), ('-0.0', True),
])
def test_broker_code_exact_numeric_zero(value, expected):
    assert TRADE._broker_code_success(value) is expected


def event(kind, payload, run='same'):
    return {'run_id': run, 'stage': 'decision' if kind == 'trace' else 'execute_from_packet',
            'event': kind, 'payload': payload}


def execution(intent='A', action='BUY', **extra):
    return event('execution', {'intent_id': intent, 'reason': 'execution-only',
                 'order': {'action': action, 'symbol': 'FAKE', 'qty': 1},
                 'payload': {'broker_code': '0'}, **extra})


@pytest.mark.parametrize('allowed', [True, False, None])
@pytest.mark.parametrize('outcome', ['UNKNOWN', 'NOT_SENT'])
def test_execution_allowed_is_authoritative_without_verdict(allowed, outcome):
    row, = TRADE._build_rows([execution(allowed=allowed, broker_outcome=outcome)])
    assert row['allowed'] is allowed
    assert row['verdict_reason'] == ''
    assert row['execution_reason'] == 'execution-only'


def test_same_run_interleaved_intents_keep_decision_and_verdict_separate():
    records = [
        event('trace', {'decision_packet': {'intent': {'intent_id': 'A', 'rationale': 'buy-A'}},
                        'trace': {'strategy': 'buy-strategy'}}),
        event('verdict', {'intent_id': 'A', 'allowed': True, 'reason': 'verdict-A'}),
        event('trace', {'decision_packet': {'intent': {'intent_id': 'B', 'rationale': 'sell-B'}}}),
        event('verdict', {'intent_id': 'B', 'allowed': False, 'reason': 'verdict-B'}),
        execution('A', allowed=False), execution('B', 'SELL'), execution('C', 'BUY'),
    ]
    a, b, c = TRADE._build_rows(records)
    assert (a['allowed'], a['verdict_reason'], a['decision_rationale']) == (False, 'verdict-A', 'buy-A')
    assert (b['allowed'], b['verdict_reason'], b['decision_rationale']) == (False, 'verdict-B', 'sell-B')
    assert c['allowed'] is None
    assert c['verdict_reason'] == c['decision_rationale'] == c['decision_strategy'] == ''
    assert TRADE._build_rows(records, action_filter='SELL') == [b]
    assert TRADE._build_rows(records, run_id_filter='other') == []
    assert TRADE._build_rows(records, only_broker_success=True) == [a, b, c]
    assert set(a) == {'ts', 'run_id', 'action', 'symbol', 'qty', 'price', 'order_type',
        'execution_reason', 'allowed', 'verdict_reason', 'broker_code', 'broker_ok',
        'broker_message', 'order_id', 'decision_strategy', 'decision_rationale', 'decision_reason',
        'llm_provider', 'llm_model', 'llm_ok', 'llm_intent_action', 'llm_intent_reason',
        'llm_intent_rationale', 'llm_latency_ms'}


@pytest.mark.parametrize('intent', ['', 'different', None])
def test_unproven_verdict_never_attributed(intent):
    verdict = event('verdict', {'intent_id': intent, 'allowed': True, 'reason': 'foreign'})
    row, = TRADE._build_rows([verdict, execution('A')])
    assert row['allowed'] is None and row['verdict_reason'] == ''


def test_legacy_multi_execution_drops_ambiguous_decision_and_llm_context():
    records = [event('trace', {'trace': {'rationale': 'ambiguous'}}),
               {'run_id': 'same', 'stage': 'strategist_llm', 'event': 'result',
                'payload': {'intent_rationale': 'ambiguous-llm'}},
               execution('', 'BUY'), execution('', 'SELL')]
    for row in TRADE._build_rows(records):
        assert row['decision_rationale'] == row['llm_intent_rationale'] == ''


def test_conflicting_nested_intent_ids_are_unproven():
    records = [event('verdict', {'intent_id': 'A', 'decision_packet': {'intent_id': 'B'},
                               'allowed': True, 'reason': 'conflict'}), execution('A')]
    row, = TRADE._build_rows(records)
    assert row['allowed'] is None and row['verdict_reason'] == ''


@pytest.mark.parametrize('name', NAMES)
@pytest.mark.parametrize('mode', ['json', 'text', 'help', 'unknown', 'missing'])
def test_all_four_public_cli_forms_match(tmp_path, name, mode):
    fake = tmp_path / 'events.jsonl'
    rows = [execution(allowed=True),
            {'run_id': 'same', 'stage': 'commander_router', 'event': 'error', 'payload': {}},
            {'run_id': 'same', 'stage': 'strategist_llm', 'event': 'result', 'payload': {'ok': False}},
            {'ts': '2026-10-15T00:00:00Z', 'stage': 'ops_batch_notify', 'event': 'result',
             'payload': {'day': '2026-10-15', 'provider': 'none'}}]
    fake.write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')
    option = '--event-log-path' if 'm25' in name else '--path'
    args = [option, str(fake)]
    expected = 0
    if mode == 'json': args += ['--json']
    if mode == 'help': args = ['--help']
    if mode == 'unknown': args += ['--unknown-option']; expected = 2
    if mode == 'missing':
        args = [option, str(tmp_path / 'missing.jsonl'), '--json']
        expected = 0 if 'm25' in name else 2
    env = {**os.environ, 'PYTHONPATH': str(REPO), 'PYTHONIOENCODING': 'utf-8'}
    forms = [[str(REPO / 'scripts' / (name + '.py'))], ['-m', 'scripts.' + name],
             [str(REPO / 'scripts/diagnostics' / (name + '.py'))], ['-m', 'scripts.diagnostics.' + name]]
    results = [subprocess.run([sys.executable, *form, *args], cwd=tmp_path, env=env,
                             capture_output=True, text=True, timeout=20) for form in forms]
    assert all(r.returncode == expected for r in results), [(r.returncode, r.stderr) for r in results]
    assert len({r.stdout for r in results}) == 1
    assert len({r.stderr for r in results}) == 1
    if mode == 'json': json.loads(results[0].stdout)


def test_explicit_null_allowed_overrides_matching_legacy_verdict():
    row, = TRADE._build_rows([
        event('verdict', {'intent_id': 'A', 'allowed': True, 'reason': 'same-intent'}),
        execution('A', allowed=None),
    ])
    assert row['allowed'] is None
    assert row['verdict_reason'] == 'same-intent'


def test_trade_cli_filters_limit_and_invalid_action(tmp_path, capsys):
    fake = tmp_path / 'events.jsonl'
    fake.write_text('\n'.join(json.dumps(e) for e in [
        execution('A', allowed=True), execution('B', 'SELL', allowed=False),
        execution('C', allowed=True, payload={'broker_code': '0.5'}),
    ]), encoding='utf-8')
    assert TRADE.main(['--path', str(fake), '--json', '--run-id', 'same',
                       '--action', 'BUY', '--only-broker-success', '--limit', '1']) == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 1 and rows[0]['action'] == 'BUY' and rows[0]['allowed'] is True
    assert TRADE.main(['--path', str(fake), '--action', 'invalid']) == 3
    assert '--action must be BUY or SELL' in capsys.readouterr().err
