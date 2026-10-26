# RF-016: strategic_answers owner via the real facade (graphs.nodes.strategist_node._build_strategic_answers): use-time patching,
# nested copy/alias semantics, malformed-input exceptions. Offline/tmp only (writes blocked, no network).
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
root = Path("/tmp/rf016_fixed"); shutil.rmtree(root, ignore_errors=True); (root / "reports" / "trades").mkdir(parents=True)
os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "events.jsonl"); os.chdir(root)
import ssl, http.client
sn = importlib.import_module("graphs.nodes.strategist_node")
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
out = {}
def base_kwargs():
    return dict(
        commander_context={"strategist_refresh_requested": True, "strategist_refresh_reason": "why", "carry_state": "cs", "carry_risk_bias": "cb", "carry_risk_reason": "cr",
                           "session_open_recovery_assessment": {"a": {"deep": 1}}, "commander_horizon_policy": {"owner": "", "strategy_horizon": "swing", "source_strategy_horizon": "src", "observability_only": False, "do_not_force_hold": False},
                           "open_position_refresh_context": {"selected_symbol": "005930", "selected_rank": 1, "selected_score": 0.123456, "scanner_primary_candidate": {"symbol": "005930", "n": {"x": 1}},
                                                             "scanner_runner_ups": [{"s": i} for i in range(6)] + ["bad"], "scanner_top_candidates": [{"s": i} for i in range(7)], "stage2_context_quality_reasons": [" r1", "", "r2", "r3", "r4", "r5", "r6", "r7"],
                                                             "entry_state": {"e": {"n": 1}}, "prior_monitor_entry_policy_summary": {"p": 1}, "current_monitor_entry_policy_summary": "notdict", "hold_repeat_count_max": "3", "selected_hold_repeat_count": None}},
        market_regime="risk_on", market_sentiment="bullish", key_events=["e1", "e2"], themes=["t1"], avoid_themes=["a1"], playbook="pullback", scanner_bias="leader", scanner_priority=["trading_value"],
        trade_aggressiveness="medium", risk_tone="normal", monitor_guidance="hold_through_noise", report_focus=["rf"],
        recent_strategy_feedback={"feedback_window_size": "5", "top_recent_strengths": list("abcde"), "top_recent_weaknesses": ["w"], "recent_reporter_summary": ["s1", "s2", "s3"]},
        strategy_memory={"status": "ok", "best_playbooks": list("12345"), "worst_playbooks": [], "recent_failures": ["f"], "recent_success_patterns": [], "playbook_performance_snapshot": {"pb": {"n": 1}}, "reporter_analysis_digest": {"d": 1}},
        read_model_facts={"symbol_patterns": {"005930": {"wins": 3}}}, reports_root=str(root / "reports"))
# 1) baseline output
kw = base_kwargs(); before = copy.deepcopy(kw)
res = sn._build_strategic_answers(**kw)
check(kw == before, "inputs mutated")
q15 = res["q15_commander_refresh_context"]
out["keys"] = sorted(res); out["q15_keys"] = sorted(q15)
out["q13"] = res["q13_recent_strategy_feedback"]; out["q14"] = res["q14_strategy_memory_advisory"]
out["q15_scalars"] = {k: q15[k] for k in ("requested", "reason", "selected_symbol", "hold_repeat_count_max", "selected_hold_repeat_count", "selected_rank", "selected_score", "selected_symbol_was_rank1", "carry_state", "carry_risk_bias", "carry_risk_reason", "stage2_context_quality_reasons", "prior_monitor_entry_policy_summary", "current_monitor_entry_policy_summary", "horizon_context")}
out["q15_lens"] = [len(q15["scanner_runner_ups"]), len(q15["scanner_top_candidates"])]
out["selected_symbol_memory"] = q15["selected_symbol_memory"]
# 2) use-time patching through the facade module globals
calls = []
orig_round, orig_mem = sn._round_optional, sn._build_symbol_refresh_memory_excerpt
sn._round_optional = lambda v, d=4: (calls.append(("round", v, d)) or "R")
sn._build_symbol_refresh_memory_excerpt = lambda sym, facts, rr: (calls.append(("mem", sym, dict(facts), rr)) or {"patched": True})
r2 = sn._build_strategic_answers(**base_kwargs())["q15_commander_refresh_context"]
out["patched"] = [r2["selected_score"], r2["selected_symbol_memory"], [c[0] for c in calls], calls[0][1:], calls[1][1:3]]
sn._round_optional, sn._build_symbol_refresh_memory_excerpt = orig_round, orig_mem
check(r2["selected_score"] == "R" and r2["selected_symbol_memory"] == {"patched": True}, "use-time patch honoured")
r3 = sn._build_strategic_answers(**base_kwargs())["q15_commander_refresh_context"]; check(r3["selected_score"] == res["q15_commander_refresh_context"]["selected_score"], "patch restored")
# 3) nested copy / alias semantics
kw = base_kwargs(); res = sn._build_strategic_answers(**kw); q15 = res["q15_commander_refresh_context"]; rc = kw["commander_context"]["open_position_refresh_context"]
alias = {}
alias["top_dict_copied"] = q15["entry_state"] is not rc["entry_state"]
alias["nested_in_entry_state_shared"] = q15["entry_state"]["e"] is rc["entry_state"]["e"]
alias["primary_candidate_nested_shared"] = q15["scanner_primary_candidate"]["n"] is rc["scanner_primary_candidate"]["n"]
alias["runner_up_row_copied"] = q15["scanner_runner_ups"][0] is not rc["scanner_runner_ups"][0]
alias["key_events_list_copied"] = res["q2_global_macro_events"] is not kw["key_events"]
alias["q14_perf_nested_shared"] = res["q14_strategy_memory_advisory"]["recent_playbook_performance"]["pb"] is kw["strategy_memory"]["playbook_performance_snapshot"]["pb"]
alias["session_open_nested_shared"] = q15["session_open_recovery_assessment"]["a"] is kw["commander_context"]["session_open_recovery_assessment"]["a"]
out["alias"] = alias
q15["entry_state"]["e"]["n"] = 99; out["mutation_leaks_into_input_via_nested"] = rc["entry_state"]["e"]["n"] == 99
# 4) selection fallbacks & malformed inputs
def run(name, mut):
    k = base_kwargs(); mut(k)
    try: out["m|" + name] = ["ok", sorted(sn._build_strategic_answers(**k))[:3]]
    except Exception as e: out["m|" + name] = [type(e).__name__, str(e)[:70]]
def cc(k, **upd): k["commander_context"] = {**k["commander_context"], **upd}
run("ctx_none", lambda k: k.update(commander_context=None))
run("ctx_empty", lambda k: k.update(commander_context={}))
run("refresh_ctx_not_dict", lambda k: cc(k, open_position_refresh_context="x", strategist_refresh_context=["y"]))
run("rank_str", lambda k: cc(k, open_position_refresh_context={"selected_rank": "x"}))
run("rank_none", lambda k: cc(k, open_position_refresh_context={"selected_rank": None, "selected_symbol_was_rank1": None}))
run("rank1_flag_false", lambda k: cc(k, open_position_refresh_context={"selected_rank": 1, "selected_symbol_was_rank1": False}))
run("feedback_none", lambda k: k.update(recent_strategy_feedback=None))
run("memory_none", lambda k: k.update(strategy_memory=None))
run("key_events_none", lambda k: k.update(key_events=None))
run("themes_str", lambda k: k.update(themes="ab"))
run("window_size_bad", lambda k: k["recent_strategy_feedback"].update(feedback_window_size="x"))
run("score_bad", lambda k: cc(k, open_position_refresh_context={"selected_symbol": "005930", "selected_score": "abc"}))
run("facts_none", lambda k: k.update(read_model_facts=None))
run("reports_root_none", lambda k: k.update(reports_root=None))
run("refresh_fallback_to_strategist_ctx", lambda k: cc(k, open_position_refresh_context={}, strategist_refresh_context={"selected_symbol": "000660", "selected_rank": 2}))
rr = sn._build_strategic_answers(**{**base_kwargs(), "commander_context": {"strategist_refresh_context": {"selected_symbol": "000660", "selected_rank": 2, "selected_symbol_was_rank1": None}}})["q15_commander_refresh_context"]
out["fallback_ctx"] = [rr["selected_symbol"], rr["selected_rank"], rr["selected_symbol_was_rank1"]]
# 5) static consumer location
src = open(repo + "/libs/runtime/strategist/policy/node_policy_projection.py", encoding="utf-8").read()
out["consumer_uses_facade_lookup"] = "facade._build_strategic_answers(" in src
out["bad"] = bad
check(not bad, "blocked attempts: %r" % bad)
check(out["consumer_uses_facade_lookup"], "consumer lookup")
print("RF016_STRATEGIC_ANSWERS_OK keys=%d q15_keys=%d malformed=%d alias_shared=%d patched=%s writes=0 debug=%s" % (len(out["keys"]), len(out["q15_keys"]), sum(k.startswith("m|") for k in out), sum(1 for k, v in alias.items() if v and k.endswith("shared")), r2["selected_score"] == "R", __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
