"""RF-016 isolated new market-key-events boundary; no production effects."""
import ast
import copy
import importlib.util
import os
import hashlib
import sys
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(os.environ.get('AGENTRA_RF016_SOURCE') or Path(__file__).resolve().parents[4] / 'libs/agents/strategist/context/market_key_events.py')
sys.dont_write_bytecode = True
data = SOURCE.read_bytes()
blob_sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
if blob_sha != '3b09d58c283cec5e87792ada8214b361805e2668':
    raise SystemExit('RF016_SOURCE_BLOB_MISMATCH ' + blob_sha)
node = ast.parse(data.decode('utf-8'))
if not all(isinstance(x, (ast.Expr, ast.ImportFrom, ast.FunctionDef)) for x in node.body) or any(isinstance(x, (ast.Import, ast.Call)) for x in node.body):
    raise SystemExit('RF016_UNEXPECTED_MODULE_EFFECT')
spec = importlib.util.spec_from_file_location('rf016_key_events', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
f = module._key_events_r3_impl

facade = SimpleNamespace(_signal_score=lambda _: .25, _to_float=lambda x, default: float(x) if x is not None else default)
base = dict(state={}, global_signal={}, news_signal_map={}, market_regime='R', playbook='P', market_context_inputs={}, news_ctx={}, theme_strength={}, facade=facade)
count = 0

def check(condition, message):
    global count
    if not condition:
        raise SystemExit('RF016_KEY_EVENTS_FAIL ' + message)
    count += 1

r = f(**base)
check(len(r)==5 and r[0].startswith('global_sentiment score=0.250'), 'default-5-cap')
check(r[-2:]==['market_regime=R','playbook=P'], 'default-order')

v=copy.deepcopy({k:v for k,v in base.items() if k!='facade'});v['state']={'macro_events':['  EventA  ','EventB','EventA','']};before=copy.deepcopy(v)
r=f(**v,facade=facade)
check(r[:2]==['EventA','EventB'], 'dedup-trim')
check(v==before, 'state-no-mutation')

v={**base,'state':{'macro_events':'invalid','global_events':['G'],'major_events':['M']}}
check(f(**v)[0]=='G','fallback-precedence')
v={**base,'state':{'macro_events':[],'global_events':['G']}}
check(f(**v)[0].startswith('global_sentiment'), 'empty-macro-shadows')

facade._signal_score=lambda _: .75
check(f(**base)[0].startswith('global_sentiment score=0.750'), 'late-bound-facade')
facade._signal_score=lambda _: .25

v={**base,'global_signal':{'components':{'sp500_ret':.01,'nasdaq_ret':-.02,'dow_ret':0},'korea_indices':{'indices':{'KOSPI':{'current':2600,'previous_close':2590,'change_pct':.5},'KOSDAQ':{'current':850}}},'fear_index':{'level':20}},'theme_strength':{'T':2}}
r=f(**v)
check(len(r)==5 and r[1].startswith('us_indices sp500=1.00%') and r[2].startswith('korea_indices kospi=2600.00'), 'indices-branches')
check(r[3].startswith('fear_index vix=20.00'), 'fear-index')

try: f(**{**base,'theme_strength':{'bad':'not_a_float'}})
except ValueError: check(True,'theme-valueerror')
else: check(False,'theme-valueerror')
try: f(**{**base,'news_ctx':{'ok':'NaN'}})
except ValueError: check(True,'news-valueerror')
else: check(False,'news-valueerror')
try: f(**{**base,'state':None})
except AttributeError: check(True,'state-attributeerror')
else: check(False,'state-attributeerror')

print(f'RF016_KEY_EVENTS_LEAD_OK cases={count} blob=3b09d58c writes=0 network=0 order=0')
