"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List


def iter_trade_dirs(reports_root: Path, day: str, *, facade: Any) -> List[Path]:
    day_root = facade.Path(reports_root) / "trades" / str(day)
    if not day_root.exists():
        return []
    return sorted(facade._iter_trade_dirs(day_root))
