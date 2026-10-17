from __future__ import annotations

import time
from typing import Any, Dict

from libs.core.symbols import normalize_symbol


import sys as _monitor_view_sys
import libs.agents.monitor.projections.entry_state_views as _monitor_views

def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _resolve_now_epoch(state: Dict[str, Any]) -> int:
    for key in ("tick_ts", "now_epoch", "timestamp"):
        try:
            value = int(float(state.get(key)))
        except Exception:
            value = 0
        if value > 0:
            return int(value)
    try:
        return int(time.time())
    except Exception:
        return 0


def monitor_posture_for_cycle(*, open_position_count: int, intents: list[dict], exit_info: Dict[str, Any], buy_blocked_open_position: bool, buy_blocked_post_exit_cooldown: bool) -> str:
    return _monitor_views.monitor_posture_for_cycle(open_position_count=open_position_count, intents=intents, exit_info=exit_info, buy_blocked_open_position=buy_blocked_open_position, buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, facade=_monitor_view_sys.modules[__name__])


def load_previous_monitor_state(state: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    raw = persisted.get("monitor_last_state_by_symbol") if isinstance(persisted.get("monitor_last_state_by_symbol"), dict) else {}
    row = raw.get(normalize_symbol(symbol)) if isinstance(raw, dict) else {}
    return dict(row) if isinstance(row, dict) else {}


def build_monitor_entry_state_snapshot(entry_info: Dict[str, Any]) -> Dict[str, Any]:
    return _monitor_views.build_monitor_entry_state_snapshot(entry_info, facade=_monitor_view_sys.modules[__name__])


def build_monitor_entry_transition_trace(previous_monitor_state: Dict[str, Any], entry_info: Dict[str, Any]) -> Dict[str, Any]:
    return _monitor_views.build_monitor_entry_transition_trace(previous_monitor_state, entry_info, facade=_monitor_view_sys.modules[__name__])


def save_current_monitor_state(
    state: Dict[str, Any],
    symbol: str,
    *,
    posture: str,
    reason: str,
    active_exit_axis: str,
    entry_state: Dict[str, Any] | None = None,
) -> None:
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    rows = persisted.get("monitor_last_state_by_symbol") if isinstance(persisted.get("monitor_last_state_by_symbol"), dict) else {}
    row = {
        "posture": str(posture or ""),
        "reason": str(reason or ""),
        "active_exit_axis": str(active_exit_axis or ""),
        "updated_at_epoch": int(_resolve_now_epoch(state)),
    }
    if isinstance(entry_state, dict) and entry_state:
        row["entry_state"] = dict(entry_state)
    rows[normalize_symbol(symbol)] = row
    persisted["monitor_last_state_by_symbol"] = rows
    state["persisted_state"] = persisted
