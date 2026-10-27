# RF-067 P2 independent peer (A for B-owned RF): delegated diagnostics target scripts/diagnostics/check_q9_q12_readiness.py, REAL subprocess through the public root wrapper (+ target runpy bootstrap, plain, -m).
# Windows-oriented target: process status uses PowerShell/WMI (Get-CimInstance). This Linux run can only exercise the artifact (closeout) logic and the DEGRADED (powershell unavailable/blocked) preopen/intraday fail-closed path. Child bootstrap blocks network/sqlite/writes and BLOCKS subprocess (attempts are counted: only the process-query attempts are expected).
# Real Windows process detection, Task Scheduler and a live loop lock are NOT_RUN. Usage: python rf067_q9_q12_readiness_peer.py <repo_root> [-O]
# (no further notes)
import os, sys, json, re, shutil, subprocess, tempfile, hashlib
from pathlib import Path
repo = Path(sys.argv[1]).resolve(); opt = ["-O"] if "-O" in sys.argv[2:] else []
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
BOOT = r'''
import sys, os, socket, subprocess, sqlite3, atexit, runpy, builtins
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
atexit.register(lambda: sys.stderr.write("\nBLOCKED_ATTEMPTS=%d\n" % len(bad)))
script = sys.argv[1]; sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name="__main__")
'''
tmp = Path(tempfile.mkdtemp(prefix="rf067_batch_")).resolve()
import os, sys, json, re, shutil, subprocess, tempfile, hashlib
from pathlib import Path
repo = Path(sys.argv[1]).resolve(); opt = ["-O"] if "-O" in sys.argv[2:] else []
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
BOOT = r'''
import sys, os, socket, subprocess, sqlite3, atexit, runpy, builtins
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
atexit.register(lambda: sys.stderr.write("\nBLOCKED_ATTEMPTS=%d\n" % len(bad)))
script = sys.argv[1]; sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name="__main__")
'''
tmp = Path(tempfile.mkdtemp(prefix="rf067_batch_")).resolve()
def repo_status(): return subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout
repo_before = repo_status()
def put(p, obj, raw=False): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(obj if raw else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
def tree_hash(root):
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")): h.update((str(p.relative_to(root)) + ("/" if p.is_dir() else "")).encode()); h.update(p.read_bytes() if p.is_file() else b"")
    return h.hexdigest()


NAME = "check_q9_q12_readiness"
D, DOLD = "2026-10-20", "2026-08-30"
rr = tmp / "reports"
def art(rel, obj=None): put(rr / rel, obj if obj is not None else {"schema_version": "s.v1", "capture_status": "CAPTURED", "evidence_status": "OK"})
def baseline(day, lead=True, skip=()):
    items = {"evaluation/baseline_samsung_hynix/%s/baseline_samsung_hynix_decisions.json", "evaluation/baseline_samsung_hynix/%s/baseline_samsung_hynix_forward_returns.json", "evaluation/baseline_samsung_hynix/%s/q9_vs_samsung_hynix_daily_comparison.json",
             "evaluation/opportunity_engine_shadow/%s/opportunity_engine_signals.json", "evaluation/opportunity_engine_shadow/%s/opportunity_engine_virtual_trades.json", "evaluation/opportunity_engine_shadow/%s/opportunity_engine_daily_report.json",
             "evaluation/baseline_btc_woori_tech/%s/baseline_btc_woori_decisions.json", "evaluation/baseline_btc_woori_tech/%s/baseline_btc_woori_forward_returns.json", "evaluation/baseline_btc_woori_tech/%s/baseline_btc_woori_comparison.json", "evaluation/baseline_btc_woori_tech/%s/q12_btc_woori_hypothesis_validation.json"}
    for it in sorted(items):
        if it.split("/")[-1] not in skip: art(it % day)
    art("evaluation/baseline_btc_woori_tech/hypothesis_validation/q12_btc_woori_hypothesis_cumulative.json")
    if lead:
        for n in ("q10_preopen_signal_snapshot.json", "q10_actual_market_reactions.json", "q10_expected_vs_actual.json", "q10_shadow_entry_comparison.json"): art(f"evaluation/baseline_samsung_hynix/{day}/q10_forward_validation/{n}")
        (rr / f"evaluation/baseline_samsung_hynix/{day}/q10_forward_validation/q10_forward_validation_report.md").write_text("# r\n")
env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY"))}
env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "", "PATH": ""})
def run(argv, *, mode="wrapper_boot", enc="utf-8"):
    e = dict(env); e["PYTHONIOENCODING"] = enc
    wrapper, target = repo / f"scripts/{NAME}.py", repo / f"scripts/diagnostics/{NAME}.py"
    cmd = {"wrapper_boot": [sys.executable, *opt, "-c", BOOT, str(wrapper), *argv], "target_boot": [sys.executable, *opt, "-c", BOOT, str(target), *argv],
           "wrapper_plain": [sys.executable, *opt, str(wrapper), *argv], "module_plain": [sys.executable, *opt, "-m", f"scripts.diagnostics.{NAME}", *argv]}[mode]
    r = subprocess.run(cmd, cwd=str(repo if mode == "module_plain" else tmp), env=e, capture_output=True, timeout=120)
    err = r.stderr.decode("utf-8", "replace"); m = re.search(r"BLOCKED_ATTEMPTS=(\d+)", err)
    last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_ATTEMPTS")][-1:] or [""]
    return {"code": r.returncode, "out": r.stdout, "err_last": last[0].replace(str(tmp), "T").replace(str(repo), "REPO")[:140], "attempts": int(m.group(1)) if m else None}
LOCK = str(tmp / "data/state/m13_live_loop.lock")
def modes_identical(argv, deterministic=True):
    res = {m_: run(argv, mode=m_) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
    base = res["wrapper_boot"]
    check(all(v["code"] == base["code"] for v in res.values()), {k: v["code"] for k, v in res.items()})
    if deterministic:
        check(all(v["out"] == base["out"] for v in res.values() if v is not res["wrapper_boot"] or True), "stdout differs across modes")
    return base
def jload(r): return json.loads(r["out"].decode("utf-8"))
def codes(p): return sorted(b["code"] for b in p["blockers"])
before = tree_hash(tmp); out = {}
# ---- closeout (artifact logic; independent of process enumeration)
# 1) everything missing, day >= 2026-08-31 -> all 16 artifacts + lead-market capture blocker
j = modes_identical(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"]); p = jload(j)
check(j["code"] == 1 and p["status"] == "BLOCKED" and p["schema_version"] == "q9_q12_readiness_check.v1" and p["behavior_effect"] == "observability_only", (j["code"], p["status"]))
check(len(p["blockers"]) == 17 and "q10_lead_market_preopen_not_captured" in codes(p) and p["blockers"][-1]["capture_status"] == "MISSING", (len(p["blockers"]), codes(p)[:3]))
out["closeout_all_missing"] = len(p["blockers"])
# 2) day before the lead-market activation date -> 11 artifacts, no lead blockers
p = jload(modes_identical(["--day", DOLD, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"])); check(len(p["blockers"]) == 11 and not any("lead_market" in c for c in codes(p)), len(p["blockers"]))
out["closeout_pre_activation_missing"] = len(p["blockers"])
# 3) all present + captured, validity VALID -> PASS exit 0 (live/process status are ignored for closeout)
baseline(D); art(f"evaluation/daily/{D}/q9_day_validity.json", {"status": "VALID", "counts_as_formal_day": True}); art(f"operator_summary/daily/{D}/q9_decision_windows.json", {"windows": [{"generated_at": "2026-10-20T09:02:00+09:00"}, {"generated_at": "2026-10-20T09:04:30+09:00"}, "junk", {"generated_at": "bad"}]})
ok = modes_identical(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"]); p = jload(ok)
check(ok["code"] == 0 and p["status"] == "PASS" and p["blockers"] == [] and p["warnings"] == [] and p["q9"]["window_count"] == 3 and p["q9"]["first_window_kst"].startswith("2026-10-20T09:02") and p["q9"]["last_window_kst"].startswith("2026-10-20T09:04:30") and p["q9"]["counts_as_formal_day"] is True, (ok["code"], p["status"], p["q9"]))
t = modes_identical(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK]); check(t["out"].decode("utf-8") == "status=PASS\n" and t["code"] == 0, t["out"])
# 4) validity INVALID -> blocker; non-final status -> warning exit 0; lead market not captured -> blocker; one artifact missing
art(f"evaluation/daily/{D}/q9_day_validity.json", {"status": "INVALID", "blockers": ["b1"]}); p = jload(modes_identical(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"]))
check(codes(p) == ["q9_day_invalid"] and p["blockers"][0]["blockers"] == ["b1"], p["blockers"])
art(f"evaluation/daily/{D}/q9_day_validity.json", {"status": "PENDING"}); w = modes_identical(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"]); p = jload(w)
check(w["code"] == 0 and p["status"] == "PASS_WITH_WARNINGS" and p["warnings"] == [{"code": "q9_day_not_final_valid", "status": "PENDING"}], (w["code"], p["warnings"]))
art(f"evaluation/baseline_samsung_hynix/{D}/q10_forward_validation/q10_preopen_signal_snapshot.json", {"capture_status": "MISSED"}); p = jload(modes_identical(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"]))
check(codes(p) == ["q10_lead_market_preopen_not_captured"] and p["blockers"][0]["capture_status"] == "MISSED", p["blockers"])
art(f"evaluation/baseline_samsung_hynix/{D}/q10_forward_validation/q10_preopen_signal_snapshot.json")
(rr / f"evaluation/opportunity_engine_shadow/{D}/opportunity_engine_signals.json").unlink(); p = jload(modes_identical(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"]))
check(codes(p) == ["q11_signals_missing"], codes(p))
out["closeout_cases"] = ["PASS", "INVALID->blocker", "PENDING->warning", "MISSED->blocker", "missing->q11_signals_missing"]
# ---- preopen / intraday: process enumeration is PowerShell/WMI -> unavailable here -> degraded fail-closed
for ph in ("preopen", "intraday"):
    r = modes_identical(["--day", D, "--phase", ph, "--reports-root", str(rr), "--lock-path", LOCK, "--json"], deterministic=(ph == "preopen")); p = jload(r)
    cs = codes(p)
    check(r["code"] == 1 and p["status"] == "BLOCKED" and "live_session_not_running" in cs and all(f"{n}_loop_not_running" in cs for n in ("q10_samsung_hynix", "q11_opening_opportunity", "q12_btc_woori")), (ph, cs))
    check(p["live"]["running"] is False and p["live"]["process_count"] == 0 and p["live"]["lock_exists"] is False and all(not v["running"] for v in p["processes"].values()), p["live"])
    out[f"{ph}_blockers"] = [c for c in cs if not c.startswith("q9_first_window")]
# a lock file with this harness' own (alive) pid and a fresh heartbeat still cannot make it "running" without process enumeration
from datetime import datetime as _dt, timezone as _tz, timedelta as _td
put(Path(LOCK), {"heartbeat_ts": _dt.now(_tz(_td(hours=9))).isoformat(), "pid": os.getpid()})
before = tree_hash(tmp)
r = modes_identical(["--day", D, "--phase", "preopen", "--reports-root", str(rr), "--lock-path", LOCK, "--json"]); p = jload(r)
out["lock_with_fresh_heartbeat"] = {"code": r["code"], "lock_exists": p["live"]["lock_exists"], "lock_pid_alive": p["live"]["lock_pid_alive"], "running": p["live"]["running"], "heartbeat_age_sec": p["live"]["heartbeat_age_sec"] is not None}
check(p["live"]["lock_exists"] and p["live"]["running"] is False and r["code"] == 1, out["lock_with_fresh_heartbeat"])
# ---- argparse / exits / encodings / attempts
a = {"bad_phase": run(["--phase", "bogus"])["code"], "unknown": run(["--bogus"])["code"], "help": run(["--help"])["code"], "bad_day_string": run(["--day", "x", "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"])["code"]}
check(a == {"bad_phase": 2, "unknown": 2, "help": 0, "bad_day_string": 1}, a); out["argv"] = a  # invalid --day string is not validated; day<activation string compare -> blockers -> exit 1
cp = run(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK], enc="cp949"); check(cp["code"] in (0, 1), cp)
at = run(["--day", D, "--phase", "closeout", "--reports-root", str(rr), "--lock-path", LOCK, "--json"])["attempts"]; out["subprocess_attempts_bootstrap"] = at; check(at is not None and 1 <= at <= 4, at)  # only the PowerShell process queries (blocked here)
check(tree_hash(tmp) == before, "tmp tree changed by read-only audit"); check(repo_status() == repo_before, "repo working tree changed")
out["repo_tree_unchanged"] = True
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF067_Q9_Q12_READINESS_OK closeout_all_missing=17 pre_activation=11 pass/warn/blocked=yes preopen_intraday=degraded_fail_closed(powershell_unavailable) subprocess_attempts=%d modes=4_identical child_writes=0 repo_tree_unchanged=yes debug=%s" % (out["subprocess_attempts_bootstrap"], "off" if opt else "on"))
