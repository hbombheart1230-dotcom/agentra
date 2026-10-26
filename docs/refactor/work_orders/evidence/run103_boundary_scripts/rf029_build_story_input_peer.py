# RF-029: trade_story_pipeline.build_trade_story_input (facade -> story_assembly): bundle assembly, State alias, lifecycle override, malformed. Pure, no IO.
import os, sys, json, copy, importlib
repo = os.getcwd(); sys.path.insert(0, repo)
st = importlib.import_module("libs.reporting.trade_story_pipeline")
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def rich():
    return {"day": "2026-03-24", "run_id": "run-trace-1", "trade_id": "TRD_TEST_1", "story_id": "TRD_TEST_1", "symbol": "003280",
            "market_context_human": {"summary": "Commander saw a defensive regime."}, "scanner_reason_human": {"summary": "Scanner preferred 003280 over 000660.", "selected_symbol": "003280"},
            "monitor_reason_human": {"summary": "Monitor waited for confirmation."}, "operator_conclusion_human": {"summary": "No new action yet."}, "execution_outcome_human": {"summary": "Execution was not attempted."},
            "guard_reason_human": {"summary": "No guard escalation."}, "reporter_status_human": {"summary": "Reporter ready."}, "filters_human": {"summary": "filters"}, "warnings": ["w1"], "timeline": [{"step": "s", "summary": "t"}],
            "strategist_summary": {"selected_playbook": "defensive", "strategy_summary": "Strategist kept a defensive playbook.", "strategist_fallback_used": False},
            "strategist": {"news_query_targets": ["shipping", "KOSPI"], "candidate_symbols_hint": ["003280", "000660"], "candidate_hypotheses": [{"symbol": "003280", "hypothesis": "shipping momentum candidate"}],
                           "news_evidence_ranked": {"market_news_ranked": [{"title": "Shipping names stay active."}], "candidate_news_ranked": [{"symbol": "003280", "title": "003280 extends momentum."}]}},
            "scanner_summary": {"selected_symbol": "003280", "runner_up_symbol": "000660", "selection_summary": "003280 ranked first with better liquidity."},
            "scanner": {"selected_symbol": "003280", "top_ranked_symbols": ["003280", "000660"], "candidate_ranking_table": {"rows": [{"symbol": "003280", "rank": 1, "score_total": 1.18}]}},
            "monitor_summary": {"decision": "WAIT", "entry_check_summary": "VWAP reclaim confirmation is still pending."},
            "commander_summary": {"command_intent": "OBSERVE_ONLY", "decision_summary": "Commander kept the session in observe-only mode.", "shadow_used": True, "strategist_fallback_used": False},
            "canonical_agent_artifacts": {"canonical_commander_json": "/tmp/commander.json", "canonical_strategist_json": "/tmp/strategist.json", "canonical_scanner_json": "/tmp/scanner.json", "canonical_monitor_json": "/tmp/monitor.json"},
            "evidence_provenance": {"commander": "canonical", "strategist": "canonical", "scanner": "canonical", "monitor": "canonical"}}
LC_OPEN = {"status": "open", "entry": {"run_id": "RUN_ENTRY", "action": "BUY", "qty": 3, "price": 70000, "reason_human": "entry ok"}}
LC_CLOSED = {"status": "closed", "entry": {"run_id": "RUN_ENTRY", "action": "BUY", "qty": 3, "price": 70000}, "exit": {"run_id": "RUN_EXIT", "action": "SELL", "qty": 3, "price": 70100, "reason_human": "exit ok"}}
out = {}
def run(name, bundle, **kw):
    snap = copy.deepcopy((bundle, kw))
    try: r = st.build_trade_story_input(bundle, **kw)
    except Exception as e: out[name] = ["EXC", type(e).__name__, str(e)[:60]]; return None
    check((bundle, kw) == snap, "input mutated: " + name)
    out[name] = ["ok", json.dumps(r, sort_keys=True, ensure_ascii=False, default=repr)]; return r
r = run("rich", rich()); check(r is not None, "rich must assemble")
out["rich_keys"] = sorted(r); out["rich_schema"] = r.get("schema_version")
rt = r["reasoning_trace"]; check(rt["commander_summary"]["summary"] == "Commander kept the session in observe-only mode." and rt["strategist_summary"]["summary"] == "Strategist kept a defensive playbook." and rt["monitor_summary"]["summary"] == "VWAP reclaim confirmation is still pending.", "reasoning trace")
rp = r["reasoning_provenance"]; check(rp["shadow_used"] is True and rp["commander_source_ref"] == "/tmp/commander.json", "reasoning provenance")
out["trace_provenance_keys"] = [sorted(rt), sorted(rp)]
# idempotent + facade parity with the impl
a = st.build_trade_story_input(rich()); b = st.build_trade_story_input(rich()); out["idempotent"] = json.dumps(a, sort_keys=True, default=repr) == json.dumps(b, sort_keys=True, default=repr)
check(out["idempotent"], "assembly must be deterministic")
asm = importlib.import_module("libs.reporting.trade_story_pipeline_story_assembly")
out["impl_parity"] = json.dumps(asm.build_trade_story_input(rich(), trade_lifecycle=None, deps=st._story_assembly_deps()), sort_keys=True, default=repr) == json.dumps(a, sort_keys=True, default=repr)
check(out["impl_parity"], "facade vs impl")
# lifecycle variants
run("open_lifecycle", rich(), trade_lifecycle=copy.deepcopy(LC_OPEN)); run("closed_lifecycle", rich(), trade_lifecycle=copy.deepcopy(LC_CLOSED))
o, c = json.loads(out["open_lifecycle"][1]), json.loads(out["closed_lifecycle"][1])
out["lifecycle_diff_keys"] = sorted(k for k in set(o) | set(c) if o.get(k) != c.get(k))
check(o != c, "open vs closed lifecycle must differ")
run("lifecycle_empty_dict", rich(), trade_lifecycle={}); run("lifecycle_str", rich(), trade_lifecycle="x"); run("lifecycle_none", rich(), trade_lifecycle=None)
# State alias: which nested objects of the bundle are shared with the result
bo = rich(); res = st.build_trade_story_input(bo)
alias = {}
for k in ("warnings", "timeline", "market_context_human", "scanner_reason_human", "monitor_reason_human", "guard_reason_human", "execution_outcome_human", "reporter_status_human", "operator_conclusion_human", "filters_human", "canonical_agent_artifacts", "evidence_provenance", "strategist", "scanner"):
    if k in res: alias[k] = res[k] is bo[k]
out["alias_identity"] = alias
res_keys_shared = [k for k, v in alias.items() if v]
if "warnings" in res:
    res["warnings"].append("MUTATED"); out["warnings_mutation_leaks_into_bundle"] = "MUTATED" in bo["warnings"]
# malformed / minimal
run("empty_bundle", {}); run("bundle_none", None); run("bundle_list", []); run("bundle_str", "x")
bad = rich(); bad["market_context_human"] = "x"; bad["timeline"] = "x"; bad["warnings"] = None; bad["strategist"] = ["x"]; bad["canonical_agent_artifacts"] = "x"; bad["evidence_provenance"] = None
run("nested_types_polluted", bad)
b2 = rich(); b2["scanner"] = None; b2["commander_summary"] = []; b2["strategist_summary"] = 5; run("summary_types_polluted", b2)
check(out["bundle_none"][0] == "EXC" and out["bundle_list"][0] == "EXC" and out["bundle_str"][0] == "EXC", "non-dict bundle raises")
out["exc_names"] = {k: v[1] for k, v in out.items() if isinstance(v, list) and v and v[0] == "EXC"}
print("RF029_BUILD_STORY_INPUT_OK variants=%d exc=%d alias_shared=%d idempotent=%s impl_parity=%s mutation=none debug=%s" % (sum(1 for v in out.values() if isinstance(v, list) and v and v[0] in ("ok", "EXC")), len(out["exc_names"]), len(res_keys_shared), out["idempotent"], out["impl_parity"], __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
