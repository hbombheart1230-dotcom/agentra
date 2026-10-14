"""Monitor output artifact evidence sources, no-trade trace, entry cascade and focus facts.

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_monitor_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from typing import Any, NamedTuple

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _safe_int,
)


class MonitorStateSurfaceSources(NamedTuple):
    """Result of `monitor_state_surface_sources` (positional order is the pre-T3.5 tuple order)."""

    entry_detail: Any
    entry_info: Any
    exit_detail: Any
    exit_info: Any
    monitor: Any
    monitor_focus_state: Any
    monitor_output: Any
    scanner_selected_snapshot: Any
    selected: Any
    trace_sources: Any
    transition: Any

class MonitorNoTradePolicyTrace(NamedTuple):
    """Result of `monitor_no_trade_policy_trace` (positional order is the pre-T3.5 tuple order)."""

    exit_vs_strategy_intent: Any
    monitor_no_trade_surface: Any
    policy_trace: Any

class MonitorEntryCascadeHandoff(NamedTuple):
    """Result of `monitor_entry_cascade_handoff` (positional order is the pre-T3.5 tuple order)."""

    entry_blocker_surface: Any
    entry_candidate_cascade: Any
    first_intent: Any
    intent_side: Any
    intents: Any
    monitor_focus_context: Any
    open_position_count: Any
    scanner_monitor_handoff: Any
    symbol: Any
    thresholds: Any
    watch_axes: Any

def monitor_state_surface_sources(state):
    monitor = _dict(state.get("monitor"))
    monitor_output = _dict(state.get("monitor_output"))
    monitor_focus_state = _dict(state.get("monitor_focus_context"))
    monitor_evaluation = _dict(state.get("monitor_evaluation"))
    monitor_action = _dict(state.get("monitor_action_decision"))
    exit_info = _dict(state.get("monitor_exit"))
    entry_info = _dict(state.get("monitor_entry"))
    transition = _dict(state.get("monitor_state_transition"))
    entry_detail = _dict(state.get("monitor_entry_decision_detail"))
    exit_detail = _dict(state.get("monitor_exit_decision_detail"))
    selected = _dict(state.get("selected"))
    scanner_selected_snapshot = _dict(state.get("scanner_selected_snapshot"))
    trace_sources = [
        monitor_output,
        monitor_focus_state,
        monitor_action,
        monitor_evaluation,
        entry_detail,
        exit_detail,
        monitor,
        entry_info,
        exit_info,
    ]
    return MonitorStateSurfaceSources(entry_detail, entry_info, exit_detail, exit_info, monitor, monitor_focus_state, monitor_output, scanner_selected_snapshot, selected, trace_sources, transition)


def monitor_no_trade_policy_trace(_first_trace_dict, _first_trace_text, _first_trace_list, _first_trace_bool):
    policy_trace = {
        "policy_ref": _first_trace_dict("policy_ref"),
        "entry_check_summary": _first_trace_text("entry_check_summary"),
        "entry_blockers": _first_trace_list("entry_blockers"),
        "timing_assessment": _first_trace_dict("timing_assessment"),
        "exit_trigger_basis": _first_trace_dict("exit_trigger_basis"),
        "commander_context_consumed": _first_trace_bool("commander_context_consumed"),
        "consumed_fields": _first_trace_list("consumed_fields"),
        "flow_instruction_applied": _first_trace_bool("flow_instruction_applied"),
        "no_trade_reason_applied": _first_trace_bool("no_trade_reason_applied"),
        "shadow_used": _first_trace_bool("shadow_used"),
        "strategist_fallback_used": _first_trace_bool("strategist_fallback_used"),
    }
    exit_vs_strategy_intent = _first_trace_dict("exit_vs_strategy_intent")
    monitor_no_trade_surface = _first_trace_dict("no_trade_surface")
    return MonitorNoTradePolicyTrace(exit_vs_strategy_intent, monitor_no_trade_surface, policy_trace)


def monitor_entry_cascade_handoff(_first_trace_dict, monitor_no_trade_surface, entry_info, scanner_selected_snapshot, selected, state, monitor_output, _first_trace_list, monitor, exit_info, monitor_focus_state, *, facade):
    scanner_monitor_handoff = _first_trace_dict("scanner_monitor_handoff")
    if not scanner_monitor_handoff:
        scanner_monitor_handoff = facade.build_scanner_monitor_handoff_surface(
            selected=scanner_selected_snapshot or selected,
            ranked_candidates=[row for row in list(state.get("ranked_candidates") or []) if isinstance(row, dict)],
            scanner_output=_dict(state.get("scanner_output")),
            final_decision=str(monitor_output.get("intent_side") or "NOOP").strip().upper() or "WAIT",
            no_trade_surface=monitor_no_trade_surface,
            entry_info=entry_info,
        )
    entry_candidate_cascade = _first_trace_dict("entry_candidate_cascade")
    entry_blocker_surface = _first_trace_dict("entry_blocker_surface")
    if not entry_blocker_surface:
        entry_blocker_surface = facade.build_entry_blocker_surface(
            entry_info,
            final_decision=str(monitor_output.get("intent_side") or "NOOP").strip().upper() or "WAIT",
            no_trade_surface=monitor_no_trade_surface,
            entry_blockers=_first_trace_list("entry_blockers"),
            buy_blocked_open_position=bool(monitor.get("buy_blocked_open_position")),
            buy_blocked_post_exit_cooldown=bool(monitor.get("buy_blocked_post_exit_cooldown")),
            post_exit_cooldown_remaining_sec=monitor.get("post_exit_cooldown_remaining_sec"),
            open_position_count=monitor.get("open_position_count"),
        )
    symbol = str(exit_info.get("symbol") or monitor_output.get("selected_symbol") or monitor.get("selected_symbol") or "").strip()
    thresholds = _dict(exit_info.get("thresholds"))
    watch_axes = list(exit_info.get("watch_axes") or [])
    intents = [row for row in list(state.get("intents") or []) if isinstance(row, dict)]
    first_intent = intents[0] if intents else {}
    intent_side = str(monitor_output.get("intent_side") or first_intent.get("side") or "NOOP").strip().upper()
    open_position_count = _safe_int(monitor.get("open_position_count"))
    monitor_focus_context = _first_trace_dict("monitor_focus_context")
    if not monitor_focus_context and monitor_focus_state:
        monitor_focus_context = dict(monitor_focus_state)
    return MonitorEntryCascadeHandoff(entry_blocker_surface, entry_candidate_cascade, first_intent, intent_side, intents, monitor_focus_context, open_position_count, scanner_monitor_handoff, symbol, thresholds, watch_axes)


def monitor_focus_context_projection(monitor_output, entry_info, selected, scanner_monitor_handoff, exit_info, open_position_count, monitor, monitor_focus_context):
    entry_candidate_symbol = _clip(
        monitor_output.get("entry_candidate_symbol")
        or entry_info.get("selected_symbol")
        or entry_info.get("symbol")
        or selected.get("symbol"),
        max_len=24,
    )
    entry_final_symbol = _clip(
        monitor_output.get("entry_final_symbol")
        or _dict(scanner_monitor_handoff.get("entry_candidate_cascade")).get("final_selected_symbol")
        or entry_candidate_symbol,
        max_len=24,
    )
    position_focus_symbol = _clip(
        monitor_output.get("position_focus_symbol")
        or exit_info.get("symbol")
        or "",
        max_len=24,
    )
    if position_focus_symbol and entry_final_symbol and position_focus_symbol != entry_final_symbol:
        focus_mode = "entry_candidate_and_position_focus"
    elif position_focus_symbol:
        focus_mode = "position_focus"
    elif entry_final_symbol:
        focus_mode = "entry_candidate_focus"
    else:
        focus_mode = ""
    if focus_mode:
        monitor_focus_context = {
            "schema_version": "monitor.focus_context.v1",
            "focus_mode": focus_mode,
            "scanner_selected_symbol": _clip(scanner_monitor_handoff.get("scanner_selected_symbol"), max_len=24),
            "entry_candidate_symbol": entry_candidate_symbol,
            "entry_final_symbol": entry_final_symbol,
            "position_focus_symbol": position_focus_symbol,
            "monitor_output_symbol": _clip(position_focus_symbol or entry_final_symbol, max_len=24),
            "open_position_count": open_position_count,
            "max_positions": _safe_int(monitor.get("max_positions")),
            "capacity_remaining": _safe_int(monitor.get("multi_position_capacity_remaining")),
            "entry_decision": str(monitor_output.get("intent_side") or "NOOP").strip().upper(),
            "entry_reason": _clip(entry_info.get("guard_reason") or entry_info.get("reason"), max_len=160),
            "entry_primary_failure_axis": _clip(entry_info.get("primary_failure_axis"), max_len=120),
            "exit_reason": _clip(exit_info.get("reason"), max_len=160),
            "exit_monitor_reason": _clip(exit_info.get("monitor_reason"), max_len=160),
        }
    return (monitor_focus_context,)
