"""report_source_helpers build_policy_surface_quality_snapshot (moved verbatim from report_source_helpers).

Module globals and helpers are resolved on ``facade`` (the report_source_helpers module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def build_policy_surface_quality_snapshot(events_path: Path, reports_root: Path, day: str, *, facade: Any) -> Dict[str, Any]:
    try:
        runtime_health = facade.build_phase_5_2_5_3_runtime_health(
            reports_root=reports_root,
            event_log_path=events_path,
            day=day,
            limit=500,
        )
    except FileNotFoundError:
        summary = facade.build_policy_surface_quality_summary([])
        chart_summary = facade.build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": facade.build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": facade.build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["no_canonical_monitor_runs_found"],
            },
        }
    except Exception:
        summary = facade.build_policy_surface_quality_summary([])
        chart_summary = facade.build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": facade.build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": facade.build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["policy_surface_quality_summary_unavailable"],
            },
        }

    summary = runtime_health.get("policy_surface_quality_summary")
    if not isinstance(summary, dict):
        summary = facade.build_policy_surface_quality_summary([])
    chart_summary = runtime_health.get("chart_structure_decision_hint_summary")
    if not isinstance(chart_summary, dict):
        chart_summary = facade.build_chart_structure_decision_hint_summary([])
    return {
        "summary": dict(summary),
        "executive_summary": facade.build_policy_surface_quality_executive_summary(summary),
        "chart_structure_summary": dict(chart_summary),
        "chart_structure_executive_summary": facade.build_chart_structure_decision_hint_executive_summary(chart_summary),
        "source": {
            "run_count": int(runtime_health.get("run_count") or 0),
            "date": day,
            "source": "daily_monitor_artifacts",
            "health_schema_version": str(runtime_health.get("schema_version") or ""),
        },
    }
