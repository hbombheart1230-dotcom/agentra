# RF-032: evaluation/q13_q14_validation.py (build/render/write) -- tmp reports root only. Reads evaluation/daily/<d>/{attribution_score_v0,scanner_alignment_root_cause_report,horizon_compliance_report}.json;
# writes <root>/evaluation/validation/<id>/q13_q14_validation_report.{json,md}. Writes outside tmp, network, subprocess, sqlite blocked. Default reports_root never used.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.q13_q14_validation")
tmp = Path(tempfile.mkdtemp(prefix="rf032_q1314_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open; _wt = Path.write_text; _mk = Path.mkdir
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked write")
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked mkdir")
    return _mk(self, *a, **k)
Path.write_text = wt; Path.mkdir = mk
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
def put(p, obj, raw=False):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(obj if raw else json.dumps(obj), encoding="utf-8")
root = tmp / "reports"
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}
def sc(v, st="OK"): return {"score": v, "status": st}
def q13(): return {"scores": {"selection_integrity_score": sc(80.4), "scanner_alignment_score": sc("70"), "entry_timing_score": sc("bad"), "exit_horizon_score": sc(50, "INSUFFICIENT_EVIDENCE"), "evidence_quality_score": sc(None)}}
def q14(total, srf=0, cf=0, so=0, me=0, largest="Scanner Ranking Failure"):
    cs = [{"root_cause": c, "trade_count": n} for c, n in (("Scanner Ranking Failure", srf), ("Candidate Filtering", cf), ("Strategist Override", so), ("Missing Evidence", me))]
    return {"trade_count": total, "cause_summary": cs, "largest_behavior_root_cause": {"root_cause": largest}}
def hz(n_bad, n_ok=1):
    rows = [{"horizon_violation_candidate": True}] * n_bad + [{}] * n_ok
    return {"rows": rows}
def day(d, a, b, c):
    base = root / "evaluation/daily" / d
    if a is not None: put(base / "attribution_score_v0.json", a)
    if b is not None: put(base / "scanner_alignment_root_cause_report.json", b)
    if c is not None: put(base / "horizon_compliance_report.json", c)
D5 = ["2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-09"]
for d in D5: day(d, q13(), q14(10, srf=5, cf=2, me=1), hz(1))   # GO scenario: SRF largest 5/5, missing 10%
out = {}
s0 = snap()
g = mod.build_q13_q14_validation_report(reports_root=root, days=D5)
check(snap() == s0, "build mutated tree")
check(g["decision"] == "GO" and g["decision_reasons"] == ["scanner_ranking_failure_stable", "missing_evidence_within_threshold", "reports_complete"] and g["behavior_patch_authorized"] is False and g["decision_scope"] == "diagnostic_stability_only", (g["decision"], g["decision_reasons"]))
check(g["day_count"] == 5 and g["completed_report_day_count"] == 5 and g["total_trade_count"] == 50 and g["missing_evidence_ratio"] == 0.1, (g["day_count"], g["total_trade_count"], g["missing_evidence_ratio"]))
check(g["root_cause_totals"] == {"Scanner Ranking Failure": 25, "Candidate Filtering": 10, "Strategist Override": 0, "Exit Horizon": 5, "Missing Evidence": 5}, g["root_cause_totals"])
r0 = g["daily_rows"][0]
check(r0["q13_scores"] == {"selection_integrity_score": 80, "scanner_alignment_score": 70, "entry_timing_score": None, "exit_horizon_score": None, "evidence_quality_score": None}, r0["q13_scores"])  # bad/INSUFFICIENT/None -> None
check(r0["missing_evidence_ratio"] == 0.1 and r0["report_complete"] is True and r0["largest_behavior_root_cause"] == "Scanner Ranking Failure", r0)
out["go"] = [g["decision"], g["total_trade_count"], g["missing_evidence_ratio"], g["largest_behavior_root_cause_day_counts"]]
def scen(name, spec):
    """spec: day -> (q13, q14, hz) ; builds under a fresh sub root and returns payload"""
    global root
    keep = root; root = tmp / ("r_" + name)
    for d, (a, b, c) in spec.items(): day(d, a, b, c)
    try: return mod.build_q13_q14_validation_report(reports_root=root, days=list(spec))
    finally: root = keep
# IN_PROGRESS: only 4 days
p = scen("ip", {d: (q13(), q14(10, srf=5), hz(0)) for d in D5[:4]}); check(p["decision"] == "IN_PROGRESS" and p["decision_reasons"] == ["needs_5_trading_days"], p["decision_reasons"])
# NO_GO: SRF largest only 3/5 days
sp = {d: (q13(), q14(10, srf=5, largest="Scanner Ranking Failure" if i < 3 else "Candidate Filtering"), hz(0)) for i, d in enumerate(D5)}
p = scen("srf3", sp); check(p["decision"] == "NO_GO" and p["decision_reasons"] == ["scanner_ranking_failure_not_stable_4_of_5"], p["decision_reasons"])
# boundary: 4/5 -> GO
sp = {d: (q13(), q14(10, srf=5, largest="Scanner Ranking Failure" if i < 4 else "Candidate Filtering"), hz(0)) for i, d in enumerate(D5)}
p = scen("srf4", sp); check(p["decision"] == "GO", p["decision_reasons"])
# missing evidence total ratio boundary: exactly 0.20 OK, daily > 0.40 fails
sp = {d: (q13(), q14(10, srf=5, me=2), hz(0)) for d in D5}; p = scen("me20", sp); check(p["missing_evidence_ratio"] == 0.2 and p["decision"] == "GO", (p["missing_evidence_ratio"], p["decision"]))
sp = {d: (q13(), q14(10, srf=5, me=2), hz(0)) for d in D5}; sp[D5[0]] = (q13(), q14(10, srf=5, me=5), hz(0))
p = scen("meday", sp); check(p["decision"] == "NO_GO" and p["decision_reasons"] == ["missing_evidence_above_threshold"], (p["decision"], p["decision_reasons"]))  # total 13/50=.26 and one day .5
sp = {d: (q13(), q14(10, srf=5, me=4), hz(0)) for d in D5}; p = scen("me40", sp); check(p["missing_evidence_ratio"] == 0.4 and "missing_evidence_above_threshold" in p["decision_reasons"], p["decision_reasons"])  # total .4 > .2
# incomplete reports
sp = {d: (q13(), q14(10, srf=5), hz(0)) for d in D5}; sp[D5[2]] = (q13(), None, hz(0))
p = scen("inc", sp); check(p["decision"] == "NO_GO" and p["completed_report_day_count"] == 4 and p["decision_reasons"][0] == "q13_q14_reports_incomplete", (p["decision"], p["decision_reasons"]))
check(p["daily_rows"][2]["q14_available"] is False and p["daily_rows"][2]["trade_count"] == 0 and p["daily_rows"][2]["missing_evidence_ratio"] == 0.0, p["daily_rows"][2])
# Exit Horizon "override": condition is exit > max(counts incl. Exit Horizon itself) -> can never be true (observed dead branch); q14 largest is kept
sp = {d: (q13(), q14(10, srf=3, cf=2, so=1), hz(4)) for d in D5}; p = scen("exit", sp)
check(all(r["largest_behavior_root_cause"] == "Scanner Ranking Failure" and r["root_cause_counts"]["Exit Horizon"] == 4 for r in p["daily_rows"]) and p["decision"] == "GO", (p["decision"], p["decision_reasons"]))
sp = {d: (q13(), q14(10, srf=1, largest="Scanner Ranking Failure"), hz(9)) for d in D5}; p = scen("exit_dom", sp)
check(all(r["largest_behavior_root_cause"] == "Scanner Ranking Failure" for r in p["daily_rows"]) and p["root_cause_totals"]["Exit Horizon"] == 45, "even dominant Exit Horizon never overrides")
out["exit_horizon_override_reachable"] = False
sp = {d: (q13(), q14(10, srf=3), hz(3)) for d in D5}; p = scen("exit_tie", sp); check(all(r["largest_behavior_root_cause"] == "Scanner Ranking Failure" for r in p["daily_rows"]), "tie keeps q14 largest")
# horizon flags
hzf = {"rows": [{"exited_before_min_hold": 1}, {"exited_before_target_hold": 1}, {"target_hold_would_improve_exit": 1}, {"horizon_violation_candidate": 0}, "junk", None]}
p = scen("hzflags", {d: (q13(), q14(10), hzf) for d in D5}); check(p["root_cause_totals"]["Exit Horizon"] == 15, p["root_cause_totals"])
# weird values: non-int counts raise (documented as observation)
def weird(q14o, hzo=None):
    return attempt(scen, "weird_" + str(abs(hash(json.dumps(q14o, sort_keys=True))) % 10**6), {D5[0]: (q13(), q14o, hzo if hzo is not None else hz(0))})
out["weird"] = {
    "trade_count_str_digits": (lambda r: (r[1], r[0] and r[0]["daily_rows"][0]["trade_count"]))(weird({"trade_count": "5", "cause_summary": []})),
    "cause_count_nonint": weird({"trade_count": 5, "cause_summary": [{"root_cause": "Missing Evidence", "trade_count": "x"}]})[1],
    "cause_count_none": (lambda r: (r[1], r[0] and r[0]["daily_rows"][0]["root_cause_counts"]["Scanner Ranking Failure"]))(weird({"trade_count": 5, "cause_summary": [{"root_cause": "Scanner Ranking Failure", "trade_count": None}, "junk"]})),
    "largest_behavior_str": (lambda r: (r[1], r[0] and r[0]["daily_rows"][0]["largest_behavior_root_cause"]))(weird({"trade_count": 5, "largest_behavior_root_cause": "str"})),
    "rows_none": (lambda r: r[1])(weird({"trade_count": 5}, {"rows": None})),
    "trade_count_nonnum": weird({"trade_count": "abc"})[1],
}
check(out["weird"]["trade_count_str_digits"] == (None, 5) and out["weird"]["cause_count_nonint"] == "ValueError" and out["weird"]["cause_count_none"] == (None, 0) and out["weird"]["rows_none"] is None and out["weird"]["trade_count_nonnum"] == "ValueError", out["weird"])
# ---- selection by start/end (only existing daily dirs count) and exceptions
(root / "evaluation/daily/2026-10-10").mkdir(parents=True)  # empty daily dir counts as a day, incomplete
pr = mod.build_q13_q14_validation_report(reports_root=root, start="2026-10-04", end="2026-10-11")
check(pr["days"] == D5 + ["2026-10-10"] and pr["day_count"] == 6 and pr["completed_report_day_count"] == 5 and pr["decision"] == "NO_GO" and pr["decision_reasons"] == ["q13_q14_reports_incomplete"], (pr["days"], pr["decision_reasons"]))
pe = mod.build_q13_q14_validation_report(reports_root=tmp / "nope", start="2026-10-04", end="2026-10-11"); check(pe["day_count"] == 0 and pe["decision"] == "IN_PROGRESS", pe["decision"])
pz = mod.build_q13_q14_validation_report(reports_root=tmp / "nope", days=[]); check(pz["day_count"] == 0 and pz["missing_evidence_ratio"] == 0.0, "empty days")
pd_ = mod.build_q13_q14_validation_report(reports_root=root, days=("2026-10-05", "2026-10-99-bad")); check(pd_["day_count"] == 2 and pd_["completed_report_day_count"] == 1 and pd_["days"][1] == "2026-10-99-bad", "explicit days are not validated")
pe2 = mod.build_q13_q14_validation_report(reports_root=root, days=[1, None]); out["days_nonstr"] = pe2["days"]
out["exc"] = {
    "no_days_no_range": attempt(mod.build_q13_q14_validation_report, reports_root=root)[1],
    "only_start": attempt(mod.build_q13_q14_validation_report, reports_root=root, start="2026-10-05")[1],
    "start_after_end": attempt(mod.build_q13_q14_validation_report, reports_root=root, start="2026-10-09", end="2026-10-05")[1],
    "bad_date": attempt(mod.build_q13_q14_validation_report, reports_root=root, start="x", end="2026-10-05")[1],
    "none_root": attempt(mod.build_q13_q14_validation_report, reports_root=None, days=D5)[1],
    "render_none": attempt(mod.render_q13_q14_validation_report, None)[1],
    "render_empty": attempt(mod.render_q13_q14_validation_report, {})[1],
    "days_str_iter": attempt(lambda: mod.build_q13_q14_validation_report(reports_root=root, days="2026-10-05")["day_count"])[0],
}
check(out["exc"]["no_days_no_range"] == "ValueError" and out["exc"]["only_start"] == "ValueError" and out["exc"]["start_after_end"] == "ValueError" and out["exc"]["bad_date"] == "ValueError" and out["exc"]["none_root"] == "TypeError" and out["exc"]["render_none"] == "AttributeError" and out["exc"]["render_empty"] is None, out["exc"])
# ---- render
md = mod.render_q13_q14_validation_report(g); check(md == mod.render_q13_q14_validation_report(copy.deepcopy(g)), "render nondeterministic")
check(md.startswith("# Q13/Q14 Validation Run") and "- Decision: `GO`" in md and "- Behavior patch authorized: `False`" in md and "- Days: 5 / 5" in md and "- Missing Evidence ratio: 10.0%" in md and "| Scanner Ranking Failure | 5 | 5 | 5 | 5 | 5 | 25 |" in md and md.endswith("\n"), md[:300])
mde = mod.render_q13_q14_validation_report({}); check("Decision reasons: -" in mde and "decision_scope" not in mde and "Decision scope: `legacy`" in mde and "| Exit Horizon | 0 |" in mde, mde[:300])
mdj = mod.render_q13_q14_validation_report({**g, "daily_rows": ["x", None] + g["daily_rows"][:1], "days": D5[:1]}); check("| 2026-10-05 |" in mdj, "non-mapping rows skipped")
# ---- write
r, e = attempt(mod.write_q13_q14_validation_report, reports_root=root, validation_id="v_test", days=D5); check(e is None, e)
jp, mp = Path(r["json"]), Path(r["markdown"])
check(jp == root / "evaluation/validation/v_test/q13_q14_validation_report.json" and mp.name == "q13_q14_validation_report.md", r)
check(json.loads(jp.read_text(encoding="utf-8")) == g and mp.read_text(encoding="utf-8") == md, "written != built")
b1 = (jp.read_bytes(), mp.read_bytes()); r2, e2 = attempt(mod.write_q13_q14_validation_report, reports_root=root, validation_id="v_test", days=D5); check(e2 is None and (jp.read_bytes(), mp.read_bytes()) == b1, "not idempotent")
new = {k for k in snap() if k.startswith("reports/evaluation/validation")}; check(new == {"reports/evaluation/validation", "reports/evaluation/validation/v_test", "reports/evaluation/validation/v_test/q13_q14_validation_report.json", "reports/evaluation/validation/v_test/q13_q14_validation_report.md"}, new)
out["files"] = len(new) - 2
ex = attempt(mod.write_q13_q14_validation_report, reports_root=Path("/proc/nonexistent_rf032"), validation_id="v", days=D5)[1]; out["outside_write"] = ex; check(ex == "OSError", ex)
(root / "evaluation/validation").mkdir(exist_ok=True); (root / "evaluation/validation/v_file").write_text("x")
ex2 = attempt(mod.write_q13_q14_validation_report, reports_root=root, validation_id="v_file", days=D5)[1]; out["dir_collision"] = ex2; check(ex2 in ("FileExistsError", "NotADirectoryError"), ex2)
ex3 = attempt(mod.write_q13_q14_validation_report, reports_root=root, validation_id="v_noargs")[1]; check(ex3 == "ValueError" and not (root / "evaluation/validation/v_noargs").exists(), ex3)  # build fails before mkdir
trav = attempt(mod.write_q13_q14_validation_report, reports_root=root, validation_id="../escape", days=D5)  # not sanitized
out["traversal_validation_id"] = ["written" if trav[0] else trav[1], (root / "evaluation/escape/q13_q14_validation_report.json").exists()]
net = [b for b in bad if not b.startswith(("write:", "mkdir:"))]; check(not net, bad)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=str))
print("RF032_Q13_Q14_VALIDATION_OK decisions=GO/IN_PROGRESS/NO_GO boundaries=srf4of5,me0.20 exit_horizon_override=unreachable idempotent=yes files=%d outside_write=%s dir_collision=%s traversal=%s net_attempts=%d debug=%s" % (out["files"], out["outside_write"], out["dir_collision"], out["traversal_validation_id"][0], len(net), __debug__))
