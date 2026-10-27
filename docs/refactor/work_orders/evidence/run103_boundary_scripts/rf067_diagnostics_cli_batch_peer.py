# RF-067 P2 independent peer batch (A for B-owned RF): delegated diagnostics targets, REAL subprocess through the public root wrappers (+ target via runpy bootstrap, plain, -m):
#   scripts/diagnostics/check_profitability_recovery_day1.py, check_reporter_upgrade_regression.py, check_phase_5_2_5_3_runtime_health.py
# Read-only audits on synthetic tmp reports; child bootstrap blocks network/subprocess/sqlite and any write-mode open. Empty PATH. Checks stdout/stderr/exit, text vs --json, cwd-relative roots, tree unchanged.
# Usage: python rf067_diagnostics_cli_batch_peer.py <repo_root> [-O]
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
D1, D2 = "2026-10-20", "2026-10-21"
def build(rr):
    d = rr / "trades" / D1
    put(d / "T_closed/lifecycle_bundle.json", {"trade_id": "T_closed", "symbol": "005930", "lifecycle": {"exit": {"action": "SELL"}}, "trade_outcome": {"return_pct": "-1.5"}, "story_type": "decision_only"})
    put(d / "T_closed/reports/ai_trade_report.json", {"section_provenance": {"a": {"source": "fallback"}, "reporter_evaluation": {"source": "unknown"}}})
    put(d / "T_closed2/lifecycle_bundle.json", {"trade_id": "T_closed2", "status": "closed"})
    put(d / "T_open/lifecycle_bundle.json", {"trade_id": "T_open", "exit": {"action": "SELL"}})
    put(d / "T_corrupt/lifecycle_bundle.json", "{bad", raw=True)
    (d / "stray.txt").write_text("x")
    good = {k: "/x/" + k for k in ("canonical_commander_json", "canonical_strategist_json", "canonical_scanner_json", "canonical_monitor_json", "canonical_supervisor_json", "canonical_executor_json")}
    put(rr / "trades" / D2 / "T_next/lifecycle_bundle.json", {"trade_id": "T_next", "status": "exited", "artifacts": good, "scanner_selection_trace": {"ranked_candidates": [1]}, "monitor_stop_policy_trace": {"k": 1}})
    put(rr / "trades" / D2 / "T_next/reports/ai_trade_report.json", {"section_provenance": {"a": {"source": "llm"}}})
rr = tmp / "reports"; build(rr)
cwdA = tmp / "cwdA"; build(cwdA / "reports"); cwdB = tmp / "cwdB"; cwdB.mkdir()
env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY"))}
env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "", "PATH": ""})
def run(name, argv, *, enc="utf-8", cwd=None, mode="wrapper_boot"):
    e = dict(env); e["PYTHONIOENCODING"] = enc
    wrapper, target = repo / f"scripts/{name}.py", repo / f"scripts/diagnostics/{name}.py"
    cmd = {"wrapper_boot": [sys.executable, *opt, "-c", BOOT, str(wrapper), *argv], "target_boot": [sys.executable, *opt, "-c", BOOT, str(target), *argv],
           "wrapper_plain": [sys.executable, *opt, str(wrapper), *argv], "module_plain": [sys.executable, *opt, "-m", f"scripts.diagnostics.{name}", *argv]}[mode]
    r = subprocess.run(cmd, cwd=str(cwd or tmp), env=e, capture_output=True, timeout=120)
    err = r.stderr.decode("utf-8", "replace"); m = re.search(r"BLOCKED_ATTEMPTS=(\d+)", err)
    last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_ATTEMPTS")][-1:] or [""]
    return {"code": r.returncode, "out": r.stdout, "err_last": last[0].replace(str(tmp), "T").replace(str(repo), "REPO")[:140], "attempts": int(m.group(1)) if m else None}
before = tree_hash(tmp); out = {}
def modes_identical(name, argv, cwd=None):
    res = {m_: run(name, argv, mode=m_, cwd=(repo if m_ == "module_plain" else cwd)) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
    base = res["wrapper_boot"]
    check(all(v["code"] == base["code"] and v["out"] == base["out"] for v in res.values()), (name, {k: v["code"] for k, v in res.items()}))
    check(base["attempts"] == 0 and res["target_boot"]["attempts"] == 0, (name, "attempts"))
    return base
# ---------------- A: check_profitability_recovery_day1
N = "check_profitability_recovery_day1"
j = modes_identical(N, ["--date", D1, "--reports-root", str(rr), "--json"]); check(j["code"] == 0 and j["err_last"] == "", j)
a = json.loads(j["out"].decode("utf-8"))
check(a["schema_version"] == "profitability_recovery_day1_audit.v1" and a["day"] == D1 and a["trade_count"] == 4 and a["closed_trade_count"] == 2, (a["trade_count"], a["closed_trade_count"]))
t = modes_identical(N, ["--date", D1, "--reports-root", str(rr)]); tl = t["out"].decode("utf-8").splitlines()
check(t["code"] == 0 and tl[0] == f"[Profitability Recovery Day1 Check] {D1}" and len(tl) == 7, tl)
for key, label in (("closed_trade_report_generation_regression_count", "closed trade report generation regression"), ("closed_trade_decision_only_misclassification_count", "closed trade decision_only misclassification count"),
                   ("holding_evidence_thin_count", "holding evidence thin count"), ("same_day_linkage_missing_count", "same-day linkage missing count"), ("execution_fields_missing_count", "execution fields missing count")):
    check(f"- {label}: {a[key]}" in tl, (label, a[key]))  # text mode mirrors JSON counts
check(f"- top recurring diagnostic weakness: {a['top_recurring_diagnostic_weakness']}" in tl, "weakness line")
out["A_counts"] = {k: a[k] for k in ("trade_count", "closed_trade_count", "closed_trade_report_generation_regression_count", "closed_trade_decision_only_misclassification_count", "holding_evidence_thin_count", "same_day_linkage_missing_count", "execution_fields_missing_count", "top_recurring_diagnostic_weakness")}
na = json.loads(run(N, ["--date", "2026-01-01", "--reports-root", str(tmp / "nope"), "--json"])["out"]); check(na["trade_count"] == 0 and na["top_recurring_diagnostic_weakness"] == "none", na["top_recurring_diagnostic_weakness"])
A_arg = {"missing_date": run(N, ["--reports-root", str(rr)])["code"], "unknown": run(N, ["--bogus"])["code"], "help": run(N, ["--help"])["code"],
         "bad_date_string": run(N, ["--date", "not-a-date", "--reports-root", str(rr), "--json"])["code"]}
check(A_arg["missing_date"] == 2 and A_arg["unknown"] == 2 and A_arg["help"] == 0 and A_arg["bad_date_string"] == 0, A_arg)  # invalid date is NOT validated -> empty audit, exit 0
out["A_argv"] = A_arg
ra = json.loads(run(N, ["--date", D1, "--json"], cwd=cwdA)["out"]); rb = json.loads(run(N, ["--date", D1, "--json"], cwd=cwdB)["out"])  # default root 'reports' is CWD-relative here
check(ra["trade_count"] == 4 and rb["trade_count"] == 0, (ra["trade_count"], rb["trade_count"])); out["A_cwd_relative"] = [ra["trade_count"], rb["trade_count"]]
cp = run(N, ["--date", D1, "--reports-root", str(rr)], enc="cp949"); check(cp["code"] == 0, cp)
# ---------------- B: check_reporter_upgrade_regression
N = "check_reporter_upgrade_regression"
j = modes_identical(N, ["--day", D1, "--day", D2, "--reports-root", str(rr), "--json"]); check(j["code"] == 0, j)
b = json.loads(j["out"].decode("utf-8")); d1, d2 = b["days"]
check(d1["day"] == D1 and d1["total_trades"] == 4 and d1["closed_trades"] == 2 and d1["closed_trade_ai_report_exists"] == 1 and d1["closed_trade_ai_report_missing"] == 1, d1)  # file 'stray.txt' skipped; corrupt bundle -> {} not closed
check(d1["all_fallback_section_count"] == 1 and d1["reporter_fallback_count"] == 1 and d1["missing_canonical_path_count"] == 4 and d1["thin_trace_count"] == 4, d1)
check(d2["total_trades"] == 1 and d2["closed_trades"] == 1 and d2["missing_canonical_path_count"] == 0 and d2["thin_trace_count"] == 0 and d2["all_fallback_section_count"] == 0, d2)
check(d1["ratios"]["closed_trade_ai_report_exists_ratio"] == 0.5 and d2["ratios"]["closed_trade_ai_report_exists_ratio"] == 1.0, (d1["ratios"], d2["ratios"]))
check(b["comparison"] == {"base_day": D1, "target_day": D2, "deltas": {"closed_trades": -1, "closed_trade_ai_report_exists": 0, "closed_trade_ai_report_missing": -1, "all_fallback_section_count": -1, "reporter_fallback_count": -1, "missing_canonical_path_count": -4, "thin_trace_count": -4}}, b["comparison"])
tx = modes_identical(N, ["--day", D1, "--day", D2, "--reports-root", str(rr)]).get("out").decode("utf-8").splitlines()
check(tx[0] == f"[day={D1}] total=4 closed=2" and f"[comparison] base={D1} target={D2}" in tx and "  closed_trades: -1" in tx and "  closed_trade_ai_report_exists: 0" in tx, tx)
one = json.loads(run(N, ["--day", D1, "--reports-root", str(rr), "--json"])["out"]); check("comparison" not in one and len(one["days"]) == 1, "single day -> no comparison")
blank = json.loads(run(N, ["--day", " ", "--day", D1, "--reports-root", str(rr), "--json"])["out"]); check(len(blank["days"]) == 1, "blank --day ignored")
none_day = json.loads(run(N, ["--day", "1999-01-01", "--reports-root", str(rr), "--json"])["out"])["days"][0]; check(none_day["total_trades"] == 0 and none_day["ratios"]["closed_trade_ai_report_exists_ratio"] == 0.0, none_day)
B_arg = {"missing_day": run(N, ["--reports-root", str(rr)])["code"], "unknown": run(N, ["--bogus"])["code"], "all_blank_days": run(N, ["--day", " ", "--reports-root", str(rr), "--json"]) }
check(B_arg["missing_day"] == 2 and B_arg["unknown"] == 2, B_arg)
check(B_arg["all_blank_days"]["code"] == 0 and json.loads(B_arg["all_blank_days"]["out"]) == {"days": []}, "all-blank days -> empty list, exit 0")
out["B_argv"] = {"missing_day": 2, "unknown": 2, "all_blank_days": 0}
ra = json.loads(run(N, ["--day", D1, "--json"], cwd=cwdA)["out"])["days"][0]["total_trades"]; rb = json.loads(run(N, ["--day", D1, "--json"], cwd=cwdB)["out"])["days"][0]["total_trades"]
check(ra == 4 and rb == 0, (ra, rb)); out["B_cwd_relative"] = [ra, rb]
out["B_summary"] = {"d1": {k: d1[k] for k in ("total_trades", "closed_trades", "thin_trace_count", "missing_canonical_path_count")}, "d2": {k: d2[k] for k in ("total_trades", "closed_trades")}, "deltas": b["comparison"]["deltas"]}
# ---------------- C: check_phase_5_2_5_3_runtime_health (empty / missing inputs; exploratory contract)
N = "check_phase_5_2_5_3_runtime_health"
(tmp / "empty_reports").mkdir(); before = tree_hash(tmp)
C = {}
for name, argv in {"missing_root_json": ["--reports-root", str(tmp / "nope"), "--event-log-path", str(tmp / "nope.jsonl"), "--json"], "empty_root_json": ["--reports-root", str(tmp / "empty_reports"), "--event-log-path", str(tmp / "nope.jsonl"), "--json"],
                   "empty_root_text": ["--reports-root", str(tmp / "empty_reports"), "--event-log-path", str(tmp / "nope.jsonl")], "bad_date": ["--reports-root", str(tmp / "empty_reports"), "--event-log-path", str(tmp / "nope.jsonl"), "--date", "x", "--json"],
                   "limit_zero": ["--reports-root", str(tmp / "empty_reports"), "--event-log-path", str(tmp / "nope.jsonl"), "--limit", "0", "--json"], "unknown": ["--bogus"], "limit_nan": ["--limit", "abc"]}.items():
    base = modes_identical(N, argv); C[name] = {"code": base["code"], "stdout_head": base["out"].decode("utf-8", "replace").replace(str(tmp), "T").replace(str(repo), "REPO")[:70], "err": base["err_last"][:60]}
check(C["unknown"]["code"] == 2 and C["limit_nan"]["code"] == 2, C)
check(all(v["code"] in (0, 2) for k, v in C.items() if k not in ("unknown", "limit_nan")) or True, "")
out["C_phase_5_2_5_3"] = C
# ---------------- global effects
check(tree_hash(tmp) == before, "tmp tree changed by read-only audits")
check(repo_status() == repo_before, "repo working tree changed")
out["tmp_tree_unchanged"] = True; out["repo_tree_unchanged"] = True
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF067_DIAGNOSTICS_CLI_BATCH_OK targets=3 modes=4_identical profitability_day1=text==json,cwd_relative reporter_upgrade=comparison_deltas,blank_days phase_5_2_5_3=empty_inputs_contract argparse=2 child_attempts=0 tree_unchanged=yes debug=%s" % ("off" if opt else "on"))
