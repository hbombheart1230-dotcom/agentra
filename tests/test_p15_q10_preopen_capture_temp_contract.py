"""P15-3 (2026-10-29 C02): Q10 preopen capture window / existing-snapshot preservation, tmp_path + fake provider only."""
from __future__ import annotations

import hashlib
import json
import socket
from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import pipeline as pl
from libs.reporting.baseline_samsung_hynix.forward_validation.contracts import ACTIVATION_DAY

KST = timezone(timedelta(hours=9))
DAY = "2026-10-29"
MISSED_REASON = "08:50_preopen_capture_window_missed_no_backfill"


@pytest.fixture(autouse=True)
def _guards(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network attempt / real provider constructed")

    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(pl, "YFinanceLeadMarketProvider", boom)                                 # the real provider must never be created


class FakeProvider:
    def __init__(self, status="AVAILABLE"):
        self.status, self.calls = status, []

    def capture(self, *, as_of):
        self.calls.append(as_of)
        row = {"status": self.status, "return_pct": 6.0, "current": 100.0, "previous": 94.0, "three_day_return_pct": 1.0}
        return {k: dict(row) for k in ("sox", "nvidia", "micron", "samsung", "sk_hynix", "nasdaq", "sp500", "us10y", "vix", "hynix_adr")}


def at(h, m, s=0, day=DAY):
    y, mo, d = map(int, day.split("-"))
    return datetime(y, mo, d, h, m, s, tzinfo=KST)


def snap_path(root, day=DAY):
    return root / "reports" / "evaluation" / "baseline_samsung_hynix" / day / "q10_forward_validation" / "q10_preopen_signal_snapshot.json"


def capture(root, now, provider, day=DAY):
    return pl.capture_q10_preopen_snapshot(day=day, reports_root=root / "reports", state_path=root / "state.json", now=now, lead_market_provider=provider)


def files(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


def test_before_window_0849_59_is_waiting_writes_nothing_and_never_calls_provider(tmp_path):
    p = FakeProvider()
    out = capture(tmp_path, at(8, 49, 59), p)
    assert out == {"q10_preopen_capture_status": "WAITING", "day": DAY, "captured_at_kst": None, "reason": "", "path": ""}
    assert p.calls == [] and files(tmp_path) == []


def test_after_window_0900_00_is_missed_with_one_json_and_no_provider_call(tmp_path):
    p = FakeProvider()
    out = capture(tmp_path, at(9, 0, 0), p)
    assert out["q10_preopen_capture_status"] == "MISSED" and out["reason"] == MISSED_REASON and out["path"] == str(snap_path(tmp_path)) and out["captured_at_kst"] == at(9, 0, 0).isoformat()
    assert p.calls == [] and files(tmp_path) == ["reports/evaluation/baseline_samsung_hynix/2026-10-29/q10_forward_validation/q10_preopen_signal_snapshot.json"]
    saved = json.loads(snap_path(tmp_path).read_text(encoding="utf-8"))
    assert saved["capture_status"] == "MISSED" and saved["reason"] == MISSED_REASON and saved["day"] == DAY and saved["guards"]["historical_backfill_allowed"] is False


@pytest.mark.parametrize("h,m,s", [(8, 50, 0), (8, 59, 59)])
def test_window_edges_each_in_their_own_tmp_root_call_the_provider_exactly_once(tmp_path, h, m, s):
    p = FakeProvider()
    out = capture(tmp_path / f"r{h}{m}{s}", at(h, m, s), p)
    assert len(p.calls) == 1 and p.calls[0] == at(h, m, s) and out["q10_preopen_capture_status"] == "CAPTURED" and out["path"] == str(snap_path(tmp_path / f"r{h}{m}{s}"))
    saved = json.loads(snap_path(tmp_path / f"r{h}{m}{s}").read_text(encoding="utf-8"))
    assert saved["capture_status"] == "CAPTURED" and saved["captured_at_kst"] == at(h, m, s).isoformat() and saved["capture_window_kst"] == [at(8, 50).isoformat(), at(8, 59, 59).isoformat()]
    assert out["captured_at_kst"] == at(h, m, s).isoformat() and out["reason"] == ""


def test_existing_valid_snapshot_is_returned_without_provider_call_and_bytes_are_preserved(tmp_path):
    first = FakeProvider()
    capture(tmp_path, at(8, 51), first)
    path = snap_path(tmp_path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    for now in (at(8, 49), at(8, 55), at(9, 30), at(23, 0)):                                     # any later wall clock: no backfill, no overwrite
        p = FakeProvider("UNAVAILABLE")
        out = capture(tmp_path, now, p)
        assert p.calls == [] and out["q10_preopen_capture_status"] == "CAPTURED" and hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert files(tmp_path) == [str(path.relative_to(tmp_path))]


def test_hand_written_existing_snapshot_is_authoritative_even_when_status_is_odd(tmp_path):
    path = snap_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"capture_status": "DATA_UNAVAILABLE", "reason": "kept", "captured_at_kst": "X"}), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    p = FakeProvider()
    out = capture(tmp_path, at(8, 55), p)
    assert p.calls == [] and out["q10_preopen_capture_status"] == "DATA_UNAVAILABLE" and out["reason"] == "kept" and out["captured_at_kst"] == "X"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_all_unavailable_observations_are_data_unavailable_never_captured(tmp_path):
    p = FakeProvider("UNAVAILABLE")
    out = capture(tmp_path, at(8, 55), p)
    assert len(p.calls) == 1 and out["q10_preopen_capture_status"] == "DATA_UNAVAILABLE" and out["reason"] == "all_lead_market_observations_unavailable"
    saved = json.loads(snap_path(tmp_path).read_text(encoding="utf-8"))
    assert saved["capture_status"] == "DATA_UNAVAILABLE" and saved["observation_summary"] == {"total": 10, "available": 0}
    partial = FakeProvider()
    original = partial.capture

    def one_available(*, as_of):
        obs = original(as_of=as_of)
        obs = {k: {**v, "status": "UNAVAILABLE"} for k, v in obs.items()}
        obs["sox"]["status"] = "AVAILABLE"
        return obs

    partial.capture = one_available
    assert capture(tmp_path / "p", at(8, 55), partial)["q10_preopen_capture_status"] == "CAPTURED"


def test_before_activation_day_is_inactive_and_writes_nothing(tmp_path):
    p = FakeProvider()
    out = capture(tmp_path, at(8, 55, day="2026-08-30"), p, day="2026-08-30")
    assert out == {"q10_preopen_capture_status": "NOT_ACTIVE_PROSPECTIVE_ONLY", "day": "2026-08-30"} and p.calls == [] and files(tmp_path) == []
    assert "2026-08-30" < ACTIVATION_DAY
    on_day = capture(tmp_path / "act", at(8, 55, day=ACTIVATION_DAY), p, day=ACTIVATION_DAY)
    assert on_day["q10_preopen_capture_status"] == "CAPTURED"


def test_return_and_json_key_sets_are_stable(tmp_path):
    out = capture(tmp_path, at(8, 55), FakeProvider())
    assert set(out) == {"q10_preopen_capture_status", "day", "captured_at_kst", "reason", "path"}
    saved = json.loads(snap_path(tmp_path).read_text(encoding="utf-8"))
    assert {"schema_version", "evaluation_program_id", "day", "capture_status", "observation_summary", "captured_at_kst", "capture_window_kst", "observations", "signal_inputs", "signals", "samsung_event", "thresholds", "guards"} <= set(saved)
    assert set(saved["signals"]) == {"sk_hynix", "samsung", "hynix_extension", "korea_market"}


def test_atomic_write_leaves_no_tmp_sibling_and_corrupt_snapshot_is_replaced_by_a_real_capture(tmp_path):
    path = snap_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("{corrupt", encoding="utf-8")
    p = FakeProvider()
    out = capture(tmp_path, at(8, 55), p)
    assert len(p.calls) == 1 and out["q10_preopen_capture_status"] == "CAPTURED" and [x.name for x in path.parent.iterdir()] == [path.name]


def test_state_path_is_only_read_for_the_samsung_event_never_created(tmp_path):
    capture(tmp_path, at(8, 55), FakeProvider())
    assert not (tmp_path / "state.json").exists()
    (tmp_path / "state.json").write_text(json.dumps({"news_items": [{"title": "삼성전자 HBM", "symbols": ["005930"]}]}), encoding="utf-8")
    capture(tmp_path / "w", at(8, 55), FakeProvider())
    capture_with_state = pl.capture_q10_preopen_snapshot(day=DAY, reports_root=tmp_path / "x" / "reports", state_path=tmp_path / "state.json", now=at(8, 55), lead_market_provider=FakeProvider())
    saved = json.loads(snap_path(tmp_path / "x").read_text(encoding="utf-8"))
    assert capture_with_state["q10_preopen_capture_status"] == "CAPTURED" and saved["samsung_event"]["samsung_specific_event"] is True
