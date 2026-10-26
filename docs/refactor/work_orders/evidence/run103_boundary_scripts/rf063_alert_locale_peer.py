# Offline peer for RF-063 check_alert_policy_v1 {_build_parser,_evaluate_alerts} pure paths + cp949 decode/encode cause split.
# main()/generate_metrics_report/load_env_file are never called; only a tmp metrics JSON is read.
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, io, argparse
from pathlib import Path
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "ALERT_POLICY")): del os.environ[k]
sys.path.insert(0, os.getcwd())
tmp = Path(tempfile.mkdtemp(prefix="rf063_alert_")).resolve()
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
_wt, _wb, _mk = Path.write_text, Path.write_bytes, Path.mkdir
def guard(orig, tag):
    def f(self, *a, **k):
        if not inside(self): bad.append(tag + ":" + str(self)); raise OSError("blocked")
        return orig(self, *a, **k)
    return f
Path.write_text, Path.write_bytes, Path.mkdir = guard(_wt, "write_text"), guard(_wb, "write_bytes"), guard(_mk, "mkdir")
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)

m = importlib.import_module("scripts.diagnostics.check_alert_policy_v1")
P = m._build_parser()
A = lambda *argv: P.parse_args(list(argv))
a = A()
check((a.llm_success_rate_min, a.llm_circuit_open_rate_max, a.execution_blocked_rate_max, a.execution_approved_executed_gap_max, a.api_429_rate_max,
       a.portfolio_guard_blocked_ratio_max, a.portfolio_guard_strategy_budget_exceeded_max, a.fail_on, a.json)
      == (0.70, 0.30, 0.60, 0, 0.20, 0.70, 20, "critical", False), "parser defaults")
for bad_argv in (["--fail-on", "bogus"], ["--api-429-rate-max", "x"], ["--nope"]):
    _se = sys.stderr; sys.stderr = io.StringIO()
    try: P.parse_args(bad_argv); check(False, "argparse should exit")
    except SystemExit as e: check(e.code == 2, "argparse exit 2")
    finally: sys.stderr = _se
os.environ["ALERT_POLICY_FAIL_ON"] = "warning"; os.environ["ALERT_POLICY_API_429_RATE_MAX"] = "bad"; os.environ["ALERT_POLICY_EXECUTION_APPROVED_EXECUTED_GAP_MAX"] = "3.9"
P2 = m._build_parser(); b = P2.parse_args([])
check(b.fail_on == "warning" and b.api_429_rate_max == 0.20 and b.execution_approved_executed_gap_max == 3, "env defaults / bad env fallback / int(float)")
os.environ["ALERT_POLICY_FAIL_ON"] = "zzz"; check(m._env_fail_on() == "critical", "bad fail_on env")
for k in [k for k in os.environ if k.startswith("ALERT_POLICY")]: del os.environ[k]

def ev(metrics, *argv): return m._evaluate_alerts(metrics, A(*argv))
r = ev({})
check(r["ok"] is False and [x["code"] for x in r["alerts"]] == ["strategist_success_rate_low"] and r["severity_total"] == {"critical": 1}, "empty metrics -> success rate low only")
good = {"strategist_llm": {"success_rate": 0.9, "circuit_open_rate": 0.1}, "execution": {"intents_created": 10, "intents_approved": 5, "intents_blocked": 2, "intents_executed": 5}, "broker_api": {"api_429_rate": 0.1}}
r = ev(good); check(r["ok"] and r["alert_total"] == 0 and r["values"]["execution_blocked_rate"] == 0.2, "good metrics")
bd = {"strategist_llm": {"success_rate": 0.1, "circuit_open_rate": 0.9},
      "execution": {"intents_created": 10, "intents_approved": 8, "intents_blocked": 7, "intents_executed": 3},
      "broker_api": {"api_429_rate": 0.5},
      "portfolio_guard": {"applied_total": 2, "approved_total_sum": 1, "blocked_total_sum": 9, "blocked_reason_total": {"strategy_budget_exceeded": 21}}}
r = ev(bd)
check([x["code"] for x in r["alerts"]] == ["strategist_success_rate_low", "strategist_circuit_open_rate_high", "execution_blocked_rate_high",
      "execution_approved_executed_gap_high", "broker_api_429_rate_high", "portfolio_guard_blocked_ratio_high", "portfolio_guard_strategy_budget_exceeded_high"], "all seven alerts in order")
check(r["severity_total"] == {"critical": 3, "warning": 4} and r["ok"] is False and r["values"]["execution_approved_executed_gap"] == 5, "severity totals")
warn_only = {"strategist_llm": {"success_rate": 1, "circuit_open_rate": 0}, "broker_api": {"api_429_rate": 0.9}}
check(ev(warn_only)["ok"] is True and ev(warn_only, "--fail-on", "warning")["ok"] is False and ev(bd, "--fail-on", "none")["ok"] is True, "fail_on semantics")
legacy = {"strategist_llm": {"success_rate": 1}, "intents_created_total": 4, "intents_approved_total": 3, "intents_blocked_total": 4, "intents_executed_total": 1}
r = ev(legacy); check([x["code"] for x in r["alerts"]] == ["execution_blocked_rate_high", "execution_approved_executed_gap_high"], "legacy *_total fallback keys")
nonmap = {"strategist_llm": "x", "execution": [], "broker_api": 1, "portfolio_guard": None}
check(ev(nonmap)["alert_total"] == 1, "non-mapping sections tolerated")
check(ev({"strategist_llm": {"success_rate": "nan-ish"}})["values"]["llm_success_rate"] == 0.0, "unparseable value -> 0.0")
pg_idle = {"strategist_llm": {"success_rate": 1}, "portfolio_guard": {"applied_total": 0, "approved_total_sum": 0, "blocked_total_sum": 9}}
check(ev(pg_idle)["alert_total"] == 0, "guard ratio ignored when applied_total == 0")

# cp949 decode vs encode cause split (pure; tmp file only)
sample = {"strategist_llm": {"success_rate": 0.9}, "note": "한글"}
p_utf8 = tmp / "m_utf8.json"; p_utf8.write_text(json.dumps(sample, ensure_ascii=False), encoding="utf-8")
p_cp949 = tmp / "m_cp949.json"; p_cp949.write_bytes(json.dumps(sample, ensure_ascii=False).encode("cp949"))
p_bom = tmp / "m_bom.json"; p_bom.write_bytes(b"\xef\xbb\xbf" + json.dumps(sample).encode("utf-8"))
p_bad = tmp / "m_bad.json"; p_bad.write_text("{oops", encoding="utf-8")
ld = lambda p: m._load_metrics(A("--metrics-json-path", str(p)))
check(ld(p_utf8)[0] == 0 and ld(p_utf8)[1]["note"] == "한글", "utf-8 metrics ok")
rc, data, _ = ld(p_cp949); check(rc == 2 and data == {}, "cp949-encoded metrics -> decode failure rc 2")
try: p_cp949.read_text(encoding="utf-8"); check(False, "cp949 bytes must fail utf-8 decode")
except UnicodeDecodeError: dec = "UnicodeDecodeError"
rc, data, _ = ld(p_bom); check(rc == 2, "utf-8 BOM metrics -> JSON error rc 2 (read_text utf-8 keeps BOM)")
try: json.loads(p_bom.read_text(encoding="utf-8")); check(False, "bom")
except json.JSONDecodeError: bomc = "JSONDecodeError"
check(ld(p_bad)[0] == 2 and ld(tmp / "missing.json")[0] == 2, "bad json / missing -> rc 2")
# same rc 2 for all three causes: decode vs JSON vs missing are indistinguishable to the caller
buf = io.BytesIO(); w = io.TextIOWrapper(buf, encoding="cp949", errors="strict", newline="")
w.write("ok 한글\n"); w.flush(); check(buf.getvalue().decode("cp949") == "ok 한글\n", "cp949 stdout handles Hangul")
try: w.write("emoji \U0001F600\n"); w.flush(); check(False, "cp949 cannot encode emoji")
except UnicodeEncodeError: enc = "UnicodeEncodeError"
out_line = json.dumps({"path": "\U0001F600"}, ensure_ascii=False)
try: out_line.encode("cp949"); check(False, "json ensure_ascii=False emoji -> cp949 fail")
except UnicodeEncodeError: pass
check(json.dumps({"path": "\U0001F600"}).encode("cp949"), "ensure_ascii default is cp949-safe (main uses ensure_ascii=False)")
check(not bad, "blocked attempts %r" % bad)
print("RF063_ALERT_LOCALE_PEER_OK parser=3 alerts=7 evalcases=9 decode=%s bom=%s encode=%s load_rc=2/2/2 writes=0 debug=%s" % (dec, bomc, enc, __debug__))
