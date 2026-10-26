# RF-033 baseline_btc_woori_tech/hypothesis_features.py (pure): look-ahead guards, capture states, daily context, gap bands, local confirmation, pullback.
import os, sys, json, copy, importlib
from datetime import datetime, timedelta, timezone
repo = os.getcwd(); sys.path.insert(0, repo)
hf = importlib.import_module("libs.reporting.baseline_btc_woori_tech.hypothesis_features")
KST = timezone(timedelta(hours=9))
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
D = "2026-04-08"
def ep(h, m, day=D): return int(datetime.fromisoformat(f"{day}T{h:02d}:{m:02d}:00+09:00").timestamp())
T = ep(8, 55)
out = {}
def run(name, f, *a, **k):
    try: out[name] = json.dumps(f(*a, **k), sort_keys=True, default=repr)
    except Exception as e: out[name] = "EXC:" + type(e).__name__
# ---- btc_0855
row = lambda ts, mom, price=60000.0, **kw: {"ts": ts, "momentum_24h_pct": mom, "price": price, "raw_ts": str(ts), **kw}
for name, payload in {
    "missing_status": {"btc_0855_capture_status": "missing", "btc_0855_capture_reason": "r"},
    "missed_default_reason": {"btc_0855_capture_status": "MISSED"},
    "observed_two_sources": {"sources": {"btc_krw": [row(T - 60, 4.0)], "btc_usd": [row(T - 120, 6.0)]}},
    "stale_over_300s": {"sources": {"btc_krw": [row(T - 301, 4.0)]}},
    "boundary_300s": {"sources": {"btc_krw": [row(T - 300, 4.0)]}},
    "lookahead_future_row_ignored": {"sources": {"btc_krw": [row(T + 60, 9.0), row(T - 30, 1.0)]}},
    "momentum_non_numeric": {"sources": {"btc_krw": [row(T - 60, "x")], "btc_usd": [row(T - 60, 3.5)]}},
    "close_used_when_no_price": {"sources": {"btc_usd": [{"ts": T - 10, "momentum_24h_pct": 5.0, "close": 100.0}]}},
    "captured_sources_override": {"btc_0855_capture_status": "CAPTURED", "btc_0855_captured_sources": {"btc_usd": [row(T - 5, 7.5)]}, "sources": {"btc_usd": [row(T - 5, 1.0)]}},
    "captured_but_empty_override": {"btc_0855_capture_status": "CAPTURED", "btc_0855_captured_sources": {}, "sources": {"btc_usd": [row(T - 5, 2.0)]}},
    "sources_not_mapping": {"sources": ["x"]},
    "empty": {},
}.items(): run("btc|" + name, hf._btc_0855, payload, day=D)
b = json.loads(out["btc|observed_two_sources"]); check(b["status"] == "OBSERVED" and b["return_24h_pct"] == 5.0 and b["thresholds"]["gte_5pct"] and not b["thresholds"]["gte_7pct"], "avg + thresholds")
check(json.loads(out["btc|stale_over_300s"])["status"] == "MISSING" and json.loads(out["btc|boundary_300s"])["status"] == "OBSERVED", "300s staleness boundary")
check(json.loads(out["btc|lookahead_future_row_ignored"])["return_24h_pct"] == 1.0, "future rows ignored")
check(json.loads(out["btc|captured_sources_override"])["return_24h_pct"] == 7.5, "captured override")
# ---- daily context
def daily(n, start_close=100.0, step=0.0, high_bump=1.0, day=D, gap_days=0):
    rows = []
    for i in range(n):
        ts = T - 24 * 3600 - (n - i) * 86400 + 3600 * 5 - 86400 * gap_days  # closed >=24h before target
        c = start_close + i * step
        rows.append({"ts": ts, "close": c, "high": c + high_bump})
    return rows
def ctx(rows, btc_ret=4.0, price=500.0):
    b0855 = {"target_epoch": T, "return_24h_pct": btc_ret, "observations": [{"source": "btc_usd", "price": price}] if price is not None else []}
    return hf._daily_context({"research_context": {"btc_usd_daily": rows}}, btc_0855=b0855)
cases = {"first_surge_ath": ctx(daily(25, 100, 0.0), 4.0, 500.0), "no_surge": ctx(daily(25, 100, 0.0), 1.0, 50.0), "missing_lt20": ctx(daily(19), 4.0), "missing_price": ctx(daily(25), 4.0, None),
         "repeated_surge": ctx(daily(25, 100, 0.0)[:-3] + [{"ts": T - 24 * 3600 - 2 * 86400, "close": 100.0, "high": 101}, {"ts": T - 24 * 3600 - 86400, "close": 104.0, "high": 105}, {"ts": T - 24 * 3600 - 7200, "close": 104.5, "high": 105}], 4.0, 500.0),
         "breakout_20d_only": ctx(daily(25, 100, 1.0, 1.0)[:5] + [dict(r, high=1000.0) for r in daily(25, 100, 1.0, 1.0)[5:6]] + daily(25, 100, 1.0, 1.0)[6:], 4.0, 200.0),
         "no_breakout": ctx(daily(25, 100, 0.0, 1.0), 1.0, 90.0), "recent_row_excluded": ctx(daily(19) + [{"ts": T - 3600, "close": 1000.0, "high": 1000.0}], 4.0)}
for k, v in cases.items(): out["daily|" + k] = json.dumps(v, sort_keys=True)
check(cases["missing_lt20"]["status"] == "MISSING" and cases["recent_row_excluded"]["closed_daily_count"] == 19, "daily lookahead window (row within 24h excluded)")
check(cases["first_surge_ath"]["surge_state"] == "FIRST_SURGE" and cases["first_surge_ath"]["breakout_state"] == "ATH_BREAKOUT", "first surge + ATH")
check(cases["no_surge"]["surge_state"] == "NO_STRONG_SURGE" and cases["no_breakout"]["breakout_state"] == "NO_BREAKOUT", "no surge / no breakout")
check(cases["repeated_surge"]["surge_state"] == "REPEATED_SURGE", "repeated surge")
# ---- woori previous close + gap bands
tdate = datetime.strptime(D, "%Y-%m-%d").date()
wrows = [{"ts": ep(15, 30, "2026-04-06"), "close": 10.0}, {"ts": ep(15, 30, "2026-04-07"), "close": 11.0}, {"ts": ep(9, 0, D), "close": 99.0}, {"ts": 0, "close": 5.0}, {"ts": ep(15, 30, "2026-04-07") + 10, "close": 0.0}]
out["woori_prev"] = [hf._woori_previous_close({"research_context": {"woori_daily": wrows}}, day=D), hf._woori_previous_close({}, day=D), hf._woori_previous_close({"research_context": {"woori_daily": "x"}}, day=D)]
check(out["woori_prev"][0] == 11.0, "previous close strictly before target day, ignores zero close")
out["gap_bands"] = [hf._gap_band(v) for v in (None, -0.01, 0.0, 2.99, 3.0, 4.99, 5.0, 9.99, 10.0, 25.0)]
check(out["gap_bands"] == ["MISSING", "NEGATIVE", "0_TO_3", "0_TO_3", "3_TO_5", "3_TO_5", "5_TO_10", "5_TO_10", "GTE_10", "GTE_10"], "gap band boundaries")
# ---- local snapshot
def candles(start_min=0, n=8, vol=(100, 100, 100, 100, 300), base=100.0):
    rows = []
    for i in range(n):
        ts = ep(9, 0) + 60 * i; c = base + i * 0.1
        rows.append({"ts": ts, "open": c, "high": c + 0.2, "low": c - 0.2, "close": c, "volume": vol[i % len(vol)]})
    return rows
cs = candles()
for label, minute in (("09:00", 0), ("09:03", 3), ("09:05", 5), ("09:10", 10)): run("local|" + label, hf._local_snapshot, cs, day=D, hour=9, minute=minute)
run("local|no_entry_candle", hf._local_snapshot, cs[:2], day=D, hour=9, minute=5)
run("local|entry_price_missing", hf._local_snapshot, [{"ts": ep(9, 0), "open": None, "close": None}], day=D, hour=9, minute=0)
run("local|vol_not_confirm_price_confirms", hf._local_snapshot, candles(vol=(100, 100, 100, 100, 100)), day=D, hour=9, minute=5)
flat = [{"ts": ep(9, 0) + 60 * i, "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0 if i < 5 else 99.0, "volume": 100} for i in range(6)]
run("local|no_confirmation", hf._local_snapshot, flat, day=D, hour=9, minute=5)
run("local|zero_prior_volume", hf._local_snapshot, [{"ts": ep(9, 0) + 60 * i, "open": 100, "close": 100, "volume": 0} for i in range(6)], day=D, hour=9, minute=5)
l0 = json.loads(out["local|09:00"]); check(l0["reason"] == "opening_auction_entry_has_no_local_confirmation" and l0["local_confirmation"] is None, "09:00 has no local confirmation")
l5 = json.loads(out["local|09:05"]); check(l5["confirmation_cutoff_epoch"] == ep(9, 5) - 60, "cutoff = entry-60s")
# ---- pullback
def pb(vwap_touch=True, late_next=False):
    rows = [{"ts": ep(9, 0) + 60 * i, "open": 100.0, "high": 101.0, "low": 99.5, "close": 100.5, "volume": 100} for i in range(5)]
    rows.append({"ts": ep(9, 5), "open": 100.5, "high": 101.0, "low": 99.0 if vwap_touch else 100.4, "close": 100.6, "volume": 100})
    rows.append({"ts": ep(9, 6), "open": 100.7, "high": 101.0, "low": 100.5, "close": 100.8, "volume": 100})
    return rows
run("pullback|trigger", hf._pullback_snapshot, pb(), day=D); run("pullback|no_touch", hf._pullback_snapshot, pb(False), day=D)
run("pullback|last_row_no_next", hf._pullback_snapshot, pb()[:6], day=D); run("pullback|zero_volume", hf._pullback_snapshot, [dict(r, volume=0) for r in pb()], day=D)
check(json.loads(out["pullback|trigger"])["status"] == "OBSERVED" and json.loads(out["pullback|trigger"])["entry_epoch"] == ep(9, 6), "pullback entry at next minute")
check(json.loads(out["pullback|last_row_no_next"])["status"] == "MISSING", "pullback needs next minute")
# ---- full build + immutability + malformed
sig = {"sources": {"btc_krw": [row(T - 60, 4.0)], "btc_usd": [row(T - 60, 4.0, price=500.0)]}, "research_context": {"btc_usd_daily": daily(25, 100, 0.0), "woori_daily": wrows}}
cs_full = candles(); before = copy.deepcopy((cs_full, sig))
feat = hf.build_hypothesis_features(day=D, candles=cs_full, btc_signals=sig); check((cs_full, sig) == before, "inputs mutated")
out["full_keys"] = sorted(feat); out["full_entries"] = sorted(feat["entry_methods"]); out["full_gap"] = feat["woori_opening"]; out["full_ctx"] = {k: feat["btc_daily_context"].get(k) for k in ("status", "surge_state", "breakout_state")}
check(feat["woori_opening"]["opening_gap_pct"] is not None and feat["btc_0855"]["status"] == "OBSERVED", "full build observed")
run("full|empty_inputs", hf.build_hypothesis_features, day=D, candles=[], btc_signals={})
run("full|bad_day", hf.build_hypothesis_features, day="2026/04/08", candles=[], btc_signals={})
run("full|candles_none", hf.build_hypothesis_features, day=D, candles=None, btc_signals={})
run("full|ts_str", hf.build_hypothesis_features, day=D, candles=[{"ts": "abc"}], btc_signals={})
run("full|signals_none", hf.build_hypothesis_features, day=D, candles=[], btc_signals=None)
check(out["full|bad_day"].startswith("EXC:ValueError") and out["full|candles_none"].startswith("EXC:TypeError") and out["full|ts_str"].startswith("EXC:ValueError"), "malformed exceptions")
print("RF033_HYPOTHESIS_FEATURES_OK btc=%d daily=%d local=%d pullback=%d gap_bands=10 malformed=5 mutation=none debug=%s" % (sum(k.startswith("btc|") for k in out), sum(k.startswith("daily|") for k in out), sum(k.startswith("local|") for k in out), sum(k.startswith("pullback|") for k in out), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
