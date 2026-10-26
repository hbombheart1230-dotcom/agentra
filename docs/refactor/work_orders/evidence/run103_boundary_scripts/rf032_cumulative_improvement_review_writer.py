# RF-032: evaluation/cumulative_improvement_review.py -- _strategist_weighting_review (tmp baseline files), _candidate_rows, build (payloads/historical_review/q14_range injected so heavy collaborators are bypassed), render, writer (build swapped for fake; plus one run with real collaborators on an empty tmp reports root). Writes only under tmp.
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.cumulative_improvement_review")
tmp = Path(tempfile.mkdtemp(prefix="rf032_cir_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
sqlite3.connect = blocked("sqlite")
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
_open = builtins.open; _wt = Path.write_text; _mk = Path.mkdir
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
def wt(self, *a, **k):
    if not inside(self): bad.append("wt:" + str(self)); raise OSError("blocked write")
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
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}
# 1 _strategist_weighting_review
root = tmp / "reports"; src = root / "evaluation" / "baseline_samsung_hynix"
def perf(h, a_n, a_r, b_n, b_r):
    return {"horizon": h, "performers": [{"performer": "A_SCANNER_CONTROL", "trade_count": a_n, "avg_return_pct": a_r}, {"performer": "B_STRATEGIST_RANKED", "trade_count": b_n, "avg_return_pct": b_r}]}
S = mod._strategist_weighting_review
r0 = S(root, start="2026-10-01", end="2026-10-31")
check([x["horizon"] for x in r0["rows"]] == ["+5m", "+15m", "+30m", "EOD"] and all(x["observed_day_count"] == 0 and x["avg_strategist_minus_scanner_pct"] is None for x in r0["rows"]), "no source root")
put(src / "2026-10-01" / "q9_vs_samsung_hynix_daily_comparison.json", {"horizons": [perf("+30m", 3, 1.0, 3, 1.5), perf("+5m", 2, 0.0, 2, 0.0), perf("+30m_x", 1, 0, 1, 1), "junk", perf("EOD", 0, 1.0, 5, 2.0)]})
put(src / "2026-10-02" / "q9_vs_samsung_hynix_daily_comparison.json", {"horizons": [perf("+30m", 3, 1.0, 3, 0.5)]})
put(src / "2026-10-03" / "q9_vs_samsung_hynix_daily_comparison.json", {"horizons": [perf("+30m", 3, 1.0, 3, 1.0000001)]})
put(src / "2026-09-30" / "q9_vs_samsung_hynix_daily_comparison.json", {"horizons": [perf("+30m", 3, 0.0, 3, 9.0)]})
put(src / "2026-11-01" / "q9_vs_samsung_hynix_daily_comparison.json", {"horizons": [perf("+30m", 3, 0.0, 3, 9.0)]})
put(src / "2026-10-04" / "q9_vs_samsung_hynix_daily_comparison.json", "{bad", raw=True)
put(src / "2026-10-05" / "q9_vs_samsung_hynix_daily_comparison.json", [1, 2])
(src / "2026-10-06").mkdir()
put(src / "file_not_dir.txt", "x", raw=True)
rows = {x["horizon"]: x for x in S(root, start="2026-10-01", end="2026-10-31")["rows"]}
r30 = rows["+30m"]
check(r30["observed_day_count"] == 3 and r30["strategist_better_day_count"] == 2 and r30["strategist_worse_day_count"] == 1, "30m counts " + str(r30))
check(r30["avg_strategist_minus_scanner_pct"] == round((0.5 - 0.5 + 0.0000001) / 3, 4), "30m avg " + str(r30))
check(rows["+5m"]["observed_day_count"] == 1 and rows["+5m"]["avg_strategist_minus_scanner_pct"] == 0.0, "zero delta counted observed but neither better nor worse")
check(rows["EOD"]["observed_day_count"] == 0, "trade_count 0 skipped")
check(S(root, start="2026-10-02", end="2026-10-02")["rows"][2]["observed_day_count"] == 1, "range inclusive, string compare")
check(S(root, start="2026-10-31", end="2026-10-01")["rows"][2]["observed_day_count"] == 0, "inverted range empty")
put(src / "2026-10-07" / "q9_vs_samsung_hynix_daily_comparison.json", {"horizons": [perf("+30m", "x", 1, 1, 1)]})
_, e = attempt(S, root, start="2026-10-01", end="2026-10-31"); check(e == "ValueError", "non-numeric trade_count propagates " + str(e))
(src / "2026-10-07" / "q9_vs_samsung_hynix_daily_comparison.json").unlink()
# 2 _candidate_rows
C = mod._candidate_rows
def rr(b, h, live): return {"rank_bucket": b, "horizon": h, "live_net": {"expectancy_pct": live}}
def cand(ep=None, re=None, pr=None, sr=None): return C(episode_review=ep or {}, reentry_review=re or {}, post_reclaim_review=pr or {}, strategist_review=sr or {})
c = cand()
check([x["priority"] for x in c] == [1, 2, 3, 4] and c[0]["status"] == "INSUFFICIENT_EVIDENCE" and c[1]["status"] is None, "empty candidates")
check(c[2]["status"] == "OBSERVABILITY_NOT_READY" and c[3]["status"] == "RETAIN_UNDER_OBSERVATION" and c[3]["evidence"] == {}, "empty ranking/strategist")
check(cand(re={"behavior_candidate_eligible": True})[0]["status"] == "APPLIED_2026_07_29", "applied label hardcoded date")
ready = {"score_component_review": {"status": "READY"}}
check(cand(ep={**ready, "rank_horizon_rows": [rr("rank1", "+30m", -0.1), rr("rank2_3", "+30m", 0)]})[2]["status"] == "DIAGNOSTIC_CANDIDATE", "both <=0 incl 0")
check(cand(ep={**ready, "rank_horizon_rows": [rr("rank1", "+30m", 0.1), rr("rank2_3", "+30m", -1)]})[2]["status"] == "RETAIN_UNDER_OBSERVATION", "rank1 positive")
check(cand(ep={**ready, "rank_horizon_rows": [rr("rank1", "+5m", -1), rr("rank2_3", "+15m", -1)]})[2]["status"] == "DIAGNOSTIC_CANDIDATE", "missing +30m rows -> 0.0 -> diagnostic (observation)")
check(cand(ep={"score_component_review": {"status": "PARTIAL"}, "rank_horizon_rows": [rr("rank1", "+30m", -1), rr("rank2_3", "+30m", -1)]})[2]["status"] == "OBSERVABILITY_NOT_READY", "not READY")
check(cand(sr={"rows": [{"horizon": "+30m", "avg_strategist_minus_scanner_pct": -0.0001}]})[3]["status"] == "DIAGNOSTIC_CANDIDATE", "strategist negative")
check(cand(sr={"rows": [{"horizon": "+30m", "avg_strategist_minus_scanner_pct": None}, {"horizon": "+30m", "avg_strategist_minus_scanner_pct": -1}]})[3]["status"] == "RETAIN_UNDER_OBSERVATION", "None -> 0.0; first +30m only")
_, e = attempt(cand, ep={"rank_horizon_rows": [rr("rank1", "+30m", "x")]}); check(e == "ValueError", "non-numeric live_net raises " + str(e))
check(cand(ep={"rank_horizon_rows": [rr("rank1", "+30m", None)], "score_component_review": None})[2]["status"] == "OBSERVABILITY_NOT_READY", "None score_component_review tolerated")
# 3 build with injected inputs
Bd = mod.build_cumulative_improvement_review
q14 = {"rows": [], "largest_behavior_root_cause": {"root_cause": "X"}, "largest_structural_root_cause": None,
       "cause_summary": [{"diagnostic_kind": "outcome_conditioned", "trade_count": 3}, {"diagnostic_kind": "outcome_conditioned", "trade_count": None}, {"diagnostic_kind": "structural", "trade_count": 9}, "junk"]}
p = Bd(reports_root=str(root), start="2026-10-01", end="2026-10-31", payloads=[], historical_review={}, q14_range=q14)
check(p["schema_version"] == "cumulative_improvement_review.v1" and p["behavior_effect"] == "evaluation_only" and p["range"] == {"start": "2026-10-01", "end": "2026-10-31"}, "build header")
check(p["q14_causal_interpretation"]["outcome_conditioned_trade_count"] == 3 and p["q14_causal_interpretation"]["largest_structural_root_cause"] is None, "q14 interp")
check(p["behavior_patch_authorized"] is False and len(p["improvement_candidates"]) == 4 and p["strategist_weighting_review"]["rows"][2]["observed_day_count"] == 3, "build content (real weighting from tmp)")
check(set(p["cost_bases"]) >= {"mock_observed", "live_deployment_equity"}, "cost bases " + str(sorted(p["cost_bases"])))
json.dumps(p)
s1 = snap(); p2 = Bd(reports_root=root, start="2026-10-01", end="2026-10-31", payloads=[], historical_review={}, q14_range=q14); check(p2 == p and snap() == s1, "pure/idempotent, no writes")
_, e = attempt(Bd, reports_root=root, start="a", end="b", payloads=[], historical_review={}, q14_range={"rows": None}); check(e is None, "rows None tolerated " + str(e))
_, e = attempt(Bd, reports_root=root, start="a", end="b", payloads=[], historical_review={}, q14_range={"rows": [1]}); err_row = e
_, e = attempt(Bd, reports_root=root, start="a", end="b", payloads=[], historical_review={}, q14_range={"rows": [], "cause_summary": "ab"}); check(e is None, "string cause_summary skipped as non-mapping chars")
_, e = attempt(Bd, reports_root=root, start="a", end="b", payloads=None, historical_review={}, q14_range={})
real_empty_payloads = e or "ok"
# 4 render
R = mod.render_cumulative_improvement_review
t = R(p); check(t.endswith("\n") and "# Cumulative Improvement Review - 2026-10-01 to 2026-10-31" in t and "Legacy outcome-conditioned result: `X`" in t and "| 1 | same_symbol_loss_reentry_control |" in t and "Largest structural result: `NONE`" in t, "render")
t0 = R({}); check("None to None" in t0 and "Rule: N/A" in t0 and "`NONE`" in t0, "render {}")
tt = R({"episode_scanner_review": {"rank_horizon_rows": [{"rank_bucket": "unknown"}, "x", {"rank_bucket": "rank1", "horizon": "+30m", "episode_count": 2, "observed_count": 2, "observed_day_count": 1, "gross": {"expectancy_pct": 0.12345}, "live_net": None}]}})
check("| rank1 | +30m | 2 | 2 | 1 | 0.1235% | 0.0000% | 0.0000% |" in tt and "unknown" not in tt.split("Episode-Level")[1].split("Same-Symbol")[0], "render rank rows: unknown skipped, None->0")
_, e = attempt(R, {"episode_scanner_review": {"rank_horizon_rows": [{"rank_bucket": "rank1", "gross": {"expectancy_pct": "x"}}]}}); check(e == "ValueError", "render bad number " + str(e))
_, e = attempt(R, {"post_reclaim_shadow_review": {"rows": ["junk"]}}); check(e == "AttributeError", "render non-mapping reclaim row " + str(e))
# 5 writer
calls = []
real = mod.build_cumulative_improvement_review
def fake(**k): calls.append(k); return real(**k, payloads=[], historical_review={}, q14_range=q14)
mod.build_cumulative_improvement_review = fake
res = mod.write_cumulative_improvement_review(reports_root=str(root), start="2026-10-01", end="2026-10-31")
od = root / "evaluation" / "range" / "2026-10-01_2026-10-31"
check(calls == [{"reports_root": str(root), "start": "2026-10-01", "end": "2026-10-31"}] and set(res) == {"json", "markdown"}, "writer call/result")
check(Path(res["json"]) == od / "cumulative_improvement_review.json" and json.loads(Path(res["json"]).read_text(encoding="utf-8"))["range"]["end"] == "2026-10-31", "json written")
check(Path(res["markdown"]).read_text(encoding="utf-8").startswith("# Cumulative Improvement Review"), "md written")
s2 = snap(); mod.write_cumulative_improvement_review(reports_root=root, start="2026-10-01", end="2026-10-31"); check(snap() == s2, "idempotent")
# traversal-ish start/end create nested dir under root (no validation)
mod.write_cumulative_improvement_review(reports_root=root, start="a/b", end="c"); check((root / "evaluation" / "range" / "a" / "b_c" / "cumulative_improvement_review.json").is_file(), "start with slash nests dir (no validation)")
# partial
od2 = root / "evaluation" / "range" / "p_q"; (od2 / "cumulative_improvement_review.md").mkdir(parents=True)
_, e = attempt(mod.write_cumulative_improvement_review, reports_root=root, start="p", end="q"); check(e in ("PermissionError", "IsADirectoryError") and (od2 / "cumulative_improvement_review.json").is_file(), "md fail leaves json " + str(e))
od3 = root / "evaluation" / "range" / "r_s"; (od3 / "cumulative_improvement_review.json").mkdir(parents=True)
_, e = attempt(mod.write_cumulative_improvement_review, reports_root=root, start="r", end="s"); check(e in ("PermissionError", "IsADirectoryError") and not (od3 / "cumulative_improvement_review.md").exists(), "json fail no md")
mod.build_cumulative_improvement_review = lambda **k: (_ for _ in ()).throw(RuntimeError("b"))
_, e = attempt(mod.write_cumulative_improvement_review, reports_root=root, start="t", end="u"); check(e == "RuntimeError" and not (root / "evaluation" / "range" / "t_u").exists(), "build fail no dir")
mod.build_cumulative_improvement_review = real
# outside write blocked
_, e = attempt(mod.write_cumulative_improvement_review, reports_root=Path(repo) / "zz_outside", start="a", end="b")
check(e is not None and not (Path(repo) / "zz_outside").exists(), "outside blocked " + str(e))
# 6 real collaborators on empty tmp root
er = tmp / "empty_reports"; er.mkdir()
rr_, e = attempt(mod.write_cumulative_improvement_review, reports_root=er, start="2026-10-01", end="2026-10-05")
real_write = e or "ok"
if rr_: check(json.loads(Path(rr_["json"]).read_text(encoding="utf-8"))["behavior_patch_authorized"] is False, "real json")
check(not [b for b in bad if not b.startswith(("write:", "wt:", "mkdir:"))], "network/subprocess " + str(bad))
check(all("zz_outside" in b for b in bad), "unexpected outside writes " + str(bad))
print("RF032_CUMULATIVE_IMPROVEMENT_REVIEW_OK weighting=pair_days(str_range,skip_corrupt/empty/zero_trades) candidates=4_status_map applied_label=hardcoded_2026_07_29 build=pure_idempotent render=tolerant writer=json_then_md partial=json_left_on_md_fail build_fail=no_dir nested_start=no_validation real_empty_payloads=" + real_empty_payloads + " real_empty_write=" + real_write + " row_junk=" + str(err_row) + " outside_write=OSError net_attempts=0")
