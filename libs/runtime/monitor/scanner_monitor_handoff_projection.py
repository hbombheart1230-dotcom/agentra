"""Monitor cycle: Scanner-to-Monitor handoff surface with selection and cascade evidence.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::monitor_node` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_scanner_monitor_handoff_for_cycle(entry_candidate_cascade, entry_info, final_entry_decision, monitor_no_trade_surface, scanner_selected_snapshot, selected, state, *, facade):
    scanner_monitor_handoff = facade.build_scanner_monitor_handoff_surface(
        selected=scanner_selected_snapshot if isinstance(scanner_selected_snapshot, dict) else {},
        ranked_candidates=[row for row in list(state.get("ranked_candidates") or []) if isinstance(row, dict)],
        scanner_output=state.get("scanner_output") if isinstance(state.get("scanner_output"), dict) else {},
        final_decision=final_entry_decision,
        no_trade_surface=monitor_no_trade_surface,
        entry_info=entry_info,
    )
    scanner_monitor_handoff["monitor_selected_symbol"] = str((selected or {}).get("symbol") or "")
    scanner_monitor_handoff["entry_candidate_cascade"] = dict(entry_candidate_cascade)
    return scanner_monitor_handoff
