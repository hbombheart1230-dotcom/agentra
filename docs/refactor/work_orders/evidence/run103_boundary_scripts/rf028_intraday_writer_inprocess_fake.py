# RF-028 OWNER FIXTURE (A, for B's independent peer): in-process writer fake for libs.reporting.intraday_trade_reports.generate_intraday_trade_artifacts.
# B reported the rich-writer peer BLOCKED because generate_intraday_trade_artifacts(..., root=temp) runs the real bundle runner (run_live_execution_bundle_inprocess
# -> live_execution_bundle_runner.main with --trade-report-ai / --env-path). Seam: the module-level `_run_bundle_sync(argv)` is resolved at call time, so a fake
# replaces ONLY the bundle runner; everything else (policy/skip branches, argv build, event logging, brief-cache invalidation, result assembly) is the real code.
# This harness both PROVIDES the fake (FakeBundleRunner, importable / copyable) and SELF-VERIFIES it: tmp root only, network/subprocess/sqlite blocked, writes confined
# to tmp (builtins.open + io.open + os.mkdir/remove/unlink/rename/replace). Usage: PYTHONPATH=<repo> python rf028_intraday_writer_inprocess_fake.py [-O via python -O]
import os, sys, io, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, shutil
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY", "OPERATOR_UI_CACHE_PATH", "INTRADAY_TRADE")): del os.environ[k]
tmp = Path(tempfile.mkdtemp(prefix="rf028_fake_")).resolve()
for k, v in {"EVENT_LOG_PATH": "data/logs/events.jsonl", "EVIDENCE_LOG_PATH": "data/evidence_ledger/events.jsonl", "INTENTS_PATH": "data/logs/intents.jsonl", "ENV_PATH": ".env.absent", "EVIDENCE_LEDGER_PATH": "data/evidence_ledger/events.jsonl"}.items():
    os.environ[k] = str(tmp / v)
os.chdir(tmp)
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
for name in ("mkdir", "remove", "unlink", "rmdir", "rename", "replace"):
    orig = getattr(os, name)
    def g(*a, _o=orig, _n=name, **k):
        if not all(inside(x) for x in a[:2] if isinstance(x, (str, bytes, os.PathLike))): bad.append(_n + ":" + str(a[:1])); raise OSError("blocked " + _n)
        return _o(*a, **k)
    setattr(os, name, g)
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
itr = importlib.import_module("libs.reporting.intraday_trade_reports")
from libs.reporting.llm_artifacts import trade_artifact_paths

class FakeBundleRunner:
    """In-process stand-in for intraday_trade_reports._run_bundle_sync(argv) -> (rc, stdout_json).
    Writes a minimal trade report JSON under --reports-root (the only file the real writer's result points at) and returns a run_bundles summary."""
    def __init__(self, *, rc=0, raw=None, trade_id="TRD_20261020_005930_01", report_status="ok"):
        self.rc, self.raw, self.trade_id, self.report_status, self.calls = rc, raw, trade_id, report_status, []
    def __call__(self, argv):
        self.calls.append(list(argv))
        opt = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if str(argv[i]).startswith("--") and not str(argv[i + 1]).startswith("--")}
        reports_root, run_id, symbol = Path(opt["--reports-root"]), opt.get("--target-run-id", ""), opt.get("--target-symbol", "")
        if self.raw is not None: return self.rc, self.raw
        day = "-".join((self.trade_id.split("_")[1][:4], self.trade_id.split("_")[1][4:6], self.trade_id.split("_")[1][6:8]))
        report_path = Path(trade_artifact_paths(reports_root, day, self.trade_id)["ai_trade_report_json"])
        report_path.parent.mkdir(parents=True, exist_ok=True); report_path.write_text(json.dumps({"trade_id": self.trade_id, "generation": {"status": self.report_status}}), encoding="utf-8")
        summary = {"run_bundles": [{"run_id": run_id, "trade_id": self.trade_id, "story_id": "S1", "report_status": self.report_status, "trade_report_json_path": str(report_path), "symbol": symbol},
                                   {"run_id": "other-run", "trade_id": "TRD_X"}], "linked_run_ids": [run_id, "entry-run"]}
        return self.rc, json.dumps(summary)

def state(action="SELL", ok=True, run_id="run-exit-1", policy=None, **extra):
    s = {"run_id": run_id, "symbol": "005930", "execution": {"ok": ok, "allowed": True, "order": {"action": action, "symbol": "005930"}}, "day": "2026-10-20"}
    if policy is not None: s["applied_policy"] = {"reporter": {"trade_report": policy}}
    s.update(extra); return s
root = tmp / "root"; root.mkdir()
out = {}
real_sync = itr._run_bundle_sync
fake = FakeBundleRunner(); itr._run_bundle_sync = fake
# 1) SELL with root -> force_sync -> fake runner (in-process) -> generated
r = itr.generate_intraday_trade_artifacts(state(), root=root)
check(r["ok"] is True and r["status"] == "generated" and r["trade_id"] == "TRD_20261020_005930_01" and r["story_id"] == "S1" and r["report_status"] == "ok" and r["symbol"] == "005930", r)
check(r["target_run_id"] == "run-exit-1" and r["target_symbol"] == "005930" and r["role"] == "intraday_trade_report_bundle" and Path(r["report_path"]).exists(), r)
check(r["operator_brief_json_path"].startswith(str(root / "reports" / "trades" / "2026-10-20")), r.get("operator_brief_json_path"))
a = fake.calls[-1]; check(a[a.index("--reports-root") + 1] == str(root / "reports") and a[a.index("--target-run-id") + 1] == "run-exit-1" and "--trade-report-ai" in a and a[a.index("--report-dir") + 1] == str(root / "reports/dev/analysis/live_execution_bundles"), a)
check(a[a.index("--env-path") + 1] == str(tmp / ".env.absent"), "env-path honours ENV_PATH (real .env never read)")
out["argv_keys"] = sorted(x for x in a if x.startswith("--"))
# 2) BUY with root: generate_on_open False but root forces sync -> generated (not 'skipped')
rb = itr.generate_intraday_trade_artifacts(state(action="BUY", run_id="run-entry-1"), root=root); check(rb["status"] == "generated", rb["status"])
# 3) brief-cache invalidation for run ids in summary (real code; files under root)
cache = root / "data/operator_ui/brief_cache"; cache.mkdir(parents=True); [(cache / f"{x}.json").write_text("{}") for x in ("run-exit-1", "entry-run", "unrelated")]
rc_ = itr.generate_intraday_trade_artifacts(state(), root=root); out["cache_invalidated"] = sorted(Path(p).name for p in rc_["cache_invalidated"])
check((cache / "unrelated.json").exists() and not (cache / "run-exit-1.json").exists(), out["cache_invalidated"])
# 4) skip / disabled branches never reach the runner
n0 = len(fake.calls)
os.environ["INTRADAY_TRADE_REPORTS_ENABLED"] = "false"; d1 = itr.generate_intraday_trade_artifacts(state(), root=root); del os.environ["INTRADAY_TRADE_REPORTS_ENABLED"]
d2 = itr.generate_intraday_trade_artifacts(state(policy={"enabled": False}), root=root)
d3 = itr.generate_intraday_trade_artifacts(state(ok=False), root=root)
d4 = itr.generate_intraday_trade_artifacts(state(action="HOLD"), root=root)
check([d1["status"], d2["status"], d3["status"], d4["status"]] == ["disabled", "disabled", "skipped", "skipped"] and len(fake.calls) == n0, [d1, d2, d3, d4])
out["skip_reasons"] = [d1["reason"], d2["reason"], d3["reason"], d4["reason"]]
# 5) runner failure modes
itr._run_bundle_sync = FakeBundleRunner(rc=2, raw="boom"); f1 = itr.generate_intraday_trade_artifacts(state(), root=root)
check(f1["ok"] is False and f1["status"] == "failed" and f1["return_code"] == 2 and f1["stdout"] == "boom", f1)
itr._run_bundle_sync = FakeBundleRunner(rc=0, raw="not json"); f2 = itr.generate_intraday_trade_artifacts(state(), root=root)
out["rc0_invalid_json"] = {"status": f2["status"], "trade_id": f2.get("trade_id")}  # observed: invalid JSON with rc 0 -> summary {} -> 'generated' with empty trade_id
itr._run_bundle_sync = FakeBundleRunner(rc=0, raw="[1,2]"); f3 = itr.generate_intraday_trade_artifacts(state(), root=root); out["rc0_json_list"] = f3["status"]
itr._run_bundle_sync = real_sync
# 6) effects: bundle event log written under root only; nothing outside tmp; no network/subprocess
ev = root / "data/logs/events.jsonl"; out["event_log_lines"] = len(ev.read_text(encoding="utf-8").splitlines()) if ev.exists() else 0
check(not bad, bad); out["blocked_attempts"] = 0
files = sorted(str(p.relative_to(tmp).as_posix()) for p in tmp.rglob("*") if p.is_file()); out["files_under_tmp"] = len(files)
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True))
print("RF028_INTRADAY_WRITER_INPROCESS_FAKE_OK seam=_run_bundle_sync generated=SELL/BUY(root) skip_branches=4 failed=rc!=0 rc0_invalid_json=%s cache_invalidated=%d subprocess=0 network=0 debug=%s" % (out["rc0_invalid_json"]["status"], len(out["cache_invalidated"]), __debug__))
