"""Commander open-position carry/review/cooldown/refresh assessment projections (result only; persisted_state write stays in the caller).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def open_pos_assess_carry_control(state, symbol, position_age_seconds, effective_loss_ratio, previous_reason, previous_active_exit_axis, previous_entry_state, hold_repeat_count, overnight_decisions, reasons, rows_summary, raw_loss_ratio, current_profit_ratio, peak_profit_ratio, profit_giveback_ratio, account_pnl_ratio, qty, peak_price, profit_protection_priority, profit_activation_ratio, last_exit_sweep_epoch, price_anomaly, price_anomaly_reason, horizon_review_due, horizon_revision_allowed, position_horizon_state, previous_posture, refresh_cooldown_until, now_epoch, *, facade):
    if True:
        carry_control = facade._assess_position_carry_control(
            state=state,
            symbol=symbol,
            hold_repeat_count=int(hold_repeat_count),
            position_age_seconds=position_age_seconds,
            effective_loss_ratio=effective_loss_ratio,
            monitor_reason=previous_reason,
            active_exit_axis=previous_active_exit_axis,
            entry_state=previous_entry_state,
            overnight_decision=overnight_decisions.get(symbol) if isinstance(overnight_decisions, dict) else {},
        )
        if str(carry_control.get("carry_risk_bias") or "") != "normal":
            reasons.append(
                f"{symbol}:carry_bias:{str(carry_control.get('carry_risk_bias') or '')}:{str(carry_control.get('carry_risk_reason') or '')}"
            )
        if bool(carry_control.get("closeout_unresolved_flatten_required")):
            reasons.append(f"{symbol}:closeout_unresolved_flatten_required")

        rows_summary.append(
            {
                "symbol": symbol,
                "qty": int(qty),
                "effective_loss_ratio": effective_loss_ratio,
                "raw_loss_ratio": raw_loss_ratio,
                "current_profit_ratio": current_profit_ratio,
                "peak_price": peak_price if peak_price > 0.0 else None,
                "peak_profit_ratio": peak_profit_ratio,
                "profit_giveback_ratio": profit_giveback_ratio,
                "profit_protection_priority": int(profit_protection_priority),
                "profit_protection_activation_ratio": float(profit_activation_ratio),
                "last_exit_sweep_epoch": int(last_exit_sweep_epoch),
                "account_pnl_ratio": account_pnl_ratio,
                "price_anomaly": bool(price_anomaly),
                "price_anomaly_reason": str(price_anomaly_reason),
                "hold_repeat_count": int(hold_repeat_count),
                "posture": str(previous_posture or ""),
                "reason": str(previous_reason or ""),
                "active_exit_axis": str(previous_active_exit_axis or ""),
                "entry_state": facade._compact_monitor_entry_state_for_refresh(previous_entry_state),
                "position_age_seconds": position_age_seconds,
                "horizon_review_due": bool(horizon_review_due),
                "horizon_revision_allowed": bool(horizon_revision_allowed),
                "position_horizon_state": dict(position_horizon_state),
                "refresh_cooldown_until": int(refresh_cooldown_until) if refresh_cooldown_until > 0 else None,
                "refresh_cooldown_remaining_sec": max(0, int(refresh_cooldown_until - now_epoch))
                if refresh_cooldown_until > now_epoch
                else 0,
                "carry_state": str(carry_control.get("carry_state") or ""),
                "carry_risk_bias": str(carry_control.get("carry_risk_bias") or ""),
                "carry_risk_reason": str(carry_control.get("carry_risk_reason") or ""),
                "overnight_carry_approved": bool(carry_control.get("overnight_carry_approved")),
                "overnight_carry_reason": str(carry_control.get("overnight_carry_reason") or ""),
                "closeout_unresolved_flatten_required": bool(
                    carry_control.get("closeout_unresolved_flatten_required")
                ),
                "session_open_recovery_assessment": dict(carry_control.get("session_open_recovery_assessment") or {}),
            }
        )
    return (carry_control,)


def open_pos_assess_force_exit_review_pending_open_position(closeout_unresolved_found, anomaly_found, risk_found, horizon_review_found, max_hold_repeat, *, facade):
    override_triggered = bool(
        closeout_unresolved_found
        or anomaly_found
        or risk_found
        or max_hold_repeat >= 3
        or horizon_review_found
    )
    override_action = ""
    override_reason = ""
    override_suppressed = False
    override_suppressed_reason = ""
    refresh_cooldown_symbol = ""
    refresh_cooldown_until = 0
    refresh_cooldown_remaining_sec = 0
    position_refresh_due = False
    position_refresh_trigger = ""
    force_exit_review_pending = False
    open_position_risk_review_reason = ""
    strategist_refresh_context: facade.Dict[str, facade.Any] = {}
    return (force_exit_review_pending, open_position_risk_review_reason, override_action, override_reason, override_suppressed, override_suppressed_reason, override_triggered, position_refresh_due, position_refresh_trigger, refresh_cooldown_remaining_sec, refresh_cooldown_symbol, refresh_cooldown_until, strategist_refresh_context)


def open_pos_assess_force_exit_review_pending_open_position_2(risk_found, _select_open_position_refresh_candidate, now_epoch, reasons, refresh_cooldown_remaining_sec, next_refresh_cooldowns, max_hold_repeat, min_effective_loss_ratio, anomaly_found, rows_summary, force_exit_review_pending, open_position_risk_review_reason, override_action, override_reason, override_suppressed, override_suppressed_reason, override_triggered, position_refresh_due, position_refresh_trigger, strategist_refresh_context, *, facade):
    if True:
            selected_row = (
                _select_open_position_refresh_candidate(require_loss=True)
                if risk_found
                else _select_open_position_refresh_candidate(require_loss=False)
            )
            refresh_cooldown_symbol = str(selected_row.get("symbol") or "")
            refresh_cooldown_until = max(0, facade._coerce_int(selected_row.get("refresh_cooldown_until"), 0))
            refresh_trigger = (
                "loss_threshold_exceeded"
                if risk_found
                else "horizon_review_due"
                if bool(selected_row.get("horizon_review_due"))
                else "repeated_hold_monitor_only"
            )
            if selected_row and refresh_cooldown_until > now_epoch:
                refresh_cooldown_remaining_sec = max(0, int(refresh_cooldown_until - now_epoch))
                override_suppressed = True
                override_suppressed_reason = (
                    "loss_threshold_refresh_cooldown"
                    if risk_found
                    else "repeated_hold_monitor_only_refresh_cooldown"
                )
                reasons.append(
                    f"{refresh_cooldown_symbol}:refresh_cooldown_active:{refresh_cooldown_remaining_sec}"
                )
                if risk_found:
                    override_action = "force_exit_review"
                    override_reason = "loss_threshold_exceeded"
                    force_exit_review_pending = True
                    open_position_risk_review_reason = "loss_threshold_exceeded"
                    position_refresh_trigger = str(refresh_trigger)
                else:
                    override_triggered = False
            elif selected_row:
                override_action = "strategist_refresh"
                override_reason = str(refresh_trigger)
                position_refresh_due = True
                position_refresh_trigger = str(refresh_trigger)
                force_exit_review_pending = bool(risk_found)
                open_position_risk_review_reason = "loss_threshold_exceeded" if risk_found else ""
                refresh_cooldown_until = int(now_epoch + facade._OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC)
                refresh_cooldown_remaining_sec = int(facade._OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC)
                if refresh_cooldown_symbol:
                    next_refresh_cooldowns[refresh_cooldown_symbol] = int(refresh_cooldown_until)
                strategist_refresh_context = facade._build_open_position_strategist_refresh_context(
                    {
                        "refresh_cooldown_symbol": refresh_cooldown_symbol,
                        "hold_repeat_count_max": max_hold_repeat,
                        "effective_loss_ratio_min": min_effective_loss_ratio,
                        "price_anomaly_flag": anomaly_found,
                        "refresh_trigger": str(refresh_trigger),
                        "refresh_cadence_sec": int(facade._OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC),
                        "force_exit_review_pending": bool(force_exit_review_pending),
                        "open_position_risk_review_reason": str(open_position_risk_review_reason),
                        "reason_chain": list(reasons),
                        "positions": rows_summary,
                    }
                )
            elif risk_found:
                override_action = "force_exit_review"
                override_reason = "loss_threshold_exceeded"
                force_exit_review_pending = True
                open_position_risk_review_reason = "loss_threshold_exceeded"
    return (force_exit_review_pending, open_position_risk_review_reason, override_action, override_reason, override_suppressed, override_suppressed_reason, override_triggered, position_refresh_due, position_refresh_trigger, refresh_cooldown_remaining_sec, refresh_cooldown_symbol, refresh_cooldown_until, strategist_refresh_context)
