"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _below_vwap_reclaim_observation(row: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    payload = row.get("below_vwap_reclaim_observation")
    if isinstance(payload, facade.Mapping):
        return dict(payload)
    return facade.classify_below_vwap_reclaim_observation(row)
