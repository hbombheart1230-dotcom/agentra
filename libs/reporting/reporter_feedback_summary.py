"""Reporter feedback narrative / confidence projections (moved verbatim from reporter_feedback).

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def build_insight_summary(
    *,
    route_analysis: Mapping[str, Any],
    blocker_analysis: list[dict[str, Any]],
    trade_report_summary: Mapping[str, Any] | None = None,
    facade: Any,
) -> str:
    parts: list[str] = []
    route_total = facade._safe_total(route_analysis.get("route_selected_total") if isinstance(route_analysis.get("route_selected_total"), dict) else {})
    if route_total > 0:
        route_counts = route_analysis.get("route_selected_total") if isinstance(route_analysis.get("route_selected_total"), dict) else {}
        monitor_only = facade._safe_int((route_counts or {}).get("monitor_only"), 0)
        cached = facade._safe_int((route_counts or {}).get("cached_strategist"), 0)
        leader = ""
        leader_count = 0
        if isinstance(route_counts, dict):
            leader, leader_count = max(
                ((str(name), facade._safe_int(count, 0)) for name, count in route_counts.items()),
                key=lambda item: item[1],
                default=("", 0),
            )
        if leader and leader_count > 0:
            parts.append(
                f"Route mix is led by {leader} {leader_count}/{route_total}; "
                f"monitor_only {monitor_only}/{route_total}, cached_strategist {cached}/{route_total}."
            )
        else:
            parts.append(
                f"Route mix recorded {route_total} routed decisions; "
                f"monitor_only {monitor_only}/{route_total}, cached_strategist {cached}/{route_total}."
            )
    if blocker_analysis:
        top = blocker_analysis[0]
        parts.append(f"Top blocker is {top.get('blocker')} ({top.get('count')}).")
    trade_summary = dict(trade_report_summary or {})
    closed_trade_count = facade._safe_int(trade_summary.get("closed_trade_count"), 0)
    if closed_trade_count > 0:
        win_count = facade._safe_int(trade_summary.get("win_count"), 0)
        loss_count = facade._safe_int(trade_summary.get("loss_count"), 0)
        flat_count = facade._safe_int(trade_summary.get("flat_count"), 0)
        unknown_pnl_count = facade._safe_int(trade_summary.get("unknown_pnl_count"), 0)
        avg_pnl_pct = trade_summary.get("avg_pnl_pct")
        pnl_pct_sample_count = facade._safe_int(trade_summary.get("pnl_pct_sample_count"), 0)
        result_bits = [f"{win_count} wins", f"{loss_count} losses"]
        if flat_count > 0:
            result_bits.append(f"{flat_count} flat")
        if unknown_pnl_count > 0:
            result_bits.append(f"{unknown_pnl_count} unknown pnl")
        avg_text = f", avg pnl pct {avg_pnl_pct}" if pnl_pct_sample_count > 0 else ""
        parts.append(
            f"Same-day closed trade reports show {closed_trade_count} trades with {', '.join(result_bits)}{avg_text}."
        )
    if not parts:
        parts.append("Feedback packet is available but source evidence is limited.")
    return " ".join(parts)


def build_confidence(
    *,
    route_analysis: Mapping[str, Any],
    blocker_analysis: list[dict[str, Any]],
    trade_report_summary: Mapping[str, Any] | None = None,
    facade: Any,
) -> str:
    route_total = facade._safe_total(route_analysis.get("route_selected_total") if isinstance(route_analysis.get("route_selected_total"), dict) else {})
    blocker_total = sum(facade._safe_int(item.get("count"), 0) for item in list(blocker_analysis or []))
    trade_summary = dict(trade_report_summary or {})
    closed_trade_count = facade._safe_int(trade_summary.get("closed_trade_count"), 0)
    broker_truth_count = facade._safe_int(trade_summary.get("broker_truth_count"), 0)
    if route_total >= 50 and len(blocker_analysis) >= 3:
        return "high"
    if route_total >= 10:
        return "medium"
    if closed_trade_count >= 3 and broker_truth_count >= 2:
        return "high"
    if closed_trade_count >= 1 and broker_truth_count >= 1:
        return "medium"
    if blocker_total >= 20 and len(blocker_analysis) >= 2:
        return "high"
    if blocker_total >= 5 and len(blocker_analysis) >= 1:
        return "medium"
    return "low"
