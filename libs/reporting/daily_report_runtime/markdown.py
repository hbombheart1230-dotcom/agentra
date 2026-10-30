from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any, Callable, Dict, List

from libs.reporting.narrative_axes import narrative_axis_policy
from libs.reporting.report_metadata import render_data_freshness_markdown
from libs.reporting.daily_report_runtime import markdown_snapshot_projection as _snapshot_owner
from libs.reporting.daily_report_runtime import markdown_route_projection as _route_owner
from libs.reporting.daily_report_runtime import markdown_integrity_projection as _integrity_owner
from libs.reporting.daily_report_runtime import markdown_policy_projection as _policy_owner
from libs.reporting.daily_report_runtime import markdown_operator_projection as _operator_owner
from libs.reporting.daily_report_runtime import markdown_alignment_projection as _alignment_owner
from libs.reporting.daily_report_runtime import markdown_daily_projection as _daily_owner


ResidualRenderer = Callable[[Dict[str, Any]], List[str]]


def render_operator_summary_snapshot(
    operator_summary_snapshot: Dict[str, Any],
    *,
    include_system_status: bool,
) -> List[str]:
    return _snapshot_owner.render_operator_summary_snapshot(operator_summary_snapshot, include_system_status=include_system_status)


def render_route_and_narrative_sections(payload: Dict[str, Any]) -> List[str]:
    return _route_owner.render_route_and_narrative_sections(payload, facade=sys.modules[__name__])


def render_trade_report_integrity(payload: Dict[str, Any]) -> List[str]:
    return _integrity_owner.render_trade_report_integrity(payload, facade=sys.modules[__name__])


def render_broker_alignment(payload: Dict[str, Any]) -> List[str]:
    return _alignment_owner.render_broker_alignment(payload)


def render_policy_surface_sections(payload: Dict[str, Any]) -> List[str]:
    return _policy_owner.render_policy_surface_sections(payload, facade=sys.modules[__name__])


def render_top_issues(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    return _operator_owner.render_top_issues(operator_summary_snapshot)


def render_recommended_operator_actions(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    return _operator_owner.render_recommended_operator_actions(operator_summary_snapshot)


def render_no_event_daily_markdown(
    *,
    day: str,
    payload: Dict[str, Any],
    operator_snapshot_freshness: Dict[str, Any],
    render_residual_positions: ResidualRenderer,
) -> str:
    return _daily_owner.render_no_event_daily_markdown(day=day, payload=payload, operator_snapshot_freshness=operator_snapshot_freshness, render_residual_positions=render_residual_positions, facade=sys.modules[__name__])


def render_daily_markdown(
    *,
    day: str,
    summary: Dict[str, Any],
    operator_summary_snapshot_freshness: Dict[str, Any],
    approvals: int,
    blocks: int,
    symbols_for_day: List[str],
    actions: Counter,
    stage_counter: Counter,
    render_residual_positions: ResidualRenderer,
) -> str:
    operator_summary_snapshot = (
        summary.get("operator_summary_snapshot")
        if isinstance(summary.get("operator_summary_snapshot"), dict)
        else {}
    )
    residual_positions = summary.get("residual_positions") if isinstance(summary.get("residual_positions"), dict) else {}
    lines = [
        f"# Daily Report ({day})",
        "",
        *render_data_freshness_markdown(summary["data_freshness"]),
        f"- operator_summary_snapshot_stale: **{operator_summary_snapshot_freshness['stale']}**",
        "",
        f"- events: **{summary['events']}**",
        f"- approvals: **{approvals}** / blocks: **{blocks}**",
        f"- symbols observed: **{len(symbols_for_day)}**",
        "",
        "## Decision actions",
        "",
    ]
    if actions:
        for key, value in actions.most_common():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- (none)")

    lines += ["", "## Stage counts", ""]
    for key, value in stage_counter.most_common():
        lines.append(f"- {key}: {value}")

    lines += render_operator_summary_snapshot(operator_summary_snapshot, include_system_status=True)
    lines += render_residual_positions(residual_positions)
    lines += render_trade_report_integrity(summary)
    lines += render_broker_alignment(summary)
    lines += render_route_and_narrative_sections(summary)
    lines += render_policy_surface_sections(summary)
    lines += render_top_issues(operator_summary_snapshot)
    lines += render_recommended_operator_actions(operator_summary_snapshot)
    return "\n".join(lines) + "\n"
