"""RF-034 C3: opening_rank1_shadow.observability helpers, conditional lanes and the point-in-time assembly (pure)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.opening_rank1_shadow import observability as ob

KST = timezone(timedelta(hours=9))


def ep(h, m, s=0):
    return int(datetime(2026, 9, 7, h, m, s, tzinfo=KST).timestamp())


def bar(h, m, close, volume=10.0, open_=None):
    return {"ts": ep(h, m), "open": close if open_ is None else open_, "close": close, "volume": volume}


def test_number_pct_first_number_completed_return():
    assert ob._number(None) is None and ob._number("") is None and ob._number("x") is None and ob._number("2") == 2.0 and ob._number(0) == 0.0
    assert ob._pct(110.0, 100.0) == 10.0 and ob._pct(None, 1.0) is None and ob._pct(1.0, 0.0) is None and ob._pct(1.0, -1.0) is None
    assert ob._first_number([{"a": None}, {"a": "", "b": 3}], "a", "b") == 3.0 and ob._first_number([], "a") is None and ob._first_number([{"a": 0}], "a") == 0.0
    rows = [{"close": 100.0}, {"close": 101.0}, {"close": 102.0}]
    assert ob._completed_return(rows, 1) == pytest.approx(0.9901) and ob._completed_return(rows, 2) == 2.0 and ob._completed_return(rows, 3) is None


def test_opening_relative_volume_uses_median_of_last_ten_prior_days_same_bar_count():
    completed = [{"volume": 10.0}, {"volume": 20.0}]
    ref = []
    for d in range(1, 13):                                                      # 12 prior days: only the latest 10 count
        day_ts = int(datetime(2026, 8, d, 9, 0, tzinfo=KST).timestamp())
        ref += [{"ts": day_ts, "volume": float(d)}, {"ts": day_ts + 60, "volume": float(d)}, {"ts": day_ts + 120, "volume": 999.0}]
    ref.append({"ts": int(datetime(2026, 9, 7, 9, 0, tzinfo=KST).timestamp()), "volume": 1e9})        # same day excluded
    ref.append({"ts": 0, "volume": 1e9})
    got = ob._opening_relative_volume(completed=completed, reference_rows=ref, day="2026-09-07")
    sums = sorted(2.0 * d for d in range(3, 13))
    assert got == round(30.0 / ((sums[4] + sums[5]) / 2), 4)
    assert ob._opening_relative_volume(completed=[], reference_rows=ref, day="2026-09-07") is None
    assert ob._opening_relative_volume(completed=completed, reference_rows=[], day="2026-09-07") is None
    short = [{"ts": int(datetime(2026, 8, 1, 9, 0, tzinfo=KST).timestamp()), "volume": 5.0}]            # only 1 bar < 2 needed
    assert ob._opening_relative_volume(completed=completed, reference_rows=short, day="2026-09-07") is None
    zero = [{"ts": int(datetime(2026, 8, 1, 9, 0, tzinfo=KST).timestamp()) + i * 60, "volume": 0.0} for i in range(2)]
    assert ob._opening_relative_volume(completed=completed, reference_rows=zero, day="2026-09-07") is None


@pytest.mark.parametrize("cand,expected,direction,status", [
    ({"asset_class_detected": "Inverse_ETF"}, "inverse_etf", "INVERSE_HEDGE", "OBSERVED"),
    ({"asset_class": "leveraged_etf"}, "leveraged_etf", "LEVERAGED_LONG_RISK", "OBSERVED"),
    ({"compact_feature_snapshot": {"asset_class_detected": "active_etf"}}, "active_etf", "LONG_RISK_OR_OTHER", "OBSERVED"),
    ({"name": "KODEX 인버스"}, "inverse_etf", "INVERSE_HEDGE", "OBSERVED"),
    ({"name": "TIGER Leverage"}, "leveraged_etf", "LEVERAGED_LONG_RISK", "OBSERVED"),
    ({"name": "KODEX 200 etf"}, "etf", "LONG_RISK_OR_OTHER", "OBSERVED"),
    ({"symbol_name": "삼성전자"}, "common_stock", "LONG_RISK_OR_OTHER", "OBSERVED"),
    ({}, "unknown", "UNKNOWN", "MISSING_METADATA"),
    ({"asset_class": "weird"}, "weird", "UNKNOWN", "MISSING_METADATA"),
])
def test_asset_observation(cand, expected, direction, status):
    a = ob._asset_observation(cand)
    assert (a["asset_class"], a["exposure_direction"], a["status"]) == (expected, direction, status)


def test_execution_evidence_status_and_spread_flag():
    c = ob.LIVE_COST_PCT
    assert ob._execution_evidence(completed=[], best_bid=None, best_ask=None, spread_pct=None)["status"] == "INSUFFICIENT"
    p = ob._execution_evidence(completed=[1], best_bid=None, best_ask=1.0, spread_pct=None)
    assert p["status"] == "PARTIAL" and p["missing_fields"] == ["best_bid_ask"]
    assert ob._execution_evidence(completed=[], best_bid=1.0, best_ask=2.0, spread_pct=None)["missing_fields"] == ["completed_minute_bar"]
    full = ob._execution_evidence(completed=[1], best_bid=1.0, best_ask=2.0, spread_pct=c)
    assert full["status"] == "COMPLETE" and full["spread_exceeds_live_cost"] is False                    # equal is not exceeding
    assert ob._execution_evidence(completed=[1], best_bid=1.0, best_ask=2.0, spread_pct=c + 0.01)["spread_exceeds_live_cost"] is True


def lanes(**kw):
    base = dict(decision_from_open_sec=100, prior_rank1_observations_5m=0, completed_return_1m_pct=None, opening_relative_volume=None, above_vwap=None, market_return_pct=None, entry_vs_prior_close_pct=None)
    base.update(kw)
    return ob._conditional_lanes(**base)


def test_lane_immediate_probe_boundary():
    assert lanes(decision_from_open_sec=59)["IMMEDIATE_OPENING_PROBE"]["eligible"] is True
    assert lanes(decision_from_open_sec=60)["IMMEDIATE_OPENING_PROBE"]["eligible"] is False


def test_lane_confirmed_recurrent_requires_prior_observation_and_positive_return():
    f = lambda **k: lanes(**k)["CONFIRMED_RECURRENT_RANK"]  # noqa: E731
    assert f(prior_rank1_observations_5m=1, completed_return_1m_pct=0.01)["eligible"] is True
    assert f(prior_rank1_observations_5m=0, completed_return_1m_pct=1.0)["eligible"] is False
    assert f(prior_rank1_observations_5m=1, completed_return_1m_pct=0.0)["eligible"] is False
    none = f(prior_rank1_observations_5m=1)
    assert none["eligible"] is False and none["status"] == "INSUFFICIENT_EVIDENCE" and none["missing_fields"] == ["completed_return_1m_pct"]
    assert f(prior_rank1_observations_5m=1, completed_return_1m_pct=1.0)["status"] == "OBSERVED"
    assert f(opening_relative_volume=0.5)["evidence"]["moderate_volume_0_5_to_4x"] is True and f(opening_relative_volume=4.0)["evidence"]["moderate_volume_0_5_to_4x"] is True
    assert f(opening_relative_volume=0.49)["evidence"]["moderate_volume_0_5_to_4x"] is False and f(opening_relative_volume=4.01)["evidence"]["moderate_volume_0_5_to_4x"] is False


def test_lane_dislocation_thresholds_and_evidence_states():
    d = lambda **k: lanes(**k)["DISLOCATION_REBOUND"]  # noqa: E731
    assert d(market_return_pct=-3.0, opening_relative_volume=1.0)["eligible"] is True
    assert d(market_return_pct=-2.99, opening_relative_volume=1.0)["eligible"] is False
    assert d(entry_vs_prior_close_pct=-8.0, opening_relative_volume=1.0)["eligible"] is True
    assert d(entry_vs_prior_close_pct=-7.99, opening_relative_volume=1.0)["eligible"] is False
    assert d(market_return_pct=-5.0, opening_relative_volume=5.0)["eligible"] is False                  # dislocation without moderate volume
    assert d(market_return_pct=-5.0)["eligible"] is None and d(market_return_pct=-5.0)["missing_fields"] == ["opening_relative_volume"]
    assert d(opening_relative_volume=1.0)["status"] == "INSUFFICIENT_EVIDENCE" and d(opening_relative_volume=1.0)["missing_fields"] == ["market_or_prior_close_dislocation"]
    assert d()["missing_fields"] == ["market_or_prior_close_dislocation", "opening_relative_volume"]


def _assemble(**kw):
    base = dict(candidate={"symbol": "A", "name": "삼성전자"}, day_rows=[bar(9, 0, 100.0), bar(9, 1, 101.0), bar(9, 2, 102.0)], decision_epoch=ep(9, 3), baseline_epoch=ep(9, 3, 30), baseline_price=103.0)
    base.update(kw)
    return ob.opening_observability(**base)


def test_assembly_completed_bars_open_price_and_flags():
    o = _assemble()
    assert o["completed_bar_count_at_decision"] == 3 and o["opening_price"] == 100.0 and o["reference_entry_vs_open_pct"] == 3.0
    assert o["decision_from_open_sec"] == 180 and o["reference_entry_delay_sec"] == 30 and o["completed_return_1m_pct"] == pytest.approx(0.9901, abs=1e-4)
    assert o["completed_cumulative_volume"] == 30.0 and o["completed_volume_status"] == "OBSERVED" and o["exact_opening_09_00_04"] is True
    assert o["opening_chase_7pct"] is False and o["late_09_15_19_no_chase"] is False and o["above_vwap"] is None
    assert o["quote_snapshot"]["status"] == "MISSING_FROM_Q9_SNAPSHOT" and o["asset_observation"]["asset_class"] == "common_stock"


def test_assembly_bar_is_completed_only_after_its_full_minute():
    o = _assemble(day_rows=[bar(9, 0, 100.0), bar(9, 3, 101.0)], decision_epoch=ep(9, 3))              # 09:03 bar still forming at 09:03:00
    assert o["completed_bar_count_at_decision"] == 1
    first_minute = _assemble(day_rows=[bar(9, 0, 100.0)], decision_epoch=ep(9, 0, 30))
    assert first_minute["completed_volume_status"] == "UNAVAILABLE_FIRST_MINUTE" and first_minute["completed_cumulative_volume"] is None


def test_assembly_chase_and_late_window_flags():
    chase = _assemble(baseline_price=107.0)
    assert chase["opening_chase_7pct"] is True
    late = _assemble(decision_epoch=ep(9, 15), baseline_price=103.0)
    assert late["late_09_15_19_no_chase"] is True and late["exact_opening_09_00_04"] is False
    assert _assemble(decision_epoch=ep(9, 15), baseline_price=107.0)["late_09_15_19_no_chase"] is False
    assert _assemble(decision_epoch=ep(9, 20))["late_09_15_19_no_chase"] is False
    assert _assemble(decision_epoch=ep(9, 5))["exact_opening_09_00_04"] is False and _assemble(decision_epoch=ep(9, 4, 59))["exact_opening_09_00_04"] is True


def test_assembly_market_return_priority_and_vwap_strictness():
    snap = {"kospi_pct": -4.0}
    assert _assemble(market_snapshot=snap)["market_return_pct"] == -4.0
    assert _assemble(market_return_pct=1.0, market_snapshot=snap)["market_return_pct"] == 1.0                    # explicit arg wins
    assert _assemble(candidate={"kospi_pct": 2.5})["market_return_pct"] == 2.5                                  # candidate fallback
    assert _assemble(candidate={"above_vwap": True})["above_vwap"] is True and _assemble(candidate={"above_vwap": 1})["above_vwap"] is None
    assert _assemble(candidate={"compact_feature_snapshot": {"above_vwap": False}})["above_vwap"] is False


def test_assembly_quote_spread_and_prior_close_and_relative_volume_sources():
    cand = {"previous_close": 110.0, "relative_volume": 2.0, "compact_feature_snapshot": {"quote_best_bid": 100.0, "quote_best_ask": 100.5, "quote_payload_available": True, "quote_source": "q9"}}
    o = _assemble(candidate=cand)
    assert o["quote_snapshot"]["spread_pct"] == 0.5 and o["quote_snapshot"]["status"] == "OBSERVED" and o["quote_snapshot"]["source"] == "q9" and o["quote_snapshot"]["payload_available"] is True
    assert o["entry_vs_prior_close_pct"] == pytest.approx((103 / 110 - 1) * 100, abs=1e-4) and o["opening_relative_volume"] == 2.0
    assert o["execution_evidence"]["spread_exceeds_live_cost"] is True
    crossed = _assemble(candidate={"compact_feature_snapshot": {"quote_best_bid": 101.0, "quote_best_ask": 100.0}})
    assert crossed["quote_snapshot"]["spread_pct"] is None
    noq = _assemble(candidate={"compact_feature_snapshot": {"quote_evidence_status": "STALE"}})
    assert noq["quote_snapshot"]["status"] == "STALE"


def test_assembly_empty_rows_and_ordering_do_not_crash():
    o = _assemble(day_rows=[])
    assert o["opening_price"] is None and o["completed_bar_count_at_decision"] == 0 and o["reference_entry_vs_open_pct"] is None
    shuffled = _assemble(day_rows=[bar(9, 2, 102.0), bar(9, 0, 100.0), {"ts": 0, "close": 5.0}, bar(9, 1, 101.0)])
    assert shuffled["opening_price"] == 100.0 and shuffled["completed_bar_count_at_decision"] == 3
    assert _assemble(day_rows=[bar(9, 0, 100.0, open_=0.0)])["opening_price"] == 100.0                           # open falsy -> close
