# Offline owner-boundary checks for RF-029 read_display_context + read_truth_projection (synthetic tmp-only, no network).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf029_dp_")).resolve()
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt, _mk = Path.write_text, Path.mkdir
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked")
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked")
    return _mk(self, *a, **k)
Path.write_text, Path.mkdir = wt, mk
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)
def tree(root):
    return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())

facade = importlib.import_module("libs.reporting.trade_read_model")
dc = importlib.import_module("libs.reporting.trade_read_model_parts.read_display_context")
tp = importlib.import_module("libs.reporting.trade_read_model_parts.read_truth_projection")

# helpers copied verbatim from the build_trade_read_model closures (the orchestrator passes these in)
def _clip(s, max_len=255):
    t = str(s or "").strip()
    return "unknown" if (not t or t.lower() in ("none", "null", "unavailable", "nan")) else t[:max_len]
def _meaningful(v):
    t = str(v or "").strip().lower()
    return bool(t and t not in {"unknown", "none", "null", "unavailable", "nan"})
def _pick(c, *, default="unknown"):
    for k, raw in c:
        cl = _clip(raw)
        if _meaningful(cl): return cl, k
    return str(default), "default"
def _sf(v, default=0.0):
    try: return float(v)
    except Exception: return float(default)
def _trim(v, max_len=255): return str(v or "").strip()[:max_len]
def _cl(v, *, limit=6, max_len=220):
    out = []
    if not isinstance(v, list): return out
    for i in v[:limit]:
        t = str(i or "").strip()
        if t: out.append(t[:max_len])
    return out
def exc(f):
    try: f(); return "no_raise"
    except Exception as e: return type(e).__name__
out = {}

# ---- read_truth_projection ----
existing = tmp / "life.json"; existing.write_text("{}", encoding="utf-8")
missing = tmp / "nope.json"; sameday = tmp / "sameday.json"; sameday.write_text("{}", encoding="utf-8")
def truth(**o):
    a = dict(hold_duration_sec=-5, _pick_with_source=_pick, exit_obj={}, shared_facts={}, bundle={}, report_data={}, entry_obj={}, monitor_art={}, scanner_art={}, strategist_art={}, commander_art={}, lifecycle={}, executor_art={}, entry_ts="unknown", exit_ts="unknown", _safe_float=_sf, report={}, artifacts={}, _clip=_clip, same_day_linkage={}, story_meta={}, evidence_provenance={}, entry_ts_source="default", exit_ts_source="default", hold_duration_source="default", td=tmp / "td", lifecycle_path_used=missing, report_path_used=missing, canonical={}, facade=facade)
    a.update(o)
    r = tp.read_truth_blocker_trace_data_source_quality(**a)
    names = "blocker_trace dsq exec_label facts exit_trigger playbook prov sd_reason sd_status stop_trace strat_src thresholds watch_axes".split()
    check(len(r) == len(names), "13-tuple")
    return dict(zip(names, r))
before = tree(tmp)
e = truth()
check(e["facts"]["hold_duration_sec"] == 0 and e["facts"]["pnl"] == 0.0 and e["facts"]["trade_id"] == "unknown" and e["facts"]["data_source"] == "unknown", "empty defaults (negative hold clamped to 0)")
check(e["sd_status"] == "missing" and e["sd_reason"] == "Same-day reporter linkage was not captured.", "same-day defaults")
check(e["prov"]["paths"]["lifecycle_bundle_json"] == "" and e["dsq"] == {"has_lifecycle_bundle": False, "has_ai_trade_report": False, "has_canonical_artifacts": False, "has_evidence_provenance": False, "same_day_reporter_found": False}, "empty dsq/paths")
check(e["facts"]["primary_blocker_if_no_buy"] == "unknown" and e["prov"]["field_sources"]["primary_blocker_if_no_buy"] == "default", "blocker default")
check(e["exit_trigger"] == "unknown" and e["thresholds"] == {} and e["watch_axes"] == [] and e["prov"]["field_sources"]["pnl"] == "default", "empty trace defaults")
e = truth(exit_obj={"pnl": "12.5", "pnl_pct": "None", "reason": "tp", "monitor_reason": "m", "reason_human": "h"}, shared_facts={"pnl": "99", "pnl_pct": "3.5"},
          bundle={"story_id": "S1", "symbol": "005930", "evidence_recovery_used": False}, report_data={"trade_id": "T9", "symbol": "ZZZ", "evidence_recovery_used": True, "status": "closed"},
          entry_obj={"reason": "r", "strategist_context": {"playbook": "pb_ctx"}}, strategist_art={"playbook": "pb_can", "policy_source": "ps"}, commander_art={"applied_policy_source": "cmd"}, monitor_art={"policy_source": "mon"},
          lifecycle={"status": "open"}, executor_art={"final_execution_status": "filled"})
f, fs = e["facts"], e["prov"]["field_sources"]
check(f["pnl"] == 12.5 and fs["pnl"] == "lifecycle.exit.pnl" and f["pnl_pct"] == 3.5 and fs["pnl_pct"] == "ai_trade_report.shared_facts.pnl_pct", "pnl precedence / 'None' skipped")
check(f["trade_id"] == "S1" and fs["trade_id"] == "lifecycle_bundle.story_id" and f["symbol"] == "005930", "trade_id/symbol precedence")
check(f["playbook"] == "pb_can" and f["exit_reason"] == "tp" and f["entry_reason"] == "r", "playbook/reason precedence")
check(f["applied_policy_source"] == "cmd" and f["strategy_policy_source"] == "ps" and f["execution_label"] == "open" and fs["execution_label"] == "lifecycle.status", "policy/execution label")
check(f["data_source"] == "lifecycle_bundle" and f["evidence_recovery_used"] is True and fs["evidence_recovery_used"] == "lifecycle_bundle.evidence_recovery_used", "evidence_recovery is OR of bundle/report_data; source label follows bundle presence")
check(f["primary_blocker_if_no_buy"] == "unknown", "entry_obj present -> no blocker lookup")
e = truth(monitor_art={"dominant_blocker": "DB"}, scanner_art={"dominant_block_reason": "SB"}, report_data={"missing_reason": "MR"})
check(e["facts"]["primary_blocker_if_no_buy"] == "DB" and e["prov"]["field_sources"]["primary_blocker_if_no_buy"] == "canonical.monitor.dominant_blocker", "blocker chain")
e = truth(report={"x": 1}, hold_duration_sec=77, artifacts={"canonical_commander_json": "A", "canonical_scanner_json": ""}, bundle={"canonical_scanner_json": "B"}, canonical={"k": 1})
check(e["facts"]["data_source"] == "lifecycle_bundle" and e["facts"]["hold_duration_sec"] == 77 and e["dsq"]["has_canonical_artifacts"] is True, "bundle wins data_source over report")
check(truth(report={"x": 1})["facts"]["data_source"] == "ai_trade_report", "report-only data_source")
cp = e["prov"]["canonical_artifact_paths"]
check(cp["canonical_commander_json"] == "A" and cp["canonical_scanner_json"] == "B" and cp["canonical_monitor_json"] == "" and len(cp) == 6, "canonical paths fall back to bundle")
e = truth(same_day_linkage={"status": "FOUND", "analysis_path": str(sameday), "expected_path": "", "fallback_expected_path": "fb"}, lifecycle_path_used=existing)
check(e["sd_status"] == "FOUND" and e["prov"]["same_day_reporter_linkage"]["file_found"] is True and e["prov"]["same_day_reporter_linkage"]["expected_path"] == "fb", "same-day file exists -> found (only Path.exists IO)")
check(e["prov"]["paths"]["lifecycle_bundle_json"] == str(existing) and e["dsq"]["same_day_reporter_found"] is True, "existing path exposed")
e = truth(same_day_linkage={"analysis_path": str(missing), "file_found": True}, story_meta={"same_day_reporter_linkage_status": "SM"})
check(e["prov"]["same_day_reporter_linkage"]["file_found"] is True and e["sd_status"] == "SM", "file_found flag preserved when path missing; story_meta status fallback")
e = truth(monitor_art={"monitor_stop_policy_trace": {"watch_axes": ["a", "b"], "active_exit_axis": "AX"}, "monitor_blocker_trace": [1], "effective_stop_loss_pct": -3, "confirm_count": 0, "take_profit_pct": None})
check(e["watch_axes"] == ["a", "b"] and e["blocker_trace"] == {} and e["thresholds"] == {"effective_stop_loss_pct": -3, "confirm_count": 0} and e["exit_trigger"] == "AX", "trace fallbacks; None filtered, 0 kept")
e = truth(monitor_art={"watch_axes": "str", "thresholds_snapshot": {"t": 1}, "trigger_type": "TT"}, exit_obj={"reason": "R"})
check(e["watch_axes"] == [] and e["thresholds"] == {"t": 1} and e["exit_trigger"] == "TT", "non-list watch_axes -> []")
check(tree(tmp) == tree(tmp) and set(p for p, _ in tree(tmp)) == set(p for p, _ in before), "truth projection created no files")
out["exc_hold_str"] = exc(lambda: truth(hold_duration_sec="5"))
out["exc_exit_obj_none"] = exc(lambda: truth(exit_obj=None))
out["exc_artifacts_none"] = exc(lambda: truth(artifacts=None))
out["exc_lifecycle_path_str"] = exc(lambda: truth(lifecycle_path_used="x"))
check(out["exc_hold_str"] == "TypeError" and out["exc_exit_obj_none"] == "AttributeError" and out["exc_artifacts_none"] == "AttributeError" and out["exc_lifecycle_path_str"] == "AttributeError", "no fail-soft on wrong types")

# ---- read_display_context ----
def disp(**o):
    a = dict(report_data={}, _trim_text=_trim, _clean_str_list=_cl, entry_obj={}, scanner_reason_human={}, monitor_reason_human={}, filters_human={}, market_context_human={}, bundle={}, lifecycle={}, holding_obj={}, monitor_exit_trigger="mx", thresholds_snapshot={"a": 1}, stop_policy_trace={}, blocker_trace={}, same_day_status="ss", same_day_reason="sr", data_source_quality={"q": 1}, _clip=_clip, playbook_value="pb", strategy_policy_source_value="sp", execution_label_value="el", watch_axes=[], scanner_art={}, executor_art={}, monitor_art={}, facade=facade)
    a.update(o)
    r = dc.read_display_context(**a)
    check(isinstance(r, tuple) and len(r) == 1, "1-tuple")
    return r[0]
c = disp()
check(c["scanner_selection_summary"] == "unknown" and c["monitor_primary_blocker"] == "unknown" and c["scanner"]["top_candidates"] == [] and c["scanner_score_drivers"] == {}, "empty ctx")
check(len(c["report_section_seeds"]) == 11 and all(set(v) == {"summary", "bullets", "status", "grade", "current_action", "watch_next", "thesis_invalidation"} for v in c["report_section_seeds"].values()), "11 seeds x 7 keys")
check(c["report_section_seeds"]["exit_decision"]["summary"] == "" and c["strategist"]["themes"] == [], "empty exit seed")
c = disp(report_data={"entry_decision": {"summary": "RS", "bullets": ["x"] * 20, "status": "S" * 100}}, entry_obj={"reason_human": "RH"}, scanner_reason_human={"summary": "SC"})
sd = c["report_section_seeds"]["entry_decision"]
check(sd["summary"] == "RS" and len(sd["bullets"]) == 12 and len(sd["status"]) == 64 and c["report_section_seeds"]["why_this_symbol_was_chosen"]["summary"] == "RH", "report_data wins; truncation limits")
c = disp(lifecycle={"status": "OPEN"})
check(c["report_section_seeds"]["exit_decision"]["summary"].startswith("Position is still open"), "open fallback (case-insensitive)")
c = disp(lifecycle={"exit": {"reason_human": "LX"}, "status": "open"}, bundle={"execution_outcome_human": {"summary": "EO"}}, monitor_reason_human={"summary": "MR"})
check(c["report_section_seeds"]["exit_decision"]["summary"] == "LX" and c["report_section_seeds"]["execution_quality"]["summary"] == "EO" and c["report_section_seeds"]["holding_monitoring_story"]["summary"] == "MR", "exit chain / human summaries")
c = disp(lifecycle={"exit": "notmap"}, bundle={"execution_outcome_human": "str"})
check(c["report_section_seeds"]["exit_decision"]["summary"] == "" and c["report_section_seeds"]["execution_quality"]["summary"] == "", "non-dict exit/human ignored")
c = disp(holding_obj={"run_ids": [1, 2, 3]})
check(c["report_section_seeds"]["holding_monitoring_story"]["summary"] == "Holding phase captured 3 runs.", "holding runs text")
c = disp(entry_obj={"strategist_context": {"themes": ["t"], "market_context_summary": "MCS"}}, market_context_human={"summary": "MH"})
check(c["report_section_seeds"]["market_context_at_entry"]["summary"] == "MCS" and c["strategist"]["themes"] == ["t"] and c["strategist"]["market_context_summary"] == "MCS", "strategist_context precedence")
c = disp(entry_obj={"strategist_context": {}}, market_context_human={"summary": "MH"})
check(c["report_section_seeds"]["market_context_at_entry"]["summary"] == "" and c["strategist"]["market_context_summary"] == "unknown", "empty strategist_context dict suppresses market_context_human")
c = disp(entry_obj={"strategist_context": {"themes": "notlist"}})
check(c["strategist"]["themes"] == [], "non-list themes -> []")
c = disp(scanner_art={"top_candidates": list(range(9)), "selected_symbol_score_drivers": {"d": 1}, "selection_reason": "SR"}, monitor_art={"decision_summary": "DS", "dominant_blocker": "DBL"}, executor_art={"execution_details": {"e": 1}}, watch_axes=list(range(12)))
check(c["scanner"]["top_candidates"] == [0, 1, 2, 3, 4] and c["scanner_selection_summary"] == "SR" and c["monitor"]["entry_reason"] == "DS" and c["monitor"]["primary_blocker"] == "DBL" and c["executor"]["execution_details"] == {"e": 1} and len(c["watch_axes"]) == 8, "caps/fallbacks")
c = disp(scanner_art={"top_candidates": "x", "ranked_candidates": [1, 2]}, executor_art={"execution_details": "x"})
check(c["scanner"]["top_candidates"] == [1, 2] and c["executor"]["execution_details"] == {}, "ranked_candidates fallback; non-dict details")
th = {"a": 1}; c = disp(thresholds_snapshot=th)
check(c["thresholds_snapshot"] is th and c["monitor"]["thresholds_snapshot"] is th, "thresholds aliased, not copied")
out["exc_entry_none"] = exc(lambda: disp(entry_obj=None))
out["exc_scanner_none"] = exc(lambda: disp(scanner_art=None))
out["exc_report_none"] = exc(lambda: disp(report_data=None))
out["exc_watch_none"] = exc(lambda: disp(watch_axes=None))
out["exc_facade_obj"] = exc(lambda: disp(facade=object()))
check(out["exc_entry_none"] == "AttributeError" and out["exc_report_none"] == "AttributeError" and out["exc_watch_none"] == "TypeError" and out["exc_facade_obj"] == "AttributeError", "exceptions propagate")

# ---- real consumer: build_trade_read_model on a synthetic tmp trade dir (read-only) ----
td = tmp / "trade_001"; td.mkdir()
(td / "lifecycle_bundle.json").write_text(json.dumps({"trade_id": "T1", "symbol": "005930"}), encoding="utf-8")
tb = tree(td)
rm = facade.build_trade_read_model(str(td))
check(tree(td) == tb, "consumer read-only")
check(isinstance(rm, dict) and "context" in rm, "consumer exposes context")
check(rm["context"]["strategist"]["playbook"] == rm["facts"]["playbook"] and rm["context"]["executor"]["execution_label"] == rm["facts"]["execution_label"], "consumer wiring truth -> display")
check(rm["provenance"]["schema_version"] == "trade_read_model.v2" and rm["context"]["data_source_quality"] == {k: v for k, v in rm["context"]["data_source_quality"].items()}, "consumer provenance")
rm2 = facade.build_trade_read_model(str(tmp / "no_such_dir"))
miss = (rm2["facts"]["data_source"], rm2["context"]["data_source_quality"]["has_lifecycle_bundle"])
check(miss[1] is False, "missing dir fail-soft")
check(not bad, "blocked operations attempted: %s" % bad)
sha = hashlib.sha1(b"".join(Path(p).read_bytes() for p in ("libs/reporting/trade_read_model_parts/read_display_context.py", "libs/reporting/trade_read_model_parts/read_truth_projection.py"))).hexdigest()[:8]
print("RF029_DISPLAY_PROJECTION_OK truth=14 display=15 seeds=11 consumer=ok missing_dir=%s/%s exc=%s writes_outside=0 blocked=%d debug=%s srcsha=%s" % (miss[0], miss[1], "/".join(out[k] for k in sorted(out)), len(bad), __debug__, sha))
