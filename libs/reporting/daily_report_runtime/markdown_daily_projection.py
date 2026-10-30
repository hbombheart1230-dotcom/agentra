"""Daily report markdown no-event daily report (moved verbatim from daily_report_runtime.markdown).

Section renderers are resolved on ``facade`` (the markdown module) at call time; this module never imports it.
Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List


ResidualRenderer = Callable[[Dict[str, Any]], List[str]]


def render_no_event_daily_markdown(
    *,
    day: str,
    payload: Dict[str, Any],
    operator_snapshot_freshness: Dict[str, Any],
    render_residual_positions: ResidualRenderer,
    facade: Any,
) -> str:
    operator_summary_snapshot = (
        payload.get("operator_summary_snapshot")
        if isinstance(payload.get("operator_summary_snapshot"), dict)
        else {}
    )
    residual_positions = payload.get("residual_positions") if isinstance(payload.get("residual_positions"), dict) else {}
    lines = [
        f"# Daily Report ({day})",
        "",
        "No events found.",
    ]
    lines += [""] + facade.render_data_freshness_markdown(payload["data_freshness"])
    lines += [f"- operator_summary_snapshot_stale: **{operator_snapshot_freshness['stale']}**"]
    lines += facade.render_operator_summary_snapshot(operator_summary_snapshot, include_system_status=False)
    lines += render_residual_positions(residual_positions)
    lines += facade.render_trade_report_integrity(payload)
    lines += facade.render_broker_alignment(payload)
    lines += facade.render_route_and_narrative_sections(payload)
    lines += facade.render_policy_surface_sections(payload)
    return "\n".join(lines) + "\n"
