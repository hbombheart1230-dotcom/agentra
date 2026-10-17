"""Monitor observation views; policy/effects remain at the facade."""
from __future__ import annotations

from typing import Any, Dict


def monitor_posture_for_cycle(
    *,
    open_position_count: int,
    intents: list[dict],
    exit_info: Dict[str, Any],
    buy_blocked_open_position: bool,
    buy_blocked_post_exit_cooldown: bool,
    facade,
) -> str:
    if any(str((intent or {}).get("side") or "").strip().upper() == "SELL" for intent in list(intents or [])):
        return "SELL"
    if any(str((intent or {}).get("side") or "").strip().upper() == "BUY" for intent in list(intents or [])):
        return "BUY"
    if bool(exit_info.get("triggered")):
        return "SELL"
    if open_position_count > 0:
        return "HOLD"
    if buy_blocked_open_position or buy_blocked_post_exit_cooldown:
        return "WAIT"
    return "WAIT"


def build_monitor_entry_state_snapshot(entry_info: Dict[str, Any], *, facade) -> Dict[str, Any]:
    metrics = dict(entry_info.get("metrics") or {}) if isinstance(entry_info.get("metrics"), dict) else {}
    scores = dict(entry_info.get("condition_scores") or {}) if isinstance(entry_info.get("condition_scores"), dict) else {}
    margins = dict(entry_info.get("threshold_margins") or {}) if isinstance(entry_info.get("threshold_margins"), dict) else {}
    breakout_margins = dict(margins.get("breakout_gap_pct") or {}) if isinstance(margins.get("breakout_gap_pct"), dict) else {}
    return {
        "extended_from_vwap_pct": facade._optional_float(metrics.get("extended_from_vwap_pct")),
        "volume_ratio": facade._optional_float(metrics.get("volume_ratio")),
        "breakout_gap_pct": facade._optional_float(breakout_margins.get("actual")),
        "reclaim_gate_ok": bool(metrics.get("reclaim_gate_ok")),
        "volume_ok": bool(metrics.get("volume_ok")),
        "breakout_ok": bool(metrics.get("breakout_ok")),
        "extension_ok": bool(metrics.get("extension_ok")),
        "breakout_path_ok": bool(metrics.get("breakout_path_ok")),
        "pullback_volume_path_ok": bool(metrics.get("pullback_volume_path_ok")),
        "confidence_gate_ok": bool(scores.get("confidence_gate_ok")),
        "triggered": bool(entry_info.get("triggered")),
        "current_blocking_axis": str(entry_info.get("primary_failure_axis") or ""),
        "transition_readiness_score": facade._optional_float(entry_info.get("transition_readiness_score")),
    }


def build_monitor_entry_transition_trace(previous_monitor_state: Dict[str, Any], entry_info: Dict[str, Any], *, facade) -> Dict[str, Any]:
    previous_entry = (
        dict(previous_monitor_state.get("entry_state") or {})
        if isinstance(previous_monitor_state.get("entry_state"), dict)
        else {}
    )
    thresholds = dict(entry_info.get("thresholds") or {}) if isinstance(entry_info.get("thresholds"), dict) else {}
    current_volume_ratio = facade._optional_float((entry_info.get("metrics") or {}).get("volume_ratio"))
    current_extended_from_vwap = facade._optional_float((entry_info.get("metrics") or {}).get("extended_from_vwap_pct"))
    current_breakout_gap = facade._optional_float((((entry_info.get("threshold_margins") or {}).get("breakout_gap_pct") or {}).get("actual")))
    previous_volume_ratio = facade._optional_float(previous_entry.get("volume_ratio"))
    previous_extended_from_vwap = facade._optional_float(previous_entry.get("extended_from_vwap_pct"))
    previous_breakout_gap = facade._optional_float(previous_entry.get("breakout_gap_pct"))
    volume_ratio_improvement = (
        current_volume_ratio - previous_volume_ratio
        if current_volume_ratio is not None and previous_volume_ratio is not None
        else None
    )
    extended_from_vwap_improvement = (
        current_extended_from_vwap - previous_extended_from_vwap
        if current_extended_from_vwap is not None and previous_extended_from_vwap is not None
        else None
    )
    breakout_gap_improvement = (
        current_breakout_gap - previous_breakout_gap
        if current_breakout_gap is not None and previous_breakout_gap is not None
        else None
    )
    current_ready = bool(entry_info.get("triggered"))
    previous_ready = bool(previous_entry.get("triggered"))
    volume_ratio_min = facade._optional_float(thresholds.get("volume_ratio_min"))
    volume_recovery_recent = False
    if (
        current_volume_ratio is not None
        and previous_volume_ratio is not None
        and volume_ratio_min is not None
        and volume_ratio_min > 0.0
    ):
        volume_recovery_recent = bool(
            current_volume_ratio > previous_volume_ratio
            and max(current_volume_ratio, previous_volume_ratio) >= (0.75 * volume_ratio_min)
        )
    improving_axes = []
    if extended_from_vwap_improvement is not None and extended_from_vwap_improvement > 0.0:
        improving_axes.append("reclaim")
    if volume_ratio_improvement is not None and volume_ratio_improvement > 0.0:
        improving_axes.append("volume")
    if breakout_gap_improvement is not None and breakout_gap_improvement > 0.0:
        improving_axes.append("breakout")
    last_blocking_axis = str(entry_info.get("primary_failure_axis") or "").strip()
    previous_blocking_axis = str(previous_entry.get("current_blocking_axis") or "").strip()
    if current_ready and not previous_ready and previous_blocking_axis:
        last_blocking_axis = previous_blocking_axis
    elif not last_blocking_axis:
        last_blocking_axis = previous_blocking_axis
    return {
        "reclaim_distance_to_ready": entry_info.get("reclaim_distance_to_ready"),
        "vwap_reclaim_progress": entry_info.get("vwap_reclaim_progress"),
        "rebound_progress": entry_info.get("rebound_progress"),
        "volume_distance_to_ready": entry_info.get("volume_distance_to_ready"),
        "breakout_distance_to_ready": entry_info.get("breakout_distance_to_ready"),
        "transition_readiness_score": entry_info.get("transition_readiness_score"),
        "last_blocking_axis": last_blocking_axis,
        "became_ready_this_cycle": bool(current_ready and not previous_ready),
        "extended_from_vwap_improvement": extended_from_vwap_improvement,
        "volume_ratio_improvement": volume_ratio_improvement,
        "breakout_gap_improvement": breakout_gap_improvement,
        "transition_happening_now": bool(
            improving_axes and (current_ready or len(improving_axes) >= 2 or volume_recovery_recent)
        ),
        "volume_recovery_slope": volume_ratio_improvement,
        "volume_recovery_recent": volume_recovery_recent,
    }
