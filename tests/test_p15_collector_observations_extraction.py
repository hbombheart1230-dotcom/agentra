"""P15 order 2: _collector_raw_row MOVE to collector_observations.py - parity with the frozen pre-extraction output plus the
market-timestamp integrity fix. Collector module is replaced in sys.modules (no Kiwoom call, no files)."""
from __future__ import annotations

import ast
import json
import sys
import types
from pathlib import Path

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import collector_observations as co
from libs.reporting.baseline_samsung_hynix.forward_validation import reaction_reader as rr

DAY = "2026-09-07"
EXPECTED = json.loads(r'''{"absent":null,"bad_observed_time":{"actual_observed_at_kst":"nope","collector_status":"AVAILABLE","integrity_failure":true,"reason":"observed_timestamp_unparseable","requested_at_kst":null},"corrupt":{"actual_observed_at_kst":null,"collector_status":"CORRUPT_STATE","integrity_failure":true,"reason":"collector_observation_not_calculation_usable","requested_at_kst":null,"unverified_observation":null},"evidence_invalid":{"collector_status":"AVAILABLE","integrity_failure":true,"reason":"verification_evidence_invalid"},"index_missing":{"actual_observed_at_kst":"2026-09-07T09:30:05+09:00","collector_status":"AVAILABLE","integrity_failure":true,"reason":"index_component_not_present_in_verified_observation","requested_at_kst":null},"late_missed":{"actual_observed_at_kst":"a","collector_status":"LATE_MISSED","integrity_failure":true,"reason":"too late","requested_at_kst":"r","unverified_observation":{"calculation_usable":false,"capture_status":"LATE_MISSED","observed_at_kst":"a","price":5.0,"requested_at_kst":"r","source":"src"}},"missing_not_never_attempted":{"actual_observed_at_kst":null,"collector_status":"MISSING","integrity_failure":true,"reason":"collector_observation_not_calculation_usable","requested_at_kst":null,"unverified_observation":null},"partial_verified":{"capture_status":"PARTIAL","close":2400.0,"open":2400.0,"source":"q10_index_observation_collector","ts":1788741000,"volume":null},"verified":{"capture_status":"AVAILABLE","close":2500.0,"open":2500.0,"source":"q10_index_observation_collector","ts":1788741000,"volume":null}}''')


@pytest.fixture
def state(monkeypatch):
    st = {"obs": {}, "evidence": True, "calls": []}
    mod = types.ModuleType("libs.market.q10_index_observation_collector")

    def observation_for_slot(day, slot, root=None):
        st["calls"].append((day, slot, root))
        return st["obs"]

    mod.observation_for_slot = observation_for_slot
    mod._has_verification_evidence = lambda indices, **kw: st["evidence"]
    monkeypatch.setitem(sys.modules, "libs.market.q10_index_observation_collector", mod)
    return st


def ver(price=2500.0, obs_at="2026-09-07T09:30:05+09:00", mkt="2026-09-07T09:30:00+09:00"):
    row = {"current": price}
    if mkt:
        row["market_observed_at"] = mkt
    return {"availability": "AVAILABLE", "actual_observed_at_kst": obs_at, "source": "kiwoom.ka20009", "indices": {"KOSPI": row}}


CASES = {
    "absent": ({"availability": "MISSING", "never_attempted": True}, True, "KOSPI"),
    "missing_not_never_attempted": ({"availability": "MISSING"}, True, "KOSPI"),
    "late_missed": ({"availability": "LATE_MISSED", "error": "too late", "indices": {"KOSPI": {"current": 5.0}}, "source": "src", "requested_at_kst": "r", "actual_observed_at_kst": "a"}, True, "KOSPI"),
    "corrupt": ({"availability": "CORRUPT_STATE"}, True, "KOSPI"),
    "evidence_invalid": (ver(), False, "KOSPI"),
    "index_missing": (ver(), True, "KOSDAQ"),
    "bad_observed_time": ({**ver(), "actual_observed_at_kst": "nope"}, True, "KOSPI"),
    "verified": (ver(2500.0), True, "KOSPI"),
    "partial_verified": ({**ver(2400.0), "availability": "PARTIAL"}, True, "KOSPI"),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_wrapper_and_owner_match_frozen_pre_extraction_output(state, name):
    obs, ev, idx = CASES[name]
    state["obs"], state["evidence"] = obs, ev
    via_wrapper = rr._collector_raw_row(day=DAY, index_name=idx, slot="09:30", root=None)
    direct = co.collector_raw_row_impl(day=DAY, index_name=idx, slot="09:30", root=None, facade=rr)
    assert json.loads(json.dumps(via_wrapper, sort_keys=True)) == EXPECTED[name] == json.loads(json.dumps(direct, sort_keys=True))


def test_tristate_categories():
    assert EXPECTED["absent"] is None
    for k in ("missing_not_never_attempted", "late_missed", "corrupt", "evidence_invalid", "index_missing", "bad_observed_time"):
        assert EXPECTED[k]["integrity_failure"] is True
    assert EXPECTED["late_missed"]["unverified_observation"]["price"] == 5.0 and EXPECTED["late_missed"]["unverified_observation"]["calculation_usable"] is False
    assert EXPECTED["index_missing"]["reason"] == "index_component_not_present_in_verified_observation" and EXPECTED["bad_observed_time"]["reason"] == "observed_timestamp_unparseable"
    for k in ("verified", "partial_verified"):
        assert set(EXPECTED[k]) == {"ts", "close", "open", "volume", "source", "capture_status"} and EXPECTED[k]["source"] == "q10_index_observation_collector"


def test_slot_and_root_are_passed_to_the_observation_reader(state):
    state["obs"] = {"availability": "MISSING", "never_attempted": True}
    rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="15:30", root="/tmp/x")
    assert state["calls"] == [(DAY, "15:30", "/tmp/x")]


def test_market_timestamp_missing_is_integrity_failure_not_typeerror(state):
    """Before the fix this exact input raised TypeError from int(None); the legacy fallback must stay forbidden."""
    obs = ver(mkt=None)
    state["obs"] = obs
    for fn in (lambda: rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None), lambda: co.collector_raw_row_impl(day=DAY, index_name="KOSPI", slot="09:30", root=None, facade=rr)):
        r = fn()
        assert r == {"integrity_failure": True, "collector_status": "AVAILABLE", "reason": "market_timestamp_missing",
                     "requested_at_kst": None, "actual_observed_at_kst": "2026-09-07T09:30:05+09:00"}
    bad = ver(mkt="not-a-date")
    state["obs"] = bad
    assert rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)["reason"] == "market_timestamp_missing"


def test_missing_market_timestamp_blocks_legacy_fallback_end_to_end(state):
    state["obs"] = ver(mkt=None)
    legacy = [{"ts": 1_788_000_000, "close": 9.0, "open": 9.0, "high": 9.0, "low": 9.0, "volume": None, "previous_close": 8.0}]
    out = rr._index_reaction(day=DAY, target={"key": "kospi", "symbol": "KOSPI", "kind": "index"}, rows=legacy)
    p = out["points"]["09:30"]
    assert p["status"] == "PENDING" and p["integrity_failure"] is True and p["integrity_reason"] == "market_timestamp_missing"


def test_facade_constants_and_number_are_resolved_at_call_time(state, monkeypatch):
    state["obs"] = {"availability": "AVAILABLE", "actual_observed_at_kst": "2026-09-07T09:30:05+09:00", "indices": {"KOSPI": {"current": 5.0}}}
    monkeypatch.setattr(rr, "_COLLECTOR_VERIFIED_STATES", frozenset({"PARTIAL"}))
    assert rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)["integrity_failure"] is True      # AVAILABLE no longer verified
    monkeypatch.setattr(rr, "_COLLECTOR_VERIFIED_STATES", frozenset({"AVAILABLE", "PARTIAL"}))
    monkeypatch.setattr(rr, "market_epoch", lambda row: 42.9)
    assert rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)["ts"] == 42
    monkeypatch.setattr(rr, "_number", lambda v: 777.0)
    assert rr._collector_raw_row(day=DAY, index_name="KOSPI", slot="09:30", root=None)["close"] == 777.0


def test_wrapper_delegates_to_owner_and_owner_does_not_import_facade(monkeypatch):
    seen = {}
    monkeypatch.setattr(rr, "collector_raw_row_impl", lambda **kw: seen.update(kw) or "X")
    assert rr._collector_raw_row(day=DAY, index_name="K", slot="s", root=None) == "X" and seen["facade"] is sys.modules[rr.__name__]
    path = Path(co.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert "reaction_reader" not in " ".join(m or "" for m in mods) and len(path.read_text(encoding="utf-8").splitlines()) <= 350
    # the collector module is still imported lazily inside the function (not at import time)
    assert not any((m or "").startswith("libs.market.q10_index_observation_collector") for m in {n.module for n in tree.body if isinstance(n, ast.ImportFrom)})
