"""Commander open-position, focus-symbol and strategist-refresh context projections (pure read-model).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _portfolio_open_position_count_r3_impl(state, *, facade):
    snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    positions = snapshot.get("positions")
    if isinstance(positions, dict):
        rows = list(positions.values())
    elif isinstance(positions, list):
        rows = positions
    else:
        rows = []
    count = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if facade._coerce_int(row.get("qty"), 0) > 0:
            count += 1
    return int(count)


def _portfolio_open_position_symbols_r3_impl(state, *, facade):
    snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    positions = snapshot.get("positions")
    if isinstance(positions, dict):
        rows = list(positions.values())
    elif isinstance(positions, list):
        rows = positions
    else:
        rows = []
    seen: set[str] = set()
    symbols: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if facade._coerce_int(row.get("qty"), 0) <= 0:
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)
    return symbols


def _portfolio_open_position_row_r3_impl(state, symbol, *, facade):
    target = str(symbol or "").strip().upper()
    if not target:
        return {}
    snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    positions = snapshot.get("positions")
    if isinstance(positions, dict):
        rows = list(positions.values())
    elif isinstance(positions, list):
        rows = positions
    else:
        rows = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("symbol") or "").strip().upper() != target:
            continue
        if facade._coerce_int(row.get("qty"), 0) <= 0:
            continue
        return dict(row)
    return {}


def _open_position_focus_sort_key_r3_impl(item, *, facade):
    return (
        -int(bool(item.get("closeout_unresolved_flatten_required"))),
        -facade._carry_risk_bias_rank(item.get("carry_risk_bias")),
        -facade._carry_state_rank(item.get("carry_state")),
        -facade._coerce_int(item.get("profit_protection_priority"), 0),
        -max(0.0, float(facade._runtime_float(item.get("profit_giveback_ratio"), 0.0))),
        float(facade._runtime_float(item.get("effective_loss_ratio"), 0.0)),
        max(0, facade._coerce_int(item.get("last_exit_sweep_epoch"), 0)),
        -facade._coerce_int(item.get("hold_repeat_count"), 0),
        str(item.get("symbol") or ""),
    )


def _select_open_position_focus_symbol_r3_impl(state, fallback_symbols, *, facade):
    fallback = [str(x or "").strip().upper() for x in list(fallback_symbols or []) if str(x or "").strip()]
    held_set = set(fallback)
    unresolved = facade._closeout_unresolved_flatten_symbols(state)
    for symbol in fallback:
        if symbol in unresolved:
            return symbol

    assessment = (
        dict(state.get("commander_open_position_override") or {})
        if isinstance(state.get("commander_open_position_override"), dict)
        else {}
    )
    positions = []
    for row in list(assessment.get("positions") or []):
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol or (held_set and symbol not in held_set):
            continue
        positions.append({**dict(row), "symbol": symbol})
    if positions:
        return str(sorted(positions, key=facade._open_position_focus_sort_key)[0].get("symbol") or "")
    return fallback[0] if fallback else ""


def _closeout_unresolved_flatten_symbols_r3_impl(state, *, facade):
    symbols: set[str] = set()
    sources: list[Dict[str, Any]] = []
    if isinstance(state, dict):
        sources.append(state)
        persisted = state.get("persisted_state")
        if isinstance(persisted, dict):
            sources.append(persisted)
    for source in sources:
        backup = source.get("closeout_backup_liquidation") if isinstance(source, dict) else {}
        if isinstance(backup, dict):
            for key in ("unresolved_flatten_symbols", "unresolved_flatten_requires_next_open_symbols"):
                for value in list(backup.get(key) or []):
                    symbol = str(value or "").strip().upper()
                    if symbol:
                        symbols.add(symbol)
        unresolved_map = source.get("closeout_unresolved_flatten_by_symbol") if isinstance(source, dict) else {}
        if isinstance(unresolved_map, dict):
            for key in unresolved_map.keys():
                symbol = str(key or "").strip().upper()
                if symbol:
                    symbols.add(symbol)
    return symbols


def _resolve_position_age_seconds_r3_impl(state, row, symbol, *, facade):
    for key in ("position_age_seconds", "hold_sec"):
        age = facade._coerce_int(row.get(key), 0)
        if age > 0:
            return int(age)

    now_epoch = facade._runtime_now_epoch(state)
    entry_epoch = facade._coerce_int(
        row.get("position_entry_epoch")
        if row.get("position_entry_epoch") not in (None, "")
        else row.get("entry_epoch"),
        0,
    )
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    if entry_epoch <= 0 and isinstance(persisted.get("position_entry_epoch_by_symbol"), dict):
        entry_epoch = facade._coerce_int((persisted.get("position_entry_epoch_by_symbol") or {}).get(symbol), 0)
    if entry_epoch > 0 and now_epoch > 0:
        return max(0, int(now_epoch - entry_epoch))
    last_trade_side = str(persisted.get("last_trade_side") or "").strip().upper()
    last_trade_symbol = str(persisted.get("last_trade_symbol") or "").strip().upper()
    last_trade_epoch = facade._coerce_int(persisted.get("last_trade_epoch"), 0)
    if (
        last_trade_side == "BUY"
        and last_trade_epoch > 0
        and now_epoch > 0
        and (not last_trade_symbol or last_trade_symbol == str(symbol or "").strip().upper())
    ):
        return max(0, int(now_epoch - last_trade_epoch))
    if last_trade_side == "BUY" and last_trade_epoch > 0 and now_epoch > 0:
        legacy_age = max(0, int(now_epoch - last_trade_epoch))
        if legacy_age >= 12 * 3600:
            return int(legacy_age)
    return None


def _build_open_position_strategist_refresh_context_r3_impl(override_assessment, *, facade):
    assessment = dict(override_assessment or {}) if isinstance(override_assessment, dict) else {}
    positions = [dict(x) for x in list(assessment.get("positions") or []) if isinstance(x, dict)]
    selected_symbol = str(assessment.get("refresh_cooldown_symbol") or "").strip().upper()
    selected_position = next(
        (
            row
            for row in positions
            if str(row.get("symbol") or "").strip().upper() == selected_symbol
        ),
        positions[0] if positions else {},
    )
    entry_state = facade._compact_monitor_entry_state_for_refresh(selected_position.get("entry_state") or {})
    entry_blockers = [str(x) for x in list(entry_state.get("entry_blockers") or []) if str(x or "").strip()]
    refresh_trigger = str(assessment.get("refresh_trigger") or "repeated_hold_monitor_only").strip()
    selected_hold_repeat_count = int(
        selected_position.get("hold_repeat_count") or assessment.get("hold_repeat_count_max") or 0
    )
    if refresh_trigger == "loss_threshold_exceeded":
        summary = (
            f"Loss threshold refresh for {selected_symbol or 'unknown_symbol'} after "
            f"{selected_hold_repeat_count} consecutive hold cycles."
        )
    else:
        summary = (
            f"Repeated hold refresh for {selected_symbol or 'unknown_symbol'} after "
            f"{selected_hold_repeat_count} consecutive hold cycles."
        )
    blocking_axis = str(entry_state.get("current_blocking_axis") or "")
    if blocking_axis:
        summary += f" Current blocking axis is {blocking_axis}."
    if entry_blockers:
        summary += f" Primary blockers: {', '.join(entry_blockers[:3])}."
    carry_state = str(selected_position.get("carry_state") or assessment.get("carry_state") or "")
    carry_risk_bias = str(selected_position.get("carry_risk_bias") or assessment.get("carry_risk_bias") or "")
    carry_risk_reason = str(selected_position.get("carry_risk_reason") or assessment.get("carry_risk_reason") or "")
    session_open_recovery_assessment = (
        dict(selected_position.get("session_open_recovery_assessment") or assessment.get("session_open_recovery_assessment") or {})
        if isinstance(selected_position.get("session_open_recovery_assessment"), dict)
        or isinstance(assessment.get("session_open_recovery_assessment"), dict)
        else {}
    )
    if carry_state:
        summary += f" Carry state is {carry_state}."
    if carry_risk_bias and carry_risk_bias != "normal":
        summary += f" Carry risk bias is {carry_risk_bias}."
    if carry_risk_reason:
        summary += f" Carry control reason: {carry_risk_reason}."
    return {
        "refresh_scope": "open_position_monitor_refresh",
        "refresh_trigger": str(refresh_trigger),
        "refresh_cadence_sec": int(assessment.get("refresh_cadence_sec") or facade._OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC),
        "refresh_summary": summary,
        "selected_symbol": selected_symbol,
        "open_position_count": len(positions),
        "hold_repeat_count_max": int(assessment.get("hold_repeat_count_max") or 0),
        "selected_hold_repeat_count": selected_hold_repeat_count,
        "selected_effective_loss_ratio": selected_position.get("effective_loss_ratio"),
        "effective_loss_ratio_min": assessment.get("effective_loss_ratio_min"),
        "price_anomaly_flag": bool(assessment.get("price_anomaly_flag")),
        "force_exit_review_pending": bool(assessment.get("force_exit_review_pending")),
        "open_position_risk_review_reason": str(assessment.get("open_position_risk_review_reason") or ""),
        "monitor_posture": str(selected_position.get("posture") or ""),
        "monitor_reason": str(selected_position.get("reason") or ""),
        "active_exit_axis": str(selected_position.get("active_exit_axis") or ""),
        "position_qty": int(selected_position.get("qty") or 0),
        "position_age_seconds": selected_position.get("position_age_seconds"),
        "position_horizon_state": dict(selected_position.get("position_horizon_state") or {}),
        "carry_state": carry_state,
        "carry_risk_bias": carry_risk_bias,
        "carry_risk_reason": carry_risk_reason,
        "session_open_recovery_assessment": dict(session_open_recovery_assessment),
        "entry_state": dict(entry_state),
        "reason_chain": [str(x) for x in list(assessment.get("reason_chain") or []) if str(x or "").strip()][:8],
    }


def _compact_monitor_entry_state_for_refresh_r3_impl(entry_state, *, facade):
    raw = dict(entry_state or {}) if isinstance(entry_state, dict) else {}
    blockers = [str(x) for x in list(raw.get("entry_blockers") or []) if str(x or "").strip()]
    return {
        "triggered": bool(raw.get("triggered")),
        "current_blocking_axis": str(raw.get("current_blocking_axis") or ""),
        "transition_readiness_score": raw.get("transition_readiness_score"),
        "entry_blockers": blockers[:6],
        "reclaim_distance_to_ready": raw.get("reclaim_distance_to_ready"),
        "volume_distance_to_ready": raw.get("volume_distance_to_ready"),
        "breakout_distance_to_ready": raw.get("breakout_distance_to_ready"),
        "vwap_reclaim_progress": raw.get("vwap_reclaim_progress"),
        "rebound_progress": raw.get("rebound_progress"),
        "volume_ratio": raw.get("volume_ratio"),
        "extended_from_vwap_pct": raw.get("extended_from_vwap_pct"),
        "breakout_gap_pct": raw.get("breakout_gap_pct"),
        "reclaim_gate_ok": bool(raw.get("reclaim_gate_ok")),
        "volume_ok": bool(raw.get("volume_ok")),
        "breakout_ok": bool(raw.get("breakout_ok")),
        "confidence_gate_ok": bool(raw.get("confidence_gate_ok")),
    }


def _summarize_monitor_entry_policy_r3_impl(policy, *, facade):
    row = dict(policy or {}) if isinstance(policy, dict) else {}
    keys = (
        "timeframe_minutes",
        "breakout_lookback",
        "volume_lookback",
        "volume_ratio_min",
        "min_extended_from_vwap_pct",
        "max_extended_from_vwap_pct",
        "pullback_min_pct",
        "pullback_max_pct",
        "reclaim_tolerance_pct",
        "breakout_buffer_pct",
        "intent_cooldown_sec",
        "require_vwap_reclaim",
        "require_rebound",
        "policy_source",
    )
    return {key: row.get(key) for key in keys if key in row}


def _monitor_entry_policy_delta_fields_r3_impl(previous, current, *, facade):
    before = dict(previous or {}) if isinstance(previous, dict) else {}
    after = dict(current or {}) if isinstance(current, dict) else {}
    ordered_keys: list[str] = []
    for key in list(before.keys()) + list(after.keys()):
        text = str(key or "").strip()
        if text and text not in ordered_keys:
            ordered_keys.append(text)
    return [key for key in ordered_keys if before.get(key) != after.get(key)]


def _summarize_monitor_entry_policy_from_strategist_output_r3_impl(strategist_output, *, facade):
    row = dict(strategist_output or {}) if isinstance(strategist_output, dict) else {}
    if not row:
        return {}
    temp_state = {"strategist_output": dict(row)}
    applied = dict((facade._resolve_commander_applied_policy(temp_state) or {}).get("applied_policy") or {})
    return facade._summarize_monitor_entry_policy(applied)
