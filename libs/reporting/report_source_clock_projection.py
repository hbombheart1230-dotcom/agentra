"""Report source clock projections (moved verbatim from report_source_helpers).

``datetime``, ``timezone`` and ``to_epoch`` are resolved on ``facade`` (the report_source_helpers module) at call time; this module never imports it.
No clock read except through ``facade.datetime``.
"""
from __future__ import annotations

from typing import Any


def to_epoch(ts: Any, *, facade: Any) -> int:
    if ts is None:
        return 0
    if isinstance(ts, (int, float)):
        return int(ts)
    s = str(ts).strip()
    if not s:
        return 0
    try:
        return int(float(s))
    except Exception:
        pass
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = facade.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return 0


def utc_day(ts: Any, *, facade: Any) -> str:
    epoch = facade.to_epoch(ts)
    if epoch <= 0:
        return ""
    return facade.datetime.fromtimestamp(epoch, tz=facade.timezone.utc).strftime("%Y-%m-%d")


def utc_now_iso(*, facade: Any) -> str:
    return facade.datetime.now(facade.timezone.utc).isoformat(timespec="seconds")


def epoch_to_iso(epoch: Any, *, facade: Any) -> str:
    try:
        n = int(float(epoch))
    except Exception:
        return ""
    if n <= 0:
        return ""
    return facade.datetime.fromtimestamp(n, tz=facade.timezone.utc).isoformat(timespec="seconds")
