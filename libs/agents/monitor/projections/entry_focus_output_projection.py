"""Monitor cycle: entry focus and candidate evidence projected onto monitor_output.

T4-B (P1.5 Third Pass): the ordered `state["monitor_output"][KEY] = VALUE` run of `graphs/nodes/monitor_node.py::monitor_node`
is evaluated here verbatim into an insertion-ordered mapping; the orchestrator applies it with a single `dict.update` at the
original position. Values are pure reads of the passed evidence; State mutation stays at the orchestrator boundary.
"""
from __future__ import annotations


def build_entry_focus_monitor_output(entry_blocker_surface, entry_candidate_symbol, entry_cost_filter_snapshot, entry_final_symbol, entry_info, final_entry_decision, monitor_focus_context, monitor_focus_mode, monitor_output_symbol, position_focus_symbol, scanner_selected_symbol):
    out = {}
    out["entry_blocker_surface"] = dict(entry_blocker_surface)
    out["monitor_focus_context"] = dict(monitor_focus_context)
    out["scanner_selected_symbol"] = scanner_selected_symbol
    out["entry_candidate_symbol"] = entry_candidate_symbol
    out["entry_final_symbol"] = entry_final_symbol
    out["position_focus_symbol"] = position_focus_symbol
    out["monitor_output_symbol"] = monitor_output_symbol
    out["monitor_focus_mode"] = monitor_focus_mode
    out["entry_candidate_decision"] = final_entry_decision
    out["entry_candidate_reason"] = str(
        entry_info.get("guard_reason") or entry_info.get("reason") or "entry_wait"
    )
    out["entry_candidate_primary_failure_axis"] = str(
        entry_info.get("primary_failure_axis") or ""
    )
    out["entry_candidate_cost_adjusted_edge_ok"] = bool(
        entry_info.get("cost_adjusted_edge_ok")
    )
    out["entry_candidate_cost_adjusted_edge_pct"] = entry_info.get("cost_adjusted_edge_pct")
    out["entry_candidate_cost_drag_pct"] = entry_info.get("cost_drag_pct")
    out["entry_candidate_cost_filter"] = dict(entry_cost_filter_snapshot)
    return out
