"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _forward_outcome(row: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    outcome = row.get("shadow_forward_outcome")
    return dict(outcome) if isinstance(outcome, facade.Mapping) else {}
