# RF-067 C4 A peer: run the 4 "no file/subprocess token" targets through their real root wrappers
# (runpy as __main__) on empty temp trees. socket/subprocess blocked; writes outside temp blocked; .env never read.
import builtins, contextlib, io, json, os, runpy, socket, subprocess, sys, tempfile
from pathlib import Path
REPO = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(REPO))
TMP = Path(tempfile.mkdtemp(prefix="rf067_")).resolve(); os.chdir(TMP)
_open = builtins.open; writes = []
def _g(p, mode="r", *a, **k):
    if isinstance(p, int): return _open(p, mode, *a, **k)
    rp = Path(os.fspath(p)).resolve()
    if any(c in str(mode) for c in "wax+"):
        writes.append(str(rp))
        if not rp.is_relative_to(TMP): raise PermissionError(f"write outside tmp: {rp}")
    if rp.name == ".env" and not rp.is_relative_to(TMP): raise PermissionError("real .env read blocked")
    return _open(p, mode, *a, **k)
builtins.open = io.open = _g
def _no(*a, **k): raise PermissionError("blocked")
socket.socket.connect = _no; socket.create_connection = _no; subprocess.Popen.__init__ = _no  # type: ignore
(TMP / "env").write_text("", encoding="utf-8")
CASES = {
 "check_monitor_gate_patterns": ["--canonical-root", str(TMP / "canon"), "--day", "2026-10-27", "--json"],
 "check_phase_5_2_5_3_runtime_health": ["--reports-root", str(TMP / "reports"), "--event-log-path", str(TMP / "events.jsonl"), "--date", "2026-10-27"],
 "check_profitability_recovery_day1": ["--date", "2026-10-27", "--reports-root", str(TMP / "reports"), "--json"],
 "check_runtime_profile": ["--env-path", str(TMP / "env"), "--json"],
}
res = {}
for name, argv in CASES.items():
    sys.argv = [str(REPO / "scripts" / f"{name}.py")] + argv; buf = io.StringIO(); code = 0; err = ""
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        try: runpy.run_path(sys.argv[0], run_name="__main__")
        except SystemExit as e: code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        except Exception as e: code = "EXC"; err = f"{type(e).__name__}: {e}"[:160]
    out = buf.getvalue(); js = None
    try: js = json.loads(out); keys = sorted(js)[:8] if isinstance(js, dict) else type(js).__name__
    except Exception: keys = None
    res[name] = {"exit": code, "stdout_bytes": len(out), "json_keys": keys, "err": err}
outside = [w for w in writes if not Path(w).is_relative_to(TMP)]
print(json.dumps({"cases": res, "writes": len(writes), "outside_writes": len(outside)}, sort_keys=True))
ok = not outside and all(r["exit"] != "EXC" for r in res.values())
print("RF067_FOUR_TARGETS_PEER_OK" if ok else "RF067_FOUR_TARGETS_PEER_FAIL"); sys.exit(0 if ok else 1)
