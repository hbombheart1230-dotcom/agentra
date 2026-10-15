"""Commander open-position override: result surface.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/commander_runtime.py::_assess_open_position_commander_override` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_open_position_override_result(anomaly_found, carry_focus, closeout_unresolved_found, force_exit_review_pending, max_hold_repeat, min_effective_loss_ratio, open_position_risk_review_reason, override_action, override_reason, override_suppressed, override_suppressed_reason, override_triggered, position_refresh_due, position_refresh_trigger, reasons, refresh_cooldown_remaining_sec, refresh_cooldown_symbol, refresh_cooldown_until, rows_summary, strategist_refresh_context, *, facade):
    return (
        {
        "override_triggered": bool(override_triggered),
        "override_reason": str(override_reason),
        "override_action": str(override_action),
        "override_suppressed": bool(override_suppressed),
        "override_suppressed_reason": str(override_suppressed_reason),
        "reason_chain": list(reasons[:8]),
        "hold_repeat_count_max": int(max_hold_repeat),
        "effective_loss_ratio_min": min_effective_loss_ratio,
        "price_anomaly_flag": bool(anomaly_found),
        "closeout_unresolved_flatten_required": bool(closeout_unresolved_found),
        "refresh_cooldown_sec": int(facade._OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC),
        "refresh_cooldown_symbol": str(refresh_cooldown_symbol),
        "refresh_cooldown_until": int(refresh_cooldown_until) if refresh_cooldown_until > 0 else None,
        "refresh_cooldown_remaining_sec": int(refresh_cooldown_remaining_sec),
        "position_refresh_due": bool(position_refresh_due),
        "position_refresh_trigger": str(position_refresh_trigger),
        "force_exit_review_pending": bool(force_exit_review_pending),
        "open_position_risk_review_reason": str(open_position_risk_review_reason),
        "strategist_refresh_context": dict(strategist_refresh_context),
        "carry_state": str(carry_focus.get("carry_state") or ""),
        "carry_risk_bias": str(carry_focus.get("carry_risk_bias") or ""),
        "carry_risk_reason": str(carry_focus.get("carry_risk_reason") or ""),
        "session_open_recovery_assessment": dict(carry_focus.get("session_open_recovery_assessment") or {}),
        "policy_source": "commander_open_position_override",
        "positions": rows_summary,
    }
    )
