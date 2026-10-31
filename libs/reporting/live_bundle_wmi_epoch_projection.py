"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _creation_epoch_from_wmi(value: Any, *, facade: Any) -> float:
    raw = str(value or "").strip()
    if not raw:
        return 0.0
    match = facade.re.search(r"/Date\((\d+)", raw)
    if match:
        try:
            return float(match.group(1)) / 1000.0
        except Exception:
            return 0.0
    return 0.0
