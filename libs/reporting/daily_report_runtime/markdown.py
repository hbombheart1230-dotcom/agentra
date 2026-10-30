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
from libs.reporting.daily_report_runtime import markdown_daily_full_projection as _daily_full_owner


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
    return _daily_full_owner.render_daily_markdown(day=day, summary=summary, operator_summary_snapshot_freshness=operator_summary_snapshot_freshness, approvals=approvals, blocks=blocks, symbols_for_day=symbols_for_day, actions=actions, stage_counter=stage_counter, render_residual_positions=render_residual_positions, facade=sys.modules[__name__])
