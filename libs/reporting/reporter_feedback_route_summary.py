"""``_extract_route_summary`` moved verbatim from reporter_feedback.py as ``extract_route_summary``.

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def extract_route_summary(payload: Mapping[str, Any] | None, *, facade: Any) -> Dict[str, Any]:
    row = dict(payload or {})
    nested = row.get("route_summary") if isinstance(row.get("route_summary"), dict) else {}
    route_selected_total = nested.get("route_selected_total")
    strategy_generation_mode_total = nested.get("strategy_generation_mode_total")
    strategist_fallback_total = nested.get("strategist_fallback_total")
    if not isinstance(route_selected_total, dict):
        route_selected_total = row.get("route_selected_total") if isinstance(row.get("route_selected_total"), dict) else {}
    if not isinstance(strategy_generation_mode_total, dict):
        strategy_generation_mode_total = row.get("strategist_mode_total") if isinstance(row.get("strategist_mode_total"), dict) else {}
    if strategist_fallback_total is None:
        strategist_fallback_total = row.get("strategist_fallback_total")
    return {
        "route_source": str(nested.get("route_source") or row.get("route_source") or "unavailable"),
        "route_source_run_count": facade._safe_int(nested.get("route_source_run_count") or row.get("route_source_run_count"), 0),
        "route_source_missing_count": facade._safe_int(nested.get("route_source_missing_count") or row.get("route_source_missing_count"), 0),
        "route_source_breakdown": dict(nested.get("route_source_breakdown") or row.get("route_source_breakdown") or {}),
        "route_selected_total": dict(route_selected_total or {}),
        "strategy_generation_mode_total": dict(strategy_generation_mode_total or {}),
        "strategist_fallback_total": facade._safe_int(strategist_fallback_total, 0),
    }
