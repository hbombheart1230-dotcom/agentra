# RF-029: human payload builders (market/scanner/filters/monitor/guard/outcome/reporter/conclusion/timeline/warnings) -> story renderers.
# Pure functions via the real facade; inputs mirror the shapes used by tests/test_trade_story_pipeline_enrichment.py. No IO.
import os, sys, json, copy, importlib, re
repo = os.getcwd(); sys.path.insert(0, repo)
st = importlib.import_module("libs.reporting.trade_story_pipeline")
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
out = {}
def call(name, f, *a, **k):
    snap = copy.deepcopy((a, k))
    try: r = f(*a, **k)
    except Exception as e: out[name] = "EXC:" + type(e).__name__ + ":" + str(e)[:60]; return None
    check((a, k) == snap, "input mutated: " + name)
    out[name] = json.dumps(r, sort_keys=True, ensure_ascii=False, default=repr); return r
strategist = {"market_regime": "neutral", "market_sentiment": "neutral", "playbook": "breakout", "themes": ["broad_market_leaders"], "macro_stress_overlay": {"stress_flags": ["elevated_vix"], "active": True},
              "news_query_targets": ["KOSPI", "US indices"], "theme_strength_packet": {"source": "unavailable", "status": "unavailable", "reason": "kiwoom_theme_live_fetch_disabled", "top_themes": [], "theme_scores": {}},
              "input_summary": {"global_sentiment_score": -0.2235, "vix_level": 25.09, "headline_count": 75, "candidate_signal_total": 5, "market_signal_total": 10, "news_query_targets": ["코스피", "환율"]}}
scanner = {"universe_size": 5, "selected_symbol": "000660",
           "ranking_table": [{"rank": 1, "symbol": "000660", "score_total": 1.1776, "risk_score": 0.6281, "confidence": 0.8099}, {"rank": 2, "symbol": "005930", "score_total": 1.1519, "risk_score": 0.731, "confidence": 0.7851}],
           "selected_candidate": {"symbol": "000660", "sources": ["top_value"], "score_total": 1.1776, "risk_score": 0.6281, "confidence": 0.8099, "score_breakdown": {"trading_value": 0.22, "trend": 0.16, "sentiment": 0.018}, "feature_snapshot": {"engine_ma20_gap": 0.05}},
           "candidate_preview": [{"symbol": "005930", "why": "weaker sector fit"}]}
supervisor_ok = {"supervisor_allow": True, "verdict": "approve", "supervisor_reason": "within limits", "action": "BUY", "symbol": "000660"}
supervisor_block = {"supervisor_allow": False, "guard_reason": "max_positions_reached", "action": "BUY", "symbol": "000660"}
monitor_exit = {"trigger_type": "hard_stop", "monitor_reason": "confirmed_exit_signal", "thresholds_guards_used": {"thresholds": {"stop_loss_pct": 0.08, "effective_stop_loss_pct": 0.01, "effective_stop_reason": "hard_stop"}, "exit_confirm_ticks": 3, "exit_confirm_count": 2},
                "exit_triggered": True, "current_price": 29300.0, "average_price": 29650.0, "active_exit_axis": "Hard Stop", "watch_axes": ["Hard stop", "Take profit"]}
monitor_pending = {"exit_reason": "exit_confirmation_pending:1/2", "monitor_reason": "exit_signal_pending_confirmation", "thresholds_guards_used": {"exit_confirm_ticks": 2, "exit_confirm_count": 1}, "exit_triggered": False, "sell_guard_blocked": True, "active_exit_axis": "Partial Take Profit"}
mkt = call("market", st.build_market_context_human, strategist)
sc = call("scanner", st.build_scanner_reason_human, scanner, strategist)
fl = call("filters", st.build_filters_human, scanner, strategist, supervisor_ok)
mon_exit = call("monitor_exit", st.build_monitor_reason_human, monitor_exit, {"action": "SELL"})
mon_pend = call("monitor_pending", st.build_monitor_reason_human, monitor_pending, {"action": "SELL"})
call("monitor_empty", st.build_monitor_reason_human, {}, {})
g_ok = call("guard_ok", st.build_guard_reason_human, supervisor_ok); g_bl = call("guard_block", st.build_guard_reason_human, supervisor_block); call("guard_empty", st.build_guard_reason_human, {})
ex = {"action": "BUY", "symbol": "000660", "qty": 3, "status": "filled", "price": 70100}
eo = call("outcome", st.build_execution_outcome_human, ex, {"executor_mode": "mock"}, story_type="simulation", mode_label="simulation")
call("outcome_empty", st.build_execution_outcome_human, {}, {}, story_type="", mode_label="")
rs_linked = call("reporter_linked", st.build_reporter_status_human, {"reporter_analysis_found": True, "reporter_analysis_summary": "ok"}, {"ai_run_grade": "B"})
rs_pend = call("reporter_pending", st.build_reporter_status_human, {"reporter_analysis_day_file_found": True}, {})
rs_none = call("reporter_none", st.build_reporter_status_human, {}, {})
oc = call("conclusion", st.build_operator_conclusion_human, execution=ex, scanner_reason_human=sc, filters_human=fl, monitor_reason_human=mon_exit, execution_outcome_human=eo, reporter_status_human=rs_linked)
call("conclusion_empty", st.build_operator_conclusion_human, execution={}, scanner_reason_human={}, filters_human={}, monitor_reason_human={}, execution_outcome_human={}, reporter_status_human={})
tl = call("timeline", st.build_timeline, commander={"selected_route": "full_cycle"}, market_context_human=mkt, scanner_reason_human=sc, monitor_reason_human=mon_exit, guard_reason_human=g_ok, execution_outcome_human=eo, reporter_status_human=rs_linked, execution=ex)
call("timeline_empty", st.build_timeline, commander={}, market_context_human={}, scanner_reason_human={}, monitor_reason_human={}, guard_reason_human={}, execution_outcome_human={}, reporter_status_human={}, execution={})
call("warnings", st.collect_story_warnings, story_contract={"story_type": "simulation"}, market_context_human=mkt, filters_human=fl, reporter_status_human=rs_none, execution_outcome_human=eo)
call("warnings_empty", st.collect_story_warnings, story_contract={}, market_context_human={}, filters_human={}, reporter_status_human={}, execution_outcome_human={})
# renderers
bundle = {"run_id": "run-9", "day": "2026-04-20", "story_contract": {"story_anchor": "TRD_X", "story_type": "simulation", "execution_mode_label": "simulation"}, "market_context_human": mkt, "scanner_reason_human": sc, "filters_human": fl,
          "monitor_reason_human": mon_exit, "guard_reason_human": g_ok, "execution_outcome_human": eo, "reporter_status_human": rs_linked, "operator_conclusion_human": oc, "timeline": tl or [], "artifacts": {"report_json": "/tmp/x.json", "md": "/tmp/x.md"}}
b0 = copy.deepcopy(bundle); md = st.render_bundle_markdown(bundle); check(bundle == b0, "bundle mutated by renderer"); out["bundle_md"] = md
out["bundle_md_empty"] = st.render_bundle_markdown({}); out["bundle_md_badtypes"] = st.render_bundle_markdown({"story_contract": "x", "market_context_human": "x", "timeline": ["x", {"step": "s"}, 5], "artifacts": {}})
out["bundle_md_cap"] = st.render_bundle_markdown({"scanner_reason_human": {"summary": "S", "bullets": [str(i) for i in range(12)]}, "timeline": [{"step": i, "summary": "t%d" % i} for i in range(14)]})
bundles = [{"run_id": "r1", "action": "BUY", "symbol": "000660", "qty": 3, "story_type": "simulation", "trade_report_json_path": "/tmp/a.json"}, {"run_id": "r2", "action": "SELL"}]
out["summary_md"] = st.render_summary_markdown({"day": "2026-04-20", "bundle_count": 2, "canonical_trades_root": "/tmp/trades", "bundles": bundles})
out["summary_md_none"] = st.render_summary_markdown({"day": "2026-04-20", "bundle_count": 0, "canonical_trades_root": "/tmp/trades", "bundles": []})
out["summary_md_badtype"] = st.render_summary_markdown({"bundles": "x"})
try: st.render_bundle_markdown(None); out["bundle_none"] = "no-raise"
except Exception as e: out["bundle_none"] = type(e).__name__
# use-time patch through the facade (builders look up deps on the module at call time)
orig = st.safe_float if hasattr(st, "safe_float") else None
out["patch_target_exists"] = orig is not None
# checks on key content
check("Aggregated Execution Bundle (run-9)" in md and "## Operator Conclusion" in md and "- report_json: `/tmp/x.json`" in md, "bundle md sections")
cap = out["bundle_md_cap"]; check("\n- 7\n" in cap and "\n- 8\n" not in cap and "- 9: t9" in cap and "- 10: t10" not in cap, "caps: 8 bullets + 10 timeline rows")
check("No executed BUY/SELL runs" in out["summary_md_none"] and "x3" in out["summary_md"], "summary md")
check(json.loads(out["guard_ok"])["allow"] is True and json.loads(out["guard_block"])["allow"] is False and "max_positions_reached" in out["guard_block"], "guard")
check(json.loads(out["monitor_pending"])["pending_confirmation"] is True and json.loads(out["monitor_pending"])["monitor_execution_mismatch"] is True, "pending exit is mismatch")
check(json.loads(out["monitor_exit"])["posture"] == "SELL" and json.loads(out["monitor_exit"])["confirm_required"] == 3, "exit confirmed")
check(json.loads(out["scanner"])["selected_symbol"] == "000660" and json.loads(out["market"])["headline_count"] == 75, "scanner/market")
n_exc = sum(1 for v in out.values() if isinstance(v, str) and v.startswith("EXC:"))
print("RF029_STORY_HUMAN_RENDER_OK builders=%d renderers=7 exc=%d bundle_md=%d summary_md=%d mutation=none debug=%s" % (sum(1 for k in out if not k.startswith(("bundle_md", "summary_md", "patch", "bundle_none"))), n_exc, len(md), len(out["summary_md"]), __debug__), file=sys.stderr)
# wall-clock timestamps (timeline reporter_output step uses now()) are redacted for byte comparison
print(re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+00:00', "NOW", json.dumps(out, sort_keys=True, ensure_ascii=False)))
