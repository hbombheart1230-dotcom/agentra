"""Pure root-cause classification for the Q9 full-chain component review (P1.5 DEV-A).

Top-k metric lookup and the root-cause decision tree over already computed role metrics. No I/O, clock or loaders:
every helper, threshold and contract constant is read on the injected ``facade``
(``libs.reporting.evaluation.full_chain_component_review``) at call time, so patching a facade attribute behaves as
before the move.
"""
from __future__ import annotations

from typing import Any, Mapping


def _topk_metric_impl(
    scanner_quality: Mapping[str, Any],
    *,
    top_k: int,
    horizon: str,
    facade: Any,
) -> dict[str, Any]:
    topk = scanner_quality.get("topk_forward_performance")
    topk = topk if isinstance(topk, Mapping) else {}
    return next(
        (
            dict(row)
            for row in topk.get("rows") or []
            if isinstance(row, Mapping)
            and int(row.get("top_k") or 0) == top_k
            and str(row.get("horizon") or "") == horizon
        ),
        {},
    )


def _classify_root_cause_impl(
    *,
    scanner_quality: Mapping[str, Any],
    attribution: Mapping[str, Any],
    entry: Mapping[str, Any],
    exit_hold: Mapping[str, Any],
    facade: Any,
) -> dict[str, Any]:
    scanner_top1 = facade._topk_metric(scanner_quality, top_k=1, horizon="+30m")
    scanner_top3 = facade._topk_metric(scanner_quality, top_k=3, horizon="+30m")
    scanner_enough = bool(
        int(scanner_top1.get("window_count") or 0) >= facade.DIRECTIONAL_MIN_OBSERVATIONS
        and int(scanner_top1.get("observed_day_count") or 0) >= facade.DIRECTIONAL_MIN_DAYS
    )
    top1_net = facade._number((scanner_top1.get("net") or {}).get("expectancy_pct"))
    top3_net = facade._number((scanner_top3.get("net") or {}).get("expectancy_pct"))
    scanner_fail = bool(
        scanner_enough
        and top1_net is not None
        and top3_net is not None
        and top1_net <= 0.0
        and top3_net <= 0.0
    )

    attribution_30 = next(
        (
            row
            for row in attribution.get("by_horizon") or []
            if isinstance(row, Mapping) and row.get("horizon") == "+30m"
        ),
        {},
    )
    strategist_enough = bool(
        int(attribution_30.get("strategist_comparison_count") or 0)
        >= facade.DIRECTIONAL_MIN_OBSERVATIONS
        and int(attribution_30.get("strategist_day_count") or 0) >= facade.DIRECTIONAL_MIN_DAYS
    )
    commander_enough = bool(
        int(attribution_30.get("commander_comparison_count") or 0)
        >= facade.DIRECTIONAL_MIN_OBSERVATIONS
        and int(attribution_30.get("commander_day_count") or 0) >= facade.DIRECTIONAL_MIN_DAYS
    )
    strategist_delta = facade._number(attribution_30.get("average_strategist_delta_pct"))
    commander_delta = facade._number(attribution_30.get("average_commander_delta_pct"))
    strategist_fail = bool(
        strategist_enough
        and strategist_delta is not None
        and strategist_delta <= -facade.MIN_MATERIAL_RANKING_DELTA_PCT
    )
    commander_fail = bool(
        commander_enough
        and commander_delta is not None
        and commander_delta <= -facade.MIN_MATERIAL_RANKING_DELTA_PCT
    )

    entry_enough = bool(
        int(entry.get("matched_trade_count") or 0) >= facade.DIRECTIONAL_MIN_OBSERVATIONS
        and int(entry.get("matched_day_count") or 0) >= facade.DIRECTIONAL_MIN_DAYS
    )
    entry_delta = facade._number(entry.get("average_entry_price_delta_pct"))
    entry_fail = bool(entry_enough and entry_delta is not None and entry_delta > 0.30)

    exit_enough = bool(
        int(exit_hold.get("observed_trade_count") or 0) >= facade.DIRECTIONAL_MIN_OBSERVATIONS
        and int(exit_hold.get("observed_day_count") or 0) >= facade.DIRECTIONAL_MIN_DAYS
    )
    exit_5m = next(
        (
            row
            for row in exit_hold.get("by_hold_offset") or []
            if isinstance(row, Mapping) and row.get("offset") == "+5m"
        ),
        {},
    )
    exit_improvement = facade._number(exit_5m.get("average_improvement_pct"))
    exit_fail = bool(exit_enough and exit_improvement is not None and exit_improvement >= 0.30)

    statuses = {
        "scanner_intrinsic_fail": scanner_fail,
        "strategist_degradation": strategist_fail,
        "commander_over_filtering": commander_fail,
        "monitor_entry_fail": entry_fail,
        "monitor_exit_fail": exit_fail,
    }
    primary = next((name for name, active in statuses.items() if active), "")
    if not primary:
        primary = (
            "no_dominant_problem"
            if all((scanner_enough, strategist_enough, commander_enough, entry_enough, exit_enough))
            else "insufficient_sample"
        )
    return {
        "schema_version": "q9_problem_segment_classification.v1",
        "behavior_effect": "evaluation_only",
        "primary_root_cause": primary,
        "statuses": statuses,
        "sample_status": {
            "scanner": scanner_enough,
            "strategist": strategist_enough,
            "commander": commander_enough,
            "monitor_entry": entry_enough,
            "monitor_exit": exit_enough,
        },
        "evidence": {
            "scanner_top1_net_expectancy_pct": top1_net,
            "scanner_top3_net_expectancy_pct": top3_net,
            "strategist_delta_pct": strategist_delta,
            "commander_delta_pct": commander_delta,
            "monitor_entry_price_delta_pct": entry_delta,
            "monitor_exit_5m_improvement_pct": exit_improvement,
        },
    }
