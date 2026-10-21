"""FAST06 display-only smoke: no historical suite or operational data required."""
import copy
import json
import socket
import subprocess
import types

import pytest
from apps.operator_ui import data_access_status as status


@pytest.mark.parametrize('raw, expected', [
    ({}, 'unavailable'),
    ({'reader_ok': 'false', 'positions_mismatch_detected': False}, 'reader_error'),
    ({'reader_ok': 'true', 'positions_mismatch_detected': 'false'}, 'aligned'),
    ({'reader_ok': True, 'positions_mismatch_detected': True, 'reconciliation_applied': 'false'}, 'mismatch'),
    ({'reader_ok': True, 'positions_mismatch_detected': True, 'reconciliation_applied': True}, 'reconciled'),
    ({'reader_ok': 'unknown', 'positions_mismatch_detected': False}, 'unavailable'),
])
def test_recorded_sync_evidence_not_python_truthiness(raw, expected):
    original = copy.deepcopy(raw)
    card = status.build_portfolio_sync_card(raw)
    assert card['status'] == expected
    assert card['available'] == bool(raw)
    assert raw == original
    assert card['badge_class'].endswith('--ok') == (expected in {'aligned', 'reconciled'})


@pytest.mark.parametrize('lifecycle, story, expected, reason', [
    ('open', '', 'pending', 'awaiting_exit_for_full_report'),
    ('', 'decision_only', 'skipped', 'decision_only_run'),
    ('', 'failed_execution', 'skipped', 'execution_failed'),
    ('', '', 'failed', 'missing_report_linkage'),
])
def test_empty_diagnostics_fallback_keeps_unknown_input_and_reason(lifecycle, story, expected, reason):
    result = status.normalize_ai_report_diagnostics(None, report_exists=False, lifecycle_status=lifecycle, story_type=story)
    assert result['report_status'] == expected
    assert result['report_reason_code'] == reason
    assert result['story_input_available'] is False
    assert result['report_artifact_available'] is False
    assert result['generation_attempted'] is False
    assert result['next_expected_step']


@pytest.mark.parametrize('exists, stale_flag', [(False, True), (True, False)])
def test_actual_linked_artifact_wins_over_stale_diagnostic(exists, stale_flag):
    raw = {'report_status': 'available', 'report_output_available': stale_flag,
           'report_artifact_available': stale_flag, 'story_input_available': 'false'}
    result = status.normalize_ai_report_diagnostics(raw, report_exists=exists, lifecycle_status='', story_type='')
    assert result['report_output_available'] is exists
    assert result['report_artifact_available'] is exists
    assert result['story_input_available'] is False
    assert result['report_status'] == ('available' if exists else 'failed')


@pytest.mark.parametrize('raw, generation', [({'generation_attempted': 'false'}, {'status': 'failed'}), ({}, {'status': 'pending'})])
def test_generation_not_inferred_from_false_text_or_pending(raw, generation):
    result = status.normalize_ai_report_diagnostics(raw, report_exists=False, lifecycle_status='', story_type='', generation=generation)
    assert result['generation_attempted'] is False


def test_guard_reason_error_counts_and_unknown_badge_are_observations():
    raw = {'reader_ok': True, 'positions_mismatch_detected': False, 'reader_error': '조회 실패 한글',
           'guard_reason': 'NOOP / guard_denied', 'reader_positions_count': -4,
           'persisted_positions_count': 'not numeric', 'reader_positions_authoritative': 'false'}
    card = status.build_portfolio_sync_card(raw)
    assert card['status'] == 'reader_error'
    assert card['reader_error'] == '조회 실패 한글'
    assert 'NOOP / guard_denied' in card['note']
    assert card['reader_positions_count'] == card['persisted_positions_count'] == 0
    assert card['reader_positions_authoritative'] is False
    assert status.portfolio_sync_badge_class('stale') == 'status-badge'
    assert status.portfolio_sync_badge_class('unknown') == 'status-badge'
    assert '조회 실패' in json.dumps(card, ensure_ascii=False)


def test_schema_order_valid_baseline_and_no_io_or_order_effects(monkeypatch):
    baseline = types.ModuleType('fast06_status_baseline')
    text = subprocess.check_output(['git', 'show', 'd9e77a3f39e435edd10d09498cc0ade2d1232585:apps/operator_ui/data_access_status.py']).decode('utf-8')
    exec(compile(text, '<immutable FAST06 status BASE>', 'exec'), baseline.__dict__)
    raw = {'reader_ok': True, 'positions_mismatch_detected': False, 'reconciliation_applied': False,
           'reader_positions_count': 2, 'persisted_positions_count': 2, 'positions_source': 'reader_positions'}
    expected = baseline.build_portfolio_sync_card(raw)
    expected_empty = baseline.build_portfolio_sync_card(None)
    diag = {'story_input_available': True, 'generation_attempted': True}
    kwargs = dict(report_exists=True, lifecycle_status='closed', story_type='live_trade')
    expected_diag = baseline.normalize_ai_report_diagnostics(diag, **kwargs)
    original = copy.deepcopy(raw)
    def forbidden(*args, **kwargs):
        raise AssertionError('display code attempted IO/network/process')
    with monkeypatch.context() as m:
        m.setattr('builtins.open', forbidden)
        m.setattr(socket.socket, 'connect', forbidden)
        m.setattr(subprocess, 'Popen', forbidden)
        actual = status.build_portfolio_sync_card(raw)
        empty = status.build_portfolio_sync_card(None)
        actual_diag = status.normalize_ai_report_diagnostics(diag, **kwargs)
    assert actual == expected and list(actual) == list(expected)
    assert empty == expected_empty and list(empty) == list(expected_empty)
    assert actual_diag == expected_diag and list(actual_diag) == list(expected_diag)
    assert raw == original
