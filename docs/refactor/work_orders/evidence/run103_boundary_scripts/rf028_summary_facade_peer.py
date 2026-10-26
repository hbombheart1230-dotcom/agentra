# RF-028 trade_report main_renderer <- markdown_summary <- trade_report_markdown_clean <- trade_report_ai use-time facade (synthetic tmp-only) (synthetic tmp-only, no network, no order).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
from pathlib import Path
ROOT = Path(os.getcwd()).resolve()
tmp = Path(tempfile.mkdtemp(prefix="rf028_summary_")).resolve()
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



os.chdir(tmp)
sys.path.insert(0, str(ROOT))
import copy
os.environ.update({"EVIDENCE_LEDGER_PATH": str(tmp / "ledger" / "events.jsonl"), "EVENT_LOG_PATH": str(tmp / "ev" / "e.jsonl"), "OPENROUTER_API_KEY": ""})
ai = importlib.import_module("libs.reporting.trade_report_ai")
clean = importlib.import_module("libs.reporting.trade_report_markdown_clean")
ms = importlib.import_module("libs.reporting.trade_report.markdown_summary")
mr = importlib.import_module("libs.reporting.trade_report.summary_render_parts.main_renderer")
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except BaseException as e: return None, type(e).__name__
# facade identity chain: ai -> clean -> markdown_summary -> main_renderer impl (call-time bindings)
check(ai.render_trade_summary_markdown.__module__ == "libs.reporting.trade_report_ai", "ai facade owner")
reports = {
  "empty": {},
  "minimal": {"symbol": "005930", "trade_id": "T1", "status": "closed", "summary": "x"},
  "rich": {"symbol": "005930", "trade_id": "T2", "status": "closed", "entry_price": 70000, "exit_price": 71000, "pnl": 1000, "pnl_pct": 1.43,
           "entry_time": "2026-10-26T09:05:00+09:00", "exit_time": "2026-10-26T09:40:00+09:00", "execution_mode": "mock",
           "lifecycle": {"entry": {"reason": "breakout"}, "exit": {"reason": "take_profit"}}, "market_context": {"kospi": {"change_pct": 0.5}}},
}
res = {}
for name, rp in reports.items():
    snap = copy.deepcopy(rp)
    a, ea = attempt(ai.render_trade_summary_markdown, rp)
    b, eb = attempt(clean.render_trade_summary_markdown_clean, rp)
    c, ec = attempt(ms.render_trade_summary_markdown, rp, deps=clean._summary_render_deps())
    check(rp == snap, "input mutated: " + name)
    check((ea, eb, ec) == (None, None, None), "exceptions %s %s %s" % (name, ea, eb))
    check(a == b == c and isinstance(a, str) and a.strip(), "facade chain equal: " + name)
    check(attempt(ai.render_trade_summary_markdown, copy.deepcopy(rp))[0] == a, "deterministic: " + name)
    res[name] = len(a)
# evaluation variant: with / without summary_report, input untouched
rp = reports["rich"]; sm = {"evaluation": {"problems": []}, "summary": "ok"}; s0 = copy.deepcopy(sm)
w, ew = attempt(ai.render_trade_summary_markdown_with_evaluation, rp, sm)
w0, ew0 = attempt(ai.render_trade_summary_markdown_with_evaluation, rp, {})
check(ew is None and ew0 is None and isinstance(w, str) and isinstance(w0, str) and sm == s0, "with_evaluation ok: %s %s" % (ew, ew0))
# build_trade_summary_input facade
inp, ei = attempt(ai.build_trade_summary_input, rp)
check(ei is None and isinstance(inp, dict), "summary input dict: %s" % ei)
# exception boundary: non-dict report / bad deps
bad_in = {}
for name, v in {"none": None, "str": "x", "list": []}.items():
    bad_in[name] = attempt(ai.render_trade_summary_markdown, v)[1]
check(any(bad_in.values()), "at least one non-dict report raises (no failsoft): %s" % bad_in)
missing_dep, em = attempt(mr.render_trade_summary_markdown_impl, {}, deps={}, **{k: None for k in ("append_summary_overview","append_summary_market_news","append_summary_decision_lifecycle","append_summary_closing","collect_render_diagnostics","pick_impl","money_impl","compact_number_impl","compact_decimal_impl","first_matching_line_impl","section_texts_impl","same_day_summary_impl","selected_score_impl","selected_rank_impl","extract_run_id_impl","policy_delta_lines_impl")})
check(em == "KeyError", "missing deps key -> KeyError, got %s" % em)
# late-binding: patching markdown_summary.append_summary_closing is honoured at call time
orig = ms.append_summary_closing; marker = []
def spy(*a, **k): marker.append(1); return orig(*a, **k)
ms.append_summary_closing = spy
try: out_spy, es = attempt(ai.render_trade_summary_markdown, rp)
finally: ms.append_summary_closing = orig
check(es is None and marker, "call-time patch of markdown_summary helper honoured via facade chain (calls=%d)" % len(marker))
# State/IO: no writes anywhere
check(not bad, "blocked attempts: %s" % bad)
check(not any(tmp.rglob("*")) or all(p.is_dir() for p in tmp.rglob("*")), "no files written under tmp")
print("RF028_SUMMARY_FACADE_OK lens=%s chain_equal=3 with_eval=ok input=dict nondict_raises=%s missing_dep=%s latepatch=%d blocked=%d debug=%s" % (res, {k: v for k, v in bad_in.items()}, em, len(marker), len(bad), __debug__))
