"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _tactic_id(row: Mapping[str, Any], *, facade: Any) -> str:
    direct = facade._text(row.get("quant_tactic_id") or row.get("tactic_id"))
    if direct:
        return direct
    decision = row.get("entry_quant_decision")
    if isinstance(decision, facade.Mapping):
        tactic = facade._text(decision.get("tactic_id"))
        if tactic:
            return tactic
    snapshot = row.get("quant_factor_snapshot")
    if isinstance(snapshot, facade.Mapping):
        return facade._text(snapshot.get("tactic_id"))
    return ""
