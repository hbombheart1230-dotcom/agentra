"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _stale_process_after_sec(*, facade: Any) -> float:
    try:
        return max(30.0, float(facade.os.getenv("INTRADAY_TRADE_REPORT_STALE_PROCESS_SEC", "180") or 180.0))
    except Exception:
        return 180.0
