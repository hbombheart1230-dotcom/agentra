import sys, os, socket, subprocess, tempfile, json
root = sys.argv[1]
os.chdir(tempfile.mkdtemp()); sys.path.insert(0, root)
def _blk(*a, **k): raise RuntimeError("blocked")
socket.socket.connect = _blk; subprocess.Popen = _blk
import builtins
_open = builtins.open
def sopen(f, mode="r", *a, **k):
    if any(c in mode for c in "wax+"): raise RuntimeError("write blocked")
    return _open(f, mode, *a, **k)
builtins.open = sopen
from libs.reporting import trade_story_pipeline as fac
from libs.reporting.trade_story_assembly_parts import lifecycle_bundle as owner
kw = dict(day="2000-01-01", trade_id="T1", run_id="R1", symbol="005930",
  lifecycle={"entry": {"qty": 1}, "holding": {"holding_events": [{"a": 1}, "x"]}, "exit": {"reason_human": "tp"}, "summary": {}},
  strategist_summary={}, scanner_summary={}, monitor_summary={}, commander_summary={},
  story_input={}, diagnostics={}, canonical_refs={}, llm_refs={}, artifact_links={})
# 1 facade == owner(deps from facade)
a = fac.build_lifecycle_bundle(**kw)
b = owner.build_lifecycle_bundle(**kw, deps=fac._story_assembly_deps())
a.pop("generated_at", None); b.pop("generated_at", None)
for d in (a, b):
    for k in list(d):
        if k.endswith("_at") or k == "created_at": d.pop(k)
assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
# 2 use-time monkeypatch seam on facade reaches owner
orig = fac.compute_evidence_completeness
calls = []
fac.compute_evidence_completeness = lambda si: (calls.append(1), {"completeness_score": 0.77})[1]
c = fac.build_lifecycle_bundle(**kw)
assert calls and json.dumps(c, default=str).count("0.77") >= 1, c
fac.compute_evidence_completeness = orig
# 3 dep exception propagates, no swallow
def boom(si): raise ValueError("dep")
fac.compute_evidence_completeness = boom
try: fac.build_lifecycle_bundle(**kw); raise SystemExit("no raise")
except ValueError: pass
fac.compute_evidence_completeness = orig
# 4 input not mutated
import copy
kw2 = copy.deepcopy(kw); fac.build_lifecycle_bundle(**kw2); assert kw2 == kw
# 5 owner never imports facade
import inspect
assert "trade_story_pipeline" not in inspect.getsource(owner)
print("RF029_FACADE_BUNDLE_OK keys=%d" % len(a))
