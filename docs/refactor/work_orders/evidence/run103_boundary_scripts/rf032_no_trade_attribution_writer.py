# RF-032: evaluation/no_trade_attribution.py build/render + report write (the module has no writer of its own; pipeline._write_json/_write_text emit
# <root>/evaluation/daily/<day>/no_trade_attribution_report.{json,md}, reproduced here json.dumps(indent=2)+"\n"). tmp reports root only.
# Writes outside tmp, network, subprocess, sqlite blocked. Default/operational reports_root never used.
import os, sys, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.no_trade_attribution")
tmp = Path(tempfile.mkdtemp(prefix="rf032_nta_")).resolve(); os.chdir(tmp)
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
def put(p, obj, raw=False, indent=2):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(obj if raw else json.dumps(obj, indent=indent), encoding="utf-8")
root = tmp / "reports"
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}
Q9 = lambda d: root / "operator_summary/daily" / d / "q9_decision_windows.json"
def win(top1, sel, cmd_sel, decision, intent, reason="", detail="", mon_reason=None, obs_reason=None, at="2026-09-01T10:00:00+09:00", rid="live"):
    c = {"selected_symbol": cmd_sel, "decision": decision, "monitor_intent": intent, "reason": reason, "detail": detail}
    if mon_reason is not None: c["monitor_reason"] = mon_reason
    if obs_reason is not None: c["monitor_observation"] = {"reason": obs_reason}
    return {"run_id": rid, "generated_at": at, "scanner_control": {"top1_symbol": top1}, "strategist_selection": {"selected_symbol": sel}, "commander_final": c}
def put_q11(day, report=None, signals=None, virtual=None):
    d = root / "evaluation/opportunity_engine_shadow" / day
    if report is not None: put(d / "opportunity_engine_daily_report.json", report)
    if signals is not None: put(d / "opportunity_engine_signals.json", signals)
    if virtual is not None: put(d / "opportunity_engine_virtual_trades.json", virtual)
out = {}
# --- A: approve+NOOP, positive q11 shadow -> POSSIBLE_OVER_FILTERING (indent=2 streamed windows)
dA = "2026-09-01"
windows = [
    win("005930", "005930", "005930", "approve", "NOOP", "ok", "d" * 200, obs_reason="cooldown"),
    win("005930", "000660", "000660", "approve", "NOOP", "ok", "x", mon_reason="spread", obs_reason="ignored"),
    win("000660", "000660", "000660", "approve", "BUY", "ok"),
    win("005930", "", "", "reject", "", "weak"),
    win("999999x", "005930", "005930", "approve", "NOOP", "ok"),                                   # non-KRX symbol -> synthetic, dropped
    win("005930", "005930", "005930", "approve", "NOOP", "ok", rid="test-run"),                   # synthetic id, dropped
    win("005930", "005930", "005930", "approve", "NOOP", "ok", at="2026-09-01T08:30:00+09:00"),  # pre-open, dropped
    win("005930", "005930", "005930", "approve", "NOOP", "ok", at="2026-09-01T15:31:00+09:00"),  # post-close, dropped
    win("005930", "005930", "005930", "approve", "NOOP", "ok", at="garbage"),                      # unparsable ts kept as regular
    "notadict", None,
]
put(Q9(dA), {"schema": "q9_decision_windows.v1", "windows": windows, "tail": {"x": 1}})
put_q11(dA, report={"win_rate": 0.5}, signals={"signal_count": 7, "signals": [{"opportunity": {"probe_candidate": True}}, {"opportunity": {"probe_candidate": False}}, "x", {"opportunity": "s"}], "data_quality": {"probe_near_miss_count": 2}},
        virtual={"trade_count": 3, "summary": {"win_rate": 0.66, "average_net_return_pct": 0.31, "average_mfe_pct": 0.8, "average_mae_pct": -0.2, "profit_factor": 1.9}})
put(root / "evaluation/baseline_samsung_hynix" / dA / "baseline_samsung_hynix_forward_returns.json",
    {"summary": {"horizons": [{"horizon": "5m", "top1_observation_count": 9, "top1_net": {"win_rate": 0.55, "average_return_pct": 0.1, "profit_factor": 1.2}}, {"horizon": "30m", "trade_count": 4, "win_rate": 0.4, "avg_net_return_pct": -0.2, "profit_factor": 0.8}, "junk"]}})
put(root / "evaluation/baseline_btc_woori_tech" / dA / "baseline_btc_woori_forward_returns.json",
    {"summary": {"horizons": [{"horizon": "1d", "trade_count": 2, "eligible_entries_net": {"win_rate": 0.5, "average_return_pct": 1.5, "profit_factor": 2.0}}, {"horizon": 7, "trade_count": 1, "top1_net": {"win_rate": 1.0, "average_return_pct": 2.0, "profit_factor": 3.0}}]}})
s0 = snap()
pA, e = attempt(mod.build_no_trade_attribution_report, day=dA, reports_root=root, trade_count=0); check(e is None, e)
check(snap() == s0, "build mutated tree")
check(pA["schema_version"] == "no_trade_attribution_report.v1" and pA["behavior_effect"] == "observation_only" and pA["day"] == dA and pA["trade_count"] == 0, pA["schema_version"])
check(pA["q9_window_count"] == 5, pA["q9_window_count"])
check(pA["commander_approve_monitor_noop_count"] == 3 and pA["commander_approve_monitor_buy_count"] == 1, (pA["commander_approve_monitor_noop_count"], pA["commander_approve_monitor_buy_count"]))
check(pA["no_trade_class"] == "POSSIBLE_OVER_FILTERING" and pA["primary_issue"] == "positive_net_shadow_blocked_after_commander_approval", pA["no_trade_class"])
check(pA["shadow_opportunity_status"] == "POSITIVE_NET_SHADOW", pA["shadow_opportunity_status"])
nr = {r["name"]: r["count"] for r in pA["monitor_noop_reasons"]}; check(nr == {"cooldown": 1, "spread": 1}, nr)
check(max(len(r["name"]) for r in pA["commander_details"]) == 160 and {r["name"]: r["count"] for r in pA["commander_decisions"]} == {"approve": 4, "reject": 1}, pA["commander_decisions"])
q11 = pA["q11_opening_opportunity"]; check(q11["available"] and q11["signal_rows"] == 7 and q11["probe_candidates"] == 1 and q11["probe_near_misses"] == 2 and q11["virtual_trades"] == 3 and q11["avg_net_return_pct"] == 0.31 and q11["win_rate"] == 0.66, q11)
h = {r["horizon"]: r for r in pA["q10_samsung_hynix"]["horizons"]}; check(h["5m"]["trade_count"] == 9 and h["5m"]["win_rate"] == 0.55 and h["30m"]["avg_net_return_pct"] == -0.2, h)
g = {r["horizon"]: r for r in pA["q12_btc_woori"]["horizons"]}; check(g["1d"]["profit_factor"] == 2.0 and g["7"]["win_rate"] == 1.0, g)
out["A"] = (pA["no_trade_class"], pA["q9_window_count"], pA["shadow_opportunity_status"], {r["name"]: r["count"] for r in pA["scanner_top1"]})
# same fixture, compact (non-indent) layout -> fallback json.loads path gives identical report
dA2 = "2026-09-02"
put(Q9(dA2), {"schema": "q9_decision_windows.v1", "windows": windows, "tail": {"x": 1}}, indent=None)
for sub in ("opportunity_engine_shadow", "baseline_samsung_hynix", "baseline_btc_woori_tech"):
    src = root / "evaluation" / sub / dA; dst = root / "evaluation" / sub / dA2
    for f in src.iterdir(): put(dst / f.name, json.loads(f.read_text(encoding="utf-8")))
pA2, e = attempt(mod.build_no_trade_attribution_report, day=dA2, reports_root=root, trade_count=0); check(e is None, e)
check({k: v for k, v in pA2.items() if k != "day"} == {k: v for k, v in pA.items() if k != "day"}, "compact layout differs")
# --- B: trade_count>0 -> NOT_NO_TRADE_DAY even with approve+NOOP
pB, e = attempt(mod.build_no_trade_attribution_report, day=dA, reports_root=root, trade_count=2); check(e is None and pB["no_trade_class"] == "NOT_NO_TRADE_DAY" and pB["primary_issue"] == "" and pB["trade_count"] == 2, e)
check(attempt(mod.build_no_trade_attribution_report, day=dA, reports_root=str(root), trade_count=True)[0]["trade_count"] == 1, "bool/str root")
# --- C: classification matrix
def cls(day, wins, q11=None, tc=0, raw=None):
    if raw is not None: Q9(day).parent.mkdir(parents=True, exist_ok=True); Q9(day).write_text(raw, encoding="utf-8")
    elif wins is not None: put(Q9(day), {"windows": wins})
    if q11: put_q11(day, **q11)
    p, e = attempt(mod.build_no_trade_attribution_report, day=day, reports_root=root, trade_count=tc); check(e is None, (day, e)); return p
c = {}
c["missing"] = cls("2026-09-10", None); check((c["missing"]["no_trade_class"], c["missing"]["primary_issue"]) == ("MISSING_Q9_EVIDENCE", "q9_windows_missing"), c["missing"]["no_trade_class"])
c["corrupt"] = cls("2026-09-11", None, raw='{"windows": [ {"a":'); check(c["corrupt"]["no_trade_class"] == "MISSING_Q9_EVIDENCE" and c["corrupt"]["q9_window_count"] == 0, "corrupt windows -> no windows")
c["reject"] = cls("2026-09-12", [win("005930", "005930", "005930", "reject", "")]); check(c["reject"]["no_trade_class"] == "UPSTREAM_REJECTED", c["reject"]["no_trade_class"])
c["none"] = cls("2026-09-13", [win("005930", "005930", "005930", "hold", "")]); check(c["none"]["no_trade_class"] == "NO_ACTIONABLE_CANDIDATE", c["none"]["no_trade_class"])
nz = [win("005930", "005930", "005930", "approve", "NOOP", "ok", mon_reason="m")]
c["fr_noq11"] = cls("2026-09-14", nz); check(c["fr_noq11"]["no_trade_class"] == "FILTERING_REVIEW_REQUIRED" and c["fr_noq11"]["shadow_opportunity_status"] == "UNAVAILABLE", c["fr_noq11"]["no_trade_class"])
c["fr_neg"] = cls("2026-09-15", nz, dict(virtual={"trade_count": 2, "summary": {"average_net_return_pct": -0.1, "average_mfe_pct": 0.4}})); check(c["fr_neg"]["no_trade_class"] == "FILTERING_REVIEW_REQUIRED" and c["fr_neg"]["shadow_opportunity_status"] == "MFE_ONLY_SHADOW", c["fr_neg"]["shadow_opportunity_status"])
c["neg"] = cls("2026-09-16", nz, dict(virtual={"trade_count": 2, "summary": {"average_net_return_pct": -0.1, "average_mfe_pct": 0}})); check(c["neg"]["shadow_opportunity_status"] == "NEGATIVE_SHADOW", c["neg"]["shadow_opportunity_status"])
c["noshadow"] = cls("2026-09-17", nz, dict(report={"x": 1})); check(c["noshadow"]["shadow_opportunity_status"] == "NO_SHADOW_TRADES" and c["noshadow"]["q11_opening_opportunity"]["available"] is True, c["noshadow"]["shadow_opportunity_status"])
c["zero_net"] = cls("2026-09-18", nz, dict(virtual={"trade_count": 2, "summary": {"average_net_return_pct": 0}})); check(c["zero_net"]["no_trade_class"] == "FILTERING_REVIEW_REQUIRED", "net 0 not positive")
out["cls"] = {k: (v["no_trade_class"], v["shadow_opportunity_status"]) for k, v in c.items()}
# --- D: tolerant readers: non-dict / broken auxiliary JSON
put(root / "evaluation/baseline_samsung_hynix/2026-09-19/baseline_samsung_hynix_forward_returns.json", [1, 2])
put(root / "evaluation/baseline_btc_woori_tech/2026-09-19/baseline_btc_woori_forward_returns.json", "{bad", raw=True)
dd = root / "evaluation/opportunity_engine_shadow/2026-09-19"; put(dd / "opportunity_engine_signals.json", {"signal_count": 3, "signals": "notalist"}); put(dd / "opportunity_engine_virtual_trades.json", "{broken", raw=True)
pD = cls("2026-09-19", nz)
check(pD["q10_samsung_hynix"] == {"available": False, "horizons": []} and pD["q12_btc_woori"] == {"available": False, "horizons": []}, "aux")
check(pD["q11_opening_opportunity"]["signal_rows"] == 3 and pD["q11_opening_opportunity"]["probe_candidates"] == 0 and pD["q11_opening_opportunity"]["virtual_trades"] == 0, pD["q11_opening_opportunity"])
dE = root / "evaluation/opportunity_engine_shadow/2026-09-20"; put(dE / "opportunity_engine_virtual_trades.json", {"trade_count": "x"})
out["exc"] = {
    "q11_trade_count_nonint": attempt(mod.build_no_trade_attribution_report, day="2026-09-20", reports_root=root, trade_count=0)[1],
    "trade_count_str": attempt(mod.build_no_trade_attribution_report, day=dA, reports_root=root, trade_count="x")[1],
    "trade_count_none": attempt(mod.build_no_trade_attribution_report, day=dA, reports_root=root, trade_count=None)[1],
    "root_none": attempt(mod.build_no_trade_attribution_report, day=dA, reports_root=None, trade_count=0)[1],
    "missing_kw": attempt(mod.build_no_trade_attribution_report, day=dA)[1],
    "positional": attempt(mod.build_no_trade_attribution_report, dA, root, 0)[1],
    "render_none": attempt(mod.render_no_trade_attribution_report, None)[1],
    "render_empty": attempt(mod.render_no_trade_attribution_report, {})[1],
}
check(out["exc"]["q11_trade_count_nonint"] == "ValueError" and out["exc"]["trade_count_str"] == "TypeError" and out["exc"]["trade_count_none"] == "TypeError", out["exc"])
check(out["exc"]["root_none"] == "TypeError" and out["exc"]["missing_kw"] == "TypeError" and out["exc"]["positional"] == "TypeError", out["exc"])
check(out["exc"]["render_none"] == "AttributeError" and out["exc"]["render_empty"] is None, out["exc"])
pN, e = attempt(mod.build_no_trade_attribution_report, day=dA, reports_root=tmp / "nope", trade_count=0); check(e is None and pN["no_trade_class"] == "MISSING_Q9_EVIDENCE", e)
# --- render
md = mod.render_no_trade_attribution_report(pA); check(md == mod.render_no_trade_attribution_report(copy.deepcopy(pA)), "render nondeterministic")
check(md.startswith("# No-Trade Attribution Report\n") and md.endswith("\n") and "- No-trade class: `POSSIBLE_OVER_FILTERING`" in md and "- `approve`: 4" in md and "### Monitor NOOP Reasons" in md, md[:160])
check("| Q10 Samsung/Hynix | 5m | 9 | 0.55 | 0.1000% | 1.2 |" in md and "| Q12 BTC/Woori | 7 | 1 | 1.0 | 2.0000% | 3.0 |" in md and "- Q11 avg net: 0.3100%" in md, "table rows")
mdE = mod.render_no_trade_attribution_report({}); check("- None" in mdE and "| Q10 Samsung/Hynix | - | 0 | - | - | - |" in mdE and "- Q11 avg net: -" in mdE and "- Q11 win rate: -" in mdE, "empty render")
mdJ = mod.render_no_trade_attribution_report({"commander_decisions": [1, None, {"name": "a", "count": 2}], "q10_samsung_hynix": {"horizons": ["x", {"horizon": "h"}]}, "q11_opening_opportunity": "str"}); check("- `a`: 2" in mdJ and "| Q10 Samsung/Hynix | h | 0 | - | - | - |" in mdJ, "junk render")
# --- write (as pipeline._write_json/_write_text do) and idempotence
daily = root / "evaluation/daily" / dA; jp, mp = daily / "no_trade_attribution_report.json", daily / "no_trade_attribution_report.md"
def write(p):
    jp.parent.mkdir(parents=True, exist_ok=True); jp.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); mp.write_text(mod.render_no_trade_attribution_report(p), encoding="utf-8")
before = snap(); write(pA); b1 = (jp.read_bytes(), mp.read_bytes())
check(json.loads(jp.read_text(encoding="utf-8")) == pA and mp.read_text(encoding="utf-8") == md, "written != built")
pA_again = mod.build_no_trade_attribution_report(day=dA, reports_root=root, trade_count=0); check(pA_again == pA, "rebuild with outputs present differs")
write(pA_again); check((jp.read_bytes(), mp.read_bytes()) == b1, "not idempotent")
after = snap(); check(all(after.get(k) == v for k, v in before.items() if v is not None), "inputs mutated")
ex = attempt(Path("/proc/nonexistent_rf032/x.json").write_text, "x")[1]; out["outside_write"] = ex; check(ex == "OSError", ex)
check(all(b.startswith("write_text:") for b in bad), bad)
print("RF032_NO_TRADE_ATTRIBUTION_OK", "windowsA=%d" % pA["q9_window_count"], "classes=%d" % len({v[0] for v in out["cls"].values()} | {pA["no_trade_class"]}), "compact_eq=yes idempotent=yes files=2", "outside_write=" + out["outside_write"], "net_attempts=0", "debug=" + str(__debug__))
print(json.dumps(out, sort_keys=True))
