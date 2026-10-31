"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _entry_quant_decision(row: Mapping[str, Any], *, facade: Any) -> str:
    decision = row.get("entry_quant_decision")
    if isinstance(decision, facade.Mapping):
        return facade._text(decision.get("decision"))
    return ""
