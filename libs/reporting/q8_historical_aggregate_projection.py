"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _aggregate_return_rows(rows: Sequence[Mapping[str, Any]], key: str, *, limit: int = 12, facade: Any) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[float]] = facade.defaultdict(list)
    for row in rows:
        value = facade._text(row.get(key)) or "missing"
        pnl = row.get("pnl_pct")
        if isinstance(pnl, (int, float)):
            grouped[value].append(float(pnl))
    out: List[Dict[str, Any]] = []
    for name, values in grouped.items():
        if not values:
            continue
        out.append(
            {
                "name": name,
                "count": len(values),
                "win_count": sum(1 for value in values if value > 0),
                "loss_count": sum(1 for value in values if value < 0),
                "win_rate": round(sum(1 for value in values if value > 0) / len(values), 4),
                "avg_return_pct": facade._avg(values),
            }
        )
    out.sort(key=lambda row: (int(row["count"]), abs(float(row["avg_return_pct"]))), reverse=True)
    return out[:limit]
