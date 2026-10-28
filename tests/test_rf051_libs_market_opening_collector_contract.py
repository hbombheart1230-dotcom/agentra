"""RF-051 opening_macro_snapshot_collector C2/C3: failure/SLA/manifest edges, tmp_path only.

``capture`` and ``now_fn`` are injected, so no yfinance/network/sleep happens;
``run_collector`` is only run for a past day so its loop exits immediately.
Complements tests/test_opening_macro_snapshot_collector.py. Explicit raises
keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
from datetime import datetime, time as clock_time, timedelta
from pathlib import Path

from libs.market import opening_macro_snapshot_collector as oc
from libs.market.opening_macro_snapshot_collector import KST, capture_slot, mark_missed_slots, run_collector, scheduled_slots

DAY = "2026-08-27"


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _sched(h, m):
    return datetime(2026, 8, 27, h, m, tzinfo=KST)


def _clock(*deltas, base=None):
    base = base or _sched(9, 0)
    it = iter(base + timedelta(seconds=d) for d in deltas)
    return lambda: next(it)


def test_failed_capture_is_recorded_with_error_and_sla_flags(tmp_path):
    mp = tmp_path / "m" / "manifest.json"

    def boom(**kw):
        raise RuntimeError("yfinance unavailable")

    row = capture_slot(day=DAY, scheduled_at=_sched(9, 0), manifest_path=mp, macro_root=tmp_path / "macro",
                       now_fn=_clock(61, 70), capture=boom)
    _eq((row["status"], row["error"], row["signal_status"], row["signal_source"], row["source_path"]),
        ("CAPTURE_FAILED", "RuntimeError: yfinance unavailable", "unavailable", "", ""))
    _eq((row["start_delay_sec"], row["within_sla"], row["duration_sec"], row["freshness_sla_sec"]), (61, False, 9, 60))
    saved = json.loads(mp.read_text(encoding="utf-8"))
    _eq((saved["behavior_effect"], saved["schema_version"], saved["scope"], saved["day"]),
        ("observation_only", oc.SCHEMA_VERSION, "opening_lead_market_08_50_to_09_20", DAY))
    _eq(sorted(x.name for x in mp.parent.iterdir()), ["manifest.json"])   # temp file replaced, none left behind


def test_capture_without_new_artifact_is_failed_even_if_capture_reports_ok(tmp_path):
    row = capture_slot(day=DAY, scheduled_at=_sched(9, 0), manifest_path=tmp_path / "m.json", macro_root=tmp_path / "macro",
                       now_fn=_clock(60, 61), capture=lambda **kw: {"status": "ok", "source": "fx"})
    _eq((row["status"], row["error"], row["signal_status"], row["within_sla"], row["start_delay_sec"]),
        ("CAPTURE_FAILED", "macro_snapshot_artifact_not_created", "ok", True, 60))   # exactly 60 s is still within SLA


def test_early_start_has_zero_delay_and_pre_existing_artifact_does_not_count(tmp_path):
    macro = tmp_path / "macro"
    old = macro / DAY / "085000_macro_indicators.json"
    old.parent.mkdir(parents=True)
    old.write_text("{}", encoding="utf-8")
    row = capture_slot(day=DAY, scheduled_at=_sched(9, 1), manifest_path=tmp_path / "m.json", macro_root=macro,
                       now_fn=_clock(-30, -29), capture=lambda **kw: {"status": "ok", "source": "fx"})
    _eq((row["start_delay_sec"], row["status"], row["source_path"]), (0, "CAPTURE_FAILED", ""))
    # an overwrite of the same file (new mtime) is detected as a new artifact
    def rewrite(**kw):
        old.write_text("{\"n\": 1}", encoding="utf-8")
        import os
        os.utime(old, ns=(old.stat().st_atime_ns, old.stat().st_mtime_ns + 5_000_000_000))
        return {}

    row2 = capture_slot(day=DAY, scheduled_at=_sched(9, 2), manifest_path=tmp_path / "m.json", macro_root=macro,
                        now_fn=_clock(0, 1), capture=rewrite)
    _eq((row2["status"], row2["source_path"], row2["signal_status"]), ("CAPTURED", str(old), "unavailable"))


def test_existing_slot_is_returned_without_calling_capture_and_manifest_stays_sorted(tmp_path):
    mp = tmp_path / "m.json"
    calls = []

    def cap(**kw):
        calls.append(1)
        return {}

    capture_slot(day=DAY, scheduled_at=_sched(9, 5), manifest_path=mp, macro_root=tmp_path / "x", now_fn=_clock(0, 1), capture=cap)
    capture_slot(day=DAY, scheduled_at=_sched(8, 55), manifest_path=mp, macro_root=tmp_path / "x", now_fn=_clock(0, 1), capture=cap)
    again = capture_slot(day=DAY, scheduled_at=_sched(9, 5), manifest_path=mp, macro_root=tmp_path / "x", now_fn=_clock(0, 1), capture=cap)
    _eq(len(calls), 2)
    _eq(again["slot"], "09:05")
    _eq([r["slot"] for r in json.loads(mp.read_text(encoding="utf-8"))["slots"]], ["08:55", "09:05"])


def test_manifest_for_another_day_or_corrupt_file_is_reset(tmp_path):
    mp = tmp_path / "m.json"
    mp.write_text(json.dumps({"day": "2026-08-26", "slots": [{"slot": "09:00"}]}), encoding="utf-8")
    _eq(oc._read_manifest(mp, DAY)["slots"], [])
    mp.write_text("{bad", encoding="utf-8")
    _eq(oc._read_manifest(mp, DAY)["slots"], [])
    mp.write_text("[1]", encoding="utf-8")
    _eq(oc._read_manifest(mp, DAY)["slots"], [])
    _eq(oc._read_manifest(tmp_path / "none.json", DAY)["day"], DAY)
    mp.write_text(json.dumps({"day": DAY, "slots": [{"slot": "09:00", "status": "CAPTURED"}]}), encoding="utf-8")
    _eq(oc._read_manifest(mp, DAY)["slots"], [{"slot": "09:00", "status": "CAPTURED"}])


def test_mark_missed_grace_boundary_idempotence_and_known_slots_skipped(tmp_path):
    mp = tmp_path / "m.json"
    # at 08:51:00 the 08:50 slot is exactly 60 s late -> still within grace, nothing marked
    _eq(mark_missed_slots(day=DAY, now=_sched(8, 51), manifest_path=mp), [])
    _eq(mp.exists(), False)   # nothing added -> no write
    added = mark_missed_slots(day=DAY, now=_sched(8, 51) + timedelta(seconds=1), manifest_path=mp)
    _eq([r["slot"] for r in added], ["08:50"])
    _eq((added[0]["status"], added[0]["start_delay_sec"], added[0]["within_sla"], added[0]["reason"]),
        ("MISSED", 61, False, "collector_not_running_or_capture_overrun"))
    _eq(mark_missed_slots(day=DAY, now=_sched(8, 51) + timedelta(seconds=1), manifest_path=mp), [])   # idempotent
    # a captured slot is never overwritten as MISSED
    capture_slot(day=DAY, scheduled_at=_sched(8, 55), manifest_path=mp, macro_root=tmp_path / "x", now_fn=_clock(-300, -299), capture=lambda **kw: {})
    rows = mark_missed_slots(day=DAY, now=_sched(9, 30), manifest_path=mp)
    _eq(len(rows), 25 - 2)
    _eq("08:55" in {r["slot"] for r in rows}, False)
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    _eq(len(manifest["slots"]), 25)
    _eq([r["slot"] for r in manifest["slots"]], sorted(r["slot"] for r in manifest["slots"]))


def test_run_collector_for_a_past_day_returns_summary_without_looping(tmp_path):
    mp = tmp_path / "m.json"
    mp.write_text(json.dumps({"day": "2020-01-02", "slots": [{"slot": "09:00", "status": "CAPTURED"}, {"slot": "09:01", "status": "MISSED"}]}), encoding="utf-8")
    out = run_collector(day="2020-01-02", manifest_path=mp, keepalive_until=clock_time(0, 0))
    _eq(out, {"day": "2020-01-02", "captured": 1, "slot_count": 25, "manifest_path": str(mp)})
    _eq(len(scheduled_slots("2020-01-02")), 25)
    _eq(scheduled_slots("2020-01-02T10:00:00")[0].strftime("%Y-%m-%d %H:%M"), "2020-01-02 08:50")   # day string is truncated to 10 chars


class _ClockDT(datetime):
    """datetime whose now() walks through a scripted list (last value repeats); combine() stays real."""
    script: list = []
    idx = 0

    @classmethod
    def now(cls, tz=None):
        i = min(cls.idx, len(cls.script) - 1)
        cls.idx += 1
        return cls.script[i]


def test_run_collector_loop_marks_missed_captures_due_slot_then_sleeps_and_stops(tmp_path, monkeypatch):
    s = lambda h, m, sec: datetime(2026, 8, 27, h, m, sec, tzinfo=KST)
    # two now() calls per iteration (loop condition + body); iteration 3 starts after the 09:01:00 session end
    _ClockDT.script, _ClockDT.idx = [s(9, 0, 30), s(9, 0, 30), s(9, 0, 31), s(9, 0, 31), s(9, 1, 30)], 0
    monkeypatch.setattr(oc, "datetime", _ClockDT)
    slept, captured_slots = [], []
    monkeypatch.setattr(oc.time, "sleep", slept.append)
    mp = tmp_path / "m.json"

    def fake_capture_slot(*, day, scheduled_at, manifest_path, **kw):
        captured_slots.append(scheduled_at.strftime("%H:%M"))
        manifest = oc._read_manifest(manifest_path, day)
        manifest["slots"].append({"slot": scheduled_at.strftime("%H:%M"), "status": "CAPTURED"})
        oc._write_manifest(manifest_path, manifest)

    monkeypatch.setattr(oc, "capture_slot", fake_capture_slot)
    out = run_collector(day=DAY, manifest_path=mp, poll_sec=0.0, keepalive_until=clock_time(9, 1))
    _eq(captured_slots, ["09:00"])                       # only the slot inside its 60 s window is captured
    _eq(slept, [0.1])                                    # idle iteration sleeps max(0.1, poll_sec)
    rows = {r["slot"]: r["status"] for r in json.loads(mp.read_text(encoding="utf-8"))["slots"]}
    _eq([rows[k] for k in ("08:50", "08:55", "08:58", "08:59")], ["MISSED"] * 4)   # earlier slots are marked missed first
    _eq(rows["09:00"], "CAPTURED")
    _eq((out["day"], out["captured"], out["slot_count"], out["manifest_path"]), (DAY, 1, 25, str(mp)))
