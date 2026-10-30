"""Strategist LLM evaluation performance formatting (moved verbatim from strategist_llm_evaluation).

Helpers are resolved on ``facade`` (the strategist_llm_evaluation module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _format_perf(rows: Sequence[Mapping[str, Any]], *, limit: int = 3, facade: Any) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = facade._text(row.get("name"))
        if not name:
            continue
        parts.append(
            f"{name} ({row.get('count')}, win {float(row.get('win_rate') or 0.0) * 100:.1f}%, avg {float(row.get('avg_return_pct') or 0.0):.2f}%)"
        )
    return ", ".join(parts) if parts else "none"


def render_strategist_llm_evaluation_lines(payload: Mapping[str, Any] | None, *, facade: Any) -> List[str]:
    evaluation = dict(payload or {})
    if not evaluation:
        return []
    shadow = evaluation.get("shadow_shape_diagnostics") if isinstance(evaluation.get("shadow_shape_diagnostics"), facade.Mapping) else {}
    lines = [
        "",
        "## Strategist LLM Evaluation",
        "",
        "- Strategist lane quality: "
        f"`{evaluation.get('lane_selection_quality') or 'not_available'}` / "
        f"primary `{evaluation.get('selected_primary_tactic') or 'none'}` "
        f"({evaluation.get('selected_primary_lane') or 'unavailable'}) / "
        f"samples {evaluation.get('closed_or_realized_sample_count') or 0}",
        f"- Strategist tactic performance: {facade._format_perf(list(evaluation.get('tactic_performance') or []))}",
        "- Strategist shadow contrast: "
        f"candidates {shadow.get('candidate_count') or 0}, "
        f"opening would-enter {shadow.get('opening_would_enter_count') or 0}",
        f"- Strategist overused: {evaluation.get('overused_lane_or_tactic') or 'none'} / underused shadow lane: {evaluation.get('underused_shadow_lane') or 'none'}",
        "- Strategist call effectiveness: "
        f"{(evaluation.get('call_effectiveness') or {}).get('status') if isinstance(evaluation.get('call_effectiveness'), facade.Mapping) else 'not_available'}",
    ]
    return lines
