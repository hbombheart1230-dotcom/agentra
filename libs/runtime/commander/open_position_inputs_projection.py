"""Commander open-position inventory/position/age input projections.

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def open_pos_input_anomaly_found_last_exit_sweep_by_symbol(state, *, facade):
    snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    positions = snapshot.get("positions")
    if isinstance(positions, dict):
        rows = list(positions.values())
    elif isinstance(positions, list):
        rows = positions
    else:
        rows = []

    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    monitor_last_state = (
        persisted.get("monitor_last_state_by_symbol")
        if isinstance(persisted.get("monitor_last_state_by_symbol"), dict)
        else {}
    )
    prior_hold_counts = (
        persisted.get("commander_open_position_hold_repeat_by_symbol")
        if isinstance(persisted.get("commander_open_position_hold_repeat_by_symbol"), dict)
        else {}
    )
    prior_refresh_cooldowns = (
        persisted.get("commander_open_position_refresh_cooldown_until_by_symbol")
        if isinstance(persisted.get("commander_open_position_refresh_cooldown_until_by_symbol"), dict)
        else {}
    )
    overnight_decisions = (
        persisted.get("overnight_decision_by_symbol")
        if isinstance(persisted.get("overnight_decision_by_symbol"), dict)
        else {}
    )
    position_peak_price = (
        persisted.get("position_peak_price")
        if isinstance(persisted.get("position_peak_price"), dict)
        else {}
    )
    position_strategy_context = (
        persisted.get("position_strategy_context")
        if isinstance(persisted.get("position_strategy_context"), dict)
        else {}
    )
    last_exit_sweep_by_symbol = (
        persisted.get("commander_pre_entry_exit_sweep_last_checked_by_symbol")
        if isinstance(persisted.get("commander_pre_entry_exit_sweep_last_checked_by_symbol"), dict)
        else {}
    )
    profit_activation_ratio = facade._resolve_profit_protection_activation_ratio(state)

    next_hold_counts: facade.Dict[str, int] = {}
    next_refresh_cooldowns: facade.Dict[str, int] = {}
    reasons: list[str] = []
    rows_summary: list[facade.Dict[str, facade.Any]] = []
    repeated_hold_rows: list[facade.Dict[str, facade.Any]] = []
    anomaly_found = False
    risk_found = False
    max_hold_repeat = 0
    min_effective_loss_ratio: float | None = None
    now_epoch = facade._runtime_now_epoch(state)
    return (anomaly_found, last_exit_sweep_by_symbol, max_hold_repeat, min_effective_loss_ratio, monitor_last_state, next_hold_counts, next_refresh_cooldowns, now_epoch, overnight_decisions, persisted, position_peak_price, position_strategy_context, prior_hold_counts, prior_refresh_cooldowns, profit_activation_ratio, reasons, repeated_hold_rows, risk_found, rows, rows_summary)


def open_pos_input_anomaly_found_candidate_loss_ratios(current_price, avg_price, qty, unrealized_pnl, account_pnl_ratio, price_anomaly, position_peak_price, row, symbol, profit_activation_ratio, last_exit_sweep_by_symbol, monitor_last_state, prior_hold_counts, next_hold_counts, max_hold_repeat, prior_refresh_cooldowns, now_epoch, next_refresh_cooldowns, min_effective_loss_ratio, reasons, price_anomaly_reason, repeated_hold_rows, state, position_strategy_context, anomaly_found, risk_found, *, facade):
    if True:
        raw_loss_ratio = (
            float((current_price / avg_price) - 1.0)
            if current_price > 0.0 and avg_price > 0.0
            else None
        )
        unrealized_loss_ratio = (
            float(unrealized_pnl / float(avg_price * qty))
            if avg_price > 0.0 and qty > 0
            else None
        )
        candidate_loss_ratios = [x for x in (raw_loss_ratio, unrealized_loss_ratio) if x is not None]
        if account_pnl_ratio is not None and not price_anomaly:
            candidate_loss_ratios.append(float(account_pnl_ratio))
        effective_loss_ratio = min(candidate_loss_ratios) if candidate_loss_ratios else None
        current_profit_ratio = facade._position_current_profit_ratio(
            raw_price_ratio=raw_loss_ratio,
            account_pnl_ratio=account_pnl_ratio,
            price_anomaly=price_anomaly,
        )
        peak_price = max(
            facade._runtime_float(row.get("peak_price"), 0.0),
            facade._runtime_float(row.get("high_water_mark"), 0.0),
            facade._runtime_float(position_peak_price.get(symbol), 0.0) if isinstance(position_peak_price, dict) else 0.0,
            current_price,
            avg_price,
        )
        peak_profit_ratio = float((peak_price / avg_price) - 1.0) if peak_price > 0.0 and avg_price > 0.0 else None
        profit_giveback_ratio = (
            max(0.0, float(peak_profit_ratio) - float(current_profit_ratio))
            if peak_profit_ratio is not None and current_profit_ratio is not None
            else 0.0
        )
        profit_protection_priority = 0
        if peak_profit_ratio is not None and peak_profit_ratio >= profit_activation_ratio:
            profit_protection_priority = 2
        elif current_profit_ratio is not None and current_profit_ratio >= profit_activation_ratio:
            profit_protection_priority = 2
        elif current_profit_ratio is not None and current_profit_ratio >= (profit_activation_ratio * 0.75):
            profit_protection_priority = 1
        last_exit_sweep_epoch = max(0, facade._coerce_int(last_exit_sweep_by_symbol.get(symbol), 0))

        previous = monitor_last_state.get(symbol) if isinstance(monitor_last_state, dict) else {}
        previous_posture = str((previous or {}).get("posture") or "").strip().lower()
        previous_reason = str((previous or {}).get("reason") or "")
        previous_active_exit_axis = str((previous or {}).get("active_exit_axis") or "")
        previous_entry_state = dict((previous or {}).get("entry_state") or {})
        hold_repeat_count = max(0, facade._coerce_int(prior_hold_counts.get(symbol), 0))
        if previous_posture == "hold":
            hold_repeat_count += 1
        else:
            hold_repeat_count = 0
        next_hold_counts[symbol] = int(hold_repeat_count)
        max_hold_repeat = max(max_hold_repeat, int(hold_repeat_count))
        refresh_cooldown_until = max(0, facade._coerce_int(prior_refresh_cooldowns.get(symbol), 0))
        if refresh_cooldown_until > now_epoch:
            next_refresh_cooldowns[symbol] = int(refresh_cooldown_until)

        if effective_loss_ratio is not None:
            min_effective_loss_ratio = (
                float(effective_loss_ratio)
                if min_effective_loss_ratio is None
                else min(float(min_effective_loss_ratio), float(effective_loss_ratio))
            )

        if price_anomaly:
            anomaly_found = True
            reasons.append(f"{symbol}:price_anomaly:{price_anomaly_reason}")
        if effective_loss_ratio is not None and effective_loss_ratio <= -0.01:
            risk_found = True
            reasons.append(f"{symbol}:loss_threshold:{effective_loss_ratio:.4f}")
        if hold_repeat_count >= 3:
            reasons.append(f"{symbol}:hold_repeat:{hold_repeat_count}")
            repeated_hold_rows.append(
                {
                    "symbol": symbol,
                    "hold_repeat_count": int(hold_repeat_count),
                    "refresh_cooldown_until": int(refresh_cooldown_until) if refresh_cooldown_until > 0 else 0,
                    "refresh_cooldown_remaining_sec": max(0, int(refresh_cooldown_until - now_epoch))
                    if refresh_cooldown_until > now_epoch
                    else 0,
                }
            )
        position_age_seconds = facade._resolve_position_age_seconds(state, row, symbol)
        symbol_strategy_context = (
            position_strategy_context.get(symbol)
            if isinstance(position_strategy_context, dict)
            else {}
        )
        symbol_strategy_context = (
            symbol_strategy_context if isinstance(symbol_strategy_context, dict) else {}
        )
        horizon_revision_allowed = bool(
            symbol_strategy_context.get("horizon_revision_allowed", True)
        )
    return (anomaly_found, candidate_loss_ratios, current_profit_ratio, effective_loss_ratio, hold_repeat_count, horizon_revision_allowed, last_exit_sweep_epoch, max_hold_repeat, min_effective_loss_ratio, peak_price, peak_profit_ratio, position_age_seconds, previous, previous_active_exit_axis, previous_entry_state, previous_posture, previous_reason, profit_giveback_ratio, profit_protection_priority, raw_loss_ratio, refresh_cooldown_until, risk_found, symbol_strategy_context, unrealized_loss_ratio)
