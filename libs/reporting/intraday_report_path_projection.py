"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _brief_cache_dir(root: Path, *, facade: Any) -> Path:
    return facade.Path(
        facade.os.getenv("OPERATOR_UI_CACHE_PATH", str(root / "data" / "operator_ui" / "brief_cache"))
    )


def _script_path(root: Path) -> Path:
    return root / "scripts" / "run_live_execution_bundle_report.py"
