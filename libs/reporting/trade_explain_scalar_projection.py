"""Trade explain scalar projections (moved verbatim from trade_explain).

``_to_epoch``, ``datetime`` and ``timezone`` are resolved on ``facade`` (the trade_explain module) at call time for ``_utc_day``; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Optional


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _utc_day(ts: Any, *, facade: Any) -> Optional[str]:
    epoch = facade._to_epoch(ts)
    if epoch is None:
        return None
    return facade.datetime.fromtimestamp(epoch, tz=facade.timezone.utc).strftime("%Y-%m-%d")
