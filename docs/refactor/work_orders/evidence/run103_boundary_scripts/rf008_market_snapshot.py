# RF-008 downstream market read: graphs.nodes.build_market_snapshot with injected fake readers (State/exception/fail-soft).
# SAFETY: KiwoomPriceReader.from_env is replaced by a trap (the real one builds an HTTP client + token flow); sockets/subprocess/sqlite/writes blocked.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "MOCK_PRICE")): del os.environ[k]
root = Path("/tmp/rf008_ms_fixed"); shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "events.jsonl"); os.chdir(root)
import ssl, http.client
bms = importlib.import_module("graphs.nodes.build_market_snapshot")
from libs.read.snapshot_models import MarketSnapshot
traps = []
def trap_from_env(*a, **k): traps.append("KiwoomPriceReader.from_env"); raise RuntimeError("TRAP: real Kiwoom reader construction blocked")
bms.KiwoomPriceReader.from_env = classmethod(lambda cls: trap_from_env())
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
Path.write_text = lambda *a, **k: (bad.append("write_text"), (_ for _ in ()).throw(OSError("blocked")))[1]
Path.mkdir = lambda *a, **k: (bad.append("mkdir"), (_ for _ in ()).throw(OSError("blocked")))[1]
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
class Raising:
    def __init__(self, exc): self.exc = exc
    def get_market_snapshot(self, symbol): raise self.exc
class Fixed:
    def __init__(self, price): self.price = price
    def get_market_snapshot(self, symbol): return MarketSnapshot(symbol=symbol, price=self.price, ts=111)
out = {}
def run(name, state, mode=None, fallback_env=None):
    for k in ("KIWOOM_MODE", "MOCK_PRICE_FALLBACK"): os.environ.pop(k, None)
    if mode is not None: os.environ["KIWOOM_MODE"] = mode
    if fallback_env is not None: os.environ["MOCK_PRICE_FALLBACK"] = fallback_env
    st = copy.copy(state); st.pop("_x", None)
    n0 = len(traps)
    try:
        res = bms.build_market_snapshot(st)
        snap = dict(res["market_snapshot"]); snap.pop("ts", None); h = res["market_snapshot_health"]
        out[name] = ["ok", snap, h, res.get("persisted_state"), res is st, len(traps) - n0]
    except Exception as e: out[name] = [type(e).__name__, str(e)[:80], len(traps) - n0]
S = "005930"
run("ok_mock_mode", {"symbol": S, "price_reader": Fixed(70500.0)})
run("ok_mock_explicit", {"symbol": S, "price_reader": Fixed(70500.0)}, mode="MOCK")
run("ok_real_mode", {"symbol": S, "price_reader": Fixed(70500.0)}, mode="paper")
run("err_mock_no_hint", {"symbol": S, "price_reader": Raising(RuntimeError("quote down"))})
run("err_mock_fallback_env", {"symbol": S, "price_reader": Raising(RuntimeError("quote down"))}, fallback_env="55555")
run("err_mock_last_snapshot", {"symbol": S, "price_reader": Raising(TimeoutError("t")), "market_snapshot": {"price": 61000}})
run("err_mock_persisted_hint", {"symbol": S, "price_reader": Raising(OSError("o")), "persisted_state": {"last_market_price": 62000.5, "other": 1}})
run("err_mock_snapshot_beats_persisted", {"symbol": S, "price_reader": Raising(RuntimeError("x")), "market_snapshot": {"price": 1.5}, "persisted_state": {"last_market_price": 9}})
run("err_mock_bad_hints", {"symbol": S, "price_reader": Raising(RuntimeError("x")), "market_snapshot": {"price": "abc"}, "persisted_state": {"last_market_price": None}})
run("err_real_mode_raises", {"symbol": S, "price_reader": Raising(RuntimeError("quote down"))}, mode="real")
run("err_paper_mode_raises", {"symbol": S, "price_reader": Raising(RuntimeError("quote down"))}, mode="paper")
run("zero_price_mock_no_hint", {"symbol": S, "price_reader": Fixed(0.0)})
run("zero_price_mock_hint", {"symbol": S, "price_reader": Fixed(-1.0), "persisted_state": {"last_market_price": 62000}})
run("zero_price_real_mode_kept", {"symbol": S, "price_reader": Fixed(0.0)}, mode="real")
run("bad_fallback_env", {"symbol": S, "price_reader": Fixed(70500.0)}, fallback_env="abc")
run("empty_fallback_env", {"symbol": S, "price_reader": Raising(RuntimeError("x"))}, fallback_env="")
run("missing_symbol", {"price_reader": Fixed(1.0)})
run("blank_symbol", {"symbol": "  ", "price_reader": Fixed(1.0)})
run("persisted_not_dict", {"symbol": S, "price_reader": Fixed(70500.0), "persisted_state": "x"})
run("no_reader_default_path_trapped", {"symbol": S})
run("reader_none_default_path_trapped", {"symbol": S, "price_reader": None})
out["traps"] = traps; out["bad"] = bad
check(not bad, "blocked attempts: %r" % bad)
check(out["ok_mock_mode"][5] == 0 and out["err_mock_no_hint"][5] == 0, "injected reader must not construct real reader")
check(out["no_reader_default_path_trapped"][0] == "RuntimeError" and out["no_reader_default_path_trapped"][2] == 1, "default path would build the real reader (trapped)")
check(out["err_real_mode_raises"][0] == "RuntimeError" and out["err_mock_no_hint"][0] == "ok", "failsoft only in mock mode")
print("RF008_MARKET_SNAPSHOT_OK cases=%d failsoft=mock_only real_mode_raises=yes default_reader_trapped=%d blocked=0 debug=%s" % (sum(1 for k in out if k not in ("traps", "bad")), len(traps), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
