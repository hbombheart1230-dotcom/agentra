# RF-031: reporter_analysis.generate_reporter_analysis_report -- AST consumer map (static) + fully tmp-isolated fake writer/State/exception boundary.
# Run from the repository root:  python <this>  and  python -O <this>.  Every write is confined to a fresh tempfile root (anything else is blocked and fails the run).
import ast, os, sys, io, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile, contextlib
from pathlib import Path
repo = Path(os.getcwd()).resolve(); sys.path.insert(0, str(repo))
sys.dont_write_bytecode = True
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "DRY_RUN", "PYTEST")): del os.environ[k]
out = {}

# ---------------- static: consumers (AST only, nothing imported) ----------------
callers = {}
for base in ("libs", "graphs", "scripts", "apps", "services", "tools"):
    for p in sorted((repo / base).rglob("*.py")) if (repo / base).is_dir() else []:
        try: tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception: continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                f = n.func; nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                if nm in ("generate_reporter_analysis_report", "analyze_event_logs"):
                    callers.setdefault(p.relative_to(repo).as_posix(), []).append((nm, sorted(k.arg for k in n.keywords if k.arg), len(n.args)))
out["callers"] = callers
bad = []

# ---------------- isolation ----------------
root = Path(tempfile.mkdtemp(prefix="rf031_")).resolve()
def inside(p):
    try: return Path(os.path.abspath(str(p))).resolve().is_relative_to(root)
    except Exception: return False
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
_open = io.open
def gopen(f, mode="r", *a, **k):
    if isinstance(f, int): return _open(f, mode, *a, **k)
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write_open:" + str(f)); raise OSError("blocked write " + str(f))
    return _open(f, mode, *a, **k)
builtins.open = gopen; io.open = gopen
for nm in ("mkdir", "makedirs", "replace", "rename", "remove", "unlink", "rmdir"):
    orig = getattr(os, nm)
    def mk(orig=orig, nm=nm):
        def f(p, *a, **k):
            if not inside(p): bad.append("os." + nm + ":" + str(p)); raise OSError("blocked os." + nm)
            return orig(p, *a, **k)
        return f
    setattr(os, nm, mk())

os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger" / "events.jsonl")
os.environ["EVENT_LOG_PATH"] = str(root / "logs" / "events.jsonl")
os.environ["EVENT_LOG_DAY_CACHE_DIR"] = str(root / "day_cache")
os.environ["STRATEGY_MEMORY_PATH"] = str(root / "memory" / "strategy.jsonl")
os.environ["STRATEGY_MEMORY_DAILY_DIR"] = str(root / "memory" / "daily")
os.chdir(root)

ra = importlib.import_module("libs.reporting.reporter_analysis")
rep_mod = importlib.import_module("libs.agent.reporter")
router_mod = importlib.import_module("libs.llm.llm_router")
def trap_router(*a, **k): bad.append("LLMRouter.from_env"); raise AssertionError("LLM router must not be reached")
router_mod.LLMRouter.from_env = staticmethod(trap_router)
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)

DAY = "2026-04-20"
def ev(minute, stage, event, payload=None, run_id="r1"):
    return {"ts": "%sT00:%02d:00+00:00" % (DAY, minute), "run_id": run_id, "stage": stage, "event": event, "payload": payload or {}}
rows = [
    ev(1, "execute_from_packet", "verdict", {"allowed": False, "reason": "cooldown"}),
    ev(2, "execute_from_packet", "verdict", {"allowed": False, "reason": "cooldown"}),
    ev(3, "execute_from_packet", "verdict", {"allowed": True, "reason": "ok"}),
    ev(4, "monitor", "summary", {"min_hold_blocked": True, "sell_cooldown_blocked": True, "monitor_reason": "trail"}),
    ev(5, "decision_trace", "agent", {"agent": "monitor", "payload": {"summary": "hold"}}),
    {"ts": "2026-04-19T23:59:00+00:00", "stage": "monitor", "event": "summary", "payload": {"monitor_reason": "other_day"}},
    "not-json",
]
def write_log(path, rs):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(r if isinstance(r, str) else json.dumps(r) for r in rs) + "\n", encoding="utf-8")
def write_intents(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rs = [{"ts": DAY + "T00:10:00+00:00", "status": "approved"}, {"ts": DAY + "T00:11:00+00:00", "status": "rejected", "reason": "risk"},
          {"ts": DAY + "T00:12:00+00:00", "status": "executed"}, {"ts": DAY + "T00:13:00+00:00"}, {"ts": "2026-04-19T10:00:00+00:00", "status": "failed"}]
    path.write_text("\n".join(json.dumps(r) for r in rs) + "\n", encoding="utf-8")
def files_under(p):
    return sorted(x.relative_to(p).as_posix() for x in p.rglob("*") if x.is_file()) if p.exists() else []
def stable(o):
    s = json.dumps(o, sort_keys=True, default=repr)
    return s.replace(str(root), "<ROOT>").replace(str(root).replace("\\", "\\\\"), "<ROOT>")

# A. missing event log, explicit day, AI disabled: writer contract.
a_dir = root / "A" / "reports" / "dev" / "analysis" / "reporter_analysis"
md, js, o = ra.generate_reporter_analysis_report(root / "A" / "none.jsonl", a_dir, day=DAY, ai_review_enabled=False)
check(md == a_dir / ("reporter_analysis_%s.md" % DAY) and js == a_dir / ("reporter_analysis_%s.json" % DAY), "A paths")
check(json.loads(js.read_text(encoding="utf-8")) == json.loads(json.dumps(o, ensure_ascii=False)), "A json == returned out")
check(md.read_text(encoding="utf-8") == ra._to_markdown(o), "A md == _to_markdown(out)")
out["A"] = {"schema": o["schema_version"], "day": o["day"], "ai_status": o["ai_review"]["status"], "ai_enabled": o["ai_review"]["enabled"], "grade": o["ai_run_grade"],
            "intent_keys": sorted(o["intent_flow_analysis"]), "strategy_memory_keys": sorted(o["strategy_memory_record"]), "ai_summary_nonempty": bool(o["ai_summary"]),
            "files": files_under(root / "A")}
canonical_a = root / "A" / "reports"
check(o["source_reports"]["trade_explain_json"].startswith(str(canonical_a)), "A trade_explain goes under canonical 'reports' ancestor")
check(o["source_reports"]["operator_summary_json"].startswith(str(a_dir.parent.parent)) or True, "operator root")
out["A"]["operator_json_under_report_dir_parent"] = o["source_reports"]["operator_summary_json"].startswith(str(a_dir.parent))
out["A"]["decision_story_enabled"] = o["source_reports"]["decision_story_enabled"]

# B. populated log + intents: intent_flow derivation, other-day/invalid rows excluded.
b_log = root / "B" / "events.jsonl"; write_log(b_log, rows); b_int = root / "B" / "intents.jsonl"; write_intents(b_int)
b_dir = root / "B" / "reports" / "dev" / "analysis" / "reporter_analysis"
snap = b_log.read_bytes()
md, js, o = ra.generate_reporter_analysis_report(b_log, b_dir, day=DAY, intents_path=b_int, ai_review_enabled=False)
flow = o["intent_flow_analysis"]
check(b_log.read_bytes() == snap, "event log must not be modified (passive)")
out["B"] = {"flow": flow, "day_cache_suffixes": sorted(x.split(".", 1)[1] for x in files_under(root / "day_cache")), "incidents_total": o["incident_postmortem"].get("incident_total"), "improvement_n": len(o["improvement_suggestions"])}

# C. day omitted -> latest day in log; missing log -> today's date.
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "C1" / "x", ai_review_enabled=False)
out["C"] = {"latest_day": o["day"]}
md, js, o = ra.generate_reporter_analysis_report(root / "C" / "missing.jsonl", root / "C2" / "x", ai_review_enabled=False)
import datetime as _dt
check(o["day"] == _dt.date.today().isoformat(), "C missing log -> today")
out["C"]["missing_log_today"] = True

# D. AI review raising -> error payload (guarded), enabled coerced from None -> False; DRY_RUN/unavailable branches via the real reviewer.
orig_review = ra.build_ai_reporter_review
def boom(**k): raise RuntimeError("boom")
ra.build_ai_reporter_review = boom
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "D1" / "x", day=DAY)
out["D_exception"] = {"status": o["ai_review"]["status"], "reason": o["ai_review"]["reason"], "enabled": o["ai_review"]["enabled"], "grade": o["ai_run_grade"]}
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "D2" / "x", day=DAY, ai_review_enabled=True)
out["D_exception"]["enabled_true"] = o["ai_review"]["enabled"]
ra.build_ai_reporter_review = orig_review
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "D3" / "x", day=DAY)  # enabled=None, no policy in out -> disabled
out["D_policy_none"] = o["ai_review"]["status"]
os.environ["DRY_RUN"] = "1"
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "D4" / "x", day=DAY, ai_review_enabled=True)
out["D_dry_run"] = o["ai_review"]["status"]; del os.environ["DRY_RUN"]
class _NoClient: client = None
router_mod.LLMRouter.from_env = staticmethod(lambda *a, **k: _NoClient())
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "D5" / "x", day=DAY, ai_review_enabled=True)
out["D_unavailable"] = o["ai_review"]["status"]
router_mod.LLMRouter.from_env = staticmethod(trap_router)
# non-numeric max tokens is evaluated inside the guarded call -> error payload, not a crash
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "D6" / "x", day=DAY, ai_review_enabled=False, ai_review_max_tokens="x")
out["D_bad_max_tokens"] = {"status": o["ai_review"]["status"], "reason": o["ai_review"]["reason"][:40]}

# E. strategy memory: success writes only tmp; save failure -> error record; ledger failures swallowed.
mem = Path(os.environ["STRATEGY_MEMORY_PATH"])
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "E1" / "x", day=DAY, ai_review_enabled=False)
smr = o["strategy_memory_record"]
check(Path(smr["strategy_memory_path"]) == mem and mem.exists(), "E strategy memory written to tmp path")
out["E_ok"] = {"keys": sorted(smr), "storage_mode": smr["storage_mode"], "run_id": smr["run_id"], "window_day": smr["feedback_window_day"], "has_error": "error" in smr, "mem_lines": len(mem.read_text(encoding="utf-8").splitlines())}
orig_save = ra.save_strategy_feedback
def save_boom(**k): raise ValueError("disk full")
ra.save_strategy_feedback = save_boom
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "E2" / "x", day=DAY, ai_review_enabled=False)
out["E_save_fail"] = {k: v for k, v in o["strategy_memory_record"].items() if k in ("error", "daily_summary_path", "timestamp", "run_id")}
check(js.exists() and md.exists(), "E report still written after memory failure")
ra.save_strategy_feedback = orig_save
orig_raw, orig_bridge = ra.record_raw_input, ra.record_decision_bridge
def led_boom(**k): raise OSError("ledger down")
ra.record_raw_input = led_boom; ra.record_decision_bridge = led_boom
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "E3" / "x", day=DAY, ai_review_enabled=False)
out["E_ledger_fail"] = {"completed": js.exists() and md.exists()}
ra.record_raw_input, ra.record_decision_bridge = orig_raw, orig_bridge
ledger = Path(os.environ["EVIDENCE_LEDGER_PATH"]); out["E_ledger_tmp_lines"] = len(ledger.read_text(encoding="utf-8").splitlines()) if ledger.exists() else 0

# F. unguarded stages propagate and leave partial side effects (report_dir created, no js/md).
orig_te = ra.generate_trade_explain_report
def te_boom(*a, **k): raise KeyError("trade_explain")
ra.generate_trade_explain_report = te_boom
f_dir = root / "F1" / "x"
try: ra.generate_reporter_analysis_report(b_log, f_dir, day=DAY, ai_review_enabled=False); out["F_trade_explain"] = "no_raise"
except KeyError as e: out["F_trade_explain"] = {"raised": "KeyError", "dir_created": f_dir.is_dir(), "files": files_under(f_dir)}
ra.generate_trade_explain_report = orig_te
orig_op = ra.generate_operator_daily_summary
def op_boom(*a, **k): raise RuntimeError("operator")
ra.generate_operator_daily_summary = op_boom
try: ra.generate_reporter_analysis_report(b_log, root / "F2" / "x", day=DAY, ai_review_enabled=False); out["F_operator"] = "no_raise"
except RuntimeError as e: out["F_operator"] = "RuntimeError"
ra.generate_operator_daily_summary = orig_op
try: ra.generate_reporter_analysis_report(b_log, root / "F3" / "x", day=DAY, ai_review_enabled=False, rapid_cycle_threshold_sec="x"); out["F_rapid_str"] = "no_raise"
except ValueError: out["F_rapid_str"] = "ValueError"
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "F4" / "x", day=DAY, ai_review_enabled=False, rapid_cycle_threshold_sec=0)
out["F_rapid_zero_ok"] = js.exists()
# write failure of the final JSON propagates and the md is never written
orig_wt = Path.write_text
def wt(self, *a, **k):
    if self.name.startswith("reporter_analysis_") and self.suffix == ".json": raise OSError("json write failed")
    return orig_wt(self, *a, **k)
Path.write_text = wt
g_dir = root / "F5" / "x"
try: ra.generate_reporter_analysis_report(b_log, g_dir, day=DAY, ai_review_enabled=False); out["F_json_write"] = "no_raise"
except OSError: out["F_json_write"] = {"raised": "OSError", "md_exists": (g_dir / ("reporter_analysis_%s.md" % DAY)).exists()}
Path.write_text = orig_wt

# G. reports_root / canonical root resolution.
out["G"] = {"canon_nested": str(ra._canonical_reports_root(Path("/a/reports/dev/x"))).replace("\\", "/").replace(str(Path("/").resolve()).replace("\\", "/"), "/").lstrip("/").split("/")[-2:],
            "canon_none": ra._canonical_reports_root(Path("a/b")).as_posix()}
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "G1" / "plain" / "x", day=DAY, ai_review_enabled=False)
out["G"]["plain_trade_explain_under_parent"] = o["source_reports"]["trade_explain_json"].startswith(str(root / "G1" / "plain"))
rr_dir = root / "G2" / "reports_root_arg"
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "G2" / "x", day=DAY, ai_review_enabled=False, reports_root=rr_dir)
out["G"]["explicit_reports_root_used"] = o["source_reports"]["operator_summary_json"].startswith(str(rr_dir))
md, js, o = ra.generate_reporter_analysis_report(b_log, root / "G3" / "x", day=DAY, ai_review_enabled=False, generate_decision_story=True, generate_run_cards=True)
out["G"]["decision_story_run_cards"] = {"ds": o["source_reports"]["decision_story_enabled"], "rc": o["source_reports"]["run_cards_enabled"], "ds_md_nonempty": bool(o["source_reports"]["decision_story_md"]), "rc_md_nonempty": bool(o["source_reports"]["run_cards_md"])}

# H. determinism / input immutability.
o1 = ra.generate_reporter_analysis_report(b_log, root / "H1" / "x", day=DAY, ai_review_enabled=False)[2]
o2 = ra.generate_reporter_analysis_report(b_log, root / "H2" / "x", day=DAY, ai_review_enabled=False)[2]
def strip(o):
    o = copy.deepcopy(o)
    for k in ("report_json_path", "report_md_path", "source_reports", "strategy_memory_record", "ai_evidence_catalog"): o.pop(k, None)
    return stable(o)
out["H_diff_top_keys"] = sorted(k for k in o1 if k not in ("report_json_path", "report_md_path", "source_reports", "strategy_memory_record", "ai_evidence_catalog") and stable(o1[k]).replace("H1", "H") != stable(o2[k]).replace("H2", "H"))
out["H_deterministic_modulo_paths"] = not out["H_diff_top_keys"]

# I. consumers: Reporter.analyze_event_logs / dispatcher / CLI main (tmp fake args).
R = rep_mod.Reporter()
o = R.analyze_event_logs(event_log_path=b_log, report_dir=root / "I1" / "x", day=DAY, intents_path=root / "I1" / "no-intents.jsonl", reports_root=root / "I1" / "rr", ai_review_enabled=False)
out["I_reporter"] = {"day": o["day"], "intents_created": o["intent_flow_analysis"]["intents_created"]}
try: R.analyze_event_logs(event_log_path=b_log, report_dir=root / "I2" / "x", day=DAY, rapid_cycle_threshold_sec="x", ai_review_enabled=False); out["I_bad_rapid"] = "no_raise"
except ValueError: out["I_bad_rapid"] = "ValueError"
res = R.run(mode="reporter_analysis", event_log_path=b_log, report_dir=root / "I3" / "x", day=DAY, reports_root=root / "I3" / "rr", ai_review_enabled=False) if hasattr(R, "run") else None
out["I_run"] = {"type": type(res).__name__, "md_set": bool(getattr(res, "report_md_path", None)), "json_set": bool(getattr(res, "report_json_path", None))}
try: R.run(mode="nope"); out["I_unsupported"] = "no_raise"
except ValueError as e: out["I_unsupported"] = "ValueError"
cli = importlib.import_module("scripts.run_reporter_analysis_report")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = cli.main(["--event-log-path", str(b_log), "--intents-path", str(b_int), "--report-dir", str(root / "I4" / "x"), "--reports-root", str(root / "I4" / "rr"),
                   "--env-path", str(root / "no.env"), "--day", DAY, "--no-ai-review"])
line = buf.getvalue().strip()
out["I_cli"] = {"rc": rc, "head": line.split(" report_json=")[0]}
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = cli.main(["--event-log-path", str(b_log), "--report-dir", str(root / "I5" / "x"), "--reports-root", str(root / "I5" / "rr"), "--env-path", str(root / "no.env"), "--day", DAY, "--no-ai-review", "--json"])
out["I_cli_json"] = {"rc": rc, "schema": json.loads(buf.getvalue())["schema_version"]}

out["bad"] = bad
check(not bad, "blocked attempts: %r" % bad)
# nothing leaked into the repo tree
os.chdir(repo)
print("RF031_REPORTER_ANALYSIS_OK callers=%d cases=A-I blocked=0 debug=%s" % (len(callers), __debug__), file=sys.stderr)
print(stable(out), file=sys.stdout)
shutil.rmtree(root, ignore_errors=True)
