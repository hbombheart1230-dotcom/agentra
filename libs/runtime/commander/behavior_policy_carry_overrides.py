"""Commander behavior policy: carry-risk exit policy overrides and adjustment trace.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/commander_runtime.py::_resolve_commander_behavior_policy` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class CarryExitPolicyOverrides(NamedTuple):
    """Result of `resolve_carry_exit_policy_overrides` (positional order = sorted output names)."""

    carry_exit_policy_overrides: Any
    carry_policy_adjustments: Any

def resolve_carry_exit_policy_overrides(carry_risk_bias, carry_state, commander_override, eod_flat_cutoff_min, hold_repeat_count_max, override_reason, state, *, facade):
    effective_loss_ratio_min = float(facade._runtime_float(commander_override.get("effective_loss_ratio_min"), 0.0))
    session_open_recovery = (
        dict(commander_override.get("session_open_recovery_assessment") or {})
        if isinstance(commander_override.get("session_open_recovery_assessment"), dict)
        else {}
    )
    market_context = state.get("market_context") if isinstance(state.get("market_context"), dict) else {}
    raw_minutes_to_close = market_context.get("minutes_to_close")
    minutes_to_close = None if raw_minutes_to_close in (None, "") else float(facade._runtime_float(raw_minutes_to_close, 0.0))
    carry_exit_policy_overrides: facade.Dict[str, facade.Any] = {}
    carry_policy_adjustments: list[str] = []
    if carry_risk_bias == "urgent_exit_review":
        carry_exit_policy_overrides = {
            "vwap_break_requires_profit": False,
            "hard_stop_pct": 0.015,
            "intraday_low_break_pct": 0.001,
            "trend_strength_floor": -0.10,
        }
        carry_policy_adjustments.append("carry_bias:urgent_exit_review->tighten_exit_policy")
        if str(session_open_recovery.get("recovery_state") or "").strip().lower() == "failed":
            carry_exit_policy_overrides["peak_drawdown_mode"] = "always_on"
            carry_policy_adjustments.append("session_open_recovery:failed->always_on_peak_drawdown")
    elif carry_risk_bias == "elevated" and carry_state in {"overnight_open", "multi_session_stale"}:
        carry_exit_policy_overrides = {
            "vwap_break_requires_profit": False,
            "intraday_low_break_pct": 0.0015,
            "trend_strength_floor": -0.12,
        }
        carry_policy_adjustments.append("carry_bias:elevated->narrow_exit_confirmation")
    elif (
        carry_risk_bias == "elevated"
        and carry_state == "same_session"
        and override_reason == "loss_threshold_exceeded"
        and hold_repeat_count_max >= 6
    ):
        carry_exit_policy_overrides = {
            "vwap_break_requires_profit": False,
            "intraday_low_break_pct": 0.0012,
            "trend_strength_floor": -0.11,
        }
        carry_policy_adjustments.append("carry_bias:elevated_same_session->tighten_loss_review")
        if effective_loss_ratio_min <= -0.01:
            carry_exit_policy_overrides["peak_drawdown_mode"] = "always_on"
            carry_policy_adjustments.append("same_session_loss_threshold->always_on_peak_drawdown")
        closeout_cutoff_min = max(15, facade._coerce_int(eod_flat_cutoff_min, 10))
        if minutes_to_close is not None and minutes_to_close <= float(closeout_cutoff_min):
            carry_exit_policy_overrides["use_eod_flat"] = True
            carry_exit_policy_overrides["eod_flat_cutoff_min"] = closeout_cutoff_min
            carry_policy_adjustments.append(
                f"same_session_loss_near_close->eod_flat_cutoff:{int(closeout_cutoff_min)}"
            )
    return CarryExitPolicyOverrides(carry_exit_policy_overrides, carry_policy_adjustments)
