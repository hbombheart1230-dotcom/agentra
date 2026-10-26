# RF-067 root wrapper peer: runpy delegation (__main__) and import-time alias of two public root wrappers.
import os, sys, json, io, shutil, socket, subprocess, sqlite3, builtins, contextlib, runpy, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
root = Path("/tmp/rf067_fixed"); shutil.rmtree(root, ignore_errors=True)
def w(p, obj): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(obj), encoding="utf-8")
for day in ("2026-04-08", "2026-04-09"):
    for i in range(3):
        td = root / "reports" / "trades" / day / f"T{i}"
        w(td / "lifecycle_bundle.json", {"lifecycle": {"exit": {"price": 1}}} if i == 0 else {"status": "open"})
        w(td / "reports" / "ai_trade_report.json", {"section_provenance": {"a": {"source": "fallback"}}} if i == 0 else {})
        w(td / "reports" / "ai_trade_report_llm_response.json", {"status": "partial" if i == 1 else "ok"})
import ssl, http.client
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
def snap(): return sorted(str(p.relative_to(root)) for p in root.rglob("*"))
before = snap(); rr = str(root / "reports"); out = {}
def run_main(path, argv):
    saved = sys.argv; sys.argv = [path] + argv
    buf = io.StringIO(); code = None
    try:
        with contextlib.redirect_stdout(buf):
            try: runpy.run_path(path, run_name="__main__")
            except SystemExit as e: code = e.code if e.code is not None else 0
    finally: sys.argv = saved
    return [code, buf.getvalue().replace(str(root), "ROOT")]
W1, W2 = "scripts/check_reports_trades_health.py", "scripts/check_reporter_upgrade_regression.py"
out["w1_json"] = run_main(W1, ["--reports-root", rr, "--day", "2026-04-08", "--json"])
out["w1_plain"] = run_main(W1, ["--reports-root", rr])
out["w1_badflag"] = run_main(W1, ["--nope"])[0]
out["w2_json"] = run_main(W2, ["--reports-root", rr, "--day", "2026-04-08", "--day", "2026-04-09", "--json"])
out["w2_plain"] = run_main(W2, ["--reports-root", rr, "--day", "2026-04-08"])
out["w2_nodays"] = run_main(W2, ["--reports-root", rr])[0]
# delegated result equals direct module main (equivalence)
direct = importlib.import_module("scripts.diagnostics.check_reports_trades_health")
buf = io.StringIO()
with contextlib.redirect_stdout(buf): rc = direct.main(["--reports-root", rr, "--day", "2026-04-08", "--json"])
check(out["w1_json"][0] == rc and out["w1_json"][1] == buf.getvalue().replace(str(root), "ROOT"), "wrapper __main__ output equals direct main")
# import-time alias: wrapper module object is the diagnostics module itself
for name in ("check_reports_trades_health", "check_reporter_upgrade_regression"):
    sys.modules.pop("scripts." + name, None)
    m = importlib.import_module("scripts." + name)
    tgt = importlib.import_module("scripts.diagnostics." + name)
    out["alias|" + name] = [m is tgt, m.__name__, sys.modules["scripts." + name] is tgt, hasattr(m, "main")]
    check(m is tgt, "alias identity " + name)
# monkeypatch propagation through alias
m = importlib.import_module("scripts.check_reports_trades_health"); orig = m.audit_reports_trades_health
m.audit_reports_trades_health = lambda *a, **k: {"patched": True, "ok": True, "trade_dir_count": 0, "issue_counts": {}}
t = importlib.import_module("scripts.diagnostics.check_reports_trades_health")
out["alias_patch_visible"] = t.audit_reports_trades_health is m.audit_reports_trades_health
m.audit_reports_trades_health = orig
out["tree_unchanged"] = before == snap(); out["blocked_attempts"] = bad
check(out["tree_unchanged"] and not bad and out["alias_patch_visible"], "side effects/patchability")
check(out["w1_json"][0] == 0 and out["w2_json"][0] == 0 and out["w1_badflag"] == 2 and out["w2_nodays"] == 2, "exit codes")
print("RF067_WRAPPER_PEER_OK w1=%s w2=%s argparse=%s/%s alias=2 patch_visible=%s writes=0 debug=%s" % (out["w1_json"][0], out["w2_json"][0], out["w1_badflag"], out["w2_nodays"], out["alias_patch_visible"], __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
