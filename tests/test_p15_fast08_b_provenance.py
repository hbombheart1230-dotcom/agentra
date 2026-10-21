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


@pytest.mark.parametrize('intent,reader', [('HOLD <script>x</script>','canonical <b>db</b>'), (0,False), (None,None)])
def test_restored_run_observations_preserve_values_and_escape(monkeypatch,intent,reader):
    d=run_detail(found=True,commander={'command_intent':intent},portfolio_sync={'positions_source_label':reader})
    r=client_for(monkeypatch,run_detail=d).get('/runs/R1')
    assert r.status_code==200
    from html import escape
    expected_intent='not captured' if intent is None else escape(str(intent))
    expected_reader='not captured' if reader is None else escape(str(reader))
    assert f'<dt>Decision / intent</dt><dd>{expected_intent}</dd>' in r.text
    assert f'<dt>Reader source</dt><dd>{expected_reader}</dd>' in r.text
    assert '<script>' not in r.text


def test_recorded_intent_path_fallback(monkeypatch):
    d=run_detail(found=True,commander={'path':'recorded fallback'})
    assert '<dt>Decision / intent</dt><dd>recorded fallback</dd>' in client_for(monkeypatch,run_detail=d).get('/runs/R1').text


@pytest.mark.parametrize('payload,state', [
    ({'report_status':'available','report_link':'/reports/trade/T1'},'NO_DATA'),
    ({'report_available':'true','report_link':'/reports/trade/T1'},'NO_DATA'),
    ({'report_available':True,'report_link':'https://outside.test'},'UNKNOWN'),
    ({'report_available':True},'UNKNOWN'),
    ({'report_available':False,'report_link':'/reports/trade/T1'},'NO_DATA'),
    ({'found':False,'report_available':True,'report_link':'/reports/trade/T1'},'UNKNOWN'),
    ({'report_available':True,'report_link':'/reports/trade/T1'},'OBSERVED')])
def test_linked_artifact_requires_confirmed_availability_and_safe_link(payload,state):
    from apps.operator_ui.fast08_detail_view import artifact_observation
    view=artifact_observation(payload)
    assert view['state']==state
    assert bool(view['link']) is (state=='OBSERVED')


@pytest.mark.parametrize('raw,sections,state,source', [
    ({'status':'saved'}, {}, 'NO_DATA','unknown'),
    ({'path':'invented.json','url':'/reports/trade/T1'}, {}, 'NO_DATA','unknown'),
    ({'status':'saved'}, {'summary':0}, 'DERIVED','derived_view'),
    ({'sections':{'summary':False}}, None, 'SAVED','saved_artifact'),
    ({'sections':{'summary':0}}, None, 'SAVED','saved_artifact'),
    ({'sections':{'summary':''}}, None, 'NO_DATA','unknown'),
    ({'status':'fallback'}, {'summary':'derived'}, 'FALLBACK','derived_view'),
    ({}, {}, 'NO_DATA','missing')])
def test_saved_brief_metadata_is_not_saved_content(raw,sections,state,source):
    from apps.operator_ui.fast08_detail_view import saved_brief_observation
    view=saved_brief_observation(raw,sections=sections)
    assert (view['state'],view['source_class'])==(state,source)
    assert view['freshness_verified'] is False


@pytest.mark.parametrize('raw,sections,expected', [
    ({'status':'ok'}, {'executive_decision':{'final_action':'WAIT'}}, 'DERIVED'),
    ({'sections':{'executive_decision':{'final_action':'WAIT'}}}, {'executive_decision':{'final_action':'WAIT'}}, 'SAVED'),
    ({'status':'saved','path':'invented.json'}, {}, 'NO_DATA')])
def test_actual_brief_get_uses_content_not_metadata_as_saved_evidence(monkeypatch,raw,sections,expected):
    c=client_for(monkeypatch,operator_brief_detail={'found':True,'raw_brief':raw,'sections':sections})
    response=c.get('/reports/trade/T1/brief')
    assert response.status_code==200
    assert f'data-brief-state="{expected}"' in response.text
