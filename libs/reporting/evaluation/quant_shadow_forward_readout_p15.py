"""Pure Q8 shadow-candidate forward-outcome readout (P1.5 DEV-A).

Per-row checkpoint reads, group summaries and the entry-lane forward grouping behind
``libs.reporting.quant_shadow_candidate_evaluation``. Read-only aggregation of already attached forward outcomes: no
loaders, files, clocks or trust-gate/promotion decisions. ``*_impl`` bodies resolve every helper on the injected
``facade`` at call time, so patching a facade attribute behaves as before the move.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence


def _checkpoint_value_impl(row: Mapping[str, Any], checkpoint: str, metric: str, *, facade: Any) -> float | None:
    outcome = facade._forward_outcome(row)
    checkpoints = outcome.get("checkpoints")
    if not isinstance(checkpoints, Mapping):
        return None
    payload = checkpoints.get(checkpoint)
    if not isinstance(payload, Mapping) or facade._text(payload.get("status")) != "observed":
        return None
    value = payload.get(metric)
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _forward_outcome_summary_impl(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    observed_rows = [row for row in rows if facade._bool(facade._forward_outcome(row).get("available"))]
    observed_days = Counter(facade._candidate_day(row) for row in observed_rows if facade._candidate_day(row))
    largest_day_count = observed_days.most_common(1)[0][1] if observed_days else 0
    horizon_counts: Dict[str, int] = {}
    horizon_day_counts: Dict[str, int] = {}
    for horizon in ("+3m", "+5m", "+15m", "+30m", "+60m", "EOD"):
        horizon_rows = [
            row
            for row in rows
            if facade._checkpoint_value(row, horizon, "return_pct") is not None
        ]
        horizon_counts[horizon] = len(horizon_rows)
        horizon_day_counts[horizon] = len(
            {facade._candidate_day(row) for row in horizon_rows if facade._candidate_day(row)}
        )
    return {
        "measurement_contract_version": "forward_horizon_coverage.v2",
        "candidate_count": len(rows),
        "observed_count": len(observed_rows),
        "observed_day_count": len(observed_days),
        "sample_concentration": (
            round(float(largest_day_count) / float(len(observed_rows)), 4)
            if observed_rows
            else 0.0
        ),
        "observed_days": [name for name, _count in observed_days.most_common(5)],
        "observed_count_by_horizon": horizon_counts,
        "observed_day_count_by_horizon": horizon_day_counts,
        **{
            f"observed_count_{horizon[1:-1]}m" if horizon.startswith("+") else "observed_count_eod": count
            for horizon, count in horizon_counts.items()
        },
        **{
            f"observed_day_count_{horizon[1:-1]}m" if horizon.startswith("+") else "observed_day_count_eod": count
            for horizon, count in horizon_day_counts.items()
        },
        "avg_return_3m_pct": facade._mean([facade._checkpoint_value(row, "+3m", "return_pct") for row in rows]),
        "avg_return_5m_pct": facade._mean([facade._checkpoint_value(row, "+5m", "return_pct") for row in rows]),
        "avg_return_15m_pct": facade._mean([facade._checkpoint_value(row, "+15m", "return_pct") for row in rows]),
        "avg_return_30m_pct": facade._mean([facade._checkpoint_value(row, "+30m", "return_pct") for row in rows]),
        "avg_return_60m_pct": facade._mean([facade._checkpoint_value(row, "+60m", "return_pct") for row in rows]),
        "avg_mfe_5m_pct": facade._mean([facade._checkpoint_value(row, "+5m", "mfe_pct") for row in rows]),
        "avg_mae_5m_pct": facade._mean([facade._checkpoint_value(row, "+5m", "mae_pct") for row in rows]),
        "coverage": (float(len(observed_rows)) / float(len(rows))) if rows else 0.0,
    }


def _top_forward_groups_impl(groups: Mapping[str, List[Mapping[str, Any]]], *, limit: int = 10, facade: Any) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for name, rows in groups.items():
        summary = facade._forward_outcome_summary(rows)
        if int(summary.get("observed_count") or 0) <= 0:
            continue
        summary["name"] = name
        summaries.append(summary)
    summaries.sort(
        key=lambda item: (
            float(item.get("avg_return_5m_pct") or item.get("avg_return_3m_pct") or -999.0),
            int(item.get("observed_count") or 0),
        ),
        reverse=True,
    )
    return summaries[:limit]


def _entry_lane_forward_outcomes_impl(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    by_lane: Dict[str, List[Mapping[str, Any]]] = {}
    by_subtype: Dict[str, List[Mapping[str, Any]]] = {}
    by_subtype_v2: Dict[str, List[Mapping[str, Any]]] = {}
    by_lane_subtype: Dict[str, List[Mapping[str, Any]]] = {}
    by_lane_subtype_v2: Dict[str, List[Mapping[str, Any]]] = {}
    by_time_bucket: Dict[str, List[Mapping[str, Any]]] = {}
    by_market_rail: Dict[str, List[Mapping[str, Any]]] = {}
    for row in candidates:
        observation = facade._entry_lane_observation(row)
        lane = facade._text(observation.get("primary_lane")) or "unknown"
        subtype = facade._text(observation.get("subtype")) or "unknown"
        subtype_v2 = facade._text(observation.get("subtype_v2")) or subtype
        time_bucket = facade._text(observation.get("time_bucket")) or "unknown"
        market_rail = facade._text(observation.get("market_regime_rail")) or "unknown"
        by_lane.setdefault(lane, []).append(row)
        by_subtype.setdefault(subtype, []).append(row)
        by_subtype_v2.setdefault(subtype_v2, []).append(row)
        by_lane_subtype.setdefault(f"{lane}:{subtype}", []).append(row)
        by_lane_subtype_v2.setdefault(f"{lane}:{subtype_v2}", []).append(row)
        by_time_bucket.setdefault(time_bucket, []).append(row)
        by_market_rail.setdefault(market_rail, []).append(row)
    return {
        "behavior_effect": "evaluation_only",
        "by_primary_lane": facade._top_forward_groups(by_lane, limit=10),
        "by_subtype": facade._top_forward_groups(by_subtype, limit=10),
        "by_subtype_v2": facade._top_forward_groups(by_subtype_v2, limit=10),
        "by_lane_subtype": facade._top_forward_groups(by_lane_subtype, limit=12),
        "by_lane_subtype_v2": facade._top_forward_groups(by_lane_subtype_v2, limit=12),
        "by_time_bucket": facade._top_forward_groups(by_time_bucket, limit=8),
        "by_market_regime_rail": facade._top_forward_groups(by_market_rail, limit=8),
    }
