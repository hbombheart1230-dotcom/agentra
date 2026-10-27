# RF-063 / RF-067 independent peer (A for B-owned RF): diagnostics CLIs check_log_archive_integrity, check_metrics_schema_v1, check_audit_trail_completeness, check_alert_policy_v1 -- REAL subprocess via the public root wrappers (+ target runpy bootstrap, plain, -m).
# These CLIs WRITE reports (mkdir + json/md) and read cwd-relative defaults (data/logs/events.jsonl, reports/...). The harness runs them with cwd = a tmp dir; writes are allowed ONLY under the tmp root (bootstrap blocks others), network/subprocess/sqlite blocked, PATH empty.
# check_alert_policy_v1 additionally calls load_env_file('.env') from the CWD -> the harness plants a FAKE .env in the tmp cwd (never a real one). Usage: python rf063_check_cli_batch_peer.py <repo_root> [-O]
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



import hashlib as _h
def sha(b): return _h.sha256(b).hexdigest()
env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY", "ALERT_POLICY", "EVENT_LOG_DAY_CACHE_DIR"))}
env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "", "PATH": "", "RF_TMP_ROOT": str(tmp)})
def run(name, argv, *, cwd, mode="wrapper_boot", enc="utf-8", extra_env=None):
    e = dict(env); e["PYTHONIOENCODING"] = enc; e.update(extra_env or {})
    wrapper, target = repo / f"scripts/{name}.py", repo / f"scripts/diagnostics/{name}.py"
    cmd = {"wrapper_boot": [sys.executable, *opt, "-c", BOOT, str(wrapper), *argv], "target_boot": [sys.executable, *opt, "-c", BOOT, str(target), *argv],
           "wrapper_plain": [sys.executable, *opt, str(wrapper), *argv], "module_plain": [sys.executable, *opt, "-m", f"scripts.diagnostics.{name}", *argv]}[mode]
    r = subprocess.run(cmd, cwd=str(cwd), env=e, capture_output=True, timeout=120)
    err = r.stderr.decode("utf-8", "replace"); m = re.search(r"BLOCKED_ATTEMPTS=(\d+)", err)
    last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_ATTEMPTS")][-1:] or [""]
    return {"code": r.returncode, "out": r.stdout.decode("utf-8", "replace").replace(str(tmp), "T").replace(str(repo), "REPO"), "err_last": last[0].replace(str(tmp), "T").replace(str(repo), "REPO")[:160], "attempts": int(m.group(1)) if m else None}
def files(root): return sorted(str(p.relative_to(root).as_posix()) for p in Path(root).rglob("*") if p.is_file())
fresh_n = [0]
def fresh():
    fresh_n[0] += 1; d = tmp / f"w{fresh_n[0]}"; d.mkdir(); return d
out = {}
# ================= A: check_log_archive_integrity
N = "check_log_archive_integrity"; DAY = "2026-10-20"
w = fresh(); arc = w / "arch"; dd = arc / DAY; dd.mkdir(parents=True)
f1 = b'{"a":1}\n{"a":2}\n'; f2 = "한글\nline2\n".encode("utf-8")
(dd / "events.jsonl").write_bytes(f1); (dd / "other.log").write_bytes(f2)
put(dd / "manifest.json", {"files": [{"name": "events.jsonl", "sha256": sha(f1), "bytes": len(f1), "line_count": 2}, {"name": "other.log", "sha256": sha(f2), "bytes": len(f2), "line_count": 2}]})
(arc / "2026-01-01").mkdir()  # stale (> 30 days before target)
rep = w / "rep"
base = ["--archive-dir", str(arc), "--report-dir", str(rep), "--day", DAY, "--json"]
r = run(N, base, cwd=w); p = json.loads(r["out"])
check(r["code"] == 3 and p["ok"] is False and p["file_total"] == 2 and p["verified_total"] == 2 and p["stale_archive_days"] == ["2026-01-01"] and p["failures"] == ["stale_archive_total > 0 (1)"], (r["code"], p["failures"]))
check(files(rep) == [f"log_archive_integrity_{DAY}.json", f"log_archive_integrity_{DAY}.md"], files(rep))
r = run(N, [*base, "--allow-stale"], cwd=w); p = json.loads(r["out"]); check(r["code"] == 0 and p["ok"] is True and p["stale_archive_total"] == 1 and p["failures"] == [], (r["code"], p["failures"]))
ident = {m_: run(N, [*base, "--allow-stale"], cwd=(repo if m_ == "module_plain" else w), mode=m_) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
check(all(v["code"] == 0 and v["out"] == ident["wrapper_boot"]["out"] for v in ident.values()) and ident["wrapper_boot"]["attempts"] == 0, "modes")
# corruption cases
(dd / "events.jsonl").write_bytes(f1 + b"extra\n"); r = run(N, [*base, "--allow-stale"], cwd=w); p = json.loads(r["out"])
check(r["code"] == 3 and set(p["failures"]) == {"hash_mismatch:events.jsonl", "bytes_mismatch:events.jsonl", "line_count_mismatch:events.jsonl"} and p["verified_total"] == 1, p["failures"])
(dd / "events.jsonl").write_bytes(f1); (dd / "other.log").unlink(); r = run(N, [*base, "--allow-stale"], cwd=w); p = json.loads(r["out"]); check(r["code"] == 3 and p["failures"] == ["missing_file:other.log"] and p["missing_file_total"] == 1, p["failures"])
put(dd / "manifest.json", "{bad", raw=True); p = json.loads(run(N, [*base, "--allow-stale"], cwd=w)["out"]); check(p["failures"] == ["manifest missing_or_invalid", "manifest.files empty"], p["failures"])
nod = json.loads(run(N, ["--archive-dir", str(w / "nope"), "--report-dir", str(rep), "--day", "2026-10-21", "--json"], cwd=w)["out"]); check(nod["failures"][0].startswith("archive_day_dir missing") and nod["file_total"] == 0, nod["failures"])
# manifest name path traversal reads outside the archive day dir (hash only)
secret = w / "outside.txt"; secret.write_text("x\n"); put(dd / "manifest.json", {"files": [{"name": "../../outside.txt", "sha256": "", "bytes": 0, "line_count": 0}]})
p = json.loads(run(N, [*base, "--allow-stale"], cwd=w)["out"]); out["A_manifest_traversal_verified"] = p["verified_total"]; check(p["verified_total"] == 1 and p["ok"] is True, p)  # '../..' resolves to an arbitrary file and counts as verified
put(dd / "manifest.json", {"files": [{"name": "events.jsonl", "bytes": "abc"}]}); bad_int = run(N, [*base, "--allow-stale"], cwd=w); out["A_bad_bytes_type"] = {"code": bad_int["code"], "err": bad_int["err_last"].split(":")[0]}; check(bad_int["code"] == 1 and "ValueError" in bad_int["err_last"], bad_int)
# default day is the current UTC date; default paths are CWD-relative
w2 = fresh(); r = run(N, ["--json"], cwd=w2); p = json.loads(r["out"]); out["A_default_paths"] = {"code": r["code"], "archive_dir": p["archive_dir"], "report_files": [re.sub(r"\d{4}-\d{2}-\d{2}", "<utc-today>", f) for f in files(w2)]}
check(r["code"] == 3 and p["archive_dir"] == "data/logs/archive" and re.fullmatch(r"reports/archive_integrity/log_archive_integrity_\d{4}-\d{2}-\d{2}\.json", [f for f in files(w2) if f.endswith(".json")][0]), out["A_default_paths"])
a = {"retention_not_int": run(N, ["--retention-days", "x"], cwd=w2)["code"], "unknown": run(N, ["--bogus"], cwd=w2)["code"], "help": run(N, ["--help"], cwd=w2)["code"], "bad_day": json.loads(run(N, [*base[:-3], "--day", "bad", "--json"], cwd=w)["out"])["stale_archive_total"]}
check(a["retention_not_int"] == 2 and a["unknown"] == 2 and a["help"] == 0, a); out["A_argv"] = a
cp = run(N, ["--archive-dir", str(w / "nope"), "--report-dir", str(rep), "--day", "2026-10-21", "--json"], cwd=w, enc="cp949"); check(cp["code"] == 3, cp)
# ================= B: check_metrics_schema_v1
N = "check_metrics_schema_v1"
w = fresh(); ev = w / "events.jsonl"; ev.write_text("", encoding="utf-8")
r = run(N, ["--event-log-path", str(ev), "--report-dir", str(w / "m"), "--day", DAY, "--json"], cwd=w); pB = json.loads(r["out"])
out["B_empty_events"] = {"code": r["code"], "ok": pB["ok"], "required_total": pB["required_total"], "failure_total": pB["failure_total"], "files": [re.sub(r"\d{4}-\d{2}-\d{2}", "<d>", f) for f in files(w / "m")]}
check(r["code"] in (0, 3) and pB["required_total"] == 11 and (r["code"] == 0) == pB["ok"], out["B_empty_events"])
r2 = run(N, ["--event-log-path", str(w / "missing.jsonl"), "--report-dir", str(w / "m2"), "--day", DAY], cwd=w); out["B_missing_events_text"] = {"code": r2["code"], "first_line": r2["out"].splitlines()[0][:80] if r2["out"] else r2["err_last"]}
idb = {m_: run(N, ["--event-log-path", str(ev), "--report-dir", str(w / "m"), "--day", DAY, "--json"], cwd=(repo if m_ == "module_plain" else w), mode=m_) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
check(all(v["code"] == idb["wrapper_boot"]["code"] and v["out"] == idb["wrapper_boot"]["out"] for v in idb.values()) and idb["wrapper_boot"]["attempts"] == 0, "B modes")
w3 = fresh(); r3 = run(N, ["--json"], cwd=w3); out["B_default_paths"] = {"code": r3["code"], "created": sorted({f.split("/")[0] for f in files(w3)})}
check(r3["code"] in (0, 3, 2) and (not files(w3) or all(f.startswith("reports/metrics/") for f in files(w3))), out["B_default_paths"])
out["B_argv"] = {"unknown": run(N, ["--bogus"], cwd=w3)["code"], "help": run(N, ["--help"], cwd=w3)["code"]}
# ================= C: check_audit_trail_completeness
N = "check_audit_trail_completeness"
w = fresh(); ev = w / "events.jsonl"; ev.write_text("", encoding="utf-8"); rd = w / "au"
r = run(N, ["--event-log-path", str(ev), "--report-dir", str(rd), "--day", DAY, "--json"], cwd=w); pC = json.loads(r["out"])
out["C_empty_events"] = {"code": r["code"], "ok": pC["ok"], "events": pC["events"], "failures": pC["failures"], "files": [re.sub(r"\d{4}-\d{2}-\d{2}", "<d>", f) for f in files(rd)]}
check(r["code"] == 0 and pC["ok"] is True and pC["events"] == 0, out["C_empty_events"])
r = run(N, ["--event-log-path", str(ev), "--report-dir", str(rd), "--day", DAY, "--require-actionable", "--json"], cwd=w); pC2 = json.loads(r["out"])
check(r["code"] == 3 and pC2["failures"] == ["actionable_decision_run_total < 1"], (r["code"], pC2["failures"]))
r = run(N, ["--event-log-path", str(w / "nope.jsonl"), "--report-dir", str(rd), "--json"], cwd=w); out["C_missing_log_no_day"] = {"code": r["code"], "err": r["err_last"].split(":")[0][:40] if r["code"] not in (0, 3) else "-"}
idc = {m_: run(N, ["--event-log-path", str(ev), "--report-dir", str(rd), "--day", DAY, "--json"], cwd=(repo if m_ == "module_plain" else w), mode=m_) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
check(all(v["code"] == 0 and v["out"] == idc["wrapper_boot"]["out"] for v in idc.values()) and idc["wrapper_boot"]["attempts"] == 0, "C modes")
w4 = fresh(); r4 = run(N, ["--json"], cwd=w4); out["C_default_paths"] = {"code": r4["code"], "created": sorted({f.split("/")[0] for f in files(w4)}), "day_when_no_events": json.loads(r4["out"])["day"] if r4["code"] in (0, 3) else None}
out["C_argv"] = {"unknown": run(N, ["--bogus"], cwd=w4)["code"], "help": run(N, ["--help"], cwd=w4)["code"]}
# ================= D: check_alert_policy_v1 (also load_env_file('.env') from CWD)
N = "check_alert_policy_v1"
w = fresh(); ev = w / "events.jsonl"; ev.write_text("", encoding="utf-8")
base_d = ["--event-log-path", str(ev), "--report-dir", str(w / "al"), "--day", DAY, "--json"]
r = run(N, base_d, cwd=w); pD = json.loads(r["out"]); out["D_empty_events"] = {"code": r["code"], "ok": pD["ok"], "alert_total": pD["alert_total"], "fail_on": pD["fail_on"], "severity_total": pD["severity_total"]}
check(r["code"] in (0, 3) and (r["code"] == 0) == pD["ok"], out["D_empty_events"])
# a FAKE .env in cwd changes behavior (fail-on level from env default)
(w / ".env").write_text("ALERT_POLICY_FAIL_ON=warning\n", encoding="utf-8")
r_env = run(N, base_d, cwd=w); pE = json.loads(r_env["out"]); out["D_fake_dotenv_in_cwd"] = {"code": r_env["code"], "fail_on": pE["fail_on"]}
check(pE["fail_on"] == "warning", out["D_fake_dotenv_in_cwd"])  # cwd .env is honoured (env default) -> cwd-dependent policy
(w / ".env").unlink()
r_none = run(N, ["--fail-on", "none", *base_d], cwd=w); check(json.loads(r_none["out"])["fail_on"] == "none", "explicit flag wins")
r_mp = run(N, ["--metrics-json-path", str(w / "nope.json"), "--json"], cwd=w); out["D_metrics_path_missing"] = {"code": r_mp["code"], "stdout": r_mp["out"].strip()[:60]}; check(r_mp["code"] == 2 and r_mp["out"].startswith("ERROR: failed to load metrics json"), r_mp)
put(w / "m.json", {"schema_version": "metrics.v1", "strategist_llm": {"success_rate": 0.1, "circuit_open_rate": 0.9}, "execution": {"intents_created": 10, "intents_approved": 1, "intents_blocked": 9}, "broker_api": {"api_429_rate": 0.5}})
r_m = run(N, ["--metrics-json-path", str(w / "m.json"), "--fail-on", "critical", "--json"], cwd=w); pM = json.loads(r_m["out"]); out["D_bad_metrics"] = {"code": r_m["code"], "ok": pM["ok"], "alert_total": pM["alert_total"], "codes": sorted(a["code"] for a in pM["alerts"])}
check(pM["alert_total"] >= 1 and (r_m["code"] == 0) == pM["ok"], out["D_bad_metrics"])
idd = {m_: run(N, ["--metrics-json-path", str(w / "m.json"), "--fail-on", "critical", "--json"], cwd=(repo if m_ == "module_plain" else w), mode=m_) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
check(all(v["code"] == idd["wrapper_boot"]["code"] and v["out"] == idd["wrapper_boot"]["out"] for v in idd.values()) and idd["wrapper_boot"]["attempts"] == 0, "D modes")
out["D_argv"] = {"bad_fail_on": run(N, ["--fail-on", "bogus"], cwd=w)["code"], "unknown": run(N, ["--bogus"], cwd=w)["code"], "help": run(N, ["--help"], cwd=w)["code"]}
check(out["D_argv"] == {"bad_fail_on": 2, "unknown": 2, "help": 0}, out["D_argv"])
check(repo_status() == repo_before, "repo working tree changed")
out["repo_tree_unchanged"] = True
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF063_CHECK_CLI_BATCH_OK targets=4 modes=4_identical log_archive=hash/bytes/lines/missing/stale/traversal metrics_schema=ok audit_trail=ok alert_policy=fail_on+cwd_.env defaults=cwd_relative writes_only_under_tmp=yes repo_tree_unchanged=yes debug=%s" % ("off" if opt else "on"))
