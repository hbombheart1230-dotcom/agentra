"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def iter_trade_diagnostic_rows(reports_root: Path, day: str, *, facade: Any) -> List[Dict[str, Any]]:
    return [facade.read_trade_diagnostic_row(trade_dir) for trade_dir in facade.iter_trade_dirs(reports_root, day)]
