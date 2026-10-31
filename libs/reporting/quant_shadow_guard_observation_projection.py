"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _actionable_entry_guard_block(row: Mapping[str, Any], *, facade: Any) -> bool:
    if not facade._bool(row.get("guard_blocked")):
        return False
    primary = facade._text(row.get("primary_failure_axis"))
    decision = facade._entry_quant_decision(row)
    blockers = facade._row_blockers(row)
    guard_reason = facade._text(row.get("guard_reason"))
    if primary == "confirmed_entry" and decision == "entry_ready" and not blockers and not guard_reason:
        return False
    return True
