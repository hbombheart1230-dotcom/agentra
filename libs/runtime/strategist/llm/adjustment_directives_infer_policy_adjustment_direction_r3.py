"""Owner for policy adjustment direction inference."""
from __future__ import annotations


def _infer_policy_adjustment_direction_r3_impl(baseline_summary, current_summary, *, facade):
    tighter = 0
    looser = 0
    baseline = dict(baseline_summary or {}) if isinstance(baseline_summary, dict) else {}
    current = dict(current_summary or {}) if isinstance(current_summary, dict) else {}
    higher_is_tighter = {"volume_ratio_min", "pullback_min_pct", "breakout_buffer_pct", "intent_cooldown_sec"}
    lower_is_tighter = {"max_extended_from_vwap_pct", "pullback_max_pct", "reclaim_tolerance_pct"}
    for key in higher_is_tighter:
        if key in baseline and key in current and baseline.get(key) != current.get(key):
            if float(current.get(key) or 0.0) > float(baseline.get(key) or 0.0): tighter += 1
            else: looser += 1
    for key in lower_is_tighter:
        if key in baseline and key in current and baseline.get(key) != current.get(key):
            if float(current.get(key) or 0.0) < float(baseline.get(key) or 0.0): tighter += 1
            else: looser += 1
    if "min_extended_from_vwap_pct" in baseline and "min_extended_from_vwap_pct" in current and baseline.get("min_extended_from_vwap_pct") != current.get("min_extended_from_vwap_pct"):
        if float(current.get("min_extended_from_vwap_pct") or 0.0) > float(baseline.get("min_extended_from_vwap_pct") or 0.0): tighter += 1
        else: looser += 1
    if tighter and not looser: return "tighten"
    if looser and not tighter: return "relax"
    if tighter or looser: return "mixed"
    return "none"
