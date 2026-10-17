"""Monitor observation views; policy/effects remain at the facade."""
from __future__ import annotations

from typing import Any, Dict


def friendly_exit_axis(reason: Any, *, facade) -> str:
    text = str(reason or "").strip().replace("_", " ")
    if not text:
        return "No trigger"
    return " ".join(part.capitalize() for part in text.split())


def monitor_watch_axes(thresholds: Dict[str, Any], *, facade) -> list[str]:
    if not isinstance(thresholds, dict):
        return []
    out: list[str] = []
    if facade.to_float(thresholds.get("hard_stop_pct")) > 0.0:
        out.append("Hard stop")
    if facade.to_float(thresholds.get("stop_loss_pct")) > 0.0:
        out.append("Adaptive stop")
    if facade.to_float(thresholds.get("take_profit_pct")) > 0.0:
        out.append("Take profit")
    if facade._is_trueish(thresholds.get("cost_aware_profit_floor_enabled")) and facade.to_float(
        thresholds.get("cost_aware_profit_floor_pct")
    ) > 0.0:
        out.append("Cost-aware profit floor")
    if facade.to_float(thresholds.get("partial_take_profit_pct")) > 0.0:
        out.append("Partial take profit")
    if isinstance(thresholds.get("profit_ladder_levels_pct"), list) and thresholds.get("profit_ladder_levels_pct"):
        out.append("Profit ladder")
    if facade.to_float(thresholds.get("risk_reward_take_profit_r")) > 0.0:
        out.append("Risk/reward take profit")
    elif isinstance(thresholds.get("risk_reward_take_profit_rungs"), list) and thresholds.get("risk_reward_take_profit_rungs"):
        out.append("Risk/reward take profit")
    if facade.to_float(thresholds.get("vwap_extension_take_profit_pct")) > 0.0:
        out.append("VWAP extension take profit")
    if facade.to_float(thresholds.get("resistance_take_profit_near_pct")) > 0.0:
        out.append("Resistance take profit")
    if facade.to_float(thresholds.get("volume_exhaustion_take_profit_min_pct")) > 0.0:
        out.append("Volume exhaustion take profit")
    if facade.to_float(thresholds.get("opening_gap_profit_take_min_pct")) > 0.0:
        out.append("Opening gap profit take")
    if facade.to_float(thresholds.get("profit_time_stop_sec")) > 0.0:
        out.append("Time-decay profit exit")
    if facade.to_float(thresholds.get("trailing_stop_pct")) > 0.0:
        out.append("Trailing stop")
    if facade.to_float(thresholds.get("peak_drawdown_exit_pct")) > 0.0:
        out.append("Peak drawdown")
    if facade.to_float(thresholds.get("vwap_breakdown_pct")) > 0.0:
        out.append("VWAP breakdown")
    if facade.to_float(thresholds.get("intraday_low_break_pct")) > 0.0:
        out.append("Intraday low break")
    if facade.to_float(thresholds.get("trend_strength_floor")) != 0.0:
        out.append("Trend breakdown")
    if facade.to_float(thresholds.get("vol_expansion_ratio")) > 0.0:
        out.append("Volatility expansion")
    if facade.to_float(thresholds.get("news_shock_threshold")) > 0.0:
        out.append("News shock")
    if bool(thresholds.get("use_eod_flat")):
        out.append("EOD flat")
    return out
