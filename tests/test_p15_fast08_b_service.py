import json
import pytest
from fastapi.routing import APIRoute
import apps.operator_ui.main as ui
from test_p15_fast08_b_dashboard import client_for, run_detail


@pytest.mark.parametrize('path', ['/', '/runs', '/runs/R1', '/reports/trade/T1', '/reports/trade/T1/brief', '/healthz'])
def test_existing_six_get_successes_remain_read_only(monkeypatch,path):
    c=client_for(monkeypatch,run_detail=run_detail(found=True),trade_report_detail={'found':True,'raw_report':{}},operator_brief_detail={'found':True,'raw_brief':{},'sections':{}})
    response=c.get(path)
    assert response.status_code==200
    assert response.headers['cache-control']=='no-store'
    assert response.headers['x-content-type-options']=='nosniff'
    if path=='/healthz':assert response.json()=={'status':'synthetic'}


def test_missing_ids_remain_404_not_fake_empty_success(monkeypatch):
    c=client_for(monkeypatch)
    for path in ['/runs/missing','/reports/trade/missing','/reports/trade/missing/brief']:
        assert c.get(path).status_code==404


@pytest.mark.parametrize('error', [PermissionError('secret/source/path'),json.JSONDecodeError('sensitive corruption','{}',1)])
def test_known_source_read_errors_are_explicit_and_sanitized(monkeypatch,error):
    c=client_for(monkeypatch)
    def fail(*args,**kwargs):raise error
    monkeypatch.setattr(ui,'load_overview',fail)
    response=c.get('/')
    assert response.status_code==503 and response.json()=={'detail':'Read-only source temporarily unavailable.'}
    assert 'secret' not in response.text and 'sensitive' not in response.text


def test_query_validation_and_normalization_preserve_loader_arguments(monkeypatch):
    c=client_for(monkeypatch);calls=[]
    def rows(config,**kwargs):calls.append(kwargs);return []
    monkeypatch.setattr(ui,'load_recent_runs',rows)
    assert c.get('/runs').status_code==200
    assert calls.pop()=={'limit':50,'mismatch_only':False,'activity_view':'all'}
    assert c.get('/runs?limit=25&activity_view=invalid&mismatch_only=false').status_code==200
    assert calls.pop()=={'limit':25,'mismatch_only':False,'activity_view':'all'}
    assert c.get('/runs?limit=0').status_code==422 and not calls
    assert c.get('/runs?limit=201').status_code==422 and not calls


def test_no_new_action_routes_or_method_permissions(monkeypatch):
    c=client_for(monkeypatch)
    routes=[r for r in c.app.routes if isinstance(r,APIRoute)]
    assert len(routes)==6 and all(r.methods=={'GET'} for r in routes)
    def forbidden(*args,**kwargs):raise AssertionError('non-GET entered data loader')
    monkeypatch.setattr(ui,'load_overview',forbidden)
    for method in ['post','put','patch','delete']:
        assert getattr(c,method)('/').status_code==405
