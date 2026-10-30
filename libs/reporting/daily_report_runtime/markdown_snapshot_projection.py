"""Daily report markdown operator summary snapshot section (moved verbatim from daily_report_runtime.markdown).

Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_operator_summary_snapshot(
    operator_summary_snapshot: Dict[str, Any],
    *,
    include_system_status: bool,
) -> List[str]:
    executive = (
        operator_summary_snapshot.get("executive_summary")
        if isinstance(operator_summary_snapshot.get("executive_summary"), dict)
        else {}
    )
    if not executive.get("summary_lines"):
        return []

    lines = ["", "## Operator Summary Snapshot", ""]
    if include_system_status and executive.get("system_status"):
        lines.append(f"- system_status: **{executive['system_status']}**")
    for line in executive.get("summary_lines") or []:
        lines.append(f"- {line}")
    return lines
