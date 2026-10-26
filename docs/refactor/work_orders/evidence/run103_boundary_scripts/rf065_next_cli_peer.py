# RF-065 next CLI: run_agent_effectiveness_scorecard.main on an EMPTY/synthetic tmp reports_root.
# Writes are allowed ONLY under the tmp root (every other write is recorded and blocked); no network/process/db.
import os, sys, json, io, shutil, socket, subprocess, sqlite3, builtins, contextlib, runpy
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
os.environ.pop("Q9_EVALUATION_SLIPPAGE_PCT", None)
root = Path("/tmp/rf065_fixed"); shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
import ssl, http.client
sys.path.insert(0, repo + "/scripts/research")
import importlib
cli = importlib.import_module("scripts.research.run_agent_effectiveness_scorecard")
bad, outside = [], []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: return Path(os.path.abspath(str(p))).is_relative_to(root)
    except Exception: return False
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): outside.append("open:" + str(f)); raise OSError("blocked write outside tmp")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt = Path.write_text; _mk = Path.mkdir
def wt(self, *a, **k):
    if not inside(self): outside.append("write_text:" + str(self)); raise OSError("blocked write outside tmp")
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): outside.append("mkdir:" + str(self)); raise OSError("blocked mkdir outside tmp")
    return _mk(self, *a, **k)
Path.write_text = wt; Path.mkdir = mk
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def files(): return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
out = {}
def run(name, argv):
    saved = sys.argv; sys.argv = ["x"] + argv; buf = io.StringIO(); code = 0
    try:
        with contextlib.redirect_stdout(buf):
            try: code = cli.main()
            except SystemExit as e: code = e.code
            except Exception as e: code = "EXC:" + type(e).__name__ + ":" + str(e)[:80]
    finally: sys.argv = saved
    out[name] = [code, buf.getvalue().replace(str(root), "ROOT")[:6000], files()]
rr = str(root / "reports"); od = str(root / "out")
run("single_day_explicit_outdir", ["--start", "2026-04-08", "--end", "2026-04-08", "--reports-root", rr, "--output-dir", od])
run("range_default_outdir", ["--start", "2026-04-08", "--end", "2026-04-10", "--reports-root", rr])
run("missing_end", ["--reports-root", rr])
check(out["single_day_explicit_outdir"][0] == 0, "single day exit 0: %r" % (out["single_day_explicit_outdir"][0],))
check(out["range_default_outdir"][0] == 0, "range exit 0: %r" % (out["range_default_outdir"][0],))
check(out["missing_end"][0] == 2, "argparse exit 2")
check(not bad and not outside, "no blocked/outside writes: %r %r" % (bad, outside))
res = json.loads(out["single_day_explicit_outdir"][1])
out["keys"] = sorted(res); out["files_final"] = files(); out["bad"] = bad; out["outside"] = outside
check(all(f.startswith(("out/", "reports/")) for f in out["files_final"]), "files confined")
print("RF065_NEXT_CLI_PEER_OK single=%s range=%s argparse=%s files=%d outside_writes=%d debug=%s" % (out["single_day_explicit_outdir"][0], out["range_default_outdir"][0], out["missing_end"][0], len(out["files_final"]), len(outside), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
