"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _largecap_surge_would_enter(row: Mapping[str, Any], *, facade: Any) -> bool:
    if row.get("opening_largecap_surge_would_enter") not in (None, ""):
        return facade._bool(row.get("opening_largecap_surge_would_enter"))
    return facade._bool(facade._largecap_surge_probe(row).get("would_probe"))
