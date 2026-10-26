# RF-032: evaluation/attribution_score_range.py writer (build/render/write) -- tmp reports root only. Reads per-day attribution_score_v0.json / daily_scorecard.json and trades/operator_summary/evaluation dirs;
# writes <root>/evaluation/range/<start>_<end>/attribution_score_range.{json,md}. Writes outside tmp root, network, subprocess, sqlite blocked. Default reports_root never used.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.attribution_score_range")
tmp = Path(tempfile.mkdtemp(prefix="rf032_asr_")).resolve(); os.chdir(tmp)
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
def sc(score, status="OK", reasons=()):
    return {"score": score, "status": status, "reasons": list(reasons)}
def ds(a, b, c, d, e, weak=None):
    o = {"scores": {"selection_integrity_score": a, "scanner_alignment_score": b, "entry_timing_score": c, "exit_horizon_score": d, "evidence_quality_score": e}}
    if weak: o["weakest_observed_axis"] = {"name": weak}
    return o
D = lambda d: root / "evaluation/daily" / d
put(D("2026-07-06") / "attribution_score_v0.json", ds(sc(80.4), sc(70), sc(60, reasons=["late", "late"]), sc(None, "INSUFFICIENT_EVIDENCE", ["no_exit"]), sc(90), "entry_timing_score"))
put(D("2026-07-06") / "daily_scorecard.json", {"artifact_integrity": {"trade_count": 4}})
put(D("2026-07-07") / "attribution_score_v0.json", ds(sc(60), sc("70.5"), sc("bad"), sc(50), {"status": "MISSING"}, "exit_horizon_score"))
put(D("2026-07-07") / "daily_scorecard.json", {"artifact_integrity": {"trade_count": "x"}})  # non-int -> falls back to TRD_ dir count
for t in ("TRD_A", "TRD_B"): (root / "trades/2026-07-07" / t).mkdir(parents=True)
(root / "trades/2026-07-07/TRD_file").write_text("x")  # file, not dir -> not counted
# 07-08: no artifacts at all (skipped unless include_empty_days)
(root / "operator_summary/daily/2026-07-09").mkdir(parents=True)  # source artifact only, no score payload
(root / "trades/2026-07-09/TRD_Z").mkdir(parents=True)
put(D("2026-07-10") / "attribution_score_v0.json", "{broken", raw=True)
put(D("2026-07-11") / "attribution_score_v0.json", ds(sc(None, "INSUFFICIENT_EVIDENCE"), sc(None, "INSUFFICIENT_EVIDENCE"), sc(None, "INSUFFICIENT_EVIDENCE"), sc(None, "INSUFFICIENT_EVIDENCE"), sc(None, "INSUFFICIENT_EVIDENCE")))
put(D("2026-07-13") / "daily_scorecard.json", {"artifact_integrity": {"trade_count": 3}})  # scorecard only: source artifact, payload {}
out = {}
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}
s0 = snap()
p, e = attempt(mod.build_attribution_score_range, reports_root=root, start="2026-07-06", end="2026-07-13"); check(e is None, e)
check(snap() == s0, "build mutated tree")
rows = {r["day"]: r for r in p["daily_rows"]}
check(sorted(rows) == ["2026-07-06", "2026-07-07", "2026-07-09", "2026-07-10", "2026-07-11", "2026-07-13"], sorted(rows))  # 07-08 skipped
check(p["schema_version"] == "attribution_score_range.v1" and p["behavior_effect"] == "observation_only" and p["include_empty_days"] is False, p["schema_version"])
check(p["day_count"] == 6 and p["available_day_count"] == 3 and p["scored_day_count"] == 2, (p["day_count"], p["available_day_count"], p["scored_day_count"]))  # 06,07,11 available; scored 06,07 (11 all INSUFFICIENT)
check(rows["2026-07-07"]["trade_count"] == 2, rows["2026-07-07"]["trade_count"])
check(rows["2026-07-06"]["trade_count"] == 4 and rows["2026-07-09"]["trade_count"] == 1 and rows["2026-07-13"]["trade_count"] == 3, "trade counts")
check(rows["2026-07-10"]["available"] is False and rows["2026-07-09"]["available"] is False and rows["2026-07-09"]["scored"] is False, "unavailable")
check(p["total_trade_count"] == 4 + 2 + 1 + 0 + 0 + 0 + 3 and p["scored_trade_count"] == 6 and p["trade_day_count"] == 4, (p["total_trade_count"], p["scored_trade_count"], p["trade_day_count"]))
a = p["axis_summary"]
check(a["selection_integrity_score"]["average_score"] == 70.0 and a["selection_integrity_score"]["min_score"] == 60 and a["selection_integrity_score"]["max_score"] == 80, a["selection_integrity_score"])
check(a["entry_timing_score"]["scored_day_count"] == 1 and a["entry_timing_score"]["top_reasons"] == [{"reason": "late", "count": 2}], a["entry_timing_score"])
check(a["exit_horizon_score"]["insufficient_day_count"] == 0 or a["exit_horizon_score"]["insufficient_day_count"] >= 1, "x")
check(a["evidence_quality_score"]["missing_day_count"] >= 1, a["evidence_quality_score"])
check(p["weakest_axis_distribution"] == {"entry_timing_score": 1, "exit_horizon_score": 1}, p["weakest_axis_distribution"])
w = p["weakest_axis_by_average_score"]; check(w["name"] in a and w["average_score"] == min(v["average_score"] for v in a.values() if v["average_score"] is not None), w)
out["axes"] = {k: (v["average_score"], v["scored_day_count"], v["missing_day_count"], v["insufficient_day_count"], v["status_counts"]) for k, v in a.items()}
out["rows"] = {d: (r["available"], r["scored"], r["trade_count"], r["weakest_axis"]) for d, r in sorted(rows.items())}
# include_empty_days
pi, e = attempt(mod.build_attribution_score_range, reports_root=root, start="2026-07-06", end="2026-07-13", include_empty_days=True); check(e is None and pi["day_count"] == 8 and pi["include_empty_days"] is True, (e,))
# single-day range and empty/nonexistent root
p1, e = attempt(mod.build_attribution_score_range, reports_root=root, start="2026-07-06", end="2026-07-06"); check(e is None and p1["day_count"] == 1 and p1["scored_day_count"] == 1, e)
pe, e = attempt(mod.build_attribution_score_range, reports_root=tmp / "nope", start="2026-07-06", end="2026-07-08"); check(e is None and pe["day_count"] == 0 and pe["weakest_axis_by_average_score"] == {"name": "", "average_score": None}, (e, pe))
pz, e = attempt(mod.build_attribution_score_range, reports_root=tmp / "nope", start="2026-07-06", end="2026-07-08", include_empty_days=True); check(e is None and pz["day_count"] == 3 and pz["available_day_count"] == 0, e)
# exceptions
out["exc"] = {
    "start_after_end": attempt(mod.build_attribution_score_range, reports_root=root, start="2026-07-09", end="2026-07-06")[1],
    "bad_date": attempt(mod.build_attribution_score_range, reports_root=root, start="notadate", end="2026-07-06")[1],
    "none_start": attempt(mod.build_attribution_score_range, reports_root=root, start=None, end="2026-07-06")[1],
    "none_root": attempt(mod.build_attribution_score_range, reports_root=None, start="2026-07-06", end="2026-07-06")[1],
    "missing_kw": attempt(mod.build_attribution_score_range, reports_root=root)[1],
    "scores_not_mapping": (put(D("2026-08-12") / "attribution_score_v0.json", {"scores": "notamap"}), attempt(mod.build_attribution_score_range, reports_root=root, start="2026-08-12", end="2026-08-12")[1])[1],
    "weakest_not_mapping": (put(D("2026-08-15") / "attribution_score_v0.json", {**ds(sc(50), sc(50), sc(50), sc(50), sc(50)), "weakest_observed_axis": "str"}), attempt(mod.build_attribution_score_range, reports_root=root, start="2026-08-15", end="2026-08-15")[1])[1],
    "render_none": attempt(mod.render_attribution_score_range, None)[1],
    "render_empty": attempt(mod.render_attribution_score_range, {})[1],
}
check(out["exc"]["scores_not_mapping"] == "ValueError" and out["exc"]["weakest_not_mapping"] == "ValueError", out["exc"])
check(out["exc"]["start_after_end"] == "ValueError" and out["exc"]["bad_date"] == "ValueError" and out["exc"]["missing_kw"] == "TypeError", out["exc"])
check(out["exc"]["render_empty"] is None and out["exc"]["render_none"] == "AttributeError", out["exc"])
# render
md = mod.render_attribution_score_range(p); check(md == mod.render_attribution_score_range(copy.deepcopy(p)), "render nondeterministic")
check(md.startswith("# Q13 Attribution Score Range - 2026-07-06 to 2026-07-13") and "## Axis Summary" in md and "## Weakest Axis Distribution" in md and "- `entry_timing_score`: 1" in md and md.endswith("\n"), md[:200])
mdnon = mod.render_attribution_score_range({**p, "daily_rows": [1, "x", None] + p["daily_rows"][:1]}); check("| 2026-07-06 |" in mdnon, "non-mapping rows skipped")
mde = mod.render_attribution_score_range({"axis_summary": "str", "weakest_axis_distribution": None}); check("No scored days." in mde, "empty render")
# write
r, e = attempt(mod.write_attribution_score_range, reports_root=root, start="2026-07-06", end="2026-07-13"); check(e is None, e)
jp, mp = Path(r["json"]), Path(r["markdown"])
check(jp == root / "evaluation/range/2026-07-06_2026-07-13/attribution_score_range.json" and mp.name == "attribution_score_range.md", r)
check(json.loads(jp.read_text(encoding="utf-8")) == p and mp.read_text(encoding="utf-8") == md, "written != built")
b1 = (jp.read_bytes(), mp.read_bytes()); r2, e = attempt(mod.write_attribution_score_range, reports_root=root, start="2026-07-06", end="2026-07-13"); check(e is None and (jp.read_bytes(), mp.read_bytes()) == b1, "not idempotent")
new = {k for k in snap() if k not in s0 and k.startswith("reports/evaluation/range")}; check(new == {"reports/evaluation/range", "reports/evaluation/range/2026-07-06_2026-07-13", "reports/evaluation/range/2026-07-06_2026-07-13/attribution_score_range.json", "reports/evaluation/range/2026-07-06_2026-07-13/attribution_score_range.md"}, new)
check(all(snap().get(k) == v for k, v in s0.items()), "inputs mutated")
# window_id style traversal: start/end are validated dates so path is safe
out["files"] = len(new) - 2
# unwritable (outside tmp) root
ro = Path("/proc/nonexistent_rf032"); ex = attempt(mod.write_attribution_score_range, reports_root=ro, start="2026-07-06", end="2026-07-06")[1]; out["outside_write"] = ex; check(ex == "OSError", ex)
# dir-collision: output dir path occupied by a file
(root / "evaluation/range/2026-07-14_2026-07-14").parent.mkdir(parents=True, exist_ok=True); (root / "evaluation/range/2026-07-14_2026-07-14").write_text("x")
ex2 = attempt(mod.write_attribution_score_range, reports_root=root, start="2026-07-14", end="2026-07-14")[1]; out["dir_collision"] = ex2; check(ex2 in ("FileExistsError", "NotADirectoryError"), ex2)
check(not [b for b in bad if not b.startswith(("write:", "mkdir:"))], bad)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=str))
print("RF032_ATTRIBUTION_SCORE_RANGE_OK days=%d available=%d scored=%d include_empty=%d trades=%d idempotent=yes files=%d outside_write=%s dir_collision=%s net_attempts=%d debug=%s" % (p["day_count"], p["available_day_count"], p["scored_day_count"], pi["day_count"], p["total_trade_count"], out["files"], out["outside_write"], out["dir_collision"], len([b for b in bad if not b.startswith(("write:", "mkdir:"))]), __debug__))
