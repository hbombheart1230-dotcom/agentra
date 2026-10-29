"""Alpha research board: ``_fresh_change`` (moved verbatim from builder).

Helpers are resolved on ``facade`` (the builder module) at call time; this module never imports the builder.
"""
from __future__ import annotations

from typing import Any, Mapping


def _fresh_change(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    reference = facade.mapping(payload.get("historical_reference"))
    historical = facade.mapping(reference.get("branch"))
    historical_metric = facade.mapping(facade.mapping(historical.get("horizons")).get("+30m"))
    prospective_metric = facade.mapping(facade.mapping(facade.mapping(payload.get("branch")).get("horizons")).get("+30m"))
    source_status = str(facade.mapping(payload.get("decision")).get("status") or "INSUFFICIENT_EVIDENCE")
    return facade._candidate(
        candidate_id="R1_FRESH_CHANGE_ACTIVATION_V1",
        track_id="OPENING_CONDITIONAL",
        discriminator="fresh top-change activation",
        target_horizon="+30m",
        source_status=source_status,
        board_bucket="CLOSED_NEGATIVE_PROSPECTIVE",
        owner="SCANNER",
        historical=facade.metric_snapshot(historical_metric),
        prospective=facade.metric_snapshot(prospective_metric),
        evidence_note="과거 양수 결과가 prospective에서 음수로 뒤집힘.",
        next_action="승격 후보에서 기각하고 과거 참고자료로만 보존.",
        source_keys=["fresh_change"],
    )
