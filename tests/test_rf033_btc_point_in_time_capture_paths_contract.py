"""RF-033 C3: BTC point_in_time_capture dependency/loader paths, source freshness, merge and ledger de-dup (tmp root only)."""
from __future__ import annotations

import json
import socket
from datetime import datetime, timedelta, timezone

import pytest

from libs.market.yfinance_support import DataSourceDependencyError
from libs.reporting.baseline_btc_woori_tech import data_provider as dp
from libs.reporting.baseline_btc_woori_tech import point_in_time_capture as pit

KST = timezone(timedelta(hours=9))
DAY = "2026-10-28"
TARGET = datetime(2026, 10, 28, 8, 55, tzinfo=KST)
T = int(TARGET.timestamp())


@pytest.fixture(autouse=True)
def _deny(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)


def at(h, m, s=0):
    return datetime(2026, 10, 28, h, m, s, tzinfo=KST)


def loader(rows_usd=None, rows_krw=None):
    def f(*, day):
        return {"sources": {"btc_usd": rows_usd or [], "btc_krw": rows_krw or [], "coinbase_proxy": [{"ts": T, "close": 9}]}}

    return f


def test_source_points_freshness_boundary_future_rows_and_filtering():
    sp = pit._source_points
    fresh = {"sources": {"btc_usd": [{"ts": T - 900, "close": 1}, {"ts": T - 1000, "close": 0}, {"ts": T + 1, "close": 9}, "junk"], "btc_krw": [{"ts": T - 901, "close": 2}]}}
    out = sp(fresh, target_epoch=T)
    assert list(out) == ["btc_usd"] and out["btc_usd"] == [{"ts": T - 900, "close": 1, "capture_age_sec": 900}]          # 900s inclusive; 901s excluded; future ignored
    assert sp({}, target_epoch=T) == {} and sp({"sources": {"btc_usd": [{"ts": 0}]}}, target_epoch=T) == {}
    latest = sp({"sources": {"btc_usd": [{"ts": T - 120, "close": 1}, {"ts": T - 60, "close": 2}]}}, target_epoch=T)
    assert latest["btc_usd"][0]["close"] == 2 and latest["btc_usd"][0]["capture_age_sec"] == 60
    assert "coinbase_proxy" not in sp({"sources": {"coinbase_proxy": [{"ts": T}]}}, target_epoch=T)


def test_captured_when_btc_usd_present_and_missing_when_only_krw(tmp_path):
    ok = pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 56), signal_loader=loader([{"ts": T - 30, "close": 5}]))
    assert ok["capture_status"] == "CAPTURED" and ok["snapshot_submitted"] is True and ok["available_sources"] == ["btc_usd"] and ok["reason"] == ""
    miss = pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "b", now=at(8, 56), signal_loader=loader(rows_krw=[{"ts": T - 30, "close": 5}]))
    assert miss["capture_status"] == "MISSING" and miss["reason"] == "btc_usd_point_in_time_source_missing" and miss["available_sources"] == ["btc_krw"]
    again = pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "b", now=at(8, 57), signal_loader=loader([{"ts": T - 30, "close": 5}]))
    assert again["capture_status"] == "CAPTURED"                                                            # MISSING is retryable inside the window, unlike CAPTURED/MISSED


def test_captured_and_missed_snapshots_are_immutable(tmp_path):
    pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 56), signal_loader=loader([{"ts": T, "close": 5}]))
    first = pit.capture_paths(DAY, root=tmp_path)["snapshot"].read_text(encoding="utf-8")
    calls = []
    pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 57), signal_loader=lambda **k: calls.append(1) or {})
    assert calls == [] and pit.capture_paths(DAY, root=tmp_path)["snapshot"].read_text(encoding="utf-8") == first
    m = pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "m", now=at(9, 0), signal_loader=loader())
    assert m["capture_status"] == "MISSED" and pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "m", now=at(8, 56), signal_loader=loader([{"ts": T, "close": 1}]))["capture_status"] == "MISSED"


def test_window_boundaries_waiting_and_deadline(tmp_path):
    assert pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "w", now=at(8, 54, 59), signal_loader=loader())["capture_status"] == "WAITING"
    assert pit.capture_paths(DAY, root=tmp_path / "w")["snapshot"].exists() is False                         # WAITING is never persisted as a snapshot
    assert pit.capture_paths(DAY, root=tmp_path / "w")["ledger"].exists() is True
    assert pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "s", now=at(8, 55), signal_loader=loader())["capture_status"] == "MISSING"
    assert pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "d", now=at(8, 59, 59), signal_loader=loader())["capture_status"] == "MISSING"
    assert pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path / "x", now=at(8, 59, 59, ) + timedelta(seconds=1), signal_loader=loader())["capture_status"] == "MISSED"


def test_dependency_missing_is_explicit_and_persisted(tmp_path, monkeypatch):
    def missing():
        raise DataSourceDependencyError("yfinance", "ImportError: x")

    monkeypatch.setattr(pit, "require_yfinance", missing)
    out = pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 56))
    assert out["capture_status"] == "DEPENDENCY_MISSING" and out["reason"] == "dependency_missing:yfinance" and "yfinance" in out["error"]
    assert out["available_sources"] == [] and out["target_epoch"] == T
    assert json.loads(pit.capture_paths(DAY, root=tmp_path)["snapshot"].read_text(encoding="utf-8"))["capture_status"] == "DEPENDENCY_MISSING"
    # not terminal: a later attempt with the dependency restored can still capture
    monkeypatch.setattr(pit, "require_yfinance", lambda: object())
    monkeypatch.setattr(dp, "load_btc_signal_rows", lambda *, day, include_research_context: {"sources": {"btc_usd": [{"ts": T - 10, "close": 3}]}})
    assert pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 57))["capture_status"] == "CAPTURED"


def test_default_loader_path_requests_no_research_context(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(pit, "require_yfinance", lambda: object())

    def rows(*, day, include_research_context):
        seen.update(day=day, research=include_research_context)
        return {"sources": {}}

    monkeypatch.setattr(dp, "load_btc_signal_rows", rows)
    out = pit.capture_q12_btc_0855_snapshot(day=f"{DAY}T00:00", root=tmp_path, now=at(8, 56))
    assert seen == {"day": DAY, "research": False} and out["capture_status"] == "MISSING"


def test_ledger_dedups_identical_attempts_and_counts_distinct_ones(tmp_path):
    for _ in range(2):
        pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 54), signal_loader=loader())
    pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 53), signal_loader=loader())
    led = json.loads(pit.capture_paths(DAY, root=tmp_path)["ledger"].read_text(encoding="utf-8"))
    assert led["attempt_count"] == 2 and led["latest_status"] == "WAITING" and led["schema_version"] == "q12_btc_0855_capture_ledger.v1" and led["snapshot_path"].endswith("btc_0855_snapshot.json")


def test_merge_unions_captured_rows_by_epoch_and_clears_fallback_reasons(tmp_path):
    pit.capture_q12_btc_0855_snapshot(day=DAY, root=tmp_path, now=at(8, 56), signal_loader=loader([{"ts": T - 30, "close": 5}]))
    payload = {"sources": {"btc_usd": [{"ts": T - 30, "close": 1.0}, {"ts": T - 90, "close": 4.0}, {"ts": 0, "close": 9}, "junk"], "other": []}, "fallback_reason": "fresh_fetch_disabled"}
    out = pit.merge_capture_into_signal_payload(payload, day=DAY, root=tmp_path)
    assert [r["close"] for r in out["sources"]["btc_usd"]] == [4.0, 5]                                    # captured row wins on the same epoch; zero-ts dropped
    assert out["available_sources"] == ["btc_usd"] and out["available"] is True and out["btc_0855_capture_reused"] is True and out["btc_0855_capture_status"] == "CAPTURED"
    assert out["fallback_reason"] == "" and out["btc_0855_captured_sources"]["btc_usd"][0]["close"] == 5
    kept = pit.merge_capture_into_signal_payload({"fallback_reason": "other", "sources": {"btc_usd": [{"ts": 1, "close": 1}]}}, day=DAY, root=tmp_path / "none")
    assert kept["fallback_reason"] == "other" and kept["btc_0855_capture_reused"] is False and kept["btc_0855_capture_status"] == ""
    empty = pit.merge_capture_into_signal_payload(None, day=DAY, root=tmp_path / "none")
    assert empty["available"] is False and empty["available_sources"] == [] and empty["sources"] == {}
    cleared = pit.merge_capture_into_signal_payload({"fallback_reason": "btc_and_crypto_proxy_unavailable"}, day=DAY, root=tmp_path)
    assert cleared["fallback_reason"] == ""


def test_load_captured_sources_only_when_status_captured_and_read_fail_soft(tmp_path):
    path = pit.capture_paths(DAY, root=tmp_path)["snapshot"]
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"capture_status": "MISSING", "sources": {"btc_usd": [{"ts": 1}]}}), encoding="utf-8")
    assert pit.load_captured_sources(DAY, root=tmp_path) == {}
    path.write_text("{bad", encoding="utf-8")
    assert pit.load_capture_snapshot(DAY, root=tmp_path) == {}
    path.write_text("[1]", encoding="utf-8")
    assert pit.load_capture_snapshot(DAY, root=tmp_path) == {}
    path.write_text(json.dumps({"capture_status": "CAPTURED", "sources": {"btc_usd": [{"ts": 1}, "x"], "bad": None}}), encoding="utf-8")
    assert pit.load_captured_sources(f"{DAY}T09:00", root=tmp_path) == {"btc_usd": [{"ts": 1}], "bad": []}
    assert pit.capture_paths(f"{DAY}T09:00", root=tmp_path)["snapshot"] == path
