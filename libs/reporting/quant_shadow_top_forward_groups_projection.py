"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping


def _top_forward_groups(groups: Mapping[str, List[Mapping[str, Any]]], *, limit: int = 10, facade: Any) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for name, rows in groups.items():
        summary = facade._forward_outcome_summary(rows)
        if int(summary.get("observed_count") or 0) <= 0:
            continue
        summary["name"] = name
        summaries.append(summary)
    summaries.sort(
        key=lambda item: (
            float(item.get("avg_return_5m_pct") or item.get("avg_return_3m_pct") or -999.0),
            int(item.get("observed_count") or 0),
        ),
        reverse=True,
    )
    return summaries[:limit]
