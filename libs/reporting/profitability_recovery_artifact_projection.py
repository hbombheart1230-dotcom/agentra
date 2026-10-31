"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path


def _artifact_path(trade_dir: Path, *candidates: str) -> Path:
    for raw in candidates:
        candidate = trade_dir / raw
        if candidate.exists():
            return candidate
    return trade_dir / candidates[0]
