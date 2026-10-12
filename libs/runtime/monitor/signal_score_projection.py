"""Intraday entry-signal score components and caps (pure projections of features).

Second Pass (P1.5) intra-function extraction from `libs/runtime/intraday_monitor_signals.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def signal_score_entry_condition_path_entry_condition_pat(volume_ratio, volume_ratio_raw, average_volume, median_volume, extended_from_vwap_pct, min_extended_from_vwap_pct, max_extended_from_vwap_pct, pullback_depth_pct, pullback_min_pct, pullback_max_pct, breakout_gap_pct, breakout_buffer_pct, open_gap_pct, prev_close_distance_pct, minutes_since_session_open, etf_deviation_pct, etf_deviation_source, asset_class_detected, market_regime, volume_confirmation, opening_gap_chase_observed, volume_ok, breakout_chase_extension_observed, etf_deviation_entry_path_ok, inverse_hedge_volume_ok, inverse_hedge_confidence_ok, inverse_hedge_reclaim_path_ok, lower_rebound_higher_lows, lower_rebound_volume_ok, rebound_ok, lower_vwap_rebound_probe_path_ok, resolved_policy, breakout_level, current_close, etf_deviation_entry_score, confidence_score, breakout_path_ok, pullback_volume_path_ok, *, facade):
    threshold_margins = {
        "volume_ratio": {
            "actual": volume_ratio,
            "raw": volume_ratio_raw,
            "effective": volume_ratio,
            "min": facade._to_float(resolved_policy.volume_ratio_min),
            "distance_to_min": volume_ratio - facade._to_float(resolved_policy.volume_ratio_min),
            "adjusted": bool(volume_confirmation.adjusted),
            "adjustment_reason": volume_confirmation.adjustment_reason,
            "average_volume": average_volume,
            "median_volume": median_volume,
            "max_reference_volume": float(volume_confirmation.max_reference_volume),
            "spike_skew_ratio": float(volume_confirmation.spike_skew_ratio),
        },
        "extended_from_vwap_pct": {
            "actual": extended_from_vwap_pct,
            "min": min_extended_from_vwap_pct,
            "max": max_extended_from_vwap_pct,
            "distance_to_min": extended_from_vwap_pct - min_extended_from_vwap_pct,
            "distance_to_max": max_extended_from_vwap_pct - extended_from_vwap_pct,
        },
        "pullback_depth_pct": {
            "actual": pullback_depth_pct,
            "min": pullback_min_pct,
            "max": pullback_max_pct,
            "distance_to_min": pullback_depth_pct - pullback_min_pct,
            "distance_to_max": pullback_max_pct - pullback_depth_pct,
        },
        "breakout_gap_pct": {
            "actual": breakout_gap_pct,
            "min": breakout_buffer_pct,
            "distance_to_breakout": (current_close - breakout_level) if breakout_level > 0.0 else None,
        },
        "opening_gap_chase": {
            "open_gap_pct": open_gap_pct,
            "prev_close_distance_pct": prev_close_distance_pct,
            "min_open_gap_pct": facade._OPENING_GAP_CHASE_MIN_PCT,
            "minutes_since_session_open": minutes_since_session_open,
            "window_minutes": facade._OPENING_GAP_CHASE_WINDOW_MINUTES,
            "observed": bool(opening_gap_chase_observed),
            "observation_only": True,
            "volume_gate_required": False,
            "volume_ok": bool(volume_ok),
        },
        "breakout_chase_extension": {
            "actual": extended_from_vwap_pct,
            "min_without_volume": facade._BREAKOUT_CHASE_VOLUME_GATE_MIN_EXTENDED_PCT,
            "observed": bool(breakout_chase_extension_observed),
            "observation_only": True,
            "volume_gate_required": False,
            "volume_ok": bool(volume_ok),
        },
        "etf_deviation_pct": {
            "actual": etf_deviation_pct,
            "discount_trigger_pct": -0.30,
            "entry_score": round(float(etf_deviation_entry_score), 4),
            "source": etf_deviation_source,
            "asset_class_detected": asset_class_detected,
            "path_ok": bool(etf_deviation_entry_path_ok),
        },
        "inverse_hedge_reclaim": {
            "asset_class_detected": asset_class_detected,
            "market_regime": market_regime,
            "volume_ok": bool(inverse_hedge_volume_ok),
            "confidence_ok": bool(inverse_hedge_confidence_ok),
            "path_ok": bool(inverse_hedge_reclaim_path_ok),
        },
        "lower_vwap_rebound_probe": {
            "vwap_distance": extended_from_vwap_pct,
            "min_distance_pct": facade._LOWER_VWAP_REBOUND_MIN_DISTANCE_PCT,
            "max_distance_pct": facade._LOWER_VWAP_REBOUND_MAX_DISTANCE_PCT,
            "higher_lows": bool(lower_rebound_higher_lows),
            "volume_ok": bool(lower_rebound_volume_ok),
            "rebound_ok": bool(rebound_ok),
            "confidence_ok": bool(confidence_score >= facade._LOWER_VWAP_REBOUND_MIN_CONFIDENCE),
            "path_ok": bool(lower_vwap_rebound_probe_path_ok),
        },
    }

    pattern = ""
    reason = ""
    triggered = False
    primary_failure_axis = ""
    entry_condition_path = ""
    entry_condition_paths_passed: facade.List[str] = []
    if breakout_path_ok:
        entry_condition_paths_passed.append("breakout_path")
    if pullback_volume_path_ok:
        entry_condition_paths_passed.append("pullback_volume_path")
    if etf_deviation_entry_path_ok:
        entry_condition_paths_passed.append("etf_discount_reversion_path")
    if inverse_hedge_reclaim_path_ok:
        entry_condition_paths_passed.append("inverse_hedge_reclaim_path")
    if lower_vwap_rebound_probe_path_ok:
        entry_condition_paths_passed.append("lower_vwap_rebound_probe_path")
    return (entry_condition_path, entry_condition_paths_passed, pattern, primary_failure_axis, reason, threshold_margins, triggered)


def signal_score_entry_condition_path_entry_hard_gate_blo(etf_deviation_pct, etf_deviation_source, asset_class_detected, reclaim_gate_ok, breakout_volume_gate_required, breakout_volume_gate_ok, opening_gap_chase_observed, breakout_chase_extension_observed, extension_ok, breakout_path_ok, pullback_volume_path_ok, etf_deviation_discount_entry_ok, etf_deviation_chart_ok, etf_deviation_entry_path_ok, inverse_hedge_reclaim_path_ok, lower_vwap_rebound_probe_path_ok, entry_condition_paths_passed, confidence_gate_ok, resolved_policy, volume_confirmation, threshold_margins, playbook, extended_from_vwap_pct, max_extended_from_vwap_pct, volume_ok, vwap_hold_ok, rebound_ok, vwap_reclaim_ok, pullback_ok, pullback_mature, pullback_not_too_deep, breakout_ok, triggered, primary_failure_axis, failed_checks, relevant_checks, entry_quality_score, entry_condition_path, pattern, *, facade):
    grouped_logic_trace = {
        "logic_mode": "reclaim_and_grouped_paths_v1",
        "reclaim_gate_required": bool(resolved_policy.require_vwap_reclaim),
        "reclaim_gate_ok": bool(reclaim_gate_ok),
        "breakout_volume_gate_required": bool(breakout_volume_gate_required),
        "breakout_volume_gate_ok": bool(breakout_volume_gate_ok),
        "opening_gap_chase_observed": bool(opening_gap_chase_observed),
        "breakout_chase_extension_observed": bool(breakout_chase_extension_observed),
        "opening_gap_context_observation_only": True,
        "opening_gap_chase_window_minutes": facade._OPENING_GAP_CHASE_WINDOW_MINUTES,
        "opening_gap_chase_min_pct": facade._OPENING_GAP_CHASE_MIN_PCT,
        "breakout_chase_volume_gate_min_extended_from_vwap_pct": facade._BREAKOUT_CHASE_VOLUME_GATE_MIN_EXTENDED_PCT,
        "volume_confirmation": volume_confirmation.to_metrics(),
        "extension_required": True,
        "extension_ok": bool(extension_ok),
        "breakout_path_ok": bool(breakout_path_ok),
        "pullback_volume_path_ok": bool(pullback_volume_path_ok),
        "etf_deviation_pct": etf_deviation_pct,
        "etf_deviation_source": etf_deviation_source,
        "asset_class_detected": asset_class_detected,
        "etf_deviation_discount_entry_ok": bool(etf_deviation_discount_entry_ok),
        "etf_deviation_chart_ok": bool(etf_deviation_chart_ok),
        "etf_deviation_entry_path_ok": bool(etf_deviation_entry_path_ok),
        "inverse_hedge_reclaim_path_ok": bool(inverse_hedge_reclaim_path_ok),
        "lower_vwap_rebound_probe_path_ok": bool(lower_vwap_rebound_probe_path_ok),
        "lower_vwap_rebound_probe": dict(threshold_margins.get("lower_vwap_rebound_probe") or {}),
        "paths_passed": list(entry_condition_paths_passed),
        "confidence_gate_ok": bool(confidence_gate_ok),
        "triggered_path": "",
    }
    if playbook in ("pullback", "reversal"):
        if reclaim_gate_ok and extension_ok and confidence_gate_ok and (breakout_path_ok or pullback_volume_path_ok):
            if breakout_path_ok and not pullback_volume_path_ok and not breakout_volume_gate_ok:
                triggered = False
                entry_condition_path = ""
                pattern = ""
                reason = "volume_confirmation_missing"
                primary_failure_axis = "volume_confirmation"
            else:
                triggered = True
                if breakout_path_ok:
                    entry_condition_path = "breakout_path"
                    pattern = "breakout_vwap_hold"
                    if vwap_reclaim_ok and not vwap_hold_ok:
                        reason = "breakout_above_recent_high_with_vwap_reclaim_confirmation"
                    elif volume_ok and vwap_hold_ok:
                        reason = "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation"
                    else:
                        reason = "breakout_above_recent_high_with_vwap_structure_confirmation"
                elif vwap_reclaim_ok and rebound_ok:
                    entry_condition_path = "pullback_volume_path"
                    pattern = "pullback_vwap_reclaim"
                    reason = "pullback_reclaim_above_vwap_with_rebound_confirmation"
                elif rebound_ok:
                    entry_condition_path = "pullback_volume_path"
                    pattern = "pullback_rebound"
                    reason = "pullback_rebound_above_vwap_with_confirmation"
                else:
                    entry_condition_path = "pullback_volume_path"
                    pattern = "pullback_vwap_hold"
                    reason = "pullback_structure_above_vwap_with_volume_confirmation"
        else:
            if not extension_ok:
                if extended_from_vwap_pct > max_extended_from_vwap_pct:
                    reason = "still_overextended_after_pullback"
                    primary_failure_axis = "overextension"
                else:
                    # Pullback setup is still too weak below VWAP band; wait for reclaim/structure.
                    reason = "pullback_below_vwap_reclaim_not_ready"
                    primary_failure_axis = "vwap_relationship"
            elif not reclaim_gate_ok:
                reason = "below_vwap_reclaim_not_ready"
                primary_failure_axis = "vwap_relationship"
            elif not breakout_volume_gate_ok and breakout_path_ok:
                reason = "volume_confirmation_missing"
                primary_failure_axis = "volume_confirmation"
            elif not pullback_mature:
                reason = "pullback_not_mature"
                primary_failure_axis = "pullback_structure"
            elif not pullback_not_too_deep:
                reason = "no_valid_pullback_structure"
                primary_failure_axis = "pullback_structure"
            elif pullback_ok and not volume_ok:
                reason = "volume_confirmation_missing"
                primary_failure_axis = "volume_confirmation"
            elif not breakout_ok:
                reason = "breakout_not_ready"
                primary_failure_axis = "breakout_readiness"
            else:
                reason = "entry_signal_not_confirmed"
                primary_failure_axis = "entry_confirmation"
    else:
        if reclaim_gate_ok and extension_ok and confidence_gate_ok and (breakout_path_ok or pullback_volume_path_ok):
            triggered = True
            if breakout_path_ok:
                entry_condition_path = "breakout_path"
                pattern = "breakout_vwap_hold"
                if volume_ok and vwap_hold_ok:
                    reason = "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation"
                elif vwap_reclaim_ok and not vwap_hold_ok:
                    reason = "breakout_above_recent_high_with_vwap_reclaim_confirmation"
                else:
                    reason = "breakout_above_recent_high_with_vwap_structure_confirmation"
            else:
                entry_condition_path = "pullback_volume_path"
                pattern = "pullback_rebound" if rebound_ok else "pullback_vwap_hold"
                reason = (
                    "pullback_rebound_above_vwap_with_volume_confirmation"
                    if rebound_ok
                    else "pullback_structure_above_vwap_with_volume_confirmation"
                )
        else:
            if not extension_ok:
                if extended_from_vwap_pct > max_extended_from_vwap_pct:
                    reason = "too_extended_from_vwap"
                    primary_failure_axis = "overextension"
                else:
                    reason = "below_vwap_reclaim_not_ready"
                    primary_failure_axis = "vwap_relationship"
            elif not reclaim_gate_ok:
                reason = "below_vwap_reclaim_not_ready"
                primary_failure_axis = "vwap_relationship"
            elif pullback_ok and not volume_ok:
                reason = "volume_insufficient"
                primary_failure_axis = "volume_confirmation"
            elif not breakout_ok and not pullback_ok:
                reason = "breakout_not_ready"
                primary_failure_axis = "breakout_readiness"
            elif not pullback_ok:
                reason = "pullback_too_deep"
                primary_failure_axis = "pullback_structure"
            elif not breakout_ok:
                reason = "breakout_not_ready"
                primary_failure_axis = "breakout_readiness"
            else:
                reason = "entry_signal_not_confirmed"
                primary_failure_axis = "entry_confirmation"

    if not triggered and etf_deviation_entry_path_ok:
        triggered = True
        entry_condition_path = "etf_discount_reversion_path"
        pattern = "etf_discount_reversion"
        reason = "etf_discount_reversion_entry"
        primary_failure_axis = "confirmed_entry"
    if not triggered and inverse_hedge_reclaim_path_ok:
        triggered = True
        entry_condition_path = "inverse_hedge_reclaim_path"
        pattern = "inverse_hedge_reclaim"
        reason = "inverse_hedge_reclaim_entry"
        primary_failure_axis = "confirmed_entry"
    if not triggered and lower_vwap_rebound_probe_path_ok:
        triggered = True
        entry_condition_path = "lower_vwap_rebound_probe_path"
        pattern = "lower_vwap_rebound_probe"
        reason = "lower_vwap_rebound_probe_entry"
        primary_failure_axis = "confirmed_entry"

    if triggered and not primary_failure_axis:
        primary_failure_axis = "confirmed_entry"

    entry_hard_gate_blockers = [name for name in failed_checks if name in relevant_checks]
    entry_quality_tier = facade._entry_quality_tier(entry_quality_score)
    entry_hard_gate_passed = bool(triggered)
    entry_quality_vs_gate_summary = ""
    return (entry_condition_path, entry_hard_gate_blockers, entry_hard_gate_passed, entry_quality_tier, entry_quality_vs_gate_summary, grouped_logic_trace, pattern, primary_failure_axis, reason, triggered)


def signal_score_chart_structure_features_legacy_decision(entry_condition_path, grouped_logic_trace, triggered, reason, pattern, candles, current_close, current_vwap, recent_high, breakout_ok, pullback_ok, vwap_reclaim_ok, volume_ok, confidence_gate_ok, volume_ratio, extension_ok, extended_from_vwap_pct, max_extended_from_vwap_pct, pullback_mature, *, facade):
    grouped_logic_trace["triggered_path"] = entry_condition_path
    legacy_triggered = bool(triggered)
    legacy_decision = "BUY" if legacy_triggered else "WAIT"
    legacy_reason = str(reason or "")
    legacy_pattern = str(pattern or "")
    legacy_entry_condition_path = str(entry_condition_path or "")
    chart_structure_features = facade.build_chart_structure_features(
        candles,
        current_price=current_close,
        current_vwap=current_vwap,
        recent_high=recent_high,
        breakout_ok=breakout_ok,
        pullback_ok=pullback_ok,
        reclaim_ok=vwap_reclaim_ok,
        volume_ok=volume_ok,
        confidence_ok=confidence_gate_ok,
        volume_ratio=volume_ratio,
        too_extended=bool(not extension_ok and extended_from_vwap_pct > max_extended_from_vwap_pct),
    )
    score_breakdown = facade._build_monitor_score_breakdown(
        vwap_reclaim_ok=bool(vwap_reclaim_ok),
        breakout_ok=bool(breakout_ok),
        pullback_mature=bool(pullback_mature),
        volume_ok=bool(volume_ok),
        confidence_gate_ok=bool(confidence_gate_ok),
        chart_structure_features=chart_structure_features,
    )
    return (chart_structure_features, legacy_decision, legacy_entry_condition_path, legacy_pattern, legacy_reason, legacy_triggered, score_breakdown)
