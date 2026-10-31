"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _scorecard_return_signal(row: Mapping[str, Any]) -> float | None:
    for key in ("avg_return_15m_pct", "avg_return_5m_pct", "avg_return_30m_pct", "avg_return_3m_pct"):
        value = row.get(key)
        if value not in (None, ""):
            try:
                return float(value)
            except Exception:
                continue
    return None
