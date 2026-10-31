"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _cost_floor_state(row: Mapping[str, Any], *, facade: Any) -> str:
    direct = facade._text(row.get("entry_quant_cost_floor_state"))
    if direct:
        return direct
    decision = row.get("entry_quant_decision")
    if isinstance(decision, facade.Mapping):
        cost_edge = decision.get("cost_edge")
        if isinstance(cost_edge, facade.Mapping):
            state = facade._text(cost_edge.get("cost_floor_state"))
            if state:
                return state
    snapshot = row.get("quant_factor_snapshot")
    if isinstance(snapshot, facade.Mapping):
        factors = snapshot.get("factors")
        if isinstance(factors, facade.Mapping):
            return facade._text(factors.get("cost_floor_state"))
    return ""
