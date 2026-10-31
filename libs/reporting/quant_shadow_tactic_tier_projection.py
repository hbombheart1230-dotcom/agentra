"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _tactic_suitability_tier(row: Mapping[str, Any], *, facade: Any) -> str:
    direct = facade._text(row.get("tactic_suitability_tier"))
    if direct:
        return direct
    decision = row.get("entry_quant_decision")
    if isinstance(decision, facade.Mapping):
        suitability = decision.get("tactic_suitability")
        if isinstance(suitability, facade.Mapping):
            tier = facade._text(suitability.get("tier"))
            if tier:
                return tier
    return ""
