"""Lifecycle exit/holding monitor-context projection and open-lifecycle monitor-reason backfill.

Third Pass T2 (P1.5) intra-function extraction from `libs/reporting/live_execution_bundle_runner.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


class LifecycleExitMonitorContext(NamedTuple):
    """Result of `lifecycle_exit_monitor_context` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    exit_execution_context: Any
    exit_guard_context: Any
    exit_monitor_context: Any
    latest_holding_event: Any
    latest_holding_monitor_context: Any
    lifecycle_monitor_reason_human: Any
    merged_exit_monitor_context: Any
    story_contract: Any


def lifecycle_exit_monitor_context(holding, exit_ctx, status, exit_action, anchor_bundle, symbol, runtime_state, story_type, execution_mode_label_text, trade_id, lifecycle, anchor_execution, *, facade):
    latest_holding_event = (
        list(holding.get("holding_events") or [])[-1]
        if isinstance(holding.get("holding_events"), list) and list(holding.get("holding_events") or [])
        else {}
    )
    latest_holding_monitor_context = (
        dict(latest_holding_event.get("monitor_context") or {})
        if isinstance(latest_holding_event, dict) and isinstance(latest_holding_event.get("monitor_context"), dict)
        else {}
    )
    exit_monitor_context = dict(exit_ctx.get("monitor_context") or {}) if isinstance(exit_ctx.get("monitor_context"), dict) else {}
    exit_guard_context = dict(exit_ctx.get("guard_context") or {}) if isinstance(exit_ctx.get("guard_context"), dict) else {}
    exit_execution_context = dict(exit_ctx.get("execution_context") or {}) if isinstance(exit_ctx.get("execution_context"), dict) else {}
    merged_exit_monitor_context = dict(latest_holding_monitor_context)
    if exit_monitor_context:
        merged_exit_monitor_context.update(exit_monitor_context)
    if status == "closed" and merged_exit_monitor_context:
        lifecycle_monitor_reason_human = facade.build_monitor_reason_human(
            merged_exit_monitor_context,
            {"action": exit_action or "SELL"},
        )
    elif latest_holding_monitor_context:
        lifecycle_monitor_reason_human = facade.build_monitor_reason_human(
            latest_holding_monitor_context,
            {"action": "HOLD"},
        )
    else:
        lifecycle_monitor_reason_human = dict(
            anchor_bundle.get("monitor_reason_human")
            or exit_ctx.get("monitor_context")
            or {}
        )
    lifecycle_monitor_reason_human = facade._backfill_open_lifecycle_monitor_reason(
        lifecycle_monitor_reason_human,
        lifecycle_status=status,
        symbol=symbol,
        state_obj=runtime_state,
    )
    story_contract = {
        "story_available": True,
        "story_type": story_type,
        "execution_mode_label": execution_mode_label_text,
        "story_anchor": f"{anchor_execution.get('action') or 'WAIT'} {symbol or '-'} x{facade.safe_int(anchor_execution.get('qty'), 0)} | trade {trade_id}",
        "warnings": list(lifecycle.get("warnings") or []),
    }
    return LifecycleExitMonitorContext(exit_execution_context, exit_guard_context, exit_monitor_context, latest_holding_event, latest_holding_monitor_context, lifecycle_monitor_reason_human, merged_exit_monitor_context, story_contract)
