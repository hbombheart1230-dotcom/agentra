"""Controlled validation daily read projections (moved verbatim from controlled_validation_daily).

Globals/helpers are resolved on ``facade`` (the controlled_validation_daily module) at call time; this module never imports it.
Read-only; no writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def _read(path: Path, *, facade: Any) -> dict[str, Any]:
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, facade.json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, facade.Mapping) else {}



def _rows(payload: Mapping[str, Any], key: str, *, facade: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in list(payload.get(key) or []) if isinstance(row, facade.Mapping)]



def _executor_broker_outcome(reports_root: Path, day: str, run_id: str, *, facade: Any) -> dict[str, Any]:
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
    if not run_id:
        return {"broker_outcome": "", "submission_attempts": 0}
    path = facade.Path(reports_root) / "canonical" / day / run_id / "executor.json"
    payload = facade._read(path)
    try:
        submission_attempts = int(payload.get("submission_attempts") or 0)
    except (TypeError, ValueError):
        submission_attempts = 0
    return {
        "broker_outcome": str(payload.get("broker_outcome") or ""),
        "submission_attempts": submission_attempts,
    }
