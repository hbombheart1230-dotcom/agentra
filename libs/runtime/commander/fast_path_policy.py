"""Commander monitor-only and session-closeout fast-path eligibility policy (pure decisions; routing order unchanged).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _should_use_monitor_only_fast_path_r3_impl(state, *, facade):
    enabled, policy_source = facade._resolve_commander_route_toggle(
        state,
        nested_path=("commander", "route", "monitor_only_when_holding"),
        state_key="enable_monitor_only_fast_path",
        default=True,
    )
    open_position_count = facade._portfolio_open_position_count(state)
    max_positions = facade._resolve_risk_max_positions(state)
    entry_capacity_available = open_position_count < max_positions
    applied_policy = state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {}
    applied_entry = (applied_policy.get("monitor") or {}).get("entry") if isinstance((applied_policy.get("monitor") or {}), dict) else {}
    block_buy_when_open_position = facade._is_trueish(
        applied_entry.get("block_buy_when_open_position")
        if isinstance(applied_entry, dict) and applied_entry.get("block_buy_when_open_position") is not None
        else (
            state.get("monitor_block_buy_when_open_position")
            if state.get("monitor_block_buy_when_open_position") is not None
            else True
        )
    )
    payload = {
        "enabled": bool(enabled),
        "policy_source": str(policy_source),
        "open_position_count": int(open_position_count),
        "max_positions": int(max_positions),
        "entry_capacity_available": bool(entry_capacity_available),
        "multi_position_capacity_remaining": max(0, int(max_positions) - int(open_position_count)),
        "block_buy_when_open_position": bool(block_buy_when_open_position),
        "reason": "",
    }
    state["commander_open_position_override"] = {
        "override_triggered": False,
        "override_reason": "",
        "override_action": "",
        "policy_source": "commander_open_position_override",
    }
    state.pop("force_refresh_strategist", None)
    state.pop("commander_open_position_refresh_context", None)
    if not enabled:
        payload["reason"] = "disabled"
        return False, payload
    if open_position_count <= 0:
        payload["reason"] = "no_open_position"
        return False, payload
    override_assessment = facade._assess_open_position_commander_override(state)
    state["commander_open_position_override"] = dict(override_assessment)
    facade.record_stage3_assessment(state, override_assessment)
    payload.update(
        {
            "carry_state": str(override_assessment.get("carry_state") or ""),
            "carry_risk_bias": str(override_assessment.get("carry_risk_bias") or ""),
            "carry_risk_reason": str(override_assessment.get("carry_risk_reason") or ""),
            "session_open_recovery_assessment": dict(
                override_assessment.get("session_open_recovery_assessment") or {}
            )
            if isinstance(override_assessment.get("session_open_recovery_assessment"), dict)
            else {},
        }
    )
    if str(override_assessment.get("carry_risk_bias") or "").strip().lower() == "urgent_exit_review":
        payload.update(
            {
                "override_triggered": bool(override_assessment.get("override_triggered")),
                "override_reason": str(override_assessment.get("override_reason") or ""),
                "override_action": str(override_assessment.get("override_action") or ""),
            }
        )
        payload["reason"] = "holding_position_carry_risk_monitor_only"
        return True, payload
    if bool(override_assessment.get("override_triggered")):
        override_action = str(override_assessment.get("override_action") or "").strip().lower()
        if override_action == "strategist_refresh":
            state["force_refresh_strategist"] = True
            refresh_context = (
                dict(override_assessment.get("strategist_refresh_context") or {})
                if isinstance(override_assessment.get("strategist_refresh_context"), dict)
                else {}
            )
            if refresh_context:
                state["commander_open_position_refresh_context"] = dict(refresh_context)
        payload.update(
            {
                "override_triggered": True,
                "override_reason": str(override_assessment.get("override_reason") or ""),
                "override_action": str(override_assessment.get("override_action") or ""),
                "carry_state": str(override_assessment.get("carry_state") or ""),
                "carry_risk_bias": str(override_assessment.get("carry_risk_bias") or ""),
                "carry_risk_reason": str(override_assessment.get("carry_risk_reason") or ""),
                "session_open_recovery_assessment": dict(
                    override_assessment.get("session_open_recovery_assessment") or {}
                )
                if isinstance(override_assessment.get("session_open_recovery_assessment"), dict)
                else {},
                "effective_loss_ratio_min": override_assessment.get("effective_loss_ratio_min"),
                "hold_repeat_count_max": int(override_assessment.get("hold_repeat_count_max") or 0),
                "price_anomaly_flag": bool(override_assessment.get("price_anomaly_flag")),
                "override_suppressed": bool(override_assessment.get("override_suppressed")),
                "override_suppressed_reason": str(override_assessment.get("override_suppressed_reason") or ""),
                "refresh_cooldown_sec": int(override_assessment.get("refresh_cooldown_sec") or 0),
                "refresh_cooldown_symbol": str(override_assessment.get("refresh_cooldown_symbol") or ""),
                "refresh_cooldown_until": override_assessment.get("refresh_cooldown_until"),
                "refresh_cooldown_remaining_sec": int(
                    override_assessment.get("refresh_cooldown_remaining_sec") or 0
                ),
                "position_refresh_due": bool(override_assessment.get("position_refresh_due")),
                "position_refresh_trigger": str(override_assessment.get("position_refresh_trigger") or ""),
                "force_exit_review_pending": bool(override_assessment.get("force_exit_review_pending")),
                "open_position_risk_review_reason": str(
                    override_assessment.get("open_position_risk_review_reason") or ""
                ),
                "strategist_refresh_context": dict(
                    override_assessment.get("strategist_refresh_context") or {}
                )
                if isinstance(override_assessment.get("strategist_refresh_context"), dict)
                else {},
            }
        )
        if override_action == "force_exit_review":
            payload["reason"] = "holding_position_force_exit_review_monitor_only"
            return True, payload
        payload["reason"] = "holding_position_override_full_cycle"
        return False, payload
    if bool(override_assessment.get("override_suppressed")):
        payload.update(
            {
                "override_suppressed": True,
                "override_suppressed_reason": str(override_assessment.get("override_suppressed_reason") or ""),
                "carry_state": str(override_assessment.get("carry_state") or ""),
                "carry_risk_bias": str(override_assessment.get("carry_risk_bias") or ""),
                "carry_risk_reason": str(override_assessment.get("carry_risk_reason") or ""),
                "session_open_recovery_assessment": dict(
                    override_assessment.get("session_open_recovery_assessment") or {}
                )
                if isinstance(override_assessment.get("session_open_recovery_assessment"), dict)
                else {},
                "hold_repeat_count_max": int(override_assessment.get("hold_repeat_count_max") or 0),
                "refresh_cooldown_sec": int(override_assessment.get("refresh_cooldown_sec") or 0),
                "refresh_cooldown_symbol": str(override_assessment.get("refresh_cooldown_symbol") or ""),
                "refresh_cooldown_until": override_assessment.get("refresh_cooldown_until"),
                "refresh_cooldown_remaining_sec": int(
                    override_assessment.get("refresh_cooldown_remaining_sec") or 0
                ),
                "position_refresh_due": bool(override_assessment.get("position_refresh_due")),
                "position_refresh_trigger": str(override_assessment.get("position_refresh_trigger") or ""),
                "force_exit_review_pending": bool(override_assessment.get("force_exit_review_pending")),
                "open_position_risk_review_reason": str(
                    override_assessment.get("open_position_risk_review_reason") or ""
                ),
            }
        )
    if str(override_assessment.get("carry_risk_bias") or "").strip().lower() == "urgent_exit_review":
        payload["reason"] = "holding_position_carry_risk_monitor_only"
        return True, payload
    if str(override_assessment.get("override_action") or "").strip().lower() == "strategist_refresh":
        payload["reason"] = "open_position_horizon_review_due"
        return False, payload
    if entry_capacity_available:
        payload["reason"] = "multi_position_capacity_available"
        return False, payload
    if not block_buy_when_open_position:
        payload["reason"] = "buy_not_blocked_when_open_position"
        return False, payload
    payload["reason"] = "holding_position_monitor_only" if max_positions <= 1 else "max_positions_reached_monitor_only"
    return True, payload


def _should_use_session_closeout_fast_path_r3_impl(state, *, facade):
    applied_policy = state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {}
    policy = state.get("policy") if isinstance(state.get("policy"), dict) else {}
    monitor_exit = (
        ((applied_policy.get("monitor") or {}).get("exit") or {})
        if isinstance((applied_policy.get("monitor") or {}).get("exit"), dict)
        else {}
    )
    eod_flat = (
        (monitor_exit.get("eod_flat") or {})
        if isinstance(monitor_exit.get("eod_flat"), dict)
        else {}
    )
    if not eod_flat and isinstance((((policy.get("monitor") or {}).get("exit") or {}).get("eod_flat")), dict):
        eod_flat = dict((((policy.get("monitor") or {}).get("exit") or {}).get("eod_flat")) or {})
    use_eod_flat = (
        eod_flat.get("enabled")
        if eod_flat.get("enabled") is not None
        else (
            (policy.get("exit_policy") or {}).get("use_eod_flat")
            if isinstance(policy.get("exit_policy"), dict)
            else None
        )
    )
    cutoff_min = (
        eod_flat.get("cutoff_min")
        if eod_flat.get("cutoff_min") not in (None, "")
        else (
            (policy.get("exit_policy") or {}).get("eod_flat_cutoff_min")
            if isinstance(policy.get("exit_policy"), dict)
            else None
        )
    )
    applied_entry = (
        ((applied_policy.get("monitor") or {}).get("entry") or {})
        if isinstance((applied_policy.get("monitor") or {}).get("entry"), dict)
        else {}
    )
    policy_entry = (
        ((policy.get("monitor") or {}).get("entry") or {})
        if isinstance((policy.get("monitor") or {}).get("entry"), dict)
        else {}
    )
    eod_cutoff_int = facade._coerce_int(cutoff_min, 10)
    buy_cutoff_raw = (
        applied_entry.get("buy_closeout_cutoff_min")
        if applied_entry.get("buy_closeout_cutoff_min") not in (None, "")
        else policy_entry.get("buy_closeout_cutoff_min")
    )
    buy_cutoff_min = facade._coerce_int(
        buy_cutoff_raw,
        max(facade._DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN, eod_cutoff_int),
    )
    if buy_cutoff_min <= 0:
        buy_cutoff_min = max(facade._DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN, eod_cutoff_int)
    buy_cutoff_min = max(eod_cutoff_int, buy_cutoff_min)
    market_context = facade._ensure_market_context_clock_fields(state)
    market_status = (
        state.get("kiwoom_market_status")
        if isinstance(state.get("kiwoom_market_status"), dict)
        else {}
    )
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    market_status_code = str(
        market_status.get("code")
        or (
            (persisted.get("kiwoom_market_status") or {}).get("code")
            if isinstance(persisted.get("kiwoom_market_status"), dict)
            else ""
        )
        or ""
    )
    market_closeout_notice = bool(
        market_status_code == "2"
        or state.get("kiwoom_closeout_notice_active")
        or persisted.get("kiwoom_closeout_notice_active")
    )
    raw_minutes_to_close = market_context.get("minutes_to_close")
    minutes_to_close = None if raw_minutes_to_close in (None, "") else float(facade._runtime_float(raw_minutes_to_close, 0.0))
    active = bool(
        facade._is_trueish(use_eod_flat if use_eod_flat is not None else True)
        and (
            market_closeout_notice
            or (
                minutes_to_close is not None
                and minutes_to_close >= 0.0
                and minutes_to_close <= float(buy_cutoff_min)
            )
        )
    )
    payload = {
        "active": bool(active),
        "minutes_to_close": minutes_to_close,
        "cutoff_min": int(eod_cutoff_int),
        "buy_cutoff_min": int(buy_cutoff_min),
        "use_eod_flat": bool(facade._is_trueish(use_eod_flat if use_eod_flat is not None else True)),
        "open_position_count": int(facade._portfolio_open_position_count(state)),
        "market_status_code": market_status_code,
        "market_status_triggered": market_closeout_notice,
        "reason": "kiwoom_market_closeout_notice" if market_closeout_notice else ("session_closeout_window" if active else (
            "minutes_to_close_unavailable"
            if minutes_to_close is None
            else "outside_closeout_window"
        )),
    }
    return bool(active), payload
