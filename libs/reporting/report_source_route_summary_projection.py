"""report_source_helpers build_commander_route_summary (moved verbatim from report_source_helpers).

Module globals and helpers are resolved on ``facade`` (the report_source_helpers module) at call time; this module never imports it.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def build_commander_route_summary(
    *,
    reports_root: Path,
    day: str,
    day_rows: Optional[Iterable[Dict[str, Any]]] = None,
    facade: Any,
) -> Dict[str, Any]:
    canonical_dir = reports_root / "canonical" / day
    canonical_by_run: Dict[str, Dict[str, Any]] = {}
    if canonical_dir.exists():
        for run_dir in sorted(canonical_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            commander = facade.read_json(run_dir / "commander.json")
            if not commander:
                continue
            row = facade._commander_route_from_payload(commander, artifact_path=str(run_dir / "commander.json"))
            if row.get("route_selected"):
                canonical_by_run[str(run_dir.name)] = row

    event_rows = day_rows or []
    event_by_run = facade._event_route_rows(event_rows)

    all_run_ids = set(canonical_by_run) | set(event_by_run)

    by_run: Dict[str, Dict[str, Any]] = {}
    route_selected_total: Counter[str] = facade.Counter()
    strategy_generation_mode_total: Counter[str] = facade.Counter()
    strategist_fallback_total = 0
    source_breakdown: Counter[str] = facade.Counter()
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
