"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _bundle_role(value: Any = "") -> str:
    raw = str(value or "").strip()
    return raw or "intraday_trade_report_bundle"
