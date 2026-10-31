"""q8_shadow_blocker_review projections (moved verbatim from q8_shadow_blocker_review).

Module globals and helpers are resolved on ``facade`` (the q8_shadow_blocker_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Sequence


def _text(value: Any) -> str:
    return str(value or "").strip()


def _to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0
