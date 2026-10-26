# RF-033: libs/reporting/baseline_btc_woori_tech/trend_context.py::build_recent_btc_trend_context (+ _source_context/_prior_price)
# first non-effect consumer boundary not covered by earlier RF-033 runs (consumer: data_provider.py:300). Pure synthetic rows,
# all state classifications, boundary thresholds, malformed rows, input immutability. net/sqlite/subprocess/writes blocked.
import os, sys, copy, socket, subprocess, sqlite3, builtins, importlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
from pathlib import Path
import ssl, http.client
tc = importlib.import_module("libs.reporting.baseline_btc_woori_tech.trend_context")
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
Path.write_text = lambda *a, **k: (bad.append("write_text"), (_ for _ in ()).throw(OSError("blocked")))[1]
Path.mkdir = lambda *a, **k: (bad.append("mkdir"), (_ for _ in ()).throw(OSError("blocked")))[1]
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
E = 1_800_000_000
def series(step_pct=0.01, m15=0.05, m15_prior=None, n=26 * 12, m5=0.05, peak_drop=0.0):
    """5-minute rows ending exactly at E; price rises step_pct per row; momentum fields constant (m15 overridden after E-15m)."""
    rows = []
    for i in range(n):
        ts = E - (n - 1 - i) * 300
        price = 1000.0 * (1 + step_pct / 100.0) ** i
        r = {"ts": ts, "price": price, "momentum_5m_pct": m5, "momentum_15m_pct": (m15_prior if (m15_prior is not None and ts <= E - 900) else m15)}
        rows.append(r)
    if peak_drop:   # last row falls peak_drop% below the series high
        rows[-1]["price"] = rows[-2]["price"] * (1 - peak_drop / 100.0)
    return rows
def ctx(payload, m15=1.0, m60=1.0, m24=1.0, epoch=E): return tc.build_recent_btc_trend_context(payload, epoch=epoch, momentum_15m=m15, momentum_60m=m60, momentum_24h=m24)
# 1 persistent uptrend (both sources), constant m15 -> acceleration 0
p = {"sources": {"btc_krw": series(), "btc_usd": series()}}; p0 = copy.deepcopy(p)
c1 = ctx(p); check(p == p0, "payload immutable")
check(c1["schema_version"] == "q12_btc_recent_trend_context.v1" and c1["behavior_effect"] == "observation_only" and c1["available"] and c1["source_count"] == 2, "shape")
check(c1["state"] == "persistent_uptrend" and c1["persistent_uptrend"] is True and c1["accelerating_uptrend"] is False and c1["extended_fading"] is False, "persistent: %r" % c1["state"])
check(c1["positive_5m_ratio_60m"] == 1.0 and c1["alignment_ratio"] == 1.0 and c1["drawdown_from_6h_high_pct"] == 0.0 and c1["momentum_15m_delta_pct"] == 0.0 and c1["momentum_4h_pct"] > 0, "persistent metrics")
check(abs(c1["trend_score"] - (0.40 + 0.30 + 0.15 * 1.0 + 0.15 * 0.5)) < 1e-6, "trend_score formula %r" % c1["trend_score"])
check(sorted(c1["sources"]) == ["btc_krw", "btc_usd"] and c1["sources"]["btc_krw"]["observation_count_60m"] == 13 and c1["sources"]["btc_krw"]["age_sec"] == 0, "per-source context")
# 2 accelerating: m15 jumped by +0.3 vs the value 15 minutes earlier, but 60m momentum < 0.5 so not persistent
p = {"sources": {"btc_krw": series(m15=0.4, m15_prior=0.1)}}
c2 = ctx(p, m15=0.4, m60=0.3, m24=1.0)
check(c2["state"] == "accelerating_uptrend" and c2["accelerating_uptrend"] and not c2["persistent_uptrend"] and abs(c2["momentum_15m_delta_pct"] - 0.3) < 1e-9, "accelerating: %r %r" % (c2["state"], c2["momentum_15m_delta_pct"]))
# 3 extended_fading wins over persistent: 24h >= 3, m15 <= 0, acceleration <= 0
c3 = ctx({"sources": {"btc_krw": series()}}, m15=-0.1, m60=0.8, m24=3.0)
check(c3["state"] == "extended_fading" and c3["extended_fading"] is True and c3["persistent_uptrend"] is False, "extended_fading")
c3b = ctx({"sources": {"btc_krw": series()}}, m15=0.0, m60=0.8, m24=2.99); check(c3b["extended_fading"] is False, "24h boundary 2.99 not fading")
c3c = ctx({"sources": {"btc_krw": series()}}, m15=0.0, m60=0.8, m24=3.0); check(c3c["extended_fading"] is True, "24h boundary 3.0 fading (>=)")
# 4 mixed_or_unconfirmed (sources present but thresholds fail), insufficient_evidence (no usable source)
c4 = ctx({"sources": {"btc_krw": series()}}, m15=-0.5, m60=-0.2, m24=0.0); check(c4["state"] == "mixed_or_unconfirmed" and c4["available"], "mixed")
c5 = ctx({}); check(c5["state"] == "insufficient_evidence" and c5["available"] is False and c5["source_count"] == 0 and c5["sources"] == {} and c5["trend_score"] == 0.4 * 1.0 + 0.0 + 0.0 + 0.0, "insufficient: %r" % c5["trend_score"])
c5b = ctx({"sources": {"btc_krw": "x", "btc_usd": {"a": 1}, "other": series()}}); check(c5b["state"] == "insufficient_evidence", "non-list / non-direct sources ignored")
c5c = tc.build_recent_btc_trend_context({"sources": "x"}, epoch=E, momentum_15m=None, momentum_60m=None, momentum_24h=None)
check(c5c["state"] == "insufficient_evidence" and c5c["alignment_ratio"] is None and c5c["trend_score"] == 0.0, "all-None directions -> alignment None, score 0")
# 5 rows after epoch are excluded (look-ahead guard); empty eligible -> unavailable
fut = [{"ts": E + 60, "price": 5000.0, "momentum_5m_pct": 1.0}]
c6 = ctx({"sources": {"btc_krw": fut}}); check(c6["available"] is False and c6["state"] == "insufficient_evidence", "future-only rows ignored")
base = series(); c7a = ctx({"sources": {"btc_krw": base}}); c7b = ctx({"sources": {"btc_krw": base + fut}})
check(c7a == c7b, "future rows do not change result (no look-ahead)")
# 6 price <= 0 -> unavailable
c8 = ctx({"sources": {"btc_krw": [{"ts": E, "price": 0.0}]}}); check(c8["available"] is False, "non-positive price unavailable")
# 7 drawdown from 6h/24h high and location score
c9 = ctx({"sources": {"btc_krw": series(step_pct=0.05, peak_drop=1.4)}}); dd = c9["drawdown_from_6h_high_pct"]
check(-1.41 < dd < -1.39 and c9["persistent_uptrend"] is True, "drawdown -1.4 still persistent (>= -1.5)")
check(abs(c9["drawdown_from_24h_high_pct"] - dd) < 1e-6, "24h high == 6h high for monotone series")
c9b = ctx({"sources": {"btc_krw": series(step_pct=0.05, peak_drop=1.6)}}); check(c9b["persistent_uptrend"] is False, "drawdown below -1.5 -> not persistent")
# 8 volatility from 5m returns (>=2 values) / None for a single value
vr = series(); [r.__setitem__("momentum_5m_pct", 0.1 if i % 2 else -0.1) for i, r in enumerate(vr)]
c10 = ctx({"sources": {"btc_krw": vr}}); check(c10["realized_5m_volatility_60m"] is not None and c10["positive_5m_ratio_60m"] is not None and 0.0 < c10["positive_5m_ratio_60m"] < 1.0, "volatility/ratio")
c11 = ctx({"sources": {"btc_krw": [{"ts": E, "price": 1000.0, "momentum_5m_pct": 0.2}]}}); check(c11["sources"]["btc_krw"]["realized_5m_volatility_60m"] is None and c11["sources"]["btc_krw"]["momentum_4h_pct"] is None, "single row: vol None, no 4h prior")
# 9 age_sec: latest older than epoch
c12 = ctx({"sources": {"btc_krw": series()}}, epoch=E + 600); check(c12["sources"]["btc_krw"]["age_sec"] == 600, "age_sec")
# 10 exception contract: malformed numeric row field -> ValueError (not fail-soft); non-mapping row -> AttributeError
exc = {}
for name, rows in (("ts_str", [{"ts": "x", "price": 1.0}]), ("row_int", [1]), ("price_str", [{"ts": E, "price": "p"}]), ("mom_str", [{"ts": E, "price": 1.0, "momentum_5m_pct": "m"}])):
    try: ctx({"sources": {"btc_krw": rows}}); exc[name] = "no_raise"
    except Exception as e: exc[name] = type(e).__name__
check(exc == {"ts_str": "ValueError", "row_int": "AttributeError", "price_str": "ValueError", "mom_str": "ValueError"}, "exc contract %r" % exc)
check(not bad, "blocked effects: %r" % bad)
print("RF033_TREND_CONTEXT_OK states=persistent/accelerating/extended_fading/mixed/insufficient score=%.4f lookahead=none exc=%s state_mutation=none write_attempts=0 io=net_sqlite_subprocess_write_blocked debug=%s"
      % (c1["trend_score"], "/".join(f"{k}:{v}" for k, v in sorted(exc.items())), __debug__))
