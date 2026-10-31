"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _background_job_queue_path(*, facade: Any) -> Path:
    return facade.ROOT / "reports" / "runtime" / "intraday_trade_report_bundle.queue.json"
