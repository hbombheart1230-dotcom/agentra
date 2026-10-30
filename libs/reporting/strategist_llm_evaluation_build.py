"""Strategist LLM evaluation payload builder (moved verbatim from strategist_llm_evaluation).

Helpers are resolved on ``facade`` (the strategist_llm_evaluation module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


def build_strategist_llm_evaluation(
    rows: Iterable[Mapping[str, Any]],
    shadow_payloads: Iterable[Mapping[str, Any]] = (),
    *,
    facade: Any,
) -> Dict[str, Any]:
    closed = facade._closed_rows(rows)
    tactic_rows = facade._tactic_performance(closed)
    primary = str(tactic_rows[0]["name"]) if tactic_rows else ""
    shadow_rows = facade._shadow_rows(shadow_payloads)
    shadow_diag = facade._shadow_shape_diagnostics(shadow_rows)
    overused = ""
    if tactic_rows and int(tactic_rows[0].get("count") or 0) >= 3 and float(tactic_rows[0].get("avg_return_pct") or 0.0) < 0.0:
        overused = str(tactic_rows[0].get("name") or "")
    underused = ""
    would_shapes = list(shadow_diag.get("would_enter_by_shape") or [])
    if would_shapes:
        underused = str(would_shapes[0].get("name") or "")
    elif int(shadow_diag.get("opening_would_enter_count") or 0) > 0:
        underused = "opening"
    return {
        "schema_version": "strategist_llm_evaluation.v1",
        "behavior_effect": "evaluation_only",
        "closed_or_realized_sample_count": len(closed),
        "selected_primary_tactic": primary,
        "selected_primary_lane": facade._shape_from_tactic(primary),
        "tactic_performance": tactic_rows[:8],
        "shadow_shape_diagnostics": shadow_diag,
        "lane_selection_quality": facade._quality_label(rows=closed, primary_tactic=primary, shadow=shadow_diag),
        "overused_lane_or_tactic": overused,
        "underused_shadow_lane": underused,
        "call_effectiveness": {
            "status": "not_available",
            "reason": "strategist_llm_call_trace_not_linked_to_operator_summary",
        },
    }
