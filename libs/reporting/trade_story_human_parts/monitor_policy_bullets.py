from __future__ import annotations

from typing import Any, Callable, Dict, List


def append_monitor_policy_observation_bullets(
    bullets: List[str], monitor_stop_policy_trace: Dict[str, Any], *,
    safe_float: Callable, safe_int: Callable, format_ratio_pct: Callable,
) -> None:
    """Append historical observation text; this does not authorize trades."""
    if monitor_stop_policy_trace.get("hard_stop_pct") not in (None, ""):
        bullets.append(
            f"Hard fail-safe stop: {format_ratio_pct(monitor_stop_policy_trace.get('hard_stop_pct'))}%"
        )
    if monitor_stop_policy_trace.get("adaptive_stop_loss_pct") not in (None, ""):
        bullets.append(
            f"Active adaptive stop: {format_ratio_pct(monitor_stop_policy_trace.get('adaptive_stop_loss_pct'))}%"
        )
    if monitor_stop_policy_trace.get("strategist_baseline_stop_loss_pct") not in (None, ""):
        bullets.append(
            f"Strategist baseline adaptive stop: {format_ratio_pct(monitor_stop_policy_trace.get('strategist_baseline_stop_loss_pct'))}%"
        )
    if monitor_stop_policy_trace.get("effective_stop_loss_pct") not in (None, ""):
        bullets.append(
            f"Effective stop in this run: {format_ratio_pct(monitor_stop_policy_trace.get('effective_stop_loss_pct'))}%"
        )
    if monitor_stop_policy_trace.get("trailing_stop_pct") not in (None, ""):
        bullets.append(
            f"Trailing stop: {format_ratio_pct(monitor_stop_policy_trace.get('trailing_stop_pct'))}%"
        )
    if monitor_stop_policy_trace.get("strategist_baseline_trailing_stop_pct") not in (None, ""):
        bullets.append(
            f"Strategist baseline trailing stop: {format_ratio_pct(monitor_stop_policy_trace.get('strategist_baseline_trailing_stop_pct'))}%"
        )
    if monitor_stop_policy_trace.get("take_profit_pct") not in (None, ""):
        bullets.append(
            f"Take profit target: {format_ratio_pct(monitor_stop_policy_trace.get('take_profit_pct'))}%"
        )
    if bool(monitor_stop_policy_trace.get("cost_aware_profit_floor_enabled")) and safe_float(
        monitor_stop_policy_trace.get("cost_aware_profit_floor_pct"), 0.0
    ) > 0.0:
        bullets.append(
            "Cost-aware profit floor: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('cost_aware_profit_floor_pct'))}% "
            f"(round-trip cost {format_ratio_pct(monitor_stop_policy_trace.get('round_trip_cost_floor_pct'))}% "
            f"+ buffer {format_ratio_pct(monitor_stop_policy_trace.get('min_net_profit_buffer_pct'))}%)"
        )
    if safe_float(monitor_stop_policy_trace.get("partial_take_profit_pct"), 0.0) > 0.0:
        bullets.append(
            f"Partial take profit: {format_ratio_pct(monitor_stop_policy_trace.get('partial_take_profit_pct'))}%"
        )
    if isinstance(monitor_stop_policy_trace.get("profit_ladder_levels_pct"), list) and monitor_stop_policy_trace.get("profit_ladder_levels_pct"):
        bullets.append(
            "Profit ladder levels: "
            + ", ".join(f"{format_ratio_pct(level)}%" for level in list(monitor_stop_policy_trace.get("profit_ladder_levels_pct") or [])[:4])
        )
    if safe_float(monitor_stop_policy_trace.get("risk_reward_take_profit_r"), 0.0) > 0.0:
        bullets.append(f"Risk/reward take profit R: {monitor_stop_policy_trace.get('risk_reward_take_profit_r')}")
    elif isinstance(monitor_stop_policy_trace.get("risk_reward_take_profit_rungs"), list) and monitor_stop_policy_trace.get("risk_reward_take_profit_rungs"):
        bullets.append(
            "Risk/reward take profit rungs: "
            + ", ".join(str(x) for x in list(monitor_stop_policy_trace.get("risk_reward_take_profit_rungs") or [])[:4])
        )
    if safe_float(monitor_stop_policy_trace.get("vwap_extension_take_profit_pct"), 0.0) > 0.0:
        bullets.append(
            "VWAP extension take profit: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('vwap_extension_take_profit_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("resistance_take_profit_near_pct"), 0.0) > 0.0:
        bullets.append(
            "Resistance take profit near: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('resistance_take_profit_near_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("volume_exhaustion_take_profit_min_pct"), 0.0) > 0.0:
        bullets.append(
            "Volume exhaustion take profit min: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('volume_exhaustion_take_profit_min_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("opening_gap_profit_take_min_pct"), 0.0) > 0.0:
        bullets.append(
            "Opening gap profit take min: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('opening_gap_profit_take_min_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("profit_time_stop_sec"), 0.0) > 0.0:
        bullets.append(f"Profit time stop: {safe_int(monitor_stop_policy_trace.get('profit_time_stop_sec'), 0)} seconds")
    if monitor_stop_policy_trace.get("strategist_baseline_take_profit_pct") not in (None, ""):
        bullets.append(
            f"Strategist baseline take profit: {format_ratio_pct(monitor_stop_policy_trace.get('strategist_baseline_take_profit_pct'))}%"
        )
