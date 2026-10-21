"""FAST08 A8.3 smoke tests: Q13/Q14 validation, Q16/Q17 review, cost basis and score window."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from libs.reporting.evaluation import attribution_score_window as score_window
from libs.reporting.evaluation import cost_basis_comparison as cost_basis
from libs.reporting.evaluation import fast08_qwindow_projection as qw
from libs.reporting.evaluation import q13_q14_validation as validation
from libs.reporting.evaluation import q16_proxy_rejection_review as q16


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def build_validation_reports(root: Path, days: int = 5, *, scanner_failure_days: int = 5, missing: int = 0) -> Path:
    reports = root / "reports"
    for i in range(days):
        day = f"2026-07-0{i + 1}"
        daily = reports / "evaluation" / "daily" / day
        failure = 4 if i < scanner_failure_days else 0
        _write(daily / "attribution_score_v0.json", {"scores": {
            "selection_integrity_score": {"score": 71.6}, "scanner_alignment_score": {"status": "INSUFFICIENT_EVIDENCE", "score": 5},
            "entry_timing_score": {"score": "bad"}, "exit_horizon_score": {}}})
        _write(daily / "scanner_alignment_root_cause_report.json", {
            "trade_count": 10,
            "largest_behavior_root_cause": {"root_cause": "Scanner Ranking Failure" if i < scanner_failure_days else "Candidate Filtering"},
            "cause_summary": [{"root_cause": "Scanner Ranking Failure", "trade_count": failure},
                              {"root_cause": "Missing Evidence", "trade_count": missing}]})
        _write(daily / "horizon_compliance_report.json", {"rows": [{"exited_before_min_hold": True}, {}]})
    return reports


def test_axis_score_never_turns_missing_into_zero() -> None:
    scores = {"a": {"score": 71.6}, "b": {"status": "INSUFFICIENT_EVIDENCE", "score": 5}, "c": {"score": "x"}, "d": {}}
    assert [qw.axis_score(scores, k) for k in "abcde"] == [72, None, None, None, None]


@pytest.mark.parametrize("days,failures,missing,expected", [
    (3, 5, 0, "IN_PROGRESS"), (5, 5, 0, "GO"), (5, 3, 0, "NO_GO"), (5, 5, 3, "NO_GO")])
def test_validation_decision_thresholds(tmp_path: Path, days: int, failures: int, missing: int, expected: str) -> None:
    reports = build_validation_reports(tmp_path, days, scanner_failure_days=failures, missing=missing)
    report = validation.build_q13_q14_validation_report(reports_root=reports, start="2026-07-01", end="2026-07-09")
    assert report["decision"] == expected and report["behavior_patch_authorized"] is False
    assert report["day_count"] == days
    row = report["daily_rows"][0]
    assert row["q13_scores"]["scanner_alignment_score"] is None and row["q13_scores"]["selection_integrity_score"] == 72
    assert row["report_complete"] is True
    if expected == "NO_GO" and missing:
        assert "missing_evidence_above_threshold" in report["decision_reasons"]
    md = validation.render_q13_q14_validation_report(report)
    assert md.startswith("# Q13/Q14 Validation Run") and "| Exit Horizon |" in md


def test_validation_keeps_exit_horizon_comparison_and_incomplete_day(tmp_path: Path) -> None:
    reports = build_validation_reports(tmp_path, 1, scanner_failure_days=1)
    daily = reports / "evaluation" / "daily" / "2026-07-01"
    _write(daily / "horizon_compliance_report.json", {"rows": [{"horizon_violation_candidate": True}] * 6})
    (daily / "attribution_score_v0.json").unlink()
    report = validation.build_q13_q14_validation_report(reports_root=reports, days=["2026-07-01"])
    row = report["daily_rows"][0]
    # Exit Horizon is compared against the actionable set that includes itself, so (as before the
    # extraction) the override never fires; the Q14 label is kept and the count is still reported.
    assert row["root_cause_counts"]["Exit Horizon"] == 6
    assert row["largest_behavior_root_cause"] == "Scanner Ranking Failure" and row["report_complete"] is False
    assert report["completed_report_day_count"] == 0 and report["decision"] == "IN_PROGRESS"
    with pytest.raises(ValueError):
        validation.build_q13_q14_validation_report(reports_root=reports)


def test_score_window_valid_days_only(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    freeze = reports / "evaluation" / "freeze_window" / "w1"
    _write(freeze / "daily_ledger.json", {"days": [{"day": "d1", "counts_as_valid_day": True}, {"day": "d2", "counts_as_valid_day": True},
                                                  {"day": "d3", "counts_as_valid_day": False}]})
    for day, sel in (("d1", 60), ("d3", 10)):
        daily = reports / "evaluation" / "daily" / day
        _write(daily / "attribution_score_v0.json", {"scores": {"selection_integrity_score": {"score": sel}},
                                                      "weakest_observed_axis": {"name": "selection_integrity_score"}})
        _write(daily / "daily_scorecard.json", {"artifact_integrity": {"trade_count": 3}})
    payload = score_window.build_attribution_score_window(reports_root=reports, window_id="w1")
    assert (payload["day_count"], payload["valid_day_count"], payload["available_day_count"]) == (3, 2, 2)
    assert payload["axis_summary"]["selection_integrity_score"]["average_score"] == 60.0
    assert payload["total_trade_count_valid_days"] == 3
    assert payload["weakest_axis_distribution"] == {"selection_integrity_score": 1}
    missing_day = {r["day"]: r for r in payload["daily_rows"]}["d2"]
    assert missing_day["available"] is False and missing_day["selection_integrity_score"] is None
    md = score_window.render_attribution_score_window(payload)
    assert "- `selection_integrity_score`: 1" in md
    assert "No valid scored days" in score_window.render_attribution_score_window(
        score_window.build_attribution_score_window(reports_root=tmp_path / "none", window_id="x"))


def _row(day: str, cls: str, ret15: float | None, ret30: float | None, *, base_day: str | None = None, **extra: Any) -> Dict[str, Any]:
    cps: Dict[str, Any] = {}
    for h, v in (("+15m", ret15), ("+30m", ret30)):
        if v is not None:
            cps[h] = {"status": "observed", "return_pct": v, "observed_ts": f"{(base_day or day).replace('-', '')}0930"}
    return {"q16_day": day, "q16_candidate_class": cls, "shadow_forward_base": {"baseline_raw_ts": (base_day or day).replace("-", "") + "0900"},
            "shadow_forward_outcome": {"checkpoints": cps}, **extra}


def test_forward_integrity_and_metric_bundle() -> None:
    assert qw.forward_integrity(_row("2026-07-22", "x", 1.0, 1.0)) == ("TRUSTED", [])
    status, reasons = qw.forward_integrity(_row("2026-07-22", "x", 1.0, 1.0, base_day="2026-07-21"))
    assert status == "INVALID" and "baseline_day_mismatch" in reasons and "+15m:observed_day_mismatch" in reasons
    assert qw.forward_integrity({"q16_day": "2026-07-22"})[1] == ["baseline_day_missing"]
    assert qw.timestamp_day("2026-07-22T09:00") == "20260722" and qw.timestamp_day("garbage") == ""
    bundle = qw.metric_bundle([_row("d", "x", 1.0, 2.0), _row("d", "x", None, None)], 0.5, "+30m")
    assert bundle["gross"]["count"] == 1 and bundle["net"]["average_return_pct"] == 1.5
    assert qw.expected_horizon({"directional_edge_estimate": {"forward_horizon": "30m"}}) == "+30m"


def test_q16_candidate_classes_and_final_decision(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    exact = {"triggered": True, "guard_blocked": True, "entry_cost_filter": {"proxy_edge_available": True, "passed": False}}
    assert q16._candidate_class(exact) == "EXACT_PROXY_ONLY_REJECTION"
    assert q16._candidate_class({**exact, "triggered": False}) == ""
    assert q16._candidate_class({"triggered": True, "guard_blocked": True, "reason": "cost_edge_fail", "entry_quant_cost_floor_state": "not_met"}) == "LEGACY_COST_REJECTION_UNATTRIBUTED"
    assert q16._q17_candidate_class({"triggered": True}) == "DIRECTIONAL_ESTIMATE_ARTIFACT_MISSING"
    assert q16._q17_candidate_class({"triggered": True, "directional_edge_estimate": {"available": False}}) == "DIRECTIONAL_EVIDENCE_UNAVAILABLE"
    rows = [_row("2026-07-23", "EXACT_PROXY_ONLY_REJECTION", 0.4, 0.6, q17_candidate_class="") for _ in range(3)]
    rows += [_row("2026-07-28", "", 0.2, 0.3, q17_candidate_class="DIRECTIONAL_BELOW_COST_REJECTION",
                  directional_edge_estimate={"forward_horizon": "30m", "strategy_horizon": "intraday"})]
    for i, r in enumerate(rows):
        r["symbol"] = f"S{i}"
        r["q9_decision_id"] = f"D{i}"
    monkeypatch.setattr(q16, "_load_day_rows", lambda root, day: [dict(r) for r in rows])
    monkeypatch.setattr(q16, "load_broker_cost_profile", lambda *_: {})
    review = q16.build_q16_proxy_rejection_review(reports_root=tmp_path / "reports", day="2026-07-28")
    assert review["decision"] == "RETAIN" and review["decision_authority"]["status"] == "FINAL_CLOSED"
    assert review["decision_authority"]["rolling_diagnostic_decision"] == "INSUFFICIENT_EVIDENCE"
    assert review["counts"]["exact_trusted_forward_count"] == 3 and review["counts"]["exact_observed_30m_count"] == 3
    q17 = review["q17_directional_edge_validation"]
    assert q17["class_counts"] == {"DIRECTIONAL_BELOW_COST_REJECTION": 1}
    assert q17["below_cost_expected_horizon"][0]["strategy_horizon"] == "intraday"
    md = q16.render_q16_proxy_rejection_review(review)
    assert "Q16 is closed." in md and "### Below-Cost Results At Intended Horizon" in md
    active = q16.build_q16_proxy_rejection_review(reports_root=tmp_path / "reports", day="2026-07-23")
    assert active["decision_authority"]["status"] == "ACTIVE_WINDOW" and active["evidence_status"] == "INSUFFICIENT_EVIDENCE"


def test_cost_basis_bases_and_comparison_rows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    bases = cost_basis.build_evaluation_cost_bases({"conservative_round_trip_cost_pct": 0.01, "source": "obs", "sample_count": 4})
    assert bases["mock_observed"]["round_trip_cost_pct"] == 1.0 and bases["live_deployment_equity"]["round_trip_cost_pct"] == 0.23
    assert cost_basis.build_evaluation_cost_bases(None)["mock_observed"]["source"] == "fallback"
    reviews = {}

    def review(payloads, *, cost_pct, slippage_pct, minute_rows_by_symbol=None):
        reviews[cost_pct] = 1
        return {"pre_strategist_universe_available": True, "topk_forward_performance": {"rows": [
            {"top_k": 3, "horizon": "+5m", "window_count": 4, "observed_day_count": 2, "gross": {"expectancy_pct": 0.5}, "net": {"expectancy_pct": 0.5 - cost_pct}},
            {"top_k": 1, "horizon": "+5m", "window_count": 2, "observed_day_count": 1, "gross": {}, "net": {}}]}}

    monkeypatch.setattr(cost_basis, "load_quant_shadow_candidate_payloads_for_range", lambda **_: [])
    monkeypatch.setattr(cost_basis, "load_broker_cost_profile", lambda *_: {"conservative_round_trip_cost_pct": 0.004})
    monkeypatch.setattr(cost_basis, "extract_pre_strategist_candidate_rows", lambda p: [])
    monkeypatch.setattr(cost_basis, "load_q9_forward_candles", lambda *a, **k: {})
    monkeypatch.setattr(cost_basis, "build_scanner_quality_review", review)
    result = cost_basis.build_cost_basis_comparison(reports_root=tmp_path, start="2026-07-01", end="2026-07-01")
    assert [(r["top_k"], r["horizon"]) for r in result["rows"]] == [(1, "+5m"), (3, "+5m")]
    assert result["rows"][1]["expectancy_delta_live_minus_mock_pct"] == round((0.5 - 0.23) - (0.5 - 0.4), 4)
    assert result["interpretation"]["policy_change_authorized"] is False
    assert "| 3 | +5m | 4/2 |" in cost_basis.render_cost_basis_comparison(result)


def test_a83_helper_is_pure() -> None:
    source = Path(qw.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "collections", "datetime", "typing", ".metrics"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", ".now("):
        assert banned not in source, banned
