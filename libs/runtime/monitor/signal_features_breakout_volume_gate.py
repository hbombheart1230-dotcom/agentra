"""Intraday entry-signal feature facts (price/volume/structure features before scoring).

Second Pass (P1.5) intra-function extraction from `libs/runtime/intraday_monitor_signals.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


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
