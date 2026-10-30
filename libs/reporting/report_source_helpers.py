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
from libs.reporting import report_source_policy_projection as _policy_owner
from libs.reporting import report_source_route_summary_projection as _route_summary_owner


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
    return _policy_owner.build_policy_surface_quality_snapshot(events_path, reports_root, day, facade=sys.modules[__name__])


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
    return _route_summary_owner.build_commander_route_summary(reports_root=reports_root, day=day, day_rows=day_rows, facade=sys.modules[__name__])
