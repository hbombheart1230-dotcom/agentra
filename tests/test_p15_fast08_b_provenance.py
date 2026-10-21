import pytest
from test_p15_fast08_b_dashboard import client_for, run_detail


@pytest.mark.parametrize('source', ['canonical','normalized_trade_artifact','event_log'])
def test_real_detail_exposes_declared_source_and_escapes_reason(monkeypatch,source):
    detail=run_detail(found=True,artifact_provenance={'monitor':source},monitor={'summary':{'reason':'NOOP'},'decision_trace':{}},
        supervisor={'verdict':{'allowed':False,'reason':'denied <script>bad</script>'}},executor={'execution':{'action':'BUY','status':'never_sent'}})
    r=client_for(monkeypatch,run_detail=detail).get('/runs/R1')
    assert r.status_code==200 and f'data-source-class="{source}"' in r.text
    assert 'data-execution-state="GUARDED"' in r.text
    assert 'denied &lt;script&gt;bad&lt;/script&gt;' in r.text and '<script>' not in r.text


@pytest.mark.parametrize('link, clickable', [('javascript:alert(1)',False),('//external.test/runs/R1',False),('/runs/%2e%2e/secret',False),('/runs/R1',True)])
def test_trade_trace_links_are_internal_and_artifact_absence_wins(monkeypatch,link,clickable):
    report={'found':True,'run_link':link,'report_available':False,'raw_report':{},'ai_report_diagnostics':{'report_status_label':'AI Report Available'}}
    r=client_for(monkeypatch,trade_report_detail=report).get('/reports/trade/T1')
    assert r.status_code==200
    assert ('href="/runs/R1"' in r.text) is clickable
    assert 'href="javascript:' not in r.text and 'href="//external' not in r.text
    assert 'NO_DATA — no linked AI artifact' in r.text


def test_reader_error_and_no_order_are_observations(monkeypatch):
    d=run_detail(found=True,portfolio_sync={'reader_error':'query <failed>'},executor={'execution':{'action':'NOOP','status':'ok'}})
    r=client_for(monkeypatch,run_detail=d).get('/runs/R1')
    assert r.status_code==200 and 'data-execution-state="NO_ORDER"' in r.text
    assert 'Reader error: query &lt;failed&gt;' in r.text
    assert 'data-source-class="MISSING"' in r.text
