"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _scanner_chart_fit_from_row(row: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    explicit = facade._mapping(row.get("scanner_chart_fit"))
    if explicit:
        return explicit
    if row.get("scanner_chart_fit_score") in (None, "") and not facade._mapping(row.get("scanner_chart_fit_components")):
        return {}
    return {
        "score": row.get("scanner_chart_fit_score"),
        "authority": str(row.get("scanner_chart_fit_authority") or ""),
        "components": facade._mapping(row.get("scanner_chart_fit_components")),
        "penalty": row.get("scanner_chart_fit_penalty"),
    }
