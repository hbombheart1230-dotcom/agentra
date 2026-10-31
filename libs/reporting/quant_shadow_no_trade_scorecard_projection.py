"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


def _no_trade_scorecard(
    *,
    candidates: Sequence[Mapping[str, Any]],
    entry_lane_forward_outcomes: Mapping[str, Any],
    would_enter_count: int,
    opening_probe_would_enter: int,
    largecap_probe_would_enter: int,
    facade: Any,
) -> Dict[str, Any]:
    candidate_count = len(candidates)
    outcome_count = sum(1 for row in candidates if facade._bool(facade._forward_outcome(row).get("available")))
    coverage = float(outcome_count) / float(candidate_count) if candidate_count else 0.0
    lane_rows = (
        list(entry_lane_forward_outcomes.get("by_primary_lane") or [])
        if isinstance(entry_lane_forward_outcomes, facade.Mapping)
        else []
    )
    lane_subtype_rows = (
        list(entry_lane_forward_outcomes.get("by_lane_subtype") or [])
        if isinstance(entry_lane_forward_outcomes, facade.Mapping)
        else []
    )
    combined_rows = [row for row in lane_rows + lane_subtype_rows if isinstance(row, facade.Mapping)]
    missed = facade._scorecard_rows(combined_rows, mode="missed", limit=6)
    blocked = facade._scorecard_rows(combined_rows, mode="blocked", limit=6)
    watchlist = facade._named_forward_rows(
        lane_subtype_rows,
        {
            "pullback_quality:failed_pullback",
            "vwap_reclaim:reclaim_in_progress_with_improving_volume",
        },
    )
    promotion_ready_watchlist = [
        row for row in watchlist if facade._text(row.get("review_state")) == "promotion_watch"
    ]
    if candidate_count <= 0:
        status = "no_shadow_data"
        verdict = "no shadow candidates were collected"
    elif would_enter_count > 0 or opening_probe_would_enter > 0 or largecap_probe_would_enter > 0:
        status = "trade_candidates_available"
        verdict = "shadow candidates had would-enter paths; compare against actual execution"
    elif missed and blocked:
        status = "mixed_no_trade_day"
        verdict = "major weak groups were blocked, but selected subtypes show missed-opportunity signals"
    elif missed:
        status = "possible_over_blocking"
        verdict = "no would-enter candidates, but forward outcomes show positive missed-opportunity groups"
    elif blocked:
        status = "correctly_blocked"
        verdict = "no would-enter candidates and blocked groups underperformed in forward outcomes"
    else:
        status = "inconclusive_no_trade_day"
        verdict = "no would-enter candidates; forward evidence is not decisive"
    evidence_quality = (
        "high"
        if outcome_count >= facade.TRUSTED_FORWARD_MIN_COUNT and coverage >= facade.TRUSTED_FORWARD_MIN_COVERAGE
        else "medium"
        if outcome_count >= 30
        else "low"
    )
    return {
        "behavior_effect": "evaluation_only",
        "status": status,
        "verdict": verdict,
        "candidate_count": candidate_count,
        "would_enter_count": int(would_enter_count),
        "opening_momentum_probe_would_enter_count": int(opening_probe_would_enter),
        "opening_largecap_surge_would_enter_count": int(largecap_probe_would_enter),
        "forward_outcome_available_count": int(outcome_count),
        "forward_outcome_coverage": coverage,
        "evidence_quality": evidence_quality,
        "correctly_blocked_signals": blocked,
        "missed_opportunity_candidates": missed,
        "promotion_watchlist": watchlist,
        "next_review_action": (
            "review_promotion_watchlist_for_probe_candidate"
            if promotion_ready_watchlist
            else "collect_repeatability_before_promotion_review"
            if missed or watchlist
            else "retain_current_guards_and_continue_observation"
        ),
    }
