# Offline owner-boundary checks for RF-033 point_in_time_capture read path (synthetic tmp root, no fetch).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, copy, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
import ssl, http.client
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf033_cap_")).resolve()
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
_wt, _mk, _rp = Path.write_text, Path.mkdir, Path.replace
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
m = importlib.import_module("libs.reporting.baseline_btc_woori_tech.point_in_time_capture")
root = tmp / "root"
def put(day, text):
    p = m.capture_paths(day, root=root)["snapshot"]; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")
cap = lambda rows_by: {"capture_status": "CAPTURED", "reason": "", "sources": rows_by}
put("2026-04-08", json.dumps(cap({"btc_usd": [{"ts": 1000, "close": 1.0}, {"ts": 1000, "close": 9.0}], "btc_krw": [{"ts": 900, "close": 5.0}, "bad", None]})))
put("2026-04-07", "{not json")
put("2026-04-06", json.dumps({"capture_status": "MISSED", "reason": "08:55_capture_window_missed_no_backfill", "sources": {"btc_usd": [{"ts": 5}]}}))
put("2026-04-05", json.dumps([1, 2]))
put("2026-04-04", json.dumps({"capture_status": "CAPTURED", "sources": {"btc_usd": [{"ts": "abc"}]}}))
put("2026-04-03", json.dumps({"capture_status": "CAPTURED", "sources": "notmap"}))
before = tree(root); out = {}
# load_capture_snapshot / load_captured_sources
out["snap_ok"] = m.load_capture_snapshot("2026-04-08", root=root)["capture_status"]
out["snap_broken"] = m.load_capture_snapshot("2026-04-07", root=root)
out["snap_missing_day"] = m.load_capture_snapshot("2026-04-01", root=root)
out["snap_nonmap"] = m.load_capture_snapshot("2026-04-05", root=root)
out["snap_day_trunc"] = m.load_capture_snapshot("2026-04-08T09:00:00", root=root)["capture_status"]
out["src_ok"] = m.load_captured_sources("2026-04-08", root=root)
out["src_broken"] = m.load_captured_sources("2026-04-07", root=root)
out["src_missed"] = m.load_captured_sources("2026-04-06", root=root)
out["src_missing_day"] = m.load_captured_sources("2026-04-01", root=root)
out["src_notmap"] = m.load_captured_sources("2026-04-03", root=root)
# merge: existing 08:55 capture + duplicate epoch (captured wins) + in-memory payload untouched
payload = {"sources": {"btc_usd": [{"ts": 500, "close": 7.0}, {"ts": 1000, "close": 0.0}, {"ts": 0, "close": 3.0}], "other": [{"ts": 1}]}, "fallback_reason": "fresh_fetch_disabled", "k": [1]}
snap_in = copy.deepcopy(payload)
r = m.merge_capture_into_signal_payload(payload, day="2026-04-08", root=root)
out["merge_ok"] = r
check(payload == snap_in, "input payload mutated")
check([x["ts"] for x in r["sources"]["btc_usd"]] == [500, 1000] and r["sources"]["btc_usd"][1]["close"] == 9.0, "epoch dedupe/capture-last-wins")
check(r["sources"]["btc_krw"] == [{"ts": 900, "close": 5.0}], "non-mapping rows dropped")
check(r["fallback_reason"] == "" and r["available"] and r["btc_0855_capture_reused"] and r["available_sources"] == ["btc_krw", "btc_usd", "other"], "reuse flags")
r2 = m.merge_capture_into_signal_payload({"fallback_reason": "other_reason"}, day="2026-04-08", root=root)
check(r2["fallback_reason"] == "other_reason", "unrelated fallback_reason kept")
out["merge_keep_reason"] = r2["fallback_reason"]
# broken / missing day / MISSED / non-mapping / None payload
for d in ("2026-04-07", "2026-04-01", "2026-04-06", "2026-04-05", "2026-04-03"):
    rr = m.merge_capture_into_signal_payload(None, day=d, root=root)
    out["merge|" + d] = {k: rr[k] for k in ("sources", "available", "available_sources", "btc_0855_capture_reused", "btc_0855_capture_status", "btc_0855_capture_reason")}
    check(rr["available"] is False and rr["btc_0855_capture_reused"] is False, "no-capture " + d)
check(out["merge|2026-04-06"]["btc_0855_capture_status"] == "MISSED", "MISSED status surfaced")
check(out["merge|2026-04-07"]["btc_0855_capture_status"] == "", "broken json -> empty status")
# non-mapping / nested-bad payload sources
rr = m.merge_capture_into_signal_payload({"sources": "notmap"}, day="2026-04-01", root=root); out["merge_sources_notmap"] = rr["sources"]
rr = m.merge_capture_into_signal_payload({"sources": {"a": None, "b": [1, {"ts": 3}]}}, day="2026-04-01", root=root); out["merge_rows_none"] = rr["sources"]
check(out["merge_rows_none"] == {"a": [], "b": [{"ts": 3}]}, "payload rows filtering")
# malformed ts in captured file -> exception (no fail-soft); in-memory payload malformed ts -> exception too
def exc(f):
    try: f(); return "no_raise"
    except Exception as e: return type(e).__name__
out["exc_captured_malformed_ts"] = exc(lambda: m.merge_capture_into_signal_payload({}, day="2026-04-04", root=root))
out["exc_payload_malformed_ts"] = exc(lambda: m.merge_capture_into_signal_payload({"sources": {"btc_usd": [{"ts": "x"}]}}, day="2026-04-08", root=root))
out["exc_payload_nonmalformed_no_capture"] = exc(lambda: m.merge_capture_into_signal_payload({"sources": {"btc_usd": [{"ts": "x"}]}}, day="2026-04-01", root=root))
out["exc_load_malformed_ts"] = exc(lambda: m.load_captured_sources("2026-04-04", root=root))
check(out["exc_captured_malformed_ts"] == "ValueError" and out["exc_load_malformed_ts"] == "no_raise", "malformed ts exception boundary")
check(tree(root) == before, "tmp root mutated by read path")
check(not bad, "blocked attempts: " + repr(bad))
print("RF033_CAPTURE_OWNER_OK snap=%d merge=%d dup_epoch=capture_wins malformed_ts=%s/%s writes=0 outside=%d debug=%s" % (6, 7, out["exc_captured_malformed_ts"], out["exc_payload_malformed_ts"], len(bad), __debug__))
sys.stderr.write(hashlib.sha1(json.dumps(out, sort_keys=True, default=str).encode()).hexdigest() + "\n")
