# RF-032 libs/reporting/evaluation/operator_summary_mining.py: build -> render -> write_operator_summary_mining (tmp-only, no network).
# stdlib-only module loaded by file path (no package __init__ / tzdata). Run from repository root.
import os, sys, json, copy, importlib.util, tempfile, socket, subprocess, sqlite3, builtins
from pathlib import Path
repo = os.getcwd(); sys.dont_write_bytecode = True
_sp = importlib.util.spec_from_file_location("rf032_osm", os.path.join(repo, "libs", "reporting", "evaluation", "operator_summary_mining.py"))
osm = importlib.util.module_from_spec(_sp); sys.modules["rf032_osm"] = osm; _sp.loader.exec_module(osm)
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def exc_of(f, *a, **k):
    try: f(*a, **k); return "no_raise"
    except Exception as e: return type(e).__name__
tmp = Path(tempfile.mkdtemp(prefix="rf032_osm_")); tr = str(tmp.resolve())
rr = tmp / "reports"; op = rr / "operator_summary"
def put(p, v, raw=False):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(v if raw else json.dumps(v, ensure_ascii=False), encoding="utf-8")
# ---- fixture (created before guards): 3 days
for i, day in enumerate(["2026-04-01", "2026-04-02", "2026-04-03"]):
    d = op / "daily" / day
    put(d / "daily_summary.json", {"metrics": {"trade_count": 2, "closed_trade_count": 1, "win_rate": 0.5, "avg_return_pct": "1.25"},
                                    "quant_shadow_candidate_evaluation": {"deduped_candidate_count": 7, "forward_outcome_coverage": 0.8}})
    put(d / "q8_shadow_blocker_review.json", {"candidate_count": 4, "evaluation_trust_gate": {"trusted_forward_count": 3, "promotion_allowed": False}})
    put(d / "q9_decision_windows.json", {"window_count": 5, "windows": [1, 2, 3], "recovery": {"x": 1}})
    put(d / "closeout_maintenance.json", {"ok": True})
    if i < 2: put(d / "trade_index.json", [{"a": 1}, {"a": 2}] if i == 0 else [{"a": 1}])      # day2 mismatch (2 vs 1)
    if i == 0: put(d / "daily_report.json", {"r": 1})
    if i == 2: put(d / "operator_summary.json", "{broken", raw=True)                             # json error
put(op / "daily" / "stray_file.txt", "x", raw=True)                                               # file, not dir: ignored
put(op / "weekly" / "2026-W14" / "weekly_summary.json", {"metrics": {"trade_count": 3}, "pattern_performance": {"a": 1}, "quant_tactic_evaluation": {"b": 1}, "quant_shadow_candidate_evaluation": {"c": 1}})
put(op / "weekly" / "2026-W15" / "weekly_summary.json", {})
put(op / "symbols" / "000660" / "symbol_summary.json", {"metrics": {"trade_count": 6, "closed_trade_count": 5, "win_rate": 0.6, "avg_return_pct": 0.3}, "pattern_performance": {"p": 1}})
put(op / "symbols" / "005930" / "symbol_memory.json", {"symbol_memory": {"trade_stats": {"trade_count": 2, "completed_trade_count": 1, "win_rate": 0.0, "avg_return_pct": -1}}})
put(op / "symbols" / "035720" / "symbol_summary.json", "[1,2]", raw=True)                          # non-dict summary
def tree(r): return sorted((str(p.relative_to(r)), p.read_bytes()) for p in Path(r).rglob("*") if p.is_file())
before = tree(tmp)
# ---- guards (all effects outside tmp blocked)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc")
for n in ("Popen", "run", "call", "check_output"): setattr(subprocess, n, blocked(n))
sqlite3.connect = blocked("sqlite")
_wt = Path.write_text
def wt(self, *a, **k):
    if not str(self.resolve()).startswith(tr): bad.append("write:" + str(self)); raise OSError("blocked write outside tmp")
    return _wt(self, *a, **k)
Path.write_text = wt
_mk = Path.mkdir
def mk(self, *a, **k):
    if not str(self.resolve()).startswith(tr): bad.append("mkdir:" + str(self)); raise OSError("blocked mkdir outside tmp")
    return _mk(self, *a, **k)
Path.mkdir = mk
# ---- build (read-only)
p = osm.build_operator_summary_mining(rr)
check(tree(tmp) == before, "build is read-only")
check(p["schema_version"] == "operator_summary_mining.v1" and p["behavior_effect"] == "observation_only" and p["source"] == str(op), "header")
dp = p["daily_presence"]
check(dp["daily_count"] == 3 and dp["first_day"] == "2026-04-01" and dp["last_day"] == "2026-04-03", "daily count/first/last (stray file ignored)")
check(dp["presence_counts"] == {"daily_summary": 3, "operator_summary": 1, "q8_shadow_blocker_review": 3, "q9_decision_windows": 3, "closeout_maintenance": 3, "trade_index": 2, "daily_report": 1}, "presence counts (broken JSON counted as present: {__error__} dict is truthy) %r" % dp["presence_counts"])
check(dp["json_error_count"] == 1 and dp["json_errors"][0]["day"] == "2026-04-03" and dp["json_errors"][0]["error"].startswith("operator_summary.json:"), "json error captured not raised")
check(dp["presence_ratio"]["trade_index"] == round(2 / 3, 4), "ratio rounding")
dq = p["daily_quality"]
r0 = dq["recent_days"][0]
check(r0["trade_count"] == 2 and r0["avg_return_pct"] == 1.25 and r0["shadow_candidate_count"] == 7 and r0["q8_trusted_forward_count"] == 3 and r0["q9_window_count"] == 5 and r0["q9_has_recovery"] is True and r0["closeout_ok"] is True, "daily row fields")
check(dq["trade_index_mismatch_examples"] == [{"day": "2026-04-02", "daily_trade_count": 2, "trade_index_count": 1}], "mismatch only for days WITH trade_index")
check(dq["missing_runtime_surface_days"] == ["2026-04-02", "2026-04-03"], "missing runtime surface: %r" % dq["missing_runtime_surface_days"])
check(dq["q9_window_count_average_recent"] == 5.0 and dq["shadow_forward_coverage_average_recent"] == 0.8, "recent averages")
wq = p["weekly_quality"]
check(wq["weekly_count"] == 2 and wq["usable_week_count"] == 1 and wq["recent_weeks"][1]["has_summary"] is False, "weekly")
sq = p["symbol_quality"]
check(sq["symbol_count"] == 3 and [r["symbol"] for r in sq["top_symbols"]] == ["000660", "005930", "035720"] and sq["symbols_with_trade_count_ge_2"] == 2 and sq["symbols_with_trade_count_ge_5"] == 1, "symbols sorted/threshold")
m = {r["symbol"]: r for r in sq["top_symbols"]}
check(m["005930"]["trade_count"] == 2 and m["005930"]["closed_trade_count"] == 1 and m["005930"]["win_rate"] == 0.0 and m["035720"]["trade_count"] == 0, "memory fallback + non-dict summary tolerated")
q9 = p["q9_overlap"]
check(q9["q9_operator_summary_day_count"] == 3 and q9["q9_window_count_total"] == 15 and q9["q9_window_count_average"] == 5.0, "q9 overlap")
rd = p["readiness"]
check(len(rd["issues"]) == 3 and rd["strengths"] == [] and rd["status"] == "NEEDS_REPAIR", "readiness issues/strengths: %r" % rd)
# empty root
e = osm.build_operator_summary_mining(tmp / "nope")
check(e["daily_presence"]["daily_count"] == 0 and e["daily_presence"]["presence_ratio"]["daily_summary"] == 0.0 and e["weekly_quality"]["weekly_count"] == 0 and e["symbol_quality"]["symbol_count"] == 0 and e["readiness"]["status"] == "NEEDS_REPAIR", "empty root (q9 history short -> issue)")
check(not (tmp / "nope").exists(), "build never creates dirs")
# ---- render
md = osm.render_operator_summary_mining_markdown(p)
check(isinstance(md, str) and md.startswith("# ") and "operator_summary" in md and "000660" in md, "markdown header/content")
check(osm.render_operator_summary_mining_markdown(copy.deepcopy(p)) == md, "render deterministic")
rexc = {"render_empty": exc_of(osm.render_operator_summary_mining_markdown, {}), "render_empty_payload": exc_of(osm.render_operator_summary_mining_markdown, e)}
# ---- write (default dir under reports/evaluation, explicit output_dir, idempotent, outside blocked)
w = osm.write_operator_summary_mining(rr)
jp, mp = Path(w["json"]), Path(w["markdown"])
check(jp == rr / "evaluation" / "operator_summary_mining" / "operator_summary_mining.json" and jp.exists() and mp.exists(), "default write location")
check(json.loads(jp.read_text(encoding="utf-8")) == json.loads(json.dumps(p, ensure_ascii=False)) and mp.read_text(encoding="utf-8") == md, "written == built")
b1 = (jp.read_bytes(), mp.read_bytes()); osm.write_operator_summary_mining(rr)
check((jp.read_bytes(), mp.read_bytes()) == b1, "idempotent rewrite")
w2 = osm.write_operator_summary_mining(rr, output_dir=tmp / "custom")
check(Path(w2["json"]).parent == tmp / "custom" and Path(w2["json"]).read_bytes() == b1[0], "custom output_dir")
# source tree unchanged apart from outputs
src_after = [t for t in tree(tmp) if "evaluation" not in t[0] and not t[0].startswith("custom")]
check(src_after == before, "source artifacts untouched")
outside = exc_of(osm.write_operator_summary_mining, rr, output_dir=Path(tempfile.gettempdir()) / "rf032_osm_OUTSIDE_must_not_exist")
check(outside == "OSError" and not (Path(tempfile.gettempdir()) / "rf032_osm_OUTSIDE_must_not_exist").exists(), "outside write blocked")
bad.clear()
print("RF032_OPERATOR_SUMMARY_MINING_OK days=3 json_errors=1 mismatch=1 missing_surface=2 weekly=2/usable1 symbols=3 q9_total=15 readiness=%s empty=NEEDS_REPAIR idempotent=yes files=2 render_exc=%s outside_write=OSError_blocked net_attempts=0 debug=%s" % (rd["status"], json.dumps(rexc, sort_keys=True), __debug__))
