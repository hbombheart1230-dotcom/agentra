"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _monitor(report: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    monitor = facade._mapping(report.get("monitor_snapshot"))
    if not monitor:
        monitor = facade._mapping(report.get("monitor_output"))
    return monitor
