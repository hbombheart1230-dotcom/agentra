"""Intraday entry-signal feature facts (price/volume/structure features before scoring).

Second Pass (P1.5) intra-function extraction from `libs/runtime/intraday_monitor_signals.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


def signal_feature_candles_out(policy, frame, scoring, rows, policy_contract, *, facade):
    resolved_policy = (
        policy
        if isinstance(policy, facade.MonitorEntryPolicy)
        else facade.resolve_intraday_entry_policy(policy, frame=frame)
    )
    applied_policy = resolved_policy.to_dict()
    scoring_settings = facade._resolve_monitor_scoring_settings(scoring)
    timeframe_minutes = int(resolved_policy.timeframe_minutes or 1)
    candles = facade._compress_candles(rows or [], timeframe_minutes)
    out: facade.Dict[str, facade.Any] = {
        "enabled": bool(resolved_policy.enabled),
        "evaluated": False,
        "triggered": False,
        "decision": "WAIT",
        "reason": "",
        "pattern": "",
        "signal_chain": [],
        "metrics": {},
        "thresholds": dict(applied_policy),
        "applied_policy": dict(applied_policy),
    }
    out.update(facade._empty_entry_transition_trace())
    out["entry_transition_trace"] = facade._empty_entry_transition_trace()
    out["signal_evidence"] = facade._empty_monitor_signal_evidence(
        score_threshold=float(scoring_settings.get("entry_threshold") or 3.0)
    )
    out["chart_structure_features"] = facade.empty_chart_structure_features()
    out["policy_interpretation"] = facade._build_monitor_policy_interpretation(
        received_policy=policy if isinstance(policy, (facade.Mapping, facade.MonitorEntryPolicy)) else None,
        effective_policy=resolved_policy,
        frame=frame,
        policy_contract=policy_contract,
    )
    out["policy_interpreter_trace"] = facade._empty_monitor_policy_interpreter_trace()
    out["policy_alignment_summary"] = facade._empty_monitor_policy_alignment_summary()
    out["policy_aware_gating"] = facade._empty_monitor_policy_aware_gating()
    out["chart_structure_decision_hint"] = facade._empty_chart_structure_decision_hint()
    out["human_chart_detail_context"] = facade._empty_human_chart_detail_context()
    out["human_chart_entry_setup"] = facade._empty_human_chart_entry_setup()
    return (candles, out, resolved_policy, scoring_settings, timeframe_minutes)


class BreakoutLevelFeatures(NamedTuple):
    """Result of `breakout_level_features` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    breakout_buffer_pct: Any
    breakout_level: Any
    breakout_ok: Any
    current_close: Any
    current_high: Any
    current_low: Any
    current_volume: Any
    current_vwap: Any
    extended_from_vwap_pct: Any
    minutes_since_session_open: Any
    open_gap_pct: Any
    prev_close_distance_pct: Any
    prior_bar_high: Any
    prior_bar_low: Any
    prior_close: Any
    pullback_depth_pct: Any
    rebound_ok: Any
    recent_high: Any
    reclaim_tolerance_pct: Any
    session_gap_context: Any
    volume_confirmation: Any
    volume_ratio_raw: Any
    vwap_hold_ok: Any
    vwap_reclaim_ok: Any


def breakout_level_features(out, candles, resolved_policy, current_price, *, facade):
    out["evaluated"] = True
    last = candles[-1]
    prior = candles[-2]
    lookback = int(resolved_policy.breakout_lookback or 5)
    volume_lookback = int(resolved_policy.volume_lookback or 5)
    breakout_window = candles[-(lookback + 1):-1]
    volume_window = candles[-(volume_lookback + 1):-1]
    recent_high = max(facade._to_float(row.get("high")) for row in breakout_window)
    prior_bar_high = facade._to_float(prior.get("high"))
    prior_bar_low = facade._to_float(prior.get("low"))
    current_close = facade._to_float(current_price, facade._to_float(last.get("close")))
    current_high = facade._to_float(last.get("high"))
    current_low = facade._to_float(last.get("low"))
    current_volume = max(0.0, facade._to_float(last.get("volume")))

    current_vwap = facade._to_float(last.get("vwap"))
    if current_vwap <= 0.0:
        current_vwap = facade._to_float(facade._session_vwap(candles), 0.0)
    previous_vwap = facade._to_float(prior.get("vwap"))
    if previous_vwap <= 0.0:
        previous_vwap = current_vwap

    extended_from_vwap_pct = 0.0
    if current_vwap > 0.0 and current_close > 0.0:
        extended_from_vwap_pct = (current_close / current_vwap) - 1.0

    prior_close = facade._to_float(prior.get("close"))
    reclaim_tolerance_pct = facade._to_float(resolved_policy.reclaim_tolerance_pct)
    breakout_buffer_pct = facade._to_float(resolved_policy.breakout_buffer_pct)
    breakout_level = recent_high * (1.0 + breakout_buffer_pct) if recent_high > 0.0 else 0.0
    breakout_ok = breakout_level > 0.0 and current_close >= breakout_level and current_high >= recent_high
    vwap_hold_ok = current_vwap > 0.0 and current_close >= current_vwap * (1.0 - reclaim_tolerance_pct)
    vwap_reclaim_ok = (
        current_vwap > 0.0
        and prior_close < previous_vwap * (1.0 - reclaim_tolerance_pct)
        and current_close >= current_vwap * (1.0 - reclaim_tolerance_pct)
    )
    pullback_lows = [max(0.0, facade._to_float(row.get("low"))) for row in candles[-4:-1]]
    pullback_floor = min([px for px in pullback_lows if px > 0.0], default=0.0)
    pullback_depth_pct = ((recent_high - pullback_floor) / recent_high) if recent_high > 0.0 and pullback_floor > 0.0 else 0.0
    rebound_ok = current_close > prior_bar_high and current_close >= prior_close
    session_gap_context = facade._session_gap_context(candles, current_close)
    minutes_since_session_open = session_gap_context.get("minutes_since_session_open")
    open_gap_pct = session_gap_context.get("open_gap_pct")
    prev_close_distance_pct = session_gap_context.get("prev_close_distance_pct")
    volume_confirmation = facade.evaluate_intraday_volume_confirmation(
        current_volume=current_volume,
        reference_candles=volume_window,
        threshold=facade._to_float(resolved_policy.volume_ratio_min),
        minutes_since_session_open=minutes_since_session_open,
    )
    volume_ratio_raw = float(volume_confirmation.raw_ratio)
    return BreakoutLevelFeatures(breakout_buffer_pct, breakout_level, breakout_ok, current_close, current_high, current_low, current_volume, current_vwap, extended_from_vwap_pct, minutes_since_session_open, open_gap_pct, prev_close_distance_pct, prior_bar_high, prior_bar_low, prior_close, pullback_depth_pct, rebound_ok, recent_high, reclaim_tolerance_pct, session_gap_context, volume_confirmation, volume_ratio_raw, vwap_hold_ok, vwap_reclaim_ok)


def signal_feature_average_volume_breakout_chase_extension(volume_confirmation, resolved_policy, extended_from_vwap_pct, pullback_depth_pct, vwap_hold_ok, vwap_reclaim_ok, rebound_ok, breakout_ok, minutes_since_session_open, open_gap_pct, prev_close_distance_pct, session_gap_context, current_close, breakout_level, *, facade):
    volume_ratio = float(volume_confirmation.effective_ratio)
    average_volume = float(volume_confirmation.average_volume)
    median_volume = float(volume_confirmation.median_volume)
    volume_ok = bool(volume_confirmation.passed)
    min_extended_from_vwap_pct = facade._to_float(resolved_policy.min_extended_from_vwap_pct)
    max_extended_from_vwap_pct = facade._to_float(resolved_policy.max_extended_from_vwap_pct)
    extension_ok = min_extended_from_vwap_pct <= extended_from_vwap_pct <= max_extended_from_vwap_pct
    pullback_min_pct = facade._to_float(resolved_policy.pullback_min_pct)
    pullback_max_pct = facade._to_float(resolved_policy.pullback_max_pct)
    pullback_mature = pullback_depth_pct >= pullback_min_pct
    pullback_not_too_deep = pullback_depth_pct <= pullback_max_pct
    pullback_ok = pullback_mature and pullback_not_too_deep
    vwap_structure_ok = vwap_hold_ok or vwap_reclaim_ok
    confirmation_ok = volume_ok or rebound_ok or vwap_reclaim_ok
    reclaim_gate_ok = bool(vwap_structure_ok) if bool(resolved_policy.require_vwap_reclaim) else True
    breakout_path_ok = bool(breakout_ok)
    pullback_volume_path_ok = bool(pullback_ok and volume_ok)
    opening_gap_chase_observed = bool(
        breakout_path_ok
        and not pullback_volume_path_ok
        and not volume_ok
        and bool(session_gap_context.get("session_context_available"))
        and minutes_since_session_open is not None
        and 0.0 <= facade._to_float(minutes_since_session_open) <= facade._OPENING_GAP_CHASE_WINDOW_MINUTES
        and open_gap_pct is not None
        and facade._to_float(open_gap_pct) >= facade._OPENING_GAP_CHASE_MIN_PCT
        and prev_close_distance_pct is not None
        and facade._to_float(prev_close_distance_pct) >= facade._to_float(open_gap_pct)
    )
    breakout_chase_extension_observed = bool(
        breakout_path_ok
        and not pullback_volume_path_ok
        and not volume_ok
        and extended_from_vwap_pct >= facade._BREAKOUT_CHASE_VOLUME_GATE_MIN_EXTENDED_PCT
    )
    breakout_volume_gate_required = False
    breakout_volume_gate_ok = True
    breakout_score = 1.0 if breakout_ok else facade._clamp_score((current_close / breakout_level) if breakout_level > 0.0 and current_close > 0.0 else 0.0)
    volume_score = facade._min_threshold_score(volume_ratio, facade._to_float(resolved_policy.volume_ratio_min))
    pullback_score = min(
        facade._min_threshold_score(pullback_depth_pct, pullback_min_pct if pullback_min_pct > 0.0 else 1e-9),
        facade._range_threshold_score(pullback_depth_pct, 0.0, pullback_max_pct if pullback_max_pct > 0.0 else max(pullback_depth_pct, 1e-9)),
    )
    return (average_volume, breakout_chase_extension_observed, breakout_path_ok, breakout_score, breakout_volume_gate_ok, breakout_volume_gate_required, confirmation_ok, extension_ok, max_extended_from_vwap_pct, median_volume, min_extended_from_vwap_pct, opening_gap_chase_observed, pullback_mature, pullback_max_pct, pullback_min_pct, pullback_not_too_deep, pullback_ok, pullback_score, pullback_volume_path_ok, reclaim_gate_ok, volume_ok, volume_ratio, volume_score, vwap_structure_ok)


def signal_feature_asset_class_detected_breakout_distance_t(breakout_score, pullback_score, volume_score, recent_high, current_close, reclaim_tolerance_pct, extended_from_vwap_pct, current_vwap, min_extended_from_vwap_pct, prior_bar_high, prior_close, max_extended_from_vwap_pct, vwap_hold_ok, vwap_reclaim_ok, volume_ratio, resolved_policy, breakout_buffer_pct, features, *, facade):
    breakout_path_score = round(0.55 * breakout_score, 4)
    pullback_volume_path_score = round((0.30 * pullback_score) + (0.25 * volume_score), 4)
    confidence_threshold = 0.55
    confidence_score = round(max(breakout_path_score, pullback_volume_path_score), 4)
    confidence_gate_ok = confidence_score >= confidence_threshold
    breakout_gap_pct = ((current_close / recent_high) - 1.0) if recent_high > 0.0 and current_close > 0.0 else None
    reclaim_ready_level_pct = -reclaim_tolerance_pct
    reclaim_distance_to_ready = (
        extended_from_vwap_pct - reclaim_ready_level_pct
        if current_vwap > 0.0 and current_close > 0.0
        else None
    )
    reclaim_progress_band = max(1e-6, abs(reclaim_ready_level_pct - min_extended_from_vwap_pct))
    vwap_reclaim_progress = facade._clamp_score(
        (extended_from_vwap_pct - min_extended_from_vwap_pct) / reclaim_progress_band
    )
    rebound_high_progress = facade._clamp_score((current_close / prior_bar_high) if prior_bar_high > 0.0 and current_close > 0.0 else 0.0)
    rebound_close_progress = facade._clamp_score((current_close / prior_close) if prior_close > 0.0 and current_close > 0.0 else 0.0)
    rebound_progress = round(min(rebound_high_progress, rebound_close_progress), 4)
    extension_score = facade._range_threshold_score(
        extended_from_vwap_pct,
        min_extended_from_vwap_pct,
        max_extended_from_vwap_pct,
    )
    vwap_structure_score = max(
        1.0 if bool(vwap_hold_ok) else 0.0,
        1.0 if bool(vwap_reclaim_ok) else 0.0,
    )
    confirmation_score = max(volume_score, rebound_progress)
    breakout_quality_score = round(
        facade._clamp_score(
            (0.35 * breakout_score)
            + (0.20 * volume_score)
            + (0.20 * vwap_structure_score)
            + (0.15 * extension_score)
            + (0.10 * confirmation_score)
        ),
        4,
    )
    pullback_quality_score = round(
        facade._clamp_score(
            (0.30 * pullback_score)
            + (0.25 * volume_score)
            + (0.20 * vwap_structure_score)
            + (0.15 * confirmation_score)
            + (0.10 * extension_score)
        ),
        4,
    )
    entry_quality_score = round(max(breakout_quality_score, pullback_quality_score), 4)
    entry_quality_path = "breakout_path" if breakout_quality_score >= pullback_quality_score else "pullback_volume_path"
    volume_distance_to_ready = volume_ratio - facade._to_float(resolved_policy.volume_ratio_min)
    breakout_distance_to_ready = (
        breakout_gap_pct - breakout_buffer_pct
        if breakout_gap_pct is not None
        else None
    )
    transition_readiness_score = round(
        facade._clamp_score(
            (0.35 * vwap_reclaim_progress)
            + (0.25 * volume_score)
            + (0.20 * breakout_score)
            + (0.20 * rebound_progress)
        ),
        4,
    )
    feature_payload = features if isinstance(features, facade.Mapping) else {}
    etf_deviation_pct = facade.normalize_deviation_pct(feature_payload.get("etf_deviation_pct"))
    etf_deviation_source = str(feature_payload.get("etf_deviation_source") or "")
    asset_class_detected = str(
        feature_payload.get("asset_class_detected")
        or feature_payload.get("asset_class")
        or feature_payload.get("asset_type")
        or ""
    ).strip().lower()
    return (asset_class_detected, breakout_distance_to_ready, breakout_gap_pct, breakout_path_score, breakout_quality_score, confidence_gate_ok, confidence_score, confidence_threshold, confirmation_score, entry_quality_path, entry_quality_score, etf_deviation_pct, etf_deviation_source, extension_score, pullback_quality_score, pullback_volume_path_score, rebound_progress, reclaim_distance_to_ready, transition_readiness_score, volume_distance_to_ready, vwap_reclaim_progress, vwap_structure_score)


def signal_feature_etf_deviation_chart_ok_etf_deviation_dis(etf_deviation_tradeable, etf_deviation_pct, reclaim_gate_ok, extension_ok, confirmation_ok, frame, asset_class_detected, volume_ratio, resolved_policy, confidence_threshold, confidence_score, rebound_ok, vwap_reclaim_ok, candles, current_vwap, extended_from_vwap_pct, breakout_path_ok, *, facade):
    etf_deviation_entry_score = (
        facade.score_etf_deviation_for_entry(etf_deviation_pct)
        if etf_deviation_tradeable
        else 0.0
    )
    etf_deviation_discount_entry_ok = bool(etf_deviation_tradeable and etf_deviation_entry_score > 0.0)
    etf_deviation_chart_ok = bool(reclaim_gate_ok and extension_ok and confirmation_ok)
    etf_deviation_entry_path_ok = bool(etf_deviation_discount_entry_ok and etf_deviation_chart_ok)
    market_regime = str((frame or {}).get("market_regime") or "").strip().lower()
    inverse_hedge_asset = asset_class_detected in {"inverse_etf", "leveraged_etf", "futures_etf"}
    inverse_hedge_volume_ok = volume_ratio >= min(0.75, max(0.65, facade._to_float(resolved_policy.volume_ratio_min) * 0.85))
    inverse_hedge_confidence_ok = confidence_score + 0.025 >= confidence_threshold
    inverse_hedge_reclaim_path_ok = bool(
        inverse_hedge_asset
        and market_regime == "risk_off"
        and reclaim_gate_ok
        and extension_ok
        and inverse_hedge_confidence_ok
        and (inverse_hedge_volume_ok or rebound_ok or vwap_reclaim_ok)
    )
    lower_probe_lows = [
        max(0.0, facade._to_float(row.get("low")))
        for row in candles[-3:]
        if max(0.0, facade._to_float(row.get("low"))) > 0.0
    ]
    lower_rebound_higher_lows = bool(
        len(lower_probe_lows) >= 3
        and lower_probe_lows[-1] >= lower_probe_lows[-2] >= lower_probe_lows[-3]
    )
    lower_rebound_volume_ok = volume_ratio >= min(
        0.85,
        max(0.65, facade._to_float(resolved_policy.volume_ratio_min) * 0.85),
    )
    lower_rebound_vwap_band_ok = bool(
        current_vwap > 0.0
        and facade._LOWER_VWAP_REBOUND_MIN_DISTANCE_PCT <= extended_from_vwap_pct < facade._LOWER_VWAP_REBOUND_MAX_DISTANCE_PCT
    )
    lower_vwap_rebound_probe_path_ok = bool(
        not reclaim_gate_ok
        and not breakout_path_ok
        and lower_rebound_vwap_band_ok
        and extension_ok
        and rebound_ok
        and lower_rebound_higher_lows
        and lower_rebound_volume_ok
        and confidence_score >= facade._LOWER_VWAP_REBOUND_MIN_CONFIDENCE
    )
    return (etf_deviation_chart_ok, etf_deviation_discount_entry_ok, etf_deviation_entry_path_ok, etf_deviation_entry_score, inverse_hedge_confidence_ok, inverse_hedge_reclaim_path_ok, inverse_hedge_volume_ok, lower_rebound_higher_lows, lower_rebound_volume_ok, lower_rebound_vwap_band_ok, lower_vwap_rebound_probe_path_ok, market_regime)


def signal_feature_effect_free_block_2745(out, timeframe_minutes, pullback_depth_pct, candles, current_close, current_vwap, extended_from_vwap_pct, volume_ratio, volume_ratio_raw, average_volume, median_volume, volume_confirmation, recent_high, series_quality, *, facade):
    if True:
        out["reason"] = "data_incomplete"
        out["metrics"] = {
            "timeframe_minutes": timeframe_minutes,
            "bar_count": len(candles),
            "price": current_close if current_close > 0.0 else None,
            "vwap": current_vwap if current_vwap > 0.0 else None,
            "vwap_distance": extended_from_vwap_pct if current_vwap > 0.0 and current_close > 0.0 else None,
            "volume_ratio": volume_ratio if volume_ratio > 0.0 else None,
            "volume_ratio_raw": volume_ratio_raw if volume_ratio_raw > 0.0 else None,
            "volume_ratio_effective": volume_ratio if volume_ratio > 0.0 else None,
            "average_volume": average_volume if average_volume > 0.0 else None,
            "median_volume": median_volume if median_volume > 0.0 else None,
            "volume_adjusted": bool(volume_confirmation.adjusted),
            "volume_adjustment_reason": volume_confirmation.adjustment_reason,
            "recent_high": recent_high if recent_high > 0.0 else None,
            "pullback_pct": pullback_depth_pct,
            "inferred_spacing_minutes": series_quality.get("inferred_spacing_minutes"),
            "series_class": series_quality.get("series_class"),
        }
    return None
