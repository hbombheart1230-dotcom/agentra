"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def _execution_action(state: Dict[str, Any]) -> str:
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    order = execution.get("order") if isinstance(execution.get("order"), dict) else {}
    return str(order.get("action") or execution.get("action") or "").strip().upper()


def _execution_ok(state: Dict[str, Any]) -> bool:
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    return bool(execution.get("ok")) and bool(execution.get("allowed", True))
