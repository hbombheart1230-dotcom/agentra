"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _fmt(value: Any) -> str:
    if value in (None, ""):
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)
