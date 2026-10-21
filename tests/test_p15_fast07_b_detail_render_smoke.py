"""Focused synthetic detail/brief HTML, no artifact loaders or external effects."""
import pytest
from test_p15_fast07_b_overview_render_smoke import render


def run_detail(**updates):
    data = dict(run_id='run-한글', commander={}, strategist={'summary':{}, 'llm':{}, 'decision_trace':{}, 'evidence':{}},
                scanner={'summary':{},'decision_trace':{},'feature_coverage':{},'quote_metrics':{}}, monitor={'summary':{},'decision_trace':{}},
                supervisor={'verdict':{}}, executor={'execution':{}}, reporter={}, operator_brief={'sections':{}},
                trade_report={}, portfolio_sync={}, same_day_symbol_trade_history={}, same_day_symbol_run_chain={}, event_preview=[])
    data.update(updates)
    return data


@pytest.mark.parametrize('allowed, expected', [(False,'GUARDED'),(True,'RECORDED_ALLOWED'),('false','UNKNOWN')])
def test_run_guard_is_distinct_from_intent_and_execution(allowed, expected):
    text = render('run_detail.html', detail=run_detail(supervisor={'verdict':{'allowed':allowed,'reason':'guard_denied <unsafe>'}},
        executor={'execution':{'action':'NOOP','status':'blocked'}}, commander={'command_intent':'BUY'}))
    assert f'data-approval-state="{expected}"' in text
    assert 'guard_denied &lt;unsafe&gt;' in text
    assert 'NOOP / blocked' in text
    assert 'data-decision-only="true"' in text
    assert 'status-badge--ok' not in text


@pytest.mark.parametrize('available, linked', [(True, True),(False,False),('false',False)])
def test_run_report_link_requires_actual_boolean_artifact(available, linked):
    text = render('run_detail.html', detail=run_detail(trade_report={'report_available':available, 'report_link':'/reports/trade/T1',
        'operator_brief_available':True,'operator_brief_link':'/reports/trade/T1/brief'}))
    assert ('href="/reports/trade/T1"' in text) is linked
    assert 'href="/reports/trade/T1/brief"' in text
    if not linked: assert 'data-artifact-state="NO_DATA"' in text


@pytest.mark.parametrize('available, expected', [(True,'OBSERVED'),(False,'NO_DATA'),('false','NO_DATA')])
def test_trade_provenance_absence_and_reader_error_escape(available, expected):
    report = {'report_available':available,'story_id':'T1','run_id':'R1','run_link':'/runs/R1','paths':{'ai_trade_report_json':'test/<missing>.json'},
              'ai_report_diagnostics':{'generation_attempted':'false','last_error_message':'reader <failure>'},'raw_report':{}}
    text=render('trade_report_detail.html',report=report)
    assert f'data-artifact-state="{expected}"' in text
    assert 'test/&lt;missing&gt;.json' in text
    assert 'reader &lt;failure&gt;' in text
    assert 'href="/runs/R1"' in text
    assert 'NO_DATA — No saved report JSON' in text
    assert 'Attempted: UNKNOWN' in text
