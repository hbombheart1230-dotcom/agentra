"""Monitor entry-guard evidence facts (Commander rail, risk-off, re-entry, rank-1 authority input).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_guard_market_rail_translation_market_regime_fo(state, strategy_frame, commander_context, entry_info, quant_entry_decision, quant_entry_factor_snapshot, *, facade):
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    market_regime_for_entry = (
        strategy_frame.get("market_regime")
        or commander_context.get("market_regime")
        or strategist_output.get("market_regime")
        or state.get("market_regime")
        or ""
    )
    commander_rail_shadow = (
        commander_context.get("market_regime_rail_shadow")
        if isinstance(commander_context.get("market_regime_rail_shadow"), dict)
        else {}
    )
    strategist_rail_shadow = (
        strategist_output.get("market_regime_rail_shadow")
        if isinstance(strategist_output.get("market_regime_rail_shadow"), dict)
        else {}
    )
    market_regime_rail_for_entry = (
        strategy_frame.get("market_regime_rail")
        or commander_context.get("market_regime_rail")
        or commander_rail_shadow.get("market_regime_rail")
        or commander_rail_shadow.get("rail_id")
        or strategist_output.get("market_regime_rail")
        or strategist_rail_shadow.get("market_regime_rail")
        or strategist_rail_shadow.get("rail_id")
        or state.get("market_regime_rail")
        or ""
    )
    market_rail_translation = facade.evaluate_market_rail_translation(
        entry_info=entry_info,
        entry_quant_decision=quant_entry_decision,
        factor_snapshot=quant_entry_factor_snapshot,
        market_regime=market_regime_for_entry,
        market_regime_rail=market_regime_rail_for_entry,
    )
    return (market_rail_translation, market_regime_for_entry, market_regime_rail_for_entry)


def entry_guard_base_entry_guard_blocked_base_entry_guar(state, all_pos_map, now_epoch_for_entry, same_symbol_loss_reentry_control, entry_info, entry_quality_gate, entry_cost_filter, selected_already_held, selected_pending_buy, max_positions_reached, buy_blocked_post_exit_cooldown, entry_intent_cooldown_sec, cooldown_until, closeout_window_guard, *, facade):
    forced_entry_block_reason = facade._entry_forced_block_reason_for_open_carry(
        state,
        all_pos_map,
        now_epoch=int(now_epoch_for_entry),
    )
    if not forced_entry_block_reason and bool(
        same_symbol_loss_reentry_control.get("blocked")
    ):
        forced_entry_block_reason = "same_symbol_loss_reentry_blocked"
    entry_guard = facade.evaluate_entry_guard(
        entry_info=entry_info,
        entry_quality_gate=entry_quality_gate,
        entry_cost_filter=entry_cost_filter,
        selected_already_held=selected_already_held,
        selected_pending_buy=selected_pending_buy,
        max_positions_reached=max_positions_reached,
        closeout_window_active=bool(closeout_window_guard.get("active")),
        buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown,
        entry_intent_cooldown_sec=int(entry_intent_cooldown_sec),
        cooldown_until=int(cooldown_until),
        now_epoch=int(now_epoch_for_entry),
        forced_entry_block_reason=forced_entry_block_reason,
    )
    entry_info = dict(entry_guard.get("entry_info") or entry_info)
    entry_guard_blocked = bool(entry_guard.get("entry_guard_blocked"))
    entry_guard_reason = str(entry_guard.get("entry_guard_reason") or "")
    base_entry_guard_blocked = bool(entry_guard_blocked)
    base_entry_guard_reason = str(entry_guard_reason)
    original_wait_reason = str(entry_info.get("reason") or "")
    buy_blocked_open_position = bool(entry_guard.get("buy_blocked_open_position"))
    buy_blocked_closeout_window = bool(entry_guard.get("buy_blocked_closeout_window"))
    buy_blocked_same_symbol = bool(entry_guard.get("buy_blocked_same_symbol"))
    buy_blocked_pending_buy = bool(entry_guard.get("buy_blocked_pending_buy"))
    return (base_entry_guard_blocked, base_entry_guard_reason, buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_same_symbol, entry_guard_blocked, entry_guard_reason, entry_info, original_wait_reason)
