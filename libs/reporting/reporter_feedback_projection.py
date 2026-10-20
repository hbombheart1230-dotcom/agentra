"""Deterministic strategist feedback projection (P1.5, DEV-A).

Owns the pure feedback aggregation moved from ``libs.reporting.reporter_feedback``: Reporter-analysis
blocker/recommendation extraction, dominant patterns, blocker/route analysis, recommendations, insight
summary, confidence and the evidence selection + packet assembly that precedes ``feedback_id``. Report,
metrics and trade-report reads, metrics generation and ``stable_evidence_id`` stay in the reporter_feedback
module. Helpers and sibling functions resolve on the injected module at call time to keep late patching identical.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _extract_reporter_analysis_blocker_totals(payload: Mapping[str, Any] | None, *, facade: Any) -> Dict[str, int]:
    row = dict(payload or {})
    monitor_eval = row.get("monitor_evaluation") if isinstance(row.get("monitor_evaluation"), dict) else {}
    supervisor = row.get("supervisor_activity") if isinstance(row.get("supervisor_activity"), dict) else {}
    intent_flow = row.get("intent_flow_analysis") if isinstance(row.get("intent_flow_analysis"), dict) else {}
    totals: Dict[str, int] = {}
    for key, value in dict(monitor_eval.get("monitor_reason_top") or {}).items():
        name = str(key or "").strip()
        if not name:
            continue
        totals[name] = totals.get(name, 0) + facade._safe_int(value, 0)
    for key, value in dict(supervisor.get("blocked_reason_top") or {}).items():
        name = str(key or "").strip()
        if not name:
            continue
        totals[name] = totals.get(name, 0) + facade._safe_int(value, 0)
    for key, value in dict(intent_flow.get("reason_top") or {}).items():
        name = str(key or "").strip()
        if not name or name.startswith("monitor:"):
            continue
        totals[name] = totals.get(name, 0) + facade._safe_int(value, 0)
    return totals


def _extract_reporter_analysis_recommendations(payload: Mapping[str, Any] | None, *, facade: Any) -> list[str]:
    row = dict(payload or {})
    operator = row.get("operator_facing_summary") if isinstance(row.get("operator_facing_summary"), dict) else {}
    direct = [str(x or "").strip() for x in list(row.get("improvement_suggestions") or []) if str(x or "").strip()]
    if direct:
        return direct[:4]
    recommended = [str(x or "").strip() for x in list(operator.get("recommended_actions") or []) if str(x or "").strip()]
    return recommended[:4]


def _build_dominant_patterns(
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


def _build_blocker_analysis(blocker_totals: Mapping[str, int], *, facade: Any) -> list[dict[str, Any]]:
    total = facade._safe_total(blocker_totals)
    ranked = sorted(((str(name), facade._safe_int(count, 0)) for name, count in blocker_totals.items()), key=lambda item: (-item[1], item[0]))
    out: list[dict[str, Any]] = []
    for name, count in ranked[:5]:
        out.append(
            {
                "blocker": name,
                "count": count,
                "ratio": facade._ratio(count, total),
            }
        )
    return out


def _build_route_analysis(route_summary: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    route_selected_total = dict(route_summary.get("route_selected_total") or {})
    route_total = facade._safe_total(route_selected_total)
    return {
        "route_source": str(route_summary.get("route_source") or "unavailable"),
        "route_selected_total": route_selected_total,
        "strategy_generation_mode_total": dict(route_summary.get("strategy_generation_mode_total") or {}),
        "strategist_fallback_total": facade._safe_int(route_summary.get("strategist_fallback_total"), 0),
        "route_source_run_count": facade._safe_int(route_summary.get("route_source_run_count"), 0),
        "route_source_missing_count": facade._safe_int(route_summary.get("route_source_missing_count"), 0),
        "route_source_breakdown": dict(route_summary.get("route_source_breakdown") or {}),
        "monitor_only_ratio": facade._ratio(facade._safe_int(route_selected_total.get("monitor_only"), 0), route_total),
        "cached_strategist_ratio": facade._ratio(facade._safe_int(route_selected_total.get("cached_strategist"), 0), route_total),
        "full_cycle_ratio": facade._ratio(facade._safe_int(route_selected_total.get("full_cycle"), 0), route_total),
    }


def _build_recommendations(
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


def _build_insight_summary(
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


def _build_confidence(
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


def assemble_feedback_packet(
    *,
    mode: str,
    row: Dict[str, Any],
    normalized_day: str,
    metrics_payload: Mapping[str, Any],
    trade_explain_payload: Mapping[str, Any],
    reporter_analysis_payload: Mapping[str, Any],
    trade_report_summary: Dict[str, Any],
    facade: Any,
) -> Dict[str, Any]:
    """Select route/blocker/freshness evidence and assemble the packet (before ``feedback_id``) from loaded inputs."""
    route_summary = facade._extract_route_summary(row)
    metrics_route_summary = facade._extract_route_summary(metrics_payload)
    trade_route_summary = facade._extract_route_summary(trade_explain_payload)
    reporter_route_summary = facade._extract_route_summary(reporter_analysis_payload)
    if not route_summary.get("route_selected_total"):
        if metrics_route_summary.get("route_selected_total"):
            route_summary = metrics_route_summary
        elif trade_route_summary.get("route_selected_total"):
            route_summary = trade_route_summary
        else:
            route_summary = reporter_route_summary

    blocker_totals = facade._extract_blocker_totals(metrics_payload)
    if not blocker_totals:
        blocker_totals = facade._extract_blocker_totals(trade_explain_payload)
    if not blocker_totals:
        blocker_totals = facade._extract_reporter_analysis_blocker_totals(reporter_analysis_payload)
    if not blocker_totals:
        blocker_totals = facade._extract_blocker_totals(row)

    freshness = facade._extract_freshness(row)
    if not freshness.get("latest_run_id"):
        freshness = facade._extract_freshness(metrics_payload) if metrics_payload else freshness
    if not freshness.get("latest_run_id"):
        freshness = facade._extract_freshness(trade_explain_payload) if trade_explain_payload else freshness
    if not freshness.get("latest_run_id"):
        freshness = facade._extract_freshness(reporter_analysis_payload) if reporter_analysis_payload else freshness

    route_analysis = facade._build_route_analysis(route_summary)
    blocker_analysis = facade._build_blocker_analysis(blocker_totals)
    dominant_patterns = facade._build_dominant_patterns(
        route_summary=route_summary,
        blocker_totals=blocker_totals,
        freshness=freshness,
        trade_report_summary=trade_report_summary,
    )
    recommendations = facade._build_recommendations(
        route_analysis=route_analysis,
        blocker_analysis=blocker_analysis,
        trade_report_summary=trade_report_summary,
    )
    reporter_analysis_recommendations = facade._extract_reporter_analysis_recommendations(reporter_analysis_payload)
    if reporter_analysis_recommendations and not metrics_payload:
        recommendations = reporter_analysis_recommendations[:4]
    elif not recommendations or recommendations == ["Route and blocker mix look balanced; continue observing for stable multi-session patterns before changing strategy."]:
        if reporter_analysis_recommendations:
            recommendations = reporter_analysis_recommendations[:4]
    confidence = facade._build_confidence(
        route_analysis=route_analysis,
        blocker_analysis=blocker_analysis,
        trade_report_summary=trade_report_summary,
    )

    return {
        "available": bool(route_analysis.get("route_selected_total")) or bool(blocker_analysis) or facade._safe_int(trade_report_summary.get("closed_trade_count"), 0) > 0,
        "packet_version": "strategist_feedback.v1",
        "source_day": normalized_day,
        "feedback_mode": "deterministic",
        "source_mode": str(mode or ""),
        "source_reports": {
            "metrics": bool(metrics_payload),
            "trade_explain": bool(trade_explain_payload),
            "reporter_analysis": bool(reporter_analysis_payload),
            "trade_reports": facade._safe_int(trade_report_summary.get("closed_trade_count"), 0) > 0,
            "current_payload": bool(row),
        },
        "insight_summary": facade._build_insight_summary(
            route_analysis=route_analysis,
            blocker_analysis=blocker_analysis,
            trade_report_summary=trade_report_summary,
        ),
        "dominant_patterns": dominant_patterns,
        "blocker_analysis": blocker_analysis,
        "route_analysis": route_analysis,
        "recommendation": recommendations,
        "confidence": confidence,
        "data_freshness": freshness,
        "trade_report_analysis": trade_report_summary,
        "runtime_semantics_unchanged": True,
    }
