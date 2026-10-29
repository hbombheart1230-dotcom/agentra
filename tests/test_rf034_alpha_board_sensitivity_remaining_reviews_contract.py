"""RF-034 C3: alpha_research_board sensitivity + remaining_reviews decision ladders (pure rows / tmp reports root)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import remaining_reviews as rv
from libs.reporting.alpha_research_board import sensitivity as se


def r(day, symbol, ret, epoch=0, **kw):
    return {"day": day, "symbol": symbol, "decision_epoch": epoch, "net_return_pct": ret, **kw}


# ---------- metrics & pass rule ----------

def test_metrics_values_drawdown_and_profit_factor_edges():
    m = se.performance_metrics([r("d", "a", 2.0), r("d", "b", -1.0), r("d", "c", -1.0), r("d", "d", None), r("d", "e", "x")])
    assert m["sample_count"] == 3 and m["win_rate"] == pytest.approx(0.3333, abs=1e-4) and m["avg_net_return_pct"] == 0.0 and m["median_net_return_pct"] == -1.0
    assert m["profit_factor"] == 1.0 and m["max_drawdown_pct"] == -2.0 and m["total_gain_pct"] == 2.0 and m["total_loss_pct"] == -2.0
    assert se.performance_metrics([r("d", "a", 1.0)])["profit_factor"] == 999.0
    assert se.performance_metrics([r("d", "a", -1.0)])["profit_factor"] == 0.0
    empty = se.performance_metrics([])
    assert empty["sample_count"] == 0 and empty["win_rate"] is None and empty["avg_net_return_pct"] is None and empty["profit_factor"] == 0.0 and empty["max_drawdown_pct"] is None


def test_passes_requires_strictly_positive_average_and_pf_at_least_1_2():
    assert se.performance_passes({"avg_net_return_pct": 0.01, "profit_factor": 1.2}) is True
    assert se.performance_passes({"avg_net_return_pct": 0.01, "profit_factor": 1.1999}) is False
    assert se.performance_passes({"avg_net_return_pct": 0.0, "profit_factor": 5.0}) is False
    assert se.performance_passes({"avg_net_return_pct": None, "profit_factor": 5.0}) is False
    assert se.performance_passes({"avg_net_return_pct": 1.0, "profit_factor": None}) is False
    assert se.performance_passes({}) is False


@pytest.mark.parametrize("v,regime", [(None, "UNKNOWN"), ("x", "UNKNOWN"), (1.0, "STRONG_POSITIVE"), (0.99, "NON_NEGATIVE"), (0.0, "NON_NEGATIVE"),
                                      (-0.01, "MILD_NEGATIVE"), (-0.99, "MILD_NEGATIVE"), (-1.0, "SHARP_NEGATIVE")])
def test_market_regime_boundaries(v, regime):
    assert se._market_regime(v) == regime


def test_leave_one_out_is_sorted_worst_first_and_flags_pass():
    rows = [r("d1", "A", 5.0), r("d2", "B", -1.0), r("d3", "C", -1.0)]
    out = se.leave_one_out(rows, "symbol")
    assert [o["excluded_symbol"] for o in out] == ["A", "B", "C"] and out[0]["passes"] is False and out[0]["avg_net_return_pct"] == -1.0 and out[-1]["passes"] is True
    assert se._group_metrics([r("d", "A", 1.0, asset_class="etf"), r("d", "B", 1.0)], "asset_class")[0]["asset_class"] == "UNKNOWN"


# ---------- risk-high decision ladder ----------

def _good(n=12, extra=None):
    rows = []
    for i in range(n):
        rows.append(r(f"2026-08-{i + 1:02d}", f"S{i}", 1.0 if i % 4 else -0.4, epoch=i, **{"asset_class": "common_stock", "market_regime": "NON_NEGATIVE", **(extra or {})}))
    return rows


def test_risk_high_ladder_each_branch():
    assert se.evaluate_risk_high_sensitivity(_good(9))["decision"] == "INSUFFICIENT_EVIDENCE"
    assert se.evaluate_risk_high_sensitivity(_good(10))["decision"] != "INSUFFICIENT_EVIDENCE"                       # minimum sample inclusive
    bad = [r(f"2026-08-{i + 1:02d}", f"S{i}", -1.0, epoch=i, asset_class="x", market_regime="NON_NEGATIVE") for i in range(12)]
    assert se.evaluate_risk_high_sensitivity(bad)["decision"] == "REJECT_BASE_EFFECT"
    ok = se.evaluate_risk_high_sensitivity(_good())
    assert ok["decision"] == "PROMOTION_REVIEW_PASS" and ok["behavior_change_authorized"] is False and all(ok["checks"].values())
    gap = se.evaluate_risk_high_sensitivity(_good(extra={"asset_class": "UNKNOWN"}))
    assert gap["decision"] == "CONDITIONAL_NOT_PROMOTABLE_METADATA_GAP" and gap["metadata_coverage"]["asset_class"] == 0.0


def test_risk_high_first_day_symbol_dedup_and_drops_invalid_rows():
    rows = [r("d1", "A", 1.0, epoch=5), r("d1", "A", 9.0, epoch=1), r("", "B", 1.0), r("d2", "", 1.0), r("d3", "C", None)]
    out = se.evaluate_risk_high_sensitivity(rows)
    assert [(x["day"], x["symbol"], x["net_return_pct"]) for x in out["rows"]] == [("d1", "A", 9.0)]            # earliest epoch wins
    assert out["largest_frequency_exposure"] == {"day": "d1", "day_share": 1.0, "symbol": "A", "symbol_share": 1.0}


def test_risk_high_contribution_dependence_branch():
    rows = [r(f"2026-08-{i + 1:02d}", f"S{i}", 0.3, epoch=i, asset_class="a", market_regime="NON_NEGATIVE") for i in range(10)]
    rows[0]["net_return_pct"] = 20.0
    rows += [r(f"2026-08-{i + 11:02d}", f"L{i}", -1.0, epoch=100 + i, asset_class="a", market_regime="NON_NEGATIVE") for i in range(5)]
    out = se.evaluate_risk_high_sensitivity(rows)
    assert out["decision"] == "REJECT_CONTRIBUTOR_DEPENDENCE" and out["positive_contribution"]["top_symbol"] == "S0"


def test_empty_risk_high_result_shape():
    out = se.evaluate_risk_high_sensitivity([])
    assert out["decision"] == "INSUFFICIENT_EVIDENCE" and out["metadata_coverage"] == {"asset_class": 0.0, "market_regime": 0.0}
    assert out["positive_contribution"]["top_symbol"] is None and out["positive_contribution"]["top_symbol_share_of_positive_gain"] is None
    assert out["checks"]["all_symbol_leave_one_out"] is False and out["rows"] == []


def test_render_handles_empty_and_populated():
    assert "## 결론: `INSUFFICIENT_EVIDENCE`" in se.render_risk_high_sensitivity(se.evaluate_risk_high_sensitivity([]))
    md = se.render_risk_high_sensitivity(se.evaluate_risk_high_sensitivity(_good()))
    assert "PROMOTION_REVIEW_PASS" in md and "| `common_stock` | N=" in md and "| `NON_NEGATIVE` | N=" in md


# ---------- build_risk_high_sensitivity (tmp reports root) ----------

def _w(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def test_build_risk_high_filters_days_status_candidate_and_enriches(tmp_path):
    base = tmp_path / "evaluation" / "feature_mart" / "opening_rank1" / "prospective"
    cand = se.CANDIDATE_ID
    obs = lambda eid, **kw: {"candidate_id": cand, "matched": True, "episode_id": eid, "day": kw.pop("day"), "symbol": kw.pop("symbol"), "decision_epoch": 1, "net_return_pct": 1.0, **kw}  # noqa: E731
    _w(base / "2026-08-10" / "rank1_candidate_shadow_daily.json", {"status": "VALID", "observations": [obs("E1", day="2026-08-10", symbol="A"), {"candidate_id": "OTHER", "matched": True},
                                                                                                     {**obs("E2", day="2026-08-10", symbol="B"), "matched": False}]})
    _w(base / "2026-08-09" / "rank1_candidate_shadow_daily.json", {"status": "VALID", "observations": [obs("E3", day="2026-08-09", symbol="C")]})      # before first_day
    _w(base / "2026-08-11" / "rank1_candidate_shadow_daily.json", {"status": "INVALID", "observations": [obs("E4", day="2026-08-11", symbol="D")]})
    _w(base / "2026-08-12" / "rank1_candidate_shadow_daily.json", "{corrupt")
    _w(base / "2026-08-31" / "rank1_candidate_shadow_daily.json", {"status": "VALID_NO_EPISODES", "observations": []})
    _w(tmp_path / "evaluation" / "opening_rank1_shadow" / "opening_rank1_shadow_cumulative.json",
       {"episodes": [{"episode_id": "E1", "opening_observability": {"asset_observation": {"asset_class": "etf"}, "market_snapshot": {"kospi_pct": 1.5}}}]})
    out = se.build_risk_high_sensitivity(reports_root=tmp_path, first_day="2026-08-10", through_day="2026-08-20")
    assert [(x["symbol"], x["asset_class"], x["market_regime"], x["kospi_pct"]) for x in out["rows"]] == [("A", "etf", "STRONG_POSITIVE", 1.5)]
    assert out["range"] == {"start": "2026-08-10", "end": "2026-08-20"}
    assert out["source_integrity"]["opening_source_error"] is None and len(out["source_integrity"]["daily_source_errors"]) == 1
    missing = se.build_risk_high_sensitivity(reports_root=tmp_path / "none", first_day="a", through_day="z")
    assert missing["source_integrity"]["opening_source_error"] == "MISSING_ARTIFACT" and missing["rows"] == []


# ---------- remaining_reviews ----------

def _ep(day, symbol, ret, *, lane="CONFIRMED_RECURRENT_RANK", eligible=True, horizon="+30m", epoch=0, asset=None, kospi=None):
    return {"day": day, "symbol": symbol, "decision_epoch": epoch,
            "opening_observability": {"conditional_lanes": {lane: {"eligible": eligible}}, "asset_observation": {"asset_class": asset} if asset else {}, "market_snapshot": {"kospi_pct": kospi}},
            "checkpoints": {horizon: {"live_net_return_pct": ret}}}


def test_opening_rows_filters_lane_eligibility_and_none_returns():
    payload = {"episodes": [_ep("d1", "A", 1.0, asset="etf", kospi=0.3, epoch=7), _ep("d2", "B", 1.0, eligible=False), _ep("d3", "C", None), _ep("d4", "D", 1.0, lane="OTHER"),
                            _ep("d5", "E", 1.0, horizon="+5m"), "junk"]}
    rows = rv._opening_rows(payload, lane_id="CONFIRMED_RECURRENT_RANK", horizon="+30m")
    assert rows == [{"day": "d1", "symbol": "A", "decision_epoch": 7, "net_return_pct": 1.0, "asset_class": "etf", "kospi_pct": 0.3}]
    assert rv._opening_rows({"episodes": [_ep("d", "A", 0.0)]}, lane_id="CONFIRMED_RECURRENT_RANK", horizon="+30m")[0]["asset_class"] == "UNKNOWN"   # 0.0 is a valid return


def _robust(n=12):
    return [r(f"2026-08-{i + 1:02d}", f"S{i}", v, epoch=i) for i, v in enumerate([1.0, 0.8, 0.7, 0.6, 0.5, 1.2, 0.9, 0.4, -0.2, -0.1, 0.8, 0.6][:n])]


def test_bounded_review_decision_ladder():
    assert rv.evaluate_bounded_candidate(_robust(), minimum_sample=10)["decision"] == "READY_FOR_FIXED_RUNTIME_VALIDATION"
    few = rv.evaluate_bounded_candidate(_robust(9), minimum_sample=10)
    assert few["decision"] == "RUNTIME_DATA_REQUIRED" and "9건" in few["rationale"] and rv.evaluate_bounded_candidate(_robust(10), minimum_sample=10)["decision"] != "RUNTIME_DATA_REQUIRED"
    base_bad = [r(f"d{i}", f"S{i}", -0.5, epoch=i) for i in range(12)]
    assert rv.evaluate_bounded_candidate(base_bad, minimum_sample=10)["decision"] == "REJECT_BASE_EFFECT"
    sym = [r(f"d{i}", f"S{i}", 0.2, epoch=i) for i in range(11)] + [r("d11", "BIG", 10.0, epoch=11)]
    sym += [r(f"d{20 + i}", f"L{i}", -0.5, epoch=20 + i) for i in range(6)]
    assert rv.evaluate_bounded_candidate(sym, minimum_sample=10)["decision"] == "REJECT_SYMBOL_CONTRIBUTOR_DEPENDENCE"
    day = [r("big", f"S{i}", 3.0 if i < 2 else 0.05, epoch=i) for i in range(12)] + [r(f"d{i}", f"T{i}", -0.4, epoch=30 + i) for i in range(6)]
    assert rv.evaluate_bounded_candidate(day, minimum_sample=10)["decision"] in {"REJECT_DAY_CONTRIBUTOR_DEPENDENCE", "REJECT_SYMBOL_CONTRIBUTOR_DEPENDENCE", "REJECT_SINGLE_OBSERVATION_DEPENDENCE", "REJECT_BASE_EFFECT"}
    out = rv.evaluate_bounded_candidate(_robust(), minimum_sample=10)
    assert out["largest_day_share"] == round(1 / 12, 4) and out["largest_symbol_share"] == round(1 / 12, 4) and out["minimum_sample"] == 10
    assert rv.evaluate_bounded_candidate([], minimum_sample=1)["largest_day_share"] is None


def test_single_observation_dependence_branch():
    # symbol and day leave-one-out all pass (each excluded group has several rows) but dropping the single best row breaks it
    rows = [r(f"d{i % 6}", f"S{i}", -0.1, epoch=i) for i in range(30)] + [r("d0", "BEST", 4.0, epoch=99)]
    out = rv.evaluate_bounded_candidate(rows, minimum_sample=10)
    assert out["decision"] in {"REJECT_SINGLE_OBSERVATION_DEPENDENCE", "REJECT_SYMBOL_CONTRIBUTOR_DEPENDENCE", "REJECT_BASE_EFFECT"}


def _btc_payload(values, regimes=None):
    return {"episodes": [{"day": f"2026-08-{i + 1:02d}", "start_epoch": i, "returns": {"+30m": {"return_pct": v}}, "btc": {"market_regime": (regimes or {}).get(i, "bull")}} for i, v in enumerate(values)]}


def test_btc_review_subtracts_real_drag_and_groups_regimes():
    out = rv._btc_review(_btc_payload([1.28, None, 0.28]))
    assert out["base"]["sample_count"] == 2 and out["base"]["avg_net_return_pct"] == 0.5
    assert [x["btc_regime"] for x in out["by_btc_regime"]] == ["bull"]
    assert rv._btc_review(_btc_payload([0.1, 0.1]))["decision"] == "REJECT_BASE_EFFECT"
    good = rv._btc_review(_btc_payload([2.0, 1.8, 1.5, 1.6, 1.7, 1.9, 1.4], regimes={0: "strong_bull"}))
    assert good["decision"] == "READY_FOR_FIXED_RUNTIME_VALIDATION" and {x["btc_regime"] for x in good["by_btc_regime"]} == {"bull", "strong_bull"}
    dep = rv._btc_review(_btc_payload([20.0, 0.3, 0.3, 0.3, -0.5, -0.5]))
    assert dep["decision"].startswith("REJECT_")


def test_build_remaining_reviews_on_missing_sources_does_not_raise(tmp_path):
    out = rv.build_remaining_candidate_reviews(reports_root=tmp_path / "reports", through_day="2026-08-28")
    ids = [x["candidate_id"] for x in out["reviews"]] if "reviews" in out else []
    assert "IMMEDIATE_OPENING_PROBE" in ids and "CONFIRMED_RECURRENT_RANK" in ids and "DISLOCATION_REBOUND" in ids
    assert out["schema_version"] == "remaining_candidate_reviews.v1"
    by = {x["candidate_id"]: x for x in out["reviews"]}
    assert by["IMMEDIATE_OPENING_PROBE"]["decision"] == "RUNTIME_DATA_REQUIRED" and by["IMMEDIATE_OPENING_PROBE"]["minimum_sample"] == 10
    assert by["CONFIRMED_RECURRENT_RANK"]["minimum_sample"] == 5


def test_single_observation_dependence_is_reached_only_when_symbol_and_day_loo_pass():
    rows = [r("d1", "X", 3.0, epoch=0), r("d1", "X", -2.5, epoch=1)] + [r(f"d{i + 2}", f"S{i}", 0.1, epoch=i + 2) for i in range(10)]
    out = rv.evaluate_bounded_candidate(rows, minimum_sample=10)
    assert out["decision"] == "REJECT_SINGLE_OBSERVATION_DEPENDENCE" and out["sensitivity"]["worst_symbol_leave_one_out"]["passes"] is True
    assert out["sensitivity"]["worst_day_leave_one_out"]["passes"] is True and out["sensitivity"]["without_best_observation"]["avg_net_return_pct"] < 0


def test_build_risk_high_includes_observations_of_valid_no_episodes_days(tmp_path):
    path = tmp_path / "evaluation" / "feature_mart" / "opening_rank1" / "prospective" / "2026-08-10" / "rank1_candidate_shadow_daily.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"status": "VALID_NO_EPISODES", "observations": [{"candidate_id": se.CANDIDATE_ID, "matched": True, "episode_id": "E", "day": "2026-08-10", "symbol": "A", "decision_epoch": 1, "net_return_pct": 1.0}]}), encoding="utf-8")
    out = se.build_risk_high_sensitivity(reports_root=tmp_path, first_day="2026-08-01", through_day="2026-08-31")
    assert [x["symbol"] for x in out["rows"]] == ["A"]
