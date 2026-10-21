from types import SimpleNamespace
import copy
import pytest
from fastapi.testclient import TestClient
import apps.operator_ui.main as ui
from test_p15_fast07_b_overview_render_smoke import overview
from test_p15_fast07_b_detail_render_smoke import run_detail


def client_for(monkeypatch, **payloads):
    defaults={'overview':overview(),'runs':[],'run_detail':{'found':False},'trade_report_detail':{'found':False},'operator_brief_detail':{'found':False},'health':{'status':'synthetic'}}
    defaults.update(payloads)
    for name in defaults:
        monkeypatch.setattr(ui,'load_'+('recent_runs' if name=='runs' else name),lambda *a,_name=name,**kw:copy.deepcopy(defaults[_name]))
    return TestClient(ui.create_app(SimpleNamespace(reports_root='unused-synthetic')))


@pytest.mark.parametrize('recon, expected', [
    ({'local_total':0,'broker_total':0,'matched_by_ord_no':0,'pending':False,'path':'invented-but-not-probed.json'},'NO_DATA'),
    ({'local_total':0,'broker_total':0,'matched_by_ord_no':0,'pending':False,'observed':True},'NO_EXECUTIONS'),
    ({'local_total':2,'broker_total':2,'matched_by_ord_no':2,'pending':False},'SUCCESS'),
    ({'local_total':2,'broker_total':2,'matched_by_ord_no':2,'pending':False,'broker_window_limited':True},'PENDING'),
    ({'local_total':0,'broker_total':0,'matched_by_ord_no':2,'pending':False},'UNKNOWN'),
])
def test_real_get_dashboard_does_not_promote_default_counters(monkeypatch,recon,expected):
    c=client_for(monkeypatch,overview=overview(reconciliation=recon))
    r=c.get('/');assert r.status_code==200
    assert f'data-reconciliation-state="{expected}"' in r.text
    assert 'UNKNOWN_SOURCE' in r.text


@pytest.mark.parametrize('row, expected', [({'execution_action':'BUY','execution_status':'ok','supervisor_allowed':False},'GUARDED'),
    ({'execution_action':'NOOP','execution_status':'ok'},'NO_ORDER'),
    ({'execution_action':'BUY','execution_status':'unclassified'},'UNKNOWN')])
def test_run_list_uses_shared_observations_and_stable_filter(monkeypatch,row,expected):
    c=client_for(monkeypatch,runs=[{'run_id':'R1',**row}]);r=c.get('/runs?activity_view=monitoring&mismatch_only=true&limit=25')
    assert r.status_code==200 and f'data-execution-state="{expected}"' in r.text
    assert 'activity_view=monitoring&amp;mismatch_only=false' in r.text
    assert 'href="/runs/R1"' in r.text
