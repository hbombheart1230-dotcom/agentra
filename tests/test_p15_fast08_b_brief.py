import pytest
from test_p15_fast08_b_dashboard import client_for


@pytest.mark.parametrize('saved,sections,expected', [({'status':'fallback'}, {}, 'FALLBACK'),
    ({'stale':True}, {}, 'STALE'), ({},{},'NO_DATA'), ({'status':'ok'},{'executive_decision':{'final_action':'WAIT'}},'SAVED'),
    ({},{'executive_decision':{'final_action':'WAIT'}},'DERIVED')])
def test_actual_brief_get_does_not_invent_saved_or_current_authority(monkeypatch,saved,sections,expected):
    brief={'found':True,'raw_brief':saved,'sections':sections,'run_id':'R1'}
    r=client_for(monkeypatch,operator_brief_detail=brief).get('/reports/trade/T1/brief')
    assert r.status_code==200 and f'data-brief-state="{expected}"' in r.text
    assert 'Freshness not independently verified' in r.text
    assert 'status-badge--ok' not in r.text
    assert 'aria-describedby="console-notice"' in r.text


def test_brief_trace_links_use_safe_internal_families(monkeypatch):
    brief={'found':True,'raw_brief':{},'sections':{},'run_link':'javascript:bad()', 'report_link':'/reports/trade/T1'}
    r=client_for(monkeypatch,operator_brief_detail=brief).get('/reports/trade/T1/brief')
    assert 'href="javascript:' not in r.text
    assert 'href="/reports/trade/T1"' in r.text
    assert 'Link unavailable or unsafe' in r.text


def test_keyboard_structure_and_escaped_saved_text(monkeypatch):
    b={'found':True,'raw_brief':{'commander_summary':'<script>bad</script>'},'sections':{}}
    r=client_for(monkeypatch,operator_brief_detail=b).get('/reports/trade/T1/brief')
    assert r.status_code==200 and '<script>' not in r.text
    assert '&lt;script&gt;bad&lt;/script&gt;' in r.text
    for key in ['brief-evidence','brief-decision','brief-risk','brief-next']:
        assert f'href="#{key}"' in r.text and f'id="{key}"' in r.text
    assert 'Skip to main content' in r.text and 'aria-current="page"' in r.text
