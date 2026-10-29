"""RF-034 C3: alpha_research_board.canonical status/operation/fixed-validation/promotion tables and small helpers (pure)."""
from __future__ import annotations

import json

import pytest

from libs.reporting.alpha_research_board import canonical as cn


def test_normalize_status_priority_table():
    n = cn._normalize_status
    closed_id = sorted(cn.PERMANENTLY_CLOSED)[0]
    assert n(closed_id, {"final_offline_review": {"decision": "PROMOTED"}}) == "CLOSED"                         # permanent closure outranks everything
    assert n("X", {"final_offline_review": {"decision": "PROMOTED"}}) == "PROMOTED"
    assert n("X", {"final_offline_review": {"decision": "PROMOTION_REVIEW_PASS"}}) == "REVIEW_READY"           # PROMOT + REVIEW is not promoted
    assert n("X", {"sensitivity_review": {"decision": "REJECT_BASE_EFFECT"}}) == "CLOSED"
    assert n("X", {"final_offline_review": {"decision": "FAIL_RUNTIME"}}) == "CLOSED"
    assert n("X", {"board_bucket": "closed_x"}) == "CLOSED"
    assert n("X", {"final_offline_review": {"decision": "PASS_X"}}) == "REVIEW_READY"
    assert n("X", {"source_status": "review_eligible"}) == "REVIEW_READY" and n("X", {"source_status": "REVIEW_READY_NOW"}) == "REVIEW_READY"
    for b in ("RUNTIME_VALIDATION_NEXT", "BACKGROUND_RUNTIME_REQUIRED", "OBSERVE_FIXED"):
        assert n("X", {"board_bucket": b.lower()}) == "PROSPECTIVE"
    assert n("X", {}) == "DISCOVERY" and n("X", {"board_bucket": "OTHER"}) == "DISCOVERY"
    assert n("X", {"final_offline_review": {"decision": ""}, "sensitivity_review": {"decision": "PASS"}}) == "REVIEW_READY"      # first non-empty decision wins
    assert n("X", {"final_offline_review": {"decision": "REJECT"}, "sensitivity_review": {"decision": "PASS"}}) == "CLOSED"


def test_operation_status_table():
    o = cn._operation_status
    assert o("X", "CLOSED", {"source_status": "SHADOW"}) == "NOT_RUNNING"
    assert o("X", "DISCOVERY", {"operation_authority": {"enabled": False}, "source_status": "SHADOW"}) == "NOT_RUNNING"
    assert o("X", "DISCOVERY", {"source_status": "x_disabled"}) == "NOT_RUNNING" and o("X", "DISCOVERY", {"board_bucket": "disabled"}) == "NOT_RUNNING"
    assert o("X", "DISCOVERY", {"source_status": "Shadow_only"}) == "SHADOW_CONTINUES"
    for sv in ("OBSERVATION_ONLY", "NEGATIVE_CONTROL"):
        assert o("X", "DISCOVERY", {"source_status": sv}) == "SHADOW_CONTINUES"
    assert o("X", "DISCOVERY", {"board_bucket": "OBSERVE_FIXED"}) == "SHADOW_CONTINUES"
    ctl = {"operation_authority": {"enabled": True, "mode": "controlled_mock"}}
    assert o("IMMEDIATE_OPENING_PROBE", "PROSPECTIVE", ctl) == "CONTROLLED_MOCK_CONTINUES"
    assert o("OTHER_ID", "PROSPECTIVE", ctl) == "UNKNOWN_OPERATION_STATUS"                                       # only governed probe ids qualify
    assert o("IMMEDIATE_OPENING_PROBE", "PROSPECTIVE", {"operation_authority": {"enabled": True, "mode": "live"}}) == "UNKNOWN_OPERATION_STATUS"
    assert o("IMMEDIATE_OPENING_PROBE", "PROSPECTIVE", {"operation_authority": "enabled"}) == "UNKNOWN_OPERATION_STATUS"
    assert o("IMMEDIATE_OPENING_PROBE", "PROSPECTIVE", {"source_status": "SHADOW", **ctl}) == "SHADOW_CONTINUES"          # shadow signal outranks controlled-mock
    assert o("IMMEDIATE_OPENING_PROBE", "PROSPECTIVE", {"source_status": "SHADOW_DISABLED", **ctl}) == "NOT_RUNNING"


@pytest.mark.parametrize("rv,expected", [
    ({"candidate_id": "OTHER"}, "FIXED_VALIDATION_NOT_YET_RUN"),
    ({"candidate_id": "C", "window_complete": False, "decision": "PASS_RUNTIME_VALIDATION"}, "FIXED_VALIDATION_PENDING"),
    ({"candidate_id": "C", "window_complete": True, "decision": "PASS_RUNTIME_VALIDATION"}, "FIXED_VALIDATION_PASSED"),
    ({"candidate_id": "C", "window_complete": True, "decision": "FAIL_RUNTIME_EFFECT"}, "FIXED_VALIDATION_FAILED"),
    ({"candidate_id": "C", "window_complete": True, "decision": "FAIL_RUNTIME_INTEGRITY"}, "FIXED_VALIDATION_INSUFFICIENT_EVIDENCE"),
    ({"candidate_id": "C", "window_complete": True, "decision": "INSUFFICIENT_RUNTIME_SAMPLE"}, "FIXED_VALIDATION_INSUFFICIENT_EVIDENCE"),
    ({"candidate_id": "C", "window_complete": True, "decision": "WHATEVER"}, "FIXED_VALIDATION_INSUFFICIENT_EVIDENCE"),
    ({}, "FIXED_VALIDATION_NOT_YET_RUN"),
])
def test_fixed_validation_status(rv, expected):
    assert cn._fixed_validation_status("C", rv) == expected


def test_production_promotion_requires_promoted_and_passed():
    p = cn._production_promotion_status
    assert p("PROMOTED", "FIXED_VALIDATION_PASSED") == "PRODUCTION_PROMOTION_ALLOWED"
    for s, f in (("PROMOTED", "FIXED_VALIDATION_FAILED"), ("REVIEW_READY", "FIXED_VALIDATION_PASSED"), ("CLOSED", "FIXED_VALIDATION_PASSED")):
        assert p(s, f) == "PRODUCTION_PROMOTION_NOT_ALLOWED"


def test_decision_and_rationale_fallback_chains():
    assert cn._decision({"final_offline_review": {"decision": "A"}, "sensitivity_review": {"decision": "B"}, "source_status": "C"}) == "A"
    assert cn._decision({"sensitivity_review": {"decision": "B"}, "source_status": "C"}) == "B" and cn._decision({"source_status": "C"}) == "C"
    assert cn._decision({}) == "INSUFFICIENT_EVIDENCE"
    assert cn._rationale({"final_offline_review": {"rationale": "R1"}, "sensitivity_review": {"rationale": "R2"}, "evidence_note": "R3"}) == "R1"
    assert cn._rationale({"sensitivity_review": {"rationale": "R2"}, "evidence_note": "R3"}) == "R2" and cn._rationale({"evidence_note": "R3"}) == "R3"
    assert "설명 가능한 근거가 없다" in cn._rationale({})


def test_net_metrics_prefers_prospective_then_validation_then_historical():
    m = lambda n: {"sample_count": n, "avg_net_return_pct": 1.0}  # noqa: E731
    assert cn._net_metrics({"prospective": m(1), "validation": m(9), "historical": m(9)})["cohort"] == "prospective"
    assert cn._net_metrics({"prospective": m(0), "validation": m(2), "historical": m(9)})["cohort"] == "validation"
    assert cn._net_metrics({"historical": m(3)})["cohort"] == "historical"
    empty = cn._net_metrics({})
    assert empty["cohort"] is None and empty["sample_count"] == 0


def _w(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def test_latest_stage2_source_selects_newest_cumulative_not_after_through_day(tmp_path):
    base = tmp_path / "evaluation" / "agent_effectiveness"
    name = "strategist_stage2_effectiveness_deep_dive.json"
    _w(base / "cumulative_20260801_20260820" / name, {"schema_version": "old"})
    _w(base / "cumulative_20260801_20260825" / name, {"schema_version": "mid"})
    _w(base / "cumulative_20260801_20260901" / name, {"schema_version": "future"})
    payload, src = cn._latest_stage2_source(tmp_path, "2026-08-28")
    assert payload["schema_version"] == "mid" and "20260825" in src["path"]
    assert cn._latest_stage2_source(tmp_path, "2026-08-25")[0]["schema_version"] == "mid"                      # boundary inclusive
    payload, src = cn._latest_stage2_source(tmp_path / "none", "2026-08-28")
    assert payload == {} and src["error"] == "MISSING_ARTIFACT"
    _w(tmp_path / "d" / "evaluation" / "agent_effectiveness" / "2026-08-28" / name, {"schema_version": "daily"})
    assert cn._latest_stage2_source(tmp_path / "d", "2026-08-28")[0]["schema_version"] == "daily"               # daily fallback when no cumulative


def test_negative_control_candidate_reads_5m_horizon_and_defaults():
    sa = {"cohort_review": {"cohorts": [{"cohort_id": "OTHER"}, {"cohort_id": "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1", "day_count": 4, "largest_day_share": 0.3, "largest_symbol_share": 0.2,
                                                                  "horizons": {"+5m": {"sample_count": 7, "avg_net_return_pct": -0.1}, "+30m": {"sample_count": 99}}}]}}
    c = cn._negative_control_candidate(sa)
    assert c["candidate_id"] == "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1" and c["historical"]["sample_count"] == 7 and c["concentration"] == {"day_count": 4, "largest_day_share": 0.3, "largest_symbol_share": 0.2}
    assert c["source_status"] == "NEGATIVE_CONTROL" and c["board_bucket"] == "OBSERVE_FIXED" and c["target_horizon"] == "+5m"
    assert cn._negative_control_candidate({})["historical"]["sample_count"] == 0


def test_question_summaries_counts_and_buckets():
    qid = str(cn.QUESTIONS[0]["question_id"])
    rows = [{"question_id": qid, "candidate_id": "a", "status": "DISCOVERY"}, {"question_id": qid, "candidate_id": "b", "status": "CLOSED"},
            {"question_id": qid, "candidate_id": "c", "status": "REVIEW_READY"}, {"question_id": "other", "candidate_id": "z", "status": "CLOSED"}]
    out = cn._question_summaries(rows)
    assert len(out) == len(cn.QUESTIONS)
    first = out[0]
    assert first["candidate_count"] == 3 and first["active_candidate_ids"] == ["a", "c"] and first["closed_candidate_ids"] == ["b"]
    assert first["status_counts"]["DISCOVERY"] == 1 and set(first["status_counts"]) == set(cn.ALLOWED_STATUSES)


def test_controlled_mock_requires_literal_enabled_true_and_literal_mode():
    o = cn._operation_status
    cid = "IMMEDIATE_OPENING_PROBE"
    assert o(cid, "PROSPECTIVE", {"operation_authority": {"mode": "controlled_mock"}}) == "UNKNOWN_OPERATION_STATUS"               # enabled missing
    assert o(cid, "PROSPECTIVE", {"operation_authority": {"enabled": None, "mode": "controlled_mock"}}) == "UNKNOWN_OPERATION_STATUS"
    assert o(cid, "PROSPECTIVE", {"operation_authority": {"enabled": 1, "mode": "controlled_mock"}}) == "UNKNOWN_OPERATION_STATUS"   # truthy is not True
    assert o(cid, "PROSPECTIVE", {"operation_authority": {"enabled": "yes", "mode": "controlled_mock"}}) == "UNKNOWN_OPERATION_STATUS"
    assert o(cid, "PROSPECTIVE", {"operation_authority": {"enabled": True, "mode": "paper"}}) == "UNKNOWN_OPERATION_STATUS"
    assert o(cid, "PROSPECTIVE", {"operation_authority": {"enabled": True, "mode": "controlled_mock"}}) == "CONTROLLED_MOCK_CONTINUES"
