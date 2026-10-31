"""q8_shadow_blocker_review projections (moved verbatim from q8_shadow_blocker_review).

Module globals and helpers are resolved on ``facade`` (the q8_shadow_blocker_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _decision_for_row(row: Mapping[str, Any], *, facade: Any) -> str:
    reason = facade._text(row.get("reason"))
    if reason == "volume_confirmation_missing":
        return "retain_under_observation"
    if reason in {"breakout_not_ready", "pullback_not_mature"}:
        return "adjust_and_retest"
    if reason == "human_chart_sanity_guard_blocked":
        return "promotion_review_target"
    return "retain_under_observation"
