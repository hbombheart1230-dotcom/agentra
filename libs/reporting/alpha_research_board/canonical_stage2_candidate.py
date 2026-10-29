"""``_stage2_candidate`` moved verbatim from canonical.py as ``stage2_candidate``.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def stage2_candidate(reports_root: Path, through_day: str, *, facade: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    payload, source = facade._latest_stage2_source(reports_root, through_day)
    metric = facade.mapping(facade.mapping(payload.get("changed_symbol_by_horizon")).get("+30m"))
    coverage = facade.mapping(payload.get("coverage"))
    historical = {
        "sample_count": int(metric.get("comparison_count") or 0),
        "window_count": int(metric.get("observation_count") or 0),
        "win_rate": metric.get("after_positive_rate"),
        "avg_net_return_pct": metric.get("after_average_return_pct"),
        "profit_factor": None,
        "max_drawdown_pct": None,
        "coverage": None,
        "avg_mfe_pct": None,
        "avg_mae_pct": None,
    }
    return (
        {
            "candidate_id": "STRATEGIST_STAGE2_REFRESH_AUTHORITY_V1",
            "target_horizon": "+30m",
            "source_status": "OBSERVATION_ONLY",
            "board_bucket": "OBSERVE_FIXED",
            "historical": historical,
            "validation": {},
            "prospective": {},
            "concentration": {
                "day_count": metric.get("day_count"),
                "max_single_day_share": metric.get("max_single_day_share"),
            },
            "agent_attribution": {
                "refresh_records": coverage.get("refresh_records"),
                "stage2_attributable_records": coverage.get("stage2_attributable_records"),
                "same_symbol_records": coverage.get("same_symbol_records"),
                "changed_symbol_records": coverage.get("changed_symbol_records"),
                "before_avg_return_pct": metric.get("before_average_return_pct"),
                "after_avg_return_pct": metric.get("after_average_return_pct"),
                "average_delta_pct": metric.get("average_delta_pct"),
                "interpretation": facade.mapping(payload.get("role_definition")).get(
                    "important_boundary"
                ),
            },
            "evidence_note": (
                "R2는 2차 전략가 이후 Scanner 재실행 결과이며 LLM의 명시적 종목 교체와 동일하지 않다."
            ),
            "next_action": "재순위·후보 교체·진입 강화·no-trade 권한별 표본만 누적한다.",
            "source_keys": ["strategist_stage2_effectiveness"],
        },
        source,
    )
