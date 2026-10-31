"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Sequence


def _float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        text = str(value).strip().replace("%", "").replace(",", "")
        if not text:
            return None
        return float(text)
    except Exception:
        return None


def _int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(float(str(value).replace(",", "")))
    except Exception:
        return 0


def _pct_from_ratio(value: Any, *, facade: Any) -> float | None:
    parsed = facade._float(value)
    if parsed is None:
        return None
    return parsed * 100.0 if abs(parsed) <= 1.0 else parsed


def _avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text


def _weighted_avg(total: float, weight: int) -> float:
    return round(total / weight, 4) if weight > 0 else 0.0
