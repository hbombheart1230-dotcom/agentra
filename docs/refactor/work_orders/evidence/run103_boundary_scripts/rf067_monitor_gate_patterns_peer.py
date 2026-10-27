# RF-067 P2 independent peer (A for B-owned RF): delegated diagnostics target scripts/diagnostics/check_monitor_gate_patterns.py, REAL subprocess through the public root wrapper (+ target via runpy bootstrap, plain, -m).
# Read-only canonical-artifact audit on a synthetic tmp canonical root. --live-followup (CompositeSkillRunner.from_env -> market data fetch) is NEVER passed (NOT_RUN). Child bootstrap blocks network/subprocess/sqlite/write-opens. Empty PATH.
# Checks row derivation (reclaim/breakout gaps, artifact age, stale groups, repeated states), filters/thresholds, naive-timestamp TZ dependence (TZ=UTC0 vs TZ=KST-9), cwd-relative default root, exits, tree unchanged.
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

from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
D = "2026-10-20"
def ep(s): return int(datetime.fromisoformat(s).timestamp())
croot = tmp / "canonical"
def run_dir(rid): return croot / D / rid
def mon(rid, obj, raw=False): put(run_dir(rid) / "monitor.json", obj, raw)
def shadow(rid, obj): put(run_dir(rid) / "commander_shadow.json", obj)
T1 = "2026-10-20T09:05:00+09:00"; T1e = ep(T1)
def gate(price=100.0, vd=0.02, lc=None, vr=1.5, pb=0.01, bl=105.0, tol=0.005, src=True):
    return {"monitor_gate_details": {"observed_features": {"current_price": price, "vwap_distance": vd, "latest_candle_ts": lc, "volume_ratio": vr, "pullback_pct": pb, "breakout_level": bl, "minute_source_present": src, "minute_source_used": "m1", "series_class": "S", "inferred_spacing_minutes": 1},
            "used_thresholds": {"reclaim_tolerance_pct": tol}, "entry_block_reason": "blk", "failed_gates": ["g1"], "passed_gates": ["g0"]}}
STALE = T1e - 600
mon("run-1", {"ts": T1, "symbol": "AAA", "evaluation_summary": "below_vwap_reclaim_not_ready", "primary_reason_code": "P", "decision_status": "WAIT"}); shadow("run-1", gate(lc=STALE))
mon("run-2", {"ts": "2026-10-20T09:06:00+09:00", "symbol": "AAA", "evaluation_summary": "below_vwap_reclaim_not_ready"}); shadow("run-2", gate(lc=STALE))
mon("run-3", {"ts": T1, "symbol": "BBB", "evaluation_summary": "other_reason"}); shadow("run-3", gate(lc=T1e - 60))              # fresh: age 1 min
mon("run-4", {"ts": T1, "symbol": "CCC", "evaluation_summary": "edge"}); shadow("run-4", gate(lc=T1e - 180, src=True))              # age exactly 3.0
mon("run-5", {"ts": T1, "symbol": "DDD", "evaluation_summary": "edge2"}); shadow("run-5", gate(lc=T1e - 179, src=True))            # age 2.983 (< 3.0)
mon("run-monitor-minute-1", {"ts": T1, "symbol": "SKIP", "evaluation_summary": "x"})                                                # skipped by name
mon("run-6", "{bad", raw=True)                                                                                                       # broken monitor.json -> empty row
mon("run-7", {"ts": T1, "symbol": "EEE", "evaluation_summary": "nosh", "position_snapshot": {"current_price": 50}})                  # no commander_shadow; price from position_snapshot
mon("run-8", {"ts": T1, "symbol": "FFF", "evaluation_summary": "div0"}); shadow("run-8", gate(vd=-1.0, lc=STALE))                    # denom 0 -> no reclaim price
mon("run-9", {"ts": T1, "symbol": "GGG", "evaluation_summary": "nanvd"}); shadow("run-9", gate(vd="nan", lc=STALE))                  # NaN -> None
mon("run-10", {"ts": "2026-10-20T09:05:00", "symbol": "HHH", "evaluation_summary": "naive_ts"}); shadow("run-10", gate(lc=ep("2026-10-20T09:00:00+09:00")))  # naive ts: depends on process TZ
put(croot / D / "run-11/notes.txt", "x", raw=True)                                                                                  # dir without monitor.json -> ignored
cwdA = tmp / "cwdA"; (cwdA / "reports").mkdir(parents=True); shutil.copytree(croot, cwdA / "reports/canonical"); cwdB = tmp / "cwdB"; cwdB.mkdir()
env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY"))}
env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "", "PATH": "", "TZ": "UTC0"})
NAME = "check_monitor_gate_patterns"
def run(argv, *, enc="utf-8", cwd=None, mode="wrapper_boot", tz="UTC0"):
    e = dict(env); e["PYTHONIOENCODING"] = enc; e["TZ"] = tz
    wrapper, target = repo / f"scripts/{NAME}.py", repo / f"scripts/diagnostics/{NAME}.py"
    cmd = {"wrapper_boot": [sys.executable, *opt, "-c", BOOT, str(wrapper), *argv], "target_boot": [sys.executable, *opt, "-c", BOOT, str(target), *argv],
           "wrapper_plain": [sys.executable, *opt, str(wrapper), *argv], "module_plain": [sys.executable, *opt, "-m", f"scripts.diagnostics.{NAME}", *argv]}[mode]
    r = subprocess.run(cmd, cwd=str(cwd or tmp), env=e, capture_output=True, timeout=120)
    err = r.stderr.decode("utf-8", "replace"); m = re.search(r"BLOCKED_ATTEMPTS=(\d+)", err)
    last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_ATTEMPTS")][-1:] or [""]
    return {"code": r.returncode, "out": r.stdout, "err_last": last[0].replace(str(tmp), "T").replace(str(repo), "REPO")[:140], "attempts": int(m.group(1)) if m else None}
def modes_identical(argv, cwd=None):
    res = {m_: run(argv, mode=m_, cwd=(repo if m_ == "module_plain" else cwd)) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
    base = res["wrapper_boot"]
    check(all(v["code"] == base["code"] and v["out"] == base["out"] for v in res.values()), {k: v["code"] for k, v in res.items()})
    check(base["attempts"] == 0 and res["target_boot"]["attempts"] == 0, "attempts")
    return base
before = tree_hash(tmp); out = {}
CR = str(croot)
j = modes_identical(["--canonical-root", CR, "--day", D, "--json"]); check(j["code"] == 0 and j["err_last"] == "", j)
s = json.loads(j["out"].decode("utf-8")); rows = {r["run_id"]: r for r in s["rows"]}
check(s["day"] == D and s["row_count"] == 10 and "run-monitor-minute-1" not in rows and "run-11" not in rows and s["live_followup"] == [], (s["row_count"], sorted(rows)))
r1 = rows["run-1"]
check(r1["ts_epoch"] == T1e and r1["artifact_age_minutes"] == 10.0 and r1["current_price"] == 100.0 and abs(r1["vwap_distance_pct"] - 2.0) < 1e-9, r1)
est = 100.0 / 1.02; rp = est * (1 - 0.005)
check(abs(r1["reclaim_price"] - rp) < 1e-9 and abs(r1["reclaim_gap_pct"] - ((100.0 / rp) - 1) * 100) < 1e-9 and abs(r1["reclaim_tolerance_pct"] - 0.5) < 1e-9, (r1["reclaim_price"], r1["reclaim_gap_pct"]))
check(abs(r1["breakout_gap_pct"] - ((100.0 / 105.0) - 1) * 100) < 1e-9 and abs(r1["pullback_pct"] - 1.0) < 1e-9 and r1["failed_gates"] == ["g1"] and r1["passed_gates"] == ["g0"] and r1["entry_block_reason"] == "blk" and r1["minute_source_present"] is True, r1)
check(rows["run-6"]["symbol"] == "" and rows["run-6"]["ts_epoch"] is None and rows["run-6"]["artifact_age_minutes"] is None and rows["run-6"]["minute_source_present"] is False, rows["run-6"])
check(rows["run-7"]["current_price"] == 50.0 and rows["run-7"]["reclaim_price"] is None and rows["run-7"]["failed_gates"] == [], rows["run-7"])  # monitor.position_snapshot price; no shadow -> empty gate
check(rows["run-8"]["reclaim_price"] is None and rows["run-8"]["reclaim_gap_pct"] is None, rows["run-8"])   # 1+vd == 0
check(rows["run-9"]["vwap_distance"] is None and rows["run-9"]["reclaim_price"] is None, rows["run-9"])       # NaN guard
check(rows["run-4"]["artifact_age_minutes"] == 3.0 and rows["run-5"]["artifact_age_minutes"] == 2.983, (rows["run-4"]["artifact_age_minutes"], rows["run-5"]["artifact_age_minutes"]))
sg = {(g["symbol"], g["evaluation_summary"]): g for g in s["stale_groups"]}
check(sg[("AAA", "below_vwap_reclaim_not_ready")]["repeat_count"] == 2 and sg[("AAA", "below_vwap_reclaim_not_ready")]["runs"] == ["run-1", "run-2"] and sg[("AAA", "below_vwap_reclaim_not_ready")]["max_artifact_age_minutes"] == 11.0, sg)  # run-2 is one minute later -> age 11
check(("CCC", "edge") in sg and ("DDD", "edge2") not in sg and ("BBB", "other_reason") not in sg and ("EEE", "nosh") not in sg, sorted(sg))  # >=3.0 inclusive; fresh/low-age/no-minute-source excluded
check(s["stale_groups"][0]["repeat_count"] == 2, "sorted by repeat desc")
rs = {(r["symbol"], r["evaluation_summary"]): r["repeat_count"] for r in s["repeated_states"]}; check(rs[("AAA", "below_vwap_reclaim_not_ready")] == 2, rs)
check(s["reason_counts"]["below_vwap_reclaim_not_ready"] == 2 and s["symbol_counts"]["AAA"] == 2 and s["symbol_counts"][""] == 1, (s["reason_counts"], s["symbol_counts"]))
out["rows"] = s["row_count"]; out["stale_groups"] = [(g["symbol"], g["repeat_count"]) for g in s["stale_groups"]]
# filters / thresholds
f = json.loads(run(["--canonical-root", CR, "--day", D, "--reason", "below_vwap_reclaim_not_ready", "--json"])["out"]); check(f["row_count"] == 2 and list(f["reason_counts"]) == ["below_vwap_reclaim_not_ready"], f["row_count"])
th = json.loads(run(["--canonical-root", CR, "--day", D, "--stale-age-min", "11.5", "--json"])["out"]); check([g["symbol"] for g in th["stale_groups"]] == ["HHH"], "threshold 11.5 excludes ages 10 and 11; only the naive-ts row (age 545 under TZ=UTC0) remains")
th0 = json.loads(run(["--canonical-root", CR, "--day", D, "--stale-age-min", "-5", "--json"])["out"]); check(len(th0["stale_groups"]) >= 5, "negative threshold clamps to 0 -> includes fresh ones")
nan_th = run(["--canonical-root", CR, "--day", D, "--stale-age-min", "nan", "--json"]); out["stale_age_nan"] = {"code": nan_th["code"], "stale_groups": len(json.loads(nan_th["out"])["stale_groups"]) if nan_th["code"] == 0 else None}
nod = json.loads(run(["--canonical-root", CR, "--day", "2026-01-01", "--json"])["out"]); check(nod["row_count"] == 0 and nod["stale_groups"] == [], nod)
# text mode
t = modes_identical(["--canonical-root", CR, "--day", D]); tl = t["out"].decode("utf-8").splitlines()
check(tl[0] == "=== Monitor Gate Pattern Check ===" and tl[1] == f"day={D} row_count=10" and "stale_snapshot_groups:" in tl and "rows:" in tl and not any(l.startswith("live_followup") for l in tl), tl[:4])
check(any(l.startswith("  run_id=run-1 symbol=AAA reason=below_vwap_reclaim_not_ready price=100.0") and "age_min=10.0" in l for l in tl), "row line")
# naive timestamp depends on process TZ
na = json.loads(run(["--canonical-root", CR, "--day", D, "--json"], tz="UTC0")["out"]); nk = json.loads(run(["--canonical-root", CR, "--day", D, "--json"], tz="KST-9")["out"])
ra = {r["run_id"]: r for r in na["rows"]}["run-10"]; rk = {r["run_id"]: r for r in nk["rows"]}["run-10"]
check(ra["artifact_age_minutes"] != rk["artifact_age_minutes"] and abs(ra["artifact_age_minutes"] - rk["artifact_age_minutes"]) == 540.0, (ra["artifact_age_minutes"], rk["artifact_age_minutes"]))  # naive ts: UTC vs KST differ by 9h
check({r["run_id"]: r["artifact_age_minutes"] for r in na["rows"] if r["run_id"] != "run-10"} == {r["run_id"]: r["artifact_age_minutes"] for r in nk["rows"] if r["run_id"] != "run-10"}, "tz-aware timestamps are TZ independent")
out["naive_ts_age_min"] = {"UTC": ra["artifact_age_minutes"], "KST": rk["artifact_age_minutes"]}
# default canonical root './reports/canonical' is CWD-relative
da = json.loads(run(["--day", D, "--json"], cwd=cwdA)["out"])["row_count"]; db = json.loads(run(["--day", D, "--json"], cwd=cwdB)["out"])["row_count"]
check(da == 10 and db == 0, (da, db)); out["cwd_relative_default"] = [da, db]
# argv / exits / encodings
a = {"missing_day": run(["--canonical-root", CR])["code"], "unknown": run(["--bogus"])["code"], "stale_not_float": run(["--day", D, "--stale-age-min", "abc"])["code"], "help": run(["--help"])["code"], "bad_day_string": run(["--canonical-root", CR, "--day", "../x", "--json"])["code"]}
check(a == {"missing_day": 2, "unknown": 2, "stale_not_float": 2, "help": 0, "bad_day_string": 0}, a); out["argv"] = a
cp = run(["--canonical-root", CR, "--day", D], enc="cp949"); check(cp["code"] == 0, cp)
# --live-followup is deliberately NOT executed (CompositeSkillRunner.from_env -> market data fetch); assert the flag exists in --help only
hp = run(["--help"])["out"].decode("utf-8"); check("--live-followup" in hp, "flag documented"); out["live_followup"] = "NOT_RUN"
check(tree_hash(tmp) == before, "tmp tree changed by read-only audit")
check(repo_status() == repo_before, "repo working tree changed")
out["tmp_tree_unchanged"] = True; out["repo_tree_unchanged"] = True
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF067_MONITOR_GATE_PATTERNS_OK rows=%d stale_groups=%d reclaim_breakout_math=ok naive_ts_tz_dependent=540min cwd_relative_default=yes live_followup=NOT_RUN argparse=2 child_attempts=0 tree_unchanged=yes debug=%s" % (s["row_count"], len(s["stale_groups"]), "off" if opt else "on"))
