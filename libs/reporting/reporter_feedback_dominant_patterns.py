"""``_build_dominant_patterns`` moved verbatim from reporter_feedback.py as ``build_dominant_patterns``.

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def build_dominant_patterns(
    *,
    route_summary: Mapping[str, Any],
    blocker_totals: Mapping[str, int],
    freshness: Mapping[str, Any],
    trade_report_summary: Mapping[str, Any] | None = None,
    facade: Any,
) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    route_total = facade._safe_total(route_summary.get("route_selected_total") if isinstance(route_summary.get("route_selected_total"), dict) else {})
    route_selected_total = route_summary.get("route_selected_total") if isinstance(route_summary.get("route_selected_total"), dict) else {}
    if route_total > 0:
        for name in ("monitor_only", "cached_strategist", "full_cycle"):
            count = facade._safe_int(route_selected_total.get(name), 0)
            if count <= 0:
                continue
            patterns.append(
                {
                    "name": f"{name}_ratio",
                    "value": facade._ratio(count, route_total),
                    "detail": f"{name} {count}/{route_total} runs",
                }
            )

    blocker_total = facade._safe_total(blocker_totals)
    reclaim_total = sum(count for name, count in blocker_totals.items() if "reclaim" in str(name))
    if reclaim_total > 0 and blocker_total > 0:
        patterns.append(
            {
                "name": "reclaim_blocked_ratio",
                "value": facade._ratio(reclaim_total, blocker_total),
                "detail": f"reclaim-related blockers {reclaim_total}/{blocker_total}",
            }
        )

    fallback_total = facade._safe_int(route_summary.get("strategist_fallback_total"), 0)
    if fallback_total > 0 and route_total > 0:
        patterns.append(
            {
                "name": "strategist_fallback_ratio",
                "value": facade._ratio(fallback_total, route_total),
                "detail": f"fallback observed in {fallback_total}/{route_total} route-tagged runs",
            }
        )

    if freshness:
        patterns.append(
            {
                "name": "freshness_status",
                "value": str(freshness.get("freshness_status") or "unknown"),
                "detail": str(freshness.get("source_window_summary") or ""),
            }
        )
    trade_summary = dict(trade_report_summary or {})
    closed_trade_count = facade._safe_int(trade_summary.get("closed_trade_count"), 0)
    if closed_trade_count > 0:
        patterns.append(
            {
                "name": "same_day_closed_trade_count",
                "value": closed_trade_count,
                "detail": f"closed trade reports {closed_trade_count}",
            }
        )
        patterns.append(
            {
                "name": "same_day_avg_pnl_pct",
                "value": trade_summary.get("avg_pnl_pct"),
                "detail": f"average same-day pnl pct {trade_summary.get('avg_pnl_pct')}",
            }
        )
        cost_loss_count = facade._safe_int(trade_summary.get("same_price_cost_loss_count"), 0)
        if cost_loss_count > 0:
            patterns.append(
                {
                    "name": "same_price_cost_loss_ratio",
                    "value": facade._ratio(cost_loss_count, closed_trade_count),
                    "detail": f"same-price cost-loss trades {cost_loss_count}/{closed_trade_count}",
                }
            )
    return patterns[:6]
