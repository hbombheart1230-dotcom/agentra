"""FAST10 observations through real Jinja/GETs, with synthetic reader inputs."""
import copy
from pathlib import Path
import pytest
from apps.operator_ui.fast08_detail_view import project_run_row, project_run, run_trace_link
from apps.operator_ui.fast08_dashboard_view import project_dashboard, project_traces
from test_p15_fast08_b_dashboard import client_for, overview, run_detail


@pytest.mark.parametrize('action,status,allowed,expected', [
    ('BUY','ok',True,'UNKNOWN'), ('SELL','completed',True,'UNKNOWN'),
    ('BUY','filled',None,'EXECUTED'), ('SELL','executed',True,'EXECUTED'),
    ('NOOP','ok',None,'NO_ORDER'), ('NOOP','filled',None,'UNKNOWN'),
    ('BUY','filled',False,'GUARDED'), ('BUY','accepted',True,'PENDING'),
    ('BUY','failed',True,'FAILED'), ('BUY','mystery',True,'UNKNOWN'),
    ('','','false','GUARDED'), ('','',None,'NO_DATA')])
def test_list_and_detail_use_same_recorded_execution_semantics(monkeypatch,action,status,allowed,expected):
    row={'run_id':'R1','execution_action':action,'execution_status':status,'supervisor_allowed':allowed}
    detail=run_detail(found=True,executor={'execution':{'action':action,'status':status}},supervisor={'verdict':{'allowed':allowed}})
    c=client_for(monkeypatch,runs=[row],run_detail=detail)
    for path in ['/runs','/runs/R1']:
        response=c.get(path)
        assert response.status_code==200
        assert f'data-execution-state="{expected}"' in response.text


@pytest.mark.parametrize('value,expected', [(None,'MISSING'), ({},'MISSING'),
    ({'stale':True},'STALE'), ({'reader_error':'read failed'},'ERROR'),
    ({'source':'fallback'},'FALLBACK'), ({'count':0,'allowed':False},'UNKNOWN')])
def test_source_health_is_recorded_and_not_inferred(value,expected):
    from apps.operator_ui.fast08_detail_view import source_observation
    assert source_observation(value)==expected


def test_mixed_trace_counts_are_filtered_observations_and_do_not_mutate_inputs(monkeypatch):
    rows=[{'run_id':'R1','execution_action':'BUY','execution_status':'filled'},
          {'execution_action':'NOOP','execution_status':'ok','stale':True},
          {'execution_action':'BUY','execution_status':'ok','supervisor_allowed':False},
          {'execution_action':'BUY','execution_status':'ok','supervisor_allowed':True}, None]
    before=copy.deepcopy(rows)
    view=project_traces(rows)
    assert view['total']==5 and view['malformed']==1
    assert sum(view['counts'].values())==5
    assert {k:v for k,v in view['counts'].items() if v}=={'EXECUTED':1,'GUARDED':1,'NO_ORDER':1,'UNKNOWN':1,'NO_DATA':1}
    assert rows==before
    page=client_for(monkeypatch,runs=rows).get('/runs?activity_view=monitoring&limit=25')
    assert page.status_code==200
    assert 'Filtered rows only' in page.text and '1 malformed records' in page.text
    assert 'data-source-state="STALE"' in page.text
    assert 'activity_view=trades&amp;mismatch_only=false' in page.text


@pytest.mark.parametrize('value', [False,0,{'bad':'collection'},'not a collection'])
def test_malformed_run_collection_is_explicit_not_an_empty_success(monkeypatch,value):
    page=client_for(monkeypatch,runs=value).get('/runs')
    assert page.status_code==200
    assert 'Run collection is malformed' in page.text


@pytest.mark.parametrize('run_id', [None,False,'','../secret','a/b','a\\b','a\nheader'])
def test_unsafe_run_identity_never_becomes_drilldown(monkeypatch,run_id):
    assert not run_trace_link(run_id)
    page=client_for(monkeypatch,runs=[{'run_id':run_id,'report_available':True,'report_link':'javascript:alert(1)',
                                     'operator_brief_available':True,'operator_brief_link':'//evil.test'}]).get('/runs')
    assert page.status_code==200
    assert 'Run trace not captured or unsafe' in page.text
    assert 'href="javascript:' not in page.text and 'href="//evil' not in page.text


def test_unicode_drilldown_and_missing_sources_are_escaped(monkeypatch):
    row={'run_id':'실행 0','source_error':'<script>bad</script>'}
    page=client_for(monkeypatch,runs=[row]).get('/runs')
    assert page.status_code==200 and '/runs/%EC%8B%A4%ED%96%89%200' in page.text
    assert 'data-source-state="ERROR"' in page.text and '<script>' not in page.text


@pytest.mark.parametrize('value', [False,'bad',float('nan'),float('inf'),-1,2])
def test_malformed_coverage_and_flags_never_break_run_rendering(monkeypatch,value):
    page=client_for(monkeypatch,runs=[{'run_id':'R1','feature_coverage_ratio':value,'macro_stress_active':True,'macro_stress_flags':12}]).get('/runs')
    assert page.status_code==200 and 'UNKNOWN' in page.text
    assert project_run_row({'feature_coverage_ratio':value})['coverage'] is None


def test_overview_keeps_zero_unknown_permission_and_stale_distinct(monkeypatch):
    data=overview(operator_summary={'system_status':'GREEN','stale':True,'run_total':0,'executions_total':0,'blocked_total':False},
                  daily={'approvals':0,'blocks':None},today_trades=[{'run_id':'R1','action':'BUY','status':'ok'}])
    view=project_dashboard(data)
    assert view['run_total']==0 and view['blocked_total'] is None and view['approvals']==0
    assert view['system']['state']=='STALE'
    page=client_for(monkeypatch,overview=data).get('/')
    assert page.status_code==200
    assert 'Declared run count: 0' in page.text
    assert 'Block count not captured' in page.text
    assert 'data-execution-state="UNKNOWN"' in page.text
    assert 'permission is not execution' in page.text
    assert 'href="/runs/R1"' in page.text


def test_detail_navigation_and_source_health_use_only_supplied_evidence(monkeypatch):
    detail=run_detail(found=True,portfolio_sync={'reader_error':'missing <file>'},
                      artifact_provenance={'monitor':'canonical'},monitor={'stale':True})
    page=client_for(monkeypatch,run_detail=detail).get('/runs/R1')
    assert page.status_code==200
    assert 'href="/runs"' in page.text and 'href="#run-source-status"' in page.text
    assert 'monitor: canonical / STALE' in page.text
    assert 'Reader error: missing &lt;file&gt;' in page.text
    assert 'data-source-state="ERROR"' in page.text


def test_compact_layout_has_480_and_780_keyboard_structure(monkeypatch):
    css=(Path(__file__).resolve().parents[1]/'apps/operator_ui/static/operator.css').read_text(encoding='utf-8')
    for text in ['max-width: 480px','max-width: 780px','.trace-navigation','.trace-summary .trace-counts','#run-evidence:focus']:
        assert text in css
    page=client_for(monkeypatch,runs=[]).get('/runs')
    assert 'href="#run-evidence"' in page.text
    assert 'aria-describedby="trace-count-scope" id="run-evidence"' in page.text
    assert 'tabindex="0"' in page.text
