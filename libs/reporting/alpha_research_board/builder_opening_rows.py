"""Alpha research board: ``_opening_rows`` (moved verbatim from builder).

Helpers are resolved on ``facade`` (the builder module) at call time; this module never imports the builder.
"""
from __future__ import annotations

from typing import Any, Mapping


def _opening_rows(payload: Mapping[str, Any], *, facade: Any) -> list[dict[str, Any]]:
    summary = facade.mapping(payload.get("summary"))
    lanes = facade.mapping(summary.get("conditional_lane_summaries"))
    rows: list[dict[str, Any]] = []
    for lane_id, horizon, note in [
        (
            "IMMEDIATE_OPENING_PROBE",
            "+5m",
            "즉시 반응은 초반이 가장 강하고 EOD로 갈수록 약해짐.",
        ),
        (
            "CONFIRMED_RECURRENT_RANK",
            "+30m",
            "방향은 강하지만 독립 표본이 지나치게 작음.",
        ),
        (
            "DISLOCATION_REBOUND",
            "+60m",
            "5분보다 30~60분 반등 근거가 강함.",
        ),
    ]:
        lane = facade.mapping(lanes.get(lane_id))
        horizon_row = facade.mapping(facade.mapping(lane.get("horizons")).get(horizon))
        rows.append(
            facade._candidate(
                candidate_id=lane_id,
                track_id="OPENING_CONDITIONAL",
                discriminator=lane_id.lower(),
                target_horizon=horizon,
                source_status="COLLECTING",
                board_bucket="OBSERVE_FIXED",
                owner="SCANNER_OR_HORIZON_REVIEW",
                prospective=facade.metric_snapshot(horizon_row.get("live_net")),
                evidence_note=note,
                next_action="기존 고정 observer만 지속하고 새 lane은 만들지 않음.",
                source_keys=["opening_cumulative"],
            )
        )
    return rows
