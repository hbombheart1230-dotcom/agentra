# RF-033 baseline_btc_woori_tech/input_delivery.py + hypothesis_forward.py + input_worker.InputWorker.tick (tmp-only, no network).
import os, sys, json, copy, importlib, tempfile, threading, time
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo); sys.dont_write_bytecode = True
pkg = "libs.reporting.baseline_btc_woori_tech"
idl = importlib.import_module(pkg + ".input_delivery")
hf = importlib.import_module(pkg + ".hypothesis_forward")
iw = importlib.import_module(pkg + ".input_worker")
ct = importlib.import_module(pkg + ".vnext.contract")
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def exc_of(f, *a, **k):
    try: f(*a, **k); return "no_raise"
    except Exception as e: return type(e).__name__
D = "2026-04-08"; ep = lambda hm: ct.epoch(D, hm)
T855, T900, T912 = ep("08:55"), ep("09:00"), ep("09:12")
tmp = Path(tempfile.mkdtemp(prefix="rf033_idl_")); rr = tmp / "reports"; cap = tmp / "capture"
# ---- hypothesis_forward (pure)
def c(ts, o, h, l, cl): return {"ts": ts, "open": o, "high": h, "low": l, "close": cl}
entry = ep("09:05")
candles = [c(entry + 60 * m, 100 + m, 101 + m, 99, 100 + m) for m in range(0, 70)] + [c(ep("15:30"), 110, 112, 108, 111)]
orig = copy.deepcopy(candles)
em = {"A": {"status": "OBSERVED", "entry_epoch": entry, "entry_price": 100.0},
      "B": {"status": "MISSING", "reason": "nope"}, "C": "notmap", "D": {"status": "OBSERVED", "entry_epoch": 0, "entry_price": 100.0}}
emc = copy.deepcopy(em)
r = hf.entry_forward_outcomes(em, candles=list(reversed(candles)), drag_pct=0.5)
check(candles == orig and em == emc, "inputs immutable")
a = r["A"]["returns"]
check(a["+5m"]["status"] == "OBSERVED" and abs(a["+5m"]["gross_return_pct"] - 5.0) < 1e-9 and abs(a["+5m"]["net_return_pct"] - 4.5) < 1e-9, "5m return+drag")
check(a["+60m"]["status"] == "OBSERVED" and a["EOD"]["status"] == "OBSERVED" and a["EOD"]["observed_price"] == 111.0, "60m/EOD observed")
check(r["B"] == {"status": "MISSING", "reason": "nope", "returns": {}} and r["C"]["reason"] == "entry_observation_missing" and r["D"]["status"] == "MISSING", "missing paths")
r2 = hf.entry_forward_outcomes(em, candles=candles[:3], drag_pct=0.0)
check(r2["A"]["returns"]["+60m"] == {"status": "PENDING"} and r2["A"]["returns"]["EOD"] == {"status": "PENDING"}, "pending when no data")
r3 = hf.entry_forward_outcomes({"A": em["A"]}, candles=candles[:-1], drag_pct=0.0)
check(r3["A"]["returns"]["EOD"] == {"status": "PENDING"}, "EOD pending before 15:30")
s = hf.summarize_outcomes([{"net_return_pct": 1.0, "mfe_pct": 2.0, "mae_pct": -1.0}, {"net_return_pct": -0.5, "mfe_pct": 1.0, "mae_pct": -2.0}, {"net_return_pct": "x"}])
check(s["sample_count"] == 2 and s["avg_mfe_pct"] == 1.5 and s["avg_mae_pct"] == -1.5, "summarize")
check(hf.summarize_outcomes([])["avg_mfe_pct"] is None, "summarize empty")
hexc = {"candles_none": exc_of(hf.entry_forward_outcomes, em, candles=None, drag_pct=0),
        "bad_ts": exc_of(hf.entry_forward_outcomes, em, candles=[{"ts": "x"}], drag_pct=0),
        "entries_none": exc_of(hf.entry_forward_outcomes, None, candles=[], drag_pct=0)}
# ---- publish_input
sig = {"sources": {}, "btc_0855_capture_status": "MISSED"}
rows = [c(T900 - 60, 1, 1, 1, 1), c(T900, 100, 101, 99, 100), c(T900 + 60, 100, 102, 99, 101), c(ep("15:30") + 60, 1, 1, 1, 1), c(T900 + 600, 1, 1, 1, 1)]
now = T900 + 120
sigc = copy.deepcopy(sig); rowsc = copy.deepcopy(rows)
p = idl.publish_input(day=D, reports_root=rr, signals=sig, candles=rows, now_epoch=now)
check(sig == sigc and rows == rowsc, "publish inputs immutable")
f = idl.input_path(rr, D)
check(f.name == "q12_candidate_input.json" and f.parent.name == D and f.exists(), "path")
check(json.loads(f.read_text(encoding="utf-8")) == json.loads(json.dumps(p, default=str)), "disk==returned")
check(p["schema_version"] == idl.SCHEMA and p["delivery_owner"] == "q12_input_worker" and p["btc_capture_status"] == "MISSED" and p["generated_at"].endswith("+09:00"), "payload fields")
check(p["candle_latest_epoch"] == T900 + 60 and p["generated_epoch"] == now, "rows filtered to 09:00..min(now,15:30)")
check(not [x for x in rr.rglob("*") if x.name.startswith(".q12-")], "no temp leftovers")
pe = {"candles_none": exc_of(idl.publish_input, day=D, reports_root=rr, signals={}, candles=None, now_epoch=now),
      "signals_none": exc_of(idl.publish_input, day=D, reports_root=rr, signals=None, candles=[], now_epoch=now),
      "bad_day": exc_of(idl.publish_input, day="bad", reports_root=rr, signals={}, candles=[], now_epoch=now)}
# ---- load_candidate_input
def load(now_e, legacy=None, root=cap): return idl.load_candidate_input(reports_root=rr, day=D, now_epoch=now_e, legacy=legacy, capture_root=root)
idl.publish_input(day=D, reports_root=rr, signals=sig, candles=rows, now_epoch=T900 + 120)
cur = load(T900 + 150); check(cur["delivery_status"] == "CURRENT" and "btc_delivery_source" not in cur, "CURRENT <=90s")
check(load(T900 + 120 + 90)["delivery_status"] == "CURRENT" and load(T900 + 120 + 91)["delivery_status"] == "INPUT_DELAY", "90s boundary")
st = load(T900 + 120 + 91); check(st["delivery_reason"] == "q12_candidate_input_stale" and st["features"]["entry_methods"] == {}, "stale clears entry_methods")
wc = load(T912 + 1000); check(wc["delivery_status"] == "WINDOW_CLOSED" and wc["delivery_reason"] == "q12_opening_candidate_window_closed", "window closed after 09:12")
future = load(T900 + 60)
check(future["delivery_status"] == "INPUT_DELAY" and future["delivery_reason"] == "q12_candidate_input_invalid" and future["features"] == {}, "future generated -> invalid")
f.write_text("{not json", encoding="utf-8")
check(load(T900 + 150)["delivery_reason"] == "q12_candidate_input_invalid", "corrupt json -> invalid")
for name, body in {"schema": {"schema_version": "old", "day": D, "generated_epoch": 1},
                   "day": {"schema_version": idl.SCHEMA, "day": "2026-04-07", "generated_epoch": 1},
                   "epoch": {"schema_version": idl.SCHEMA, "day": D, "generated_epoch": "abc"}}.items():
    f.write_text(json.dumps(body), encoding="utf-8")
    check(load(T900 + 150)["delivery_reason"] == "q12_candidate_input_invalid", "invalid " + name)
f.unlink()
leg = {"k": {"n": [1]}}; legc = copy.deepcopy(leg)
no = load(T900 + 150, legacy=leg)
check(no == leg and no is not leg and no["k"] is not leg["k"] and leg == legc, "no file -> deepcopy of legacy")
check(load(T900 + 150) == {}, "no file/no legacy -> {}")
cp = idl.capture_paths(D, root=cap)["snapshot"]; cp.parent.mkdir(parents=True)
mrow = lambda ts, mom: {"ts": ts, "momentum_24h_pct": mom, "price": 60000.0}
snap = {"day": D, "target_epoch": T855, "capture_status": "CAPTURED", "sources": {"btc_krw": [mrow(T855 - 30, 4.5)]}}
cp.write_text(json.dumps(snap), encoding="utf-8")
cb = load(T900)
check(cb["features"]["btc_0855"]["status"] == "OBSERVED" and cb["features"]["btc_0855"]["return_24h_pct"] == 4.5 and cb["btc_delivery_source"] == str(cp), "capture -> btc_0855 observed")
check(load(T855 - 1)["features"]["btc_0855"] == {"status": "MISSING", "reason": "btc_0855_capture_invalid"}, "now<08:55 -> invalid capture")
for name, s2 in {"day": {**snap, "day": "2026-04-07"}, "target": {**snap, "target_epoch": T855 + 60}}.items():
    cp.write_text(json.dumps(s2), encoding="utf-8")
    check(load(T900)["features"]["btc_0855"]["reason"] == "btc_0855_capture_invalid", "capture mismatch " + name)
cp.write_text(json.dumps({**snap, "capture_status": "MISSED"}), encoding="utf-8")
check(load(T900)["features"]["btc_0855"]["status"] == "MISSING", "non-CAPTURED snapshot -> MISSING")
cp.write_text("garbage", encoding="utf-8")
garbage = load(T900)["features"]["btc_0855"]; check(garbage["status"] == "MISSING", "garbage capture tolerated")
cp.write_text(json.dumps(snap), encoding="utf-8")
idl.publish_input(day=D, reports_root=rr, signals=sig, candles=rows, now_epoch=T900 + 120)
both = load(T900 + 150)
check(both["delivery_status"] == "CURRENT" and "entry_methods" in both["features"] and both["features"]["btc_0855"]["status"] == "OBSERVED", "file + capture merged")
# ---- merge_fresh_btc_into_preserved_report
ex = {"features": {"keep": 1, "btc_0855": {"status": "MISSING"}}}; exc_ = copy.deepcopy(ex)
sigs = {"btc_0855_capture_status": "CAPTURED", "sources": {"btc_usd": [mrow(T855 - 10, 6.0)]}, "btc_0855_captured_sources": {"btc_usd": [mrow(T855 - 10, 6.0)]}}
m = idl.merge_fresh_btc_into_preserved_report(ex, sigs, D)
check(ex == exc_ and m["features"]["keep"] == 1 and m["features"]["btc_0855"]["status"] == "OBSERVED" and m["btc_delivery_source"] == "canonical_0855_capture", "merge fresh btc")
m2 = idl.merge_fresh_btc_into_preserved_report(ex, {"btc_0855_capture_status": "MISSED"}, D); check(m2 == ex and m2 is not ex, "not captured -> copy unchanged")
m3 = idl.merge_fresh_btc_into_preserved_report({}, {"btc_0855_capture_status": "CAPTURED", "sources": {}}, D); check(m3 == {}, "captured but unobserved -> unchanged")
merge_exc = exc_of(idl.merge_fresh_btc_into_preserved_report, None, sigs, D)
# ---- InputWorker.tick (fake loaders; no network)
calls = {"btc": 0, "candles": []}
orig_mod = (iw.load_btc_signal_rows, iw.load_woori_candles, iw.merge_capture_into_signal_payload)
research_ok = {"btc_usd_daily": [{"ts": T855 - 86400 * 3, "close": 60000.0}], "woori_daily": [{"ts": T855 - 86400 * 3, "close": 100.0}]}
def fake_btc(day): calls["btc"] += 1; return {"research_context": research_ok}
def fake_candles(**k): calls["candles"].append(k); return rows
iw.load_btc_signal_rows, iw.load_woori_candles = fake_btc, fake_candles
iw.merge_capture_into_signal_payload = lambda payload, day: idl.merge_capture_into_signal_payload(payload, day=day, root=cap)
w = iw.InputWorker(D, rr, "state.json")
out1 = w.tick(T900 + 120)
check(calls["btc"] == 1 and w.research == research_ok and calls["candles"] == [{"day": D, "state_path": "state.json", "allow_fresh_fetch": True}], "tick fetches research+candles")
check(out1["btc_capture_status"] == "CAPTURED" and out1["features"]["btc_0855"]["status"] == "OBSERVED" and out1["candle_latest_epoch"] == T900 + 60, "tick payload")
w.tick(T900 + 130); check(calls["btc"] == 1, "research cached after success")
w2 = iw.InputWorker(D, rr, "s"); calls["candles"].clear(); w2.tick(T900 - 60)
check(calls["candles"] == [], "before 09:00 no candle load")
cp.write_text(json.dumps({**snap, "capture_status": "MISSED"}), encoding="utf-8"); w2.tick(T900 + 120)
check(calls["candles"] == [], "capture not CAPTURED -> no candle load")
iw.load_btc_signal_rows = lambda day: {"research_context": {"btc_usd_daily": research_ok["btc_usd_daily"]}}
w3 = iw.InputWorker(D, rr, "s"); w3.tick(T900 + 120); check(w3.research is None, "incomplete research -> None")
def boom(day): raise RuntimeError("net")
iw.load_btc_signal_rows = boom; w4 = iw.InputWorker(D, rr, "s"); w4.tick(T900 + 120); check(w4.research is None, "research exception swallowed")
cp.write_text(json.dumps(snap), encoding="utf-8")
def candles_boom(**k): raise OSError("candles")
iw.load_woori_candles = candles_boom
tick_exc = exc_of(iw.InputWorker(D, rr, "s").tick, T900 + 120)
iw.load_btc_signal_rows, iw.load_woori_candles, iw.merge_capture_into_signal_payload = orig_mod
stop = iw.start_input_worker(day="2000-01-01", reports_root=rr, state_path="s"); time.sleep(0.3)
check(not [t for t in threading.enumerate() if t.name == "q12-opening-input"], "wrong-day loop exits"); stop.set()
dirty = os.popen("git status --porcelain --untracked-files=all").read().replace("\\", "/")
check(all("rf033_input_delivery_peer.py" in l for l in dirty.splitlines()), "repo clean except harness: " + dirty[:200])
exc = {**{"fwd_" + k: v for k, v in hexc.items()}, **{"pub_" + k: v for k, v in pe.items()}, "merge_existing_none": merge_exc, "tick_candles_oserror": tick_exc}
print("RF033_INPUT_DELIVERY_OK forward=5m/60m/EOD/pending/missing publish=filter/schema/atomic stale=90s window=09:12 capture=observed/invalid worker=tick/cache/gates",
      "exc=" + json.dumps(exc, sort_keys=True), "debug=" + str(__debug__), "state_mutation=none outside_write=0")
