"""``_feature_candidates`` moved verbatim from builder.py.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _feature_candidates(
    feature_payload: Mapping[str, Any],
    prospective_payload: Mapping[str, Any],
    concentrations: Mapping[str, Mapping[str, Any]],
    *,
    facade: Any,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prospective_rows = prospective_payload.get("candidate_summaries") or []
    specs = [
        (
            "R1_SCANNER_RISK_HIGH_30M_V1",
            "scanner.risk_band == HIGH",
            "+30m",
            "SCANNER",
        ),
        (
            "R1_ENTRY_DAILY_MA5_20_EXTENDED_15M_V1",
            "chart.daily_ma5_20_cross_state == POST_CROSS_EXTENDED",
            "+15m",
            "MONITOR_ENTRY",
        ),
    ]
    selected = feature_payload.get("prospective_shadow_candidates") or []
    for candidate_id, label, horizon, owner in specs:
        prospective = facade.find_by_id(prospective_rows, "candidate_id", candidate_id)
        candidate_meta = facade.mapping(prospective.get("candidate"))
        expected = candidate_meta.get("expected_value")
        feature_path = candidate_meta.get("feature_path")
        historical_row = next(
            (
                facade.mapping(row)
                for row in selected
                if facade.mapping(row).get("feature") == feature_path
                and facade.mapping(row).get("category") == expected
            ),
            {},
        )
        decision = facade.mapping(prospective.get("decision"))
        source_status = str(
            decision.get("status")
            or historical_row.get("decision")
            or "INSUFFICIENT_EVIDENCE"
        )
        bucket = (
            "ACTION_REVIEW"
            if source_status == "SINGLE_BEHAVIOR_PATCH_REVIEW_ELIGIBLE"
            else "OBSERVE_FIXED"
        )
        branch = facade.metric_snapshot(prospective.get("branch"))
        rows.append(
            facade._candidate(
                candidate_id=candidate_id,
                track_id="OPENING_CONDITIONAL",
                discriminator=label,
                target_horizon=horizon,
                source_status=source_status,
                board_bucket=bucket,
                owner=owner,
                historical=facade.metric_snapshot(historical_row.get("train")),
                validation=facade.metric_snapshot(historical_row.get("validation")),
                prospective=branch,
                concentration=concentrations.get(candidate_id),
                evidence_note=(
                    "Prospective에서도 비교군을 이겼지만 날짜·종목 집중도 민감도 검토가 필요함."
                    if bucket == "ACTION_REVIEW"
                    else "과거 방향성이 prospective에서 유지되지 못함."
                ),
                next_action=(
                    "집중 종목·최대 일자를 제외한 민감도 검토 후 승격 또는 기각. 다른 영역은 변경하지 않음."
                    if bucket == "ACTION_REVIEW"
                    else "관측만 유지하고 과거 성과만으로 승격하지 않음."
                ),
                source_keys=["feature_candidates", "prospective_candidates"],
            )
        )
    return rows
