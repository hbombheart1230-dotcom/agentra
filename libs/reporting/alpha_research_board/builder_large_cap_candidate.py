"""``_large_cap_candidate`` moved verbatim from builder.py as ``large_cap_candidate``.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def large_cap_candidate(reports_root: Path, through_day: str, *, facade: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    review = facade.build_large_cap_daily_review(
        reports_root=reports_root, through_day=through_day
    )
    live_net = facade.metric_snapshot(review.get("base"))
    live_net["window_count"] = int(facade.mapping(review.get("base")).get("window_count") or 0)
    row = facade._candidate(
        candidate_id="SAMSUNG_HYNIX_FIXED_UNIVERSE_TOP1",
        track_id="LARGE_CAP_TWO_SYMBOL",
        discriminator="momentum + volume confirmation within fixed two-symbol universe",
        target_horizon="+180m",
        source_status=str(review.get("decision") or "RUNTIME_DATA_REQUIRED"),
        board_bucket="BACKGROUND_RUNTIME_REQUIRED",
        owner="SAMSUNG_HYNIX_BASELINE",
        prospective=live_net,
        evidence_note="정합성 수정 이후 하루만 비교 가능하며 반복 window는 독립 거래가 아님.",
        next_action="과거 시점 오류 자료를 섞지 않고 수정 이후 day-level episode만 누적.",
        source_keys=["large_cap_daily"],
    )
    return row, {
        "path": "multiple_daily_artifacts",
        "available": bool(review.get("source_count")),
        "error": "INVALID_DAILY_ARTIFACT" if review.get("invalid_sources") else None,
        "through_day": through_day,
        "source_count": review.get("source_count"),
    }
