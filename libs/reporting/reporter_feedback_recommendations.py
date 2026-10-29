"""``_build_recommendations`` moved verbatim from reporter_feedback.py as ``build_recommendations``.

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def build_recommendations(
    *,
    route_analysis: Mapping[str, Any],
    blocker_analysis: list[dict[str, Any]],
    trade_report_summary: Mapping[str, Any] | None = None,
    facade: Any,
) -> list[str]:
    recommendations: list[str] = []
    if float(route_analysis.get("monitor_only_ratio") or 0.0) >= 0.5:
        recommendations.append("Monitor-only share is high; review hold-management concentration before widening entry tuning.")
    if float(route_analysis.get("cached_strategist_ratio") or 0.0) >= 0.25:
        recommendations.append("Cached strategist reuse is elevated; compare refresh cadence against fresh full-cycle opportunities.")
    if blocker_analysis:
        top_blocker = blocker_analysis[0]
        blocker_name = str(top_blocker.get("blocker") or "")
        if blocker_name:
            recommendations.append(f"Top blocker is {blocker_name}; inspect whether this gate is dominating no-trade outcomes.")
        if "reclaim" in blocker_name:
            recommendations.append("VWAP reclaim-related failures are prominent; review reclaim readiness evidence before loosening thresholds.")
    trade_summary = dict(trade_report_summary or {})
    closed_trade_count = facade._safe_int(trade_summary.get("closed_trade_count"), 0)
    if closed_trade_count > 0:
        same_price_cost_loss_count = facade._safe_int(trade_summary.get("same_price_cost_loss_count"), 0)
        win_count = facade._safe_int(trade_summary.get("win_count"), 0)
        loss_count = facade._safe_int(trade_summary.get("loss_count"), 0)
        if same_price_cost_loss_count > 0:
            recommendations.append("Same-price round trips produced fee/tax drag; tighten follow-through evidence before repeating quick reversals.")
        if loss_count > win_count:
            recommendations.append("Same-day closed trades are loss-heavy; keep defensive entry posture until follow-through quality improves.")
    if not recommendations:
        recommendations.append("Route and blocker mix look balanced; continue observing for stable multi-session patterns before changing strategy.")
    return recommendations[:4]
