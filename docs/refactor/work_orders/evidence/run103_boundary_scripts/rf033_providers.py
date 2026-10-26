# Offline provider-boundary checks for RF-033 (network/yfinance providers replaced by in-process fakes).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, io, urllib.request
from datetime import datetime, timedelta, timezone
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
import ssl, http.client  # import before blocking (ssl subclassing)
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
from pathlib import Path
Path.write_text = lambda *a, **k: (bad.append("write_text"), (_ for _ in ()).throw(OSError("blocked")))[1]
Path.mkdir = lambda *a, **k: (bad.append("mkdir"), (_ for _ in ()).throw(OSError("blocked")))[1]
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)
out = {}
# ---- crypto_fear_greed via fake urlopen
fg = importlib.import_module("libs.reporting.baseline_btc_woori_tech.crypto_fear_greed")
class Resp:
    def __init__(self, body): self.body = body
    def read(self): return self.body
    def __enter__(self): return self
    def __exit__(self, *a): return False
calls = []
def mk_urlopen(payload=None, exc=None, raw=None):
    def u(request, timeout=None):
        calls.append((request.full_url, request.get_header("User-agent"), timeout))
        if exc: raise exc
        return Resp(raw if raw is not None else json.dumps(payload).encode("utf-8"))
    return u
def ts(day, hh=0): return int(datetime.fromisoformat(day + f"T{hh:02d}:00:00+09:00").timestamp())
rows = [{"value": "20", "value_classification": "Extreme Fear", "timestamp": str(ts("2026-04-08", 9)), "time_until_update": "100"}, {"value": "60", "value_classification": "", "timestamp": str(ts("2026-04-07", 9))}]
cases = {"exact": {"data": rows}, "latest_used": {"data": rows[1:]}, "empty": {"data": []}, "nodata": {"x": 1}, "notmap": [1, 2], "badrows": {"data": ["x", {"value": "abc", "timestamp": "zz"}]}, "thresholds": {"data": [{"value": str(v), "value_classification": "", "timestamp": str(ts("2026-04-08", 1))} for v in (0,)]}}
for name, payload in cases.items():
    fg.urlopen = mk_urlopen(payload); out["fg|" + name] = fg.load_crypto_fear_greed_index(day="2026-04-08")
for name, exc in (("timeout", TimeoutError("t")), ("oserr", OSError("o"))):
    fg.urlopen = mk_urlopen(exc=exc); out["fg|" + name] = fg.load_crypto_fear_greed_index(day="2026-04-08")
fg.urlopen = mk_urlopen(raw=b"not json"); out["fg|badjson"] = fg.load_crypto_fear_greed_index(day="2026-04-08", timeout_sec=1.5)
out["fg|regimes"] = [fg._regime(v) for v in (None, 0, 24, 25, 44, 45, 55, 56, 74, 75, 100)] + [fg._regime(50, "Extreme Greed")]
out["fg|urlopen_calls"] = [list(c) for c in calls][:3] + [len(calls)]
check(out["fg|exact"]["value"] == 20 and out["fg|exact"]["regime"] == "extreme_fear", "exact day row")
check(out["fg|latest_used"]["fallback_reason"] == "exact_day_not_found_latest_used", "latest fallback")
check(out["fg|timeout"]["fallback_reason"] == "crypto_fear_greed_fetch_failed:TimeoutError", "timeout fallback")
check(calls[0][0].startswith("https://api.alternative.me/") and calls[0][1] == "TradingAgentSystem/1.0", "request shape")
# ---- data_provider with fake yfinance
dp = importlib.import_module("libs.reporting.baseline_btc_woori_tech.data_provider")
out["dp|leading"] = [dp.evaluate_multihorizon_leading_signal(momentum_5m=a, momentum_15m=b, momentum_60m=c, momentum_24h=d) for a in (None, 0.2, -0.2, 0.0) for b in (None, 0.1, -0.1) for c in (None, 1.0, 0.3, 0.0, -0.3, -1.0) for d in (None, 3.0, -3.0, 0.0)]
class Row(dict):
    pass
class Frame:
    def __init__(self, items, empty=False): self.items = items; self.empty = empty
    def iterrows(self):
        for idx, r in self.items: yield idx, Row(r)
class FakeYF:
    def __init__(self, frames, raise_for=()): self.frames = frames; self.raise_for = raise_for
    def Ticker(self, t):
        outer = self
        class T:
            def history(self_, period=None, interval=None):
                if t in outer.raise_for: raise RuntimeError("boom")
                return outer.frames.get(t)
        return T()
KST = timezone(timedelta(hours=9))
def dt(day, hh, mm, tz=KST): return datetime.fromisoformat(f"{day}T{hh:02d}:{mm:02d}:00").replace(tzinfo=tz)
def minute_items(day, start_hh, n, base, step=0.5, tz=KST):
    return [(dt(day, start_hh, 0, tz) + timedelta(minutes=i), {"Close": base + i * step, "Open": base, "High": base + 1, "Low": base - 1, "Volume": 10}) for i in range(n)]
items = minute_items("2026-04-08", 9, 80, 100.0) + [(dt("2026-04-08", 9, 0), {"Close": 99.0}), (dt("2026-04-01", 9, 0), {"Close": 50.0}), (datetime(2026, 4, 8, 0, 30), {"Close": 7.0, "Open": 0, "High": 0, "Low": 0, "Volume": None}), (12345, {"Close": 5.0}), (dt("2026-04-08", 9, 1), {"Close": 0.0})]
dp.require_yfinance = lambda: FakeYF({"X": Frame(items), "E": Frame([], empty=True), "N": None})
rows_x = dp._yf_rows("X", day="2026-04-08"); out["dp|yf_n"] = len(rows_x); out["dp|yf_first_last"] = [rows_x[0], rows_x[-1]]
out["dp|yf_unrestricted"] = len(dp._yf_rows("X", day="2026-04-08", restrict_to_recent_days=False))
out["dp|yf_empty"] = [dp._yf_rows("E", day="2026-04-08"), dp._yf_rows("N", day="2026-04-08")]
dp.require_yfinance = lambda: FakeYF({"X": Frame(items)}, raise_for=("X",)); out["dp|yf_history_raises"] = dp._yf_rows("X", day="2026-04-08")
class BadFrame:
    empty = False
    def iterrows(self): raise ValueError("bad")
dp.require_yfinance = lambda: FakeYF({"X": BadFrame()}); out["dp|yf_iter_raises"] = dp._yf_rows("X", day="2026-04-08")
def dep_missing(): raise dp.DataSourceDependencyError("yfinance", "yfinance_missing") if False else dp.DataSourceDependencyError.__new__(dp.DataSourceDependencyError)
try:
    from libs.market.yfinance_support import DataSourceDependencyError as DSE
    import inspect
    sig = str(inspect.signature(DSE.__init__))
except Exception as e:
    DSE = None; sig = "n/a"
out["dp|dse_sig"] = sig
mom = dp._momentum_rows(rows_x, source="t"); out["dp|mom_n"] = len(mom); out["dp|mom_samples"] = [mom[0], mom[len(mom) // 2], mom[-1]]
out["dp|mom_short"] = dp._momentum_rows(rows_x[:5], source="t")
payload = {"sources": {"btc_usd": mom, "coinbase_proxy": mom[:10]}}
for off in (-1000, 0, 60, 120 * 60, 24 * 3600 * 2):
    e = (rows_x[-1]["ts"] + off) if off != -1000 else rows_x[0]["ts"]
    s = dp.signal_at(payload, epoch=e); s.pop("recent_trend", None); out[f"dp|signal|{off}"] = s
out["dp|signal_empty"] = {k: v for k, v in dp.signal_at({}, epoch=1).items() if k != "recent_trend"}
# load_btc_signal_rows with fake yf + fake capture merge
pit = importlib.import_module("libs.reporting.baseline_btc_woori_tech.point_in_time_capture")
pit.merge_capture_into_signal_payload = lambda payload, day: {**payload, "available_sources": [k for k, v in payload["sources"].items() if v], "btc_0855_capture_reused": False, "btc_0855_capture_status": "fake", "btc_0855_capture_reason": ""}
def fx_items(): return minute_items("2026-04-08", 9, 80, 1300.0, 0.1)
dp._DAILY_RESEARCH_CACHE.clear()
dp.require_yfinance = lambda: FakeYF({"BTC-USD": Frame(minute_items("2026-04-08", 9, 80, 60000.0, 10)), "COIN": Frame(minute_items("2026-04-08", 9, 80, 200.0)), "KRW=X": Frame(fx_items()), TARGET if (TARGET := dp.TARGET_TICKER) else "": Frame(minute_items("2026-04-08", 9, 3, 10.0))})
res = dp.load_btc_signal_rows(day="2026-04-08", include_research_context=True)
out["dp|load_keys"] = sorted(res); out["dp|load_avail"] = [res["available"], res["available_sources"], res["fallback_reason"], res["data_source_error"], {k: len(v) for k, v in res["sources"].items()}, len(res["research_context"]["btc_usd_daily"]), len(res["research_context"]["woori_daily"])]
dp._DAILY_RESEARCH_CACHE.clear()
res2 = dp.load_btc_signal_rows(day="2026-04-08", include_research_context=False); out["dp|load_noresearch"] = [res2["research_context_requested"], res2["research_context"]["btc_usd_daily"]]
if DSE is not None:
    def raiser():
        try: raise DSE("yfinance_missing") 
        except TypeError: raise DSE("yfinance", "yfinance_missing")
    dp.require_yfinance = raiser; dp._DAILY_RESEARCH_CACHE.clear()
    try:
        r3 = dp.load_btc_signal_rows(day="2026-04-08"); out["dp|load_dep_missing"] = [r3["available"], r3["fallback_reason"], r3["data_source_error"], r3["research_context"]["btc_usd_daily"]]
    except Exception as e: out["dp|load_dep_missing"] = "EXC:" + type(e).__name__
out["blocked_attempts"] = bad
check(not bad, "no blocked attempts: %r" % bad)
print("RF033_PROVIDERS_OK fg=%d dp=%d debug=%s" % (sum(k.startswith("fg|") for k in out), sum(k.startswith("dp|") for k in out), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
