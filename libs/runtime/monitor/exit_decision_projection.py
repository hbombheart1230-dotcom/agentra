"""Monitor exit decision evidence: same-symbol suppression, pending orders, hold/stop/confirm and SELL construction inputs.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def exit_decision_confirm_count_confirm_map(state, symbol, qty, sell_cooldown_sec, now_epoch, decision, confirm_ticks, selected_pending_order_for_exit, eod_carry, entry_info, min_hold_sec, hold_sec, *, facade):
    if True:
        confirm_map = state.get("_monitor_exit_confirm")
        if not isinstance(confirm_map, dict):
            confirm_map = {}
        cooldown_map = state.get("_monitor_sell_cooldown_until")
        if not isinstance(cooldown_map, dict):
            cooldown_map = {}
        pending_exit_lock = state.get("_monitor_pending_exit_lock")
        if not isinstance(pending_exit_lock, dict):
            pending_exit_lock = {}
        prev_qty_map = state.get("_monitor_prev_position_qty")
        if not isinstance(prev_qty_map, dict):
            prev_qty_map = {}

        prev_qty = max(0, facade._to_int(prev_qty_map.get(symbol)))
        if prev_qty > 0 and qty <= 0 and sell_cooldown_sec > 0:
            cooldown_map[symbol] = int(now_epoch + sell_cooldown_sec)
        prev_qty_map[symbol] = int(qty)

        cooldown_until = max(0, facade._to_int(cooldown_map.get(symbol)))
        if cooldown_until > 0 and cooldown_until <= now_epoch:
            cooldown_map.pop(symbol, None)
            cooldown_until = 0

        lock_until = max(0, facade._to_int(pending_exit_lock.get(symbol)))
        if lock_until > 0 and lock_until <= now_epoch:
            pending_exit_lock.pop(symbol, None)
            lock_until = 0

        confirm_key = f"{symbol}:{str(decision.get('reason') or '').strip()}"
        confirm_count = 0
        sell_guard_blocked = False
        sell_guard_reason = ""
        hold_block_reason = str(decision.get("hold_block_reason") or "")
        monitor_reason = "hold"
        min_hold_blocked = False
        sell_cooldown_blocked = False
        exit_signal_detected = bool(decision.get("triggered"))
        emergency_exit = facade._is_emergency_exit_reason(str(decision.get("reason") or ""))
        hard_exit = facade._is_hard_exit_reason(str(decision.get("reason") or ""))
        decision_reason = str(decision.get("reason") or "").strip()
        eod_flat_exit = decision_reason == "eod_flat"
        decision_thresholds = (
            decision.get("thresholds")
            if isinstance(decision.get("thresholds"), dict)
            else {}
        )
        effective_confirm_ticks = max(1, int(confirm_ticks))
        peak_drawdown_confirm_ticks = 0
        if decision_reason == "peak_drawdown":
            peak_drawdown_confirm_ticks = max(
                1,
                facade._to_int(decision_thresholds.get("confirm_required_for_peak_drawdown") or 2),
            )
            if bool(decision.get("peak_drawdown_profit_protection_urgent")):
                peak_drawdown_confirm_ticks = 1
                effective_confirm_ticks = 1
            else:
                effective_confirm_ticks = max(effective_confirm_ticks, peak_drawdown_confirm_ticks)

        if exit_signal_detected:
            if qty <= 0:
                sell_guard_blocked = True
                sell_guard_reason = "sell_guard_no_position"
                monitor_reason = "no_position"
            elif facade._is_trueish(state.get("execution_pending")):
                sell_guard_blocked = True
                sell_guard_reason = "sell_guard_execution_pending"
                monitor_reason = "pending_exit_lock"
            elif selected_pending_order_for_exit:
                sell_guard_blocked = True
                sell_guard_reason = "sell_guard_open_order_pending"
                monitor_reason = "pending_exit_lock"
            elif lock_until > now_epoch and not eod_flat_exit:
                sell_guard_blocked = True
                sell_guard_reason = "sell_guard_pending_exit_lock"
                monitor_reason = "pending_exit_lock"
                hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
            elif not emergency_exit and not hard_exit and min_hold_sec > 0 and hold_sec > 0 and hold_sec < min_hold_sec:
                sell_guard_blocked = True
                min_hold_blocked = True
                sell_guard_reason = f"sell_guard_min_hold:{hold_sec}s<{min_hold_sec}s"
                monitor_reason = "min_hold_active"
                hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
            elif not emergency_exit and not hard_exit and sell_cooldown_sec > 0 and cooldown_until > now_epoch:
                sell_guard_blocked = True
                sell_cooldown_blocked = True
                sell_guard_reason = f"sell_guard_cooldown:{max(0, cooldown_until - now_epoch)}s_remaining"
                monitor_reason = "cooldown_active"
                hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
            elif not emergency_exit and not hard_exit and effective_confirm_ticks > 1:
                confirm_count = facade._to_int(confirm_map.get(confirm_key)) + 1
                confirm_map[confirm_key] = int(confirm_count)
                if confirm_count < int(effective_confirm_ticks):
                    sell_guard_blocked = True
                    sell_guard_reason = f"exit_confirmation_pending:{confirm_count}/{effective_confirm_ticks}"
                    monitor_reason = "exit_signal_pending_confirmation"
                    hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
            if not sell_guard_blocked and not monitor_reason:
                monitor_reason = "confirmed_exit_signal"
        else:
            facade._clear_symbol_confirm_keys(confirm_map, symbol)
            if bool(eod_carry.get("approved")) and qty > 0:
                monitor_reason = "eod_carry_approved"
            elif qty <= 0 and bool(entry_info.get("guard_blocked")):
                monitor_reason = str(entry_info.get("guard_reason") or "entry_guard_blocked")
            elif qty <= 0 and str(entry_info.get("reason") or "").strip():
                monitor_reason = str(entry_info.get("reason") or "entry_wait")
            elif qty <= 0 and bool(entry_info.get("triggered")) and bool(entry_info.get("intent_submitted")):
                monitor_reason = str(entry_info.get("reason") or "entry_signal_confirmed")
            else:
                monitor_reason = "hold" if qty > 0 else "no_position"
    return (confirm_count, confirm_map, cooldown_map, cooldown_until, decision_thresholds, effective_confirm_ticks, emergency_exit, exit_signal_detected, hard_exit, hold_block_reason, lock_until, min_hold_blocked, monitor_reason, peak_drawdown_confirm_ticks, pending_exit_lock, prev_qty_map, sell_cooldown_blocked, sell_guard_blocked, sell_guard_reason)


def exit_decision_exit_info_exit_vs_strategy_intent(decision, features, entry_info, frame_applied, eod_carry, eod_carry_sweep, effective_exit_policy_base, decision_thresholds, symbol, selected_symbol, qty, price, avg_price, hold_sec, exit_signal_detected, sell_guard_blocked, sell_guard_reason, min_hold_sec, sell_cooldown_sec, effective_confirm_ticks, confirm_count, peak_drawdown_confirm_ticks, min_hold_blocked, sell_cooldown_blocked, hold_block_reason, cooldown_until, lock_until, now_epoch, monitor_reason, emergency_exit, hard_exit, exit_policy_guard_adjustments, monitor_memory_bias_observation_only, hold_bias_result, hold_bias_observed_result, exit_bias_result, exit_bias_observed_result, state, *, facade):
    if True:
        exit_info = facade.build_monitor_exit_payload(
            decision=decision,
            features=features,
            entry_info=entry_info,
            frame_applied=frame_applied,
            eod_carry=eod_carry,
            eod_carry_sweep=eod_carry_sweep,
            effective_exit_policy_base=effective_exit_policy_base,
            decision_thresholds=decision_thresholds,
            context={
                "symbol": symbol,
                "selected_symbol": selected_symbol,
                "qty": qty,
                "price": price,
                "avg_price": avg_price,
                "hold_sec": hold_sec,
                "exit_signal_detected": exit_signal_detected,
                "sell_guard_blocked": sell_guard_blocked,
                "sell_guard_reason": sell_guard_reason,
                "min_hold_sec": min_hold_sec,
                "sell_cooldown_sec": sell_cooldown_sec,
                "effective_confirm_ticks": effective_confirm_ticks,
                "confirm_count": confirm_count,
                "peak_drawdown_confirm_ticks": peak_drawdown_confirm_ticks,
                "min_hold_blocked": min_hold_blocked,
                "sell_cooldown_blocked": sell_cooldown_blocked,
                "hold_block_reason": hold_block_reason,
                "cooldown_until": cooldown_until,
                "lock_until": lock_until,
                "now_epoch": now_epoch,
                "monitor_reason": monitor_reason,
                "emergency_exit": emergency_exit,
                "hard_exit": hard_exit,
                "exit_policy_guard_adjustments": exit_policy_guard_adjustments,
                "monitor_memory_bias_observation_only": monitor_memory_bias_observation_only,
                "hold_bias_result": hold_bias_result,
                "hold_bias_observed_result": hold_bias_observed_result,
                "exit_bias_result": exit_bias_result,
                "exit_bias_observed_result": exit_bias_observed_result,
                "active_exit_axis": facade._friendly_exit_axis(str(decision.get("reason") or monitor_reason or "hold")),
                "watch_axes": facade._monitor_watch_axes(decision.get("thresholds") if isinstance(decision.get("thresholds"), dict) else {}),
            },
        )
        sell_would_submit = bool(exit_signal_detected) and not bool(sell_guard_blocked) and qty > 0
        exit_vs_strategy_intent = facade.build_exit_vs_strategy_intent(
            state=state,
            exit_info=exit_info,
            sell_submitted=sell_would_submit,
        )
        exit_info["exit_vs_strategy_intent"] = dict(exit_vs_strategy_intent)
    return (exit_info, exit_vs_strategy_intent)


def exit_decision_intents(qty, decision, exit_info, symbol, price, avg_price, hold_sec, exit_signal_detected, confirm_count, min_hold_blocked, sell_cooldown_blocked, emergency_exit, exit_policy_guard_adjustments, exit_vs_strategy_intent, monitor_reason, plan, frame_applied, *, facade):
    if True:
            exit_order_qty = max(1, min(int(qty), facade._to_int(decision.get("exit_qty") or qty)))
            exit_info["exit_qty"] = int(exit_order_qty)
            intents = [
                {
                    "symbol": symbol,
                    "side": "SELL",
                    "qty": int(exit_order_qty),
                    "thesis": str(plan.get("thesis") or ""),
                    "meta": {
                        "exit_reason": str(decision.get("reason") or ""),
                        "exit_qty": int(exit_order_qty),
                        "position_qty": int(qty),
                        "partial_exit": bool(decision.get("partial_exit")),
                        "exit_qty_fraction": decision.get("exit_qty_fraction"),
                        "profit_ladder_level_pct": decision.get("profit_ladder_level_pct"),
                        "profit_ladder_level_index": decision.get("profit_ladder_level_index"),
                        "risk_reward_take_profit_rung": decision.get("risk_reward_take_profit_rung"),
                        "pnl_ratio": decision.get("pnl_ratio"),
                        "raw_pnl_ratio": decision.get("raw_pnl_ratio"),
                        "gross_pnl_ratio": decision.get("gross_pnl_ratio"),
                        "technical_pnl_ratio": decision.get("technical_pnl_ratio"),
                        "effective_pnl_ratio": decision.get("effective_pnl_ratio"),
                        "stop_pnl_ratio": decision.get("stop_pnl_ratio"),
                        "stop_pnl_ratio_source": str(decision.get("stop_pnl_ratio_source") or ""),
                        "hard_stop_pnl_ratio": decision.get("hard_stop_pnl_ratio"),
                        "hard_stop_pnl_ratio_source": str(decision.get("hard_stop_pnl_ratio_source") or ""),
                        "cost_drag_pressure": bool(decision.get("cost_drag_pressure")),
                        "cost_drag_pressure_pct": decision.get("cost_drag_pressure_pct"),
                        "cost_drag_pressure_reason": str(decision.get("cost_drag_pressure_reason") or ""),
                        "stop_loss_cost_drag_blocked": bool(decision.get("stop_loss_cost_drag_blocked")),
                        "stop_loss_cost_drag_blocked_reason": str(decision.get("stop_loss_cost_drag_blocked_reason") or ""),
                        "etf_deviation_pct": decision.get("etf_deviation_pct"),
                        "etf_deviation_source": str(decision.get("etf_deviation_source") or ""),
                        "asset_class_detected": str(decision.get("asset_class_detected") or ""),
                        "avg_price": avg_price if avg_price > 0.0 else None,
                        "price": price,
                        "price_freshness": dict(decision.get("price_freshness") or {}),
                        "technical_price": decision.get("technical_price"),
                        "technical_price_source": str(decision.get("technical_price_source") or ""),
                        "effective_price": decision.get("effective_price"),
                        "account_current_price": decision.get("account_current_price"),
                        "account_mark_price": decision.get("account_mark_price"),
                        "account_unrealized_pnl": decision.get("account_unrealized_pnl"),
                        "account_pnl_ratio_source": str(decision.get("account_pnl_ratio_source") or ""),
                        "pnl_crosscheck_applied": bool(decision.get("pnl_crosscheck_applied")),
                        "pnl_crosscheck_reason": str(decision.get("pnl_crosscheck_reason") or ""),
                        "source": "monitor_exit_policy",
                        "reason": str(decision.get("reason") or ""),
                        "signal_source": "monitor_exit_policy",
                        "position_age_sec": hold_sec if hold_sec > 0 else None,
                        "position_age_seconds": hold_sec if hold_sec > 0 else None,
                        "monitor_reason": str(monitor_reason or ""),
                        "exit_signal_detected": bool(exit_signal_detected),
                        "exit_confirm_count": int(confirm_count),
                        "min_hold_blocked": bool(min_hold_blocked),
                        "sell_cooldown_blocked": bool(sell_cooldown_blocked),
                        "emergency_exit": bool(emergency_exit),
                        "playbook": str(frame_applied.get("playbook") or ""),
                        "monitor_guidance": str(frame_applied.get("monitor_guidance") or ""),
                        "risk_tone": str(frame_applied.get("risk_tone") or ""),
                        "trade_aggressiveness": str(frame_applied.get("trade_aggressiveness") or ""),
                        "strategy_horizon": str(frame_applied.get("strategy_horizon") or ""),
                        "source_strategy_horizon": str(frame_applied.get("source_strategy_horizon") or ""),
                        "horizon_behavior_translation": dict(frame_applied.get("horizon_behavior_translation") or {}),
                        "position_strategy_context_applied": bool(frame_applied.get("position_strategy_context_applied")),
                        "position_strategy_context_symbol": str(frame_applied.get("position_strategy_context_symbol") or ""),
                        "position_strategy_context_source": str(frame_applied.get("position_strategy_context_source") or ""),
                        "strategy_frame_adjustments": list(frame_applied.get("adjustments") or []),
                        "exit_policy_guard_adjustments": list(exit_policy_guard_adjustments),
                        "exit_vs_strategy_intent": dict(exit_vs_strategy_intent),
                    },
                }
            ]
    return (intents,)


def exit_decision_commander_memory_application_trace_fallb(monitor_memory_bias, hold_bias_result, exit_bias_result, monitor_memory_bias_summary, entry_info, exit_info, state, *, facade):
    commander_memory_application_trace = facade.build_monitor_commander_memory_application_trace(
        monitor_memory_bias=monitor_memory_bias,
        entry_result={
            "applied": bool(entry_info.get("monitor_memory_bias_applied")),
            "deltas": list(entry_info.get("monitor_memory_bias_deltas") or []),
        },
        hold_result=hold_bias_result,
        exit_result=exit_bias_result,
        monitor_memory_bias_summary=monitor_memory_bias_summary,
        effective_policy_source=str(entry_info.get("effective_policy_source") or ""),
        effective_policy_source_chain=list(entry_info.get("effective_policy_source_chain") or []),
    )
    entry_info["commander_memory_application_trace"] = dict(commander_memory_application_trace)
    entry_info["monitor_memory_application_trace"] = dict(commander_memory_application_trace)
    exit_info["commander_memory_application_trace"] = dict(commander_memory_application_trace)
    exit_info["monitor_memory_application_trace"] = dict(commander_memory_application_trace)

    order_status, order_status_meta = facade.extract_order_status(state)
    order_lifecycle = facade._derive_order_lifecycle(order_status)
    fallback_reasons = list(order_status_meta.get("errors") or [])
    return (commander_memory_application_trace, fallback_reasons, order_lifecycle, order_status, order_status_meta)
