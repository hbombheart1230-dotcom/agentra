"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Sequence


def _drop_q9_row_keys(payload: Dict[str, Any], drop: Optional[Sequence[str]]) -> Dict[str, Any]:
    """Remove `drop` keys from every q9 decision-candidate row of `payload` (no-op when `drop` is empty)."""
    if drop:
        for row in payload.get("q9_decision_candidates") or []:
            if isinstance(row, dict):
                for key in drop:
                    row.pop(key, None)
    return payload
