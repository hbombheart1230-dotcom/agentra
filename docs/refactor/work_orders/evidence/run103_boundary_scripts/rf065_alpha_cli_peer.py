# RF-065 alpha hypothesis competition CLI peer: main() with --no-fetch inside a tmp cwd (relative default roots), no network.
import os, sys, json, socket, subprocess, sqlite3, builtins, tempfile, hashlib, io, contextlib, runpy
from datetime import datetime, timedelta, timezone
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
REPO = os.getcwd(); sys.path.insert(0, REPO)
import ssl, http.client
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf065_alpha_")).resolve()
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
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
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)
from libs.research.post_reclaim_alpha import kiwoom_history as kh
def no_reader(*a, **k): bad.append("KiwoomHistoricalMinuteReader.from_env"); raise OSError("blocked reader")
kh.KiwoomHistoricalMinuteReader.from_env = classmethod(lambda cls, *a, **k: no_reader())
import libs.research.alpha_competition.pipeline as ap
ap.KiwoomHistoricalMinuteReader = kh.KiwoomHistoricalMinuteReader
KST = timezone(timedelta(hours=9))
def epoch(day, hh, mm): return int(datetime.fromisoformat("%sT%02d:%02d:00+09:00" % (day, hh, mm)).timestamp())
day = "2026-06-02"
def cand(sym, hh, mm, **f):
    return {"symbol": sym, "quant_factor_snapshot": {"factors": f}, "entry_lane_observation": {"market_regime_rail": "RISK_OFF"}, "shadow_forward_base": {"baseline_epoch": epoch(day, hh, mm), "baseline_price": 1000.0}}
cands = [cand("005930", 9, 10, breakout_ok=True, volume_ratio=1.5, vwap_distance_pct=0.3, vwap_reclaim_progress=0.99),
         cand("005930", 9, 12, breakout_ok=True, volume_ratio=1.6, vwap_distance_pct=0.4),
         cand("000660", 11, 0, reclaim_ok=True, pullback_ok=True, volume_ratio=0.9),
         {"symbol": "", "shadow_forward_base": {"baseline_epoch": 1, "baseline_price": 1}}, "junk"]
d = tmp / "data/logs/quant_shadow_candidates" / day; d.mkdir(parents=True)
(d / "snap1.json").write_text(json.dumps({"generated_at": day + "T09:20:00+09:00", "candidates": cands}), encoding="utf-8")
(d / "latest.json").write_text(json.dumps({"candidates": cands}), encoding="utf-8")
(d / "broken.json").write_text("{nope", encoding="utf-8")
cache = tmp / "data/research/post_reclaim_alpha/minute_cache"; cache.mkdir(parents=True)
rows = [{"ts": epoch(day, 9, 0) + 60 * i, "open": 1000 + i, "high": 1002 + i, "low": 998 + i, "close": 1001 + i, "volume": 100} for i in range(400)]
(cache / "005930.json").write_text(json.dumps({"schema_version": "kiwoom_historical_minute_cache.v1", "symbol": "005930", "rows": rows}), encoding="utf-8")
def tree(root): return sorted((str(p.relative_to(root)).replace("\\", "/"), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())
inputs_before = tree(tmp)
script = str(Path(REPO) / "scripts/research/run_alpha_hypothesis_competition.py")
def run(argv):
    os.chdir(tmp); sys.argv = [script] + argv
    buf = io.StringIO(); code = 0
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            ns = runpy.run_path(script, run_name="__main__")
    except SystemExit as e: code = e.code if isinstance(e.code, int) else 1
    finally: os.chdir(REPO)
    return code, buf.getvalue()
code, outtxt = run(["--start", day, "--end", day, "--no-fetch", "--max-pages", "0"])
check(code == 0, "main exit %r" % (code,))
res = json.loads(outtxt); check(set(res) == {"json", "markdown"}, "result keys")
check(not Path(res["json"]).is_absolute(), "relative result paths")
jp = tmp / res["json"]; mp = tmp / res["markdown"]
check(inside(jp) and inside(mp) and jp.name == "alpha_hypothesis_competition_v1.json" and jp.parent.name == day + "_" + day, "outputs under tmp cwd reports/")
check(jp.resolve().relative_to(tmp).as_posix().startswith("reports/evaluation/offline_alpha/alpha_hypothesis_competition/"), "default output root relative to cwd")
pay = json.loads(jp.read_text(encoding="utf-8"))
ce = pay["candidate_extraction"]; ps = pay["provider_summary"]
check(ce["raw_candidate_count"] == 4 and ce["canonical_candidate_count"] == 3, "extraction raw/canonical %r" % (ce,))
srcs = {r["symbol"]: r["source"] for r in ps["rows"]}
check(srcs == {"005930": "cache", "000660": "cache_only"} and ps["complete_symbol_count"] == 1, "provider rows %r" % (srcs,))
check([r for r in ps["rows"] if r["symbol"] == "000660"][0]["error"] == "cache_incomplete_and_fetch_disabled", "fetch-disabled reason")
check(set(pay["results"]) == {"H1_OPENING_RISK_OFF_RECLAIM", "H2_CONFIRMED_VOLUME_BREAKOUT", "H3_CONFIRMED_VWAP_PULLBACK"}, "3 hypotheses")
check(mp.read_text(encoding="utf-8").strip() != "", "markdown written")
check([p for p in tree(tmp) if p not in inputs_before and not p[0].startswith("reports/")] == [], "writes only under reports/")
check(len([p for p in tree(tmp) if p not in inputs_before]) == 2, "exactly json+md written")
# rerun deterministic output; no input mutation
code2, out2 = run(["--start", day, "--end", day, "--no-fetch"])
check(code2 == 0 and json.loads(out2) == res, "rerun same paths")
check([p for p in inputs_before if p not in tree(tmp)] == [], "inputs untouched")
# argparse errors
codeb, _ = run(["--bogus"]); codec, _ = run(["--max-pages", "x"])
check(codeb == 2 and codec == 2, "argparse exit 2")
# empty window -> zero candidates still exit 0 with outputs
code3, out3 = run(["--start", "2026-01-01", "--end", "2026-01-02", "--no-fetch"]); r3 = json.loads(out3)
p3 = json.loads((tmp / r3["json"]).read_text(encoding="utf-8"))
check(code3 == 0 and p3["candidate_extraction"]["canonical_candidate_count"] == 0 and p3["provider_summary"]["symbol_count"] == 0, "empty window")
# bad date -> ValueError (not fail-soft)
try: run(["--start", "bad", "--end", day, "--no-fetch"]); be = "no_raise"
except Exception as e: be = type(e).__name__
check([b for b in bad] == [], "blocked attempts: " + repr(bad))
hyp = {k: v.get("episode_count", v.get("episodes")) for k, v in pay["results"].items()}
print("RF065_ALPHA_CLI_PEER_OK main=0 argparse=2/2 raw=4 canonical=3 providers=cache/cache_only empty_window=0 bad_date=%s writes_in_tmp=2 outside_writes=0 fetch=0 debug=%s" % (be, __debug__))
