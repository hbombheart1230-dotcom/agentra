"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping


def _pattern_rows_from_daily_summaries(
    reports_root: Path,
    *,
    start: str,
    end: str,
    section: str,
    group_key: str,
    facade: Any,
) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = facade.defaultdict(
        lambda: {
            "count": 0,
            "closed_or_realized_count": 0,
            "win_count": 0,
            "loss_count": 0,
            "flat_count": 0,
            "return_sum": 0.0,
            "return_weight": 0,
            "cost_drag_loss_count": 0,
        }
    )
    for day in facade._iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = facade._read_json(path)
        pattern = payload.get("pattern_performance") if isinstance(payload.get("pattern_performance"), dict) else {}
        section_payload = pattern.get(section) if isinstance(pattern.get(section), dict) else {}
        rows = section_payload.get(group_key) if isinstance(section_payload.get(group_key), list) else []
        for row in rows:
            if not isinstance(row, facade.Mapping):
                continue
            name = facade._text(row.get("name")) or "missing"
            bucket = grouped[name]
            count = facade._int(row.get("count"))
            closed = facade._int(row.get("closed_or_realized_count") or count)
            avg = facade._float(row.get("avg_return_pct"))
            bucket["count"] += count
            bucket["closed_or_realized_count"] += closed
            bucket["win_count"] += facade._int(row.get("win_count"))
            bucket["loss_count"] += facade._int(row.get("loss_count"))
            bucket["flat_count"] += facade._int(row.get("flat_count"))
            bucket["cost_drag_loss_count"] += facade._int(row.get("cost_drag_loss_count"))
            if avg is not None and closed > 0:
                bucket["return_sum"] += float(avg) * closed
                bucket["return_weight"] += closed
    out: List[Dict[str, Any]] = []
    for name, bucket in grouped.items():
        closed = int(bucket.get("closed_or_realized_count") or 0)
        wins = int(bucket.get("win_count") or 0)
        out.append(
            {
                "name": name,
                "count": int(bucket.get("count") or 0),
                "closed_or_realized_count": closed,
                "win_count": wins,
                "loss_count": int(bucket.get("loss_count") or 0),
                "flat_count": int(bucket.get("flat_count") or 0),
                "win_rate": round(wins / closed, 4) if closed else 0.0,
                "avg_return_pct": facade._weighted_avg(float(bucket.get("return_sum") or 0.0), int(bucket.get("return_weight") or 0)),
                "cost_drag_loss_count": int(bucket.get("cost_drag_loss_count") or 0),
            }
        )
    out.sort(key=lambda row: (int(row.get("closed_or_realized_count") or 0), abs(float(row.get("avg_return_pct") or 0.0))), reverse=True)
    return out
