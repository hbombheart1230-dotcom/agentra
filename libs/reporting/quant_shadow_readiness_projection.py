"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


def _shadow_readiness(candidates: Sequence[Mapping[str, Any]], promotion: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    candidate_count = len(candidates)
    evaluated_count = sum(1 for row in candidates if facade._bool(row.get("evaluated")))
    evaluated_ratio = float(evaluated_count) / float(candidate_count) if candidate_count else 0.0
    candidate = facade._text(promotion.get("candidate"))
    confidence = facade._text(promotion.get("confidence"))
    action = facade._text(promotion.get("recommended_action")) or "hold"
    ready = bool(
        candidate_count >= facade.TRUSTED_FORWARD_MIN_COUNT
        and evaluated_count >= facade.PROMOTION_CANDIDATE_MIN_OBSERVED
        and evaluated_ratio >= facade.TRUSTED_FORWARD_MIN_COVERAGE
        and candidate not in {"", "hold"}
        and confidence in {"medium", "high"}
    )
    if not candidate_count:
        status = "hold_no_shadow_candidates"
    elif ready:
        status = "ready"
    elif evaluated_count < facade.PROMOTION_CANDIDATE_MIN_OBSERVED:
        status = "hold_shadow_sample_insufficient"
    elif evaluated_ratio < facade.TRUSTED_FORWARD_MIN_COVERAGE:
        status = "hold_shadow_coverage_insufficient"
    else:
        status = "review_shadow_signal_weak"
    return {
        "status": status,
        "action": action if ready else "hold",
        "candidate_count": candidate_count,
        "evaluated_count": evaluated_count,
        "evaluated_ratio": evaluated_ratio,
        "sample_floor": facade.TRUSTED_FORWARD_MIN_COUNT,
        "evaluated_floor": facade.PROMOTION_CANDIDATE_MIN_OBSERVED,
        "coverage_floor": facade.TRUSTED_FORWARD_MIN_COVERAGE,
        "candidate": candidate or "hold",
        "confidence": confidence or "none",
        "promotion_scope": facade._text(promotion.get("promotion_scope")) or "none",
    }
