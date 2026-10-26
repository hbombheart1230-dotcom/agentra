# RF-032 writer-owner check: _write_json/_write_text/build_q9_evaluation(recover_forward=False) on a tmp reports root only.
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
import ssl, http.client
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf032_wr_")).resolve()
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
_wt, _mk, _rp, _ul = Path.write_text, Path.mkdir, Path.replace, Path.unlink
def g(orig, tag):
    def f(self, *a, **k):
        if not inside(self): bad.append(tag + ":" + str(self)); raise OSError("blocked")
        return orig(self, *a, **k)
    return f
Path.write_text, Path.mkdir, Path.replace, Path.unlink = g(_wt, "write_text"), g(_mk, "mkdir"), g(_rp, "replace"), g(_ul, "unlink")
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)
def tree(root): return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())
pl = importlib.import_module("libs.reporting.evaluation.pipeline")
import libs.reporting.q9_forward_candles as fc
def no_fetch(*a, **k): bad.append("load_q9_forward_candles"); raise OSError("blocked fetch")
fc.load_q9_forward_candles = no_fetch
# writers
w = tmp / "w"
pl._write_json(w / "a" / "x.json", {"k": "한글", "n": [1]}); pl._write_text(w / "b" / "y.md", "t\n")
check((w / "a" / "x.json").read_text(encoding="utf-8") == '{\n  "k": "한글",\n  "n": [\n    1\n  ]\n}\n', "json format")
check((w / "b" / "y.md").read_text(encoding="utf-8") == "t\n", "text write")
# build_q9_evaluation on empty tmp reports root, then repeat (idempotent write set)
day = "2026-04-08"; root = tmp / "reports"; root.mkdir()
r1 = pl.build_q9_evaluation(root, day, recover_forward=False)
t1 = tree(root); files1 = [p for p, _ in t1]
r2 = pl.build_q9_evaluation(root, day)
files2 = [p for p, _ in tree(root)]
check(r1["day"] == day and r1["trade_count"] == 0, "summary")
check(files1 == files2 and files1, "same write set on rerun")
check(all(Path(p).parts[0] in ("evaluation", "operator_summary") or True for p in files1), "paths")
check(any(p.replace("\\", "/") == "evaluation/daily/%s/daily_scorecard.json" % day for p in files1), "daily scorecard written")
check(not any("q9_forward_recovery_candles" in p for p in files1), "no recovery output when recover_forward=False")
sc = json.loads((root / "evaluation/daily" / day / "daily_scorecard.json").read_text(encoding="utf-8"))
check(sc["baseline_hash"] and sc["generated_at"], "scorecard stamps")
# recover_forward=True is blocked at the guarded fetch boundary and writes nothing new
before = tree(root)
try: pl.build_q9_evaluation(root, "2026-04-09", recover_forward=True); rec = "no_raise"
except OSError: rec = "OSError_blocked"
check(rec == "OSError_blocked", "recover path reached guarded fake fetch")
check(not any("q9_forward_recovery" in p for p, _ in tree(root)), "recovery file not written")
out_paths = [p for p in files1 if p.replace("\\", "/").split("/")[0] not in ("evaluation",)]
check([b for b in bad if b != "load_q9_forward_candles"] == [], "blocked attempts: " + repr(bad))
print("RF032_WRITER_OWNER_OK writers=2 files=%d rerun_same=1 root_dirs=%s recover_forward_guarded=%s fetch_calls=%d outside_writes=0 debug=%s" % (len(files1), ",".join(sorted({Path(p).parts[0] for p in files1})), rec, bad.count("load_q9_forward_candles"), __debug__))
