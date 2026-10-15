"""Monitor entry selection: cascade plan for the selected symbol and runner-up exclusions.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::monitor_node` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class OrderPriceResolution(NamedTuple):
    """Result of `resolve_entry_order_price` (positional order = sorted output names)."""

    order_price: Any
    order_price_source: Any

def build_entry_cascade_plan_for_selection(entry_candidate_cascade, entry_cascade_config, entry_cascade_max_runner_ups, entry_guard_blocked, entry_guard_reason, entry_info, held_symbols_for_entry, max_positions, open_position_count, pending_buy_symbols_for_entry, state, symbol, *, facade):
    cascade_plan = facade.build_entry_candidate_cascade_plan(
        selected_symbol=symbol,
        ranked_candidates=[row for row in list(state.get("ranked_candidates") or []) if isinstance(row, dict)],
        scanner_output=state.get("scanner_output") if isinstance(state.get("scanner_output"), dict) else {},
        open_position_count=open_position_count,
        max_positions=max_positions,
        entry_guard_blocked=entry_guard_blocked,
        entry_guard_reason=entry_guard_reason,
        entry_triggered=bool(entry_info.get("triggered")),
        entry_reason=str(entry_info.get("reason") or ""),
        max_runner_ups=int(entry_cascade_max_runner_ups),
        cascade_enabled=bool(entry_cascade_config.get("cascade_enabled", True)),
        cascade_allowed_reasons=list(entry_cascade_config.get("cascade_allowed_reasons") or []),
        cascade_blocked_reasons=list(entry_cascade_config.get("cascade_blocked_reasons") or []),
        hard_block_override_enabled=bool(entry_cascade_config.get("hard_block_override_enabled")),
        hard_block_override_reason=str(entry_cascade_config.get("hard_block_override_reason") or ""),
        excluded_symbols=sorted(held_symbols_for_entry | pending_buy_symbols_for_entry),
    )
    entry_candidate_cascade.update(dict(cascade_plan))
    return cascade_plan

def resolve_entry_order_price(entry_info, selected, sizing_info, *, facade):
    entry_metrics_for_order = (
        dict(entry_info.get("metrics") or {})
        if isinstance(entry_info.get("metrics"), dict)
        else {}
    )
    entry_cost_filter_for_order = (
        dict(entry_info.get("entry_cost_filter") or {})
        if isinstance(entry_info.get("entry_cost_filter"), dict)
        else {}
    )
    order_price_source = ""
    order_price = 0.0
    for source_name, candidate in (
        ("entry_cost_filter.price", entry_cost_filter_for_order.get("price")),
        ("selected.price", selected.get("price")),
        ("entry.metrics.current_price", entry_metrics_for_order.get("current_price")),
        ("entry.metrics.price", entry_metrics_for_order.get("price")),
        ("sizing.price", sizing_info.get("price")),
    ):
        candidate_price = facade._to_float(candidate)
        if candidate_price > 0.0:
            order_price = float(candidate_price)
            order_price_source = source_name
            break
    return OrderPriceResolution(order_price, order_price_source)

def annotate_entry_intent_meta(entry_info, intent, post_exit_cooldown_sec, sizing_info):
    if bool(sizing_info.get("enabled")):
        intent["meta"]["sizing"] = {
            "reason": str(sizing_info.get("reason") or ""),
            "price": sizing_info.get("price"),
            "cash": sizing_info.get("cash"),
            "inputs": sizing_info.get("inputs"),
        }
    if post_exit_cooldown_sec > 0:
        intent["meta"]["post_exit_cooldown_sec"] = int(post_exit_cooldown_sec)
    if int(entry_info.get("intent_cooldown_sec") or 0) > 0:
        intent["meta"]["entry_intent_cooldown_sec"] = int(entry_info.get("intent_cooldown_sec") or 0)
    return None
