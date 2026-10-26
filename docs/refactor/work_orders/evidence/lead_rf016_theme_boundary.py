"""RF-016 isolated, source-blob-pinned theme/avoid consumer smoke; no live effects."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import os
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
source = Path(os.environ.get('AGENTRA_RF016_SOURCE') or Path(__file__).resolve().parents[4] / 'libs/agents/strategist/context/theme_strength.py')
raw = source.read_bytes()
blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
if blob != '0268ed0e32b337f41606a6897b6a7bbbe23aad24':
    raise SystemExit('SOURCE_BLOB_MISMATCH')
spec = importlib.util.spec_from_file_location('rf016_pinned', source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
facade = SimpleNamespace(_to_float=lambda x, d: float(x) if x is not None else d,
                         _clamp=lambda x, lo, hi: min(hi, max(lo, x)))
cases = 0
def check(actual, expected):
    global cases
    if isinstance(actual, dict) and isinstance(expected, dict) and actual.keys() == expected.keys() and all(isinstance(x, (float, int)) for x in [*actual.values(), *expected.values()]):
        ok = all(math.isclose(actual[k], expected[k], abs_tol=1e-12) for k in actual)
    else:
        ok = actual == expected
    if not ok:
        raise AssertionError(f'{actual!r} != {expected!r}')
    cases += 1

fn = mod._theme_strength_map_r3_impl
themes = [' AI ', 'ai', '', None]
candidates = [{'symbol': 's1'}, {'symbol': ' S2 '}, {'symbol': ''}]
scores = {'AI': 50, 'ai': 0.25}
index = {'ai': {'S1', 's2'}}
before = json.dumps([themes, candidates, scores, sorted(index['ai'])], sort_keys=True)
check(fn(themes=themes, candidates=candidates, theme_scores=scores, theme_index=index, facade=facade), {'AI': 0.65, 'ai': 0.475})
check(json.dumps([themes, candidates, scores, sorted(index['ai'])], sort_keys=True), before)
for score, expected in [(200, 0.7), (-200, -0.7)]:
    check(fn(themes=['AI'], candidates=[], theme_scores={'AI': score}, theme_index={}, facade=facade), {'AI': expected})
check(fn(themes=['AI'], candidates=[{'symbol': 'S1'}], theme_scores={}, theme_index={'ai': {'s1'}}, facade=facade), {'AI': 0.3})
check(fn(themes=[None, ' '], candidates=[], theme_scores={}, theme_index={}, facade=facade), {})
facade._clamp = lambda x, lo, hi: 0.0
check(fn(themes=['AI'], candidates=[], theme_scores={'AI': 50}, theme_index={}, facade=facade), {'AI': 0.0})
try:
    fn(themes=['AI'], candidates=['not-mapping'], theme_scores={}, theme_index={}, facade=facade)
except AttributeError:
    cases += 1
else:
    raise AssertionError('malformed candidate exception swallowed')
avoid = mod._avoid_themes_r3_impl
for sentiment, playbook, count in [('bearish', 'reversal', 3), ('neutral', 'defensive', 3), ('neutral', 'reversal', 2), ('neutral', 'pullback', 1), ('neutral', 'normal', 1)]:
    check(len(avoid(market_sentiment=sentiment, playbook=playbook, facade=facade)), count)
if list(source.parent.rglob('*.pyc')):
    raise AssertionError('pyc artifact present in isolated source dir')
print(f'RF016_THEME_LEAD_OK cases={cases} source_blob={blob} mode={"normal" if __debug__ else "-O"} pyc=0')
