# RF-033: baseline_btc_woori_tech/vnext/equities.py -- fetch_equities provider -> consumers (session_return / confirmation / pipeline.build_vnext preopen context).
# The provider boundary is an injected FAKE `yfinance` module placed in sys.modules (no real fetch, no network, no yfinance install needed); frames are fake pandas-like objects.
# The only filesystem writes are the pipeline's own context publish under a tmp reports root (writes outside tmp, network, subprocess, sqlite blocked). No Windows Thread involved.
import os, sys, math, copy, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, types
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
eq = importlib.import_module("libs.reporting.baseline_btc_woori_tech.vnext.equities")
pipe = importlib.import_module("libs.reporting.baseline_btc_woori_tech.vnext.pipeline")
feat = importlib.import_module("libs.reporting.baseline_btc_woori_tech.vnext.features")
sup = importlib.import_module("libs.market.yfinance_support")
tmp = Path(tempfile.mkdtemp(prefix="rf033_feq_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open; _mk = Path.mkdir; _wt = Path.write_text
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
NY = ZoneInfo("America/New_York")
# ---- fake yfinance provider
class Idx:
    def __init__(self, dt): self.dt = dt
    def to_pydatetime(self): return self.dt
class Frame:
    def __init__(self, items, boom=None): self.items, self.boom = items, boom
    def iterrows(self):
        if self.boom: raise self.boom
        for idx, row in self.items: yield idx, row
def ny(day, hour=0): return Idx(datetime.fromisoformat(day).replace(hour=hour, tzinfo=NY))
def series(closes, base="2026-09-"):  # [(day_of_month, close)]
    return Frame([(ny(f"{base}{d:02d}"), {"Close": c}) for d, c in closes])
class FakeYF(types.ModuleType):
    def __init__(self, frames):
        super().__init__("yfinance"); self.frames, self.calls, self.history_calls = frames, [], []
    def Ticker(self, t):
        self.calls.append(t); outer = self
        class T:
            def history(s, **kw):
                outer.history_calls.append((t, kw)); v = outer.frames[t]
                if isinstance(v, BaseException) or (isinstance(v, type) and issubclass(v, BaseException)): raise v
                return v
        if isinstance(self.frames.get("__ticker__"), BaseException): raise self.frames["__ticker__"]
        return T()
def install(frames):
    fy = FakeYF(frames); sys.modules["yfinance"] = fy; return fy
DAY = "2026-09-08"  # Tuesday -> expected US session 2026-09-07 (Mon); previous 2026-09-04 (Fri)
out = {}
# ---- expected_session (pure)
check(eq.expected_session("2026-09-08") == "2026-09-07" and eq.expected_session("2026-09-07") == "2026-09-04" and eq.expected_session("2026-09-06") == "2026-09-04" and eq.expected_session("2026-09-05") == "2026-09-04", "expected_session weekends")
out["expected_exc"] = {"bad": attempt(eq.expected_session, "x")[1], "none": attempt(eq.expected_session, None)[1], "dt": attempt(eq.expected_session, "2026-09-08T10:00")[1]}
# ---- session_return (pure): observed / unknown reasons / dirty rows
R = lambda s, c: {"session": s, "close": c}
ok = eq.session_return([R("2026-09-03", 90), R("2026-09-04", 100), R("2026-09-07", 110), R("2026-09-08", 999)], DAY)  # later-than-expected session ignored
check(ok["status"] == "OBSERVED" and ok["session"] == "2026-09-07" and ok["previous_session"] == "2026-09-04" and abs(ok["return_pct"] - 10.0) < 1e-9 and ok["close"] == 110 and ok["previous_close"] == 100 and "auto_adjust=False" in ok["definition"], ok)
check(eq.session_return([R("2026-09-04", 100), R("2026-09-07", 110)], DAY)["status"] == "OBSERVED", "two rows suffice")
for name, rows, reason in (("empty", [], "holiday_or_missing_expected_session"), ("one", [R("2026-09-07", 1)], "holiday_or_missing_expected_session"),
                           ("missing_expected", [R("2026-09-03", 1), R("2026-09-04", 2)], "holiday_or_missing_expected_session"),
                           ("stale_gap", [R("2026-09-01", 1), R("2026-09-07", 2)], "invalid_previous_session"),  # >4 days
                           ("dup_expected", [R("2026-09-07", 1), R("2026-09-07", 2)], "invalid_previous_session")):
    r = eq.session_return(rows, DAY); check(r["status"] == "UNKNOWN" and r["reason"] == reason and r["expected_session"] == "2026-09-07", (name, r))
check(eq.session_return([R("2026-09-03", 1), R("2026-09-07", 2)], DAY)["status"] == "OBSERVED", "gap of exactly 4 days is allowed")  # 09-03 -> 09-07 = 4
for name, bad_close in (("nan", float("nan")), ("inf", float("inf")), ("zero", 0), ("neg", -5), ("str", "x"), ("none", None)):
    r = eq.session_return([R("2026-09-04", 100), R("2026-09-07", bad_close)], DAY); check(r["status"] == "UNKNOWN", (name, r))  # invalid close row dropped -> expected missing
out["string_close_obs"] = attempt(eq.session_return, [R("2026-09-04", "100"), R("2026-09-07", "110")], DAY)[1]  # validity uses number() but pct() gets the raw str -> TypeError (provider path always yields floats via number())
out["session_return_exc"] = {"missing_session_key": attempt(eq.session_return, [{"close": 1}, R("2026-09-07", 2), R("2026-09-04", 1)], DAY)[1], "none_session": attempt(eq.session_return, [{"session": None, "close": 1}], DAY)[1],
                             "rows_none": attempt(eq.session_return, None, DAY)[1], "bad_day": attempt(eq.session_return, [], "x")[1], "row_not_dict": attempt(eq.session_return, ["x"], DAY)[1]}
# ---- fetch_equities: provider -> result, exact provider calls
fy = install({"COIN": series([(3, 90), (4, 100), (7, 110)]), "MSTR": series([(3, 95), (4, 100), (7, 106)])})
res = eq.fetch_equities(DAY)
check(list(res) == ["COIN", "MSTR"] and fy.calls == ["COIN", "MSTR"], (list(res), fy.calls))
check(all(kw == {"period": "1mo", "interval": "1d", "auto_adjust": False, "prepost": False, "timeout": 8} for _, kw in fy.history_calls) and [t for t, _ in fy.history_calls] == ["COIN", "MSTR"], fy.history_calls)
check(res["COIN"]["status"] == "OBSERVED" and abs(res["COIN"]["return_pct"] - 10.0) < 1e-9 and res["COIN"]["source"] == "yfinance:COIN:1d" and res["MSTR"]["source"] == "yfinance:MSTR:1d" and abs(res["MSTR"]["return_pct"] - 6.0) < 1e-9, res)
check(copy.deepcopy(eq.fetch_equities(DAY)) == res, "deterministic")
# timezone handling: provider index is converted to America/New_York before .date(); a UTC-midnight index lands on the previous NY date
fy = install({"COIN": Frame([(Idx(datetime(2026, 9, 4, tzinfo=timezone.utc)), {"Close": 100}), (Idx(datetime(2026, 9, 7, tzinfo=timezone.utc)), {"Close": 110})]), "MSTR": series([(4, 100), (7, 106)])})
r = eq.fetch_equities(DAY); check(r["COIN"]["status"] == "UNKNOWN" and r["COIN"]["reason"] == "holiday_or_missing_expected_session" and r["COIN"]["source"] == "yfinance:COIN:1d" and r["MSTR"]["status"] == "OBSERVED", r["COIN"])
out["utc_index_obs"] = "UTC-midnight index -> NY previous date -> expected session missing -> UNKNOWN (tz-aware NY index is what yfinance returns)"
# naive datetime index: astimezone() assumes system local tz (observed; not asserted beyond no crash)
fy = install({"COIN": Frame([(Idx(datetime(2026, 9, 4, 12)), {"Close": 100}), (Idx(datetime(2026, 9, 7, 12)), {"Close": 110})]), "MSTR": series([(4, 100), (7, 106)])})
r = eq.fetch_equities(DAY); check(r["COIN"]["status"] in ("OBSERVED", "UNKNOWN") and "source" in r["COIN"], r["COIN"]); out["naive_index"] = r["COIN"]["status"]
# per-ticker isolation: exceptions in Ticker/history/iterrows/row access -> UNKNOWN with type name; the other ticker unaffected
for label, frames, want in (("history_runtime", {"COIN": RuntimeError("down"), "MSTR": series([(4, 100), (7, 106)])}, "RuntimeError"),
                            ("history_timeout", {"COIN": TimeoutError("t"), "MSTR": series([(4, 100), (7, 106)])}, "TimeoutError"),
                            ("iterrows", {"COIN": Frame([], boom=ConnectionError("c")), "MSTR": series([(4, 100), (7, 106)])}, "ConnectionError"),
                            ("no_close_col", {"COIN": Frame([(ny("2026-09-07"), {"Open": 1})]), "MSTR": series([(4, 100), (7, 106)])}, "KeyError"),
                            ("bad_idx", {"COIN": Frame([("notidx", {"Close": 1})]), "MSTR": series([(4, 100), (7, 106)])}, "AttributeError")):
    fy = install(frames); r = eq.fetch_equities(DAY)
    check(r["COIN"] == {"status": "UNKNOWN", "reason": want} and r["MSTR"]["status"] == "OBSERVED" and "source" not in r["COIN"], (label, r["COIN"]))
fy = install({"COIN": series([]), "MSTR": series([(4, 100), (7, 106)])}); check(eq.fetch_equities(DAY)["COIN"]["reason"] == "holiday_or_missing_expected_session", "empty frame")
fy = install({"COIN": series([(4, float("nan")), (7, float("nan"))]), "MSTR": series([(4, 100), (7, 106)])}); check(eq.fetch_equities(DAY)["COIN"]["status"] == "UNKNOWN", "NaN closes -> dropped -> UNKNOWN")
fy = install({"__ticker__": ValueError("bad ticker"), "COIN": None, "MSTR": None}); r = eq.fetch_equities(DAY); check(r["COIN"] == {"status": "UNKNOWN", "reason": "ValueError"} and r["MSTR"] == r["COIN"], "Ticker() raising is caught per ticker")
fy = install({"COIN": series([(4, 100), (7, 110)]), "MSTR": KeyboardInterrupt}); _, e = attempt(lambda: None)
try: eq.fetch_equities(DAY); kb = "no_raise"
except KeyboardInterrupt: kb = "KeyboardInterrupt"
check(kb == "KeyboardInterrupt", kb); out["base_exception"] = kb  # BaseException is not swallowed
fy = install({"COIN": series([(4, 100), (7, 110)]), "MSTR": series([(4, 100), (7, 106)])})
r = eq.fetch_equities("2026-09-06"); check(r["COIN"]["status"] == "UNKNOWN" and r["COIN"]["source"] == "yfinance:COIN:1d", "Sunday day -> expected Friday 09-04 -> only prior rows")  # 09-07 row is > expected, filtered
r = eq.fetch_equities("x"); check(r["COIN"] == {"status": "UNKNOWN", "reason": "ValueError"}, r["COIN"]); out["bad_day"] = "per-ticker UNKNOWN ValueError (no raise)"
# dependency handling: yfinance not importable -> explicit DataSourceDependencyError (NOT swallowed, no per-ticker UNKNOWN)
sys.modules["yfinance"] = None
_, e = attempt(eq.fetch_equities, DAY); check(e == "DataSourceDependencyError", e)
try: eq.fetch_equities(DAY)
except sup.DataSourceDependencyError as ex: check(ex.reason == "dependency_missing:yfinance" and ex.package == "yfinance", ex.reason)
out["dependency_missing"] = e
_, e2 = attempt(eq.fetch_equities, "x"); check(e2 == "DataSourceDependencyError", "dependency error precedes day validation")
# ---- consumer 1: confirmation(equities, btc_return)
fy = install({"COIN": series([(4, 100), (7, 110)]), "MSTR": series([(4, 100), (7, 106)])}); live = eq.fetch_equities(DAY)
C = eq.confirmation
check(C(live, 2.0) == "STRONG" and C(live, -2.0) == "DIVERGENCE", "both |ret|>=5 aligned/opposed")
fy = install({"COIN": series([(4, 100), (7, 110)]), "MSTR": series([(4, 100), (7, 102)])}); l2 = eq.fetch_equities(DAY)
check(C(l2, 1.0) == "CONFIRM" and C(l2, -1.0) == "DIVERGENCE", "aligned but one <5 -> CONFIRM")
fy = install({"COIN": series([(4, 100), (7, 110)]), "MSTR": series([(4, 100), (7, 95)])}); l3 = eq.fetch_equities(DAY)
check(C(l3, 1.0) == "MIXED" and C(l3, -1.0) == "MIXED", "split direction -> MIXED")
check(C(live, None) == "UNKNOWN" and C(live, 0) == "UNKNOWN" and C({}, 1.0) == "UNKNOWN" and C({"COIN": live["COIN"]}, 1.0) == "UNKNOWN", "UNKNOWN guards")
fy = install({"COIN": RuntimeError("x"), "MSTR": series([(4, 100), (7, 106)])}); check(C(eq.fetch_equities(DAY), 2.0) == "UNKNOWN", "one ticker UNKNOWN -> confirmation UNKNOWN")
check(C({"COIN": {"status": "OBSERVED", "return_pct": 5.0}, "MSTR": {"status": "OBSERVED", "return_pct": 5.0}}, 1.0) == "STRONG" and C({"COIN": {"status": "OBSERVED", "return_pct": 0.0}, "MSTR": {"status": "OBSERVED", "return_pct": 6.0}}, 1.0) == "MIXED", "boundary |5| inclusive; zero return is neither aligned nor opposed")
out["confirmation_exc"] = {"equities_none": attempt(C, None, 1.0)[1], "btc_str": attempt(C, live, "x")[1]}
# ---- consumer 2: pipeline.build_vnext publishes the provider result in the immutable preopen context (equity_loader=None -> fetch_equities)
fy = install({"COIN": series([(4, 100), (7, 110)]), "MSTR": series([(4, 100), (7, 106)])})
now = datetime(2026, 9, 8, 8, 50, tzinfo=pipe.KST); root = tmp / "reports"
align = lambda day, equities: {"status": "UNKNOWN", "reason": "fake_alignment", "seen_equities": sorted(equities)}
def run_pipe(now, root, **kw):
    try: return pipe.build_vnext(day=DAY, reports_root=root, signals={"research_context": {"btc_usd_daily": [{"ts": 1}] * 3, "woori_daily": [{"ts": 1}] * 12}}, candles=[], control_payload={}, cost_pct=0.1, slippage_pct=0.1, allow_fetch=True, now=now, alignment_loader=align, **kw), None
    except Exception as ex: return None, type(ex).__name__
res_p, perr = run_pipe(now, root)  # later stages (build_features) may reject the minimal signals -- we only need the published context
ctxp = root / "evaluation/baseline_btc_woori_tech/vnext" / pipe.VERSION / DAY / "preopen_context.json"
check(ctxp.is_file(), ("context not published", res_p, perr)); ctx = json.loads(ctxp.read_text(encoding="utf-8"))
check(ctx["equities"]["COIN"]["status"] == "OBSERVED" and ctx["equities"]["MSTR"]["source"] == "yfinance:MSTR:1d" and ctx["crypto_time_alignment"]["seen_equities"] == ["COIN", "MSTR"] and ctx["day"] == DAY and ctx["version"] == pipe.VERSION, ctx)
check(len(ctx["daily_context"]["btc_usd_daily"]) == 3 and len(ctx["daily_context"]["woori_daily"]) == 10, "bounded lookback")
before = ctxp.read_bytes(); n_calls = len(fy.calls)
fy2 = install({"COIN": RuntimeError("must not refetch"), "MSTR": RuntimeError("must not refetch")})
res_p2, perr2 = run_pipe(now, root); check(ctxp.read_bytes() == before and fy2.calls == [], "existing context is never replaced and the provider is not called again (immutable)")
out["pipeline_after_context"] = perr or "ok"
# dependency missing inside the pipeline is converted to {'status':'UNKNOWN','reason':'DataSourceDependencyError'} (equities-level, not per ticker)
sys.modules["yfinance"] = None; root2 = tmp / "reports2"; res_d, perr_d = run_pipe(now, root2)
ctx2 = json.loads((root2 / "evaluation/baseline_btc_woori_tech/vnext" / pipe.VERSION / DAY / "preopen_context.json").read_text(encoding="utf-8"))
check(ctx2["equities"] == {"status": "UNKNOWN", "reason": "DataSourceDependencyError"}, ctx2["equities"]); out["pipeline_dependency_missing"] = ctx2["equities"]
# after 08:59:59 or allow_fetch=False the provider is never consulted
fy3 = install({"COIN": series([(4, 100), (7, 110)]), "MSTR": series([(4, 100), (7, 106)])}); root3 = tmp / "reports3"
late = datetime(2026, 9, 8, 9, 0, 0, tzinfo=pipe.KST); run_pipe(late, root3)
check(fy3.calls == [] and not (root3 / "evaluation/baseline_btc_woori_tech/vnext" / pipe.VERSION / DAY / "preopen_context.json").exists(), "late: no fetch, no context")
net = [b for b in bad if not b.startswith(("write:", "mkdir:"))]; check(not net and not [b for b in bad if b.startswith(("write:", "mkdir:"))], bad)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=str))
print("RF033_FETCH_EQUITIES_OK tickers=2 provider_kwargs=exact tz=NY isolation=per_ticker dependency_missing=%s confirmation=STRONG/CONFIRM/DIVERGENCE/MIXED/UNKNOWN pipeline_ctx_immutable=yes net_attempts=%d outside_writes=0 debug=%s"
      % (out["dependency_missing"], len(net), __debug__))
