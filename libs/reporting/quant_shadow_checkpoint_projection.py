"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _checkpoint_value(row: Mapping[str, Any], checkpoint: str, metric: str, *, facade: Any) -> float | None:
    outcome = facade._forward_outcome(row)
    checkpoints = outcome.get("checkpoints")
    if not isinstance(checkpoints, facade.Mapping):
        return None
    payload = checkpoints.get(checkpoint)
    if not isinstance(payload, facade.Mapping) or facade._text(payload.get("status")) != "observed":
        return None
    value = payload.get(metric)
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None
