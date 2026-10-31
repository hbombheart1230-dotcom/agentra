"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Mapping, Sequence


def _entry_lane_observation_payload(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    lane_counter: Counter[str] = facade.Counter()
    subtype_counter: Counter[str] = facade.Counter()
    subtype_v2_counter: Counter[str] = facade.Counter()
    lane_subtype_counter: Counter[str] = facade.Counter()
    lane_subtype_v2_counter: Counter[str] = facade.Counter()
    time_bucket_counter: Counter[str] = facade.Counter()
    market_regime_counter: Counter[str] = facade.Counter()
    market_rail_counter: Counter[str] = facade.Counter()
    total = 0
    for row in candidates:
        observation = facade._entry_lane_observation(row)
        lane = facade._text(observation.get("primary_lane")) or "unknown"
        subtype = facade._text(observation.get("subtype")) or "unknown"
        subtype_v2 = facade._text(observation.get("subtype_v2")) or subtype
        time_bucket = facade._text(observation.get("time_bucket")) or "unknown"
        market_regime = facade._text(observation.get("market_regime")) or "unknown"
        market_rail = facade._text(observation.get("market_regime_rail")) or "unknown"
        total += 1
        lane_counter[lane] += 1
        subtype_counter[subtype] += 1
        subtype_v2_counter[subtype_v2] += 1
        lane_subtype_counter[f"{lane}:{subtype}"] += 1
        lane_subtype_v2_counter[f"{lane}:{subtype_v2}"] += 1
        time_bucket_counter[time_bucket] += 1
        market_regime_counter[market_regime] += 1
        market_rail_counter[market_rail] += 1
    return {
        "behavior_effect": "observation_only",
        "candidate_count": int(total),
        "by_primary_lane": facade._top_counter(lane_counter, limit=10),
        "by_subtype": facade._top_counter(subtype_counter, limit=10),
        "by_subtype_v2": facade._top_counter(subtype_v2_counter, limit=10),
        "by_lane_subtype": facade._top_counter(lane_subtype_counter, limit=12),
        "by_lane_subtype_v2": facade._top_counter(lane_subtype_v2_counter, limit=12),
        "by_time_bucket": facade._top_counter(time_bucket_counter, limit=8),
        "by_market_regime": facade._top_counter(market_regime_counter, limit=8),
        "by_market_regime_rail": facade._top_counter(market_rail_counter, limit=8),
    }
