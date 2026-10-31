"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _build_trade_id(day: str, symbol: str, seq: int, *, facade: Any) -> str:
    compact_day = str(day or "").replace("-", "")
    clean_symbol = facade.normalize_symbol(symbol or "", allow_test_symbols=True) or "UNKNOWN"
    return f"TRD_{compact_day}_{clean_symbol}_{int(seq):02d}"
