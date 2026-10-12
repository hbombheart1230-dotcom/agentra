"""Monitor exit decision evidence: same-symbol suppression, pending orders, hold/stop/confirm and SELL construction inputs.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def exit_decision_confirm_count_confirm_key(symbol, decision, confirm_ticks, *, facade):
    if True:
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
    return (confirm_count, confirm_key, decision_thresholds, effective_confirm_ticks, emergency_exit, eod_flat_exit, exit_signal_detected, hard_exit, hold_block_reason, min_hold_blocked, monitor_reason, peak_drawdown_confirm_ticks, sell_cooldown_blocked, sell_guard_blocked, sell_guard_reason)


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
    return (exit_info, exit_vs_strategy_intent)


def exit_decision_intents(symbol, exit_order_qty, price, qty, avg_price, hold_sec, exit_signal_detected, confirm_count, min_hold_blocked, sell_cooldown_blocked, emergency_exit, exit_policy_guard_adjustments, exit_vs_strategy_intent, decision, monitor_reason, plan, frame_applied, *, facade):
    if True:
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
