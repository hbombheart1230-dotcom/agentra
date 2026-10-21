"""Compare owned projections with immutable d7ab8294 source, not candidate oracles."""
import copy
import importlib
import inspect
import json
import subprocess
import sys
import types
from functools import lru_cache
from pathlib import Path
import pytest

BASE = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
ROOT = Path(__file__).resolve().parents[1]
PREFIX = "libs.runtime."


@lru_cache(None)
def baseline(short):
    name = PREFIX + short
    source = subprocess.check_output(['git','show',BASE+':'+name.replace('.','/')+'.py'],cwd=ROOT).decode('utf-8')
    module = types.ModuleType('_p15_base_'+short.replace('.','_'))
    sys.modules[module.__name__] = module
    exec(compile(source, '<pinned '+short+'>', 'exec'), module.__dict__)
    # Imported B2 helpers must also come from BASE, never from the new Owner.
    if short in {'commander.strategist_fingerprint','commander.strategist_refresh_decision'}:
        old_cache=baseline('commander.strategist_cache_decision')
        for key in ('portfolio_open_position_count','runtime_now_epoch','strategist_cache_payload'):
            if key in module.__dict__:setattr(module,key,getattr(old_cache,key))
    if short=='commander.strategist_refresh_decision':
        old_fp=baseline('commander.strategist_fingerprint')
        for key in ('shadow_float','post_scanner_candidate_snapshot','post_scanner_selected_symbol',
                    'assess_cached_strategist_input_drift','runtime_float'):
            if key in module.__dict__:setattr(module,key,getattr(old_fp,key))
    return module


def encoded(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':'),default=lambda x:vars(x) if isinstance(x,types.SimpleNamespace) else repr(x))


class Seam:
    from collections.abc import Mapping

    def __init__(self):self.calls=[]
    def __getattr__(self,name):
        fixed={'_OPENING_GAP_CHASE_MIN_PCT':0.03,'_OPENING_GAP_CHASE_WINDOW_MINUTES':30,
               '_BREAKOUT_CHASE_VOLUME_GATE_MIN_EXTENDED_PCT':0.02,
               '_LOWER_VWAP_REBOUND_MIN_DISTANCE_PCT':-0.03,'_LOWER_VWAP_REBOUND_MAX_DISTANCE_PCT':0.01,
               '_LOWER_VWAP_REBOUND_MIN_CONFIDENCE':0.55}
        if name in fixed:return fixed[name]
        def call(*args,**kw):
            self.calls.append((name,copy.deepcopy(args),copy.deepcopy(kw)))
            if name=='_build_shadow_assessment_summary':return {}
            if name=='_resolve_risk_max_positions':return 3
            if name=='_derive_commander_market_regime':return ('neutral',False)
            if name=='_build_commander_entry_control':return {'mode':'baseline'}
            if name=='_is_trueish':return str(args[0]).lower() in {'true','1'}
            if name=='_resolve_entry_candidate_cascade_config':return dict(args[0])
            if name in {'_to_float','normalize_deviation_pct'}:
                try:return float(args[0] or 0)
                except (TypeError,ValueError):return 0.0
            if name=='_clamp_score':return min(1.0,max(0.0,float(args[0])))
            if name=='_range_threshold_score':return 0.5
            if name=='build_factor_snapshot_from_monitor_entry':return {'factors':dict(args[0])}
            if name=='build_entry_quant_decision':return {'decision':'OBSERVE','snapshot':kw['factor_snapshot']}
            if name=='build_entry_quant_enforcement':return {'enforced':False,'decision':args[0]}
            raise AssertionError('unexpected seam '+name)
        return call


def observe(module,name,args,kwargs=None):
    args=copy.deepcopy(args);kwargs=copy.deepcopy(kwargs or {})
    seam=Seam()
    if 'facade' in inspect.signature(getattr(module,name)).parameters:kwargs['facade']=seam
    try:
        value=getattr(module,name)(*args,**kwargs)
        result=('return',value)
    except Exception as exc:result=('error',type(exc).__name__,str(exc))
    kwargs.pop('facade',None)
    return encoded((result,args,kwargs,seam.calls))


def compare(short,name,args,kwargs=None):
    old=baseline(short);current=importlib.import_module(PREFIX+short)
    assert str(inspect.signature(getattr(old,name)))==str(inspect.signature(getattr(current,name)))
    expected=observe(old,name,args,kwargs)
    assert observe(current,name,args,kwargs)==expected
    return expected


@pytest.mark.parametrize('phase,path,status', [('session','active','ok'),('preopen','cached','blocked'),('closeout','cached','preflight_blocked')])
@pytest.mark.parametrize('state', [{}, {'portfolio_snapshot':{'positions':[{'symbol':'A'}]},'strategist_output':{'market_regime_rail':'risk_off','macro_stress_overlay':{'active':False,'stress_flags':['x']}}}, {'portfolio_preflight':{'blocked':True},'market_regime_rail':'risk_on','runtime_resilience_state':{'degrade_mode':'safe'}}])
def test_b1_context_exact_tuple_key_order_and_callbacks(phase,path,status,state):
    compare('commander.decision_context_projection','decision_ctx_entry_capacity_available_market_regime',[state,'mock',phase,status,path,'한글 note'])


@pytest.mark.parametrize('cached,refresh,positions', [({},False,0),({'x':0},False,0),({'x':False},True,2)])
def test_b1_cache_decision_view_alias_and_order(cached,refresh,positions):
    compare('commander.decision_overlay_projection','decision_overlay_blocker_counts_monitor_last_states',
            [700,600,cached,refresh,{'persisted_state':{'monitor_last_state_by_symbol':{'A':{'allowed':False}}}},positions,positions==0])


@pytest.mark.parametrize('feedback', [{}, {'dominant_blocker':'volume','failure_streak':0,'avg_distance_to_ready':0.0}, {'blocker_count':'broken'}])
def test_b1_feedback_context_and_error_parity(feedback):
    compare('commander.decision_rules_projection','decision_rules_adaptive_feedback_allowed_adaptive_polic',
            [{'volume':2},4,0.8,1,{'mock_monitor_feedback':feedback},'neutral','','balanced',0,{},[],{}, {},3,{},{}])


@pytest.mark.parametrize('value', [None,'',0,False,'0.36','bad',-1.5])
@pytest.mark.parametrize('name', ['runtime_float','shadow_float','shadow_text','score_bucket','rank_bucket'])
def test_b2_normalization_and_exceptions(name,value):
    compare('commander.strategist_fingerprint',name,[value])


@pytest.mark.parametrize('row', [{}, {'symbol':' a ','score_total':0,'confidence':False,'rank':1,'theme':'한글/테마'},
    {'code':'B','rank':3,'score_breakdown':{'zero':0,'text':'한글'},'scanner_chart_fit_components':{'x':False}},
    {'ticker':'C','score_total':'bad','final_score':0.75,'themes':['A','B','A'],'status':'hold'}, None, {'symbol':'D','rank':[]}])
def test_b2_candidate_projection_priority_unicode_and_no_input_mutation(row):
    for name in ('compact_post_scanner_candidate_row','candidate_theme_tokens','candidate_chart_fit_value'):
        compare('commander.strategist_fingerprint',name,[row])


@pytest.mark.parametrize('state', [{},{'selected':{'symbol':'a','_monitor_synthetic_selected':True}},
    {'selected':{'symbol':'a'},'monitor_output':{'intent_side':'BUY','entry_transition_readiness_score':0}},
    {'monitor':{'intent_side':'WAIT'},'monitor_entry_decision_detail':{'transition_trace':{'became_ready_this_cycle':False}}}])
def test_b2_readiness_and_selection(state):
    compare('commander.strategist_fingerprint','post_scanner_selected_symbol',[state])
    compare('commander.strategist_refresh_decision','_monitor_entry_readiness_context',[state])


@pytest.mark.parametrize('payload', [{},{'candidate_hints':['a','a','b'],'candidate_symbols_hint':['c'],'candidates':[{'symbol':'d'},None]}, {'candidates':False}])
def test_b2_cache_hint_order(payload):
    compare('commander.strategist_refresh_decision','_cached_candidate_hints',[payload])


def signal_case():
    return [0.8,0.4,0.5,100.0,101.0,0.01,0.01,100.0,-0.03,100.0,99.0,0.04,True,False,1.5,
            types.SimpleNamespace(volume_ratio_min=1.2),0.002,{'etf_deviation_pct':0,'asset_class':'etf'}]


@pytest.mark.parametrize('price', [0.0,99.0,101.0])
def test_b3_score_outputs_and_use_time_helpers(price):
    args=signal_case();args[4]=price
    result=compare('monitor.signal_features','signal_feature_asset_class_detected_breakout_distance_t',args)
    assert json.loads(result)[0][0]=='return'


@pytest.mark.parametrize('control', [{},{'max_priority_rank':0,'max_runner_ups':0,'cascade_enabled':False},
    {'max_priority_rank':5,'cascade_allowed_reasons':['wait'],'source':'한글'}, {'max_priority_rank':'bad'}])
def test_b4_cascade_metadata_not_state_or_intent_mutation(control):
    compare('monitor.entry_cascade_projection','entry_cascade_entry_candidate_cascade_entry_cascade_co',
            [{'symbol':'A'},control,1,3,{'B'},{'C'}])


@pytest.mark.parametrize('entry,selected,sizing', [({}, {}, {}),({'entry_cost_filter':{'price':100}},{'price':99},{'price':98}),
    ({'metrics':{'current_price':0,'price':101}},{'price':False},{'price':102}), ({},{'price':'bad'},{'price':103})])
def test_b4_order_price_precedence_and_namedtuple_abi(entry,selected,sizing):
    compare('monitor.entry_cascade_selection','resolve_entry_order_price',[entry,selected,sizing])


@pytest.mark.parametrize('plan,frame', [({},{}),({'playbook':'pullback'},{'tactical_strategy':'한글'}),
    ({'selected_playbook':'','tactical_strategy':False},{'playbook':'breakout'})])
def test_b4_quant_readout_callback_order_and_aliases(plan,frame):
    compare('monitor.entry_quality_projection','entry_quality_quant_entry_decision_quant_entry_enforce',[plan,frame,{'allowed':False},{'symbol':'A'},{}])


@pytest.mark.parametrize('breakout,pullback', [(True,False),(False,True),(False,False)])
def test_b3_threshold_margin_json_keys_order_and_zero_observations(breakout,pullback):
    volume=types.SimpleNamespace(adjusted=False,adjustment_reason='none',max_reference_volume=110,spike_skew_ratio=1.2)
    policy=types.SimpleNamespace(volume_ratio_min=1.2)
    args=[1.5,1.5,100,90,0.01,-0.03,0.04,0.01,0.005,0.02,0.01,0.002,0.02,0.01,30,
          0,'provided','etf','neutral',volume,False,True,False,False,False,False,False,
          False,False,False,False,policy,100,101,0,0.6,breakout,pullback]
    result=compare('monitor.signal_score_projection','signal_score_entry_condition_path_entry_condition_pat',args)
    assert json.loads(result)[0][0]=='return'


@pytest.mark.parametrize('row,state', [({'expected_edge_pct':0},{}),({'expected_move_pct':-0.01},{}),
    ({},{'monitor_output':{'intent_side':'BUY'}}),({'cost_adjusted_edge_pct':'bad'},{'monitor':{'reason':'cost_below'}})])
def test_b2_edge_buckets_and_entry_gate_priority(row,state):
    compare('commander.strategist_fingerprint','candidate_edge_bucket',[row,state])
    compare('commander.strategist_fingerprint','entry_gate_bucket',[state])


@pytest.mark.parametrize('score', [0,0.79,0.80,0.87])
def test_b2_noop_readiness_threshold_uses_original_runtime_constant(score):
    result=compare('commander.strategist_refresh_decision','_monitor_entry_readiness_context',
                   [{'monitor_output':{'intent_side':'NOOP','entry_transition_readiness_score':score}}])
    assert json.loads(result)[0][0]=='return'
