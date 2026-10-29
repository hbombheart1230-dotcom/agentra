"""Alpha research board: ``_broad_opening`` (moved verbatim from builder).

Helpers are resolved on ``facade`` (the builder module) at call time; this module never imports the builder.
"""
from __future__ import annotations

from typing import Any, Mapping


def _broad_opening(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    decision = facade.mapping(payload.get("promotion_decision"))
    values = facade.mapping(decision.get("values"))
    return facade._candidate(
        candidate_id="OPEN_0_20_RANK1_30M",
        track_id="OPENING_CONDITIONAL",
        discriminator="all opening Rank-1 candidates",
        target_horizon="+30m",
        source_status=str(decision.get("status") or "INSUFFICIENT_EVIDENCE"),
        board_bucket="CLOSED",
        owner="NONE",
        prospective={
            "sample_count": values.get("observed_count", 0),
            "window_count": values.get("observed_count", 0),
            "win_rate": values.get("win_rate"),
            "avg_net_return_pct": values.get("average_net_return_pct"),
            "profit_factor": values.get("profit_factor"),
            "coverage": values.get("coverage"),
        },
        concentration={
            "largest_day_share": values.get("largest_day_share"),
            "largest_symbol_share": values.get("largest_symbol_share"),
        },
        evidence_note="평균은 양수지만 고정된 종목 집중도 gate를 통과하지 못함.",
        next_action="종료. Rank-1 전부 진입 근거로 재해석하지 않음.",
        source_keys=["opening_cumulative"],
    )
