# RF-067 P2 independent peer (A for B-owned RF): delegated diagnostics target scripts/diagnostics/check_phase_5_2_5_3_runtime_health.py (NORMAL path), REAL subprocess through the public root wrapper (+ target via runpy bootstrap, plain, -m).
# Synthetic canonical monitor runs + monitor event log in a tmp reports root; REAL subprocess via the public root wrapper (+ target runpy bootstrap, plain, -m). Network/subprocess/sqlite blocked. Empty PATH.
# NOTE: unlike the other targets, this bootstrap ALLOWS writes (writes are observed, not blocked) because --date + an existing event log makes the 'inspect' CLI create .day_cache files via event_log_reader; the harness asserts where they go.
# Usage: python rf067_monitor_gate_patterns_peer.py <repo_root> [-O]
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
    if isinstance(mode, str) and set(mode) & set("wax+") and not str(f).startswith(os.environ.get("RF_TMP_ROOT", "\0")): bad.append("write:" + str(f)); raise OSError("blocked write outside tmp")
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
    if isinstance(mode, str) and set(mode) & set("wax+") and not str(f).startswith(os.environ.get("RF_TMP_ROOT", "\0")): bad.append("write:" + str(f)); raise OSError("blocked write outside tmp")
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


D, D0 = "2026-10-20", "2026-10-19"
croot = tmp / "reports/canonical"
def mon(day, rid, obj, raw=False): put(croot / day / rid / "monitor.json", obj, raw)
mon(D, "run-a", {"decision": "buy", "entry_reason": "r_buy"})
mon(D, "run-b", {"decision": "WAIT", "entry_reason": "below_vwap_reclaim_not_ready"})
mon(D, "run-c", {"decision": "NOOP", "monitor_reason": "below_vwap_reclaim_not_ready"})
mon(D, "run-d", {})
mon(D, "run-e", "{bad", raw=True)
(croot / D / "stray.txt").write_text("x")
mon(D0, "run-z", {"decision": "BUY", "primary_reason_code": "old"})
ev = tmp / "events.jsonl"
rows = [{"run_id": "run-a", "event_name": "monitor.entry_decision", "ts": "2026-10-20T00:00:00+00:00", "payload": {"policy_alignment_summary": {"alignment_state": "ALIGNED", "primary_blocker": "none"}, "signal_evidence": {"k": 1}}},
        {"run_id": "run-a", "event_name": "other.event", "ts": "2026-10-20T00:00:01+00:00", "payload": {"x": 1}},
        {"run_id": "run-b", "event": "monitor.entry_decision_detail", "ts": "2026-10-20T00:00:02+00:00", "payload": {"policy_aware_gating": {"applied": True, "applied_hints": ["h1"], "blocked_by_required": ["c1"]}}},
        {"run_id": "run-x", "event_name": "monitor.entry_decision", "ts": "2026-10-20T00:00:03+00:00", "payload": {}}]
ev.write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY", "EVENT_LOG_DAY_CACHE_DIR"))}
env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "", "PATH": "", "RF_TMP_ROOT": str(tmp)})
NAME = "check_phase_5_2_5_3_runtime_health"
def run(argv, *, extra_env=None, cwd=None, mode="wrapper_boot", enc="utf-8"):
    e = dict(env); e["PYTHONIOENCODING"] = enc; e.update(extra_env or {})
    wrapper, target = repo / f"scripts/{NAME}.py", repo / f"scripts/diagnostics/{NAME}.py"
    cmd = {"wrapper_boot": [sys.executable, *opt, "-c", BOOT, str(wrapper), *argv], "target_boot": [sys.executable, *opt, "-c", BOOT, str(target), *argv],
           "wrapper_plain": [sys.executable, *opt, str(wrapper), *argv], "module_plain": [sys.executable, *opt, "-m", f"scripts.diagnostics.{NAME}", *argv]}[mode]
    r = subprocess.run(cmd, cwd=str(cwd or tmp), env=e, capture_output=True, timeout=120)
    err = r.stderr.decode("utf-8", "replace"); m = re.search(r"BLOCKED_ATTEMPTS=(\d+)", err)
    last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_ATTEMPTS")][-1:] or [""]
    return {"code": r.returncode, "out": r.stdout, "err_last": last[0].replace(str(tmp), "T").replace(str(repo), "REPO")[:140], "attempts": int(m.group(1)) if m else None}
def modes_identical(argv):
    res = {m_: run(argv, mode=m_, cwd=(repo if m_ == "module_plain" else None)) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
    base = res["wrapper_boot"]
    check(all(v["code"] == base["code"] and v["out"] == base["out"] for v in res.values()), {k: (v["code"], v["err_last"]) for k, v in res.items()})
    check(base["attempts"] == 0 and res["target_boot"]["attempts"] == 0, ("attempts", base["attempts"], base["err_last"]))
    return base
RR, EV = str(tmp / "reports"), str(ev)
def files(root): return sorted(str(p.relative_to(root).as_posix()) for p in Path(root).rglob("*") if p.is_file())
out = {}
snap_before = files(tmp)
# 1) WITHOUT --date: streaming read of the event log (no cache), latest canonical day chosen
j = modes_identical(["--reports-root", RR, "--event-log-path", EV, "--json"]); check(j["code"] == 0 and j["err_last"] == "", j)
p = json.loads(j["out"].decode("utf-8"))
check(p["schema_version"] == "phase_5_runtime_health_check.v1" and p["run_count"] == 5 and p["final_decision_counts"] == {"BUY": 1, "WAIT": 1, "NOOP": 1, "UNKNOWN": 2}, (p["run_count"], p["final_decision_counts"]))  # latest day = 2026-10-20 (5 run dirs, stray.txt skipped)
check(len(p["buy_runs"]) == 1 and len(p["reclaim_wait_runs"]) == 2, (len(p["buy_runs"]), len(p["reclaim_wait_runs"])))
check(files(tmp) == snap_before, "no cache/other files created without --date"); out["no_date_new_files"] = 0
sp = p["structure_presence"]; check(sp["policy_alignment_summary"]["present_count"] == 1 and sp["policy_aware_gating"]["present_count"] == 1 and sp["signal_evidence"]["present_count"] == 1, {k: v["present_count"] for k, v in sp.items()})  # event payloads picked up (run-a alignment/evidence; run-b gating via 'event' key)
check(p["policy_aware_gating_stats"]["applied_true_count"] == 1 and p["policy_aware_gating_stats"]["applied_hint_counts"] == {"h1": 1} and p["policy_aware_gating_stats"]["required_blocked_count"] == 1, p["policy_aware_gating_stats"])
out["json_core"] = {"run_count": p["run_count"], "decisions": p["final_decision_counts"], "structure_present": {k: v["present_count"] for k, v in sp.items()}, "gating": p["policy_aware_gating_stats"], "suspicious": p["suspicious_counts"]}
# 2) text + view flags
t = modes_identical(["--reports-root", RR, "--event-log-path", EV]); check(t["code"] == 0 and len(t["out"]) > 100, t["code"])
views = {}
for name, argv in {"only_buy": ["--only-buy"], "reason": ["--reason", "below_vwap_reclaim_not_ready"], "reclaim": ["--show-reclaim-near-ready"], "policy": ["--show-policy-summary"], "chart": ["--show-chart-structure-summary"]}.items():
    r = modes_identical(["--reports-root", RR, "--event-log-path", EV, *argv]); views[name] = {"code": r["code"], "lines": len(r["out"].decode("utf-8").splitlines())}; check(r["code"] == 0, (name, r["err_last"]))
out["views"] = views
only_buy = run(["--reports-root", RR, "--event-log-path", EV, "--only-buy"])["out"].decode("utf-8"); check("run-a" in only_buy and "run-b" not in only_buy, only_buy[:200])
# 3) --run-id lookup across days (limit), --limit, bad inputs
rz = json.loads(run(["--reports-root", RR, "--event-log-path", EV, "--run-id", "run-z", "--json"])["out"]); check(rz["run_count"] == 1 and rz["runs"][0]["run_id"] == "run-z", rz["run_count"])
rm = json.loads(run(["--reports-root", RR, "--event-log-path", EV, "--run-id", "run-a", "--run-id", "run-z", "--json"])["out"]); check(rm["run_count"] == 2, rm["run_count"])
rl = json.loads(run(["--reports-root", RR, "--event-log-path", EV, "--limit", "2", "--json"])["out"]); check(rl["run_count"] == 2, rl["run_count"])
rneg = json.loads(run(["--reports-root", RR, "--event-log-path", EV, "--limit", "-5", "--json"])["out"]); out["limit_negative_run_count"] = rneg["run_count"]; check(rneg["run_count"] == 1, rneg["run_count"])  # max(1, -5) -> 1
miss = run(["--reports-root", RR, "--event-log-path", EV, "--run-id", "nope"]); check(miss["code"] == 2 and b'"ok": false' in miss["out"], miss)
# 4) WITH --date and an existing event log: the 'read-only' CLI writes .day_cache beside the event log
before = files(tmp)
d = modes_identical(["--reports-root", RR, "--event-log-path", EV, "--date", D, "--json"]); check(d["code"] == 0, d["err_last"])
created = sorted(set(files(tmp)) - set(before))
out["date_creates_cache"] = [re.sub(r"_[0-9a-f]{12}", "_<pathhash>", c) for c in created]
check(any(c.startswith(".day_cache/events_2026-10-20_") and c.endswith(".jsonl") for c in created) and any(c.endswith(".meta.json") for c in created), created)
check(all(c.startswith(".day_cache/") for c in created), created)  # only the day cache, beside the event log (tmp root here)
pd = json.loads(d["out"].decode("utf-8")); check(pd["run_count"] == 5 and pd["structure_presence"]["policy_aware_gating"]["present_count"] == 1, "same results via cache path")
# 5) cache dir redirected by EVENT_LOG_DAY_CACHE_DIR
alt = tmp / "alt_cache"; shutil.rmtree(tmp / ".day_cache"); before = files(tmp)
r5 = run(["--reports-root", RR, "--event-log-path", EV, "--date", D, "--json"], extra_env={"EVENT_LOG_DAY_CACHE_DIR": str(alt)}); check(r5["code"] == 0, r5["err_last"])
c5 = sorted(set(files(tmp)) - set(before)); out["env_redirected_cache"] = [re.sub(r"_[0-9a-f]{12}", "_<pathhash>", c) for c in c5]; check(c5 and all(c.startswith("alt_cache/") for c in c5), c5)
# 6) relative paths are anchored at REPO ROOT (cwd ignored); default paths would point into the repo
rel = json.loads(run(["--reports-root", "rf067_nonexistent_rel", "--event-log-path", "x.jsonl", "--json"], cwd=tmp)["out"].decode("utf-8")); check(rel["ok"] is False, rel)
out["relative_root_error"] = rel["error"][:60]
# 7) encodings: cp949 text output OK
cp = run(["--reports-root", RR, "--event-log-path", EV], enc="cp949"); check(cp["code"] == 0, cp["err_last"])
check(repo_status() == repo_before, "repo working tree changed")
out["repo_tree_unchanged"] = True
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF067_PHASE_5_2_5_3_POSITIVE_OK runs=5 views=5 run_id_cross_day=yes date_cache_side_effect=%s env_redirect=yes limit_neg_clamp=1 modes=4_identical child_attempts=0 repo_tree_unchanged=yes debug=%s" % ("yes" if out["date_creates_cache"] else "no", "off" if opt else "on"))
