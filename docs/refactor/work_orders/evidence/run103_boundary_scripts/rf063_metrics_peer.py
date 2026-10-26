# RF-063 check_metrics_schema_v1.main on synthetic tmp inputs. NOTE: the CLI is NOT read-only (mkdir report_dir + the
# metrics generator writes JSON/MD); writes are permitted ONLY under the tmp root, everything else is blocked+recorded.
import os, sys, json, io, shutil, socket, subprocess, sqlite3, builtins, contextlib, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
root = Path("/tmp/rf063_metrics_fixed"); shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
import ssl, http.client
cli = importlib.import_module("scripts.diagnostics.check_metrics_schema_v1")
bad, outside = [], []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: return Path(os.path.abspath(str(p))).is_relative_to(root)
    except Exception: return False
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): outside.append("open:" + str(f)); raise OSError("blocked")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt = Path.write_text; _mk = Path.mkdir
def wt(self, *a, **k):
    if not inside(self): outside.append("write_text:" + str(self)); raise OSError("blocked")
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): outside.append("mkdir:" + str(self)); raise OSError("blocked")
    return _mk(self, *a, **k)
Path.write_text = wt; Path.mkdir = mk
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def files(): return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
out = {}
def run(name, argv):
    buf = io.StringIO(); code = None
    with contextlib.redirect_stdout(buf):
        try: code = cli.main(argv)
        except SystemExit as e: code = e.code
        except Exception as e: code = "EXC:" + type(e).__name__ + ":" + str(e)[:80]
    out[name] = [code, buf.getvalue().replace(str(root), "ROOT")[:1500]]
ev_empty = root / "events_empty.jsonl"; ev_empty.write_text("", encoding="utf-8")
ev = root / "events.jsonl"
ev.write_text("\n".join(json.dumps(r) for r in [
    {"run_id": "r1", "ts": "2026-04-08T01:00:00+00:00", "stage": "strategist", "event": "llm_call", "payload": {"ok": True, "latency_ms": 120}},
    {"run_id": "r1", "ts": "2026-04-08T01:00:01+00:00", "stage": "execute_from_packet", "event": "verdict", "payload": {"allowed": False, "reason": "blocked"}},
    {"run_id": "r2", "ts": "2026-04-09T01:00:00+00:00", "stage": "broker", "event": "api_error", "payload": {"api_id": "ka10001", "status": 429}}]) + "\n", encoding="utf-8")
for name, evp, extra in (("empty_json", ev_empty, ["--json"]), ("sample_json", ev, ["--json", "--day", "2026-04-08"]), ("sample_plain", ev, []), ("missing_log", root / "nope.jsonl", ["--json"])):
    run(name, ["--event-log-path", str(evp), "--report-dir", str(root / ("rep_" + name))] + extra)
run("badflag", ["--bogus"])
# failure paths via a patched generator
real = cli.generate_metrics_report
def gen_unreadable(events_path, report_dir, day=None): return Path(report_dir) / "m.md", Path(report_dir) / "does_not_exist.json"
cli.generate_metrics_report = gen_unreadable; run("unreadable_metrics", ["--event-log-path", str(ev), "--report-dir", str(root / "rep_unreadable"), "--json"])
def gen_partial(events_path, report_dir, day=None):
    p = Path(report_dir) / "partial.json"; p.write_text(json.dumps({"schema_version": "metrics.v0", "strategist_llm": {"success_rate": "x"}, "execution": {"intents_created": True}}), encoding="utf-8"); return Path(report_dir) / "m.md", p
cli.generate_metrics_report = gen_partial; run("partial_schema", ["--event-log-path", str(ev), "--report-dir", str(root / "rep_partial"), "--json"]); run("partial_plain", ["--event-log-path", str(ev), "--report-dir", str(root / "rep_partial")])
cli.generate_metrics_report = real
out["json_path_get"] = [cli._json_path_get({"a": {"b": 1}}, "a.b"), cli._json_path_get({"a": 1}, "a.b"), cli._json_path_get({}, "x")]
out["is_number"] = [cli._is_number(v) for v in (1, 1.5, True, "1", None)]
out["files"] = files(); out["bad"] = bad; out["outside"] = outside
check(out["sample_json"][0] in (0, 3) and out["empty_json"][0] in (0, 3), "schema exit 0/3")
check(out["badflag"][0] == 2 and out["unreadable_metrics"][0] == 2 and out["partial_schema"][0] == 3, "exit codes")
check("failure_total" in out["partial_schema"][1] and "missing:" in out["partial_schema"][1], "partial failures listed")
check(not bad and not outside, "no blocked/outside writes: %r %r" % (bad, outside))
print("RF063_METRICS_PEER_OK empty=%s sample=%s plain=%s missing_log=%s badflag=%s unreadable=%s partial=%s outside_writes=0 debug=%s" % (out["empty_json"][0], out["sample_json"][0], out["sample_plain"][0], out["missing_log"][0], out["badflag"][0], out["unreadable_metrics"][0], out["partial_schema"][0], __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
