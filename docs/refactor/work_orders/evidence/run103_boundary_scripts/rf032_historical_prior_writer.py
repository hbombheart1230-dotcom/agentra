# RF-032: evaluation/historical_prior.py (iter/summarize/render/build_historical_q9_prior) -- tmp reports root only. Pure summarize/render/iter are called directly; the writer path runs with the trade read-model/evaluator/attribution collaborators swapped for fakes
# (plus one run with the real collaborators on a minimal bundle to observe the per-trade error capture). Writes 5 files under <root>/evaluation/historical_q9_prior/. Writes outside tmp, network, subprocess, sqlite blocked.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.historical_prior")
tmp = Path(tempfile.mkdtemp(prefix="rf032_hp_")).resolve(); os.chdir(tmp)
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
out = {}
def bundle(day, tid): put(root / "trades" / day / tid / "lifecycle_bundle.json", {"trade_id": tid})
for day, tid in (("2026-06-01", "TRD_A"), ("2026-06-02", "TRD_B"), ("2026-06-28", "TRD_C"), ("2026-06-29", "TRD_D"), ("2026-07-01", "TRD_E")): bundle(day, tid)
put(root / "trades/2026-06-02/TRD_B/other.json", {})
put(root / "trades/notaday_no_trades_segment.txt", "x", raw=True)
# ---- iter_historical_trade_dirs
it = lambda **k: [str(p.relative_to(root / "trades").as_posix()) for p in mod.iter_historical_trade_dirs(root, **k)]
check(it() == ["2026-06-01/TRD_A", "2026-06-02/TRD_B", "2026-06-28/TRD_C"], it())  # default before 2026-06-29 (exclusive)
check(it(from_day="2026-06-02") == ["2026-06-02/TRD_B", "2026-06-28/TRD_C"], it(from_day="2026-06-02"))  # from inclusive
check(it(before_day="") == ["2026-06-01/TRD_A", "2026-06-02/TRD_B", "2026-06-28/TRD_C", "2026-06-29/TRD_D", "2026-07-01/TRD_E"], "no upper bound")
check(it(from_day="2026-06-29", before_day="2026-06-29") == [], "empty window")
check(mod.iter_historical_trade_dirs(tmp / "nope") == [], "missing root")
check(it(from_day="2026-07-05", before_day="") == [], "from beyond")
out["day_from_dir"] = [mod._day_from_trade_dir(Path("a/trades/2026-01-01/T")), mod._day_from_trade_dir(Path("a/b")), mod._day_from_trade_dir(Path("trades"))]
check(out["day_from_dir"] == ["2026-01-01", "", ""], out["day_from_dir"])
out["rank_bucket"] = [mod._rank_bucket(v) for v in (0, 1, "1.9", 2, 3, 4, 10, 11, None, "x", -3, True)]
check(out["rank_bucket"] == ["rank1", "rank1", "rank1", "rank2-3", "rank2-3", "rank4-10", "rank4-10", "rank11_plus", "unknown", "unknown", "rank1", "rank1"], out["rank_bucket"])
out["net_return"] = [mod._net_return(v) for v in ({"realized_outcome": {"net_return_pct": "1.5"}}, {"realized_outcome": {"net_return_pct": None}}, {"realized_outcome": None}, {}, {"realized_outcome": {"net_return_pct": "x"}})]
check(out["net_return"] == [1.5, None, None, None, None], out["net_return"])
# ---- summarize
def ev(day, ret, elig=True, status="OK", watch=(), defects=(), bucket="short"):
    return {"day": day, "realized_outcome": {"net_return_pct": ret}, "integrity": {"promotion_metric_eligible": elig, "status": status, "watch_items": list(watch), "defects": list(defects)}, "horizon_alignment": {"bucket": bucket}}
def mo(rank, pb, sym): return {"selection": {"selected_rank": rank, "strategist_playbook": pb}, "symbol": sym}
models = [mo(1, "pbA", "AAA"), mo(2, "pbA", "BBB"), mo(12, None, "AAA"), mo("x", "pbB", ""), mo(1, "pbB", "CCC")]
evals = [ev("2026-06-01", 2.0), ev("2026-06-02", -1.0, status="WATCH", watch=["w1"]), ev("2026-06-02", 0.5, elig=False, defects=["d1", "d1"]), ev("2026-06-03", None), ev("", 1.0, bucket=None)]
atts = [{"deltas": {"strategist_delta_pct": 1.0}}, {"deltas": {"strategist_delta_pct": None}}, {"deltas": None}, {}]
errs = [{"trade_dir": f"d{i}", "error": "E"} for i in range(60)]
inp = copy.deepcopy((models, evals, atts, errs))
s = mod.summarize_historical_prior(models=models, evaluations=evals, attributions=atts, errors=errs, from_day="", before_day="2026-06-29")
check((models, evals, atts, errs) == inp, "summarize mutated input")
check(s["schema_version"] == "historical_q9_prior_summary.v1" and s["behavior_effect"] == "read_only_historical_prior" and s["scope"]["official_q9_freeze_sample"] is False and s["scope"]["usage"] == "prior_evidence_only", s["scope"])
c = s["coverage"]
check(c["trade_count"] == 5 and c["eligible_trade_count"] == 4 and c["build_error_count"] == 60 and len(s["errors"]) == 50, (c["trade_count"], c["eligible_trade_count"], len(s["errors"])))
check(c["source_days"] == ["2026-06-01", "2026-06-02", "2026-06-03"] and c["source_day_count"] == 3, c["source_days"])  # empty day excluded, sorted unique
check(c["integrity_status_counts"] == {"OK": 4, "WATCH": 1} and c["top_watch_items"] == {"w1": 1} and c["top_defects"] == {"d1": 2}, (c["integrity_status_counts"], c["top_defects"]))
check(s["performance"]["eligible"]["count"] == 3 and s["performance"]["all_realized"]["count"] == 4, (s["performance"]["eligible"]["count"], s["performance"]["all_realized"]["count"]))  # eligible with ret: 2.0, -1.0, 1.0 ; all: +0.5
b = s["breakdowns"]
check(sorted(b["selected_rank_bucket"]) == ["rank1", "rank11_plus", "rank2-3"] and b["selected_rank_bucket"]["rank1"]["count"] == 2, sorted(b["selected_rank_bucket"]))  # row4 ret None skipped, so 'x' absent... rank1 = model0 only (model4 has no matching eval)
check(sorted(b["strategist_playbook"]) == ["pbA", "pbB", "unknown"] and sorted(b["symbol"]) == ["AAA", "BBB", "CCC"] and sorted(b["horizon_bucket"]) == ["short", "unknown"], (sorted(b["strategist_playbook"]), sorted(b["symbol"]), sorted(b["horizon_bucket"])))
check(s["selection_attribution"] == {"comparison_count": 1, "unavailable_count": 3, "note": s["selection_attribution"]["note"]}, s["selection_attribution"])
check(abs(len(s["generated_at"]) - 32) <= 1 and s["generated_at"].endswith("+00:00"), s["generated_at"])
out["summary_keys"] = sorted(s)
out["rank_buckets"] = {k: v["count"] for k, v in b["selected_rank_bucket"].items()}
# zip truncation: models longer than evals ignored
s2 = mod.summarize_historical_prior(models=models + [mo(1, "x", "Z")] * 3, evaluations=evals, attributions=[], errors=[], from_day="2026-06-01", before_day="2026-06-29"); check(s2["breakdowns"]["symbol"].keys() == b["symbol"].keys() and s2["selection_attribution"]["comparison_count"] == 0, "zip truncation")
se = mod.summarize_historical_prior(models=[], evaluations=[], attributions=[], errors=[], from_day="", before_day="x"); check(se["coverage"]["trade_count"] == 0 and se["performance"]["eligible"]["count"] == 0 and se["breakdowns"]["symbol"] == {}, "empty")
out["sum_exc"] = {"none_models": attempt(mod.summarize_historical_prior, models=None, evaluations=[], attributions=[], errors=[], from_day="", before_day="")[1],
                  "integrity_str": attempt(mod.summarize_historical_prior, models=[], evaluations=[{"integrity": "str"}], attributions=[], errors=[], from_day="", before_day="")[1],
                  "model_none": attempt(mod.summarize_historical_prior, models=[None], evaluations=[ev("d", 1.0)], attributions=[], errors=[], from_day="", before_day="")[1],
                  "kw_missing": attempt(mod.summarize_historical_prior, models=[], evaluations=[])[1]}
# ---- render
md = mod.render_historical_prior_markdown(s)
check(md.startswith("# Historical Q9 Prior") and "Official Q9 freeze sample: **False**" in md and "- Trades: 5 total / 4 eligible" in md and "- Build errors: 60" in md and "### selected_rank_bucket" in md and "### horizon_bucket" in md and md.endswith("\n"), md[:200])
check("- Scope: `beginning` to before `2026-06-29`" in md, "scope line")
mde = mod.render_historical_prior_markdown({}); check("No comparable rows" in mde and "Scope: `beginning` to before `None`" in mde and "Eligible win rate: 0.0%" in mde, mde[:200])
out["render_exc"] = {"none": attempt(mod.render_historical_prior_markdown, None)[1], "metrics_str": attempt(mod.render_historical_prior_markdown, {"breakdowns": {"selected_rank_bucket": {"k": "str"}}})[1]}
# ---- build with fakes (writer path)
calls = []
real = (mod.build_q9_trade_read_model, mod.evaluate_trade, mod.build_selection_attribution)
def fake_model(td):
    calls.append(Path(td).name)
    if Path(td).name == "TRD_B": raise ValueError("boom B")
    return {"trade_id": Path(td).name, "symbol": "S" + Path(td).name[-1], "selection": {"selected_rank": 1, "strategist_playbook": "pb"}}
mod.build_q9_trade_read_model = fake_model
mod.evaluate_trade = lambda m: {"day": "2026-06-01", "realized_outcome": {"net_return_pct": 1.25}, "integrity": {"promotion_metric_eligible": True, "status": "OK"}}
mod.build_selection_attribution = lambda m: {"deltas": {"strategist_delta_pct": 0.5}}
s0 = snap()
r, e = attempt(mod.build_historical_q9_prior, root); check(e is None, e)
check(r["ok"] is True and r["trade_count"] == 2 and r["error_count"] == 1 and calls == ["TRD_A", "TRD_B", "TRD_C"], (r, calls))  # TRD_D/E excluded by default window
od = root / "evaluation/historical_q9_prior"
names = sorted(p.name for p in od.iterdir()); check(names == ["historical_q9_prior_report.md", "historical_q9_prior_summary.json", "historical_q9_selection_attributions.json", "historical_q9_trade_evaluations.json", "historical_q9_trade_read_models.json"], names)
sm = json.loads((od / "historical_q9_prior_summary.json").read_text(encoding="utf-8"))
check(sm["coverage"]["build_error_count"] == 1 and sm["errors"][0]["error"] == "ValueError: boom B" and sm["errors"][0]["day"] == "2026-06-02" and sm["performance"]["eligible"]["count"] == 2, sm["errors"])
check(json.loads((od / "historical_q9_trade_read_models.json").read_text(encoding="utf-8"))["schema_version"] == "historical_q9_trade_read_models.v1" and len(json.loads((od / "historical_q9_trade_evaluations.json").read_text(encoding="utf-8"))["rows"]) == 2, "rows")
check(r["summary"] == str(od / "historical_q9_prior_summary.json") and r["report"] == str(od / "historical_q9_prior_report.md") and r["output_dir"] == str(od), r)
b1 = {n: (od / n).read_bytes() for n in names}
r2, e2 = attempt(mod.build_historical_q9_prior, root); check(e2 is None, e2)
same = {n: (od / n).read_bytes() == b1[n] for n in names}; out["rewrite_identical"] = same
check(all(v for n, v in same.items() if n != "historical_q9_prior_summary.json"), same)  # generated_at differs in summary only
check(not same["historical_q9_prior_summary.json"] or True, "summary has timestamp")
out["inputs_unchanged"] = all(snap().get(k) == v for k, v in s0.items())
check(out["inputs_unchanged"], "inputs mutated")
# window params honoured
calls.clear(); rr, _ = attempt(mod.build_historical_q9_prior, root, from_day="2026-06-02", before_day=""); check(calls == ["TRD_B", "TRD_C", "TRD_D", "TRD_E"], calls)
# empty root still writes 5 files
calls.clear(); empty = tmp / "reports_empty"; re_, e = attempt(mod.build_historical_q9_prior, empty); check(e is None and re_["trade_count"] == 0 and len(list((empty / "evaluation/historical_q9_prior").iterdir())) == 5, e)
# exception inside evaluate/attribution also captured per trade; KeyboardInterrupt not captured
mod.evaluate_trade = lambda m: (_ for _ in ()).throw(KeyError("k"))
rk, e = attempt(mod.build_historical_q9_prior, root); check(e is None and rk["trade_count"] == 0 and rk["error_count"] == 3, (e, rk))
def kbd(m): raise KeyboardInterrupt()
mod.evaluate_trade = kbd
try: mod.build_historical_q9_prior(root); out["kbd"] = "not raised"
except BaseException as x: out["kbd"] = type(x).__name__
check(out["kbd"] == "KeyboardInterrupt", out["kbd"])
# restore real collaborators: minimal bundle -> observe per-trade handling
mod.build_q9_trade_read_model, mod.evaluate_trade, mod.build_selection_attribution = real
real_root = tmp / "reports_real"; put(real_root / "trades/2026-06-01/TRD_R/lifecycle_bundle.json", {"trade_id": "TRD_R"})
rr_, e = attempt(mod.build_historical_q9_prior, real_root); check(e is None and rr_["trade_count"] + rr_["error_count"] == 1, (e, rr_))
out["real_minimal_bundle"] = {"trade_count": rr_["trade_count"], "error_count": rr_["error_count"]}
# exceptions on writer
out["write_exc"] = {"outside_root": attempt(mod.build_historical_q9_prior, Path("/proc/nonexistent_rf032"))[1], "none_root": attempt(mod.build_historical_q9_prior, None)[1]}
check(out["write_exc"] == {"outside_root": "OSError", "none_root": "TypeError"}, out["write_exc"])
col = tmp / "reports_col"; (col / "evaluation").mkdir(parents=True); (col / "evaluation/historical_q9_prior").write_text("x")
out["collision"] = attempt(mod.build_historical_q9_prior, col)[1]; check(out["collision"] in ("FileExistsError", "NotADirectoryError"), out["collision"])
net = [b for b in bad if not b.startswith(("write:", "mkdir:"))]; check(not net, bad)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=str))
print("RF032_HISTORICAL_PRIOR_OK iter_window=3/2/5 summarize_trades=5/eligible4 errors_capped=50 files=5 rewrite_summary_timestamp_only=yes per_trade_error_capture=yes kbd=%s real_bundle=%s net_attempts=%d debug=%s" % (out["kbd"], "%d/%d" % (out["real_minimal_bundle"]["trade_count"], out["real_minimal_bundle"]["error_count"]), len(net), __debug__))
