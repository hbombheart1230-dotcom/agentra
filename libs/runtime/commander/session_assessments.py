"""Commander session-open recovery, intraday performance circuit and market-regime assessments (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_session_open_recovery_assessment_r3_impl(
    *,
    state,
    carry_state,
    entry_state,
    monitor_reason,
    active_exit_axis,
    effective_loss_ratio,
    facade,
):
    mh = facade.MarketHours()
    dt_kst = facade._runtime_clock_dt_kst(state, market_hours=mh)
    open_dt = dt_kst.replace(
        hour=mh.open_time.hour,
        minute=mh.open_time.minute,
        second=0,
        microsecond=0,
    )
    minutes_from_open = None
    if mh.is_open(dt_kst):
        minutes_from_open = max(0.0, (dt_kst - open_dt).total_seconds() / 60.0)
    in_open_window = bool(minutes_from_open is not None and minutes_from_open <= 15.0)
    compact_entry_state = facade._compact_monitor_entry_state_for_refresh(entry_state)
    blocking_axis = str(compact_entry_state.get("current_blocking_axis") or "")
    reclaim_gate_ok = bool(compact_entry_state.get("reclaim_gate_ok"))
    volume_ok = bool(compact_entry_state.get("volume_ok"))
    blockers = [str(x) for x in list(compact_entry_state.get("entry_blockers") or []) if str(x or "").strip()]
    recovery_state = "not_applicable"
    recovery_reason = ""
    if carry_state == "same_session":
        recovery_reason = "same_session_position"
    elif not in_open_window:
        recovery_state = "pending"
        recovery_reason = "outside_session_open_window"
    elif reclaim_gate_ok and volume_ok:
        recovery_state = "recovered"
        recovery_reason = "reclaim_and_volume_recovered"
    elif (
        blocking_axis == "reclaim_readiness"
        or any("reclaim" in str(x or "").strip().lower() for x in blockers)
        or "reclaim" in monitor_reason.lower()
        or "vwap" in monitor_reason.lower()
        or active_exit_axis == "vwap_relationship"
        or not reclaim_gate_ok
    ):
        recovery_state = "failed"
        recovery_reason = "reclaim_failed_near_open"
    elif effective_loss_ratio is not None and float(effective_loss_ratio) <= -0.01:
        recovery_state = "failed"
        recovery_reason = "loss_threshold_open_weakness"
    else:
        recovery_state = "mixed"
        recovery_reason = "open_recovery_signal_mixed"
    return {
        "evaluated": bool(carry_state != "same_session"),
        "market_clock_kst": dt_kst.isoformat(),
        "minutes_from_open": round(float(minutes_from_open), 2) if minutes_from_open is not None else None,
        "in_session_open_window": bool(in_open_window),
        "recovery_state": str(recovery_state),
        "reason": str(recovery_reason),
        "blocking_axis": blocking_axis,
        "reclaim_gate_ok": bool(reclaim_gate_ok),
        "volume_ok": bool(volume_ok),
        "monitor_reason": str(monitor_reason or ""),
        "active_exit_axis": str(active_exit_axis or ""),
    }


def _build_intraday_performance_circuit_r3_impl(*, strategist_output, memory_packets, current_day, facade):
    if not str(current_day or "").strip():
        return {
            "schema_version": "intraday_performance_circuit.v1",
            "active": False,
            "playbook": str(strategist_output.get("final_playbook") or strategist_output.get("playbook") or "").strip().lower(),
            "reason": "",
            "triggers": [],
            "thresholds": {"loss_count": 3, "avg_return": -0.008, "playbook_win_rate": 0.20},
            "source": "disabled:no_current_day",
        }
    playbook = str(
        strategist_output.get("final_playbook")
        or strategist_output.get("playbook")
        or ""
    ).strip().lower()
    daily = facade._mapping(memory_packets.get("daily_strategy_memory"))
    resolved_day = str(daily.get("resolved_day") or daily.get("day") or "").strip()
    if resolved_day and resolved_day != str(current_day or "").strip():
        return {
            "schema_version": "intraday_performance_circuit.v1",
            "active": False,
            "playbook": playbook,
            "reason": "",
            "triggers": [],
            "thresholds": {"loss_count": 3, "avg_return": -0.008, "playbook_win_rate": 0.20},
            "source": f"disabled:memory_day_mismatch:{resolved_day}",
        }
    pattern_snapshot = facade._mapping(daily.get("pattern_performance_snapshot"))
    entry_exit = facade._mapping(pattern_snapshot.get("entry_exit_combos"))
    playbook_stats = facade._mapping(daily.get("playbook_performance_snapshot") or daily.get("playbook_stats"))
    triggers = []

    if playbook:
        for combo, payload in entry_exit.items():
            combo_text = str(combo or "").strip().lower()
            if not combo_text.startswith(f"{playbook} -> "):
                continue
            row = facade._mapping(payload)
            loss_count = facade._coerce_int(row.get("loss_count"), 0)
            avg_return = facade._runtime_float(row.get("avg_return"), 0.0)
            if loss_count >= 3 or avg_return <= -0.008:
                triggers.append(
                    {
                        "scope": "entry_exit_combo",
                        "combo": combo_text,
                        "loss_count": int(loss_count),
                        "avg_return": float(avg_return),
                    }
                )
        row = facade._mapping(playbook_stats.get(playbook))
        usage_count = facade._coerce_int(row.get("usage_count") or row.get("trade_count"), 0)
        avg_return = facade._runtime_float(row.get("avg_return"), 0.0)
        win_rate = facade._runtime_float(row.get("win_rate"), 0.0)
        if usage_count >= 3 and (avg_return <= -0.008 or win_rate <= 0.20):
            triggers.append(
                {
                    "scope": "playbook",
                    "playbook": playbook,
                    "usage_count": int(usage_count),
                    "win_rate": float(win_rate),
                    "avg_return": float(avg_return),
                }
            )

    active = bool(triggers)
    return {
        "schema_version": "intraday_performance_circuit.v1",
        "active": active,
        "playbook": playbook,
        "reason": "intraday_playbook_exit_combo_underperforming" if active else "",
        "triggers": triggers[:5],
        "thresholds": {"loss_count": 3, "avg_return": -0.008, "playbook_win_rate": 0.20},
        "source": "daily_strategy_memory.pattern_performance_snapshot",
    }


def _derive_commander_market_regime_r3_impl(state, *, shadow_assessment, facade):
    direct_regime = str(state.get("market_regime") or "").strip()
    if direct_regime:
        return direct_regime, False
    shadow_regime = str(
        (
            (shadow_assessment.get("post_strategist_assessment") or {}).get("market_regime")
            if isinstance(shadow_assessment.get("post_strategist_assessment"), dict)
            else ""
        )
        or ""
    ).strip()
    if shadow_regime:
        return shadow_regime, True
    global_signal = state.get("global_signal") if isinstance(state.get("global_signal"), dict) else {}
    fear_index = global_signal.get("fear_index") if isinstance(global_signal.get("fear_index"), dict) else {}
    sentiment_score = facade._runtime_float(global_signal.get("score"), 0.0)
    fear_level = facade._runtime_float(fear_index.get("level"), 0.0)
    if fear_level >= 28.0 or sentiment_score <= -0.15:
        return "risk_off", False
    if fear_level <= 20.0 and sentiment_score >= 0.15:
        return "risk_on", False
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    fallback_regime = str(strategist_output.get("market_regime") or "").strip()
    if fallback_regime:
        return fallback_regime, True
    return "neutral", False


def _build_shadow_assessment_summary_r3_impl(
    state,
    *,
    mode_value,
    phase_value,
    status_value,
    path_value,
    reason_text,
    facade,
):
    try:
        return facade.build_commander_shadow_artifact(
            state,
            mode=str(mode_value or ""),
            phase=str(phase_value or ""),
            path=str(path_value or ""),
            status=str(status_value or "ok"),
            reason=str(reason_text or ""),
        )
    except Exception:
        return {}


def _ensure_market_context_clock_fields_r3_impl(state, *, market_hours, facade):
    mh = market_hours or facade.MarketHours()
    market_context = state.get("market_context") if isinstance(state.get("market_context"), dict) else {}
    out = dict(market_context or {})
    existing_minutes = None if out.get("minutes_to_close") in (None, "") else float(facade._runtime_float(out.get("minutes_to_close"), 0.0))
    has_reliable_runtime_clock = facade._runtime_clock_input_present(state)
    if existing_minutes is not None and not has_reliable_runtime_clock:
        state["market_context"] = out
        return out
    dt_kst = facade._runtime_clock_dt_kst(state, market_hours=mh)
    minutes_to_close: float | None = None
    if mh.is_open(dt_kst):
        close_dt = dt_kst.replace(
            hour=mh.close_time.hour,
            minute=mh.close_time.minute,
            second=0,
            microsecond=0,
        )
        minutes_to_close = max(0.0, (close_dt - dt_kst).total_seconds() / 60.0)
    if minutes_to_close is None and existing_minutes is not None:
        state["market_context"] = out
        return out

    previous_source = str(out.get("market_clock_source") or "")
    if existing_minutes is not None and minutes_to_close is not None:
        drift = abs(float(existing_minutes) - float(minutes_to_close))
        if drift <= 1.0:
            out["minutes_to_close"] = float(existing_minutes)
            out.setdefault("market_clock_source", previous_source or "runtime_clock_verified")
            out.setdefault("market_clock_kst", dt_kst.isoformat())
            out["market_clock_verified_minutes_to_close"] = float(minutes_to_close)
            state["market_context"] = out
            return out
        out["market_clock_previous_minutes_to_close"] = float(existing_minutes)
        if previous_source:
            out["market_clock_previous_source"] = previous_source
        out["market_clock_source"] = "runtime_clock_override"
    else:
        out.setdefault("market_clock_source", "runtime_clock")
    out["minutes_to_close"] = minutes_to_close
    out["market_clock_kst"] = dt_kst.isoformat()
    state["market_context"] = out
    return out
