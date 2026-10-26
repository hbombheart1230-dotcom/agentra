# RF-033: baseline_btc_woori_tech/input_worker.py -- start_input_worker + InputWorker.tick with a FAKE thread/event/clock and fake collaborators
# (merge_capture_into_signal_payload / load_btc_signal_rows / load_woori_candles / publish_input). No real thread is ever started, no sleep, no network,
# no file written anywhere (the fake publish_input records its kwargs). Windows concurrency / real-thread timing stays UNKNOWN (NOT_RUN).
import os, sys, io, builtins, socket, subprocess, sqlite3, importlib, contextlib, tempfile, types
from datetime import datetime, timedelta
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.baseline_btc_woori_tech.input_worker")
KST, epoch = mod.KST, mod.epoch
tmp = Path(tempfile.mkdtemp(prefix="rf033_siw_")).resolve()
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
Path.write_text = blocked("write_text"); Path.mkdir = blocked("mkdir")
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: " % sys._getframe(1).f_lineno + str(m))
D = "2026-09-01"
class Clock:
    t = None
    def set(self, hhmmss, day=D): self.t = datetime.fromisoformat(f"{day}T{hhmmss}").replace(tzinfo=KST)
clock = Clock()
class FDT:
    @staticmethod
    def now(tz=None):
        check(tz is KST, "now() must be called with KST"); return clock.t
class FakeEvent:
    def __init__(self): self._s = False; self.waits = []; self.on_wait = None
    def is_set(self): return self._s
    def set(self): self._s = True
    def wait(self, t=None):
        self.waits.append(t)
        if self.on_wait: self.on_wait(self)
        return self._s
threads = []
class FakeThread:
    def __init__(self, target=None, name=None, daemon=None): self.target, self.name, self.daemon, self.started = target, name, daemon, 0; threads.append(self)
    def start(self): self.started += 1
mod.threading = types.SimpleNamespace(Event=FakeEvent, Thread=FakeThread)
mod.datetime = FDT
calls = []
class Fakes:
    sig = {"btc_0855_capture_status": "CAPTURED", "btc": 1}
    research = {"btc_usd_daily": [1], "woori_daily": [2]}
    research_exc = None; candles = [{"c": 1}]; publish_exc = None; merge_exc = None; tick_log = []
fk = Fakes()
def merge(payload, *, day):
    calls.append(("merge", dict(payload), day))
    if fk.merge_exc: raise fk.merge_exc
    return dict(fk.sig)
def load_btc(*, day):
    calls.append(("btc", day))
    if fk.research_exc: raise fk.research_exc
    return {"research_context": fk.research}
def load_woori(*, day, state_path, allow_fresh_fetch):
    calls.append(("woori", day, state_path, allow_fresh_fetch)); return fk.candles
def publish(*, day, reports_root, signals, candles, now_epoch):
    calls.append(("publish", day, reports_root, signals, candles, now_epoch))
    if fk.publish_exc: raise fk.publish_exc
    return {"published": now_epoch}
mod.merge_capture_into_signal_payload, mod.load_btc_signal_rows, mod.load_woori_candles, mod.publish_input = merge, load_btc, load_woori, publish
root, state = tmp / "r", tmp / "s.json"
out = {}
# ---------- tick() ----------
w = mod.InputWorker(D, root, state); check(w.research is None and (w.day, w.reports_root, w.state_path) == (D, root, state), "ctor")
t0855, t0900, t0905 = epoch(D, "08:55"), epoch(D, "09:00"), epoch(D, "09:05")
# before 09:00 -> no candles even if CAPTURED; research fetched + cached
r = w.tick(t0855); check(r == {"published": t0855}, r)
pub = [c for c in calls if c[0] == "publish"][-1]
check(pub[1:3] == (D, root) and pub[4] == [] and pub[5] == t0855 and pub[3]["research_context"] == fk.research and pub[3]["btc"] == 1, pub)
check(not any(c[0] == "woori" for c in calls) and [c for c in calls if c[0] == "merge"][-1][1:] == ({}, D), "merge called with empty payload + day")
check(w.research == fk.research, "research cached")
n_btc = sum(c[0] == "btc" for c in calls)
# at/after 09:00 + CAPTURED -> fresh-fetch candles with state_path; cached research => no re-fetch
w.tick(t0900); wc = [c for c in calls if c[0] == "woori"][-1]
check(wc == ("woori", D, state, True), wc); check(sum(c[0] == "btc" for c in calls) == n_btc, "cached research refetched")
check([c for c in calls if c[0] == "publish"][-1][4] == fk.candles, "candles published")
# exactly 08:59:59 boundary: epoch < 09:00 -> no candles
calls.clear(); w.tick(t0900 - 1); check(not any(c[0] == "woori" for c in calls), "1s before 09:00 must not fetch candles")
# not CAPTURED -> no candles even after 09:00
fk.sig = {"btc_0855_capture_status": "MISSED"}; calls.clear(); w.tick(t0905)
check(not any(c[0] == "woori" for c in calls) and [c for c in calls if c[0] == "publish"][-1][4] == [], "uncaptured -> no candles")
fk.sig = {}; calls.clear(); w.tick(t0905); check(not any(c[0] == "woori" for c in calls), "status absent -> no candles")
fk.sig = {"btc_0855_capture_status": "CAPTURED", "btc": 1}
# research invalid shapes -> None -> {} and retried next tick
for bad_ctx in ({}, {"btc_usd_daily": [1]}, {"woori_daily": [2]}, {"btc_usd_daily": [], "woori_daily": [2]}):
    w2 = mod.InputWorker(D, root, state); fk.research = bad_ctx; calls.clear(); w2.tick(t0855)
    p = [c for c in calls if c[0] == "publish"][-1]; check(w2.research is None and p[3]["research_context"] == {}, (bad_ctx, p[3]))
    calls.clear(); w2.tick(t0855); check(sum(c[0] == "btc" for c in calls) == 1, "invalid research must be retried")
fk.research = None; w3 = mod.InputWorker(D, root, state); calls.clear(); w3.tick(t0855)  # {'research_context': None} -> `or {}` -> {} -> falsy -> None
check(w3.research is None, "None research_context")
# research fetch raising is swallowed (Exception family) -> {}
for exc in (ValueError("v"), TimeoutError("t"), KeyError("k")):
    fk.research_exc = exc; w4 = mod.InputWorker(D, root, state); calls.clear(); w4.tick(t0855)
    check([c for c in calls if c[0] == "publish"][-1][3]["research_context"] == {} and w4.research is None, exc)
fk.research_exc = None; fk.research = {"btc_usd_daily": [1], "woori_daily": [2]}
# exceptions from merge / publish propagate out of tick (loop handles them)
fk.merge_exc = RuntimeError("m"); e1 = None
try: mod.InputWorker(D, root, state).tick(t0855)
except Exception as e: e1 = type(e).__name__
fk.merge_exc = None; fk.publish_exc = ValueError("p"); e2 = None
try: mod.InputWorker(D, root, state).tick(t0855)
except Exception as e: e2 = type(e).__name__
fk.publish_exc = None; out["tick_exc"] = (e1, e2); check(out["tick_exc"] == ("RuntimeError", "ValueError"), out["tick_exc"])
# ---------- start_input_worker + loop ----------
threads.clear(); calls.clear(); clock.set("08:00:00")
stop = mod.start_input_worker(day=D, reports_root=root, state_path=state)
check(isinstance(stop, FakeEvent) and not stop.is_set() and len(threads) == 1, "returns stop event")
th = threads[0]; check(th.started == 1 and th.name == "q12-opening-input" and th.daemon is True and not calls, (th.started, th.name, th.daemon))
# drive the captured loop synchronously: each wait(15) advances the fake clock by `step` seconds
def run_loop(start, step, stop_after=None, day=D):
    th = threads[-1]; clock.set(start, day); ev = th_ev[-1]; ev._s = False; ev.waits.clear(); calls.clear(); n = {"w": 0}
    def adv(e):
        n["w"] += 1; clock.t = clock.t + timedelta(seconds=step)
        if stop_after and n["w"] >= stop_after: e.set()
    ev.on_wait = adv; buf = io.StringIO()
    with contextlib.redirect_stdout(buf): th.target()
    return buf.getvalue(), n["w"], ev
th_ev = [stop]
# before 08:50 nothing ticks; loop steps 15s*... use 600s steps: 08:30 -> 08:40 -> 08:50(tick) -> 09:00(tick) -> 09:10(tick) -> 09:20 returns
txt, waits, ev = run_loop("08:30:00", 600)
ticks = [c for c in calls if c[0] == "publish"]
check([c[5] for c in ticks] == [epoch(D, "08:50"), epoch(D, "09:00"), epoch(D, "09:10")], [c[5] for c in ticks])
check(set(ev.waits) == {15} and waits == 5, (ev.waits, waits)); check(not ev.is_set() and txt == "", "loop returns by itself, stop not set")
out["loop_ticks"] = [c[5] - epoch(D, "08:50") for c in ticks]
# 09:12:00 exactly still ticks; 09:12:01 returns without tick
txt, waits, ev = run_loop("09:12:00", 1); check([c[5] for c in calls if c[0] == "publish"] == [epoch(D, "09:12")] and waits == 1, ([c[5] for c in calls if c[0] == "publish"], waits))
txt, waits, ev = run_loop("09:12:01", 1); check(not [c for c in calls if c[0] == "publish"] and waits == 0, "after 09:12 returns immediately")
txt, waits, ev = run_loop("08:49:59", 1); check([c[5] for c in calls if c[0] == "publish"][:1] == [epoch(D, "08:50")] and waits >= 2, "tick starts at 08:50")
# wrong calendar day (clock on D+1 or D-1) -> return immediately, no tick
for other in ("2026-09-02", "2026-08-31"):
    txt, waits, ev = run_loop("08:55:00", 1, day=other); check(not calls and waits == 0, ("other day", other))
# stop set before first iteration -> exits without ticking or waiting
ev0 = th_ev[-1]; ev0.set(); clock.set("08:55:00"); calls.clear(); threads[-1].target(); check(not calls, "stop pre-set"); ev0._s = False
# stop set during wait ends the loop after that wait
txt, waits, ev = run_loop("08:55:00", 1, stop_after=2); check(waits == 2 and len([c for c in calls if c[0] == "publish"]) == 2 and ev.is_set(), (waits,))
# tick failure: printed marker, loop keeps going, later tick succeeds
class Flaky:
    n = 0
orig_publish = mod.publish_input
def flaky(**k):
    Flaky.n += 1
    if Flaky.n == 1: raise ValueError("bad producer")
    if Flaky.n == 2: raise OSError("disk")
    return orig_publish(**k)
mod.publish_input = flaky
txt, waits, ev = run_loop("09:11:00", 20, stop_after=4)
check(txt == "q12_input_delivery_error=ValueError\nq12_input_delivery_error=OSError\n", repr(txt)); check([c[5] for c in calls if c[0] == "publish"], "later tick succeeded")
out["flaky_stdout"] = txt
# BaseException (KeyboardInterrupt) from tick is NOT swallowed by the loop
def kbd(**k): raise KeyboardInterrupt()
mod.publish_input = kbd; clock.set("08:55:00"); ke = None; stop._s = False; stop.on_wait = None
try:
    with contextlib.redirect_stdout(io.StringIO()): threads[-1].target()
except BaseException as e: ke = type(e).__name__
check(ke == "KeyboardInterrupt", ke); mod.publish_input = orig_publish
# merge failure inside tick is also reported not raised; research cached across loop ticks (one fetch)
fk.merge_exc = TypeError("m"); txt, waits, ev = run_loop("09:11:00", 20, stop_after=2); check(txt.count("q12_input_delivery_error=TypeError") == 2, txt); fk.merge_exc = None
# each start_input_worker call builds its own worker/event/thread (no sharing)
s2 = mod.start_input_worker(day=D, reports_root=root, state_path=state); check(s2 is not stop and len(threads) == 2 and threads[0] is not threads[1], "independent workers")
# kwargs-only signature
pe = None
try: mod.start_input_worker(D, root, state)
except TypeError as e: pe = "TypeError"
check(pe == "TypeError", "positional args rejected")
check(not bad, bad)
print("RF033_START_INPUT_WORKER_OK", "threads_started=0_real", "loop_ticks=%d" % len(out["loop_ticks"]), "tick_exc=%s/%s" % out["tick_exc"], "kbd=%s" % ke, "writes=0 net_attempts=0", "debug=" + str(__debug__))
