from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from libs.reporting.chart_structure_decision_hint_summary import (
    build_chart_structure_decision_hint_executive_summary,
    build_chart_structure_decision_hint_summary,
)
from libs.reporting.policy_surface_summary import (
    build_policy_surface_quality_executive_summary,
    build_policy_surface_quality_summary,
)
from libs.reporting.phase_runtime_health import build_phase_5_2_5_3_runtime_health
from libs.reporting import report_source_read_projection as _read_owner
from libs.reporting import report_source_clock_projection as _clock_owner
from libs.reporting import report_source_route_projection as _route_owner


def read_json(path: Path) -> Dict[str, Any]:
    return _read_owner.read_json(path, facade=sys.modules[__name__])


def to_epoch(ts: Any) -> int:
    return _clock_owner.to_epoch(ts, facade=sys.modules[__name__])


def utc_day(ts: Any) -> str:
    return _clock_owner.utc_day(ts, facade=sys.modules[__name__])


def utc_now_iso() -> str:
    return _clock_owner.utc_now_iso(facade=sys.modules[__name__])


def epoch_to_iso(epoch: Any) -> str:
    return _clock_owner.epoch_to_iso(epoch, facade=sys.modules[__name__])


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    return _read_owner.iter_jsonl(path, facade=sys.modules[__name__])


def build_policy_surface_quality_snapshot(events_path: Path, reports_root: Path, day: str) -> Dict[str, Any]:
    try:
        runtime_health = build_phase_5_2_5_3_runtime_health(
            reports_root=reports_root,
            event_log_path=events_path,
            day=day,
            limit=500,
        )
    except FileNotFoundError:
        summary = build_policy_surface_quality_summary([])
        chart_summary = build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["no_canonical_monitor_runs_found"],
            },
        }
    except Exception:
        summary = build_policy_surface_quality_summary([])
        chart_summary = build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["policy_surface_quality_summary_unavailable"],
            },
        }

    summary = runtime_health.get("policy_surface_quality_summary")
    if not isinstance(summary, dict):
        summary = build_policy_surface_quality_summary([])
    chart_summary = runtime_health.get("chart_structure_decision_hint_summary")
    if not isinstance(chart_summary, dict):
        chart_summary = build_chart_structure_decision_hint_summary([])
    return {
        "summary": dict(summary),
        "executive_summary": build_policy_surface_quality_executive_summary(summary),
        "chart_structure_summary": dict(chart_summary),
        "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
        "source": {
            "run_count": int(runtime_health.get("run_count") or 0),
            "date": day,
            "source": "daily_monitor_artifacts",
            "health_schema_version": str(runtime_health.get("schema_version") or ""),
        },
    }


def _commander_route_from_payload(payload: Dict[str, Any], *, artifact_path: str = "") -> Dict[str, Any]:
    return _route_owner._commander_route_from_payload(payload, artifact_path=artifact_path)


def _event_route_rows(day_rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return _route_owner._event_route_rows(day_rows, facade=sys.modules[__name__])


def build_commander_route_summary(
    *,
    reports_root: Path,
    day: str,
    day_rows: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    canonical_dir = reports_root / "canonical" / day
    canonical_by_run: Dict[str, Dict[str, Any]] = {}
    if canonical_dir.exists():
        for run_dir in sorted(canonical_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            commander = read_json(run_dir / "commander.json")
            if not commander:
                continue
            row = _commander_route_from_payload(commander, artifact_path=str(run_dir / "commander.json"))
            if row.get("route_selected"):
                canonical_by_run[str(run_dir.name)] = row

    event_rows = day_rows or []
    event_by_run = _event_route_rows(event_rows)

    all_run_ids = set(canonical_by_run) | set(event_by_run)

    by_run: Dict[str, Dict[str, Any]] = {}
    route_selected_total: Counter[str] = Counter()
    strategy_generation_mode_total: Counter[str] = Counter()
    strategist_fallback_total = 0
    source_breakdown: Counter[str] = Counter()
    missing_count = 0

    for run_id in sorted(all_run_ids):
        selected = canonical_by_run.get(run_id)
        if not selected:
            selected = event_by_run.get(run_id)
        if not selected or not str(selected.get("route_selected") or "").strip():
            missing_count += 1
            continue
        by_run[run_id] = dict(selected)
        route_selected_total[str(selected.get("route_selected"))] += 1
        mode = str(selected.get("strategy_generation_mode") or "").strip()
        if mode:
            strategy_generation_mode_total[mode] += 1
        if bool(selected.get("strategist_fallback_used")):
            strategist_fallback_total += 1
        source_breakdown[str(selected.get("route_source") or "unknown")] += 1

    return {
        "route_source": "canonical_commander_preferred",
        "route_source_run_count": int(len(by_run)),
        "route_source_missing_count": int(missing_count),
        "route_selected_total": dict(route_selected_total),
        "strategy_generation_mode_total": dict(strategy_generation_mode_total),
        "strategist_fallback_total": int(strategist_fallback_total),
        "route_source_breakdown": dict(source_breakdown),
        "by_run": by_run,
    }
