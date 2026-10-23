"""Pure component decision assembly for the Q9 full-chain component review (P1.5 DEV-A).

Attribution, scanner and unavailable component decision records built from already computed metrics against the
contract thresholds. No I/O or clock; thresholds, ``DecisionClass`` and helpers are read on the injected ``facade``
at call time.
"""
from __future__ import annotations

from typing import Any, Mapping


def _attribution_component_impl(
    *,
    attribution: Mapping[str, Any],
    component: str,
    question: str,
    missing_comparison: str,
    availability: dict[str, Any],
    facade: Any,
) -> dict[str, Any]:
    prefix = "strategist" if component == "strategist" else "commander"
    primary = next(
        (
            row for row in attribution.get("by_horizon") or []
            if row.get("horizon") == "+30m"
        ),
        {},
    )
    count = int(primary.get(f"{prefix}_comparison_count") or 0)
    days = int(primary.get(f"{prefix}_day_count") or 0)
    delta = facade._number(primary.get(f"average_{prefix}_delta_pct"))
    positive_rate = facade._number(primary.get(f"{prefix}_positive_delta_rate"))
    enough = count >= facade.DIRECTIONAL_MIN_OBSERVATIONS and days >= facade.DIRECTIONAL_MIN_DAYS
    material = (
        enough
        and delta is not None
        and positive_rate is not None
        and delta >= facade.MIN_MATERIAL_RANKING_DELTA_PCT
        and positive_rate >= facade.MIN_POSITIVE_RANKING_DELTA_RATE
    )
    if not enough:
        return {
            "decision": facade.DecisionClass.INSUFFICIENT_EVIDENCE.value,
            "question": question,
            "finding": (
                f"{component.title()} has {count} comparable +30m windows across {days} day(s); "
                "the fixed 20-observation and 2-day threshold is not complete."
            ),
            "missing_comparison": (
                f"at least {facade.DIRECTIONAL_MIN_OBSERVATIONS} comparable +30m windows across "
                f"{facade.DIRECTIONAL_MIN_DAYS} days; current={count} windows/{days} days"
            ),
            "availability": dict(availability),
            "primary_horizon": "+30m",
            "metrics": dict(primary),
            "behavior_change_authorized": False,
        }
    return {
        "decision": (
            facade.DecisionClass.PROMOTION_CANDIDATE.value
            if material
            else facade.DecisionClass.ADJUST_AND_RETEST.value
        ),
        "question": question,
        "finding": (
            f"{component.title()} shows a material +30m delta."
            if material
            else f"{component.title()} does not show a material +30m delta under the fixed contract."
        ),
        "missing_comparison": None,
        "primary_horizon": "+30m",
        "metrics": dict(primary),
        "behavior_change_authorized": False,
    }


def _scanner_decision_impl(
    *,
    role_metrics: list[dict[str, Any]],
    paired: list[dict[str, Any]],
    facade: Any,
) -> dict[str, Any]:
    top_30 = next(
        (row for row in role_metrics if row["role"] == "top_pick" and row["horizon"] == "+30m"),
        {},
    )
    pair_30 = next((row for row in paired if row["horizon"] == "+30m"), {})
    enough = (
        int(pair_30.get("paired_window_count") or 0) >= facade.DIRECTIONAL_MIN_OBSERVATIONS
        and int(pair_30.get("observed_day_count") or 0) >= facade.DIRECTIONAL_MIN_DAYS
    )
    relative_positive = (
        enough
        and float(pair_30.get("average_delta_pct") or 0.0) >= facade.MIN_MATERIAL_RANKING_DELTA_PCT
        and float(pair_30.get("positive_delta_rate") or 0.0) >= facade.MIN_POSITIVE_RANKING_DELTA_RATE
    )
    absolute_positive = float(top_30.get("expectancy_pct") or 0.0) > 0
    decision = (
        facade.DecisionClass.RETAIN.value
        if relative_positive and absolute_positive
        else facade.DecisionClass.ADJUST_AND_RETEST.value
        if relative_positive
        else facade.DecisionClass.ADJUST_AND_RETEST.value
        if enough
        else facade.DecisionClass.INSUFFICIENT_EVIDENCE.value
    )
    return {
        "decision": decision,
        "question": "Does Scanner ranking put stronger candidates ahead of runner-ups and retain cost-positive edge?",
        "relative_ranking_effect_positive": relative_positive,
        "absolute_cost_adjusted_edge_positive": absolute_positive,
        "primary_horizon": "+30m",
        "finding": (
            "Top-pick ordering is directionally better than evaluated runner-ups, but the selected "
            "Top-pick set remains cost-negative; ranking direction is useful while candidate quality "
            "and horizon calibration require adjustment."
            if relative_positive and not absolute_positive
            else "Scanner Top-pick ordering does not establish a material ranking effect after "
            "applying the fixed +0.30% delta and 55% positive-window thresholds."
            if not relative_positive
            else "Scanner ranking and absolute cost-adjusted edge are both positive."
        ),
        "missing_comparison": None if enough else "paired Top-pick and runner-up forward outcomes",
        "materiality_contract": {
            "minimum_average_delta_pct": facade.MIN_MATERIAL_RANKING_DELTA_PCT,
            "minimum_positive_delta_rate": facade.MIN_POSITIVE_RANKING_DELTA_RATE,
        },
    }


def _unavailable_component_impl(
    *,
    question: str,
    missing_comparison: str,
    availability: dict[str, Any],
    facade: Any,
) -> dict[str, Any]:
    return {
        "decision": facade.DecisionClass.INSUFFICIENT_EVIDENCE.value,
        "question": question,
        "finding": "Historical value-add cannot be measured without the named control comparison.",
        "missing_comparison": missing_comparison,
        "availability": availability,
        "behavior_change_authorized": False,
    }
