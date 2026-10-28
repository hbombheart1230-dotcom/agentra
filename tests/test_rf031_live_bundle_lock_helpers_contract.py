"""RF-031 live caller `live_execution_bundle_runner`: background-job lock helpers, tmp_path only.

The live caller itself (``main``) is NOT executed. These tests pin the lock semantics that decide what
happens to a bundle job when the reporter-analysis stage raises (the caller registers
``_clear_background_job_lock`` with ``atexit`` and does not wrap ``_load_or_generate_reporter_analysis``).
Signal 0 is the only OS interaction (``os.kill(pid, 0)`` inside ``_pid_active``); no process is
terminated. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import os
import time

from libs.reporting import live_execution_bundle_runner as lr


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _write(path, **fields):
    path.write_text(json.dumps(fields), encoding="utf-8")


def test_none_paths_are_noops():
    _eq((lr._write_background_job_lock(None, status="running", role="r"), lr._touch_background_job_lock(None, role="r"),
         lr._clear_background_job_lock(None), lr._active_background_job(None)), (None, None, None, {}))


def test_write_touch_clear_lifecycle_for_own_pid(tmp_path):
    p = tmp_path / "locks" / "job.lock"
    lr._write_background_job_lock(p, status="running", role="intraday_trade_report_bundle", extra={"target_run_id": "r1"})
    d = json.loads(p.read_text(encoding="utf-8"))
    _eq((d["pid"], d["status"], d["target_run_id"], d["script"]), (os.getpid(), "running", "r1", "run_live_execution_bundle_report.py"))
    created = d["created_at_epoch"]
    time.sleep(0.01)
    lr._touch_background_job_lock(p, role="intraday_trade_report_bundle", extra={"current_run_id": "r2"})
    t = json.loads(p.read_text(encoding="utf-8"))
    _eq((t["current_run_id"], t["target_run_id"], t["created_at_epoch"]), ("r2", "r1", created))      # heartbeat refreshed, identity kept
    if not t["touched_at_epoch"] > created:
        raise AssertionError("touch must advance the heartbeat")
    lr._clear_background_job_lock(p)
    _eq(p.exists(), False)
    lr._clear_background_job_lock(p)                                                                   # idempotent
    lr._touch_background_job_lock(p, role="r")                                                          # touch recreates a missing lock
    _eq(json.loads(p.read_text(encoding="utf-8"))["pid"], os.getpid())


def test_foreign_owner_lock_is_never_cleared_or_touched(tmp_path):
    p = tmp_path / "job.lock"
    foreign = os.getpid() + 7
    _write(p, pid=foreign, status="running", touched_at_epoch=time.time())
    lr._clear_background_job_lock(p)
    _eq(p.exists(), True)                                                                              # not ours -> left alone
    before = p.read_text(encoding="utf-8")
    lr._touch_background_job_lock(p, role="r", extra={"x": 1})
    _eq(p.read_text(encoding="utf-8"), before)
    p.write_text("{corrupt", encoding="utf-8")
    lr._clear_background_job_lock(p)
    _eq(p.exists(), False)                                                                             # unreadable lock has owner 0 -> removed
    _write(p, pid=0)
    lr._clear_background_job_lock(p)
    _eq(p.exists(), False)


def test_write_failure_is_swallowed(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    _eq(lr._write_background_job_lock(blocker / "sub" / "job.lock", status="running", role="r"), None)   # parent is a file -> silently ignored


def test_active_background_job_cases(tmp_path):
    p = tmp_path / "job.lock"
    _eq(lr._active_background_job(p), {})                                                              # missing
    p.write_text("{bad", encoding="utf-8")
    _eq(lr._active_background_job(p), {})                                                              # corrupt -> {} (file kept)
    _eq(p.exists(), True)
    _write(p)                                                                                          # empty payload
    _eq(lr._active_background_job(p), {})
    # own pid: reported as active with detection_source=lock
    _write(p, pid=os.getpid(), role="intraday_trade_report_bundle", touched_at_epoch=time.time())
    own = lr._active_background_job(p)
    _eq((own["pid"], own["detection_source"], own["lock_path"]), (os.getpid(), "lock", str(p)))
    # live foreign pid (parent process) with a fresh heartbeat: active
    _write(p, pid=os.getppid(), role="intraday_trade_report_bundle", touched_at_epoch=time.time())
    _eq(lr._active_background_job(p)["pid"], os.getppid())
    # live foreign pid but stale heartbeat: removed as stale
    _write(p, pid=os.getppid(), role="intraday_trade_report_bundle", touched_at_epoch=time.time() - 5000)
    _eq(lr._active_background_job(p, stale_after_sec=900.0), {})
    _eq(p.exists(), False)
    # dead foreign pid with a fresh heartbeat: removed
    _write(p, pid=2_000_000_000, role="intraday_trade_report_bundle", touched_at_epoch=time.time())
    _eq(lr._active_background_job(p), {})
    _eq(p.exists(), False)
    # pid helper edge cases
    _eq((lr._pid_active(0), lr._pid_active(-5), lr._pid_active(os.getpid())), (False, False, True))
