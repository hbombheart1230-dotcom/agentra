"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def _is_closed_trade(lifecycle_bundle: Dict[str, Any]) -> bool:
    status = str(
        lifecycle_bundle.get("trade_lifecycle_status")
        or lifecycle_bundle.get("status")
        or ""
    ).strip().lower()
    if status == "closed":
        return True
    exit_obj = lifecycle_bundle.get("exit") if isinstance(lifecycle_bundle.get("exit"), dict) else {}
    exit_action = str(exit_obj.get("action") or "").strip().upper()
    return exit_action == "SELL"



def _linkage_surface_present(linkage: Dict[str, Any]) -> bool:
    if not linkage:
        return False
    status = str(linkage.get("status") or "").strip().lower()
    reason = str(linkage.get("linkage_reason") or "").strip()
    return bool(status) and (status != "missing" or bool(reason))
