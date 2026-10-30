"""Strategist LLM evaluation tactic/shadow projections (moved verbatim from strategist_llm_evaluation).

Helpers are resolved on ``facade`` (the strategist_llm_evaluation module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _tactic_performance(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Mapping[str, Any]]] = {}
    for row in rows:
        tactic = facade._tactic(row)
        if not tactic:
            continue
        grouped.setdefault(tactic, []).append(row)
    out: List[Dict[str, Any]] = []
    for tactic, items in grouped.items():
        returns = [facade._result_pct(row) for row in items]
        wins = sum(1 for value in returns if value > 0.0)
        losses = sum(1 for value in returns if value < 0.0)
        out.append(
            {
                "name": tactic,
                "shape": facade._shape_from_tactic(tactic),
                "count": len(items),
                "win_count": wins,
                "loss_count": losses,
                "win_rate": float(wins) / float(len(items)) if items else 0.0,
                "avg_return_pct": sum(returns) / float(len(returns)) if returns else 0.0,
            }
        )
    out.sort(key=lambda row: (int(row.get("count") or 0), abs(float(row.get("avg_return_pct") or 0.0))), reverse=True)
    return out


def _shadow_shape_diagnostics(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    shapes = facade.Counter(facade._shape_from_reason(facade._text(row.get("reason")), facade._text(row.get("primary_failure_axis"))) for row in rows)
    would_enter_shapes = facade.Counter(
        facade._shape_from_reason(facade._text(row.get("reason")), facade._text(row.get("primary_failure_axis")))
        for row in rows
        if facade._bool(row.get("would_enter"))
    )
    opening_would = sum(1 for row in rows if facade._bool(row.get("opening_momentum_probe_would_enter")) or facade._bool(row.get("opening_largecap_surge_would_enter")))
    return {
        "candidate_count": len(rows),
        "by_shape": facade._top_counter(shapes),
        "would_enter_by_shape": facade._top_counter(would_enter_shapes),
        "opening_would_enter_count": opening_would,
    }
