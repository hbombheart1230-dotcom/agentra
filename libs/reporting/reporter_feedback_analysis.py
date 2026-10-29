"""Reporter feedback analysis projections (moved verbatim from reporter_feedback).

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def extract_reporter_analysis_recommendations(payload: Mapping[str, Any] | None) -> list[str]:
    row = dict(payload or {})
    operator = row.get("operator_facing_summary") if isinstance(row.get("operator_facing_summary"), dict) else {}
    direct = [str(x or "").strip() for x in list(row.get("improvement_suggestions") or []) if str(x or "").strip()]
    if direct:
        return direct[:4]
    recommended = [str(x or "").strip() for x in list(operator.get("recommended_actions") or []) if str(x or "").strip()]
    return recommended[:4]


def build_blocker_analysis(blocker_totals: Mapping[str, int], *, facade: Any) -> list[dict[str, Any]]:
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


def build_route_analysis(route_summary: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
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
