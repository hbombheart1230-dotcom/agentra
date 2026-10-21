"""FAST08 A8.4 smoke tests: cumulative review, horizon compliance, score range and feedback."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from libs.reporting.evaluation import attribution_score_range as score_range
from libs.reporting.evaluation import cumulative_improvement_review as cumulative
from libs.reporting.evaluation import fast08_cumulative_projection as cp
from libs.reporting.evaluation.feedback_effectiveness import build_feedback_effectiveness
from libs.reporting.evaluation.horizon_compliance_report import build_horizon_compliance_report, render_horizon_compliance_report


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def comparison(a_ret: float, b_ret: float, *, a_trades: int = 3, b_trades: int = 3, horizon: str = "+30m") -> Dict[str, Any]:
    return {"horizons": [{"horizon": horizon, "performers": [
        {"performer": "A_SCANNER_CONTROL", "trade_count": a_trades, "avg_return_pct": a_ret},
        {"performer": "B_STRATEGIST_RANKED", "trade_count": b_trades, "avg_return_pct": b_ret}]}, "bad", {"horizon": "+99m"}]}


def test_strategist_weighting_counts_only_paired_traded_days(tmp_path: Path) -> None:
    root = tmp_path / "evaluation" / "baseline_samsung_hynix"
    _write(root / "2026-07-01" / "q9_vs_samsung_hynix_daily_comparison.json", comparison(0.1, 0.4))
    _write(root / "2026-07-02" / "q9_vs_samsung_hynix_daily_comparison.json", comparison(0.5, 0.1))
    _write(root / "2026-07-03" / "q9_vs_samsung_hynix_daily_comparison.json", comparison(0.5, 9.0, b_trades=0))
    _write(root / "2026-07-04" / "q9_vs_samsung_hynix_daily_comparison.json", {})
    _write(root / "2026-08-01" / "q9_vs_samsung_hynix_daily_comparison.json", comparison(0.0, 5.0))
    review = cumulative._strategist_weighting_review(tmp_path, start="2026-07-01", end="2026-07-31")
    row = {r["horizon"]: r for r in review["rows"]}["+30m"]
    assert (row["observed_day_count"], row["strategist_better_day_count"], row["strategist_worse_day_count"]) == (2, 1, 1)
    assert row["avg_strategist_minus_scanner_pct"] == -0.05
    assert {r["horizon"]: r["avg_strategist_minus_scanner_pct"] for r in review["rows"]}["EOD"] is None
    assert cp.strategist_day_delta(comparison(0.1, 0.4, horizon="+99m")) == {}


def test_candidate_status_stays_in_facade_and_rank_row_lookup() -> None:
    episode = {"rank_horizon_rows": [{"rank_bucket": "rank1", "horizon": "+30m", "live_net": {"expectancy_pct": -0.1}},
                                     {"rank_bucket": "rank2_3", "horizon": "+30m", "live_net": {"expectancy_pct": -0.2}}],
               "score_component_review": {"status": "READY"}}
    rows = cumulative._candidate_rows(episode_review=episode, reentry_review={"behavior_candidate_eligible": False},
                                      post_reclaim_review={}, strategist_review={"rows": [{"horizon": "+30m", "avg_strategist_minus_scanner_pct": -0.3}]})
    status = {r["candidate"]: r["status"] for r in rows}
    assert status["same_symbol_loss_reentry_control"] == "INSUFFICIENT_EVIDENCE"
    assert status["scanner_rank_ordering_component_review"] == "DIAGNOSTIC_CANDIDATE"
    assert status["strategist_ranking_weight_guard"] == "DIAGNOSTIC_CANDIDATE"
    assert cp.rank_row(episode, bucket="rank9", horizon="+30m") == {}


def test_cumulative_build_and_render_with_injected_inputs(tmp_path: Path) -> None:
    review = cumulative.build_cumulative_improvement_review(
        reports_root=tmp_path, start="2026-07-01", end="2026-07-02", payloads=[], historical_review={},
        q14_range={"largest_behavior_root_cause": {"root_cause": "x"},
                   "cause_summary": [{"diagnostic_kind": "outcome_conditioned", "trade_count": 4}, {"diagnostic_kind": "structural", "trade_count": 9}],
                   "rows": []})
    assert review["q14_causal_interpretation"]["outcome_conditioned_trade_count"] == 4
    assert review["behavior_patch_authorized"] is False and len(review["improvement_candidates"]) == 4
    md = cumulative.render_cumulative_improvement_review(review)
    assert md.startswith("# Cumulative Improvement Review - 2026-07-01 to 2026-07-02") and "## Decision Boundary" in md


def _evaluation(horizon: str, reason: str, ret: float | None, **flags: Any) -> Dict[str, Any]:
    return {"trade_id": f"{horizon}-{reason}", "integrity": {"promotion_metric_eligible": True},
            "horizon_alignment": {"strategy_horizon": horizon, "actual_hold_sec": 120, **flags},
            "exit_quality": {"reason": reason}, "realized_outcome": {"net_return_pct": ret, "holding_seconds": 90}}


def test_horizon_compliance_exclusions_and_groups() -> None:
    evaluations = [
        _evaluation("intraday", "stop", -0.5, exited_before_min_hold=True, horizon_violation_candidate=True),
        _evaluation("intraday", "stop", 0.3, target_hold_would_improve_exit=True, valid_early_exit=True),
        _evaluation("swing", "target", None),
        {"integrity": {"promotion_metric_eligible": False}},
        {"integrity": {"exit_metric_eligible": False}},
        {},
    ]
    report = build_horizon_compliance_report(evaluations)
    assert (report["trade_count"], report["excluded_trade_count"], report["exit_incident_excluded_trade_count"]) == (4, 1, 1)
    group = next(g for g in report["group_rows"] if g["strategy_horizon"] == "intraday")
    assert group["count"] == 2 and group["exit_before_min_hold_count"] == 1 and group["valid_or_allowed_early_exit_count"] == 1
    assert group["average_hold_sec"] == 120.0 and group["performance"]["count"] == 2
    swing = next(g for g in report["group_rows"] if g["strategy_horizon"] == "swing")
    assert swing["performance"]["count"] == 0
    assert "- `intraday`: 2" in render_horizon_compliance_report(report)
    assert "- No observed horizons." in render_horizon_compliance_report(build_horizon_compliance_report([]))


def test_score_range_marks_missing_days_and_skips_unscored(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    daily = reports / "evaluation" / "daily"
    _write(daily / "2026-07-01" / "attribution_score_v0.json", {"scores": {"selection_integrity_score": {"score": 80},
                                                                           "entry_timing_score": {"status": "INSUFFICIENT_EVIDENCE", "reasons": ["gap"]}},
                                                                "weakest_observed_axis": {"name": "selection_integrity_score"}})
    _write(daily / "2026-07-02" / "attribution_score_v0.json", {"scores": {"selection_integrity_score": {"status": "INSUFFICIENT_EVIDENCE"}}})
    (reports / "trades" / "2026-07-03").mkdir(parents=True)
    result = score_range.build_attribution_score_range(reports_root=reports, start="2026-07-01", end="2026-07-04")
    assert (result["day_count"], result["available_day_count"], result["scored_day_count"]) == (3, 2, 1)
    axis = result["axis_summary"]["selection_integrity_score"]
    assert axis["average_score"] == 80.0 and axis["missing_day_count"] == 1 and axis["insufficient_day_count"] == 1
    assert result["axis_summary"]["entry_timing_score"]["top_reasons"] == [{"reason": "gap", "count": 1}]
    assert result["weakest_axis_distribution"] == {"selection_integrity_score": 1}
    assert result["weakest_axis_by_average_score"] == {"name": "selection_integrity_score", "average_score": 80.0}
    full = score_range.build_attribution_score_range(reports_root=reports, start="2026-07-01", end="2026-07-04", include_empty_days=True)
    assert full["day_count"] == 4
    assert "- `selection_integrity_score`: 1" in score_range.render_attribution_score_range(result)


def test_feedback_exposure_never_claims_causality() -> None:
    windows = [{"decision_id": "D1", "strategist_provenance": {"feedback": {"feedback_id": "F1", "adoption_status": "CHANGE_OBSERVED_WITH_FEEDBACK_EXPOSURE", "consumed": 1}}},
               {"decision_id": "D1", "strategist_provenance": {"feedback": {"feedback_id": "F1"}}},
               {"q9_decision_id": "D2", "strategist_provenance": {"feedback": {"feedback_id": "F1"}}}, {"strategist_provenance": {}}]
    models = [{"trade_id": "T1", "provenance": {"field_sources": {"strategy_policy_source": "Feedback.Loop"}}},
              {"trade_id": "T2", "provenance": {"field_sources": {"strategy_policy_source": "static"}}}]
    result = build_feedback_effectiveness(models, windows)
    assert (result["exposure_count"], result["adoption_count"], result["adoption_rate"]) == (3, 1, 0.3333)
    assert result["causal_claim_allowed"] is False and result["decision_class"] == "INSUFFICIENT_EVIDENCE"
    assert result["records"][0]["causal_attribution"] is False and result["provenance_linkage_status"] == "ACTIVE"
    empty = build_feedback_effectiveness([])
    assert empty["adoption_rate"] == 0.0 and empty["provenance_linkage_status"] == "AWAITING_NEW_RUNTIME_ARTIFACTS"


def test_a84_helper_is_pure() -> None:
    source = Path(cp.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "collections", "typing", ".metrics"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", "now("):
        assert banned not in source, banned
