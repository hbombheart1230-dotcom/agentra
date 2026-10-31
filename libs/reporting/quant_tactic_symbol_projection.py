"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _symbol(report: Mapping[str, Any], *, facade: Any) -> str:
    fact_trade = facade._mapping(facade._mapping(report.get("fact_payload")).get("trade"))
    return str(
        report.get("symbol")
        or fact_trade.get("symbol")
        or facade._mapping(report.get("shared_facts")).get("symbol")
        or ""
    ).strip()
