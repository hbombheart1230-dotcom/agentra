"""q8_shadow_blocker_review projections (moved verbatim from q8_shadow_blocker_review).

Module globals and helpers are resolved on ``facade`` (the q8_shadow_blocker_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping


def _checkpoint_values(outcome: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    checkpoints = outcome.get("checkpoints") if isinstance(outcome.get("checkpoints"), facade.Mapping) else {}
    observed: List[Mapping[str, Any]] = [
        checkpoint
        for checkpoint in checkpoints.values()
        if isinstance(checkpoint, facade.Mapping) and str(checkpoint.get("status") or "") == "observed"
    ]
    if not observed:
        return {"available": False}
    returns = [facade._to_float(row.get("return_pct")) for row in observed]
    mfes = [facade._to_float(row.get("mfe_pct")) for row in observed]
    maes = [facade._to_float(row.get("mae_pct")) for row in observed]
    returns = [value for value in returns if value is not None]
    mfes = [value for value in mfes if value is not None]
    maes = [value for value in maes if value is not None]
    latest = returns[-1] if returns else None
    return {
        "available": True,
        "latest_return_pct": latest,
        "max_favorable_pct": max(mfes) if mfes else None,
        "max_adverse_pct": min(maes) if maes else None,
    }
