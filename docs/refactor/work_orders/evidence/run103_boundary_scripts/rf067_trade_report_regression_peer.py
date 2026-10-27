# RF-067 P2 independent peer (A for B-owned RF): delegated diagnostics target scripts/diagnostics/check_trade_report_runtime_regression.py, REAL subprocess through the public root wrapper (+ target runpy bootstrap, plain, -m).
# Only the read-only validation mode (--skip-repair --skip-local-debug, no --llm-acceptance) is executed against a synthetic tmp reports root. The DEFAULT mode shells out to scripts/run_live_execution_bundle_report.py (repair, writes under reports/dev/...) and scripts/run_ai_trade_report_batch.py (regeneration);
# it is exercised ONLY under the bootstrap that BLOCKS subprocess to prove it tries to spawn them (nothing runs). --llm-acceptance (network/LLM) is NOT_RUN. Usage: python rf067_trade_report_regression_peer.py <repo_root> [-O]
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



sys.path.insert(0, str(repo))
from libs.reporting.llm_artifacts import trade_artifact_paths  # pure path mapping
NAME = "check_trade_report_runtime_regression"
rr = tmp / "reports"; D = "2026-10-20"
def write_trade(tid, *, entry=None, hold=None, exit_=None, bundle=None, story=None, report=None, prov=None, health=None, md=True):
    tp = trade_artifact_paths(rr, D, tid)
    for key, obj in (("entry_json", entry), ("hold_json", hold), ("exit_json", exit_), ("lifecycle_bundle_json", bundle), ("ai_trade_report_input_json", story), ("ai_trade_report_json", report), ("trade_provenance_json", prov), ("trade_health_json", health)):
        if obj is not None: put(tp[key], obj)
    if md: tp["ai_trade_report_md"].parent.mkdir(parents=True, exist_ok=True); tp["ai_trade_report_md"].write_text("# r\n", encoding="utf-8")
GOOD = dict(entry={"run_id": "r1", "ts": "2026-10-20T09:01:00+09:00", "price": 100}, hold={"hold_duration": "00:05:00", "hold_duration_sec": 300}, exit_={"run_id": "r2", "ts": "2026-10-20T09:06:00+09:00", "reason_human": "tp"},
            bundle={"status": "closed", "linked_run_ids": ["r1", "r2"], "hold_duration": "00:05:00"}, story={"selected_rank": 1, "candidate_count": 5, "symbol": "005930", "selected_symbol": "005930", "status": "closed", "action": "SELL"},
            report={"generation": {"status": "ok"}, "section_provenance": {"a": {"source": "llm"}}}, prov={"lifecycle_status": "closed", "trade_origin": "full", "lifecycle_completeness": "complete"}, health={"lifecycle_status": "closed"})
write_trade("TRD_OK", **GOOD)
write_trade("TRD_BAD", entry={"price": 100}, hold={"hold_duration": "00:00:00", "hold_duration_sec": 0}, exit_={"ts": "2026-10-20T09:06:00+09:00"}, bundle={"status": "closed", "same_day_reporter_linkage": {"status": "missing", "reporter_analysis_json_path": "/x.json"}},
            story={"selected_rank": 0, "candidate_count": 0, "symbol": "A", "selected_symbol": "B", "status": "open", "action": "SELL"}, report={"generation": {"status": "failed"}, "section_provenance": {"a": {"source": "fallback"}, "b": {"source": "unknown"}}}, prov={"lifecycle_status": "closed"}, md=False)
write_trade("TRD_OPEN_SELL", entry={"run_id": "r1", "ts": "t"}, bundle={"status": "open"}, story={"action": "SELL", "status": "open", "selected_rank": 1, "candidate_count": 1}, report=None, prov={"lifecycle_status": "open"}, md=True)
write_trade("TRD_PARTIAL", entry={}, exit_={"run_id": "r9", "ts": "t"}, bundle={"status": "exited", "linked_run_ids": ["r9"]}, story={"selected_rank": 1, "candidate_count": 2, "hold_duration": "00:01:00"}, prov={"trade_origin": "recovered_partial", "lifecycle_completeness": "full"})
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
    return {"code": r.returncode, "out": r.stdout, "err_last": last[0].replace(str(tmp), "T").replace(str(repo), "REPO")[:160], "attempts": int(m.group(1)) if m else None}
def modes_identical(argv):
    res = {m_: run(argv, mode=m_) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
    base = res["wrapper_boot"]
    check(all(v["code"] == base["code"] and v["out"] == base["out"] for v in res.values()), {k: (v["code"], v["err_last"]) for k, v in res.items()})
    check(base["attempts"] == 0 and res["target_boot"]["attempts"] == 0, ("attempts", base["attempts"], base["err_last"]))
    return base
SAFE = ["--reports-root", str(rr), "--skip-repair", "--skip-local-debug"]
before = tree_hash(tmp); out = {}
def case(*specs): return [a for s_ in specs for a in ("--case", s_)]
j = modes_identical([*SAFE, *case(f"{D}:TRD_OK"), "--json"]); p = json.loads(j["out"].decode("utf-8"))
v = p["rows"][0]["validation"]
check(j["code"] == 0 and p["ok"] is True and p["case_count"] == 1 and p["failed_case_count"] == 0 and v["ok"] is True and v["failures"] == [] and v["closed_trade"] is True and v["hold_duration"] == "00:05:00" and v["selected_rank"] == 1 and v["candidate_count"] == 5 and v["linked_run_ids"] == ["r1", "r2"], (j["code"], v))
check(p["rows"][0]["resolved_target_run_id"] == "r2" and p["rows"][0]["repair"]["skipped"] is True and p["rows"][0]["local_debug_regen"]["skipped"] is True and p["rows"][0]["llm_acceptance"]["skipped"] is True, "target_run_id=exit run; stages skipped")
out["ok_case"] = {"code": j["code"], "target": p["rows"][0]["resolved_target_run_id"]}
t = modes_identical([*SAFE, *case(f"{D}:TRD_OK")]).get("out").decode("utf-8").splitlines()
check(t[0] == f"[PASS] {D} TRD_OK" and t[1] == "  target_run_id=r2" and t[2] == "  repair=skip local_debug=skip llm=skip" and t[-1] == "[summary] cases=1 failed=0", t)
# failing cases (exit 1) with the exact failure codes
fb = modes_identical([*SAFE, *case(f"{D}:TRD_BAD"), "--json"]); pb = json.loads(fb["out"].decode("utf-8")); fv = pb["rows"][0]["validation"]
exp_bad = {"missing_artifact:ai_trade_report_md", "missing_artifact:ai_trade_report_json" if False else "closed_trade_missing_exit_run_id", "closed_trade_missing_linked_run_ids", "closed_trade_missing_entry_run_id", "closed_trade_missing_entry_ts",
           "closed_trade_fake_or_missing_hold_duration", "closed_trade_zero_hold_duration_sec", "closed_trade_selected_rank_zero", "closed_trade_candidate_count_zero", "story_input_status_conflicts_with_authoritative_status",
           "selected_symbol_mismatch_story_symbol", "ai_trade_report_generation_status_bad", "ai_trade_report_all_section_provenance_fallback", "reporter_linkage_missing_but_artifact_path_populated"}
got = set(fv["failures"]); check(fb["code"] == 1 and pb["ok"] is False and pb["failed_case_count"] == 1 and exp_bad <= got, (fb["code"], sorted(exp_bad - got)))
out["bad_case_failures"] = sorted(got)
miss = json.loads(modes_identical([*SAFE, *case(f"{D}:TRD_MISSING"), "--json"])["out"])["rows"][0]["validation"]; check(len([f for f in miss["failures"] if f.startswith("missing_artifact:")]) == 7 and miss["closed_trade"] is False, miss["failures"])
os_ = json.loads(modes_identical([*SAFE, *case(f"{D}:TRD_OPEN_SELL"), "--json"])["out"])["rows"][0]["validation"]; check("story_input_action_conflicts_with_open_trade" in os_["failures"] and os_["authoritative_status"] == "open" and os_["closed_trade"] is False, os_["failures"])
pa = json.loads(modes_identical([*SAFE, *case(f"{D}:TRD_PARTIAL"), "--json"])["out"])["rows"][0]["validation"]; check("thin_entry_evidence_not_marked_partial" in pa["failures"] and pa["closed_trade"] is True, pa["failures"])  # closed (exit evidence), no entry evidence, completeness!=partial
out["other_failures"] = {"open_sell": sorted(os_["failures"])[:3], "partial": sorted(pa["failures"])}
# mixed run: summary counts, dedupe of identical (day,trade) specs, explicit run id wins for target_run_id
mx = modes_identical([*SAFE, *case(f"{D}:TRD_OK", f"{D}:TRD_BAD", f"{D}:TRD_OK:r77"), "--json"]); pm = json.loads(mx["out"].decode("utf-8"))
check(mx["code"] == 1 and pm["case_count"] == 2 and pm["failed_case_count"] == 1, (pm["case_count"], pm["failed_case_count"]))  # duplicate (day, trade) collapsed; first spec kept
mr = json.loads(run([*SAFE, *case(f"{D}:TRD_OK:r77"), "--json"])["out"])["rows"][0]; check(mr["requested_target_run_id"] == "r77" and mr["resolved_target_run_id"] == "r77", mr["resolved_target_run_id"])
tm = modes_identical([*SAFE, *case(f"{D}:TRD_OK", f"{D}:TRD_BAD")]).get("out").decode("utf-8").splitlines(); check(f"[FAIL] {D} TRD_BAD" in tm and "  failures: " in "\n".join(tm) and tm[-1] == "[summary] cases=2 failed=1", tm[-3:])
# golden default cases (no --case) against the tmp root -> all FAIL (missing artifacts) exit 1
g = modes_identical(["--reports-root", str(rr), "--skip-repair", "--skip-local-debug", "--json"]); pg = json.loads(g["out"]); check(g["code"] == 1 and pg["case_count"] == 3 and pg["failed_case_count"] == 3, (g["code"], pg["case_count"]))
out["golden_default_cases"] = [(r_["day"], r_["trade_id"]) for r_ in pg["rows"]]
# invalid args
a = {"bad_case": run([*SAFE, "--case", "nocolon"]), "empty_case_parts": run([*SAFE, "--case", ":x"]), "unknown": run(["--bogus"]), "help": run(["--help"]), "max_runs_nan": run([*SAFE, "--max-runs", "abc"]), "relative_root": run(["--reports-root", "nonexistent_rel_xyz", "--skip-repair", "--skip-local-debug", "--case", f"{D}:TRD_OK"])}
check(a["bad_case"]["code"] == 1 and "ValueError" in a["bad_case"]["err_last"] and a["empty_case_parts"]["code"] == 1 and a["unknown"]["code"] == 2 and a["help"]["code"] == 0 and a["max_runs_nan"]["code"] == 2 and a["relative_root"]["code"] == 1, {k: (v["code"], v["err_last"][:60]) for k, v in a.items()})
out["argv"] = {k: v["code"] for k, v in a.items()}
# DEFAULT mode (no --skip-*): proves the CLI tries to spawn effectful helpers; subprocess is BLOCKED by the bootstrap so nothing runs
d = run(["--reports-root", str(rr), "--case", f"{D}:TRD_OK", "--json"])
check(d["code"] == 1 and (d["attempts"] or 0) >= 1 and "blocked" in d["err_last"].lower(), d)
out["default_mode_spawns_helpers_when_blocked"] = {"code": d["code"], "subprocess_attempts": d["attempts"]}
dnone = run(["--reports-root", str(rr), "--case", f"{D}:TRD_MISSING", "--skip-local-debug", "--json"]); out["default_repair_without_run_id"] = {"code": dnone["code"], "attempts": dnone["attempts"]}  # no target run id -> repair skipped, no spawn
check(dnone["code"] == 1 and dnone["attempts"] == 0, dnone)
cp = run([*SAFE, *case(f"{D}:TRD_OK")], enc="cp949"); check(cp["code"] == 0, cp)
check(tree_hash(tmp) == before, "tmp tree changed by validation-only mode"); check(repo_status() == repo_before, "repo working tree changed")
out["repo_tree_unchanged"] = True; out["llm_acceptance"] = "NOT_RUN"
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF067_TRADE_REPORT_REGRESSION_OK validation_only_mode=read_only cases=ok/bad/missing/open_sell/partial exit=0/1 default_mode=spawns_helpers(blocked) llm_acceptance=NOT_RUN modes=4_identical repo_tree_unchanged=yes debug=%s" % ("off" if opt else "on"))
