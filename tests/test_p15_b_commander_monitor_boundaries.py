"""Scoped ABI, use-time seams, pure effects and non-vacuous mutation checks."""
import importlib
import inspect
import pickle
import socket
import subprocess
import sys
import builtins
from pathlib import Path
import pytest
from test_p15_b_commander_monitor_pure_parity import baseline, compare, observe, Seam, signal_case, PREFIX

OWNERS = [
    'libs.agents.commander.projections.decision_context_read_model',
    'libs.agents.commander.projections.cache_refresh_read_model']
MODULES = ['commander.decision_context_projection','commander.decision_overlay_projection',
    'commander.decision_rules_projection','commander.strategist_fingerprint','commander.strategist_refresh_decision',
    'monitor.signal_features','monitor.signal_score_projection','monitor.entry_cascade_projection',
    'monitor.entry_cascade_selection','monitor.entry_quality_projection']


@pytest.mark.parametrize('short', MODULES)
def test_existing_callable_inventory_signatures_and_real_module_identity(short):
    old=baseline(short);current=importlib.import_module(PREFIX+short)
    for name,value in vars(old).items():
        if inspect.isfunction(value) and value.__module__==old.__name__:
            assert hasattr(current,name)
            assert str(inspect.signature(value))==str(inspect.signature(getattr(current,name)))
    assert sys.modules[PREFIX+short] is current
    assert current.__name__==PREFIX+short


@pytest.mark.parametrize('reverse',[False,True])
def test_fresh_owner_runtime_import_orders_without_cycles(reverse):
    names=OWNERS+[PREFIX+m for m in MODULES]
    if reverse:names.reverse()
    code='import importlib,sys; [importlib.import_module(n) for n in sys.argv[1:]]'
    result=subprocess.run([sys.executable,'-B','-c',code,*names],capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr


def test_b2_shadow_coercion_is_resolved_at_use_time(monkeypatch):
    name='commander.strategist_fingerprint';current=importlib.import_module(PREFIX+name);old=baseline(name)
    monkeypatch.setattr(current,'shadow_float',lambda v:0.25)
    monkeypatch.setattr(old,'shadow_float',lambda v:0.25)
    assert current.score_bucket('ignored')==old.score_bucket('ignored')=='0.20-0.30'
    assert current.compact_post_scanner_candidate_row({'symbol':'A','score':9})==old.compact_post_scanner_candidate_row({'symbol':'A','score':9})


def test_original_namedtuple_pickle_and_alias_contract():
    mod=importlib.import_module(PREFIX+'monitor.entry_cascade_selection')
    result=mod.resolve_entry_order_price({}, {'price':100}, {},facade=Seam())
    assert type(result) is mod.OrderPriceResolution
    assert result._fields==('order_price','order_price_source')
    assert pickle.loads(pickle.dumps(result))==result
    state={'portfolio_preflight':{'blocked':False},'runtime_resilience_state':{'x':0},'runtime_fast_path':{'x':False}}
    ctx=importlib.import_module(PREFIX+'commander.decision_context_projection')
    value=ctx.decision_ctx_entry_capacity_available_market_regime(state,'mock','session','ok','active','',facade=Seam())
    assert value[5] is state['portfolio_preflight']
    assert value[7] is state['runtime_resilience_state']
    assert value[9] is state['runtime_fast_path']
    quality=importlib.import_module(PREFIX+'monitor.entry_quality_projection')
    decision,enforcement,factors,tactic=quality.entry_quality_quant_entry_decision_quant_entry_enforce({}, {}, {}, {}, {},facade=Seam())
    assert decision['snapshot'] is factors and enforcement['decision'] is decision


def test_pure_calls_do_not_open_files_network_or_processes(monkeypatch):
    mod=importlib.import_module(PREFIX+'commander.strategist_fingerprint')
    score=importlib.import_module(PREFIX+'monitor.signal_features')
    def forbidden(*args,**kw):raise AssertionError('pure projection attempted effect')
    with monkeypatch.context() as m:
        m.setattr(builtins,'open',forbidden);m.setattr(socket.socket,'connect',forbidden);m.setattr(subprocess,'Popen',forbidden)
        assert mod.compact_post_scanner_candidate_row({'symbol':'A','score':0})['score']==0
        assert score.signal_feature_asset_class_detected_breakout_distance_t(*signal_case(),facade=Seam())


MUTATIONS=[
    ('commander.decision_context_projection','decision_ctx_entry_capacity_available_market_regime',0,
     'decision_context_readout',[{},'mock','session','ok','active','']),
    ('commander.strategist_fingerprint','compact_post_scanner_candidate_row',1,
     'compact_post_scanner_candidate_row',[{'symbol':'A','score':0}]),
]


@pytest.mark.parametrize('short,name,owner_index,target,args',MUTATIONS)
def test_base_first_parity_rejects_wrong_owner_result(monkeypatch,short,name,owner_index,target,args):
    current=importlib.import_module(PREFIX+short)
    expected=observe(baseline(short),name,args)
    assert observe(current,name,args)==expected  # Baseline positive first, before perturbation.
    fn=getattr(importlib.import_module(OWNERS[owner_index]),target)
    def wrong(*args,**kwargs):return {'wrong_owner_result':True}
    with monkeypatch.context() as m:
        m.setattr(fn,'__code__',wrong.__code__)
        assert observe(current,name,args)!=expected  # The real consumer must observe/reject the corruption.
    assert observe(current,name,args)==expected


@pytest.mark.parametrize('threshold',[0.5,0.9])
def test_b2_threshold_monkeypatch_remains_use_time(monkeypatch,threshold):
    current=importlib.import_module(PREFIX+'commander.strategist_refresh_decision')
    old=baseline('commander.strategist_refresh_decision')
    monkeypatch.setattr(current,'PRE_BUY_STRATEGIST_REFRESH_READINESS_THRESHOLD',threshold)
    monkeypatch.setattr(old,'PRE_BUY_STRATEGIST_REFRESH_READINESS_THRESHOLD',threshold)
    state={'monitor_output':{'intent_side':'NOOP','entry_transition_readiness_score':0.8}}
    assert current._monitor_entry_readiness_context(state)==old._monitor_entry_readiness_context(state)
    assert current._monitor_entry_readiness_context(state)['actionable'] is (0.8>=threshold)


@pytest.mark.parametrize('name', ['signal_features','signal_score_projection','signal_features_breakout_volume_gate',
    'entry_cascade_projection','entry_cascade_selection','entry_quality_projection'])
def test_stage_blocked_monitor_sources_are_exactly_preserved(name):
    # Do not teach the old gate to accept this stage. Preserve the exact BASE blob.
    from test_p15_b_commander_monitor_pure_parity import ROOT, BASE
    path='libs/runtime/monitor/'+name+'.py'
    expected=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
    assert (ROOT/path).read_bytes().replace(b'\r\n',b'\n')==expected.replace(b'\r\n',b'\n')
