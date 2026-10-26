# RF-032: evaluation/attribution_score_window.py writer (build/render/write) -- tmp reports root only. Reads freeze-window daily_ledger.json +
# per-day attribution_score_v0.json / daily_scorecard.json; writes <root>/evaluation/freeze_window/<id>/attribution_score_window.{json,md}.
# Writes outside the tmp root, network, subprocess and sqlite are blocked. UEF / frozen window / real reports are NOT touched (default reports_root never used).
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.attribution_score_window")
tmp = Path(tempfile.mkdtemp(prefix="rf032_asw_")).resolve(); os.chdir(tmp)
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
W = "w_test"; root = tmp / "reports"
def sc(score, status="OK", reasons=()):
    return {"score": score, "status": status, "reasons": list(reasons)}
def day_scores(sel, scan, ent, ext, evd):
    return {"scores": {"selection_integrity_score": sel, "scanner_alignment_score": scan, "entry_timing_score": ent, "exit_horizon_score": ext, "evidence_quality_score": evd}}
put(root / "evaluation/freeze_window" / W / "daily_ledger.json", {"days": [
    {"day": "2026-06-29", "counts_as_valid_day": True}, {"day": "2026-06-30", "counts_as_valid_day": True},
    {"day": "2026-07-01", "counts_as_valid_day": False}, {"day": "2026-07-02", "counts_as_valid_day": True}, "junk", {"day": "2026-07-03", "counts_as_valid_day": True}]})
put(root / "evaluation/daily/2026-06-29/attribution_score_v0.json", {**day_scores(sc(80.4), sc(70), sc(60, reasons=["late", "late"]), sc(None, "INSUFFICIENT_EVIDENCE", ["no_exit"]), sc(90)), "weakest_observed_axis": {"name": "entry_timing_score"}})
put(root / "evaluation/daily/2026-06-29/daily_scorecard.json", {"artifact_integrity": {"trade_count": 4}})
put(root / "evaluation/daily/2026-06-30/attribution_score_v0.json", {**day_scores(sc(60), sc("70.5"), sc("bad"), sc(50), {"status": "MISSING"}), "weakest_observed_axis": {"name": "exit_horizon_score"}})
put(root / "evaluation/daily/2026-07-01/attribution_score_v0.json", {**day_scores(sc(10), sc(10), sc(10), sc(10), sc(10)), "weakest_observed_axis": {"name": "selection_integrity_score"}})
put(root / "evaluation/daily/2026-07-02/attribution_score_v0.json", "{not json", raw=True)
put(root / "evaluation/daily/2026-07-03/attribution_score_v0.json", [1, 2])
put(root / "evaluation/daily/2026-07-03/daily_scorecard.json", {"artifact_integrity": {"trade_count": 2}})
snap = {str(p.relative_to(tmp).as_posix()): p.read_bytes() for p in tmp.rglob("*") if p.is_file()}
out = {}
# build is read-only
p1, e = attempt(mod.build_attribution_score_window, reports_root=root, window_id=W); check(e is None, e)
check({str(p.relative_to(tmp).as_posix()): p.read_bytes() for p in tmp.rglob("*") if p.is_file()} == snap, "build wrote files")
check(not (root / "evaluation/freeze_window" / W / "attribution_score_window.json").exists(), "build created output")
check(p1["schema_version"] == "attribution_score_window.v1" and p1["behavior_effect"] == "observation_only" and p1["window_id"] == W, p1["schema_version"])
check(p1["day_count"] == 5 and p1["valid_day_count"] == 4 and p1["available_day_count"] == 3, (p1["day_count"], p1["valid_day_count"], p1["available_day_count"]))  # "junk" ledger row skipped; 06-29, 06-30, 07-01 available
check(p1["total_trade_count_valid_days"] == 4, p1["total_trade_count_valid_days"])  # unavailable valid days contribute trade_count 0
rows = {r["day"]: r for r in p1["daily_rows"]}
check(rows["2026-07-02"]["available"] is False and rows["2026-07-02"]["trade_count"] == 0, "broken JSON -> unavailable")
check(rows["2026-07-03"]["available"] is False, "list payload -> {} -> unavailable")
ax = p1["axis_summary"]
check(ax["selection_integrity_score"]["average_score"] == 70.0 and ax["selection_integrity_score"]["min_score"] == 60 and ax["selection_integrity_score"]["max_score"] == 80, ax["selection_integrity_score"])  # round(80.4)=80, 60
check(ax["scanner_alignment_score"]["average_score"] == 70.5 or ax["scanner_alignment_score"]["average_score"] == 71.0 or ax["scanner_alignment_score"]["scored_day_count"] == 2, ax["scanner_alignment_score"])
check(ax["entry_timing_score"]["scored_day_count"] == 1 and ax["entry_timing_score"]["top_reasons"] == [{"reason": "late", "count": 2}], ax["entry_timing_score"])  # "bad" score non-numeric -> excluded
check(ax["exit_horizon_score"]["insufficient_day_count"] == 1 and ax["exit_horizon_score"]["scored_day_count"] == 1, ax["exit_horizon_score"])
check(ax["evidence_quality_score"]["status_counts"].get("MISSING") == 3 and ax["evidence_quality_score"]["scored_day_count"] == 1, ax["evidence_quality_score"])
check(p1["weakest_axis_distribution"] == {"entry_timing_score": 1, "exit_horizon_score": 1}, p1["weakest_axis_distribution"])  # invalid 07-01 excluded
check(rows["2026-07-01"]["valid"] is False and rows["2026-07-01"]["selection_integrity_score"] == 10, "invalid day shown for audit")
w = p1["weakest_axis_by_average_score"]; check(w["name"] in ax and w["average_score"] == min(v["average_score"] for v in ax.values() if v["average_score"] is not None), w)
out["axes"] = {k: (v["average_score"], v["scored_day_count"]) for k, v in ax.items()}
# empty / missing window / odd ledger
pe, ee = attempt(mod.build_attribution_score_window, reports_root=tmp / "nope", window_id="none"); check(ee is None and pe["day_count"] == 0 and pe["weakest_axis_by_average_score"] == {"name": "", "average_score": None}, (ee, pe))
put(root / "evaluation/freeze_window/w_bad/daily_ledger.json", {"days": "notalist"}); pb, eb = attempt(mod.build_attribution_score_window, reports_root=root, window_id="w_bad"); out["ledger_days_str"] = (eb, None if pb is None else pb["day_count"])
put(root / "evaluation/freeze_window/w_nulls/daily_ledger.json", {"days": None}); pn, en = attempt(mod.build_attribution_score_window, reports_root=root, window_id="w_nulls"); check(en is None and pn["day_count"] == 0, (en, pn))
# string reports_root coerced; deterministic
ps, es = attempt(mod.build_attribution_score_window, reports_root=str(root), window_id=W); check(es is None and ps == p1, "str root + deterministic")
# render
md, er = attempt(mod.render_attribution_score_window, p1); check(er is None and md.endswith("\n") and "| selection_integrity_score | 70.0 |" in md and "- `entry_timing_score`: 1" in md, md[:300])
check("| 2026-07-01 | False |" in md, "invalid day row rendered")
check(attempt(mod.render_attribution_score_window, {})[1] is None and "No valid scored days." in mod.render_attribution_score_window({}), "empty payload render")
rr = attempt(mod.render_attribution_score_window, None)[1]; out["render_none"] = rr
# write
res, ew = attempt(mod.write_attribution_score_window, reports_root=root, window_id=W); check(ew is None, ew)
jp, mp = Path(res["json"]), Path(res["markdown"]); check(jp.parent == root / "evaluation/freeze_window" / W and jp.name == "attribution_score_window.json" and mp.name == "attribution_score_window.md", res)
check(json.loads(jp.read_text(encoding="utf-8")) == p1 and jp.read_text(encoding="utf-8").endswith("\n") and mp.read_text(encoding="utf-8") == md, "written == built/rendered")
b1 = (jp.read_bytes(), mp.read_bytes()); res2, _ = attempt(mod.write_attribution_score_window, reports_root=root, window_id=W); check((jp.read_bytes(), mp.read_bytes()) == b1 and res2 == res, "idempotent rewrite")
# the written output is not an input (no feedback): rebuild unchanged
check(attempt(mod.build_attribution_score_window, reports_root=root, window_id=W)[0] == p1, "output not re-read as input")
# new window id creates dir tree; non-writable target blocked
rw, ex = attempt(mod.write_attribution_score_window, reports_root=tmp / "fresh", window_id="w_new"); check(ex is None and Path(rw["json"]).exists(), ex)
outside = Path(tempfile.gettempdir()).resolve() / "rf032_asw_outside_probe"; ro, eo = attempt(mod.write_attribution_score_window, reports_root=outside, window_id="x"); check(eo == "OSError" and not outside.exists(), "outside tmp blocked: %s" % eo)
out["outside"] = eo
bw, ebw = attempt(mod.write_attribution_score_window, reports_root=root, window_id="../../escape"); out["traversal"] = (ebw, None if bw is None else Path(bw["json"]).resolve().relative_to(tmp).as_posix())
check(ebw is None or ebw == "OSError", "traversal id result")
nc, enc = attempt(mod.write_attribution_score_window, reports_root=None); out["root_none"] = enc
# no mutation of inputs, only the expected new files
after = {str(p.relative_to(tmp).as_posix()): p.read_bytes() for p in tmp.rglob("*") if p.is_file()}
check(all(after[k] == v for k, v in snap.items()), "input fixtures changed")
new = sorted(k for k in after if k not in snap); check(all(k.endswith(("attribution_score_window.json", "attribution_score_window.md")) or k.endswith("daily_ledger.json") for k in new), new)
check(not [b for b in bad if not b.startswith(("write:", "write_text:", "mkdir:"))], bad)
shutil.rmtree(tmp, ignore_errors=True)
print("RF032_ATTRIBUTION_SCORE_WINDOW_OK days=5 valid=4 available=3 axes=%s weakest=%s idempotent=yes new_files=%d ledger_days_str=%s render_none=%s outside_write=%s traversal=%s root_none=%s net_attempts=0 debug=%s" % (
    out["axes"], p1["weakest_axis_by_average_score"]["name"], len(new), out["ledger_days_str"], out["render_none"], out["outside"], out["traversal"], out["root_none"], __debug__))
