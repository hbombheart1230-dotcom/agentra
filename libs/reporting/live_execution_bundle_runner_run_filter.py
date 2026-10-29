"""``_filter_rows_by_run_ids`` moved verbatim from live_execution_bundle_runner.py as ``filter_rows_by_run_ids``.

Pure function; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List


def filter_rows_by_run_ids(
    rows: List[Dict[str, Any]] | None,
    run_ids: Iterable[str] | None,
) -> List[Dict[str, Any]]:
    source_rows = list(rows or [])
    allowed = {str(run_id or "").strip() for run_id in list(run_ids or []) if str(run_id or "").strip()}
    if not allowed:
        return source_rows
    return [
        row
        for row in source_rows
        if str((row or {}).get("run_id") or "").strip() in allowed
    ]
