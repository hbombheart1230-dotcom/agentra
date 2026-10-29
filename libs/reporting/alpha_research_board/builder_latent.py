"""Alpha research board: ``_latent`` (moved verbatim from builder).

Helpers are resolved on ``facade`` (the builder module) at call time; this module never imports the builder.
"""
from __future__ import annotations

from typing import Any, Mapping


def _latent(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    summary = facade.mapping(payload.get("summary"))
    horizon = facade.mapping(facade.mapping(summary.get("horizons")).get("+30m"))
    return facade._candidate(
        candidate_id="LATENT_REACTIVATION_FRESH_TRIGGER",
        track_id="SCANNER_REACTIVATION_HORIZON",
        discriminator="fresh D+1-D+5 trigger after prior Rank-1 discovery",
        target_horizon="+30m",
        source_status=str(summary.get("status") or "INSUFFICIENT_EVIDENCE"),
        board_bucket="CLOSED",
        owner="NONE",
        prospective=facade.metric_snapshot(horizon.get("live_net")),
        concentration={
            "largest_day_share": summary.get("largest_day_share"),
            "largest_symbol_share": summary.get("largest_symbol_share"),
            "positive_day_ratio": summary.get("positive_day_ratio"),
        },
        evidence_note="수익률은 양수지만 날짜·종목 집중도와 양수 일자 gate를 통과하지 못함.",
        next_action="고정 계약은 기각하고 30~60분 방향성만 연구 힌트로 보존.",
        source_keys=["latent_reactivation"],
    )
