# RF-029: read_truth_projection.read_truth_blocker_trace_data_source_quality -- external-root `facade.Path(...).exists()` consumer,
# polluted/odd paths, field-source precedence, State immutability. tmp read-only; Path.exists is counted, every write/network/subprocess is blocked.
import os, sys, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile, types
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.trade_read_model_parts.read_truth_projection")
fn = mod.read_truth_blocker_trace_data_source_quality
root = Path(tempfile.mkdtemp(prefix="rf029_ext_")); ext = root / "external"; ext.mkdir(); (ext / "analysis.json").write_text("{}", encoding="utf-8")
os.chdir(root)
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
def attempt(f, *a, **k):
    try: return f(*a, **k), None
    except Exception as e: return None, type(e).__name__
def clip(s, n=255):
    t = str(s or "").strip()
    return "unknown" if not t or t.lower() in ("none", "null", "unavailable", "nan") else t[:n]
def pick(c, *, default="unknown"):
    for key, raw in c:
        v = clip(raw)
        if v != "unknown": return v, key
    return str(default), "default"
def sf(v, d=0.0):
    try: return float(v)
    except Exception: return float(d)
exists_calls = []
class SpyPath(type(Path())):
    def exists(self, *a, **k):
        exists_calls.append(str(self)); return super().exists(*a, **k)
facade = types.SimpleNamespace(Path=SpyPath)
def call(**over):
    kw = dict(hold_duration_sec=-5, _pick_with_source=pick, exit_obj={}, shared_facts={}, bundle={}, report_data={}, entry_obj={}, monitor_art={}, scanner_art={}, strategist_art={},
              commander_art={}, lifecycle={}, executor_art={}, entry_ts="", exit_ts="", _safe_float=sf, report={}, artifacts={}, _clip=clip, same_day_linkage={}, story_meta={}, evidence_provenance={},
              entry_ts_source="s", exit_ts_source="s", hold_duration_source="s", td=root / "trade", lifecycle_path_used=root / "nope_l.json", report_path_used=root / "nope_r.json", canonical={}, facade=facade)
    kw.update(over); snap = {k: copy.deepcopy(v) for k, v in kw.items() if isinstance(v, (dict, list))}
    r, e = attempt(fn, **kw)
    check(all(kw[k] == v for k, v in snap.items()), "input mutated")
    return r, e
IDX = dict(blocker_trace=0, dsq=1, exec_label=2, facts=3, exit_trigger=4, playbook=5, prov=6, reason=7, status=8, stop=9, strat_src=10, thr=11, axes=12)
out = {}
# 1 external root exists
r, e = call(same_day_linkage={"analysis_path": str(ext / "analysis.json"), "status": "found"}); check(e is None and len(r) == 13, e)
check(r[IDX["dsq"]]["same_day_reporter_found"] is True and r[IDX["prov"]]["same_day_reporter_linkage"]["file_found"] is True, "ext exists -> found")
check(r[IDX["prov"]]["same_day_reporter_linkage"]["analysis_path"] == str(ext / "analysis.json") and str(ext / "analysis.json") in exists_calls, "exists consulted on ext path")
# 2 missing, linkage flag trusted, artifact_path alias
r, _ = call(same_day_linkage={"artifact_path": str(ext / "missing.json"), "file_found": True}); check(r[IDX["dsq"]]["same_day_reporter_found"] is True, "file_found flag wins without file")
r, _ = call(same_day_linkage={"artifact_path": str(ext / "missing.json")}); check(r[IDX["dsq"]]["same_day_reporter_found"] is False, "missing -> False")
r, _ = call(same_day_linkage={"artifact_path": str(ext / "analysis.json")}); check(r[IDX["dsq"]]["same_day_reporter_found"] is True, "artifact_path alias consulted")
# 3 directory path counts as exists (observed), polluted strings
r, _ = call(same_day_linkage={"analysis_path": str(ext)}); out["dir_counts_exists"] = r[IDX["dsq"]]["same_day_reporter_found"]
check(out["dir_counts_exists"] is True, "directory path counts as found (BASE behaviour)")
polluted = {"nul": "bad\x00path", "dotdot": str(ext / ".." / "external" / "analysis.json"), "empty_ws": "   ", "tilde": "~/definitely_missing_rf029.json", "long": "x" * 5000}
pol = {}
for n, p in polluted.items():
    r, e = call(same_day_linkage={"analysis_path": p}); pol[n] = (e, None if r is None else r[IDX["dsq"]]["same_day_reporter_found"])
check(pol["dotdot"] == (None, True) and pol["empty_ws"] == (None, False) and pol["tilde"] == (None, False), pol)
check(all(v[0] in (None, "ValueError", "OSError") for v in pol.values()), pol)
out["polluted"] = pol
# 4 expected_path never probed (no exists on it), fallbacks
before = len(exists_calls)
r, _ = call(same_day_linkage={"fallback_expected_path": str(ext / "analysis.json")}); check(len(exists_calls) == before and r[IDX["prov"]]["same_day_reporter_linkage"]["expected_path"] == str(ext / "analysis.json") and r[IDX["dsq"]]["same_day_reporter_found"] is False, "expected_path not probed")
r, _ = call(story_meta={"same_day_reporter_linkage_status": "pending", "same_day_reporter_linkage_reason": "r", "same_day_reporter_expected_path": "E"}); lk = r[IDX["prov"]]["same_day_reporter_linkage"]
check((lk["status"], lk["reason"], lk["expected_path"]) == ("pending", "r", "E"), lk)
r, _ = call(); lk = r[IDX["prov"]]["same_day_reporter_linkage"]; check(lk["status"] == "missing" and "not captured" in lk["reason"], lk)
# 5 lifecycle/report path exists -> strings
lp = ext / "life.json"; lp.write_text("{}", encoding="utf-8")
r, _ = call(lifecycle_path_used=lp); check(r[IDX["prov"]]["paths"]["lifecycle_bundle_json"] == str(lp) and r[IDX["prov"]]["paths"]["ai_trade_report_json"] == "", "path existence strings")
r, e = call(lifecycle_path_used="notapath"); out["str_lifecycle_path"] = e; check(e == "AttributeError", "non-Path lifecycle_path_used -> AttributeError")
r, e = call(same_day_linkage={"analysis_path": 123}); out["int_path"] = (e, None if r is None else r[IDX["dsq"]]["same_day_reporter_found"]); check(out["int_path"][0] is None, "int analysis_path coerced via str")
# 6 precedence, defaults, data_source
r, _ = call(exit_obj={"pnl": "5.5", "pnl_pct": "0.02", "reason": "R", "monitor_reason": "M"}, shared_facts={"pnl": "9"}, bundle={"trade_id": "T1", "symbol": "S1"}, entry_obj={"reason": "ER"},
            strategist_art={"playbook": "pb", "policy_source": "ps"}, commander_art={"applied_policy_source": "cps"}, lifecycle={"status": "closed"}, hold_duration_sec=30)
f = r[IDX["facts"]]; check(f["pnl"] == 5.5 and f["pnl_pct"] == 0.02 and f["trade_id"] == "T1" and f["playbook"] == "pb" and f["applied_policy_source"] == "cps" and f["execution_label"] == "closed" and f["data_source"] == "lifecycle_bundle", f)
fs = r[IDX["prov"]]["field_sources"]; check(fs["pnl"] == "lifecycle.exit.pnl" and fs["trade_id"] == "lifecycle_bundle.trade_id" and fs["data_source"] == "derived.presence_check", fs)
r, _ = call(exit_obj={"pnl": None}, shared_facts={"pnl": "7"}); check(r[IDX["facts"]]["pnl"] == 7.0 and r[IDX["prov"]]["field_sources"]["pnl"] == "ai_trade_report.shared_facts.pnl", "falls to shared_facts")
r, _ = call(); f = r[IDX["facts"]]; check(f["hold_duration_sec"] == 0 and f["pnl"] == 0.0 and f["trade_id"] == "unknown" and f["data_source"] == "unknown", "negative hold clamps to 0; defaults")
r, _ = call(report={"x": 1}); check(r[IDX["facts"]]["data_source"] == "ai_trade_report", "report-only data_source")
r, _ = call(exit_obj={"pnl": "garbage"}); check(r[IDX["facts"]]["pnl"] == 0.0, "unparseable pnl -> 0.0 via _safe_float")
# 7 primary blocker only when no entry
r, _ = call(monitor_art={"primary_reason_code": "MON"}, scanner_art={"dominant_block_reason": "SCN"}); check(r[IDX["facts"]]["primary_blocker_if_no_buy"] == "MON", "no entry -> monitor code")
r, _ = call(entry_obj={"reason": "x"}, monitor_art={"primary_reason_code": "MON"}); check(r[IDX["facts"]]["primary_blocker_if_no_buy"] == "unknown" and r[IDX["prov"]]["field_sources"]["primary_blocker_if_no_buy"] == "default", "entry present -> blocker unknown")
# 8 monitor derived values
r, _ = call(monitor_art={"monitor_stop_policy_trace": {"watch_axes": ["a"], "active_exit_axis": "AX"}, "effective_stop_loss_pct": 0.01, "confirm_required": 3, "take_profit_pct": None})
check(r[IDX["axes"]] == ["a"] and r[IDX["thr"]] == {"effective_stop_loss_pct": 0.01, "confirm_required": 3} and r[IDX["exit_trigger"]] == "AX", (r[IDX["axes"]], r[IDX["thr"]], r[IDX["exit_trigger"]]))
r, _ = call(monitor_art={"monitor_stop_policy_trace": "bad", "monitor_blocker_trace": [1], "watch_axes": "nolist", "thresholds_snapshot": {"k": 1}}, exit_obj={"monitor_reason": "MR"})
check(r[IDX["stop"]] == {} and r[IDX["blocker_trace"]] == {} and r[IDX["axes"]] == [] and r[IDX["thr"]] == {"k": 1} and r[IDX["exit_trigger"]] == "MR", "non-dict traces -> {}")
r, _ = call(artifacts={"canonical_commander_json": "A"}, bundle={"canonical_executor_json": "B"}); cp = r[IDX["prov"]]["canonical_artifact_paths"]; check(cp["canonical_commander_json"] == "A" and cp["canonical_executor_json"] == "B" and cp["canonical_scanner_json"] == "", cp)
# 9 exceptions: bad inputs / state
exc = {}
for n, ov in {"exit_obj_none": dict(exit_obj=None), "bundle_none": dict(bundle=None), "same_day_none": dict(same_day_linkage=None), "story_meta_none": dict(story_meta=None), "hold_none": dict(hold_duration_sec=None), "facade_missing": dict(facade=types.SimpleNamespace())}.items():
    exc[n] = call(**ov)[1]
check(exc["exit_obj_none"] == "AttributeError" and exc["hold_none"] == "TypeError", exc)
check(exc["facade_missing"] in (None, "AttributeError"), exc)
out["exc"] = exc
check(not bad, "blocked attempts %s" % bad)
files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()); check(files == ["external/analysis.json", "external/life.json"], files)
shutil.rmtree(root, ignore_errors=True)
print("RF029_TRUTH_PROJECTION_EXTROOT_OK exists_calls=%d dir_counts_exists=%s polluted=%s str_lifecycle_path=%s int_path=%s exc=%s write_attempts=0 debug=%s" % (len(exists_calls), out["dir_counts_exists"], out["polluted"], out["str_lifecycle_path"], out["int_path"], out["exc"], __debug__))
