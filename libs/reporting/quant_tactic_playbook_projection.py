"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _playbook(report: Mapping[str, Any], *, fallback: str = "", facade: Any) -> str:
    for item in (
        facade._mapping(report.get("strategist_summary")),
        facade._mapping(report.get("market_context_at_entry")),
        facade._mapping(report.get("market_context")),
    ):
        value = str(item.get("playbook") or item.get("selected_playbook") or "").strip()
        if value:
            return value
    return str(fallback or "").strip()
