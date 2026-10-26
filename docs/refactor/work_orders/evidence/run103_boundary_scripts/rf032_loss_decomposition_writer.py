# RF-032: libs/reporting/evaluation/loss_decomposition.py (evaluation writer; not covered by run 105/108/118/120):
# build/render/write_loss_decomposition on a fully tmp tree (reports/trades/<day>/**/lifecycle_bundle.json, data/logs/quant_shadow_candidates,
# data/state.json minute rows). No network/subprocess/sqlite, all writes outside tmp blocked. Run from repository root.
import os, sys, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
from datetime import datetime, timezone, timedelta
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
repo = os.getcwd(); sys.path.insert(0, repo); sys.dont_write_bytecode = True
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf032_ld_")).resolve()
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def tree(root): return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())
def exc_of(f, *a, **k):
    try: f(*a, **k); return "no_raise"
    except Exception as e: return type(e).__name__
KST = timezone(timedelta(hours=9))
os.chdir(tmp)   # data/state.json is resolved relative to cwd by load_minute_rows_from_state
ld = importlib.import_module("libs.reporting.evaluation.loss_decomposition")
reports = tmp / "reports"; reports.mkdir()
shadow = tmp / "data" / "logs" / "quant_shadow_candidates"
days = ["2026-06-22", "2026-06-23"]
def epoch(day, hh, mm): return int(datetime.strptime(day, "%Y-%m-%d").replace(hour=hh, minute=mm, tzinfo=KST).timestamp())
def rawts(day, hh, mm): return day.replace("-", "") + "%02d%02d00" % (hh, mm)
minute = {}; by_day = {d: [] for d in days}
for day in days:
    for r in range(1, 7):
        sym = "%06d" % (100000 + r)
        drift = (2.0 - 0.3 * r) / 100.0
        rows = []
        for m in range(0, 50):
            hh, mm = 9 + (10 + m) // 60, (10 + m) % 60
            px = round(10000.0 * (1 + drift * min(m, 30) / 30.0), 4)
            rows.append({"ts": epoch(day, hh, mm), "close": px, "high": px, "low": px, "raw_ts": rawts(day, hh, mm)})
        minute.setdefault(sym, []).extend(rows)
        by_day[day].append({"q9_decision_role": "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "q9_decision_id": "d-" + day, "symbol": sym, "rank": r,
                            "shadow_role": "top_pick" if r == 1 else "runner_up", "quant_tactic_id": "tac_a" if r % 2 else "tac_b", "reason": "r%d" % r,
                            "shadow_forward_base": {"available": True, "baseline_epoch": epoch(day, 9, 10), "baseline_price": 10000.0, "baseline_raw_ts": rawts(day, 9, 10)}})
for day, cands in by_day.items():
    d = shadow / day; d.mkdir(parents=True)
    (d / "a.json").write_text(json.dumps({"generated_at": day + "T09:10:30+09:00", "candidates": cands + ["not-a-mapping", None, cands[0]]}), encoding="utf-8")
    (d / "broken.json").write_text("{nope", encoding="utf-8")
(tmp / "data" / "state.json").write_text(json.dumps({"recent_minute_ohlcv_by_symbol": minute}), encoding="utf-8")
# one realized trade per day, symbol 100001 (shadow baseline 09:10 KST = 00:10Z; entry 09:12 KST at +1.0% vs baseline), one trade with no matching shadow
def trade(day, sym, tid, entry_ts, entry_px, pnl):
    td = reports / "trades" / day / sym / tid; td.mkdir(parents=True)
    (td / "lifecycle_bundle.json").write_text(json.dumps({"day": day, "trade_id": tid, "symbol": sym, "lifecycle": {
        "entry": {"ts": entry_ts, "action": "BUY", "execution_details": {"filled_price": entry_px}},
        "exit": {"ts": entry_ts.replace("T00:12", "T00:40"), "action": "SELL", "execution_details": {"filled_price": entry_px * 0.99, "broker_realized_pnl_pct": pnl, "broker_day_authoritative": True}}}}), encoding="utf-8")
trade("2026-06-22", "100001", "TRD_1", "2026-06-22T00:12:00+00:00", 10100, -0.0128)
trade("2026-06-23", "100001", "TRD_2", "2026-06-23T00:12:00+00:00", 10000, 0.0072)
trade("2026-06-23", "555555", "TRD_3", "2026-06-23T00:12:00+00:00", 5000, -0.0328)       # symbol with no shadow baseline -> unmatched
(reports / "trades" / "2026-06-24").mkdir()                                                # empty day dir
before = tree(tmp)
# ---- guards (installed after fixture creation)
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt, _mk, _rp, _ul = Path.write_text, Path.mkdir, Path.replace, Path.unlink
def g(orig, tag):
    def f(self, *a, **k):
        if not inside(self): bad.append(tag + ":" + str(self)); raise OSError("blocked")
        return orig(self, *a, **k)
    return f
Path.write_text, Path.mkdir, Path.replace, Path.unlink = g(_wt, "write_text"), g(_mk, "mkdir"), g(_rp, "replace"), g(_ul, "unlink")
# ---- pure helpers
check(ld._rank_bucket(None) == "unknown" and ld._rank_bucket("x") == "unknown" and ld._rank_bucket("2.9") == "rank2-3" and ld._rank_bucket(11) == "rank11+" and ld._rank_bucket(0) == "rank2-3", "rank bucket (0 -> rank2-3 quirk)")
check(list(ld._iter_days("2026-06-22T09:00", "2026-06-24")) == ["2026-06-22", "2026-06-23", "2026-06-24"] and list(ld._iter_days("2026-06-24", "2026-06-22")) == [], "iter_days")
check(exc_of(lambda: list(ld._iter_days("bad", "2026-06-22"))) == "ValueError", "iter_days bad date")
check(ld._to_float("") is None and ld._to_float("1.5") == 1.5 and ld._to_float("x") is None and ld._parse_ts("2026-06-22T00:00:00Z").tzinfo is not None and ld._parse_ts("bad") is None, "to_float/parse_ts")
# ---- build
out = ld.build_loss_decomposition(reports_root=reports, start=days[0], end="2026-06-24")
check(tree(tmp) == before and not bad, "build wrote nothing / no blocked effect: %r" % bad)
check(out["schema_version"] == "full_chain_loss_decomposition.v1" and out["behavior_effect"] == "evaluation_only" and out["range"] == {"start": days[0], "end": "2026-06-24"}, "header")
ev = out["evidence"]
check(ev["shadow_payload_count"] == 2 and ev["trade_model_count"] == 3, "payloads 2 (broken.json skipped), trade models 3 (empty day ok): %r" % ev)
check(ev["raw_shadow_candidate_count"] is not None and ev["deduped_shadow_candidate_count"] is not None and ev["deduped_shadow_candidate_count"] <= ev["raw_shadow_candidate_count"], "dedup <= raw")
sr = out["scanner_ranking"]
rb = {r["name"]: r for r in sr["by_rank_bucket"]}
check(rb["rank1"]["candidate_count"] == 2 and rb["rank2-3"]["candidate_count"] == 4 and rb["rank4-5"]["candidate_count"] == 4 and rb["rank6-10"]["candidate_count"] == 2, "rank buckets (dup + non-mapping rows dropped): %r" % {k: v["candidate_count"] for k, v in rb.items()})
r1 = rb["rank1"]
check(r1["observed_30m"] == 2 and abs(r1["avg_return_30m_pct"] - 1.7) < 0.01 and r1["coverage"] == 1.0 and r1["observed_60m"] == 0 and r1["avg_return_60m_pct"] is None, "rank1 +30m ~ 1.7pct, no +60m: %r" % (r1,))
check(rb["rank6-10"]["avg_return_30m_pct"] < rb["rank1"]["avg_return_30m_pct"], "deeper rank worse")
roles = {r["name"]: r for r in sr["by_selection_role"]}
check(sorted(roles) == ["runner_up", "top_pick"] and roles["top_pick"]["candidate_count"] == 2 and sr["control_status"] == "RECONSTRUCTED_ONLY", "roles")
check(sorted(r["name"] for r in out["raw_candidate_edge"]["by_tactic"]) == ["tac_a", "tac_b"], "tactics")
check(out["strategist_commander"]["status"] == "UNAVAILABLE", "strategist commander unavailable")
rs = out["realized_system"]
check(rs["comparable_trade_count"] == 3 and rs["scanner_top1_execution_mismatch_count"] == 0, "realized: 3 comparable: %r" % {k: rs[k] for k in ("comparable_trade_count",)})
check(rs["by_executed_rank"] and rs["by_executed_rank"][0]["rank_bucket"] == "unknown", "executed rank unknown (no selected_rank)")
me = out["monitor_entry"]
check(me["matched_trade_count"] == 2 and me["matched_day_count"] == 2 and me["late_entry_count"] == 1 and me["better_entry_count"] == 0, "entry timing: TRD_1 +1.0pct late, TRD_2 0.0pct, TRD_3 unmatched: %r" % {k: me[k] for k in ("matched_trade_count", "late_entry_count", "better_entry_count")})
check(abs(me["average_entry_price_delta_pct"] - 0.5) < 1e-6 and abs(me["median_entry_price_delta_pct"] - 0.5) < 1e-6, "avg/median delta 0.5")
check(out["monitor_exit"]["observed_trade_count"] == 0 and out["monitor_exit"]["by_hold_offset"] == [], "no post-exit data")
check([d["stage"] for d in out["diagnosis"]] == ["raw_candidate_edge", "scanner_ranking", "strategist_commander", "monitor_entry", "monitor_exit", "realized_system"], "diagnosis stages")
na = out["next_action"]
check(na["behavior_change_authorized"] is False and na["decision"] == "FIX_BEFORE_ENTRY_OR_EXIT_TUNING", "next action fixed text, behavior change not authorized")
# static-text caveat: next_action.reason / diagnosis 'NEGATIVE' status are hard-coded, not derived from data
pos = ld._diagnosis(shadow={}, candidate_rank=[], realized={"performance": {"count": 9, "expectancy_pct": 5.0, "profit_factor": 3.0}}, entry={}, exit_hold={})
check(pos[-1]["status"] == "NEGATIVE" and pos[0]["status"] == "CONDITIONAL_EDGE", "OBSERVATION: realized_system status is hard-coded NEGATIVE even for +5.0 expectancy")
posn = ld._next_action(role_rows=[], realized={"performance": {"expectancy_pct": 5.0}}, exit_hold={})
check(posn["decision"] == "FIX_BEFORE_ENTRY_OR_EXIT_TUNING" and "deeply negative" in posn["reason"], "OBSERVATION: next_action decision/reason are static text regardless of data")
# ---- pure summaries with synthetic models (post-exit hold, selection mismatch, parse failures)
models = [
    {"trade_id": "t1", "symbol": "A", "day": "2026-06-22", "outcome": {"net_return_pct": 1.0}, "selection": {"selected_rank": 1, "selected_symbol": "A", "scanner_top1": {"symbol": "B"}},
     "monitor": {"post_exit": {"checkpoints": {"+5m": {"status": "observed", "return_pct": 0.01}, "+15m": {"status": "pending", "return_pct": 0.5}, "+30m": {"status": "observed", "return_pct": "x"}}}}},
    {"trade_id": "t2", "symbol": "A", "day": "2026-06-23", "outcome": {"net_return_pct": "bad"}, "selection": "notmap", "monitor": {"post_exit": {"checkpoints": {"+5m": {"status": "observed", "return_pct": -0.02}}}}},
    {"trade_id": "t3", "symbol": "A", "entry": {"timestamp": "bad", "price": 1}},
]
rsum = ld._realized_trade_summary(models[:1])
check(rsum["comparable_trade_count"] == 1 and rsum["scanner_top1_execution_mismatch_count"] == 1 and rsum["by_executed_rank"][0]["rank_bucket"] == "rank1", "synthetic realized/mismatch")
check(exc_of(ld._realized_trade_summary, models[1:2]) == "no_raise" and ld._realized_trade_summary(models[1:2])["comparable_trade_count"] == 0, "non-numeric net_return skipped before selection is touched")
check(exc_of(ld._realized_trade_summary, [{"outcome": {"net_return_pct": 1.0}, "selection": "notmap"}]) == "AttributeError", "non-mapping selection with numeric return -> AttributeError (fail-hard)")
eh = ld._exit_hold_summary(models)
hb = {r["offset"]: r for r in eh["by_hold_offset"]}
check(eh["observed_trade_count"] == 2 and eh["observed_day_count"] == 2 and list(hb) == ["+5m"] and hb["+5m"]["count"] == 2 and hb["+5m"]["average_improvement_pct"] == -0.5 and hb["+5m"]["improved_count"] == 1 and hb["+5m"]["worsened_count"] == 1, "exit hold: ratio*100, pending/non-numeric skipped: %r" % eh["by_hold_offset"])
check(ld._entry_timing_summary(models[2:], [])["matched_trade_count"] == 0 and ld._entry_timing_summary([], [])["average_entry_price_delta_pct"] is None, "entry timing empties")
# ---- render
md = ld.render_loss_decomposition(out)
check(isinstance(md, str) and md.endswith("\n") and "behavior change authorized: **False**" in md and md == ld.render_loss_decomposition(copy.deepcopy(out)), "markdown deterministic")
check(exc_of(ld.render_loss_decomposition, {}) in ("no_raise",), "render empty payload")
# ---- write
od = tmp / "out"
w = ld.write_loss_decomposition(reports_root=reports, start=days[0], end="2026-06-24", output_dir=od)
jp, mp = Path(w["json"]), Path(w["markdown"])
check(jp.name == "full_chain_loss_decomposition.json" and mp.name == "full_chain_loss_decomposition.md" and jp.parent == od, "output names")
check(json.loads(jp.read_text(encoding="utf-8")) == json.loads(json.dumps(out, ensure_ascii=False)) and mp.read_text(encoding="utf-8") == md and jp.read_text(encoding="utf-8").endswith("}\n"), "written == built")
b1 = (jp.read_bytes(), mp.read_bytes()); ld.write_loss_decomposition(reports_root=reports, start=days[0], end="2026-06-24", output_dir=od)
check((jp.read_bytes(), mp.read_bytes()) == b1, "idempotent rewrite")
check([t for t in tree(tmp) if not t[0].startswith("out")] == before, "source tree untouched")
oexc = exc_of(ld.write_loss_decomposition, reports_root=reports, start=days[0], end=days[0], output_dir=Path(tempfile.gettempdir()) / "rf032_ld_OUTSIDE_must_not_exist")
check(oexc == "OSError" and not (Path(tempfile.gettempdir()) / "rf032_ld_OUTSIDE_must_not_exist").exists(), "outside write blocked")
bad.clear()
bexc = {"bad_start": exc_of(ld.build_loss_decomposition, reports_root=reports, start="bad", end="2026-06-22"), "empty_range": exc_of(ld.build_loss_decomposition, reports_root=reports, start="2026-07-01", end="2026-06-01"),
        "missing_root": exc_of(ld.build_loss_decomposition, reports_root=tmp / "nope", start=days[0], end=days[0])}
check(bexc["bad_start"] == "ValueError" and bexc["empty_range"] == "no_raise" and bexc["missing_root"] == "no_raise", "range exceptions: %r" % bexc)
print("RF032_LOSS_DECOMPOSITION_OK payloads=2 trade_models=3 rank1_30m=%.2f entry_matched=2/late=1 avg_entry_delta=0.5 exit_hold_5m=-0.5 diag_stages=6 static_diag_status=NEGATIVE_hardcoded idempotent=yes files=2 outside_write=OSError_blocked exc=%s net_attempts=0 debug=%s" % (r1["avg_return_30m_pct"], json.dumps(bexc, sort_keys=True), __debug__))
