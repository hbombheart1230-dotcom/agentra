# RF-031 C2: downstream recovery after a partial reporter_analysis write (JSON written, MD OSError).
# Temp-only; the generator is faked; socket/subprocess blocked. Prints one JSON line.
import json, os, socket, subprocess, sys, tempfile
from pathlib import Path
def _no(*a, **k): raise PermissionError("blocked")
socket.socket.connect = _no; subprocess.Popen.__init__ = _no  # type: ignore
TMP = Path(tempfile.mkdtemp(prefix="rf031_rec_")).resolve()
import libs.reporting.live_execution_bundle_runner as R
calls = []
def fake_gen(event_log_path, report_dir, *, day, intents_path=None, reports_root=None, **k):
    calls.append(day); report_dir.mkdir(parents=True, exist_ok=True)
    js = report_dir / f"reporter_analysis_{day}.json"; md = report_dir / f"reporter_analysis_{day}.md"
    js.write_text(json.dumps({"gen": len(calls)}), encoding="utf-8")
    if len(calls) == 1: raise OSError("synthetic md write failure")
    md.write_text("# ok", encoding="utf-8"); return md, js, {"gen": len(calls)}
R.generate_reporter_analysis_report = fake_gen
analysis_root = TMP / "reports" / "analysis"; ev = TMP / "events.jsonl"; ev.write_text("", encoding="utf-8")
out = {}
try:
    R._load_or_generate_reporter_analysis(ev, analysis_root, TMP / "reports", None, "2026-10-27"); out["first_raises"] = False
except OSError: out["first_raises"] = True
rd = analysis_root / "reporter_analysis"
out["after_fail"] = sorted(p.name for p in rd.iterdir())
md, js, payload = R._load_or_generate_reporter_analysis(ev, analysis_root, TMP / "reports", None, "2026-10-27")
out["second_regenerated"] = payload == {"gen": 2} and len(calls) == 2
md, js, payload = R._load_or_generate_reporter_analysis(ev, analysis_root, TMP / "reports", None, "2026-10-27")
out["third_reused_no_call"] = payload == {"gen": 2} and len(calls) == 2
out["outside_tmp"] = not str(js.resolve()).startswith(str(TMP))
ok = out["first_raises"] and out["after_fail"] == ["reporter_analysis_2026-10-27.json"] and out["second_regenerated"] and out["third_reused_no_call"] and not out["outside_tmp"]
print(json.dumps(out, sort_keys=True)); print("RF031_PARTIAL_RECOVERY_OK" if ok else "RF031_PARTIAL_RECOVERY_FAIL"); sys.exit(0 if ok else 1)
