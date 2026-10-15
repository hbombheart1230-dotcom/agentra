"""WO03: pure diagnostic helpers; child CLIs are stubs, no closeout/drill runs."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys

import pytest

from libs.diagnostics import broker_code_success, capture_cli_json, line_count, numeric_summary, sha256_file

D = 'scripts.diagnostics.'
CAPTURES = [
    ('run_m23_closeout_check', '_run_resilience_closeout_json', 'resilience_closeout_main',
     {'events_path': Path('fake'), 'no_clear': True, 'skip_error_case': True},
     ['--event-log-path', 'fake', '--json', '--no-clear', '--skip-error-case']),
    ('run_m24_closeout_check', '_run_guard_json', 'guard_main',
     {'intent_log_path': Path('fake'), 'state_db_path': Path('fake.db'), 'no_clear': True, 'skip_duplicate_case': True},
     ['--intent-log-path','fake','--state-db-path','fake.db','--json','--no-clear','--skip-duplicate-case']),
    ('run_m24_closeout_check', '_run_state_query_json', 'query_state_main',
     {'intent_log_path': Path('fake'), 'state_db_path': Path('fake.db'), 'stuck_executing_sec': -1},
     ['--intent-log-path','fake','--state-db-path','fake.db','--stuck-executing-sec','0','--require-no-stuck','--json','--limit','50']),
    ('run_m26_closeout_check', '_run_json', None, {}, ['--fake']),
    ('run_m27_closeout_check', '_run_json', None, {}, ['--fake']),
    ('run_m29_closeout_check', '_run_json', None, {}, ['--fake']),
    ('run_m29_log_archive_integrity_check', '_run_json', 'integrity_main', {}, ['--fake']),
]


@pytest.mark.parametrize('stdout,expected', [(' {"한글":1} ', {'한글':1}), ('[1,2]', [1,2]),
    ('3',3), ('null',None), ('true',True), ('"text"','text'), ('',{}), ('broken',{}), ('{}\nnoise',{})])
def test_capture_preserves_json_types_invalid_and_stderr(stdout, expected, capsys):
    args = ['--fake', 'a b']
    def stub(argv):
        assert argv is args
        print(stdout)
        print('child-stderr', file=sys.stderr)
        return '7'
    assert capture_cli_json(stub, args) == (7, expected)
    out = capsys.readouterr()
    assert out.out == '' and out.err == 'child-stderr\n'
    print('outer-stdout')
    assert capsys.readouterr().out == 'outer-stdout\n'


@pytest.mark.parametrize('error', [RuntimeError('fake'), SystemExit(9)])
def test_capture_propagates_child_exceptions_and_restores_stdout(error, capsys):
    def stub(argv):
        print('hidden'); print('visible', file=sys.stderr); raise error
    with pytest.raises(type(error)) as raised: capture_cli_json(stub, [])
    assert raised.value is error
    print('restored')
    assert capsys.readouterr() == ('restored\n', 'visible\n')


def test_capture_invalid_return_code_raises():
    with pytest.raises(ValueError):capture_cli_json(lambda argv: 'not-int', [])


@pytest.mark.parametrize('module_name,fn,binding,kwargs,expected', CAPTURES)
def test_milestone_capture_facades_call_only_stub_and_preserve_argv(monkeypatch, module_name, fn, binding, kwargs, expected):
    module = importlib.import_module(D+module_name)
    calls = []
    def stub(argv):calls.append(argv);print('[1,"가짜"]');return 3
    if binding:monkeypatch.setattr(module,binding,stub)
    target = getattr(module,fn)
    result = target(**kwargs) if kwargs else target(stub,expected) if binding is None else target(expected)
    assert result == (3,[1,'가짜'])
    assert calls == [expected]
    assert importlib.import_module('scripts.'+module_name) is module


@pytest.mark.parametrize('values,expected', [([], {'count':0.,'avg':0.,'p50':0.,'p95':0.,'max':0.}),
    ([-1,-2], {'count':0.,'avg':0.,'p50':0.,'p95':0.,'max':0.}),
    ([3], {'count':1.,'avg':3.,'p50':3.,'p95':3.,'max':3.}),
    ([0,10], {'count':2.,'avg':5.,'p50':0.,'p95':10.,'max':10.}),
    ([0,10,20,30], {'count':4.,'avg':15.,'p50':20.,'p95':30.,'max':30.}),
    ([9,1,-1,5], {'count':3.,'avg':5.,'p50':5.,'p95':9.,'max':9.}),
    (list(range(11)), {'count':11.,'avg':5.,'p50':5.,'p95':10.,'max':10.}),
    (list(range(31)), {'count':31.,'avg':15.,'p50':15.,'p95':28.,'max':30.})])
def test_numeric_nearest_index_and_round(values, expected):
    assert numeric_summary(values) == expected
    for name in ('generate_ops_diagnostic_report','reconstruct_incident_timeline'):
        assert importlib.import_module(D+name)._numeric_summary(values) == expected


def test_numeric_invalid_input_not_silently_swallowed():
    with pytest.raises(ValueError): numeric_summary(['bad'])


@pytest.mark.parametrize('value,expected', [(0,True),('0',True),('0.0',True),(1,False),('-1',False),
    (0.5,False),('0.5',False),('-0.5',False),('NaN',False),('Infinity',False),('1e-9999',False),
    ('ok',True),('success',True),('accepted',True),('error',False),('failed',False),('rejected',False),(None,None),('',None)])
def test_shared_and_both_broker_facades(value, expected):
    assert broker_code_success(value) is expected
    for name in ('generate_ops_diagnostic_report','query_trade_reason_chain'):
        assert importlib.import_module(D+name)._broker_code_success(value) is expected


def test_ops_report_fractional_codes_are_failures():
    module=importlib.import_module(D+'generate_ops_diagnostic_report')
    codes=['0','0.5','-0.5','1e-9999','NaN','Infinity',None]
    events=[{'stage':'execute_from_packet','event':'execution','payload':{'payload':{'broker_code':code}}} for code in codes]
    result=module._build_summary(events,day='2026-10-15')
    execution=result['execution']
    assert execution['broker_success_total']==1
    assert execution['broker_fail_total']==5
    assert execution['broker_unknown_total']==1


@pytest.mark.parametrize('name,fn,lazy', [('generate_ops_diagnostic_report','_iter_events',True),
    ('reconstruct_incident_timeline','_iter_rows',False),('run_m31_weekly_health_summary','_iter_jsonl',True)])
def test_jsonl_contamination_duplicates_order_and_streaming(tmp_path,monkeypatch,name,fn,lazy):
    read=getattr(importlib.import_module(D+name),fn)
    path=tmp_path/'events.jsonl'
    assert list(read(path))==[]
    path.write_text('',encoding='utf-8');assert list(read(path))==[]
    rows=[{'unicode':'가짜'},{'i':2},{'unicode':'가짜'}]
    path.write_text('\n \nnot-json\n[]\n2\n"text"\n'+'\n'.join(json.dumps(r,ensure_ascii=False) for r in rows),encoding='utf-8')
    calls=[];original=Path.open
    def tracked(self,*args,**kwargs):calls.append(self);return original(self,*args,**kwargs)
    monkeypatch.setattr(Path,'open',tracked)
    result=read(path)
    assert bool(calls) is (not lazy)
    assert list(result)==rows
    assert calls==[path]
    assert list(tmp_path.iterdir())==[path]


def test_archive_large_file_invalid_utf8_and_facades(tmp_path):
    path=tmp_path/'archive.jsonl';data=b'a'*(1024*1024+9)+b'\n\xff\n'+ '한글'.encode()+b'\nlast'
    path.write_bytes(data)
    for hash_fn,count_fn in [(sha256_file,line_count),*(
        (getattr(importlib.import_module(D+n),'_sha256_file'),getattr(importlib.import_module(D+n),'_line_count'))
        for n in ('check_log_archive_integrity','run_m29_log_archive_integrity_check'))]:
        assert hash_fn(path)==hashlib.sha256(data).hexdigest()
        assert count_fn(path)==4
        with pytest.raises(FileNotFoundError):hash_fn(tmp_path/'missing')
        with pytest.raises(FileNotFoundError):count_fn(tmp_path/'missing')
