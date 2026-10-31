"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def _lock_timestamp_epoch(payload: Dict[str, Any], *, stale_after_sec: float, facade: Any) -> float:
    raw = (
        payload.get("touched_at_epoch")
        or payload.get("heartbeat_epoch")
        or payload.get("started_at_epoch")
    )
    try:
        epoch = float(raw or 0.0)
    except Exception:
        epoch = 0.0
    if epoch > 0:
        return epoch
    started_at = str(payload.get("started_at") or "").strip()
    return facade._to_epoch(started_at) or (facade.time.time() - stale_after_sec - 1.0)
