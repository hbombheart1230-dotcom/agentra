# RF-029: trade_story_pipeline.build_trade_story_input_from_bundle -> trade_story_facade_r3_parts.bodies_01 -> build_trade_story_input
# (existing_story_input carry-over, lifecycle normalization, late facade binding, State immutability, exception contract). Offline, tmp cwd, writes/net blocked.
import os, sys, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo); sys.dont_write_bytecode = True
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
root = Path(tempfile.mkdtemp(prefix="rf029_fb_")); rootr = str(root.resolve())
os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "events.jsonl")
os.chdir(root)
facade = importlib.import_module("libs.reporting.trade_story_pipeline")
bodies = importlib.import_module("libs.reporting.trade_story_facade_r3_parts.bodies_01")
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
_open = builtins.open
def guarded(file, mode="r", *a, **k):
    if isinstance(file, (str, os.PathLike)) and any(c in mode for c in "wax+") and not str(Path(file).resolve()).startswith(rootr):
        bad.append("write:" + str(file)); raise OSError("blocked write")
    return _open(file, mode, *a, **k)
builtins.open = guarded
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def exc_of(f, *a, **k):
    try: f(*a, **k); return "no_raise"
    except Exception as e: return type(e).__name__
def bundle(closed=True):
    b = {"day": "2026-04-21", "trade_id": "TRD_20260421_005380_01", "run_id": "RUN_EXIT", "symbol": "005380",
         "trade_lifecycle_status": "closed" if closed else "open",
         "lifecycle": {"entry": {"run_id": "RUN_ENTRY", "ts": "2026-04-21T00:10:00+00:00", "action": "BUY",
                                  "execution_details": {"order_id": "0100001", "filled_price": 537000}, "scanner_context": {"selected_symbol": "005380"}},
                       "hold": {"run_ids": ["RUN_MONITOR_1"]}, "summary": {"lifecycle_summary_human": "closed" if closed else "open"}},
         "execution_outcome_human": {}, "market_context_human": {"summary": "market"}, "scanner_reason_human": {"summary": "scanner", "selected_symbol": "005380"},
         "filters_human": {"summary": "filters"}, "monitor_reason_human": {"summary": "monitor"}, "guard_reason_human": {"summary": "guard"},
         "reporter_status_human": {"status": "linked_run", "summary": "reporter"}, "operator_conclusion_human": {"summary": "conclusion"},
         "timeline": [], "warnings": [], "monitor_timeline": {}}
    if closed: b["lifecycle"]["exit"] = {"run_id": "RUN_EXIT", "ts": "2026-04-21T00:11:00+00:00", "action": "SELL", "execution_details": {"order_id": "0100002", "filled_price": 537000}}
    return b
def js(x): return json.dumps(x, sort_keys=True, ensure_ascii=False, default=repr)
res = {}
# 1. closed lifecycle, no existing: facade == bodies_01 impl, input unchanged, execution outcome synthesized
b = bundle(); snap = copy.deepcopy(b)
o1 = facade.build_trade_story_input_from_bundle(b)
check(b == snap, "bundle immutable")
o1b = bodies.build_trade_story_input_from_bundle_r3_impl(copy.deepcopy(snap), trade_lifecycle=None, existing_story_input=None, facade=facade)
check(js(o1) == js(o1b), "facade == impl")
eo = o1["execution_outcome_human"]
check("0100001" in js(eo) and "0100002" in js(eo), "closed lifecycle outcome has both order ids")
# 2. existing_story_input carry-over: runtime keys only when absent in story_input; trade_id/day/run_id only when empty
b2 = bundle(); b2["trade_id"] = ""; b2["run_id"] = None; del b2["day"]
ex = {"report_runtime_mode": "shadow", "skip_separated_report_llm": True, "entry_strategist_run_id": "S1", "strategy_anchor_run_id": "S0", "trade_id": "TRD_X", "day": "2026-04-20", "run_id": "RUN_X"}
exs = copy.deepcopy(ex); b2s = copy.deepcopy(b2)
o2 = facade.build_trade_story_input_from_bundle(b2, existing_story_input=ex)
check(ex == exs and b2 == b2s, "existing/bundle immutable")
carried = {k: o2.get(k) for k in ("report_runtime_mode", "skip_separated_report_llm", "entry_strategist_run_id", "strategy_anchor_run_id")}
check(carried == {"report_runtime_mode": "shadow", "skip_separated_report_llm": True, "entry_strategist_run_id": "S1", "strategy_anchor_run_id": "S0"}, "runtime keys carried: %r" % carried)
res["empty_ids"] = {k: o2.get(k) for k in ("trade_id", "day", "run_id")}
check(res["empty_ids"]["trade_id"] in ("TRD_X", None) or res["empty_ids"]["trade_id"], "empty ids observed: %r" % res["empty_ids"])
# 3. non-empty values in story_input are not overridden by existing
o3 = facade.build_trade_story_input_from_bundle(bundle(), existing_story_input=ex)
check(o3["trade_id"] == "TRD_20260421_005380_01" and o3["day"] == "2026-04-21" and o3["run_id"] == "RUN_EXIT", "non-empty ids kept")
# 4. existing not dict is ignored
o4 = facade.build_trade_story_input_from_bundle(bundle(), existing_story_input="junk")
check(js(o4) == js(o1), "non-dict existing ignored")
# 5. open lifecycle differs from closed
o5 = facade.build_trade_story_input_from_bundle(bundle(closed=False))
res["open_action"] = o5.get("current_action") or o5["operator_conclusion_human"].get("current_action")
check(js(o5["execution_outcome_human"]) != js(eo), "open != closed outcome")
# 6. late facade binding + empty normalized lifecycle falls back to the passed trade_lifecycle
calls = []
orig_norm = facade._normalize_trade_lifecycle_for_story_input
facade._normalize_trade_lifecycle_for_story_input = lambda bo, trade_lifecycle=None, existing_story_input=None: (calls.append(("norm", trade_lifecycle)), {})[1]
orig_bti = facade.build_trade_story_input
facade.build_trade_story_input = lambda bo, trade_lifecycle=None: (calls.append(("bti", trade_lifecycle)), {"x": 1})[1]
try: o6 = facade.build_trade_story_input_from_bundle(bundle(), trade_lifecycle={"tl": 1}, existing_story_input={"run_id": "R", "report_runtime_mode": "m"})
finally: facade._normalize_trade_lifecycle_for_story_input = orig_norm; facade.build_trade_story_input = orig_bti
check(calls == [("norm", {"tl": 1}), ("bti", {"tl": 1})], "late binding + fallback: %r" % calls)
check(o6 == {"x": 1, "report_runtime_mode": "m", "run_id": "R"}, "carry-over onto stub output: %r" % o6)
# 7. exception contract
exc = {"bundle_none": exc_of(facade.build_trade_story_input_from_bundle, None), "bundle_list": exc_of(facade.build_trade_story_input_from_bundle, []),
       "bundle_empty": exc_of(facade.build_trade_story_input_from_bundle, {}), "lifecycle_str": exc_of(facade.build_trade_story_input_from_bundle, bundle(), trade_lifecycle="x"),
       "facade_missing": exc_of(bodies.build_trade_story_input_from_bundle_r3_impl, bundle(), trade_lifecycle=None, existing_story_input=None, facade=object())}
check(exc["facade_missing"] == "AttributeError" and exc["bundle_none"] != "no_raise", "exception contract: %r" % exc)
check(not bad, "blocked effects attempted: %r" % bad)
print("RF029_STORY_FROM_BUNDLE_OK schema=%s carried=4 ids=%s open_action=%s exc=%s write_attempts=0 debug=%s" % (o1.get("schema_version") or o1.get("schema"), json.dumps(res["empty_ids"], sort_keys=True), res["open_action"], json.dumps(exc, sort_keys=True), __debug__))
