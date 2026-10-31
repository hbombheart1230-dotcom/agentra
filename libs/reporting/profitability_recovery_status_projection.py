"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def _is_closed_trade_report_generation_regression(
    *, closed_trade: bool, ai_trade_report_llm_exists: bool, ai_status: str
) -> bool:
    if not closed_trade:
        return False
    if not ai_trade_report_llm_exists:
        return True
    normalized = str(ai_status or "").strip().lower()
    if not normalized:
        return False
    return normalized in {"failed", "error", "skipped"}



def _resolve_ai_trade_report_status(
    lifecycle_bundle: Dict[str, Any],
    ai_component: Dict[str, Any],
    ai_trade_report_llm_exists: bool,
) -> str:
    diagnostics = lifecycle_bundle.get("ai_report_diagnostics")
    diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
    for candidate in (
        ai_component.get("status"),
        diagnostics.get("ai_trade_report_status"),
        lifecycle_bundle.get("ai_trade_report_status"),
    ):
        value = str(candidate or "").strip().lower()
        if value:
            return value
    if ai_trade_report_llm_exists:
        return "ok"
    return ""
