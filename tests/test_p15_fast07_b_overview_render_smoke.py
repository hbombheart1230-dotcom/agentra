"""Synthetic Jinja renders only; no runtime loaders, broker or production files."""
from pathlib import Path
from types import SimpleNamespace

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]


def render(name, **context):
    env = Environment(loader=FileSystemLoader(ROOT/'apps/operator_ui/templates'), autoescape=select_autoescape(['html']))
    return env.get_template(name).render(request=SimpleNamespace(url_for=lambda name, path: '/static/'+path), page_title='Test', section='runs', **context)


def overview(**updates):
    data = dict(operator_summary={}, reconciliation={}, portfolio_sync={}, portfolio_sync_summary={},
                daily={'events': 0, 'approvals': 0, 'blocks': 0, 'decision_actions': {}}, today_trades=[],
                overtrading_warning={}, today_traded_symbols=[], reporter={}, latest_strategist_prompt={}, strategy_memory_timeline=[])
    data.update(updates)
    return data


@pytest.mark.parametrize('action, execution, expected', [
    ('BUY', 'filled', 'SUCCESS'), ('BUY', 'failed', 'FAILED'), ('NOOP', 'denied', 'GUARDED'),
    ('BUY', 'accepted', 'PENDING'), ('BUY', 'mystery', 'UNKNOWN'), ('', '', 'NO_DATA'), ('NOOP', 'ok', 'NO_EXECUTION'),
])
def test_execution_state_is_recorded_not_truthy(action, execution, expected):
    text = render('runs.html', runs=[{'run_id': 'run-한글', 'execution_action': action, 'execution_status': execution,
        'report_available': 'false', 'report_link': '/not-an-artifact', 'macro_stress_active': None}], limit=50, activity_view='all', mismatch_only=False)
    assert f'data-execution-state="{expected}"' in text
    assert 'href="/not-an-artifact"' not in text
    assert 'UNKNOWN' in text


@pytest.mark.parametrize('recon, expected', [({}, 'NO_DATA'),
    ({'local_total': 0, 'broker_total': 0, 'matched_by_ord_no': 0, 'pending': False}, 'NO_EXECUTIONS'),
    ({'local_total': 2, 'broker_total': 2, 'matched_by_ord_no': 2, 'pending': False}, 'SUCCESS'),
    ({'local_total': 1, 'broker_total': 1, 'matched_by_ord_no': 1, 'pending': 'false'}, 'UNKNOWN'),
])
def test_dashboard_distinguishes_absence_from_reconciliation(recon, expected):
    text = render('overview.html', overview=overview(reconciliation=recon))
    assert f'data-reconciliation-state="{expected}"' in text
    assert 'data-system-state="NO_DATA"' in text
    assert text.count('card--status-ok') == (2 if expected == 'SUCCESS' else 0)


def test_empty_runs_and_filter_trace_are_preserved_and_escaped():
    text = render('runs.html', runs=[], limit=25, activity_view='monitoring', mismatch_only=True)
    assert 'NO_DATA — No runs match' in text
    assert 'activity_view=monitoring&amp;mismatch_only=false' in text
    assert 'activity_view=trades&amp;mismatch_only=true' in text
    attack = render('runs.html', runs=[{'run_id':'<script>alert(1)</script>'}], limit=25, activity_view='all', mismatch_only=False)
    assert '<script>' not in attack
    assert '&lt;script&gt;' in attack
