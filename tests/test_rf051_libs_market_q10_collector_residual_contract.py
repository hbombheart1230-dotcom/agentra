"""RF-051 q10_index_observation_collector residual branches: tmp roots + fake readers, no Kiwoom/network."""
from __future__ import annotations

import socket
import sys
import types
from datetime import datetime

import pytest

from libs.market import q10_index_observation_collector as q

DAY = "2026-10-28"
KST = q.KST


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    def deny(*_a, **_k):
        raise AssertionError("real network attempted")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _at(slot, plus=0):
    return lambda: datetime.fromtimestamp(q._slot_epoch(DAY, slot) + plus, tz=KST)


def _pkt(**names):
    return {"status": "ok", "indices": {n: {"current": v, "current_date": "20261028"} for n, v in names.items()}}


def test_default_reader_factory_import_path_and_failures(monkeypatch):
    class FakeReader:
        def get_index_packet(self, indices):
            return {"status": "ok", "indices": {n: {"current": 1.0} for n in indices}}

    mod = types.ModuleType("libs.read.kiwoom_market_index_reader")
    mod.KiwoomMarketIndexReader = types.SimpleNamespace(from_env=lambda: FakeReader())
    monkeypatch.setitem(sys.modules, "libs.read.kiwoom_market_index_reader", mod)
    out = q.capture_q10_index_snapshot(indices=["KOSPI"])
    _eq(sorted(out["indices"]), ["KOSPI"])

    def boom():
        raise RuntimeError("no creds")

    mod.KiwoomMarketIndexReader = types.SimpleNamespace(from_env=boom)
    bad = q.capture_q10_index_snapshot()
    _eq(bad["status"], "unavailable")


def test_claim_write_failure_returns_false(tmp_path, monkeypatch):
    def bad_fsync(_fd):
        raise OSError("disk")

    monkeypatch.setattr(q.os, "fsync", bad_fsync)
    _eq(q._acquire_slot_claim(DAY, "09:30", root=tmp_path), False)


def test_classify_skips_non_mapping_and_rejects_bad_price_and_date():
    packet = {"indices": {
        "KOSPI": "junk",
        "KOSDAQ": {"current": -5, "current_date": "20261028"},
        "OTHER": {"current": 5},
    }}
    row = q._classify_row(day=DAY, slot="09:30", scheduled_at_epoch=q._slot_epoch(DAY, "09:30"),
                          observed_epoch=q._slot_epoch(DAY, "09:30") + 10, packet=packet, window_sec=60)
    _eq(row["indices"], {})
    _eq(sorted(row["rejected_components"]), ["KOSDAQ", "OTHER"])       # non-mapping row is skipped, not rejected
    _eq(row["rejected_components"]["KOSDAQ"], {"reason": "invalid_index_price"})
    _eq(row["availability"], "MISSING")
    stale = q._classify_row(day=DAY, slot="09:30", scheduled_at_epoch=q._slot_epoch(DAY, "09:30"),
                            observed_epoch=q._slot_epoch(DAY, "09:30") + 10,
                            packet={"indices": {"KOSPI": {"current": 1, "current_date": "20250101"}}}, window_sec=60)
    _eq(stale["rejected_components"]["KOSPI"]["reason"], "component_date_mismatch")
    _eq(stale["error"], "all_components_date_mismatch")


def test_capture_exception_is_recorded_as_missing_with_error_text(tmp_path):
    def broken(**_k):
        raise RuntimeError("reader down")

    row = q.capture_slot(day=DAY, slot="09:30", root=tmp_path, now_fn=_at("09:30", 5), capture=broken)
    _eq(row["availability"], "MISSING")
    _eq(row["error"], "RuntimeError: reader down")
    _eq(q.observation_for_slot(DAY, "09:30", root=tmp_path)["availability"], "MISSING")
    again = q.capture_slot(day=DAY, slot="09:30", root=tmp_path, now_fn=_at("09:30", 6), capture=lambda **_: 1 / 0)
    _eq(again["availability"], "MISSING")                                # at-most-once: not captured twice


def test_race_guards_inside_lock(tmp_path, monkeypatch):
    # first read says no row, the in-lock read says otherwise (another process won the race)
    monkeypatch.setattr(q, "load_observations", lambda *a, **k: [])

    def never_called(**_k):
        raise AssertionError("capture must not run")

    monkeypatch.setattr(q, "observation_for_slot", lambda *a, **k: {"availability": "AVAILABLE", "never_attempted": False})
    _eq(q.capture_slot(day=DAY, slot="09:30", root=tmp_path, now_fn=_at("09:30"), capture=never_called)["availability"], "AVAILABLE")
    # force is only for MISSING/LATE_MISSED/PARTIAL*, never for a complete row
    _eq(q.capture_slot(day=DAY, slot="09:30", root=tmp_path, now_fn=_at("09:30"), capture=never_called, force=True)["availability"], "AVAILABLE")
    # claim already held -> CORRUPT_STATE row, still no capture
    monkeypatch.setattr(q, "observation_for_slot", lambda *a, **k: {"availability": "MISSING", "never_attempted": True})
    _eq(q._acquire_slot_claim(DAY, "09:30", root=tmp_path), True)
    row = q.capture_slot(day=DAY, slot="09:30", root=tmp_path, now_fn=_at("09:30"), capture=never_called)
    _eq((row["availability"], row.get("error") or row.get("reason")), ("CORRUPT_STATE", "attempt_claim_already_exists"))


def test_corrupt_in_lock_state_blocks_capture(tmp_path, monkeypatch):
    monkeypatch.setattr(q, "load_observations", lambda *a, **k: [])
    monkeypatch.setattr(q, "observation_for_slot", lambda *a, **k: {"availability": "CORRUPT_STATE"})
    row = q.capture_slot(day=DAY, slot="09:30", root=tmp_path, now_fn=_at("09:30"), capture=lambda **_: 1 / 0)
    _eq(row["availability"], "CORRUPT_STATE")


def test_closeout_requery_waits_for_grace_and_run_due_slots_blocks_on_corrupt_manifest(tmp_path):
    def never_called(**_k):
        raise AssertionError("capture must not run")

    early = q.closeout_requery_if_missing(day=DAY, slot="15:30", root=tmp_path, now_fn=_at("15:30", 5),
                                          capture=never_called, min_ready_grace_sec=300)
    if early.get("requested_at_kst") is not None:
        raise AssertionError(early)                                      # nothing was attempted before the grace window
    manifest = q._manifest_path(DAY, root=tmp_path)
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{not json", encoding="utf-8")
    rows = q.run_due_slots(day=DAY, root=tmp_path, now_fn=_at("15:30", 900), capture=never_called)
    _eq(len(rows), 1)
    _eq((rows[0]["requested_slot"], rows[0]["availability"]), ("*", "CORRUPT_STATE"))
