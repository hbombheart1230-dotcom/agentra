"""Commander stage-4 carry-review context/decision and position carry-control assessment (pure policy over state).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_stage4_carry_review_context_r3_impl(state, override_assessment, *, review_reason, facade):
    assessment = dict(override_assessment or {}) if isinstance(override_assessment, dict) else {}
    positions = [dict(row) for row in list(assessment.get("positions") or []) if isinstance(row, dict)]
    if not positions:
        for symbol in facade._portfolio_open_position_symbols(state):
            positions.append({"symbol": symbol, "qty": 0, "carry_state": "same_session", "carry_risk_bias": "normal"})
    if not positions:
        return {}
    focus = sorted(
        positions,
        key=facade._open_position_focus_sort_key,
    )[0]
    symbol = str(focus.get("symbol") or "").strip().upper()
    entry_state = facade._compact_monitor_entry_state_for_refresh(focus.get("entry_state") or {})
    market_context = state.get("market_context") if isinstance(state.get("market_context"), dict) else {}
    minutes_to_close = facade._shadow_float(market_context.get("minutes_to_close"))
    carry_state = str(focus.get("carry_state") or assessment.get("carry_state") or "same_session")
    carry_risk_bias = str(focus.get("carry_risk_bias") or assessment.get("carry_risk_bias") or "normal")
    carry_risk_reason = str(focus.get("carry_risk_reason") or assessment.get("carry_risk_reason") or "")
    summary = (
        f"End-of-day carry review for {symbol or 'unknown_symbol'} "
        f"with carry_state={carry_state}, carry_risk_bias={carry_risk_bias}."
    )
    if minutes_to_close is not None:
        summary += f" Minutes to close is {round(float(minutes_to_close), 2)}."
    if carry_risk_reason:
        summary += f" Carry reason: {carry_risk_reason}."
    return {
        "refresh_scope": "session_closeout_carry_review",
        "refresh_trigger": "end_of_day_carry_review",
        "refresh_signal": str(review_reason or "session_closeout_carry_review"),
        "refresh_summary": summary,
        "selected_symbol": symbol,
        "open_position_count": len(positions),
        "selected_hold_repeat_count": int(focus.get("hold_repeat_count") or 0),
        "selected_effective_loss_ratio": focus.get("effective_loss_ratio"),
        "monitor_posture": str(focus.get("posture") or ""),
        "monitor_reason": str(focus.get("reason") or ""),
        "active_exit_axis": str(focus.get("active_exit_axis") or ""),
        "position_qty": int(focus.get("qty") or 0),
        "position_age_seconds": focus.get("position_age_seconds"),
        "position_horizon_state": dict(focus.get("position_horizon_state") or {}),
        "carry_state": carry_state,
        "carry_risk_bias": carry_risk_bias,
        "carry_risk_reason": carry_risk_reason,
        "session_open_recovery_assessment": dict(
            focus.get("session_open_recovery_assessment")
            or assessment.get("session_open_recovery_assessment")
            or {}
        ),
        "entry_state": dict(entry_state),
        "minutes_to_close": round(float(minutes_to_close), 2) if minutes_to_close is not None else None,
        "positions": [
            {
                "symbol": str(row.get("symbol") or "").strip().upper(),
                "qty": int(row.get("qty") or 0),
                "carry_state": str(row.get("carry_state") or ""),
                "carry_risk_bias": str(row.get("carry_risk_bias") or ""),
                "carry_risk_reason": str(row.get("carry_risk_reason") or ""),
                "closeout_unresolved_flatten_required": bool(row.get("closeout_unresolved_flatten_required")),
                "effective_loss_ratio": row.get("effective_loss_ratio"),
                "hold_repeat_count": int(row.get("hold_repeat_count") or 0),
                "position_age_seconds": row.get("position_age_seconds"),
                "position_horizon_state": dict(row.get("position_horizon_state") or {}),
            }
            for row in positions[:5]
        ],
    }


def _force_stage4_carry_review_decision_r3_impl(state, commander_decision, *, review_reason, facade):
    override_assessment = (
        dict(state.get("commander_open_position_override") or {})
        if isinstance(state.get("commander_open_position_override"), dict)
        else {}
    )
    if not isinstance(override_assessment.get("positions"), list):
        override_assessment = facade._assess_open_position_commander_override(state)
        state["commander_open_position_override"] = dict(override_assessment)
    context = facade._build_stage4_carry_review_context(
        state,
        override_assessment,
        review_reason=review_reason,
    )
    if not context:
        return commander_decision
    state["commander_open_position_refresh_context"] = dict(context)
    out = dict(commander_decision or {})
    out["command_intent"] = "MANAGE_OPEN_RISK"
    out["strategist_invocation"] = "RUN_REFRESH"
    out["strategist_invocation_mode"] = "end_of_day_carry_review"
    out["llm_policy"] = "allow_context_refresh"
    out["flow_instruction"] = "REVIEW_END_OF_DAY_CARRY_BEFORE_CLOSE"
    out["strategist_refresh_requested"] = True
    out["strategist_refresh_reason"] = str(review_reason or "session_closeout_carry_review")
    out["strategist_refresh_context"] = dict(context)
    out["open_position_refresh_context"] = dict(context)
    out["carry_state"] = str(context.get("carry_state") or "")
    out["carry_risk_bias"] = str(context.get("carry_risk_bias") or "")
    out["carry_risk_reason"] = str(context.get("carry_risk_reason") or "")
    observations = out.get("observations") if isinstance(out.get("observations"), dict) else {}
    out["observations"] = {
        **dict(observations),
        "stage4_carry_review_requested": True,
        "stage4_carry_review_reason": str(review_reason or "session_closeout_carry_review"),
        "stage4_carry_review_selected_symbol": str(context.get("selected_symbol") or ""),
    }
    return out


def _assess_position_carry_control_r3_impl(
    *,
    state,
    symbol,
    hold_repeat_count,
    position_age_seconds,
    effective_loss_ratio,
    monitor_reason,
    active_exit_axis,
    entry_state,
    overnight_decision,
    facade,
):
    overnight = dict(overnight_decision or {}) if isinstance(overnight_decision, dict) else {}
    closeout_unresolved_flatten_required = facade._is_closeout_unresolved_flatten_symbol(state, symbol)
    carry_state = facade._derive_carry_state(
        position_age_seconds=position_age_seconds,
        hold_repeat_count=int(hold_repeat_count),
        overnight_decision=overnight,
    )
    if closeout_unresolved_flatten_required:
        carry_state = "multi_session_stale"
    session_open_recovery = facade._build_session_open_recovery_assessment(
        state=state,
        carry_state=carry_state,
        entry_state=entry_state,
        monitor_reason=str(monitor_reason or ""),
        active_exit_axis=str(active_exit_axis or ""),
        effective_loss_ratio=effective_loss_ratio,
    )
    carry_risk_bias = "normal"
    carry_risk_reason = "same_session_baseline"
    if closeout_unresolved_flatten_required:
        carry_risk_bias = "urgent_exit_review"
        carry_risk_reason = "closeout_unresolved_flatten_required"
    elif carry_state == "multi_session_stale":
        carry_risk_bias = "urgent_exit_review"
        carry_risk_reason = "multi_session_stale_position"
    elif carry_state == "overnight_open" and str(session_open_recovery.get("recovery_state") or "") == "failed":
        carry_risk_bias = "urgent_exit_review"
        carry_risk_reason = str(session_open_recovery.get("reason") or "overnight_open_recovery_failed")
    elif carry_state == "overnight_open":
        carry_risk_bias = "elevated"
        carry_risk_reason = "overnight_open_needs_confirmation"
    elif int(hold_repeat_count) >= 3 and effective_loss_ratio is not None and float(effective_loss_ratio) <= -0.01:
        carry_risk_bias = "elevated"
        carry_risk_reason = "same_session_repeated_hold_loss"
    return {
        "symbol": str(symbol or "").strip().upper(),
        "carry_state": str(carry_state),
        "carry_risk_bias": str(carry_risk_bias),
        "carry_risk_reason": str(carry_risk_reason),
        "overnight_carry_approved": bool(overnight.get("approved")),
        "overnight_carry_reason": str(overnight.get("reason") or ""),
        "closeout_unresolved_flatten_required": bool(closeout_unresolved_flatten_required),
        "session_open_recovery_assessment": dict(session_open_recovery),
    }


def _derive_carry_state_r3_impl(*, position_age_seconds, hold_repeat_count, overnight_decision, facade):
    age_sec = max(0, facade._coerce_int(position_age_seconds, 0))
    overnight = dict(overnight_decision or {}) if isinstance(overnight_decision, dict) else {}
    overnight_approved = bool(overnight.get("approved"))
    if age_sec >= 36 * 3600 or (overnight_approved and hold_repeat_count >= 5):
        return "multi_session_stale"
    if overnight_approved or age_sec >= 12 * 3600:
        return "overnight_open"
    return "same_session"


def _carry_state_rank_r3_impl(value, *, facade):
    text = str(value or "").strip().lower()
    if text == "multi_session_stale":
        return 2
    if text == "overnight_open":
        return 1
    return 0


def _carry_risk_bias_rank_r3_impl(value, *, facade):
    text = str(value or "").strip().lower()
    if text == "urgent_exit_review":
        return 2
    if text == "elevated":
        return 1
    return 0
