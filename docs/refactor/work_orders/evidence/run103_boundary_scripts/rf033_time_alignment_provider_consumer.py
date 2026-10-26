# RF-033: baseline_btc_woori_tech/vnext/time_alignment.py -- fetch_alignment provider -> capture_alignment / project_alignment / pipeline.build_vnext preopen context.
# Provider boundaries are injected FAKES in sys.modules (`yfinance`, `exchange_calendars`): no real fetch, no network, no installs needed. Frames are fake pandas-like objects.
# The only filesystem writes are the pipeline's own context publish under a tmp reports root (writes outside tmp, network, subprocess, sqlite blocked). No Windows Thread involved.
import os, sys, math, copy, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, types
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
ta = importlib.import_module("libs.reporting.baseline_btc_woori_tech.vnext.time_alignment")
pipe = importlib.import_module("libs.reporting.baseline_btc_woori_tech.vnext.pipeline")
con = importlib.import_module("libs.reporting.baseline_btc_woori_tech.vnext.contract")
sup = importlib.import_module("libs.market.yfinance_support")
tmp = Path(tempfile.mkdtemp(prefix="rf033_talign_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open; _mk = Path.mkdir
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked mkdir")
    return _mk(self, *a, **k)
Path.mkdir = mk
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: " % sys._getframe(1).f_lineno + str(m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
NY = ZoneInfo("America/New_York"); KST = con.KST
# ---- fake exchange_calendars (XNYS): weekdays are sessions except HOLIDAYS; close 16:00 NY (+CLOSE_SHIFT_H hours, to exercise the age buckets)
HOLIDAYS, CLOSE_SHIFT_H, CAL_CALLS = set(), [0], []
class Ts:
    def __init__(self, dt): self.dt = dt
    def timestamp(self): return self.dt.timestamp()
    def to_pydatetime(self): return self.dt
    def date(self): return self.dt.date()
    def __str__(self): return self.dt.date().isoformat()
class Cal:
    def is_session(self, d): CAL_CALLS.append(("is_session", d)); dd = date.fromisoformat(str(d)[:10]); return dd.weekday() < 5 and dd.isoformat() not in HOLIDAYS
    def previous_session(self, d):
        dd = date.fromisoformat(str(d)[:10]) - timedelta(days=1)
        while dd.weekday() > 4 or dd.isoformat() in HOLIDAYS: dd -= timedelta(days=1)
        return Ts(datetime(dd.year, dd.month, dd.day, tzinfo=NY))
    def session_close(self, d):
        dd = date.fromisoformat(str(d)[:10]); return Ts(datetime(dd.year, dd.month, dd.day, 16, tzinfo=NY) + timedelta(hours=CLOSE_SHIFT_H[0]))
xc = types.ModuleType("exchange_calendars"); xc.get_calendar = lambda name: (CAL_CALLS.append(("get_calendar", name)), Cal())[1]
sys.modules["exchange_calendars"] = xc
# ---- fake yfinance
class Idx:
    def __init__(self, dt): self.dt = dt
    def to_pydatetime(self): return self.dt
    def timestamp(self): return self.dt.timestamp() if isinstance(self.dt, datetime) else self.dt
class Frame:
    def __init__(self, items, boom=None): self.items, self.boom = items, boom
    def iterrows(self):
        if self.boom: raise self.boom
        for idx, row in self.items: yield idx, row
class FakeYF(types.ModuleType):
    def __init__(self, frames):
        super().__init__("yfinance"); self.frames, self.calls, self.history_calls = frames, [], []
    def Ticker(self, t):
        self.calls.append(t); outer = self
        class T:
            def history(s, **kw):
                outer.history_calls.append((t, kw)); v = outer.frames[t]
                if isinstance(v, BaseException): raise v
                return v
        return T()
def install(frames):
    fy = FakeYF(frames); sys.modules["yfinance"] = fy; return fy
def ny(day): return Idx(datetime.fromisoformat(day).replace(tzinfo=NY))
def eq_series(pairs): return Frame([(ny(d), {"Close": c}) for d, c in pairs])
DAY = "2026-09-09"   # Wed -> US session 2026-09-08, previous 2026-09-07
def reset(): ta.session_context.cache_clear(); HOLIDAYS.clear(); CLOSE_SHIFT_H[0] = 0
reset()
ctx = ta.session_context(DAY)
check(ctx["status"] == "AVAILABLE" and ctx["session"] == "2026-09-08" and ctx["previous_session"] == "2026-09-07" and ctx["gap_type"] == "OVERNIGHT" and ctx["calendar"].startswith("exchange_calendars:XNYS"), ctx)
check(ctx["us_close_epoch"] > ctx["us_previous_close_epoch"] and 0 < ctx["age_hours"] < 30, ctx)
CE, PE = ctx["us_close_epoch"], ctx["us_previous_close_epoch"]
EQ_OK = {"COIN": {"session": "2026-09-08", "previous_session": "2026-09-07"}, "MSTR": {"session": "2026-09-08", "previous_session": "2026-09-07"}}
def rows(**ov):
    r = {PE: 100.0, CE: 103.0}; r.update(ov); return r
def btc_frame(m, dup=None, extra=True):
    items = [(Idx(t), {"Open": v}) for t, v in m.items() if v != "__omit__"]
    if dup: items.append((Idx(dup), {"Open": 1.0}))
    if extra: items.append((Idx(CE + 300), {"Open": 777.0, "Close": 5.0}))
    return Frame(items)
out = {}
# ---- session_context: lru_cache returns the SAME mutable dict; weekend / Monday / extended-closure / holiday / calendar failure
check(ta.session_context(DAY) is ctx, "cached identity")
m1 = dict(ctx); ctx["poison"] = 1; check("poison" in ta.session_context(DAY), "cache pollution by direct mutation"); ctx.pop("poison")
out["cache_shared_dict"] = "yes"
reset(); check(ta.session_context("2026-09-14")["gap_type"] == "WEEKEND" and ta.session_context("2026-09-14")["session"] == "2026-09-11", "Monday -> Friday, WEEKEND")   # Mon
check(ta.session_context("2026-09-12")["session"] == "2026-09-11" and ta.session_context("2026-09-13")["session"] == "2026-09-11", "Sat/Sun -> Friday")
reset(); CLOSE_SHIFT_H[0] = -40; check(ta.session_context(DAY)["gap_type"] == "EXTENDED_CLOSURE", "age>30h")   # older close -> bucket
reset(); HOLIDAYS.add("2026-09-08"); h = ta.session_context(DAY)
check(h == {"status": "UNKNOWN", "reason": "US_MARKET_HOLIDAY", "expected_session": "2026-09-08"}, h)
out["holiday"] = h["reason"]
reset(); sys.modules["exchange_calendars"] = None
r, e = attempt(ta.session_context, DAY); check(e == "ImportError" or e == "ModuleNotFoundError", e)
out["calendar_missing_exc"] = e
a = ta.capture_alignment(DAY, EQ_OK, []); check(a == {"status": "UNKNOWN", "reason": "calendar_unavailable:" + e}, a)
check("exchange_calendars" in sys.modules and sys.modules["exchange_calendars"] is None, "still blocked")
sys.modules["exchange_calendars"] = xc; reset()
check(attempt(ta.session_context, "bad")[1] == "ValueError" and attempt(ta.session_context, None)[1] == "TypeError", "bad day raises")
check(ta.capture_alignment("bad", EQ_OK, [])["reason"] == "calendar_unavailable:ValueError", "capture swallows bad day")
reset()
# ---- capture_alignment (pure): holiday passthrough, mismatch, exact-boundary open, duplicates, invalid values
HOLIDAYS.add("2026-09-08"); check(ta.capture_alignment(DAY, EQ_OK, []) == h, "holiday context returned"); reset()
RW = lambda m: [{"ts": t, "open": v} for t, v in m.items()]
good = ta.capture_alignment(DAY, EQ_OK, RW(rows()))
check(good["status"] == "AVAILABLE" and good["reason"] == "" and abs(good["btc_equity_interval_return_pct"] - 3.0) < 1e-9 and good["us_close_btc_price"] == 103.0 and good["us_previous_close_btc_price"] == 100.0 and good["source"] == "yfinance:BTC-USD:5m:exact_boundary_open" and good["session"] == "2026-09-08", good)
check(good["us_close_epoch"] == CE, "epochs kept")
for name, eqs in (("session_mismatch", {**EQ_OK, "COIN": {"session": "2026-09-07", "previous_session": "2026-09-04"}}), ("prev_mismatch", {**EQ_OK, "MSTR": {"session": "2026-09-08", "previous_session": "2026-09-03"}}),
                  ("missing_ticker", {"COIN": EQ_OK["COIN"]}), ("unknown_equities", {"status": "UNKNOWN", "reason": "RuntimeError"}), ("none_entry", {"COIN": None, "MSTR": EQ_OK["MSTR"]})):
    r = ta.capture_alignment(DAY, eqs, RW(rows())); check(r["status"] == "UNKNOWN" and r["reason"] == "equity_interval_missing_or_mismatch" and r["session"] == "2026-09-08" and "btc_equity_interval_return_pct" not in r, (name, r))
out["equities_none"] = attempt(ta.capture_alignment, DAY, None, RW(rows()))[1]
def ret(m_rows, **kw):
    r = ta.capture_alignment(DAY, EQ_OK, m_rows); return r
miss = ret(RW({CE: 103.0})); check(miss["status"] == "UNKNOWN" and miss["reason"] == "exact_US_close_BTC_reference_missing" and miss["btc_equity_interval_return_pct"] is None and miss["us_previous_close_btc_price"] is None and miss["us_close_btc_price"] == 103.0 and miss["source"].startswith("yfinance"), miss)
dup = ret(RW(rows()) + [{"ts": CE, "open": 5.0}]); check(dup["status"] == "UNKNOWN" and dup["us_close_btc_price"] is None and dup["us_previous_close_btc_price"] == 100.0, dup)   # duplicate boundary -> not matched
off = ret(RW({PE + 300: 100.0, CE - 300: 103.0})); check(off["status"] == "UNKNOWN" and off["us_close_btc_price"] is None, "near-boundary rows never used")
for name, v in (("zero", 0.0), ("neg", -1.0), ("nan", float("nan")), ("inf", float("inf")), ("str", "abc"), ("none", None)):
    r = ret(RW(rows(**{}) )[:1] + [{"ts": CE, "open": v}]); check(r["status"] == "UNKNOWN" and r["us_close_btc_price"] is None, (name, r))
check(abs(ret([{"ts": PE, "open": "100"}, {"ts": CE, "open": "103.5"}])["btc_equity_interval_return_pct"] - 3.5) < 1e-9, "numeric strings accepted")
check(ret([{"ts": PE, "open": 100}, {"ts": CE, "open": 100}])["btc_equity_interval_return_pct"] == 0.0 and ret([{"ts": PE, "open": 100}, {"ts": CE, "open": 100}])["status"] == "AVAILABLE", "0% return is AVAILABLE")
check(ret([{"ts": str(PE), "open": 100}, {"ts": float(CE), "open": 103}])["status"] == "AVAILABLE" and ret([{"ts": None, "open": 9}, {"open": 9}, {"ts": PE, "open": 100}, {"ts": CE, "open": 101}])["status"] == "AVAILABLE", "ts coerced via int(); None/missing ts -> 0")
out["row_exc"] = {"ts_str_bad": attempt(ta.capture_alignment, DAY, EQ_OK, [{"ts": "x", "open": 1}])[1], "row_none": attempt(ta.capture_alignment, DAY, EQ_OK, [None])[1], "rows_none": attempt(ta.capture_alignment, DAY, EQ_OK, None)[1]}
before = copy.deepcopy(EQ_OK); inrows = RW(rows()); b2 = copy.deepcopy(inrows); ta.capture_alignment(DAY, EQ_OK, inrows); check(EQ_OK == before and inrows == b2, "inputs unchanged")
cached = ta.session_context(DAY); ta.capture_alignment(DAY, EQ_OK, RW(rows())); check(set(cached) == set(ctx) and "status" in cached and cached["status"] == "AVAILABLE" and "btc_equity_interval_return_pct" not in cached, "capture does not mutate cached context")
# ---- project_alignment (pure)
p = ta.project_alignment(good, 106.0); check(abs(p["btc_since_us_close_pct"] - (106 / 103 - 1) * 100) < 1e-9 and p is not good and "btc_since_us_close_pct" not in good, p)
check(ta.project_alignment(None, 5) == {"btc_since_us_close_pct": None} and ta.project_alignment({}, None)["btc_since_us_close_pct"] is None and ta.project_alignment({"us_close_btc_price": 0}, 5)["btc_since_us_close_pct"] is None and abs(ta.project_alignment({"us_close_btc_price": "100"}, "110")["btc_since_us_close_pct"] - 10) < 1e-9, "project edge")
check(ta.project_alignment({"status": "UNKNOWN"}, 1)["status"] == "UNKNOWN", "status kept")
out["project_exc"] = {"list": attempt(ta.project_alignment, [1], 1)[1]}
# ---- fetch_alignment: provider -> result, exact provider calls
reset(); fy = install({"BTC-USD": btc_frame(rows())})
res = ta.fetch_alignment(DAY, EQ_OK)
check(fy.calls == ["BTC-USD"] and fy.history_calls == [("BTC-USD", {"period": "5d", "interval": "5m", "auto_adjust": False, "timeout": 8})], fy.history_calls)
check(res == good and abs(res["btc_equity_interval_return_pct"] - 3.0) < 1e-9, res)    # the trailing +300s row with Close is ignored: only Open at the exact boundary
check(copy.deepcopy(ta.fetch_alignment(DAY, EQ_OK)) == res, "deterministic")
# row with missing/NaN Open -> number()->None, never falls back to Close
fy = install({"BTC-USD": Frame([(Idx(PE), {"Open": 100.0}), (Idx(CE), {"Close": 103.0}), (Idx(CE + 1), {"Open": float("nan")})])})
r = ta.fetch_alignment(DAY, EQ_OK); check(r["status"] == "UNKNOWN" and r["us_close_btc_price"] is None and r["reason"] == "exact_US_close_BTC_reference_missing", r)
out["no_close_fallback"] = "yes"
# empty frame
fy = install({"BTC-USD": Frame([])}); r = ta.fetch_alignment(DAY, EQ_OK); check(r["status"] == "UNKNOWN" and r["reason"] == "exact_US_close_BTC_reference_missing", r)
# holiday: provider still called (calendar checked after fetch), result is the holiday context
HOLIDAYS.add("2026-09-08"); ta.session_context.cache_clear(); fy = install({"BTC-USD": btc_frame(rows())}); r = ta.fetch_alignment(DAY, EQ_OK)
check(r["reason"] == "US_MARKET_HOLIDAY" and fy.calls == ["BTC-USD"], r); HOLIDAYS.clear(); reset()
out["holiday_provider_called"] = "yes"
# equity mismatch: provider still called, UNKNOWN
fy = install({"BTC-USD": btc_frame(rows())}); r = ta.fetch_alignment(DAY, {}); check(r["reason"] == "equity_interval_missing_or_mismatch" and fy.calls == ["BTC-USD"], r)
# provider exception propagation (NOT swallowed by fetch_alignment)
exc = {}
for name, frames in (("history_runtime", {"BTC-USD": RuntimeError("net")}), ("iterrows_value", {"BTC-USD": Frame([], boom=ValueError("bad frame"))}),
                     ("keyerror_ticker", {}), ("index_no_timestamp", {"BTC-USD": Frame([("notidx", {"Open": 1})])}), ("row_not_mapping", {"BTC-USD": Frame([(Idx(PE), 5)])})):
    install(frames); exc[name] = attempt(ta.fetch_alignment, DAY, EQ_OK)[1]
check(exc == {"history_runtime": "RuntimeError", "iterrows_value": "ValueError", "keyerror_ticker": "KeyError", "index_no_timestamp": "AttributeError", "row_not_mapping": "AttributeError"}, exc)
out["fetch_exc"] = exc
install({"BTC-USD": KeyboardInterrupt()})
try: ta.fetch_alignment(DAY, EQ_OK); raise SystemExit("CHECK_FAILED: KeyboardInterrupt swallowed")
except KeyboardInterrupt: pass
# yfinance missing -> DataSourceDependencyError BEFORE any calendar/provider work
reset(); sys.modules["yfinance"] = None; CAL_CALLS.clear()
r, e = attempt(ta.fetch_alignment, "not-a-day", EQ_OK); check(e == "DataSourceDependencyError" and not CAL_CALLS, (e, CAL_CALLS))
out["yf_missing"] = e
# invalid day with yfinance present: provider called, then calendar_unavailable:ValueError (swallowed)
fy = install({"BTC-USD": btc_frame(rows())}); r = ta.fetch_alignment("not-a-day", EQ_OK); check(r == {"status": "UNKNOWN", "reason": "calendar_unavailable:ValueError"} and fy.calls == ["BTC-USD"], r)
# calendar missing with yfinance present
reset(); sys.modules["exchange_calendars"] = None; fy = install({"BTC-USD": btc_frame(rows())}); r = ta.fetch_alignment(DAY, EQ_OK)
check(r["reason"].startswith("calendar_unavailable:") and fy.calls == ["BTC-USD"], r); sys.modules["exchange_calendars"] = xc; reset()
# ---- pipeline.build_vnext consumer: real fetch_equities + fetch_alignment through fake providers; context published immutable; provider re-use guard
NOW = datetime(2026, 9, 9, 8, 30, tzinfo=KST)
def provider_frames(btc=None):
    return {"COIN": eq_series([("2026-09-04", 90), ("2026-09-07", 100), ("2026-09-08", 110)]), "MSTR": eq_series([("2026-09-04", 90), ("2026-09-07", 100), ("2026-09-08", 106)]), "BTC-USD": btc if btc is not None else btc_frame(rows())}
def run(root, now=NOW, frames=None, **kw):
    fy = install(frames or provider_frames()); res = attempt(pipe.build_vnext, day=DAY, reports_root=root, signals={}, candles=[], control_payload={}, cost_pct=0.0, slippage_pct=0.0, allow_fetch=True, now=now, **kw)
    return fy, res
cpath = lambda root: Path(root) / "evaluation/baseline_btc_woori_tech/vnext" / con.VERSION / DAY / "preopen_context.json"
rd = lambda p: json.loads(p.read_text(encoding="utf-8"))
root1 = tmp / "r1"; fy, (v, e) = run(root1)
ctxf = rd(cpath(root1)); al = ctxf["crypto_time_alignment"]
check(fy.calls == ["COIN", "MSTR", "BTC-USD"] and [t for t, _ in fy.history_calls] == ["COIN", "MSTR", "BTC-USD"], fy.calls)
check(ctxf["day"] == DAY and ctxf["version"] == con.VERSION and ctxf["equities"]["COIN"]["status"] == "OBSERVED" and al["status"] == "AVAILABLE" and abs(al["btc_equity_interval_return_pct"] - 3.0) < 1e-9 and al["session"] == "2026-09-08" and ctxf["daily_context"] == {"btc_usd_daily": [], "woori_daily": []}, ctxf)
out["pipeline_post_publish_exc"] = e    # downstream build_features rejects minimal signals; only the context publish is in scope
b1 = cpath(root1).read_bytes(); fy2, _ = run(root1); check(fy2.calls == [] and cpath(root1).read_bytes() == b1, "existing context: provider not called, bytes unchanged")
fy3, _ = run(tmp / "r2", now=datetime(2026, 9, 9, 9, 0, 0, tzinfo=KST)); check(fy3.calls == [] and not cpath(tmp / "r2").exists(), "after 08:59:59 no fetch, no publish")
fy4, _ = run(tmp / "r3", now=datetime(2026, 9, 9, 8, 59, 59, tzinfo=KST)); check(fy4.calls == ["COIN", "MSTR", "BTC-USD"] and cpath(tmp / "r3").exists(), "08:59:59 boundary inclusive")
# BTC provider exception -> alignment UNKNOWN reason=exception name, equities still published
fy5, _ = run(tmp / "r4", frames=provider_frames(RuntimeError("btc down"))); c5 = rd(cpath(tmp / "r4"))
check(c5["crypto_time_alignment"] == {"status": "UNKNOWN", "reason": "RuntimeError"} and c5["equities"]["COIN"]["status"] == "OBSERVED", c5["crypto_time_alignment"])
# yfinance missing -> BOTH equities and alignment published UNKNOWN/DataSourceDependencyError
reset(); sys.modules["yfinance"] = None
v6 = attempt(pipe.build_vnext, day=DAY, reports_root=tmp / "r5", signals={}, candles=[], control_payload={}, cost_pct=0.0, slippage_pct=0.0, allow_fetch=True, now=NOW)
c6 = rd(cpath(tmp / "r5")); check(c6["equities"] == {"status": "UNKNOWN", "reason": "DataSourceDependencyError"} and c6["crypto_time_alignment"] == {"status": "UNKNOWN", "reason": "DataSourceDependencyError"}, c6)
out["pipeline_yf_missing"] = "both_UNKNOWN_DataSourceDependencyError"
# equities UNKNOWN session mismatch (provider returns different sessions) -> alignment UNKNOWN equity_interval_missing_or_mismatch
reset(); fr = provider_frames(); fr["COIN"] = eq_series([("2026-09-03", 90), ("2026-09-04", 100)])
fy7, _ = run(tmp / "r6", frames=fr); c7 = rd(cpath(tmp / "r6")); check(c7["equities"]["COIN"]["status"] == "UNKNOWN" and c7["crypto_time_alignment"]["reason"] == "equity_interval_missing_or_mismatch", c7["crypto_time_alignment"])
# custom alignment_loader / equity_loader injection: fetch_alignment not called
reset(); calls = []
fy8, _ = run(tmp / "r7", equity_loader=lambda d: calls.append(("eq", d)) or EQ_OK, alignment_loader=lambda d, e: calls.append(("al", d)) or {"status": "AVAILABLE", "injected": True}); c8 = rd(cpath(tmp / "r7"))
check(fy8.calls == [] and calls == [("eq", DAY), ("al", DAY)] and c8["crypto_time_alignment"] == {"status": "AVAILABLE", "injected": True}, (fy8.calls, calls))
fy9, _ = run(tmp / "r8", equity_loader=lambda d: EQ_OK); c9 = rd(cpath(tmp / "r8")); check(fy9.calls == [] and c9["crypto_time_alignment"] == {}, c9["crypto_time_alignment"])   # equity_loader w/o alignment_loader -> signals' alignment ({}), no provider
out["loader_injection"] = "yes"
# ---- boundary guards
check(not [b for b in bad if b in ("connect", "cc", "gai", "Popen", "run", "call", "check_call", "check_output", "os.system", "sqlite")], bad)
_, e = attempt(builtins.open, str(Path(tempfile.gettempdir()).parent / "rf033_talign_outside.txt"), "w"); check(e == "OSError" and any(b.startswith("write:") for b in bad), (e, bad))
net = 0
os.chdir(repo); import shutil; shutil.rmtree(tmp, ignore_errors=True)
print("RF033_TIME_ALIGNMENT_OK holiday=%s calendar_missing=%s yf_missing=%s cache_shared_dict=%s no_close_fallback=%s pipeline_yf_missing=%s loader_injection=%s fetch_exc=%d outside_write=OSError net_attempts=%d" % (out["holiday"], out["calendar_missing_exc"], out["yf_missing"], out["cache_shared_dict"], out["no_close_fallback"], out["pipeline_yf_missing"], out["loader_injection"], len(out["fetch_exc"]), net))
