# RF-028: main_renderer carryover / same-day-summary FORMAL-schema branches (not covered by the 8-branch rich cascade).
# Real facade chain (trade_report_ai.render_trade_summary_markdown -> clean -> markdown_summary -> main_renderer), hand-built formal reports, tmp-only, no network.
import os, sys, copy, re, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
root = Path(tempfile.mkdtemp(prefix="rf028_carry_")); os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "l.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "e.jsonl"); os.chdir(root)
ai = importlib.import_module("libs.reporting.trade_report_ai")
clean = importlib.import_module("libs.reporting.trade_report_markdown_clean")
diag = importlib.import_module("libs.reporting.trade_report.markdown_diagnostics")
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
def report(action="SELL", status="closed", exit_ts="2026-04-20T00:45:00+00:00", hold=None, carry=None, bias=None, pnl=None, pct=None, eval_texts=None):
    r = {"trade_id": "TRD_C", "symbol": "000660", "action": action, "status": status, "story_type": "simulation", "execution_mode_label": "simulation",
         "shared_facts": {"symbol": "000660", "action": action, "status": status, "pnl": pnl, "pnl_pct": pct, "exit_ts": exit_ts},
         "final_operator_conclusion": {"current_action": action}, "reporter_evaluation": {"summary": "", "bullets": eval_texts or []},
         "truth_surface": {"status": {"status": status}, "pnl": {"value": pnl, "pct": pct}, "price": {}}}
    if carry is not None or bias is not None:
        r["shared_facts"]["commander_route"] = {"applied_policy": {"horizon": {"runtime_context": {"carry_state": carry, "carry_risk_bias": bias}}}}
    if hold is not None: r["fact_payload"] = {"trade": {"exit_vs_strategy_intent": {"actual_hold_sec": hold}}}
    return r
out = {}
cc = clean._carryover_context
cases = {
 "explicit_overnight": report(carry="overnight_open", bias="elevated"),
 "same_session": report(hold=1800),
 "crosses_date": report(exit_ts="2026-04-21T00:30:00+00:00", hold=20 * 3600),
 "weekend": report(exit_ts="2026-04-20T00:30:00+00:00", hold=72 * 3600),
 "buy_with_carry": report(action="BUY", carry="overnight_open"),
 "stale": report(carry="multi_session_stale"),
 "unknown_state": report(carry="weird_state", hold=60),
 "empty": {},
 "bad_ts": report(exit_ts="not-a-date", hold=99999),
 "timeline_exit": {**report(hold=20 * 3600), "shared_facts": {"action": "SELL"}, "timeline": [{"event": "entry", "ts": "x"}, {"event": "exit_confirmed", "ts": "2026-04-21T00:30:00+00:00"}]},
}
res = {}
for n, rp in cases.items():
    s = copy.deepcopy(rp); v, e = attempt(cc, rp); check(rp == s, "carryover_context mutated input " + n); check(e is None, "carryover raised %s %s" % (n, e)); res[n] = v
check(res["explicit_overnight"]["is_carryover_exit"] and res["explicit_overnight"]["carry_state"] == "overnight_open", "explicit overnight")
check(not res["same_session"]["is_carryover_exit"], "same-session not carry")
check(res["crosses_date"]["is_carryover_exit"], "date cross")
check(res["weekend"]["is_carryover_exit"] and res["weekend"]["weekend_carry"], "weekend carry")
check(not res["buy_with_carry"]["is_carryover_exit"], "BUY never carryover exit")
check(res["stale"]["is_carryover_exit"], "multi_session_stale")
check(not res["unknown_state"]["is_carryover_exit"], "unknown carry_state ignored")
check(res["empty"]["is_carryover_exit"] is False and res["empty"]["actual_hold_sec"] is None, "empty report")
check(res["bad_ts"]["is_carryover_exit"] is False, "unparseable ts -> not carry (fail-soft)")
check(res["timeline_exit"]["is_carryover_exit"] and res["timeline_exit"]["exit_ts"] == "2026-04-21T00:30:00+00:00", "timeline exit ts fallback")
out["carry"] = {k: (int(v["is_carryover_exit"]), int(v["weekend_carry"])) for k, v in res.items()}
sd = lambda texts, fb="FB", cur=None: diag.same_day_summary_from_texts(texts, fb, cur, deps={"translate_text": lambda x: str(x or "")})
sdc = {}
sdc["ko_full"] = sd(["닫힌 거래 3건, 2승 / 1패, 평균 손익률 1.25%"])
sdc["ratio_avg"] = sd(["closed trade 2 trades, 1 wins 1 loss, avg pnl pct 0.012"])
sdc["unknown"] = sd(["닫힌 거래 4건, 2승 / 1패, 손익 미확정 1건, 평균 0.50%"])
sdc["flat"] = sd(["닫힌 거래 3건, 1승 / 1패, 보합 1건, 평균 0.00%"])
sdc["all_zero_to_unknown"] = sd(["닫힌 거래 2건, 0승 / 0패, 평균 0.00%"])
sdc["cur_win"] = sd(["닫힌 거래 1건, 0승 / 0패, 평균 0.00%"], cur={"classification": 1, "pct_text": "1.50"})
sdc["cur_loss"] = sd(["closed trade 1 trades, 0 wins 0 loss"], cur={"classification": -1, "pct_text": "-0.80"})
sdc["cur_flat"] = sd(["닫힌 거래 1건, 0승 / 0패"], cur={"classification": 0, "pct_text": ""})
sdc["no_win_loss_skip"] = sd(["닫힌 거래 3건 있음", "평균 손익 0.1%"])
sdc["plain_fallback_text"] = sd(["평균 손익 0.1%"])
sdc["nothing"] = sd([])
sdc["blank_texts"] = sd(["", None, "  "])
for k, v in sdc.items(): print("SD", k, "=>", v)
check(sdc["ko_full"] == "3건 중 2승 / 1패 / 평균 1.25%", sdc["ko_full"])
check(sdc["ratio_avg"].endswith("1.20%"), sdc["ratio_avg"])
check("1건 손익 미확정" in sdc["unknown"] and "확인분 평균 0.50%" in sdc["unknown"], sdc["unknown"])
check("1건 보합" in sdc["flat"], sdc["flat"])
check("2건 손익 미확정" in sdc["all_zero_to_unknown"] and "평균" not in sdc["all_zero_to_unknown"], sdc["all_zero_to_unknown"])
check(sdc["cur_win"].startswith("1건 중 1승 / 0패") and "1.50%" in sdc["cur_win"], sdc["cur_win"])
check(sdc["cur_loss"].startswith("1건 중 0승 / 1패") and "-0.80%" in sdc["cur_loss"], sdc["cur_loss"])
check("1건 보합" in sdc["cur_flat"], sdc["cur_flat"])
check(sdc["no_win_loss_skip"] in ("닫힌 거래 3건 있음", "평균 손익 0.1%"), sdc["no_win_loss_skip"])
check(sdc["plain_fallback_text"] == "평균 손익 0.1%" and sdc["nothing"] == "FB" and sdc["blank_texts"] == "FB", "fallbacks")
cr = clean._same_day_current_result
crs = {"open": cr(report(status="open", pnl=5, pct=0.01)), "no_pnl": cr(report()), "win": cr(report(pnl=100, pct=0.012)), "loss_pct_only": cr(report(pnl=None, pct=-0.5)),
       "flat": cr(report(pnl=0, pct=0)), "pct_gt1": cr(report(pnl=10, pct=2.5)), "pnl_wins_over_pct": cr(report(pnl=-1, pct=0.3))}
check(crs["open"] == {} and crs["no_pnl"] == {}, "open/no pnl -> empty")
check(crs["win"] == {"classification": 1, "pct_text": "1.20"} and crs["flat"]["classification"] == 0 and crs["pct_gt1"]["pct_text"] == "2.50", crs)
check(crs["loss_pct_only"]["classification"] == -1 and crs["pnl_wins_over_pct"]["classification"] == -1, crs)
out["cur"] = {k: v.get("classification") for k, v in crs.items()}
rend = {}
for n in ("explicit_overnight", "same_session", "weekend", "buy_with_carry", "crosses_date"):
    rp = cases[n]; s = copy.deepcopy(rp)
    a, ea = attempt(ai.render_trade_summary_markdown, rp); b, eb = attempt(clean.render_trade_summary_markdown_clean, rp)
    check(rp == s and ea is None and eb is None and a == b and isinstance(a, str) and a.strip(), "render chain " + n + str((ea, eb)))
    rend[n] = a
carry_marks = {n: bool(re.search("이월", t)) for n, t in rend.items()}
check(carry_marks["explicit_overnight"] and carry_marks["weekend"] and carry_marks["crosses_date"], "carryover renders note: %s" % carry_marks)
check(not carry_marks["same_session"] and not carry_marks["buy_with_carry"], "non-carry has no note: %s" % carry_marks)
check("오버나이트/주말 이월 포지션 청산" in rend["explicit_overnight"], "selection_reason replaced")
check("오늘 신규 진입 판단이 아니라" in rend["explicit_overnight"], "entry_reason replaced")
rp = report(pnl=100, pct=0.012, eval_texts=["닫힌 거래 3건, 2승 / 1패, 평균 손익률 1.25%"])
t, e = attempt(ai.render_trade_summary_markdown, rp); check(e is None and "3건 중 2승 / 1패 / 평균 1.25%" in t, "same-day summary in rendered output")
rp2 = report(pnl=100, pct=0.012, eval_texts=["닫힌 거래 1건, 0승 / 0패, 평균 0.00%"])
t2, e2 = attempt(ai.render_trade_summary_markdown, rp2); check(e2 is None and "1건 중 1승 / 0패" in t2, "current-result override in rendered output")
rp3 = report(); t3, e3 = attempt(ai.render_trade_summary_markdown, rp3); check(e3 is None and "당일 성과 집계는 리포터 평가 섹션에서 확인 필요" in t3, "fallback in rendered output")
exc = {n: attempt(ai.render_trade_summary_markdown, v)[1] for n, v in {"none": None, "list": [], "str": "x"}.items()}
check(not bad, "blocked attempts %s" % bad)
check(not [p for p in root.rglob("*") if p.is_file()], "files written")
shutil.rmtree(root, ignore_errors=True)
print("RF028_CARRYOVER_SAMEDAY_OK carry=%s same_day=%d current_result=%s render_marks=%s nondict=%s write_attempts=0 debug=%s" % (out["carry"], len(sdc), out["cur"], carry_marks, exc, __debug__))
