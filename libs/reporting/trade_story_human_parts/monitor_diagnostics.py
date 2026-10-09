from __future__ import annotations

from typing import Any, Callable, Dict, List


def build_monitor_watch_axes(
    monitor: Dict[str, Any], trigger_details: Dict[str, Any],
    thresholds: Dict[str, Any], safe_float: Callable,
) -> List[str]:
    """Describe configured exit/watch thresholds without adjusting execution policy."""
    watch_axes: List[str] = [str(x or "") for x in list(monitor.get("watch_axes") or trigger_details.get("watch_axes") or []) if str(x or "").strip()]
    if "Hard stop" not in watch_axes and (thresholds.get("hard_stop_pct") not in (None, "") or thresholds.get("stop_loss_pct") not in (None, "")):
        watch_axes.append("Hard stop")
    if "Take profit" not in watch_axes and thresholds.get("take_profit_pct") not in (None, ""):
        watch_axes.append("Take profit")
    if "Partial take profit" not in watch_axes and safe_float(thresholds.get("partial_take_profit_pct"), 0.0) > 0.0:
        watch_axes.append("Partial take profit")
    if "Profit ladder" not in watch_axes and isinstance(thresholds.get("profit_ladder_levels_pct"), list) and thresholds.get("profit_ladder_levels_pct"):
        watch_axes.append("Profit ladder")
    if "Risk/reward take profit" not in watch_axes and safe_float(thresholds.get("risk_reward_take_profit_r"), 0.0) > 0.0:
        watch_axes.append("Risk/reward take profit")
    elif "Risk/reward take profit" not in watch_axes and isinstance(thresholds.get("risk_reward_take_profit_rungs"), list) and thresholds.get("risk_reward_take_profit_rungs"):
        watch_axes.append("Risk/reward take profit")
    if "VWAP extension take profit" not in watch_axes and safe_float(thresholds.get("vwap_extension_take_profit_pct"), 0.0) > 0.0:
        watch_axes.append("VWAP extension take profit")
    if "Resistance take profit" not in watch_axes and safe_float(thresholds.get("resistance_take_profit_near_pct"), 0.0) > 0.0:
        watch_axes.append("Resistance take profit")
    if "Volume exhaustion take profit" not in watch_axes and safe_float(thresholds.get("volume_exhaustion_take_profit_min_pct"), 0.0) > 0.0:
        watch_axes.append("Volume exhaustion take profit")
    if "Opening gap profit take" not in watch_axes and safe_float(thresholds.get("opening_gap_profit_take_min_pct"), 0.0) > 0.0:
        watch_axes.append("Opening gap profit take")
    if "Time-decay profit exit" not in watch_axes and safe_float(thresholds.get("profit_time_stop_sec"), 0.0) > 0.0:
        watch_axes.append("Time-decay profit exit")
    if "Trailing stop" not in watch_axes and thresholds.get("trailing_stop_pct") not in (None, ""):
        watch_axes.append("Trailing stop")
    if "Peak drawdown" not in watch_axes and thresholds.get("peak_drawdown_exit_pct") not in (None, ""):
        watch_axes.append("Peak drawdown")
    if "VWAP breakdown" not in watch_axes and thresholds.get("vwap_breakdown_pct") not in (None, ""):
        watch_axes.append("VWAP breakdown")
    if "Intraday low break" not in watch_axes and thresholds.get("intraday_low_break_pct") not in (None, ""):
        watch_axes.append("Intraday low break")
    if "Trend breakdown" not in watch_axes and thresholds.get("trend_strength_floor") not in (None, ""):
        watch_axes.append("Trend breakdown")
    if "Volatility expansion" not in watch_axes and thresholds.get("vol_expansion_ratio") not in (None, ""):
        watch_axes.append("Volatility expansion")

    return watch_axes


def build_monitor_entry_threshold_gaps(
    entry_metrics: Dict[str, Any], entry_thresholds: Dict[str, Any],
    safe_float: Callable, format_ratio_pct: Callable,
) -> List[str]:
    """Describe observed gaps for the human-readable monitor report."""
    entry_threshold_gaps: List[str] = []
    if entry_metrics.get("volume_ratio") not in (None, "") and entry_thresholds.get("volume_ratio_min") not in (None, ""):
        volume_ratio = safe_float(entry_metrics.get("volume_ratio"), 0.0)
        volume_ratio_min = safe_float(entry_thresholds.get("volume_ratio_min"), 0.0)
        if volume_ratio < volume_ratio_min:
            entry_threshold_gaps.append(f"volume ratio {volume_ratio:.2f} below min {volume_ratio_min:.2f}")
    if entry_metrics.get("extended_from_vwap_pct") not in (None, "") and entry_thresholds.get("max_extended_from_vwap_pct") not in (None, ""):
        extended = safe_float(entry_metrics.get("extended_from_vwap_pct"), 0.0)
        extended_max = safe_float(entry_thresholds.get("max_extended_from_vwap_pct"), 0.0)
        if extended > extended_max:
            entry_threshold_gaps.append(
                f"VWAP extension {format_ratio_pct(extended)}% above max {format_ratio_pct(extended_max)}%"
            )
    if entry_metrics.get("pullback_depth_pct") not in (None, "") and entry_thresholds.get("pullback_min_pct") not in (None, ""):
        pullback_depth = safe_float(entry_metrics.get("pullback_depth_pct"), 0.0)
        pullback_min = safe_float(entry_thresholds.get("pullback_min_pct"), 0.0)
        if pullback_depth < pullback_min:
            entry_threshold_gaps.append(
                f"pullback depth {format_ratio_pct(pullback_depth)}% below min {format_ratio_pct(pullback_min)}%"
            )
    return entry_threshold_gaps
