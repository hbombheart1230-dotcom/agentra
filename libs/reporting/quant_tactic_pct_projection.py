"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _pct(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        num = float(value)
    except Exception:
        return str(value)
    return f"{num * 100.0:.2f}%"
