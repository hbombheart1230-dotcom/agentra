"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _decision_for_reclaim_subtype(row: Mapping[str, Any], *, facade: Any) -> str:
    name = facade._text(row.get("name"))
    observed = facade._int(row.get("observed_count"))
    ret5 = facade._float(row.get("avg_return_5m_pct")) or 0.0
    ret15 = facade._float(row.get("avg_return_15m_pct")) or 0.0
    ret60 = facade._float(row.get("avg_return_60m_pct")) or 0.0
    mae5 = facade._float(row.get("avg_mae_5m_pct")) or 0.0
    if observed < 30:
        return "retain_observation_sample_small"
    if name.endswith("true_below_vwap_failure") and ret5 > 0 and ret15 > 0:
        return "review_classifier_or_label"
    if ret5 > 0 and ret15 > 0 and mae5 > -0.5:
        return "adjust_and_retest_candidate"
    if ret5 < 0 and ret15 < 0:
        return "keep_blocked"
    if ret60 > 0 and ret5 <= 0:
        return "hold_observation_longer_horizon_only"
    return "retain_under_observation"
