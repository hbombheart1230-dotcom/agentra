"""Monitor entry-guard evidence facts (Commander rail, risk-off, re-entry, rank-1 authority input).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_guard_base_entry_guard_blocked_base_entry_guar(quant_entry_decision, entry_info, tactic_id_for_quant_entry, market_regime_for_entry, market_regime_rail_for_entry, commander_context, symbol, entry_cooldown_map, now_epoch_for_entry, all_pos_map, open_position_count, max_positions, state, entry_quality_gate, entry_cost_filter, selected_already_held, selected_pending_buy, buy_blocked_post_exit_cooldown, closeout_window_guard, plan, *, facade):
    quant_entry_enforcement = facade.build_entry_quant_enforcement(quant_entry_decision)
    entry_info["entry_quant_decision"] = dict(quant_entry_decision)
    entry_info["quant_entry_enforcement"] = dict(quant_entry_enforcement)
    risk_off_defensive_policy = facade.evaluate_risk_off_defensive_observe_policy(
        tactic_id=tactic_id_for_quant_entry,
        market_regime=market_regime_for_entry,
        market_regime_rail=market_regime_rail_for_entry,
        entry_info=entry_info,
        commander_context=commander_context,
    )
    entry_info["risk_off_defensive_observe_policy"] = dict(risk_off_defensive_policy)
    entry_intent_cooldown_sec = max(0, facade._to_int((entry_info.get("thresholds") or {}).get("intent_cooldown_sec")))
    cooldown_until = max(0, facade._to_int(entry_cooldown_map.get(symbol)))
    if cooldown_until > 0 and cooldown_until <= now_epoch_for_entry:
        entry_cooldown_map.pop(symbol, None)
        cooldown_until = 0
    if max(0, facade._to_int((all_pos_map.get(symbol) or {}).get("qty"))) > 0:
        entry_cooldown_map.pop(symbol, None)
        cooldown_until = 0
    entry_info["intent_cooldown_sec"] = int(entry_intent_cooldown_sec)
    entry_info["intent_cooldown_until"] = int(cooldown_until) if cooldown_until > 0 else None

    max_positions_reached = bool(open_position_count >= max_positions)
    same_symbol_loss_reentry_control = facade.evaluate_same_symbol_loss_reentry(
        state,
        symbol=symbol,
        now_epoch=int(now_epoch_for_entry),
    )
    entry_info["same_symbol_loss_reentry_control"] = dict(
        same_symbol_loss_reentry_control
    )
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
    entry_info["legacy_fallback_used"] = False
    entry_info["decision"] = "WAIT"
    entry_info["cascade_candidate"] = str(plan.get("cascade_candidate") or "")
    return (base_entry_guard_blocked, base_entry_guard_reason, buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_same_symbol, entry_guard_blocked, entry_guard_reason, entry_info, entry_intent_cooldown_sec, max_positions_reached, original_wait_reason, quant_entry_enforcement, risk_off_defensive_policy)
