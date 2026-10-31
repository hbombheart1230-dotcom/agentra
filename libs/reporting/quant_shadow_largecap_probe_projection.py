"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _largecap_surge_probe(row: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    probe = row.get("opening_largecap_surge_shadow")
    return dict(probe) if isinstance(probe, facade.Mapping) else {}
