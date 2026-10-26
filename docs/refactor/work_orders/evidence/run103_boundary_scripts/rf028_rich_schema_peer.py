# RF-028: FORMAL rich report -> renderer chain. The report is produced by the real producer (trade_report_ai.build_deterministic_trade_report)
# from a rich story_input that uses the formal key names (cf. tests/test_trade_report_ai.py), then rendered through every facade layer.
import os, sys, json, copy, re, shutil, socket, subprocess, sqlite3, builtins, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
root = Path("/tmp/rf028_rich_fixed"); shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "events.jsonl"); os.chdir(root)
import ssl, http.client
mod = importlib.import_module("libs.reporting.trade_report_ai")
mclean = importlib.import_module("libs.reporting.trade_report_markdown_clean")
msum = importlib.import_module("libs.reporting.trade_report.markdown_summary")
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
def norm(s): return re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(\+00:00|Z)?", "TS", s)
def rich_story():
    return {
        "trade_id": "TRD_20260420_000660_01", "story_id": "TRD_20260420_000660_01", "run_id": "run-7", "day": "2026-04-20", "symbol": "000660",
        "action": "SELL", "status": "closed", "story_type": "simulation", "execution_mode_label": "real broker",
        "strategist_candidate_hints": ["122630", "000660"], "strategist_market_headlines": ["KOSPI opens higher as chip demand expectations improve."],
        "strategist_symbol_headlines": ["000660 rises on renewed AI memory optimism."],
        "strategist_evidence_trace": {"candidate_hints": ["000660"], "market_headlines": ["US futures steady."], "global_sentiment_signal": {"score": 0.12, "status": "ok"}, "fear_index": {"vix_level": 18.4}, "key_events": ["AI demand re-rating"]},
        "scanner_selection_trace": {"ranked_candidates": [{"rank": 1, "symbol": "034020", "score_total": 1.7}, {"rank": 2, "symbol": "000660", "score_total": 1.61}], "selected_symbol": "000660", "selected_rank": 2,
                                    "monitor_fallback_used": True, "scanner_top_pick_symbol": "034020", "monitor_fallback_reason": "breakout not ready", "selection_reason": "top_value + sector_theme"},
        "monitor_stop_policy_trace": {"hard_stop_pct": 0.03, "adaptive_stop_loss_pct": 0.0092, "effective_stop_loss_pct": 0.0092, "trailing_stop_pct": 0.012, "take_profit_pct": 0.025},
        "monitor_blocker_trace": {"entry_check_summary": "mission=wait | reason=reclaim_not_confirmed", "entry_blockers": ["volume_ok"], "threshold_shortfalls": ["volume ratio 0.10 below min 0.75"]},
        "scanner_reason_human": {"selected_symbol": "000660", "selected_rank": 2, "selected_score": 1.61, "playbook": "pullback", "policy_source": "strategist", "top_candidates": [{"rank": 1, "symbol": "034020", "score_total": 1.7}, {"rank": 2, "symbol": "000660", "score_total": 1.61}]},
        "monitor_reason_human": {"summary": "Monitor confirmed exit on trailing stop.", "posture": "SELL", "current_price": 70050.0, "price_source": "state.minute_ohlcv_by_symbol.close", "entry_condition_scores": {"confidence_score": 0.7, "confidence_threshold": 0.55}},
        "entry_summary": {"reason_human": "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation", "price": 70000, "qty": 3, "ts": "2026-04-20T00:05:00+00:00"},
        "holding_summary": {"summary": "held 40 minutes", "max_unrealized_pnl_pct": 0.012},
        "exit_summary": {"reason_human": "trailing stop hit", "price": 70100, "qty": 3, "ts": "2026-04-20T00:45:00+00:00"},
        "exit_execution_details": {"filled_price": 70100.0, "broker_truth_source": "kiwoom.order_status", "broker_realized_pnl": -320.0, "broker_realized_pnl_pct": -0.0064, "broker_fee": 14, "broker_tax": 9,
                                   "pnl_truth_source": "kiwoom.ka10077", "broker_day_truth_source": "kiwoom.ka10077", "broker_day_match_mode": "symbol_price_qty", "broker_day_authoritative": True, "broker_day_row_count": 1},
    }
minimal = {"trade_id": "TRD_X", "symbol": "005930", "action": "HOLD", "status": "open", "story_type": "simulation", "execution_mode_label": "simulation"}
out = {}
story = rich_story(); before = copy.deepcopy(story)
rep = mod.build_deterministic_trade_report(story); check(story == before, "story_input mutated by producer")
out["producer_sections"] = sorted(rep)
rep_min = mod.build_deterministic_trade_report(copy.deepcopy(minimal))
rep_before = copy.deepcopy(rep)
md_a = mod.render_trade_summary_markdown(rep); md_b = mclean.render_trade_summary_markdown_clean(rep); md_c = None
check(rep == rep_before, "report mutated by renderer")
out["chain_equal"] = [md_a == md_b, md_c is None or md_c == md_a]
check(md_a == md_b, "facade vs clean differ")
md_min = mod.render_trade_summary_markdown(rep_min)
out["len_rich_min"] = [len(md_a), len(md_min)]
out["rich_markers"] = {k: (k in md_a) for k in ("000660", "034020", "70,100", "70100", "-320", "trailing", "차순위", "선정 경로", "재평가", "kiwoom", "손실", "청산")}
out["rich_head"] = norm(md_a)[:700]
check(len(md_a) > len(md_min) * 1.2, "rich report must render materially more than minimal")
out["deterministic"] = norm(mod.render_trade_summary_markdown(copy.deepcopy(rep))) == norm(md_a)
si = mod.build_trade_summary_input(rep); out["summary_input_keys"] = sorted(si)
out["decision_flow"] = {k: si.get("decision_flow", {}).get(k) for k in ("scanner_rank_basis", "scanner_score", "selection_basis")}
out["truth_surface"] = {k: rep.get("truth_surface", {}).get(k) for k in ("price", "pnl")}
out["md_rich_norm"] = norm(md_a); out["md_min_norm"] = norm(md_min)
out["bad"] = bad
check(not bad, "blocked attempts: %r" % bad)
print("RF028_RICH_SCHEMA_OK sections=%d chain_equal=%s len=%d/%d deterministic=%s blocked=0 debug=%s" % (len(rep), out["chain_equal"], len(md_a), len(md_min), out["deterministic"], __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
