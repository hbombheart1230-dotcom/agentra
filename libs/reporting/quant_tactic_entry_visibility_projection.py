"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _entry_visibility(report: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    return facade._mapping(report.get("entry_execution_visibility"))
