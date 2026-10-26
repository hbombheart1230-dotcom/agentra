# RF-029: libs/reporting/trade_story_pipeline.py facade -> trade_story_pipeline_story_assembly.py (build_trade_story_input)
# real report/story artifact consumers: lifecycle path, direct path, canonical_*_json hydration from tmp files (read-only),
# sibling monitor.json resolution, State immutability, exception contract. Offline, tmp-isolated, all writes blocked.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
import tempfile
root = Path(tempfile.mkdtemp(prefix="rf029_sp_"))
os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "events.jsonl")
# canonical fixture files are created BEFORE writes are blocked (setup only), then everything is read-only
canon = root / "canon"; canon.mkdir()
(canon / "strategist.json").write_text(json.dumps({"strategy_horizon": "intraday", "tactical_strategy": "vwap_reclaim_pullback"}), encoding="utf-8")
(canon / "scanner.json").write_text(json.dumps({"selected": {"symbol": "000660"}}), encoding="utf-8")
(canon / "monitor.json").write_text(json.dumps({"scanner_monitor_handoff": {"scanner_selected_symbol": "000660", "monitor_selected_symbol": "000660", "entry_candidate_cascade": {"attempted": True, "fallback_used": True}}}), encoding="utf-8")
(canon / "commander.json").write_text("{not json", encoding="utf-8")        # malformed
(canon / "supervisor.json").write_text(json.dumps(["list", "not", "dict"]), encoding="utf-8")   # non-dict
os.chdir(root)
import ssl, http.client
facade = importlib.import_module("libs.reporting.trade_story_pipeline")
assembly = importlib.import_module("libs.reporting.trade_story_pipeline_story_assembly")
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

def lifecycle(status="open", exit_action="", exit_reason=""):
    return {"trade_id": "TRD_20260318_000660_01", "symbol": "000660", "status": status, "story_type": "simulation", "execution_mode_label": "simulation",
            "entry": {"run_id": "r1", "ts": "2026-03-18T00:10:00+00:00", "action": "BUY", "reason_human": "entry reason", "strategist_context": {"a": 1}, "scanner_context": {"selected_symbol": "000660"},
                      "monitor_context": {"entry_triggered": False}, "guard_context": {"ok": True}, "execution_context": {"qty": 1}},
            "holding": {"run_ids": ["r2", "", "r3"], "holding_events": [{"k": i} for i in range(25)] + ["skip"], "posture_history": [{"p": 1}], "monitor_updates": ["u1", " "]},
            "exit": ({"run_id": "r9", "ts": "2026-03-18T05:00:00+00:00", "action": exit_action, "reason_human": exit_reason, "monitor_context": {"exit_reason": exit_reason}} if exit_action else {}),
            "summary": {"holding_duration": "4h", "entry_reason_human": "e", "exit_reason_human": exit_reason, "operator_conclusion_human": "c"},
            "reporter": {"improvement_points": ["i1", "", "i2"]}, "timeline": [{"t": i} for i in range(45)] + [1]}
def bundle(**over):
    b = {"day": "2026-03-18", "trade_id": "TRD_20260318_000660_01", "run_id": "r1", "symbol": "000660", "execution": {"symbol": "000660", "action": "BUY"},
         "story_contract": {"story_type": "simulation", "execution_mode_label": "simulation"}, "warnings": ["w1", "", "w2"],
         "scanner_evidence": {"selected": {"symbol": "000660"}}, "artifacts": {}, "commander_summary": {}, "strategist_summary": {}, "scanner_summary": {}, "monitor_summary": {}}
    b.update(over); return b
results = {}
# 1 lifecycle open (no exit evidence) -> HOLD, v2 schema, caps/trim
b = bundle(trade_lifecycle=lifecycle("open")); b0 = copy.deepcopy(b); lc0 = copy.deepcopy(b["trade_lifecycle"])
out = facade.build_trade_story_input(b, trade_lifecycle=b["trade_lifecycle"])
check(out["schema_version"] == "trade_story_input.v2", "v2 schema")
check(out["action"] == "HOLD" and out["status"] == "open", "open -> HOLD")
check(len(out["timeline"]) == 40 and all(isinstance(x, dict) for x in out["timeline"]), "timeline cap 40 / dict only")
check(len(out["holding_summary"]["holding_events"]) == 20, "holding_events cap 20")
check(out["holding_summary"]["run_ids"] == ["r2", "r3"] and out["holding_summary"]["monitor_updates"] == ["u1"], "blank strings trimmed")
check(out["warnings"] == ["w1", "w2"] and out["improvement_points"] == ["i1", "i2"], "warnings/improvements filtered")
check(b == b0 and b["trade_lifecycle"] == lc0, "input State immutable (lifecycle)")
check(out["evidence_source"] in ("canonical", "direct_artifact"), "evidence_source")
check("strategist_feedback_input" in out, "feedback view attached")
results["lifecycle_open"] = (out["action"], out["status"], out["evidence_source"])
# 2 lifecycle closed with exit evidence -> exit action
b = bundle(trade_lifecycle=lifecycle("closed", "SELL", "target hit")); b0 = copy.deepcopy(b)
out2 = facade.build_trade_story_input(b)
check(out2["action"] == "SELL" and out2["status"] == "closed", "closed -> SELL")
check(out2["exit_summary"]["action"] == "SELL" and out2["exit_summary"]["reason_human"] == "target hit", "exit summary")
check(b == b0, "bundle immutable")
# 2b trade_lifecycle kwarg wins over bundle lifecycle; bundle trade_lifecycle_status authoritative
b = bundle(trade_lifecycle=lifecycle("open"), trade_lifecycle_status="closed")
out2b = facade.build_trade_story_input(b, trade_lifecycle=lifecycle("closed", "SELL", "r"))
check(out2b["status"] == "closed" and out2b["action"] == "SELL", "kwarg lifecycle")
# 3 canonical hydration from tmp files (read-only) incl. malformed/non-dict/missing
arts = {"canonical_strategist_json": str(canon / "strategist.json"), "canonical_scanner_json": str(canon / "scanner.json"),
        "canonical_commander_json": str(canon / "commander.json"), "canonical_supervisor_json": str(canon / "supervisor.json"),
        "canonical_executor_json": str(canon / "missing.json"), "canonical_monitor_json": ""}
b = bundle(trade_lifecycle=lifecycle("open"), artifacts=dict(arts)); b0 = copy.deepcopy(b)
out3 = facade.build_trade_story_input(b)
caa = out3["canonical_agent_artifacts"]
check(caa.get("strategist") == {"strategy_horizon": "intraday", "tactical_strategy": "vwap_reclaim_pullback"}, "strategist hydrated")
check("scanner" in caa and "commander" not in caa and "supervisor" not in caa and "executor" not in caa, "malformed/non-dict/missing skipped")
check(caa.get("canonical_strategist_json") == arts["canonical_strategist_json"], "path echoed")
check(out3["strategy_horizon"] == "intraday", "strategy_horizon from canonical strategist")
check(b == b0, "bundle immutable with hydration")
check(out3["artifacts"]["canonical_scanner_json"] == arts["canonical_scanner_json"], "artifacts merged")
# 3b already-present dict wins over file
b = bundle(trade_lifecycle=lifecycle("open"), artifacts=dict(arts), canonical_agent_artifacts={"strategist": {"strategy_horizon": "swing"}})
out3b = facade.build_trade_story_input(b)
check(out3b["canonical_agent_artifacts"]["strategist"] == {"strategy_horizon": "swing"} and out3b["strategy_horizon"] == "swing", "inline canonical wins")
# 4 direct path (no lifecycle)
b = bundle(artifacts=dict(arts)); b0 = copy.deepcopy(b)
out4 = facade.build_trade_story_input(b)
check(out4.get("schema_version") != "trade_story_input.v2", "direct path differs from v2")
check(b == b0, "direct path immutable")
results["direct_schema"] = out4.get("schema_version")
# 5 facade == impl with deps; sibling monitor.json selection
deps = facade._story_assembly_deps()
b = bundle(trade_lifecycle=lifecycle("open"), artifacts=dict(arts))
check(json.dumps(assembly.build_trade_story_input(copy.deepcopy(b), deps=deps), sort_keys=True, default=str) == json.dumps(facade.build_trade_story_input(copy.deepcopy(b)), sort_keys=True, default=str), "facade == impl")
sel = facade._resolve_selection_monitor_artifact(b, {"canonical_scanner_json": str(canon / "scanner.json")})
check(sel.get("scanner_monitor_handoff", {}).get("monitor_selected_symbol") == "000660", "sibling monitor.json selected")
sel2 = facade._resolve_selection_monitor_artifact(bundle(monitor={"x": 1}), {})
check(sel2 == {"x": 1}, "fallback to bundle monitor")
# 6 sub-owner facade pass-throughs
tl = facade.build_timeline(commander={}, market_context_human={}, scanner_reason_human={}, monitor_reason_human={}, guard_reason_human={}, execution_outcome_human={}, reporter_status_human={}, execution={})
check(isinstance(tl, list), "timeline list")
seeds = facade.build_report_section_seeds(market_context_human={}, scanner_reason_human={}, filters_human={})
check(isinstance(seeds, dict), "seeds dict")
w = facade.collect_story_warnings(story_contract={}, market_context_human={}, filters_human={}, reporter_status_human={}, execution_outcome_human={})
check(isinstance(w, list), "warnings list")
cm = facade._compact_canonical_monitor(None); check(isinstance(cm, dict), "compact None")
# 7 exception contract
exc = {}
for name, args, kw in (("bundle_none", (None,), {}), ("bundle_list", ([],), {}), ("lifecycle_entry_str", (bundle(trade_lifecycle={"symbol": "1", "entry": "x", "status": "open"}),), {}),
                       ("artifacts_str", (bundle(artifacts="x"),), {}), ("deps_missing", (bundle(),), {"__impl": True})):
    try:
        if kw.get("__impl"): assembly.build_trade_story_input(*args, deps={})
        else: facade.build_trade_story_input(*args)
        exc[name] = "no_raise"
    except Exception as e: exc[name] = type(e).__name__
check(exc["bundle_none"] == "AttributeError" and exc["deps_missing"] == "KeyError", "exc contract: " + repr(exc))
results["exc"] = exc
check(not bad, "blocked effects attempted: " + repr(bad))
shutil.rmtree(root, ignore_errors=True)
print("RF029_STORY_PIPELINE_ASSEMBLY_OK lifecycle=%s direct=%s hydrated=%d exc=%s write_attempts=0 io=net_sqlite_subprocess_write_blocked debug=%s"
      % ("/".join(results["lifecycle_open"][:2]), results["direct_schema"], len(caa), "/".join(f"{k}:{v}" for k, v in sorted(exc.items())), __debug__))
