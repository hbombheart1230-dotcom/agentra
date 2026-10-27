# RF-067 P2 independent peer (A for B-owned RF): delegated diagnostics TARGET scripts/diagnostics/check_reports_trades_health.py, run as REAL subprocess
# through (1) the public root wrapper scripts/check_reports_trades_health.py, (2) the target via runpy bootstrap, (3) plain `python wrapper`, (4) `python -m target`.
# Read-only audit on a synthetic tmp reports root (real iter_trade_dirs + real audit; no fakes). Child bootstrap blocks network/subprocess/sqlite and writes (any write-mode open).
# Checks stdout/stderr/exit, empty PATH, cp949/utf-8/ascii stdout encodings with a Hangul trade dir, relative --reports-root (resolved against REPO ROOT, not cwd), repo/tmp tree unchanged.
# Usage: python rf067_reports_trades_health_target_peer.py <repo_root> [-O]
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
tmp = Path(tempfile.mkdtemp(prefix="rf067_rth_")).resolve()
def repo_status(): return subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout
repo_before = repo_status()
def put(p, obj, raw=False): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(obj if raw else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
def tree_hash(root):
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")): h.update((str(p.relative_to(root)) + ("/" if p.is_dir() else "")).encode()); h.update(p.read_bytes() if p.is_file() else b"")
    return h.hexdigest()
rr = tmp / "reports"; D = rr / "trades/2026-10-20"
def sidecars(t): [put(t / n, {}) for n in ("_provenance.json", "_health.json", "_artifact_links.json")]
def llm(t, comp, obj):
    rel = {"ai": "reports/ai_trade_report_llm_response.json", "brief": "reports/brief_llm_response.json", "strat": "reports/strategist_llm_response.json"}[comp]; put(t / rel, obj)
t = D / "TRD_OK"; sidecars(t); llm(t, "ai", {"status": "ok"}); llm(t, "brief", {"status": "ok"}); llm(t, "strat", {"status": "ok"}); put(t / "lifecycle_bundle.json", {"ai_report_diagnostics": {"report_status": "Done"}})
t = D / "TRD_PART_DONE"; llm(t, "ai", {"status": "partial", "required_keys_missing": [1, 2], "meta": {"parse_error": "x" * 200}})
put(t / "ai_trade_report/ai_trade_report.json", {k: {} for k in ("executive_summary", "market_context_at_entry", "why_this_symbol_was_chosen", "entry_decision", "holding_monitoring_story", "exit_decision", "execution_quality", "scanner_filters", "guard_approval_result", "reporter_evaluation", "errors_weaknesses_improvement_points", "final_operator_conclusion")})
t = D / "TRD_PART_BAD"; sidecars(t); llm(t, "ai", {"status": "salvaged", "required_keys_missing": [1], "meta": {"parse_error": "bad"}}); put(t / "lifecycle_bundle.json", {"ai_report_diagnostics": {"report_status": "FAILED"}})
t = D / "TRD_BRIEF"; sidecars(t); llm(t, "brief", {"status": "error", "meta": {"reason": "no key"}})
t = D / "TRD_BRIEF2"; sidecars(t); llm(t, "brief", {"status": "error"})
t = D / "TRD_STRAT"; sidecars(t); llm(t, "strat", {"status": "fallback", "model": "m", "parse_mode": "X", "raw_response_text": "abc"})
t = D / "TRD_STRAT_PH"; sidecars(t); llm(t, "strat", {"status": "fallback", "meta": {"synthetic_placeholder": True}})
t = D / "TRD_STRAT_PH2"; sidecars(t); llm(t, "strat", {"status": "fallback", "model": "", "raw_response_text": "", "error": "", "retry_count": 0})
t = D / "TRD_BROKEN"; sidecars(t); put(t / "reports/ai_trade_report_llm_response.json", "{", raw=True); put(t / "reports/brief_llm_response.json", "[1]", raw=True)
t = D / "TRD_한글"; llm(t, "brief", {"status": "ok"})
put(D / "legacy_1/lifecycle_bundle.json", {})  # not TRD_ but has lifecycle bundle -> detected
put(rr / "trades/2026-10-21/TRD_NEXT/_provenance.json", {})
put(rr / "trades/notes/TRD_SKIPPED/_provenance.json", {}); (rr / "trades/stray.txt").write_text("x")
(tmp / "cwdtrap/reports/trades/2026-10-20/TRD_TRAP").mkdir(parents=True)  # cwd trap for the relative --reports-root check
before_hash = tree_hash(tmp)
env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY"))}
env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "", "PATH": ""})
def run(argv, *, enc="utf-8", cwd=None, mode="wrapper_boot"):
    e = dict(env); e["PYTHONIOENCODING"] = enc
    wrapper, target = repo / "scripts/check_reports_trades_health.py", repo / "scripts/diagnostics/check_reports_trades_health.py"
    cmd = {"wrapper_boot": [sys.executable, *opt, "-c", BOOT, str(wrapper), *argv], "target_boot": [sys.executable, *opt, "-c", BOOT, str(target), *argv],
           "wrapper_plain": [sys.executable, *opt, str(wrapper), *argv], "module_plain": [sys.executable, *opt, "-m", "scripts.diagnostics.check_reports_trades_health", *argv]}[mode]
    r = subprocess.run(cmd, cwd=str(cwd or tmp), env=e, capture_output=True, timeout=120)
    err = r.stderr.decode("utf-8", "replace"); attempts = int(m.group(1)) if (m := re.search(r"BLOCKED_ATTEMPTS=(\d+)", err)) else None
    last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_ATTEMPTS")][-1:] or [""]
    return {"code": r.returncode, "out": r.stdout, "err_last": last[0].replace(str(tmp), "T")[:140], "attempts": attempts}
out = {}
R = str(rr)
# 1) all days, --json via wrapper
j = run(["--reports-root", R, "--json"]); check(j["code"] == 0 and j["attempts"] == 0 and j["err_last"] == "", j)
rep = json.loads(j["out"].decode("utf-8"))
out["json_summary"] = {k: rep[k] for k in ("ok", "trade_dir_count", "llm_status_counts", "lifecycle_report_status_counts", "issue_counts", "severity_counts", "sidecar_counts")}
check(rep["trade_dir_count"] == 12 and rep["ok"] is True, (rep["trade_dir_count"], rep["ok"]))  # 11 TRD_* in 10-20 + legacy_1 ... see below
ic = rep["issue_counts"]; sc = rep["sidecar_counts"]
check(ic == {"diagnostic_status_mismatch": 1, "llm_error": 2, "llm_fallback": 1, "llm_partial": 1, "llm_recovered": 1, "sidecar_missing": sc and ic["sidecar_missing"]}, ic)
check(rep["llm_status_counts"] == {"ai_trade_report:ok": 1, "ai_trade_report:partial": 1, "ai_trade_report:salvaged": 1, "brief:error": 2, "brief:ok": 2, "strategist:fallback": 1, "strategist:ok": 1, "strategist:synthetic_placeholder": 2}, rep["llm_status_counts"])
check(rep["lifecycle_report_status_counts"] == {"done": 1, "failed": 1}, rep["lifecycle_report_status_counts"])
sev = rep["severity_counts"]; check(sev.get("error", 0) == 0 and sev["info"] == 1 and sev["warn"] == sum(ic.values()) - 1, sev)
mm = [i for i in rep["issues"] if i["code"] == "diagnostic_status_mismatch"][0]; check(mm["trade_id"] == "TRD_PART_BAD" and mm["path"].endswith("lifecycle_bundle.json") and mm["component"] == "lifecycle", mm)
check([i["message"] for i in rep["issues"] if i["code"] == "llm_error"] == ["no key", "Brief generation failed without a saved reason."], "brief messages")
check("parse_mode=x raw_response_len=3" in [i["message"] for i in rep["issues"] if i["code"] == "llm_fallback"][0], "fallback message lower-cased parse_mode")
check(any("TRD_한글" in i["path"] for i in rep["issues"]), "hangul trade path reported")
# 2) text mode + --day filters
t_ = run(["--reports-root", R]); check(t_["code"] == 0 and t_["out"].decode("utf-8").startswith("ok=True trade_dir_count=12 issue_counts={"), t_["out"][:80])
d20 = json.loads(run(["--reports-root", R, "--day", "2026-10-20", "--json"])["out"].decode("utf-8")); d21 = json.loads(run(["--reports-root", R, "--day", "2026-10-21", "--json"])["out"].decode("utf-8"))
dnone = json.loads(run(["--reports-root", R, "--day", "2026-01-01", "--json"])["out"].decode("utf-8")); dsp = json.loads(run(["--reports-root", R, "--day", " 2026-10-21 ", "--json"])["out"].decode("utf-8"))
check(d20["trade_dir_count"] == 11 and d21["trade_dir_count"] == 1 and dnone["trade_dir_count"] == 0 and dnone["ok"] is True and dsp["trade_dir_count"] == 1 and dsp["day"] == "2026-10-21", (d20["trade_dir_count"], d21["trade_dir_count"], dnone["trade_dir_count"]))
out["day_filter"] = [d20["trade_dir_count"], d21["trade_dir_count"], dnone["trade_dir_count"], dsp["trade_dir_count"]]
# 3) all four invocation modes produce byte-identical stdout; wrapper == target
modes = {m_: run(["--reports-root", R, "--json"], mode=m_, cwd=(repo if m_ == "module_plain" else tmp)) for m_ in ("wrapper_boot", "target_boot", "wrapper_plain", "module_plain")}
check(all(v["code"] == 0 and v["out"] == modes["wrapper_boot"]["out"] for v in modes.values()), {k: v["code"] for k, v in modes.items()})
check(modes["wrapper_boot"]["attempts"] == 0 and modes["target_boot"]["attempts"] == 0, "child attempts")
out["modes_identical"] = True
# 4) empty PATH worked above (PATH='' in child env); locale / encodings with Hangul path in --json output
e_cp = run(["--reports-root", R, "--json"], enc="cp949"); check(e_cp["code"] == 0 and "TRD_한글" in e_cp["out"].decode("cp949"), e_cp["code"])
e_ascii = run(["--reports-root", R, "--json"], enc="ascii"); out["ascii_stdout"] = {"code": e_ascii["code"], "err": e_ascii["err_last"].split(":")[0], "stdout_len": len(e_ascii["out"])}
check(e_ascii["code"] == 1 and "UnicodeEncodeError" in e_ascii["err_last"], e_ascii)  # crash (traceback), not a silent fail
e_txt_ascii = run(["--reports-root", R], enc="ascii"); check(e_txt_ascii["code"] == 0, e_txt_ascii)  # text summary contains no Hangul
out["ascii_text_mode_code"] = e_txt_ascii["code"]
# 5) argv / exit paths
a = {}
for name, argv in {"help": ["--help"], "unknown_flag": ["--bogus"], "reports_root_missing_arg": ["--reports-root"], "empty_reports_root": ["--reports-root", "", "--json"], "nonexistent_root": ["--reports-root", str(tmp / "nope"), "--json"],
                   "root_is_file": ["--reports-root", str(rr / "trades/stray.txt"), "--json"], "relative_root_resolves_under_repo": ["--reports-root", "rf067_nonexistent_relative_xyz", "--json"]}.items():
    r = run(argv); a[name] = {"code": r["code"], "stdout_head": r["out"].decode("utf-8", "replace").replace(str(tmp), "T").replace(str(repo), "REPO")[:60]}
check(a["help"]["code"] == 0 and a["unknown_flag"]["code"] == 2 and a["reports_root_missing_arg"]["code"] == 2, a)
check(json.loads(run(["--reports-root", str(tmp / "nope"), "--json"])["out"])["trade_dir_count"] == 0 and a["root_is_file"]["code"] == 0, a)
emp = json.loads(run(["--reports-root", "", "--json"])["out"]); out["empty_root_resolves_to"] = emp["reports_root"].replace(str(repo), "REPO")
check(emp["reports_root"] == str(repo / "reports"), emp["reports_root"])  # empty string -> "reports" -> REPO/reports (not cwd)
rel = json.loads(run(["--reports-root", "rf067_nonexistent_relative_xyz", "--json"])["out"]); check(rel["reports_root"] == str(repo / "rf067_nonexistent_relative_xyz") and rel["trade_dir_count"] == 0, rel["reports_root"])
# relative root with a same-named dir in cwd is IGNORED (resolved against repo root, cwd-independent)
trap = json.loads(run(["--reports-root", "reports", "--json"], cwd=tmp / "cwdtrap")["out"]); out["cwd_trap_reports_root"] = trap["reports_root"].replace(str(repo), "REPO")
check(trap["reports_root"] == str(repo / "reports") and all("TRD_TRAP" not in i["path"] for i in trap["issues"]), trap["reports_root"])
out["argv"] = a
# 6) fail-open observation: exit 0 regardless of issue severity; "ok" can only become False for severity=error which this module never emits
check(rep["ok"] is True and ic["llm_partial"] == 1 and j["code"] == 0, "exit 0 despite warnings")
# 7) read-only: no tree change, repo untouched
check(repo_status() == repo_before, "repo working tree changed")
snap_after = tree_hash(tmp)
check(snap_after == before_hash, "tmp reports tree changed by the audit")
out["tmp_tree_unchanged"] = True; out["repo_tree_unchanged"] = True
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF067_REPORTS_TRADES_HEALTH_TARGET_OK trade_dirs=12 modes=4_identical day_filter=11/1/0 empty_PATH=ok cp949=ok ascii_json=crash_exit1 exit_always_0=yes relative_root=repo_anchored child_attempts=0 tree_unchanged=yes debug=%s" % ("off" if opt else "on"))
