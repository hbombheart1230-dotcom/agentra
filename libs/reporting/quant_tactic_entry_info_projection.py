"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _entry_info_from_visibility(visibility: Mapping[str, Any], monitor: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    focus = facade._mapping(visibility.get("monitor_focus_context"))
    grouped = facade._mapping(visibility.get("entry_grouped_logic_trace"))
    cascade = facade._mapping(visibility.get("monitor_entry_candidate_cascade"))
    out: Dict[str, Any] = {}
    out.update(grouped)
    if focus:
        out.update(
            {
                "triggered": focus.get("entry_triggered"),
                "legacy_entry_decision": focus.get("entry_decision"),
                "guard_reason": focus.get("entry_guard_reason") or focus.get("entry_reason"),
                "reason": focus.get("entry_reason"),
                "primary_failure_axis": focus.get("entry_primary_failure_axis"),
                "cost_adjusted_edge_ok": focus.get("entry_cost_adjusted_edge_ok"),
                "cost_adjusted_edge_pct": focus.get("entry_cost_adjusted_edge_pct"),
                "cost_drag_pct": focus.get("entry_cost_drag_pct"),
                "entry_cost_filter": focus.get("entry_cost_filter"),
            }
        )
    if cascade:
        out.setdefault("reason", cascade.get("reason"))
        out.setdefault("primary_failure_axis", cascade.get("primary_failure_axis"))
    if monitor:
        out.setdefault("triggered", monitor.get("entry_triggered"))
        out.setdefault("legacy_entry_decision", monitor.get("entry_decision"))
    return {key: value for key, value in out.items() if value not in (None, "")}
