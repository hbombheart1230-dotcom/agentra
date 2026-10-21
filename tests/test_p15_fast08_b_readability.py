from pathlib import Path
import socket
import subprocess
import pytest
from test_p15_fast08_b_dashboard import client_for, run_detail
from test_p15_fast07_b_accessibility_smoke import Markup


@pytest.mark.parametrize('path', ['/', '/runs', '/runs/R1', '/reports/trade/T1', '/reports/trade/T1/brief'])
def test_real_get_markup_has_accessible_targets_and_no_live_controls(monkeypatch,path):
    detail=run_detail(found=True,run_id='R-'+'long-'*100)
    report={'found':True,'raw_report':{},'run_id':'R1'}
    brief={'found':True,'raw_brief':{'status':'fallback'},'sections':{}}
    c=client_for(monkeypatch,run_detail=detail,trade_report_detail=report,operator_brief_detail=brief)
    def forbidden(*a,**kw):raise AssertionError('GET rendering attempted external network/process')
    # Bootstrap the ASGI loop before guarding GET: Windows Proactor creates
    # its own internal socket pair while starting, not as a UI network effect.
    with c:
        with monkeypatch.context() as m:
            m.setattr(socket.socket,'connect',forbidden);m.setattr(subprocess,'Popen',forbidden)
            response=c.get(path)
    assert response.status_code==200
    markup=Markup();markup.feed(response.text)
    assert not markup.errors and not markup.stack
    assert len(markup.ids)==len(set(markup.ids))
    assert sum(tag=='main' for tag,_ in markup.tags)==1
    assert not any(tag in {'button','form','script'} for tag,_ in markup.tags)
    for link in markup.links:
        if link.startswith('#'):assert link[1:] in markup.ids
    assert 'Skip to main content' in response.text


def test_provenance_styles_cover_compact_screens_and_print():
    css=(Path(__file__).resolve().parents[1]/'apps/operator_ui/static/operator.css').read_text(encoding='utf-8')
    assert css.count('{')==css.count('}')
    for selector in ['max-width: 780px','max-width: 480px','@media print','.reader-error','.source-confidence',
                     '.source-details ul','overflow-wrap: anywhere',':focus-visible']:
        assert selector in css
    assert 'grid-template-columns: repeat(2, minmax(0, 1fr))' in css
    assert 'prefers-reduced-motion' in css
