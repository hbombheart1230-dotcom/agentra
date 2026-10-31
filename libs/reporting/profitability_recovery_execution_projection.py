"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _resolve_execution_details(lifecycle_bundle: Dict[str, Any], trade_dir: Path, *, facade: Any) -> Dict[str, Any]:
    explicit = lifecycle_bundle.get("execution_details")
    if isinstance(explicit, dict) and explicit:
        return dict(explicit)

    execution = lifecycle_bundle.get("execution")
    execution = execution if isinstance(execution, dict) else {}
    story_contract = lifecycle_bundle.get("story_contract")
    story_contract = story_contract if isinstance(story_contract, dict) else {}
    entry = facade._read_json(trade_dir / "entry.json")
    exit_payload = facade._read_json(trade_dir / "exit.json")

    order_id = (
        execution.get("ord_no")
        or ((entry.get("execution_details") or {}) if isinstance(entry.get("execution_details"), dict) else {}).get("order_id")
        or ((exit_payload.get("execution_details") or {}) if isinstance(exit_payload.get("execution_details"), dict) else {}).get("order_id")
        or None
    )

    if order_id in (None, ""):
        for ctx in (lifecycle_bundle.get("exit_execution_details", {}), lifecycle_bundle.get("entry_execution_details", {})):
            if ctx.get("order_id") not in (None, ""):
                order_id = ctx.get("order_id")
                break

    execution_mode_label = str(story_contract.get("execution_mode_label") or "").strip().lower()
    execution_mode = None
    broker_env = None
    if "simulation" in execution_mode_label or "mock" in execution_mode_label:
        execution_mode = "simulation"
        broker_env = "mock"
    elif execution_mode_label:
        execution_mode = execution_mode_label

    filled_qty = execution.get("qty")
    avg_price = (
        execution.get("avg_price")
        or execution.get("price")
        or entry.get("price")
        or exit_payload.get("price")
        or None
    )
    if avg_price in (None, ""):
        for ctx in (lifecycle_bundle.get("exit_execution_details", {}), lifecycle_bundle.get("entry_execution_details", {})):
            if ctx.get("avg_price") not in (None, ""):
                avg_price = ctx.get("avg_price")
                break
    if avg_price in (None, ""):
        avg_price = (
            facade._safe_float(lifecycle_bundle.get("exit", {}).get("price")) or
            facade._safe_float(lifecycle_bundle.get("entry", {}).get("price")) or
            facade._safe_float(lifecycle_bundle.get("monitor_snapshot", {}).get("average_price"))
        )

    order_status = execution.get("status")
    if order_status in (None, "") and str(execution.get("action") or "").strip():
        order_status = "filled"

    return {
        "order_status": order_status if order_status not in ("", []) else None,
        "order_id": order_id if order_id not in ("", []) else None,
        "execution_mode": execution_mode,
        "broker_env": broker_env,
        "filled_qty": filled_qty if filled_qty not in ("", []) else None,
        "avg_price": avg_price if avg_price not in ("", []) else None,
    }
