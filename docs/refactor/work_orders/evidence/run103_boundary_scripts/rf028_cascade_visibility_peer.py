# RF-028: entry_candidate_cascade / entry_execution_visibility branches via the formal producer (build_deterministic_trade_report)
# and every renderer (summary + full). Offline, tmp-isolated, writes blocked.
import os, sys, json, copy, re, shutil, socket, subprocess, sqlite3, builtins, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
root = Path("/tmp/rf028_cv_fixed"); shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "events.jsonl"); os.chdir(root)
import ssl, http.client
mod = importlib.import_module("libs.reporting.trade_report_ai")
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
def base_story():
    return {"trade_id": "TRD_20260318_000660_01", "story_id": "TRD_20260318_000660_01", "run_id": "run-1", "day": "2026-03-18", "symbol": "000660", "action": "HOLD", "status": "open", "story_type": "simulation", "execution_mode_label": "simulation", "monitor_reason_human": {"posture": "HOLD"}}
ENTRY_CONTROL = {"mode": "strategy_watch_policy", "decision": "apply_strategy_candidate_watch_policy", "reason": "strategy_candidate_watch_policy", "max_priority_rank": 7, "max_runner_ups": 6, "cascade_enabled": True,
                 "candidate_watch_policy_detected": True, "candidate_watch_policy_applied": True, "candidate_watch_policy_clamp_reason": "balanced_rank_cap",
                 "candidate_watch_policy_proposal": {"source": "strategist_output.candidate_watch_policy", "max_priority_rank": 10, "max_runner_ups": 9, "cascade_enabled": True, "reason": "watch leaders beyond the first rank"}}
CASCADE_FALLBACK = {"attempted": True, "eligible": True, "cascade_enabled": True, "top_pick_symbol": "005930", "top_pick_triggered": False, "top_pick_reason": "breakout_not_ready", "max_priority_rank": 7, "max_runner_ups": 6,
                    "runner_up_symbols": ["000660", "035420"], "fallback_used": True, "fallback_from_symbol": "005930", "fallback_to_symbol": "000660", "fallback_to_rank": 2, "final_selected_symbol": "000660", "final_selected_rank": 2,
                    "fallback_trace": [{"symbol": "000660", "rank": 2, "score_total": 0.72, "triggered": True, "reason": "vwap_reclaim_confirmed", "confidence_score": 0.61, "confidence_threshold": 0.55}]}
STRAT = {"strategy_thesis": {"selected_playbook": "pullback", "risk_tone": "balanced", "market_view": "leader pullback needs confirmation"}, "tactical_strategy": "vwap_reclaim_pullback",
         "candidate_watch_policy": {"source": "strategist_output.candidate_watch_policy", "behavior_effect": "execution_proposal", "max_priority_rank": 10, "max_runner_ups": 9, "cascade_enabled": True, "tactical_strategy": "vwap_reclaim_pullback", "reason": "watch leaders beyond the first rank"}}
def scen(name):
    s = base_story()
    if name == "fallback":      # formal schema: everything under canonical_agent_artifacts
        s["canonical_agent_artifacts"] = {"strategist": copy.deepcopy(STRAT), "commander": {"selected_route": "full_cycle", "policy_source": "strategist", "commander_decision": {"command_intent": "ALLOW_ENTRY_SCAN", "entry_control": copy.deepcopy(ENTRY_CONTROL)}},
                                          "monitor": {"entry_candidate_cascade": copy.deepcopy(CASCADE_FALLBACK)}}
    elif name == "flat_keys_ignored":   # same data placed at top level (non-formal location)
        s["commander"] = {"selected_route": "full_cycle", "commander_decision": {"entry_control": copy.deepcopy(ENTRY_CONTROL)}}
        s["monitor"] = {"entry_candidate_cascade": copy.deepcopy(CASCADE_FALLBACK)}
    elif name == "blocked":
        s["canonical_agent_artifacts"] = {"commander": {"commander_decision": {"entry_control": {"max_priority_rank": 10, "max_runner_ups": 9, "cascade_enabled": True}}},
                                          "monitor": {"entry_candidate_cascade": {"attempted": False, "eligible": False, "cascade_enabled": True, "blocked_reason": "max_positions_reached", "top_pick_symbol": "005930", "final_selected_symbol": "005930", "max_priority_rank": 10, "max_runner_ups": 9}}}
    elif name == "top_pick_triggered":
        s["canonical_agent_artifacts"] = {"commander": {"commander_decision": {"entry_control": {"max_priority_rank": 5, "max_runner_ups": 4, "cascade_enabled": True}}},
                                          "monitor": {"entry_candidate_cascade": {"attempted": True, "eligible": True, "cascade_enabled": True, "top_pick_symbol": "000660", "top_pick_triggered": True, "fallback_used": False, "final_selected_symbol": "000660", "final_selected_rank": 1, "runner_up_symbols": []}}}
    elif name == "watch_proposal_only":
        s["canonical_agent_artifacts"] = {"strategist": {"tactical_strategy": "vwap_reclaim_pullback", "candidate_watch_policy": {"tactical_strategy": "vwap_reclaim_pullback", "reason": "recent pullback pattern explanation"}}}
    elif name == "malformed_types":
        s["canonical_agent_artifacts"] = {"commander": {"commander_decision": {"entry_control": "x"}},
                                          "monitor": {"entry_candidate_cascade": {"attempted": "yes", "runner_up_symbols": "000660,035420", "fallback_trace": "nope", "max_priority_rank": "seven", "final_selected_rank": None}}}
    elif name == "cascade_not_dict":
        s["canonical_agent_artifacts"] = {"monitor": {"entry_candidate_cascade": ["x"]}}
    return s
out = {}
for name in ("fallback", "flat_keys_ignored", "blocked", "top_pick_triggered", "watch_proposal_only", "malformed_types", "cascade_not_dict", "none"):
    story = scen(name) if name != "none" else base_story(); before = copy.deepcopy(story)
    try:
        ci = mod.build_ai_trade_report_compact_input(copy.deepcopy(story))
        rep = mod.build_deterministic_trade_report(story); check(story == before, "story mutated: " + name)
        rb = copy.deepcopy(rep); summary = mod.render_trade_summary_markdown(rep); full = mod.render_trade_report_markdown(rep); check(rep == rb, "report mutated: " + name)
        vis = rep.get("entry_execution_visibility") or {}
        out[name] = {"vis_keys": sorted(vis), "compact_vis": sorted(ci.get("entry_execution_visibility") or {}), "cascade_final": (vis.get("monitor_entry_candidate_cascade") or {}).get("final_selected_symbol"),
                     "control": {k: (vis.get("commander_entry_control") or {}).get(k) for k in ("max_priority_rank", "max_runner_ups", "cascade_enabled")},
                     "summary_lines": [l for l in norm(summary).splitlines() if "후보 감시" in l or "후보 선택" in l], "full_lines": [l for l in norm(full).splitlines() if "후보 감시" in l or "후보 선택" in l or "최종 후보" in l],
                     "leaks": [t for t in ("balanced_rank_cap", "전략가 후보 감시 제안", "watch leaders beyond the first rank", "지휘관 최종 적용 범위", "recent pullback pattern explanation") if t in summary],
                     "len": [len(summary), len(full)]}
    except Exception as e:
        out[name] = {"EXC": type(e).__name__, "msg": str(e)[:100]}
check(not bad, "blocked attempts: %r" % bad)
f = out["fallback"]; check("EXC" not in f and f["cascade_final"] == "000660" and f["control"]["max_priority_rank"] == 7, "fallback branch")
check(any("후보 감시: 7위까지 / 차순위 6개 / cascade 활성" in l for l in f["summary_lines"]) and any("최종 후보: 000660(2위)" in l for l in f["summary_lines"]), "fallback summary lines")
check(not f["leaks"], "summary must not leak internal proposal text")
check(out["watch_proposal_only"].get("summary_lines") == [], "empty proposal omitted")
out["bad"] = bad
n_exc = sum(1 for v in out.values() if isinstance(v, dict) and "EXC" in v)
print("RF028_CASCADE_VISIBILITY_OK scenarios=8 exc=%d fallback_lines=%d blocked_lines=%d leaks=0 blocked=0 debug=%s" % (n_exc, len(f["summary_lines"]), len(out["blocked"].get("summary_lines", [])), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
