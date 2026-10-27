# RL32-REPORT (RunLab #32) A read-only + temp-fake trace: why can Reporter/Operator show trade_index=[], no realised samples and GREEN health
# while the broker had a BUY+SELL round trip? Synthetic events only (BUY executed locally, SELL missing locally -- the RL32-ORDER symptom), tmp roots,
# network/subprocess/sqlite blocked, writes confined to tmp. No RunLab data, no protected code touched. Usage: (cd <repo>; python [-O] rl32_report_trace.py)
import os, sys, io, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, shutil, contextlib
from pathlib import Path
repo = Path(os.getcwd()).resolve(); sys.path.insert(0, str(repo))
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY", "EVENT_LOG", "EVIDENCE", "INTRADAY_TRADE", "OPERATOR_UI")): del os.environ[k]
tmp = Path(tempfile.mkdtemp(prefix="rl32_")).resolve(); os.chdir(tmp)
os.environ["EVENT_LOG_PATH"] = str(tmp / "data/logs/events.jsonl"); os.environ["EVIDENCE_LEDGER_PATH"] = str(tmp / "data/evidence_ledger/events.jsonl"); os.environ["ENV_PATH"] = str(tmp / ".env.absent")
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
def inside(p):
    try:
        if isinstance(p, int): return True
        ap = os.path.abspath(os.fspath(p)); return ap == str(tmp) or ap.startswith(str(tmp) + os.sep)
    except Exception: return False
_open = io.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write outside tmp")
    return _open(f, mode, *a, **k)
builtins.open = gopen; io.open = gopen
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
str_mod = importlib.import_module("libs.reporting.symbol_trade_report"); ov = importlib.import_module("libs.reporting.operator_visibility"); itr = importlib.import_module("libs.reporting.intraday_trade_reports")
D = "2026-10-26"; out = {}
reports = tmp / "reports"; (reports / "trades" / D).mkdir(parents=True)
# 1) trade_index producer: built ONLY from local trade lifecycle artifacts under reports/trades/<day>; broker fills are not an input
check(str_mod.build_daily_trade_index(reports, D) == [], "no lifecycle artifacts -> []")
lc = reports / "trades" / D / "TRD_X" / "lifecycle" / "trade_lifecycle.json"; lc.parent.mkdir(parents=True); lc.write_text(json.dumps({"trade_id": "TRD_X", "symbol": "005930", "day": D, "status": "open", "entry": {"run_id": "r-buy"}}), encoding="utf-8")
ti = str_mod.build_daily_trade_index(reports, D); out["trade_index_with_open_lifecycle"] = ti
check(len(ti) == 1 and ti[0]["status"] == "open" and ti[0]["exit_run_id"] == "", ti)
lc.unlink()
# 2) the producer of those artifacts at runtime: a BUY is NOT written unless generate_on_open/force-sync; only SELL triggers the bundle.
buy_state = {"run_id": "r-buy", "symbol": "005930", "execution": {"ok": True, "allowed": True, "order": {"action": "BUY", "symbol": "005930"}}}
rb = itr.generate_intraday_trade_artifacts(buy_state)   # no root -> no force-sync
out["buy_bundle_result"] = {"status": rb.get("status"), "reason": rb.get("reason"), "report_status": rb.get("report_status")}
check(rb.get("status") == "skipped" and rb.get("reason") == "trade_report_generate_on_open_disabled", rb)
check(not any(reports.rglob("lifecycle_bundle.json")), "BUY leaves no trade artifact")
# => with only a local BUY event (SELL missing locally, RL32-ORDER), no lifecycle artifact is produced and trade_index stays [] -> input-missing, not a consumer bug
# 3) realised samples / trading health: missing performance summary -> UNKNOWN, and UNKNOWN does not raise the overall operator health
th = ov._build_trading_health_status(reports, D); out["trading_health_missing_summary"] = th.get("trading_health_level")
check(th.get("trading_health_level") == "UNKNOWN", th)
ev = tmp / "data/logs/events.jsonl"; ev.parent.mkdir(parents=True, exist_ok=True)
rows = [{"ts": f"{D}T00:01:00+00:00", "run_id": "r-buy", "stage": "execute_from_packet", "event": "execution", "payload": {"ok": True, "action": "BUY", "symbol": "005930", "order_no": "0019354"}},
        {"ts": f"{D}T00:02:00+00:00", "run_id": "r-x", "stage": "commander_router", "event": "decision", "payload": {}}]
ev.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    p = ov.build_operator_daily_summary_payload(ev, reports / "operator", day=D, metrics_report_dir=tmp / "metrics", m30_post_golive_dir=tmp / "m30p", m30_golive_dir=tmp / "m30g", m31_slo_incident_dir=tmp / "m31")
health = p.get("health") or p.get("operator_health") or (p.get("summary") or {}).get("health")
issues = p.get("issues") or []
out["operator_health"] = health; out["operator_issue_codes"] = sorted({i.get("code") for i in issues if isinstance(i, dict)}); out["operator_trading_health"] = (p.get("trading_health_status") or {}).get("trading_health_level")
check(out["operator_trading_health"] == "UNKNOWN", out)
src = (repo / "libs/reporting/operator_visibility.py").read_text(encoding="utf-8")
out["health_inputs_include_reconciliation"] = ("reconcil" in src) or ("broker_truth" in src)
check(not bad, bad)
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, default=str))
print("RL32_REPORT_TRACE_OK trade_index_input=local_lifecycle_only buy_only=skipped_no_artifact trading_health_missing=UNKNOWN operator_health=%s reconciliation_in_health=%s network=0 debug=%s" % (out["operator_health"], out["health_inputs_include_reconciliation"], __debug__))
