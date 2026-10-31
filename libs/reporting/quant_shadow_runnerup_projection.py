"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def _runner_up_risk_count(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> int:
    total = 0
    for row in candidates:
        if facade._text(row.get("shadow_role")) != "runner_up_evaluated":
            continue
        if facade._bool(row.get("would_enter")):
            total += 1
            continue
        if facade._bool(row.get("runner_up_quality_blocked")) or facade._bool(row.get("weak_fallback_blocked")):
            total += 1
            continue
        reason = facade._text(row.get("reason"))
        if reason in {"runner_up_quality_gate_failed", "weak_fallback_pullback"}:
            total += 1
    return total
