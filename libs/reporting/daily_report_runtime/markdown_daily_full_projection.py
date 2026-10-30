"""Daily report markdown full daily report (moved verbatim from daily_report_runtime.markdown).

Section renderers are resolved on ``facade`` (the markdown module) at call time; this module never imports it.
Pure formatting; no IO.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Dict, List


ResidualRenderer = Callable[[Dict[str, Any]], List[str]]


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
    facade: Any,
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
        *facade.render_data_freshness_markdown(summary["data_freshness"]),
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

    lines += facade.render_operator_summary_snapshot(operator_summary_snapshot, include_system_status=True)
    lines += render_residual_positions(residual_positions)
    lines += facade.render_trade_report_integrity(summary)
    lines += facade.render_broker_alignment(summary)
    lines += facade.render_route_and_narrative_sections(summary)
    lines += facade.render_policy_surface_sections(summary)
    lines += facade.render_top_issues(operator_summary_snapshot)
    lines += facade.render_recommended_operator_actions(operator_summary_snapshot)
    return "\n".join(lines) + "\n"
