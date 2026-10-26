# RF-028: the two branches run 115 left unverified -- `memory_application_surface` and `monitor_snapshot` -- exercised through the REAL producer
# (trade_report_ai.build_deterministic_trade_report) with formal story_input keys, then the real renderer chain. Reads only fixture files under a tmp root;
# every write outside that root is blocked. Run from the repo root: python / python -O.
import os, sys, io, json, copy, re, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = Path(os.getcwd()).resolve(); sys.path.insert(0, str(repo)); sys.dont_write_bytecode = True; sys.stdout.reconfigure(encoding="utf-8")
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PYTEST")): del os.environ[k]
root = Path(tempfile.mkdtemp(prefix="rf028m_")).resolve()
os.environ["EVIDENCE_LEDGER_PATH"] = str(root / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(root / "events.jsonl")
fx = root / "fx"; fx.mkdir()
os.chdir(root)
mod = importlib.import_module("libs.reporting.trade_report_ai")
mclean = importlib.import_module("libs.reporting.trade_report_markdown_clean")
surf = importlib.import_module("libs.reporting.trade_memory_application_surface")
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: return Path(os.path.abspath(str(p))).resolve().is_relative_to(root)
    except Exception: return False
_open = io.open
def gopen(f, mode="r", *a, **k):
    if not isinstance(f, int) and isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen; io.open = gopen
for nm in ("mkdir", "makedirs", "replace", "rename", "remove", "unlink"):
    orig = getattr(os, nm)
    def mk(orig=orig, nm=nm):
        def f(p, *a, **k):
            if not inside(p): bad.append("os." + nm + ":" + str(p)); raise OSError("blocked os." + nm)
            return orig(p, *a, **k)
        return f
    setattr(os, nm, mk())
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def norm(s): return re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(\+00:00|Z)?", "TS", s).replace(str(root), "<ROOT>")

# canonical scanner/monitor artifacts (read-only inputs for the surface builder)
scanner_art = {"scanner_memory_bias_applied": True,
               "scanner_memory_bias_summary": {"enabled": True, "active_layers": ["symbol", "playbook"], "symbol_adjustment_count": 2, "bias_source": "strategy_memory", "reason": ["recent winners"]},
               "scanner_memory_bias": {"source_weight_delta": {"volume": 0.1}, "symbol_adjustments": {"000660": 0.2, "005930": -0.1}, "reason": ["momentum persisted"], "active_layers": ["symbol"]},
               "candidate_memory_bias_adjustments": [{"symbol": "000660", "memory_bias_adjustment": 0.2, "memory_bias_adjustments": [{"kind": "symbol", "source": "memory", "symbol": "000660", "field": "score", "reason": "wins", "delta": 0.2, "from": 1.4, "to": 1.6}]},
                                                     {"symbol": "005930", "memory_bias_adjustment": -0.1}],
               "scanner_memory_application_trace": {"agent": "scanner", "applied": True, "enabled": True, "active_layers": ["symbol", "playbook"], "symbol_adjustment_count": 2, "selected_bias_adjustment": 0.2, "selected_symbol": "000660",
                                                    "selected_bias_adjustments": [{"kind": "symbol", "field": "score", "from": 1.4, "to": 1.6, "delta": 0.2}], "bias_source": "strategy_memory"}}
monitor_art = {"monitor_memory_bias_summary": {"enabled": True, "risk_posture": "defensive", "entry_delta_keys": ["min_confidence"], "bias_source": "strategy_memory", "reason": ["late-day fades"]},
               "monitor_memory_bias": {"entry_policy_delta": {"min_confidence": 0.05}, "active_layers": ["symbol", "playbook", "global"], "reason": ["late-day fades"]},
               "monitor_memory_bias_hold_applied": True, "monitor_memory_bias_exit_applied": True, "effective_policy_source": "memory_overlay",
               "monitor_memory_application_trace": {"agent": "monitor", "entry_applied": True, "hold_applied": True, "exit_applied": True, "applied": True, "enabled": True, "active_layers": ["symbol", "playbook", "global"],
                                                    "entry_deltas": [{"field": "min_confidence", "from": 0.55, "to": 0.6, "delta": 0.05}],
                                                    "hold_deltas": [{"field": "min_hold_sec", "from": 120, "to": 180}],
                                                    "exit_deltas": [{"field": "trailing_stop_pct", "from": 0.012, "to": 0.01}, {"field": "take_profit_pct", "from": 0.025, "to": 0.022}],
                                                    "risk_posture": "defensive", "bias_source": "strategy_memory", "effective_policy_source": "memory_overlay"}}
(fx / "scanner.json").write_text(json.dumps(scanner_art), encoding="utf-8"); (fx / "monitor.json").write_text(json.dumps(monitor_art), encoding="utf-8")
(fx / "list.json").write_text("[1, 2]", encoding="utf-8"); (fx / "broken.json").write_text("{not json", encoding="utf-8")

def story(artifacts=None, with_memory=True, with_monitor=True):
    s = {
        "trade_id": "TRD_20260420_000660_01", "story_id": "TRD_20260420_000660_01", "run_id": "run-7", "day": "2026-04-20", "symbol": "000660",
        "action": "SELL", "status": "closed", "story_type": "simulation", "execution_mode_label": "real broker",
        "scanner_selection_trace": {"ranked_candidates": [{"rank": 1, "symbol": "034020", "score_total": 1.7}, {"rank": 2, "symbol": "000660", "score_total": 1.61}], "selected_symbol": "000660", "selected_rank": 2, "selection_reason": "top_value + sector_theme"},
        "scanner_reason_human": {"selected_symbol": "000660", "selected_rank": 2, "selected_score": 1.61, "playbook": "pullback", "policy_source": "strategist"},
        "entry_summary": {"reason_human": "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation", "price": 70000, "qty": 3, "ts": "2026-04-20T00:05:00+00:00"},
        "exit_summary": {"reason_human": "trailing stop hit", "price": 70100, "qty": 3, "ts": "2026-04-20T00:45:00+00:00"},
        "exit_execution_details": {"filled_price": 70100.0, "broker_realized_pnl": -320.0, "broker_realized_pnl_pct": -0.0064, "broker_fee": 14, "broker_tax": 9, "pnl_truth_source": "kiwoom.ka10077"},
    }
    if with_monitor:
        s["monitor_reason_human"] = {"summary": "Monitor confirmed exit on trailing stop.", "posture": "SELL", "trigger_type": "trailing_stop", "position_age_seconds": 2400, "current_price": 70050.0, "average_price": 70000.0,
                                     "peak_price": 70800.0, "current_drawdown": -0.0107, "peak_drawdown": -0.0107, "vwap_distance": -0.004, "exit_triggered": True, "active_exit_axis": "peak_drawdown", "watch_axes": ["vwap", "peak_drawdown"],
                                     "hard_stop_pct": 0.03, "adaptive_stop_loss_pct": 0.0092, "effective_stop_loss_pct": 0.0092, "effective_stop_reason": "adaptive", "trailing_stop_pct": 0.012, "take_profit_pct": 0.025,
                                     "price_source": "state.minute_ohlcv_by_symbol.close", "feature_source": "minute_ohlcv", "price_source_policy": "close_of_last_minute_bar",
                                     "exit_quant_decision": {"decision": "exit", "score": 0.81}, "quant_factor_snapshot": {"trend_strength": 0.4, "vwap_distance": -0.004}}
        s["monitor_stop_policy_trace"] = {"hard_stop_pct": 0.03, "effective_stop_loss_pct": 0.0092, "trailing_stop_pct": 0.012, "take_profit_pct": 0.025}
        s["monitor_blocker_trace"] = {"entry_check_summary": "mission=wait | reason=reclaim_not_confirmed", "entry_blockers": ["volume_ok"]}
    if with_memory:
        s["reasoning_trace"] = {"commander_summary": {"scanner_memory_bias_summary": {"enabled": True, "active_layers": ["symbol"]}, "monitor_memory_bias_summary": {"enabled": True, "risk_posture": "defensive"},
                                                      "monitor_memory_bias": {"entry_policy_delta": {"min_confidence": 0.05}, "active_layers": ["symbol"]}}}
    if artifacts is not None: s["artifacts"] = artifacts
    return s
arts_ok = {"canonical_scanner_json": str(fx / "scanner.json"), "canonical_monitor_json": str(fx / "monitor.json")}
out = {}
def run(name, st, fatal=False):
    before = copy.deepcopy(st)
    rep = mod.build_deterministic_trade_report(st); check(st == before, name + ": story_input mutated")
    rb = copy.deepcopy(rep)
    md = mod.render_trade_summary_markdown(rep); md2 = mclean.render_trade_summary_markdown_clean(rep)
    check(rep == rb, name + ": report mutated by renderer"); check(md == md2, name + ": facade chains differ")
    return rep, md

# 1. surface builder directly (artifact read-only branches)
sa = surf.build_trade_memory_application_surface(story(arts_ok))
out["surface_full"] = {"status": sa["status"], "scanner": {k: sa["scanner_memory_bias"][k] for k in ("present", "applied", "source", "enabled", "active_layers", "symbol_adjustment_count", "selected_symbol", "selected_bias_adjustment", "bias_source")},
                       "scanner_adjustments": sa["scanner_memory_bias"]["selected_bias_adjustments"],
                       "monitor": {k: sa["monitor_memory_bias"][k] for k in ("present", "applied", "source", "active_layers", "entry_delta_keys", "hold_applied", "exit_applied", "risk_posture", "effective_policy_source", "bias_source")},
                       "monitor_entry": sa["monitor_memory_bias"]["applied_deltas"], "monitor_hold": sa["monitor_memory_bias"]["hold_deltas"], "monitor_exit": sa["monitor_memory_bias"]["exit_deltas"]}
sb = surf.build_trade_memory_application_surface(story(None))
out["surface_reasoning_only"] = {"status": sb["status"], "scanner_source": sb["scanner_memory_bias"]["source"], "monitor_source": sb["monitor_memory_bias"]["source"], "monitor_applied": sb["monitor_memory_bias"]["applied"]}
sc = surf.build_trade_memory_application_surface(story(None, with_memory=False))
out["surface_none"] = sc["status"]
out["surface_nondict_story"] = [surf.build_trade_memory_application_surface(x)["status"]["any_captured"] for x in (None, "x", [1])]
# artifact failure modes: missing / broken JSON -> {}, non-dict JSON -> exception (unguarded)
out["surface_bad_artifacts"] = {}
for nm, p in (("missing", str(fx / "nope.json")), ("broken", str(fx / "broken.json"))):
    out["surface_bad_artifacts"][nm] = surf.build_trade_memory_application_surface(story({"canonical_monitor_json": p}))["status"]["any_captured"]
try: surf.build_trade_memory_application_surface(story({"canonical_monitor_json": str(fx / "list.json")})); out["surface_bad_artifacts"]["list_json"] = "no_raise"
except Exception as e: out["surface_bad_artifacts"]["list_json"] = type(e).__name__
# relative artifact path resolves against cwd (tmp root)
shutil.copy(fx / "monitor.json", root / "rel_monitor.json")
out["surface_relative_path"] = surf.build_trade_memory_application_surface(story({"canonical_monitor_json": "rel_monitor.json"}))["monitor_memory_bias"]["applied"]

# 2. full producer + renderer with the rich branches
rep_rich, md_rich = run("rich", story(arts_ok))
rep_base, md_base = run("base", story(None, with_memory=False, with_monitor=False))
rep_mon, md_mon = run("monitor_only", story(None, with_memory=False))
rep_mem, md_mem = run("memory_only", story(arts_ok, with_monitor=False))
ms = rep_rich["monitor_snapshot"]
out["monitor_snapshot"] = {k: ms.get(k) for k in ("posture", "trigger_type", "position_age_seconds", "hard_stop_pct", "effective_stop_loss_pct", "effective_stop_reason", "trailing_stop_pct", "take_profit_pct", "exit_triggered", "current_price", "average_price", "peak_price", "vwap_distance", "active_exit_axis", "watch_axes", "price_source", "feature_source", "price_source_policy")}
out["monitor_snapshot"]["extra_keys"] = sorted(set(ms) - set(out["monitor_snapshot"]))
out["monitor_snapshot_base"] = {k: rep_base["monitor_snapshot"].get(k) for k in ("posture", "trigger_type", "position_age_seconds", "effective_stop_reason", "price_source", "exit_triggered")}
out["report_memory_surface"] = {"report_matches_direct_builder": rep_rich["memory_application_surface"] == surf.build_trade_memory_application_surface(story(arts_ok)), "any_captured_base": rep_base["memory_application_surface"]["status"]["any_captured"]}
out["len"] = {"rich": len(md_rich), "base": len(md_base), "monitor_only": len(md_mon), "memory_only": len(md_mem)}
markers = {"policy_changes_heading": "### 정책 변화", "min_hold": "min_hold_sec", "trailing": "trailing_stop_pct", "take_profit": "take_profit_pct", "scanner_memory": "스캐너 메모리", "monitor_memory": "모니터 메모리", "layers": "레벨"}
out["markers"] = {n: {"rich": t in md_rich, "base": t in md_base, "monitor_only": t in md_mon, "memory_only": t in md_mem} for n, t in markers.items()}
pd = [l for l in md_rich.splitlines() if l.startswith("* ") and ("→" in l or "메모리" in l)]
out["policy_delta_lines_rich"] = pd
out["monitor_only_vs_base_differs"] = md_mon != md_base
out["memory_only_vs_base_differs"] = md_mem != md_base
out["rich_vs_each_differs"] = [md_rich != md_mon, md_rich != md_mem]
si = mod.build_trade_summary_input(rep_rich)
si_base = mod.build_trade_summary_input(rep_base)
out["summary_input"] = {"keys_equal_rich_base": sorted(si) == sorted(si_base), "changed_keys": sorted(k for k in si if si[k] != si_base.get(k))}
# determinism / use-time patch of the delta renderer dependency is covered by run 114; here: same input twice -> same bytes
check(norm(mod.render_trade_summary_markdown(mod.build_deterministic_trade_report(story(arts_ok)))) == norm(md_rich), "rich not deterministic")
out["deterministic"] = True
# 3. exception boundary through the producer: non-dict artifact JSON
try: mod.build_deterministic_trade_report(story({"canonical_monitor_json": str(fx / "list.json")})); out["producer_list_json"] = "no_raise"
except Exception as e: out["producer_list_json"] = type(e).__name__
# malformed monitor/memory sections inside story_input
mal = {}
for nm, patch in (("monitor_reason_not_dict", {"monitor_reason_human": "x"}), ("reasoning_trace_list", {"reasoning_trace": [1]}), ("position_age_str", {"monitor_reason_human": {"position_age_seconds": "abc"}}),
                  ("watch_axes_str", {"monitor_reason_human": {"watch_axes": "abc"}}), ("commander_summary_none", {"reasoning_trace": {"commander_summary": None}})):
    st = story(None); st.update(patch)
    try: r = mod.build_deterministic_trade_report(st); mod.render_trade_summary_markdown(r); mal[nm] = "ok"
    except Exception as e: mal[nm] = type(e).__name__
out["malformed"] = mal
out["bad"] = bad
check(not bad, "blocked attempts: %r" % bad)
os.chdir(repo)
print("RF028_MEMORY_MONITOR_RICH_OK surface_cases=7 renders=4 malformed=%d blocked=0 debug=%s" % (len(mal), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
shutil.rmtree(root, ignore_errors=True)
