from __future__ import annotations

from typing import Any, Dict

from libs.runtime.monitor_exit.numeric import to_float


import sys as _monitor_view_sys
import libs.agents.monitor.projections.exit_axis_labels as _monitor_views

def _is_trueish(value: Any) -> bool:
    return str(value or "").strip().lower() in ("1", "true", "yes", "y", "on")


def is_emergency_exit_reason(reason: str) -> bool:
    text = str(reason or "").strip().lower()
    return text in ("emergency_halt", "news_shock")


def is_hard_exit_reason(reason: str) -> bool:
    text = str(reason or "").strip().lower()
    return text in (
        "emergency_halt",
        "news_shock",
        "eod_flat",
        "hard_stop",
        "stop_loss",
        "intraday_low_break",
        "trend_breakdown",
        "vwap_breakdown",
        "volatility_expansion",
        "trailing_stop",
    )


def exit_reason_priority(reason: str) -> int:
    text = str(reason or "").strip().lower()
    order = {
        "emergency_halt": 100,
        "news_shock": 95,
        "eod_flat": 90,
        "time_stop": 80,
        "max_hold": 75,
        "hard_stop": 72,
        "stop_loss": 70,
        "intraday_low_break": 69,
        "trend_breakdown": 68,
        "peak_drawdown": 67,
        "vwap_breakdown": 66,
        "volatility_expansion": 65,
        "trailing_stop": 60,
        "volume_exhaustion_take_profit": 59,
        "opening_gap_profit_take": 59,
        "vwap_extension_take_profit": 58,
        "resistance_take_profit": 57,
        "risk_reward_take_profit": 56,
        "profit_ladder": 55,
        "partial_take_profit": 55,
        "time_decay_profit_exit": 55,
        "take_profit": 50,
        "hold": 10,
        "price_unavailable": 5,
        "no_position": 0,
    }
    return int(order.get(text, 1))


def is_soft_profit_exit_reason(reason: Any) -> bool:
    return str(reason or "").strip().lower() in {
        "take_profit",
        "partial_take_profit",
        "profit_ladder",
        "risk_reward_take_profit",
        "vwap_extension_take_profit",
        "resistance_take_profit",
        "volume_exhaustion_take_profit",
        "opening_gap_profit_take",
        "time_decay_profit_exit",
    }


def friendly_exit_axis(reason: Any) -> str:
    return _monitor_views.friendly_exit_axis(reason, facade=_monitor_view_sys.modules[__name__])


def monitor_watch_axes(thresholds: Dict[str, Any]) -> list[str]:
    return _monitor_views.monitor_watch_axes(thresholds, facade=_monitor_view_sys.modules[__name__])
