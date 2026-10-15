"""Strategist: explanation fields from AI overrides and memory packet visibility.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations


def fill_strategist_output_explanations(ai_overrides, state, strategist_output, *, facade):
    for explanation_key in (
        "strategy_thesis",
        "strategy_delta_trace",
        "strategy_refresh_trace",
        "memory_usage_trace",
        "news_usage_trace",
        "scanner_handoff",
        "monitor_handoff",
        "conflict_analysis",
        "trade_permission_frame",
        "responsibility_boundary",
    ):
        if isinstance(ai_overrides.get(explanation_key), dict):
            strategist_output[explanation_key] = dict(ai_overrides.get(explanation_key) or {})
    strategist_output["memory_packet_visibility"] = facade.build_strategist_memory_packet_visibility(
        state=state,
        strategist_output=strategist_output,
    )
    return None
