"""Daily report markdown top issues and recommended operator actions (moved verbatim from daily_report_runtime.markdown).

Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_top_issues(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    top_issues = (
        operator_summary_snapshot.get("top_issues")
        if isinstance(operator_summary_snapshot.get("top_issues"), list)
        else []
    )
    if not top_issues:
        return []
    lines = ["", "## Top Issues", ""]
    for issue in top_issues:
        if not isinstance(issue, dict):
            continue
        lines.append(f"- [{issue.get('severity') or '-'}] {issue.get('code') or '-'}: {issue.get('detail') or '-'}")
    return lines


def render_recommended_operator_actions(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    recommended_actions = (
        operator_summary_snapshot.get("recommended_operator_actions")
        if isinstance(operator_summary_snapshot.get("recommended_operator_actions"), list)
        else []
    )
    if not recommended_actions:
        return []
    lines = ["", "## Recommended Operator Actions", ""]
    for action in recommended_actions:
        lines.append(f"- {action}")
    return lines
