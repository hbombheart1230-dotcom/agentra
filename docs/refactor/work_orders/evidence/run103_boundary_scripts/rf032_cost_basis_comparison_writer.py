# RF-032: libs/reporting/evaluation/cost_basis_comparison.py (pure evaluation writer; not covered by run 105/108/118):
# build/render/write_cost_basis_comparison on a fully tmp tree (reports_root, data/logs/quant_shadow_candidates, data/state.json,
# cost profile). start != end => allow_fresh_fetch=False. No UEF, no live, no network, no subprocess.
import os, sys, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
from datetime import datetime, timezone, timedelta
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
repo = os.getcwd(); sys.path.insert(0, repo); sys.dont_write_bytecode = True
import ssl, http.client
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf032_cb_")).resolve()
os.environ["BROKER_COST_PROFILE_PATH"] = str(tmp / "missing_profile.json")
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
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def tree(root): return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())
def exc_of(f, *a, **k):
    try: f(*a, **k); return "no_raise"
    except Exception as e: return type(e).__name__
KST = timezone(timedelta(hours=9))
os.chdir(tmp)
cb = importlib.import_module("libs.reporting.evaluation.cost_basis_comparison")
reports = tmp / "reports"; reports.mkdir()
shadow = tmp / "data" / "logs" / "quant_shadow_candidates"
days = ["2026-06-22", "2026-06-23", "2026-06-24"]
def epoch(day, hh, mm): return int(datetime.strptime(day, "%Y-%m-%d").replace(hour=hh, minute=mm, tzinfo=KST).timestamp())
def rawts(day, hh, mm): return day.replace("-", "") + "%02d%02d00" % (hh, mm)
# 10 pre-strategist candidates per day; rank r drifts +(2.0 - 0.3*r)% by +30m (rank1 best), 2 sources alternate
minute = {}; by_day = {d: [] for d in days}
for di, day in enumerate(days):
    for r in range(1, 11):
        sym = "%06d" % (100000 + r)
        drift = (2.0 - 0.3 * r) / 100.0
        rows = []
        for m in range(0, 50):
            hh, mm = 9 + (10 + m) // 60, (10 + m) % 60
            px = round(10000.0 * (1 + drift * min(m, 30) / 30.0), 4)
            rows.append({"ts": epoch(day, hh, mm), "close": px, "high": px, "low": px, "raw_ts": rawts(day, hh, mm)})
        minute.setdefault(sym, []).extend(rows)
        by_day[day].append({"q9_decision_role": "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "q9_decision_id": "d-" + day, "symbol": sym, "rank": r,
                            "q9_candidate_sources": ["momentum" if r % 2 else "volume"],
                            "shadow_forward_base": {"available": True, "baseline_epoch": epoch(day, 9, 10), "baseline_price": 10000.0, "baseline_raw_ts": rawts(day, 9, 10)}})
for day, cands in by_day.items():
    d = shadow / day; d.mkdir(parents=True)
    extra = [{"q9_decision_role": "OTHER_ROLE", "q9_decision_id": "x", "symbol": "999999", "rank": 1},
             {"q9_decision_role": "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "q9_decision_id": "", "symbol": "888888", "rank": 1},
             {"q9_decision_role": "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "q9_decision_id": "x", "symbol": "777777", "rank": 0}, "not-a-mapping", None, cands[0]]  # last = duplicate of rank-1 (dedupe)
    (d / "a.json").write_text(json.dumps({"generated_at": day + "T09:10:30+09:00", "q9_decision_candidates": cands + extra}), encoding="utf-8")
    (d / "latest.json").write_text(json.dumps({"generated_at": "ignored", "q9_decision_candidates": [{"symbol": "666666"}]}), encoding="utf-8")
    (d / "broken.json").write_text("{nope", encoding="utf-8")
(tmp / "data" / "state.json").write_text(json.dumps({"recent_minute_ohlcv_by_symbol": minute}), encoding="utf-8")
(tmp / "cost.json").write_text(json.dumps({"source": "tmp_profile", "sample_count": 7, "ema_round_trip_cost_pct": 0.004, "conservative_round_trip_cost_pct": 0.009}), encoding="utf-8")
(tmp / "cost_bad.json").write_text("[1,2]", encoding="utf-8")
cost = tmp / "cost.json"
before = tree(tmp)
# ---- build_evaluation_cost_bases (pure)
b0 = cb.build_evaluation_cost_bases(None); b1 = cb.build_evaluation_cost_bases({"source": "p", "sample_count": "3", "ema_round_trip_cost_pct": 0.004}, slippage_pct=0.1)
check(b0["mock_observed"]["round_trip_cost_pct"] == 0.9 and b0["mock_observed"]["source"] == "fallback" and b0["slippage_pct"] == 0.05, "fallback 0.9% / source fallback")
check(abs(b0["live_deployment_equity"]["round_trip_cost_pct"] - 0.23) < 1e-9 and b0["live_deployment_equity"]["buy_fee_pct"] == 0.015 and b0["live_deployment_equity"]["sell_tax_pct"] == 0.2, "live 0.015+0.015+0.2")
check(b1["mock_observed"]["round_trip_cost_pct"] == 0.4 and b1["mock_observed"]["sample_count"] == 3 and abs(b1["mock_observed"]["total_drag_with_slippage_pct"] - 0.5) < 1e-9, "ema fallback chain + slippage 0.1")
check(cb.build_evaluation_cost_bases({"conservative_round_trip_cost_pct": 0.01, "ema_round_trip_cost_pct": 0.002})["mock_observed"]["round_trip_cost_pct"] == 1.0, "conservative preferred over ema")
check(exc_of(cb.build_evaluation_cost_bases, {"conservative_round_trip_cost_pct": "x"}) == "ValueError", "non-numeric cost -> ValueError")
# ---- build
out = cb.build_cost_basis_comparison(reports_root=reports, start=days[0], end=days[-1], cost_profile_path=cost)
check(tree(tmp) == before and not bad, "build wrote nothing / no blocked effect")
check(out["schema_version"] == "q9_cost_basis_comparison.v1" and out["behavior_effect"] == "evaluation_only" and out["interpretation"]["policy_change_authorized"] is False, "schema/effect")
check(out["range"] == {"start": days[0], "end": days[-1]} and out["pre_strategist_universe_available"] is True, "range/universe")
check(out["cost_bases"]["mock_observed"]["source"] == "tmp_profile" and out["cost_bases"]["mock_observed"]["round_trip_cost_pct"] == 0.9, "profile used")
rows = {(r["top_k"], r["horizon"]): r for r in out["rows"]}
check(len(rows) == 16 and [(r["horizon"], r["top_k"]) for r in out["rows"]] == sorted((r["horizon"], r["top_k"]) for r in out["rows"]), "16 rows sorted by (horizon, top_k)")
t1 = rows[(1, "+30m")]
check(t1["window_count"] == 3 and t1["observed_day_count"] == 3, "top1 +30m windows/days")
g1 = float(t1["gross"].get("expectancy_pct", 0))
check(abs(g1 - 1.7) < 0.01, "top1 +30m gross expectancy 1.7 got %r" % g1)
check(abs(t1["mock_net"]["expectancy_pct"] - (1.7 - 0.95)) < 0.01 and abs(t1["live_net"]["expectancy_pct"] - (1.7 - 0.28)) < 0.01, "net = gross - (cost+slippage)")
check(abs(t1["expectancy_delta_live_minus_mock_pct"] - 0.67) < 1e-3, "delta live-mock = 0.67 got %r" % t1["expectancy_delta_live_minus_mock_pct"])
t10 = rows[(10, "+30m")]
check(t10["window_count"] == 3 and t10["gross"]["expectancy_pct"] < t1["gross"]["expectancy_pct"] and t10["mock_net"]["expectancy_pct"] < 0 < t1["mock_net"]["expectancy_pct"], "deeper top-k worse, mock net negative")
check(rows[(1, "EOD")]["window_count"] == 0 and rows[(1, "EOD")]["expectancy_delta_live_minus_mock_pct"] == 0.0, "EOD unobserved -> empty rows, delta 0")
# duplicates/other roles/garbage/latest.json excluded from the 3x10 universe
check(rows[(10, "+5m")]["window_count"] == 3, "+5m windows")
# deterministic / input not mutated
out2 = cb.build_cost_basis_comparison(reports_root=reports, start=days[0], end=days[-1], cost_profile_path=cost)
check(out2 == out and tree(tmp) == before, "deterministic, no writes")
# bad/missing cost profile -> fallback 0.9
for name, path in {"missing": tmp / "nope.json", "list": tmp / "cost_bad.json", "env_default": None}.items():
    o = cb.build_cost_basis_comparison(reports_root=reports, start=days[0], end=days[-1], cost_profile_path=path)
    check(o["cost_bases"]["mock_observed"]["source"] == "fallback" and o["cost_bases"]["mock_observed"]["round_trip_cost_pct"] == 0.9, "profile fallback " + name)
# empty range -> universe unavailable, empty-metric rows
e = cb.build_cost_basis_comparison(reports_root=reports, start="2026-07-01", end="2026-07-02", cost_profile_path=cost)
check(e["pre_strategist_universe_available"] is False and all(r["window_count"] == 0 for r in e["rows"]), "empty range")
# single-day start==end => allow_fresh_fetch=True path reaches the candle reader (blocked sockets), must not escape tmp
single = cb.build_cost_basis_comparison(reports_root=reports, start=days[0], end=days[0], cost_profile_path=cost)
check(single["range"] == {"start": days[0], "end": days[0]} and single["pre_strategist_universe_available"] is True, "single-day builds (state present, no fetch needed)")
# ---- render
md = cb.render_cost_basis_comparison(out)
check(md.startswith("# Cost Basis Comparison (2026-06-22 ~ 2026-06-24)") and "| Mock observed | 0.9000% | 0.0500% | 0.9500% |" in md and "| Live equity assumption | 0.2300% | 0.0500% | 0.2800% |" in md, "render header/cost table")
check("| 1 | +30m | 3/3 |" in md and "+0.6700% |" in md and md.endswith("\n") and "does not authorize a trading-policy change" in md, "render rows/delta/footer")
check(cb.render_cost_basis_comparison({}).count("| Mock observed |") == 1 and "(None ~ None)" in cb.render_cost_basis_comparison({}), "render {} no raise")
check("| 5 | +15m | None/None |" in cb.render_cost_basis_comparison({"rows": [{"top_k": 5, "horizon": "+15m"}]}), "render sparse row")
# ---- write
od = tmp / "out" / "nested"
res = cb.write_cost_basis_comparison(reports_root=reports, start=days[0], end=days[-1], output_dir=od, cost_profile_path=cost)
check(set(res) == {"json", "markdown"} and Path(res["json"]).name == "cost_basis_comparison.json" and Path(res["markdown"]).name == "cost_basis_comparison.md", "write result keys")
check(json.loads(Path(res["json"]).read_text(encoding="utf-8")) == json.loads(json.dumps(out)) and Path(res["json"]).read_text(encoding="utf-8").endswith("}\n"), "json == build payload")
check(Path(res["markdown"]).read_text(encoding="utf-8") == md, "md == render(build)")
snap1 = tree(od)
cb.write_cost_basis_comparison(reports_root=reports, start=days[0], end=days[-1], output_dir=od, cost_profile_path=cost)
check(tree(od) == snap1 and len(snap1) == 2, "idempotent, exactly 2 files")
check(tree(tmp) == sorted(before + [(str(Path("out/nested/cost_basis_comparison.json")), dict(snap1)["cost_basis_comparison.json"]), (str(Path("out/nested/cost_basis_comparison.md")), dict(snap1)["cost_basis_comparison.md"])]) , "only the 2 output files added")
n_blocked = len(bad)
try:
    cb.write_cost_basis_comparison(reports_root=reports, start=days[0], end=days[-1], output_dir=Path(repo) / "SHOULD_NOT_EXIST_rf032", cost_profile_path=cost); outside = "no_raise"
except OSError: outside = "OSError_blocked"
check(outside == "OSError_blocked" and len(bad) == n_blocked + 1 and not (Path(repo) / "SHOULD_NOT_EXIST_rf032").exists(), "outside-tmp output blocked")
excs = {"bad_start": exc_of(cb.build_cost_basis_comparison, reports_root=reports, start="bad", end=days[-1], cost_profile_path=cost),
        "start_none": exc_of(cb.build_cost_basis_comparison, reports_root=reports, start=None, end=days[-1], cost_profile_path=cost),
        "end_before_start": exc_of(cb.build_cost_basis_comparison, reports_root=reports, start=days[-1], end=days[0], cost_profile_path=cost)}
# bad candle state -> reader behavior observed (not asserted beyond classification)
(tmp / "data" / "state.json").write_text("{broken", encoding="utf-8")
excs["broken_state"] = exc_of(cb.build_cost_basis_comparison, reports_root=reports, start=days[0], end=days[-1], cost_profile_path=cost)
# nothing escaped the sandbox other than the single intentional outside write probe
check(not [x for x in bad if x in ("Popen", "run", "call", "check_call", "check_output", "os.system", "sqlite3.connect")], "no subprocess/sqlite")
print("RF032_COST_BASIS_OK rows=16 top1_30m_gross=%.2f mock_net=%.2f live_net=%.2f delta=+0.67 fallback=0.9 live=0.23 empty=NO_WINDOWS idempotent=yes files=2 outside_write=OSError_blocked exc=%s net_attempts=%d debug=%s"
      % (g1, t1["mock_net"]["expectancy_pct"], t1["live_net"]["expectancy_pct"], json.dumps(excs, sort_keys=True, separators=(",", ":")), len([x for x in bad if x in ("connect", "create_connection", "getaddrinfo")]), __debug__))
