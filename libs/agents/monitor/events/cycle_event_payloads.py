"""Monitor cycle: raw input snapshot persisted before the entry/exit decision.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::monitor_node` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_monitor_raw_input_snapshot(all_pos_map, commander_context, commander_entry_control, monitor_policy, open_position_count, selected, strategist_output, strategist_plan, *, facade):
    return (
        {
                "selected_symbol": (
                    str(selected.get("symbol") or "")
                    if isinstance(selected, dict)
                    else ""
                ),
                "selected_snapshot": (
                    {
                        "symbol": str(selected.get("symbol") or ""),
                        "score": selected.get("score"),
                        "risk_score": selected.get("risk_score"),
                        "confidence": selected.get("confidence"),
                        "price_source": str(selected.get("_monitor_price_source") or ""),
                        "feature_source": str(selected.get("_monitor_feature_source") or ""),
                    }
                    if isinstance(selected, dict)
                    else {}
                ),
                "open_position_count": int(open_position_count),
                "positions": {
                    str(k): {"qty": facade._to_int((v or {}).get("qty")), "avg_price": (v or {}).get("avg_price")}
                    for k, v in list(all_pos_map.items())[:20]
                },
                "monitor_policy": dict(monitor_policy),
                "strategist_guidance": {
                    "playbook": str(strategist_output.get("playbook") or ""),
                    "monitor_guidance": str(strategist_output.get("monitor_guidance") or ""),
                    "risk_tone": str(strategist_output.get("risk_tone") or ""),
                    "trade_aggressiveness": str(strategist_output.get("trade_aggressiveness") or ""),
                },
                "commander_context": {
                    "monitor_mission": str(commander_context.get("monitor_mission") or ""),
                    "flow_instruction": str(commander_context.get("flow_instruction") or ""),
                    "command_intent": str(commander_context.get("command_intent") or ""),
                    "risk_mode": str(commander_context.get("risk_mode") or ""),
                    "no_trade_reason_code": str(commander_context.get("no_trade_reason_code") or ""),
                    "llm_policy": str(commander_context.get("llm_policy") or ""),
                    "source_priority": list(commander_context.get("source_priority") or []),
                    "entry_control": dict(commander_entry_control),
                },
                "strategist_plan": {
                    "selected_playbook": str(strategist_plan.get("selected_playbook") or ""),
                    "entry_plan": dict(strategist_plan.get("entry_plan") or {}),
                    "exit_plan": dict(strategist_plan.get("exit_plan") or {}),
                    "symbol_constraints": dict(strategist_plan.get("symbol_constraints") or {}),
                    "strategy_summary": str(strategist_plan.get("strategy_summary") or ""),
                },
            }
    )

def build_state_transition_event_payload(current_posture, current_reason, entry_info, entry_transition_trace, exit_info, previous_monitor_state, previous_posture, previous_reason, state_changed):
    return (
        {
            "previous_posture": previous_posture,
            "current_posture": current_posture,
            "previous_reason": previous_reason,
            "current_reason": current_reason,
            "state_changed": bool(state_changed),
            "trigger_delta": {
                "previous_active_exit_axis": str(previous_monitor_state.get("active_exit_axis") or ""),
                "current_active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
                "exit_triggered": bool(exit_info.get("triggered")),
                "entry_triggered": bool(entry_info.get("triggered")),
                "entry_pattern": str(entry_info.get("pattern") or ""),
                "became_ready_this_cycle": bool(entry_transition_trace.get("became_ready_this_cycle")),
                "last_blocking_axis": str(entry_transition_trace.get("last_blocking_axis") or ""),
                "transition_readiness_score": entry_transition_trace.get("transition_readiness_score"),
            },
        }
    )

def build_cycle_summary_event_payload(buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_post_exit_cooldown, current_posture, current_reason, entry_blocker_surface, entry_info, exit_info, intents, monitor_symbol, open_position_count, selected, state):
    return (
        {
            "selected_symbol": str((selected.get("symbol") if isinstance(selected, dict) else "") or ""),
            "monitor_symbol": monitor_symbol,
            "posture": current_posture,
            "monitor_reason": current_reason,
            "open_position_count": int(open_position_count),
            "has_intent": bool(intents),
            "intent_side": str((state.get("monitor_output") or {}).get("intent_side") or "NOOP"),
            "active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
            "price_source": str(exit_info.get("price_source") or ""),
            "peak_update": (
                dict(state["peak_update_events"][-1])
                if isinstance(state.get("peak_update_events"), list)
                and state.get("peak_update_events")
                else {}
            ),
            "feature_source": str(exit_info.get("feature_source") or ""),
            "entry_evaluated": bool(entry_info.get("evaluated")),
            "entry_triggered": bool(entry_info.get("triggered")),
            "entry_pattern": str(entry_info.get("pattern") or ""),
            "buy_blocked_open_position": bool(buy_blocked_open_position),
            "buy_blocked_closeout_window": bool(buy_blocked_closeout_window),
            "buy_blocked_post_exit_cooldown": bool(buy_blocked_post_exit_cooldown),
            "minutes_to_close": entry_info.get("minutes_to_close"),
            "eod_flat_cutoff_min": int(entry_info.get("eod_flat_cutoff_min") or 0),
            "buy_closeout_cutoff_min": int(entry_info.get("buy_closeout_cutoff_min") or 0),
            "closeout_window_active": bool(entry_info.get("closeout_window_active")),
            "entry_blocker_surface": dict(entry_blocker_surface),
        }
    )

def build_decision_bridge_raw_input(intents, monitor_policy, selected, *, facade):
    return (
        {
                "selected_symbol": (
                    str(selected.get("symbol") or "")
                    if isinstance(selected, dict)
                    else ""
                ),
                "monitor_policy": dict(monitor_policy),
                "intents_preview": [
                    {
                        "symbol": str(x.get("symbol") or ""),
                        "side": str(x.get("side") or ""),
                        "qty": facade._to_int(x.get("qty")),
                    }
                    for x in list(intents)[:3]
                    if isinstance(x, dict)
                ],
            }
    )
