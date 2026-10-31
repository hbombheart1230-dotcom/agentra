"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, List, Mapping


def _row_blockers(row: Mapping[str, Any], *, facade: Any) -> List[str]:
    blockers: List[str] = []
    for value in (row.get("blockers"),):
        if isinstance(value, list):
            blockers.extend(facade._text(item) for item in value if facade._text(item))
    decision = row.get("entry_quant_decision")
    if isinstance(decision, facade.Mapping):
        value = decision.get("blockers")
        if isinstance(value, list):
            blockers.extend(facade._text(item) for item in value if facade._text(item))
    return blockers
