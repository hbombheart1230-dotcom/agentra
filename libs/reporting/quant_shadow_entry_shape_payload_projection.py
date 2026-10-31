"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


def _entry_shape_payload(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    shapes = facade.Counter(facade._entry_shape(row) for row in candidates)
    pullback_blocked = sum(
        1
        for row in candidates
        if facade._entry_shape(row) in {"pullback", "vwap_reclaim"}
        and not facade._bool(row.get("would_enter"))
    )
    breakout_ready = sum(
        1
        for row in candidates
        if facade._entry_shape(row) == "breakout"
        and (
            facade._bool(row.get("would_enter"))
            or facade._text(row.get("reason"))
            in {
                "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation",
                "breakout_above_recent_high_with_vwap_structure_confirmation",
            }
        )
    )
    breakout_not_ready = sum(
        1
        for row in candidates
        if facade._entry_shape(row) == "breakout" and not facade._bool(row.get("would_enter"))
    )
    return {
        "behavior_effect": "diagnostic_only",
        "by_shape": facade._top_counter(shapes),
        "pullback_or_vwap_blocked_count": pullback_blocked,
        "breakout_ready_like_count": breakout_ready,
        "breakout_not_ready_count": breakout_not_ready,
    }
