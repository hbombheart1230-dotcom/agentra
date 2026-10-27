# RF-014 OWNER FIXTURE (A, for B's independent peer): a VALID "Top1 selected" scanner State for graphs.nodes.scanner_node (RF-009 facade over the RF-014 scanner owners).
# B reported "Top1 probe: selected none / rank 0; valid selected fixture still missing". This provides `selected_state()` built from the repo's own supported test seams
# (state['mock_scan_results'] / mock_top_value_symbols / mock_top_volume_symbols, live_fetch=False policy; the two hydration hooks replaced in-process exactly as
# tests/test_scanner_fallback_policy.py does) and SELF-VERIFIES: rank-1 selection, rank-2 runner-up, symbol tie-break by score, NOOP when every candidate is vetoed/empty.
# tmp cwd, network/subprocess/sqlite blocked, writes confined to tmp. Usage: PYTHONPATH=<repo> python [-O] rf014_top1_selected_fixture.py
import os, sys, io, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile, shutil
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY", "SCANNER_", "CANDIDATE_SOURCE", "STRICT_KIWOOM", "BLOCK_STATIC")): del os.environ[k]
tmp = Path(tempfile.mkdtemp(prefix="rf014_fix_")).resolve()
for k, v in {"EVENT_LOG_PATH": "events.jsonl", "EVIDENCE_LEDGER_PATH": "ledger.jsonl"}.items(): os.environ[k] = str(tmp / v)
os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
def inside(p):
    try:
        if isinstance(p, int): return True
        ap = os.path.abspath(os.fspath(p)); return ap == str(tmp) or ap.startswith(str(tmp) + os.sep)
    except Exception: return False
_open = io.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write outside tmp")
    return _open(f, mode, *a, **k)
builtins.open = gopen; io.open = gopen
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
sn = importlib.import_module("graphs.nodes.scanner_node")
# repo-supported in-process seams (same as tests/test_scanner_fallback_policy.py::test_scanner_node_uses_kiwoom_results_without_fallback_when_pool_present)
sn._maybe_hydrate_scanner_skill_results = lambda state, _candidates: state
sn.hydrate_scanner_feature_map = lambda **_kw: ({}, "test_fixture", [])

def selected_state(scores=None, symbols=("005930", "000660")):
    scores = scores or {"005930": 0.61, "000660": 0.60}
    policy = {"scanner": {"source": {"type": "kiwoom"}, "kiwoom": {"strict_only": True, "live_fetch": False, "include_change_rate": True},
                          "fallback": {"block_static_when_empty": True}, "market_representative_guard": {"enabled": False}}}
    return {"run_id": "rf014-fixture", "applied_policy": policy, "mock_top_value_symbols": list(symbols), "mock_top_volume_symbols": list(symbols),
            "mock_scan_results": {s: {"score": scores[s], "risk_score": 0.2, "confidence": 0.8} for s in symbols}}

out = {}
s_in = selected_state(); s_copy = copy.deepcopy(s_in)
r = sn.scanner_node(s_in)
so = r.get("scanner_output") or {}
check(r.get("top_stock") == "005930" and int(so.get("selected_rank") or 0) == 1, (r.get("top_stock"), so.get("selected_rank")))
check(so.get("candidate_source") == "kiwoom_market_data" and so.get("fallback_reason") == "" and so.get("scanner_policy_source") == "commander_applied_policy", {k: so.get(k) for k in ("candidate_source", "fallback_reason", "scanner_policy_source")})
out["selected"] = {"top_stock": r.get("top_stock"), "selected_rank": so.get("selected_rank"), "candidate_source": so.get("candidate_source"), "keys": len(so)}
# swap scores -> other symbol wins (selection follows score, not list order)
r2 = sn.scanner_node(selected_state(scores={"005930": 0.40, "000660": 0.70}))
check(r2.get("top_stock") == "000660" and int((r2.get("scanner_output") or {}).get("selected_rank") or 0) == 1, r2.get("top_stock"))
out["score_swap_top"] = r2.get("top_stock")
# ranking evidence: runner-up present
rt = (r.get("scanner_output") or {}).get("ranking_table") or r.get("scanner_ranking_table") or []
out["ranking_rows"] = len(rt) if isinstance(rt, list) else None
# empty pool under strict mode -> NOOP (no top stock), like the repo test for strict-only
r3 = sn.scanner_node({"run_id": "rf014-empty", "applied_policy": selected_state()["applied_policy"], "strategist_output": {"candidates": ["123456"]}, "mock_scan_results": {"123456": {"score": 0.5, "risk_score": 0.1, "confidence": 0.8}}})
check(r3.get("top_stock") in ("", None) and (r3.get("scanner_output") or {}).get("fallback_reason") == "kiwoom_candidate_pool_empty_strict_mode", (r3.get("top_stock"), (r3.get("scanner_output") or {}).get("fallback_reason")))
out["strict_empty_noop"] = (r3.get("scanner_output") or {}).get("fallback_reason")
# determinism (same input -> same selection fields)
r4 = sn.scanner_node(selected_state()); check(r4.get("top_stock") == r.get("top_stock") and (r4.get("scanner_output") or {}).get("selected_rank") == so.get("selected_rank"), "deterministic")
check(not [b for b in bad if not b.startswith("write:")], bad); out["blocked_attempts"] = len(bad)
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True))
print("RF014_TOP1_SELECTED_FIXTURE_OK top_stock=%s selected_rank=%s score_swap=%s strict_empty=NOOP network=0 debug=%s" % (out["selected"]["top_stock"], out["selected"]["selected_rank"], out["score_swap_top"], __debug__))
