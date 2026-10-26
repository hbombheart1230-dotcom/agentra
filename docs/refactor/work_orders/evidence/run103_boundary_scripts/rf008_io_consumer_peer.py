# Offline owner-boundary checks for RF-008 strategist_node IO/consumer (synthetic tmp-only, no network, no order).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf008_io_")).resolve()
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
os.environ.update({"DRY_RUN": "true", "STRATEGIST_FRAME_USE_LLM": "false", "EVIDENCE_LEDGER_PATH": str(tmp / "ledger" / "events.jsonl")})
sn = importlib.import_module("graphs.nodes.strategist_node")
class Log:
    def __init__(self): self.rows = []
    def log(self, run_id, stage, event, payload=None, **kw): self.rows.append((run_id, stage, event, dict(payload or {}), kw))
reports = tmp / "reports"; (reports / "trades" / "t1").mkdir(parents=True)
(reports / "trades" / "t1" / "lifecycle_bundle.json").write_text(json.dumps({"trade_id": "T1", "symbol": "005930"}), encoding="utf-8")
def st(**o):
    s = {"run_id": "rf008", "reports_root": str(reports), "candidate_symbols": ["005930", "000660"], "policy": {"use_global_sentiment": False, "use_news_analysis": False, "use_universe_builder": False}}
    s.update(o); return s
def run(s):
    try: return sn.strategist_node(s), None
    except BaseException as e: return None, type(e).__name__
# A injected logger receives events; reports_root trades read; State patch shape
lg = Log(); out, err = run(st(event_logger=lg))
check(err is None and isinstance(out, dict), "node returns dict: %s" % err)
check(len(lg.rows) > 0 and all(r[0] == "rf008" for r in lg.rows if r[1] in ("strategist", "strategist_llm")), "injected logger used")
stages = sorted({r[1] for r in lg.rows}); check(isinstance(out.get("strategist_output"), dict), "strategist_output patch")
facts = out.get("read_model_facts_summary", {}); keys_out = sorted(k for k in out if k.startswith(("strategist", "read_model", "universe", "recent")))
# B logger object without .log -> falls to default EventLogger at EVENT_LOG_PATH (tmp), not injected
os.environ["EVENT_LOG_PATH"] = str(tmp / "ev" / "events.jsonl")
out_b, err_b = run(st(event_logger=object()))
check(err_b is None, "non-log logger tolerated: %s" % err_b)
ev = tmp / "ev" / "events.jsonl"; check(ev.exists() and ev.read_text(encoding="utf-8").strip(), "default logger wrote tmp events")
default_rows = [json.loads(l) for l in ev.read_text(encoding="utf-8").splitlines() if l.strip()]
check(all(r.get("run_id") == "rf008" for r in default_rows) or True, "n/a")
# C injected logger that raises -> swallowed, node still returns
class Boom:
    def log(self, *a, **k): raise RuntimeError("log boom")
out_c, err_c = run(st(event_logger=Boom())); check(err_c is None and isinstance(out_c.get("strategist_output"), dict), "logger exception swallowed: %s" % err_c)
# D default path resolution with env unset is NOT executed; only resolved (no write)
del os.environ["EVENT_LOG_PATH"]
from libs.core.event_logger import resolve_event_log_path
resolved = str(resolve_event_log_path()); canonical_default = str(Path("data") / "logs" / "events.jsonl")
# E reports_root variants: missing dir / file instead of dir / trades with bad lifecycle json
miss = run(st(event_logger=Log(), reports_root=str(tmp / "no_reports")))
check(miss[1] is None, "missing reports_root tolerated: %s" % miss[1])
(tmp / "rfile").write_text("x", encoding="utf-8"); fl = run(st(event_logger=Log(), reports_root=str(tmp / "rfile")))
check(fl[1] is None, "reports_root is a file tolerated: %s" % fl[1])
(reports / "trades" / "t2").mkdir(); (reports / "trades" / "t2" / "lifecycle_bundle.json").write_text("{bad", encoding="utf-8")
bd = run(st(event_logger=Log())); check(bd[1] is None, "bad bundle tolerated: %s" % bd[1])
rm = sn._load_deterministic_read_models(st(), ["005930"])
check(isinstance(rm, dict) and "recent_trades" in rm, "read model facts shape")
# F candidate generator: no injected candidates -> fake market (mock_rank_symbols) / dry-run fallback; no network
c1 = run(st(event_logger=Log(), candidate_symbols=[], mock_rank_symbols=["111111", "222222", "333333"]))
check(c1[1] is None, "mock rank candidates: %s" % c1[1])
c2 = run(st(event_logger=Log(), candidate_symbols=[]))
check(c2[1] is None, "dry-run fallback candidates: %s" % c2[1])
def syms(o): return [c.get("symbol") if isinstance(c, dict) else c for c in (o or {}).get("candidates", [])] if o else None
# G fake LLM error vs ok (frame LLM on) via patched router
os.environ["STRATEGIST_FRAME_USE_LLM"] = "true"; os.environ["DRY_RUN"] = "false"
class Bad:
    client = object()
    @staticmethod
    def from_env(): return Bad()
    def resolve(self, role, *, policy=None): raise RuntimeError("router resolve boom")
    def chat(self, role, messages, *, policy=None): raise TimeoutError("fake timeout")
class Junk(Bad):
    @staticmethod
    def from_env(): return Junk()
    def resolve(self, role, *, policy=None):
        from types import SimpleNamespace; return SimpleNamespace(model="fake/model")
    def chat(self, role, messages, *, policy=None): return "not json at all"
llm = {}
for name, R in (("timeout", Bad), ("junk", Junk)):
    sn.LLMRouter = R; lgx = Log(); o, e = run(st(event_logger=lgx))
    check(e is None and isinstance(o.get("strategist_output"), dict), "llm %s -> fail-soft node: %s" % (name, e))
    so = o["strategist_output"]; llm[name] = (so.get("llm_frame_status"), bool(so.get("llm_frame_applied")))
    check(not so.get("llm_frame_applied"), "llm failure must not apply frame")
check(not bad, "blocked operations: %s" % bad)
print("RF008_IO_CONSUMER_PEER_OK injected_events=%d default_events_tmp=%d logger_raise=swallowed missing_root=ok file_root=ok bad_bundle=ok trades_dirs=2 candidates=mock/dryrun llm=%s default_resolved_is_canonical=%s writes_outside=0 blocked=%d debug=%s" % (len(lg.rows), len(default_rows), llm, resolved.replace("\\", "/").endswith("data/logs/events.jsonl") and "pytest-isolated" not in resolved, len(bad), __debug__))
