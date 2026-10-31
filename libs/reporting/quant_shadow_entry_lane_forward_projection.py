"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _entry_lane_forward_outcomes(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
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
