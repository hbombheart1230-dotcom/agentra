"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _evaluation_trust_gate(
    *,
    raw_candidate_count: int,
    deduped_candidate_count: int,
    trusted_forward_count: int,
    trusted_forward_coverage: float,
    no_trade_scorecard: Mapping[str, Any],
    facade: Any,
) -> Dict[str, Any]:
    watchlist = [
        row for row in list(no_trade_scorecard.get("promotion_watchlist") or []) if isinstance(row, facade.Mapping)
    ]
    gate = facade.build_q8_trust_gate(
        raw_candidate_count=raw_candidate_count,
        deduped_candidate_count=deduped_candidate_count,
        trusted_forward_count=trusted_forward_count,
        trusted_forward_coverage=trusted_forward_coverage,
        candidate_watchlist=watchlist,
    )
    promotion_ready = [
        row for row in watchlist if facade._text(row.get("review_state")) == "promotion_watch"
    ]
    return {
        "behavior_effect": "evaluation_only",
        **gate,
        "reasons": list(gate.get("block_reasons") or []),
        "raw_candidate_count": int(raw_candidate_count),
        "deduped_candidate_count": int(deduped_candidate_count),
        "promotion_ready_candidates": promotion_ready,
        "minimum_requirements": {
            **dict(gate.get("minimums") or {}),
            "candidate_avg_return_5m_pct": "> 0",
            "candidate_avg_return_15m_pct": "> 0",
        },
    }
