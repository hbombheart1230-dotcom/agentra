"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _reason_text(values: Any, *, facade: Any) -> str:
    rows = facade._items(values)
    return ", ".join(rows[:5]) if rows else "-"
