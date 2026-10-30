"""Symbol trade report scalar projection (moved verbatim from symbol_trade_report).

Pure arithmetic; no IO.
"""
from __future__ import annotations


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator
