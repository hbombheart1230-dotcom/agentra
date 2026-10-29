"""``_negative_control_candidate`` moved verbatim from canonical.py as ``negative_control_candidate``.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def negative_control_candidate(short_alpha: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    cohorts = facade.mapping(short_alpha.get("cohort_review")).get("cohorts") or []
    cohort = next(
        (
            facade.mapping(value)
            for value in cohorts
            if facade.mapping(value).get("cohort_id") == "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1"
        ),
        {},
    )
    historical = facade.metric_snapshot(facade.mapping(cohort.get("horizons")).get("+5m"))
    return {
        "candidate_id": "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1",
        "target_horizon": "+5m",
        "source_status": "NEGATIVE_CONTROL",
        "board_bucket": "OBSERVE_FIXED",
        "historical": historical,
        "validation": {},
        "prospective": {},
        "concentration": {
            "day_count": cohort.get("day_count"),
            "largest_day_share": cohort.get("largest_day_share"),
            "largest_symbol_share": cohort.get("largest_symbol_share"),
        },
        "evidence_note": "거래대금·거래량만 높은 후보가 충분한 구분자인지 확인하는 고정 음성 대조군이다.",
        "next_action": "대조군으로만 누적하며 독립 정책 후보로 승격하지 않는다.",
        "source_keys": ["short_alpha_discriminator"],
    }
