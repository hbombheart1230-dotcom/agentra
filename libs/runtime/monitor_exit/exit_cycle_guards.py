"""Monitor exit cycle: confirm/cooldown/lock/previous-qty maps from State.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::monitor_node` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class ExitCycleMaps(NamedTuple):
    """Result of `load_exit_cycle_maps` (positional order = sorted output names)."""

    confirm_map: Any
    cooldown_map: Any
    pending_exit_lock: Any
    prev_qty_map: Any

class ExitCooldownLock(NamedTuple):
    """Result of `resolve_exit_cooldown_and_lock` (positional order = sorted output names)."""

    cooldown_until: Any
    lock_until: Any

class SellGuardResolution(NamedTuple):
    """Result of `evaluate_exit_sell_guards` (positional order = sorted output names)."""

    confirm_count: Any
    hold_block_reason: Any
    min_hold_blocked: Any
    monitor_reason: Any
    sell_cooldown_blocked: Any
    sell_guard_blocked: Any
    sell_guard_reason: Any

class ExitSignalLock(NamedTuple):
    """Result of `commit_exit_signal_lock` (positional order = sorted output names)."""

    confirm_count: Any
    cooldown_until: Any
    lock_until: Any
    monitor_reason: Any

def load_exit_cycle_maps(state):
    confirm_map = state.get("_monitor_exit_confirm")
    if not isinstance(confirm_map, dict):
        confirm_map = {}
    cooldown_map = state.get("_monitor_sell_cooldown_until")
    if not isinstance(cooldown_map, dict):
        cooldown_map = {}
    pending_exit_lock = state.get("_monitor_pending_exit_lock")
    if not isinstance(pending_exit_lock, dict):
        pending_exit_lock = {}
    prev_qty_map = state.get("_monitor_prev_position_qty")
    if not isinstance(prev_qty_map, dict):
        prev_qty_map = {}
    return ExitCycleMaps(confirm_map, cooldown_map, pending_exit_lock, prev_qty_map)

def resolve_exit_cooldown_and_lock(cooldown_map, now_epoch, pending_exit_lock, prev_qty_map, qty, sell_cooldown_sec, symbol, *, facade):
    prev_qty = max(0, facade._to_int(prev_qty_map.get(symbol)))
    if prev_qty > 0 and qty <= 0 and sell_cooldown_sec > 0:
        cooldown_map[symbol] = int(now_epoch + sell_cooldown_sec)
    prev_qty_map[symbol] = int(qty)

    cooldown_until = max(0, facade._to_int(cooldown_map.get(symbol)))
    if cooldown_until > 0 and cooldown_until <= now_epoch:
        cooldown_map.pop(symbol, None)
        cooldown_until = 0

    lock_until = max(0, facade._to_int(pending_exit_lock.get(symbol)))
    if lock_until > 0 and lock_until <= now_epoch:
        pending_exit_lock.pop(symbol, None)
        lock_until = 0
    return ExitCooldownLock(cooldown_until, lock_until)

def evaluate_exit_sell_guards(confirm_count, confirm_key, confirm_map, cooldown_until, decision, effective_confirm_ticks, emergency_exit, entry_info, eod_carry, eod_flat_exit, exit_signal_detected, hard_exit, hold_block_reason, hold_sec, lock_until, min_hold_blocked, min_hold_sec, monitor_reason, now_epoch, qty, selected_pending_order_for_exit, sell_cooldown_blocked, sell_cooldown_sec, sell_guard_blocked, sell_guard_reason, state, symbol, *, facade):
    if exit_signal_detected:
        if qty <= 0:
            sell_guard_blocked = True
            sell_guard_reason = "sell_guard_no_position"
            monitor_reason = "no_position"
        elif facade._is_trueish(state.get("execution_pending")):
            sell_guard_blocked = True
            sell_guard_reason = "sell_guard_execution_pending"
            monitor_reason = "pending_exit_lock"
        elif selected_pending_order_for_exit:
            sell_guard_blocked = True
            sell_guard_reason = "sell_guard_open_order_pending"
            monitor_reason = "pending_exit_lock"
        elif lock_until > now_epoch and not eod_flat_exit:
            sell_guard_blocked = True
            sell_guard_reason = "sell_guard_pending_exit_lock"
            monitor_reason = "pending_exit_lock"
            hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
        elif not emergency_exit and not hard_exit and min_hold_sec > 0 and hold_sec > 0 and hold_sec < min_hold_sec:
            sell_guard_blocked = True
            min_hold_blocked = True
            sell_guard_reason = f"sell_guard_min_hold:{hold_sec}s<{min_hold_sec}s"
            monitor_reason = "min_hold_active"
            hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
        elif not emergency_exit and not hard_exit and sell_cooldown_sec > 0 and cooldown_until > now_epoch:
            sell_guard_blocked = True
            sell_cooldown_blocked = True
            sell_guard_reason = f"sell_guard_cooldown:{max(0, cooldown_until - now_epoch)}s_remaining"
            monitor_reason = "cooldown_active"
            hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
        elif not emergency_exit and not hard_exit and effective_confirm_ticks > 1:
            confirm_count = facade._to_int(confirm_map.get(confirm_key)) + 1
            confirm_map[confirm_key] = int(confirm_count)
            if confirm_count < int(effective_confirm_ticks):
                sell_guard_blocked = True
                sell_guard_reason = f"exit_confirmation_pending:{confirm_count}/{effective_confirm_ticks}"
                monitor_reason = "exit_signal_pending_confirmation"
                hold_block_reason = f"{str(decision.get('reason') or 'exit_signal')}:{sell_guard_reason}"
        if not sell_guard_blocked and not monitor_reason:
            monitor_reason = "confirmed_exit_signal"
    else:
        facade._clear_symbol_confirm_keys(confirm_map, symbol)
        if bool(eod_carry.get("approved")) and qty > 0:
            monitor_reason = "eod_carry_approved"
        elif qty <= 0 and bool(entry_info.get("guard_blocked")):
            monitor_reason = str(entry_info.get("guard_reason") or "entry_guard_blocked")
        elif qty <= 0 and str(entry_info.get("reason") or "").strip():
            monitor_reason = str(entry_info.get("reason") or "entry_wait")
        elif qty <= 0 and bool(entry_info.get("triggered")) and bool(entry_info.get("intent_submitted")):
            monitor_reason = str(entry_info.get("reason") or "entry_signal_confirmed")
        else:
            monitor_reason = "hold" if qty > 0 else "no_position"
    return SellGuardResolution(confirm_count, hold_block_reason, min_hold_blocked, monitor_reason, sell_cooldown_blocked, sell_guard_blocked, sell_guard_reason)

def commit_exit_signal_lock(confirm_count, confirm_map, cooldown_map, cooldown_until, effective_confirm_ticks, emergency_exit, exit_signal_detected, hard_exit, lock_until, monitor_reason, now_epoch, pending_exit_lock, qty, sell_cooldown_sec, sell_guard_blocked, symbol, *, facade):
    if not sell_guard_blocked and exit_signal_detected:
        if not emergency_exit and not hard_exit and confirm_count <= 0:
            confirm_count = max(1, int(effective_confirm_ticks))
        facade._clear_symbol_confirm_keys(confirm_map, symbol)
        lock_sec = max(30, int(sell_cooldown_sec))
        pending_exit_lock[symbol] = int(now_epoch + lock_sec)
        lock_until = int(now_epoch + lock_sec)
        if sell_cooldown_sec > 0:
            cooldown_until = int(now_epoch + sell_cooldown_sec)
            cooldown_map[symbol] = int(cooldown_until)
        if emergency_exit:
            monitor_reason = "emergency_exit_signal"
        elif monitor_reason not in ("confirmed_exit_signal", "emergency_exit_signal"):
            monitor_reason = "confirmed_exit_signal"

    if qty <= 0:
        pending_exit_lock.pop(symbol, None)
        lock_until = 0
    return ExitSignalLock(confirm_count, cooldown_until, lock_until, monitor_reason)

def build_overnight_carry_decision_payload(eod_carry, now_epoch, symbol):
    return (
        {
                    "approved": bool(eod_carry.get("approved")),
                    "action": str(eod_carry.get("action") or ""),
                    "reason": str(eod_carry.get("reason") or ""),
                    "minutes_to_close": eod_carry.get("minutes_to_close"),
                    "cutoff_min": eod_carry.get("cutoff_min"),
                    "positive_signals": list(eod_carry.get("positive_signals") or []),
                    "blockers": list(eod_carry.get("blockers") or []),
                    "carry_calendar": dict(eod_carry.get("carry_calendar") or {}),
                    "weekend_carry": bool(eod_carry.get("weekend_carry")),
                    "allow_weekend_carry": bool(eod_carry.get("allow_weekend_carry")),
                    "holding_gap_days": eod_carry.get("holding_gap_days"),
                    "decided_at_epoch": int(now_epoch),
                    "symbol": str(symbol or ""),
                }
    )
