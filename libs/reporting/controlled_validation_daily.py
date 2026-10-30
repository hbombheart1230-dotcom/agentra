from __future__ import annotations

import json
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from libs.reporting import controlled_validation_daily_build_projection as _build_owner
from libs.reporting import controlled_validation_daily_format_projection as _format_owner
from libs.reporting import controlled_validation_daily_read_projection as _read_owner
from libs.reporting import controlled_validation_daily_status_projection as _status_owner


LANE_LABELS = {
    "BTC_WOORI": "Q12 BTC-Woori",
    "Q10_SEMICONDUCTOR": "Q10 Semiconductor",
    "Q10_INDEX": "Q10 Index",
}


def _display_evaluation_status(
    *, lane_id: str, day: str, status: str, reason: str
) -> tuple[str, str]:
    """Do not present expected post-window expiry as a delivery incident."""
    return _status_owner._display_evaluation_status(lane_id=lane_id, day=day, status=status, reason=reason, facade=sys.modules[__name__])


def _read(path: Path) -> dict[str, Any]:
    return _read_owner._read(path, facade=sys.modules[__name__])


def _rows(payload: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    return _read_owner._rows(payload, key, facade=sys.modules[__name__])


def _executor_broker_outcome(reports_root: Path, day: str, run_id: str) -> dict[str, Any]:
    """2026-09-03 daily audit (P1-B): read the actual executor artifact for
    one run_id, to distinguish "the probe reservation was claimed" (what
    `submission_count` below has always measured -- it is written by
    graphs/nodes/monitor_node.py::record_probe_submission at Monitor
    decision time, before Commander approval or execute_from_packet ever
    run) from "a broker HTTP submission was actually attempted" (only
    knowable from executor.json's own submission_attempts/broker_outcome,
    written later by graphs/nodes/execute_from_packet.py). Read-only,
    best-effort: a missing/unreadable artifact yields an empty outcome
    rather than raising."""
    return _read_owner._executor_broker_outcome(reports_root, day, run_id, facade=sys.modules[__name__])


def build_controlled_validation_daily(
    *, reports_root: Path, day: str
) -> dict[str, Any]:
    return _build_owner.build_controlled_validation_daily(reports_root=reports_root, day=day, facade=sys.modules[__name__])


def render_controlled_validation_daily_lines(payload: Mapping[str, Any]) -> list[str]:
    return _format_owner.render_controlled_validation_daily_lines(payload, facade=sys.modules[__name__])


__all__ = [
    "build_controlled_validation_daily",
    "render_controlled_validation_daily_lines",
]
