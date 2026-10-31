"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Mapping, Sequence


def _below_vwap_reclaim_observation_payload(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    subtype_counter: Counter[str] = facade.Counter()
    subtype_v2_counter: Counter[str] = facade.Counter()
    total = 0
    for row in candidates:
        observation = facade._below_vwap_reclaim_observation(row)
        if not facade._bool(observation.get("applies")):
            continue
        total += 1
        subtype_counter[facade._text(observation.get("subtype"))] += 1
        subtype_v2_counter[facade._text(observation.get("subtype_v2"))] += 1
    return {
        "behavior_effect": "observation_only",
        "candidate_count": int(total),
        "by_subtype": facade._top_counter(subtype_counter, limit=8),
        "by_subtype_v2": facade._top_counter(subtype_v2_counter, limit=10),
    }
