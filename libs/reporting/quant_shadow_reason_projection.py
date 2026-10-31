"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def _count_reason(candidates: Sequence[Mapping[str, Any]], names: set[str], *, facade: Any) -> int:
    total = 0
    for row in candidates:
        reason = facade._text(row.get("reason"))
        primary = facade._text(row.get("primary_failure_axis"))
        cost_floor = facade._cost_floor_state(row)
        if reason in names or primary in names or cost_floor in names:
            total += 1
            continue
        blockers = facade._row_blockers(row)
        if any(blocker in names for blocker in blockers):
            total += 1
    return total
