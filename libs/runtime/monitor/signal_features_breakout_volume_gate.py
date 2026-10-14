"""Intraday entry-signal feature facts (price/volume/structure features before scoring).

Second Pass (P1.5) intra-function extraction from `libs/runtime/intraday_monitor_signals.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


def signal_feature_breakout_volume_gate_ok_breakout_volume(breakout_ok, vwap_hold_ok, vwap_reclaim_ok, volume_ok, rebound_ok, pullback_ok, confirmation_ok, extension_ok, reclaim_gate_ok, breakout_path_ok, pullback_volume_path_ok, opening_gap_chase_observed, breakout_chase_extension_observed, etf_deviation_pct, etf_deviation_discount_entry_ok, etf_deviation_entry_path_ok, inverse_hedge_reclaim_path_ok, lower_vwap_rebound_probe_path_ok, frame, vwap_structure_ok, breakout_volume_gate_ok, pullback_mature, pullback_not_too_deep, confidence_gate_ok, etf_deviation_chart_ok, lower_rebound_higher_lows, lower_rebound_volume_ok, lower_rebound_vwap_band_ok, etf_deviation_tradeable, breakout_volume_gate_required, *, facade):
    signal_chain: facade.List[str] = []
    if breakout_ok:
        signal_chain.append("recent_high_breakout")
    if vwap_hold_ok:
        signal_chain.append("vwap_hold")
    if vwap_reclaim_ok:
        signal_chain.append("vwap_reclaim")
    if volume_ok:
        signal_chain.append("volume_confirmation")
    if rebound_ok:
        signal_chain.append("pullback_rebound")
    if pullback_ok:
        signal_chain.append("pullback_structure")
    if confirmation_ok:
        signal_chain.append("confirmation_ready")
    if extension_ok:
        signal_chain.append("not_extended")
    if reclaim_gate_ok:
        signal_chain.append("reclaim_gate_ready")
    if breakout_path_ok:
        signal_chain.append("breakout_path_ready")
    if pullback_volume_path_ok:
        signal_chain.append("pullback_volume_path_ready")
    if opening_gap_chase_observed:
        signal_chain.append("opening_gap_chase_observed")
        if not volume_ok:
            signal_chain.append("opening_gap_chase_volume_observed_missing")
    if breakout_chase_extension_observed:
        signal_chain.append("breakout_chase_extension_observed")
        if not volume_ok:
            signal_chain.append("breakout_chase_extension_volume_observed_missing")
    if etf_deviation_pct is not None:
        signal_chain.append("etf_deviation_observed")
    if etf_deviation_discount_entry_ok:
        signal_chain.append("etf_discount_observed")
    if etf_deviation_entry_path_ok:
        signal_chain.append("etf_discount_reversion_path_ready")
    if inverse_hedge_reclaim_path_ok:
        signal_chain.append("inverse_hedge_reclaim_path_ready")
    if lower_vwap_rebound_probe_path_ok:
        signal_chain.append("lower_vwap_rebound_probe_path_ready")

    playbook = str((frame or {}).get("playbook") or "").strip().lower()
    if playbook in ("pullback", "reversal"):
        breakout_volume_gate_required = True
        breakout_volume_gate_ok = (not breakout_path_ok) or bool(volume_ok)
    checks = {
        "breakout_ok": bool(breakout_ok),
        "vwap_hold_ok": bool(vwap_hold_ok),
        "vwap_reclaim_ok": bool(vwap_reclaim_ok),
        "vwap_structure_ok": bool(vwap_structure_ok),
        "reclaim_gate_ok": bool(reclaim_gate_ok),
        "breakout_volume_gate_ok": bool(breakout_volume_gate_ok),
        "opening_gap_chase_observed": bool(opening_gap_chase_observed),
        "breakout_chase_extension_observed": bool(breakout_chase_extension_observed),
        "volume_ok": bool(volume_ok),
        "rebound_ok": bool(rebound_ok),
        "confirmation_ok": bool(confirmation_ok),
        "extension_ok": bool(extension_ok),
        "pullback_mature": bool(pullback_mature),
        "pullback_not_too_deep": bool(pullback_not_too_deep),
        "pullback_structure_ok": bool(pullback_ok),
        "breakout_path_ok": bool(breakout_path_ok),
        "pullback_volume_path_ok": bool(pullback_volume_path_ok),
        "confidence_gate_ok": bool(confidence_gate_ok),
        "etf_deviation_discount_entry_ok": bool(etf_deviation_discount_entry_ok),
        "etf_deviation_chart_ok": bool(etf_deviation_chart_ok),
        "etf_deviation_entry_path_ok": bool(etf_deviation_entry_path_ok),
        "inverse_hedge_reclaim_path_ok": bool(inverse_hedge_reclaim_path_ok),
        "lower_vwap_rebound_probe_path_ok": bool(lower_vwap_rebound_probe_path_ok),
        "lower_rebound_higher_lows": bool(lower_rebound_higher_lows),
        "lower_rebound_volume_ok": bool(lower_rebound_volume_ok),
        "lower_rebound_vwap_band_ok": bool(lower_rebound_vwap_band_ok),
    }
    if playbook in ("pullback", "reversal"):
        relevant_checks = [
            "reclaim_gate_ok",
            "vwap_structure_ok",
            "pullback_mature",
            "pullback_not_too_deep",
            "volume_ok",
            "breakout_volume_gate_ok",
            "pullback_volume_path_ok",
            "breakout_ok",
            "breakout_path_ok",
            "extension_ok",
            "confidence_gate_ok",
            "vwap_reclaim_ok",
            "vwap_hold_ok",
            "rebound_ok",
        ]
    else:
        relevant_checks = [
            "reclaim_gate_ok",
            "breakout_ok",
            "breakout_path_ok",
            "vwap_hold_ok",
            "volume_ok",
            "pullback_structure_ok",
            "pullback_volume_path_ok",
            "extension_ok",
            "rebound_ok",
            "confidence_gate_ok",
        ]
    if etf_deviation_tradeable:
        relevant_checks.extend(
            [
                "etf_deviation_discount_entry_ok",
                "etf_deviation_chart_ok",
                "etf_deviation_entry_path_ok",
                "inverse_hedge_reclaim_path_ok",
                "lower_vwap_rebound_probe_path_ok",
            ]
        )
    passed_checks = [name for name in relevant_checks if checks.get(name)]
    failed_checks = [name for name in relevant_checks if not checks.get(name)]
    return (breakout_volume_gate_ok, breakout_volume_gate_required, failed_checks, passed_checks, playbook, relevant_checks, signal_chain)


class VolumePullbackBreakoutGateFeatures(NamedTuple):
    """Result of `volume_pullback_breakout_gate_features` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    average_volume: Any
    breakout_chase_extension_observed: Any
    breakout_path_ok: Any
    breakout_score: Any
    breakout_volume_gate_ok: Any
    breakout_volume_gate_required: Any
    confirmation_ok: Any
    extension_ok: Any
    max_extended_from_vwap_pct: Any
    median_volume: Any
    min_extended_from_vwap_pct: Any
    opening_gap_chase_observed: Any
    pullback_mature: Any
    pullback_max_pct: Any
    pullback_min_pct: Any
    pullback_not_too_deep: Any
    pullback_ok: Any
    pullback_score: Any
    pullback_volume_path_ok: Any
    reclaim_gate_ok: Any
    volume_ok: Any
    volume_ratio: Any
    volume_score: Any
    vwap_structure_ok: Any


def volume_pullback_breakout_gate_features(volume_confirmation, resolved_policy, extended_from_vwap_pct, pullback_depth_pct, vwap_hold_ok, vwap_reclaim_ok, rebound_ok, breakout_ok, minutes_since_session_open, open_gap_pct, prev_close_distance_pct, session_gap_context, current_close, breakout_level, *, facade):
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
    return VolumePullbackBreakoutGateFeatures(average_volume, breakout_chase_extension_observed, breakout_path_ok, breakout_score, breakout_volume_gate_ok, breakout_volume_gate_required, confirmation_ok, extension_ok, max_extended_from_vwap_pct, median_volume, min_extended_from_vwap_pct, opening_gap_chase_observed, pullback_mature, pullback_max_pct, pullback_min_pct, pullback_not_too_deep, pullback_ok, pullback_score, pullback_volume_path_ok, reclaim_gate_ok, volume_ok, volume_ratio, volume_score, vwap_structure_ok)
