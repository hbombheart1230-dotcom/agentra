"""RF-016 pure symbol read-model boundary, exact blob, no live dependencies."""
import ast
import copy
import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(os.environ.get('AGENTRA_RF016_SOURCE') or Path(__file__).resolve().parents[4] / 'libs/agents/strategist/context/symbol_read_models.py')
sys.dont_write_bytecode = True
raw = SOURCE.read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
if blob != '91316b5136d1a14a74eb0dc809e979f0f51c04c6':
    raise SystemExit('RF016_SOURCE_BLOB_MISMATCH ' + blob)
if any(isinstance(n, (ast.Import, ast.Call)) for n in ast.parse(raw).body):
    raise SystemExit('RF016_TOP_LEVEL_EFFECT')
spec = importlib.util.spec_from_file_location('rf016_symbol_models', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

f = SimpleNamespace(
    _compact_scalar_mapping_for_llm=lambda d, allowed_keys, max_text_len: {k:d[k] for k in allowed_keys if k in d},
    _compact_pattern_rows_for_llm=lambda x, limit: list(x or [])[:limit],
    _compact_trade_read_model_for_llm=lambda row: {'id':row['id']} if isinstance(row, dict) and 'id' in row else {},
    _compact_symbol_read_model_for_llm=lambda row: {'symbol':row['symbol']} if isinstance(row, dict) and 'symbol' in row else {},
    _operator_summary_for_llm=lambda x: {'summary':x} if x else {},
    _round_optional=lambda v, nd: round(float(v), nd) if v is not None else None,
    _stage_float=lambda v, default: float(v) if isinstance(v, (int,float)) else default,
    _clip_text_for_llm=lambda v, max_len: str(v)[:max_len],
    _compact_candidate_context_for_refresh=lambda row: mod._compact_candidate_context_for_refresh_r3_impl(row, facade=f),
    stable_evidence_id=lambda prefix, src: prefix+'-fake',
)
count=0
def check(ok, label):
    global count
    if not ok: raise SystemExit('RF016_SYMBOL_MODELS_FAIL '+label)
    count+=1

v={'symbol':'005930','trade_count':4,'unlisted':'secret','repeated_failure_pattern':[1,2,3,4],'recent_success_pattern':[5,6,7,8],'data_quality':{'status':'OK','ignored':'x'}}
old=copy.deepcopy(v)
r=mod._compact_symbol_read_model_for_llm_r3_impl(v, facade=f)
check('unlisted' not in r and r['symbol']=='005930','allowed-keys')
check(r['repeated_failure_pattern']==[1,2,3] and r['recent_success_pattern']==[5,6,7],'pattern-limit')
check(r['data_quality']=={'status':'OK'} and v==old,'data-quality-immutable')
check(mod._compact_symbol_read_model_for_llm_r3_impl(None,facade=f)=={},'nondict-empty')

v={'recent_trades':[{'id':i} for i in range(5)],'symbol_patterns':{str(i):{'symbol':str(i)} for i in range(7)},'daily_summary':'daily'}
old=copy.deepcopy(v)
r=mod._compact_read_model_facts_for_llm_r3_impl(v,facade=f)
check(r['recent_trade_count']==5 and len(r['recent_trades'])==3,'recent-trades-cap')
check(r['symbol_pattern_count']==7 and len(r['symbol_patterns'])==5,'symbol-pattern-cap')
check(r['daily_summary']=={'summary':'daily'} and v==old,'daily-summary-immutable')

v={'symbol':'005930','score_breakdown':{'a':1.23456,'b':'missing','c':3,'d':4,'e':5,'f':6},'ignored':'x'}
old=copy.deepcopy(v)
r=mod._compact_candidate_context_for_refresh_r3_impl(v,facade=f)
check('ignored' not in r and len(r['score_breakdown'])==5,'score-breakdown-cap')
check(r['score_breakdown']['a']==1.2346 and r['score_breakdown']['b']=='missing' and v==old,'score-fallback-immutable')
check(mod._compact_candidate_context_for_refresh_r3_impl([],facade=f)=={},'candidate-nondict')

v={'scanner_runner_ups':[{'symbol':str(i)} for i in range(6)],'scanner_top_candidates':[{'symbol':str(i)} for i in range(6)],'selected_symbol_memory':{'status':'OK','symbol':'005930','trade_count':'3','override_eligible':1,'operator_summary':'ok'},'untouched':{'nested':1}}
old=copy.deepcopy(v)
r=mod._slim_refresh_context_for_llm_r3_impl(v,facade=f)
check(r['feedback_id']=='feedback-fake' and len(r['scanner_runner_ups'])==3 and len(r['scanner_top_candidates'])==4,'refresh-caps')
check(r['selected_symbol_memory']['trade_count']==3 and r['selected_symbol_memory']['override_eligible'] is True,'memory-coercion')
check(v==old and r['untouched'] is v['untouched'],'shallow-state-alias-observed')
try: mod._slim_refresh_context_for_llm_r3_impl({'selected_symbol_memory':{'trade_count':'invalid'}},facade=f)
except ValueError: check(True,'invalid-memory-exception')
else: check(False,'invalid-memory-exception')

print(f'RF016_SYMBOL_MODELS_LEAD_OK cases={count} blob=91316b51 writes=0 network=0 order=0')
