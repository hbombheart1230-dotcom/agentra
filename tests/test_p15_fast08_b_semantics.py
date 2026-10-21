import copy
from pathlib import Path
import pytest
from apps.operator_ui.fast08_observation_view import observed_number, execution_observation, safe_trace_link
from apps.operator_ui.data_access_runs import prefer_canonical_agent_payload
from apps.operator_ui.data_access_linkage import existing_trade_path
from apps.operator_ui.data_access_brief import saved_brief_observation


@pytest.mark.parametrize('value, expected', [(None,None),(0,0),(False,None),(float('nan'),None),('0',None)])
def test_missing_numeric_evidence_is_not_zero(value, expected):
    assert observed_number(value) == expected


def test_nested_absence_does_not_override_real_canonical_and_false_is_evidence():
    canonical={'artifacts':{'monitor':{'summary':{'allowed':False,'count':0}}}}
    original=copy.deepcopy(canonical)
    payload, source=prefer_canonical_agent_payload(canonical,'monitor',{'fallback':1},normalized_payload={'summary':{'reason':None}})
    assert source=='canonical' and payload['summary']['allowed'] is False
    assert canonical==original
    payload,source=prefer_canonical_agent_payload(canonical,'monitor',{},normalized_payload={'summary':{'count':0}})
    assert source=='normalized_trade_artifact' and payload['summary']['count']==0


def test_linkage_requires_file_and_retains_priority(tmp_path):
    one=tmp_path/'directory';one.mkdir();two=tmp_path/'valid.json';two.write_text('{}')
    assert existing_trade_path({'a':one,'b':two},'a','b')==two
    assert existing_trade_path({'a':one},'a')==Path()


@pytest.mark.parametrize('action,status,allowed,expected', [('BUY','ok',False,'GUARDED'),('NOOP','ok',None,'NO_ORDER'),('BUY','accepted',True,'PENDING')])
def test_guard_and_intent_never_masquerade_as_fill(action,status,allowed,expected):
    assert execution_observation(action,status,allowed)['state']==expected


def test_saved_fallback_and_link_safety_are_pure():
    assert saved_brief_observation({'status':'fallback'})['state']=='FALLBACK'
    assert saved_brief_observation({})['source_class']=='missing'
    assert safe_trace_link('javascript:alert(1)')==''
    assert safe_trace_link('/runs/../secret')==''
    assert safe_trace_link('/runs/R1')=='/runs/R1'


def test_invalid_normalized_container_never_becomes_authoritative():
    for bad in [0, False, "invalid", []]:
        result, source=prefer_canonical_agent_payload({'artifacts':{'monitor':{'count':0}}},'monitor',{},normalized_payload=bad)
        assert source=='canonical' and result['count']==0
