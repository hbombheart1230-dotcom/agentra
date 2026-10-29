"""RF-034 C3: opening metrics summary counters and promotion-gate boundaries (summarize_horizon stubbed where only counters matter)."""
from __future__ import annotations

import pytest

from libs.reporting.opening_rank1_shadow import metrics as mt

G = mt.PROMOTION_GATES


def test_gate_constants_are_pinned():
    assert G == {"minimum_observed_count": 25, "minimum_observed_day_count": 10, "minimum_coverage": 0.90, "minimum_win_rate": 0.50, "minimum_average_net_return_pct": 0.0,
                 "minimum_profit_factor": 1.20, "minimum_positive_day_ratio": 0.55, "maximum_largest_day_share": 0.25, "maximum_largest_symbol_share": 0.25}
    assert mt.PRIMARY_HORIZON == "+30m"


def cp(ret, status="observed"):
    return {"status": status, "live_net_return_pct": ret}


def episode(day, symbol, ret, *, lanes=None, obs=None, status="observed"):
    return {"day": day, "symbol": symbol, "checkpoints": {"+30m": cp(ret, status)}, "opening_observability": {"conditional_lanes": lanes or {}, **(obs or {})}}


@pytest.fixture(autouse=True)
def _stub_horizon(monkeypatch):
    monkeypatch.setattr(mt, "summarize_horizon", lambda eps, horizon: {"n": len(eps), "horizon": horizon})


def test_counters_subgroups_and_lanes():
    eps = [
        episode("d1", "A", 1.0, obs={"exact_opening_09_00_04": True, "opening_chase_7pct": False, "completed_volume_status": "OBSERVED", "quote_snapshot": {"status": "OBSERVED"},
                                     "asset_observation": {"exposure_direction": "INVERSE_HEDGE"}, "execution_evidence": {"status": "COMPLETE"}},
                lanes={"L1": {"eligible": True, "status": "OBSERVED"}, "L2": {"eligible": None, "status": "INSUFFICIENT_EVIDENCE"}}),
        episode("d1", "B", -1.0, obs={"late_09_15_19_no_chase": True, "exact_opening_09_00_04": 1}, lanes={"L1": {"eligible": False}}),
        {"day": "d2", "symbol": "C", "checkpoints": "bad", "opening_observability": "bad"},
        episode("d2", "A", 2.0, status="pending"),
    ]
    s = mt.summarize_episodes(eps)
    assert s["episode_count"] == 4 and s["observed_30m_count"] == 2 and s["observed_day_count"] == 1
    assert s["subgroup_counts"] == {"exact_opening_09_00_04": 1, "late_09_15_19_no_chase": 1}                 # `is True` only; 1 does not count
    assert s["observability_counts"]["OBSERVED"] == 1 and s["observability_counts"]["MISSING"] == 3 and s["observability_counts"]["quote:OBSERVED"] == 1 and s["observability_counts"]["quote:MISSING"] == 3
    assert s["exposure_counts"] == {"INVERSE_HEDGE": 1, "UNKNOWN": 3} and s["execution_evidence_counts"] == {"COMPLETE": 1, "MISSING": 3}
    lanes = s["conditional_lane_summaries"]
    assert sorted(lanes) == ["L1", "L2"] and lanes["L1"]["eligible_episode_count"] == 1 and lanes["L2"]["eligible_episode_count"] == 0
    assert lanes["L1"]["evidence_status_counts"] == {"OBSERVED": 1, "MISSING": 1} and lanes["L1"]["horizons"]["+30m"] == {"n": 1, "horizon": "+30m"}
    assert set(s["horizons"]) == set(mt.HORIZONS)


def test_day_and_symbol_shares_and_positive_day_ratio():
    eps = [episode("d1", "A", 1.0), episode("d1", "A", -0.5), episode("d2", "B", -1.0), episode("d3", "C", 0.0)]
    s = mt.summarize_episodes(eps)
    assert s["observed_30m_count"] == 4 and s["observed_day_count"] == 3
    assert s["positive_day_ratio"] == round(1 / 3, 4)                      # only d1 mean 0.25 > 0; d3 mean 0 is not positive
    assert s["largest_day_share"] == 0.5 and s["largest_symbol_share"] == 0.5
    empty = mt.summarize_episodes([])
    assert empty["positive_day_ratio"] == 0.0 and empty["largest_day_share"] == 0.0 and empty["largest_symbol_share"] == 0.0 and empty["conditional_lane_summaries"] == {}


def summary(**kw):
    base = {"observed_30m_count": 25, "observed_day_count": 10, "positive_day_ratio": 0.55, "largest_day_share": 0.25, "largest_symbol_share": 0.25,
            "horizons": {"+30m": {"coverage": 0.90, "live_net": {"win_rate": 0.50, "average_return_pct": 0.01, "profit_factor": 1.20}}}}
    h = kw.pop("live", {})
    cov = kw.pop("coverage", None)
    base.update(kw)
    base["horizons"]["+30m"]["live_net"].update(h)
    if cov is not None:
        base["horizons"]["+30m"]["coverage"] = cov
    return base


def test_all_gates_at_exact_boundary_are_eligible():
    out = mt.evaluate_promotion(summary())
    assert out["status"] == "ELIGIBLE_FOR_CONTROLLED_SHADOW" and all(out["checks"].values()) and out["evidence_ready"] is True and out["behavior_change_authorized"] is False
    assert out["gates"] == G


@pytest.mark.parametrize("kw,check", [
    ({"coverage": 0.8999}, "coverage"), ({"live": {"win_rate": 0.4999}}, "win_rate"), ({"live": {"average_return_pct": 0.0}}, "average_net_return"),
    ({"live": {"profit_factor": 1.1999}}, "profit_factor"), ({"positive_day_ratio": 0.5499}, "positive_day_ratio"),
    ({"largest_day_share": 0.2501}, "day_concentration"), ({"largest_symbol_share": 0.2501}, "symbol_concentration"),
])
def test_single_gate_failure_rejects(kw, check):
    out = mt.evaluate_promotion(summary(**kw))
    assert out["status"] == "REJECTED" and out["checks"][check] is False and sum(not v for v in out["checks"].values()) == 1


def test_collecting_until_count_and_day_minimums_even_if_checks_fail():
    assert mt.evaluate_promotion(summary(observed_30m_count=24))["status"] == "COLLECTING"
    assert mt.evaluate_promotion(summary(observed_day_count=9))["status"] == "COLLECTING"
    bad = mt.evaluate_promotion(summary(observed_30m_count=24, positive_day_ratio=0.0))
    assert bad["status"] == "COLLECTING" and bad["evidence_ready"] is False
    assert mt.evaluate_promotion({})["status"] == "COLLECTING" and mt.evaluate_promotion({})["values"]["coverage"] == 0.0


def test_net_returns_and_compact_performance():
    eps = [{"checkpoints": {"+30m": cp(1.0)}}, {"checkpoints": {"+30m": cp(None)}}, {"checkpoints": {"+30m": cp(5.0, "pending")}}, {"checkpoints": {"+5m": cp(2.0)}}, {}, {"checkpoints": {"+30m": "bad"}}]
    assert mt.net_returns(eps) == [1.0, 0.0] and mt.net_returns(eps, "+5m") == [2.0]
    assert mt.compact_performance(eps)["count"] == 2


def test_lane_eligibility_requires_literal_true():
    eps = [episode("d1", "A", 1.0, lanes={"L": {"eligible": 1}}), episode("d1", "B", 1.0, lanes={"L": {"eligible": "yes"}}), episode("d1", "C", 1.0, lanes={"L": {"eligible": True}})]
    assert mt.summarize_episodes(eps)["conditional_lane_summaries"]["L"]["eligible_episode_count"] == 1
