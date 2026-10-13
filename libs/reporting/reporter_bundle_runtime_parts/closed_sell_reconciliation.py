"""Closed-sell lifecycle reconciliation: execution details, holding-phase observability and summary refresh.

Third Pass T2/T3 (P1.5): pure projection extracted verbatim from `libs/reporting/live_execution_bundle_runner.py::main`.
Inputs are explicit parameters; module dependencies resolve at call time through the injected runner module
(`facade`, TEMPORARY_COMPATIBILITY, keeps monkeypatch seams). No file, clock, env, lock or LLM access; the result is a
named record whose field order equals the legacy positional tuple.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class ClosedSellExecutionDetails(NamedTuple):
    """Result of `closed_sell_execution_details` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    entry_execution_details: Any
    execution_details: Any
    exit_execution_details: Any
    holding_phase_observability: Any
    lifecycle: Any
    lifecycle_bundle: Any
    status: Any
    summary_obj: Any


def closed_sell_execution_details(lifecycle, live_trade_context, lifecycle_bundle, summary_obj, *, facade):
    lifecycle = dict(live_trade_context.get("lifecycle") or lifecycle)
    lifecycle_bundle = dict(live_trade_context.get("lifecycle_bundle") or lifecycle_bundle)
    summary_obj = dict(live_trade_context.get("summary_obj") or summary_obj)
    entry_execution_details = dict(live_trade_context.get("entry_execution_details") or {})
    exit_execution_details = dict(live_trade_context.get("exit_execution_details") or {})
    execution_details = dict(live_trade_context.get("execution_details") or {})
    status = facade._reconcile_partial_full_sell_lifecycle(
        lifecycle=lifecycle,
        lifecycle_bundle=lifecycle_bundle,
        execution_details=execution_details,
    )
    summary_obj = facade._refresh_closed_sell_lifecycle_summary(
        lifecycle=lifecycle,
        lifecycle_bundle=lifecycle_bundle,
        summary_obj=summary_obj,
        execution_details=execution_details,
        status=status,
    )
    holding_phase_observability = dict(live_trade_context.get("holding_phase_observability") or {})
    return ClosedSellExecutionDetails(entry_execution_details, execution_details, exit_execution_details, holding_phase_observability, lifecycle, lifecycle_bundle, status, summary_obj)
