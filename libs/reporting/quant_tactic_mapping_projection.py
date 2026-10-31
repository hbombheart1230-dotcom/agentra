"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def _mapping(value: Any, *, facade: Any) -> Dict[str, Any]:
    return dict(value or {}) if isinstance(value, facade.Mapping) else {}
