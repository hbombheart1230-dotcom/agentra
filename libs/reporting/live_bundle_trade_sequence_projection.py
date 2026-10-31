"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations



def _trade_id_sequence(trade_id: str) -> int:
    text = str(trade_id or "").strip()
    if not text:
        return 10**9
    tail = text.rsplit("_", 1)[-1]
    try:
        return int(tail)
    except Exception:
        return 10**9
