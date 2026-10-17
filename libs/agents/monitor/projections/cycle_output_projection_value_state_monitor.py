"""Monitor cycle output projection: monitor_output, sizing, quant result and entry/exit snapshots.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def cycle_output_value_state_monitor_output(monitor_entry_exit_reason, intents, entry_candidate_cascade, quant_entry_factor_snapshot, quant_entry_decision, quant_entry_enforcement, quant_exit_decision, selected, entry_info, exit_info, *, facade):
    return (
{
        "selected_symbol": (selected.get("symbol") if isinstance(selected, dict) else None),
        "intent_side": (str(intents[0].get("side")) if intents else "NOOP"),
        "intent_qty": (int(intents[0].get("qty") or 0) if intents else 0),
        "entry_exit_reason": monitor_entry_exit_reason,
        "entry_candidate_cascade": dict(entry_candidate_cascade),
        "entry_lane": str(entry_info.get("entry_lane") or "strict"),
        "entry_cost_filter": dict(entry_info.get("entry_cost_filter") or {}),
        "directional_edge_estimate": dict(
            entry_info.get("directional_edge_estimate") or {}
        ),
        "entry_quality_gate": dict(entry_info.get("entry_quality_gate") or {}),
        "cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
        "cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
        "cost_drag_pct": entry_info.get("cost_drag_pct"),
        "exit_vs_strategy_intent": dict(exit_info.get("exit_vs_strategy_intent") or {}),
        "quant_factor_snapshot": dict(quant_entry_factor_snapshot),
        "entry_quant_decision": dict(quant_entry_decision),
        "quant_entry_enforcement": dict(quant_entry_enforcement),
        "market_rail_translation": dict(entry_info.get("market_rail_translation") or {}),
        "risk_off_defensive_observe_policy": dict(entry_info.get("risk_off_defensive_observe_policy") or {}),
        "exit_quant_decision": dict(quant_exit_decision),
    }
    )
