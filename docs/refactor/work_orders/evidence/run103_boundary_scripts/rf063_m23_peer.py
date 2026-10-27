import sys, os, io, json, runpy, socket, subprocess, tempfile, contextlib
from pathlib import Path
tree = Path(sys.argv[1]).resolve()
tmp = Path(tempfile.mkdtemp(prefix="rf063_"))
def deny(*a, **k): raise RuntimeError("blocked")
socket.socket.connect = deny
subprocess.Popen = deny
os.chdir(tmp)
sys.path.insert(0, str(tree))
res = {}
for mode in ("text", "json"):
    ev = tmp / mode / "ev.jsonl"; rd = tmp / mode / "rep"
    argv = ["--event-log-path", str(ev), "--report-dir", str(rd), "--day", "2000-01-01"] + (["--json"] if mode == "json" else [])
    from scripts.diagnostics import run_m23_closeout_check as m
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: rc = m.main(argv)
        except BaseException as e: rc = f"EXC:{type(e).__name__}:{e}"
    res[mode] = (rc, buf.getvalue().strip()[:200])
    print(mode, res[mode])
ok = all(not str(r[0]).startswith("EXC") for r in res.values())
print("RF063_M23_PEER_OK" if ok else "RF063_M23_PEER_FAIL", "optimized=", sys.flags.optimize)
sys.exit(0 if ok else 1)
