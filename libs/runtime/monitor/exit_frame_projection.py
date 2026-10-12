"""Monitor exit selected-symbol/frame/policy/carry projections computed once per cycle.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def exit_frame_exit_bias_result_exit_info(state, policy, selected, *, facade):
    use_exit_policy = facade._resolve_use_exit_policy(state, policy)
    exit_policy_base = facade._resolve_exit_policy_config(state, policy)
    exit_info: facade.Dict[str, facade.Any] = {
        "enabled": bool(use_exit_policy),
        "evaluated": False,
        "triggered": False,
        "reason": "",
        "symbol": None,
        "qty": 0,
        "pnl_ratio": None,
        "price": None,
        "avg_price": None,
        "position_age_seconds": None,
        "exit_signal_detected": False,
        "exit_confirm_count": 0,
        "min_hold_blocked": False,
        "sell_cooldown_blocked": False,
        "sell_cooldown_until": None,
        "pending_exit_lock_active": False,
        "pending_exit_lock_until": None,
        "monitor_reason": "hold",
        "emergency_exit": False,
    }
    hold_bias_result: facade.Dict[str, facade.Any] = {"applied": False, "deltas": []}
    exit_bias_result: facade.Dict[str, facade.Any] = {"applied": False, "deltas": []}
    selected_snapshot = dict(selected) if isinstance(selected, dict) else {}
    selected_symbol = facade._norm_symbol(selected_snapshot.get("symbol"))
    return (exit_bias_result, exit_info, exit_policy_base, hold_bias_result, selected_snapshot, selected_symbol, use_exit_policy)


def exit_frame_confirm_ticks_effective_exit_policy_base(hold_bias_result, monitor_memory_bias_observation_only, min_hold_sec, sell_cooldown_sec, confirm_ticks, exit_policy_base, *, facade):
    if True:
        hold_bias_observed_result = dict(hold_bias_result)
        if monitor_memory_bias_observation_only:
            hold_bias_result = {
                "controls": {
                    "min_hold_sec": int(min_hold_sec),
                    "sell_cooldown_sec": int(sell_cooldown_sec),
                    "confirm_ticks": int(confirm_ticks),
                },
                "applied": False,
                "deltas": [],
                "observation_only": True,
                "observed_deltas": list(hold_bias_observed_result.get("deltas") or []),
            }
        hold_controls = dict(hold_bias_result.get("controls") or {})
        min_hold_sec = int(hold_controls.get("min_hold_sec") or min_hold_sec)
        sell_cooldown_sec = int(hold_controls.get("sell_cooldown_sec") or sell_cooldown_sec)
        confirm_ticks = int(hold_controls.get("confirm_ticks") or confirm_ticks)
        exit_policy_harmonized = facade._harmonize_exit_policy_with_monitor_guards(
            exit_policy_base=exit_policy_base,
            min_hold_sec=min_hold_sec,
        )
        effective_exit_policy_base = dict(exit_policy_harmonized.get("policy") or {})
        effective_exit_policy_base["policy_source"] = str(
            effective_exit_policy_base.get("policy_source")
            or effective_exit_policy_base.get("effective_policy_source")
            or "monitor_effective_exit_policy"
        )
        effective_exit_policy_base["effective_policy_source"] = str(
            effective_exit_policy_base.get("effective_policy_source")
            or effective_exit_policy_base.get("policy_source")
            or "monitor_effective_exit_policy"
        )
        exit_policy_guard_adjustments = list(exit_policy_harmonized.get("adjustments") or [])
    return (confirm_ticks, effective_exit_policy_base, exit_policy_guard_adjustments, hold_bias_observed_result, hold_bias_result, min_hold_sec, sell_cooldown_sec)


def exit_frame_avg_price_decision(selected_symbol, pos_map, state, selected_snapshot, policy, effective_exit_policy_base, preliminary_exit_symbol, exit_policy_guard_adjustments, intents, frame_applied, *, facade):
    if True:
        symbol = facade._select_exit_symbol(
            selected_symbol,
            pos_map,
            state=state,
            selected=selected_snapshot,
            policy=policy,
            exit_policy_base=effective_exit_policy_base,
        )
        if preliminary_exit_symbol and symbol != preliminary_exit_symbol:
            exit_policy_guard_adjustments.append(
                f"exit_symbol_reselected_after_policy:{preliminary_exit_symbol}->{symbol}"
            )
        selected_for_exit: facade.Dict[str, facade.Any] = dict(selected_snapshot)
        if symbol and symbol != selected_symbol:
            selected_for_exit = {"symbol": symbol}
        features = selected_for_exit.get("features") if isinstance(selected_for_exit.get("features"), dict) else {}
        pending_order_symbols_for_exit = facade._pending_order_symbols_from_account_orders(state)
        selected_pending_order_for_exit = bool(
            symbol
            and (
                facade._norm_symbol(symbol) in pending_order_symbols_for_exit
                or facade._features_pending_order_count(features) > 0
            )
        )
        pos = pos_map.get(symbol, {})
        qty = max(0, facade._to_int(pos.get("qty")))
        entry_intent_symbol = facade._norm_symbol((intents[0] or {}).get("symbol")) if intents else ""
        # Suppress fresh BUY only when it targets the same symbol as an existing position.
        if qty > 0 and entry_intent_symbol and entry_intent_symbol == facade._norm_symbol(symbol):
            intents = []
        decision = facade._preview_exit_decision_for_symbol(
            state=state,
            symbol=symbol,
            position=pos,
            selected=selected_for_exit,
            exit_policy_base=effective_exit_policy_base,
        )
        avg_price = facade._to_float(decision.get("_avg_price"))
        price = decision.get("_price")
        hold_sec = facade._to_int(decision.get("_hold_sec"))
        if hold_sec <= 0:
            hold_sec = facade._position_hold_seconds(state, symbol, pos)
        eod_carry = facade._evaluate_overnight_carry_decision(
            state=state,
            symbol=symbol,
            position=pos,
            selected=selected_for_exit,
            exit_policy_base=effective_exit_policy_base,
            primary_decision=decision,
            frame=frame_applied,
            hold_sec=hold_sec,
        )
    return (avg_price, decision, eod_carry, features, hold_sec, intents, price, qty, selected_pending_order_for_exit, symbol)
