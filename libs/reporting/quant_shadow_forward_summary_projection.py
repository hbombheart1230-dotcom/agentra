"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


def _forward_outcome_summary(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    observed_rows = [row for row in rows if facade._bool(facade._forward_outcome(row).get("available"))]
    observed_days = facade.Counter(facade._candidate_day(row) for row in observed_rows if facade._candidate_day(row))
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
