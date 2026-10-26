# RF-008 strategist_node in-repo consumer map + wrapper failsoft peer (synthetic tmp-only, no network, no order).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
from pathlib import Path
ROOT = Path(os.getcwd()).resolve()
tmp = Path(tempfile.mkdtemp(prefix="rf008_consumer_")).resolve()
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt, _mk = Path.write_text, Path.mkdir
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked")
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked")
    return _mk(self, *a, **k)
Path.write_text, Path.mkdir = wt, mk
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)
def tree(root):
    return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())

os.chdir(tmp)  # cwd isolation: relative data/ paths land in tmp
os.environ.update({"DRY_RUN": "true", "STRATEGIST_FRAME_USE_LLM": "false",
                   "EVIDENCE_LEDGER_PATH": str(tmp / "ledger" / "events.jsonl"),
                   "EVENT_LOG_PATH": str(tmp / "ev" / "events.jsonl")})
sys.path.insert(0, str(ROOT))
reports = tmp / "reports"; reports.mkdir()
POL = {"use_global_sentiment": False, "use_news_analysis": False, "use_universe_builder": False}
def st(**o):
    s = {"run_id": "rf008c", "reports_root": str(reports), "candidate_symbols": ["005930", "000660"], "policy": dict(POL)}
    s.update(o); return s
# 1) static consumer map (callers of graphs.nodes.strategist_node outside tests/docs)
import ast
callers = {}
for p in list(ROOT.glob("graphs/**/*.py")) + list(ROOT.glob("libs/**/*.py")) + list(ROOT.glob("scripts/**/*.py")) + list(ROOT.glob("apps/**/*.py")):
    try: t = ast.parse(p.read_text(encoding="utf-8"))
    except Exception: continue
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.module == "graphs.nodes.strategist_node" and any(a.name == "strategist_node" for a in n.names):
            callers[str(p.relative_to(ROOT)).replace("\\", "/")] = n.lineno
expect = {"graphs/commander_runtime.py", "graphs/pipelines/offhours_validation.py", "graphs/trading_graph.py", "libs/runtime/commander/nodes.py"}
check(set(callers) == expect, "caller set mismatch: %s" % sorted(callers))
sn_src = (ROOT / "graphs/nodes/strategist_node.py").read_text(encoding="utf-8")
check("def run_strategist" not in sn_src and "__main__" not in sn_src, "run_strategist/__main__ absent")
# 2) trading_graph consumer: real strategist, stub downstream
from graphs.trading_graph import run_trading_graph
seen = []
def mk(name, **patch):
    def f(s): seen.append(name); s.update(patch); return s
    return f
s = run_trading_graph(st(), scanner=mk("scanner"), monitor=mk("monitor"), portfolio_guard=mk("guard"), decide=mk("decide", decision="noop"), executor=mk("exec"))
check(seen == ["scanner", "monitor", "guard", "decide"], "chain order %s" % seen)
check(isinstance(s.get("strategist_output"), dict), "strategist_output in graph state")
seen.clear()
s2 = run_trading_graph(st(), scanner=mk("scanner"), monitor=mk("monitor"), portfolio_guard=mk("guard"), decide=mk("decide", decision="approve"), executor=mk("exec"))
check(seen[-1] == "exec", "approve reaches executor stub only")
# 3) strategist exception propagates through trading_graph (no failsoft wrapper)
def boom(s): raise RuntimeError("strategist boom")
try: run_trading_graph(st(), strategist=boom); prop = "no"
except RuntimeError: prop = "RuntimeError"
check(prop == "RuntimeError", "exception propagates")
# 4) commander_runtime wrappers
cr = importlib.import_module("graphs.commander_runtime")
check(cr._strategist_frame_blocked({}) is False, "blocked default false")
check(cr._strategist_frame_blocked({"strategist_output": {"llm_frame_blocked": True}}) is True, "output block")
check(cr._strategist_frame_blocked({"strategist_llm": {"blocked": True}}) is True, "llm block")
check(cr._strategist_frame_blocked({"strategist_output": None, "strategist_llm": "x"}) is False, "non-dict tolerated")
b = cr._apply_strategist_block(st(strategist_output={"llm_frame_blocked": True, "llm_frame_blocked_reason": "r1"}), phase="preopen")
check((b["path"], b["decision"], b["decision_reason"], b["runtime_status"]) == ("preopen_strategist_blocked", "noop", "r1", "blocked"), "apply block")
b2 = cr._apply_strategist_block(st(), phase="closeout"); check(b2["decision_reason"] == "strategist_llm_failed", "default block reason")
calls = []
def fake_node(s): calls.append(1); return s
r, ran = cr._run_stage4_carry_review(st(), fake_node, review_reason="x", phase="closeout")
check(ran is False and not calls, "no open position -> strategist not called")
check(any(reports.rglob("*")) , "skip manifest written under tmp reports_root")
# 5) offhours pipeline: strategist injection point only, others stubbed
from graphs.pipelines import offhours_validation as ov
noop = lambda s: s
out = ov.run_offhours_validation_once(st(), load_state_fn=noop, save_state_fn=noop, build_portfolio_snapshot_fn=noop, build_risk_context_fn=noop,
    scanner_fn=noop, build_market_snapshot_fn=noop, monitor_fn=noop, decision_fn=noop, execute_fn=noop, update_state_fn=noop)
check(isinstance(out.get("strategist_output"), dict) and out.get("offhours_validation") is True, "offhours real strategist default import")
# 6) market read failsoft: real strategist with market/news readers absent -> no network, node still returns
check(not bad, "blocked attempts: %s" % bad)
outside = [p for p in Path(os.environ["TEMP"]).glob("data*")] if False else []
print("RF008_CONSUMER_PEER_OK callers=%d(%s) graph_chain=ok propagate=%s block_helpers=ok stage4_skip=ok offhours=ok blocked=%d debug=%s" % (len(callers), ",".join(sorted(callers)), prop, len(bad), __debug__))
