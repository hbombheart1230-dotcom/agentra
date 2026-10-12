"""Monitor entry-candidate context facts (selected/position/pending/cooldown/memory-bias/Commander control).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_context_buy_blocked_post_exit_cooldown_closeout(selected, state, policy, all_pos_map, *, facade):
    symbol = facade._norm_symbol(selected.get("symbol"))
    qty = 1
    max_positions = facade._resolve_max_positions(state, policy)
    held_symbols = {
        facade._norm_symbol(sym)
        for sym, row in all_pos_map.items()
        if facade._norm_symbol(sym) and max(0, facade._to_int((row or {}).get("qty"))) > 0
    }
    pending_buy_symbols = facade._pending_buy_symbols_from_account_orders(state)
    selected_already_held = bool(symbol and symbol in held_symbols)
    selected_features = selected.get("features") if isinstance(selected.get("features"), dict) else {}
    selected_pending_buy = bool(
        symbol
        and (
            symbol in pending_buy_symbols
            or facade._features_pending_order_count(selected_features) > 0
        )
    )
    strategist_output_for_sizing = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    strategy_policy_for_sizing = (
        dict(strategist_output_for_sizing.get("strategy_policy") or {})
        if isinstance(strategist_output_for_sizing.get("strategy_policy"), dict)
        else dict(state.get("strategy_policy") or {})
        if isinstance(state.get("strategy_policy"), dict)
        else {}
    )
    use_position_sizing, position_sizing_policy = facade._resolve_position_sizing_config(
        state,
        policy=policy,
        strategy_policy=strategy_policy_for_sizing,
    )
    sizing_info: facade.Dict[str, facade.Any] = {
        "enabled": bool(use_position_sizing),
        "evaluated": False,
        "qty": 1 if not use_position_sizing else 0,
        "reason": "pending" if use_position_sizing else "disabled",
        "price": None,
        "cash": None,
        "inputs": {},
        "stop_context": {},
    }

    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    last_trade_side = str(persisted.get("last_trade_side") or "").strip().upper()
    last_trade_epoch = facade._to_int(persisted.get("last_trade_epoch"))
    last_trade_symbol = facade._norm_symbol(persisted.get("last_trade_symbol"))
    post_exit_cooldown_symbol_match = bool(not last_trade_symbol or last_trade_symbol == symbol)
    post_exit_cooldown_scope = "same_symbol" if last_trade_symbol else "legacy_global_no_symbol"
    closeout_window_guard = facade._resolve_entry_closeout_window_guard(state, policy)
    buy_blocked_post_exit_cooldown = False
    post_exit_cooldown_remaining_sec = 0
    return (buy_blocked_post_exit_cooldown, closeout_window_guard, held_symbols, last_trade_epoch, last_trade_side, last_trade_symbol, max_positions, pending_buy_symbols, position_sizing_policy, post_exit_cooldown_remaining_sec, post_exit_cooldown_scope, post_exit_cooldown_symbol_match, qty, selected_already_held, selected_features, selected_pending_buy, sizing_info, symbol, use_position_sizing)
