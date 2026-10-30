"""Daily report markdown policy surface sections (moved verbatim from daily_report_runtime.markdown).

``json`` is resolved on ``facade`` (the markdown module) at call time; this module never imports it.
Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_policy_surface_sections(payload: Dict[str, Any], *, facade: Any) -> List[str]:
    policy_surface_summary = (
        payload.get("policy_surface_quality_summary")
        if isinstance(payload.get("policy_surface_quality_summary"), dict)
        else {}
    )
    policy_surface_exec = (
        payload.get("policy_surface_quality_executive_summary")
        if isinstance(payload.get("policy_surface_quality_executive_summary"), dict)
        else {}
    )
    chart_structure_summary = (
        payload.get("chart_structure_decision_hint_summary")
        if isinstance(payload.get("chart_structure_decision_hint_summary"), dict)
        else {}
    )
    chart_structure_exec = (
        payload.get("chart_structure_decision_hint_executive_summary")
        if isinstance(payload.get("chart_structure_decision_hint_executive_summary"), dict)
        else {}
    )
    policy_surface_source = (
        payload.get("policy_surface_quality_source")
        if isinstance(payload.get("policy_surface_quality_source"), dict)
        else {}
    )
    chart_structure_source = (
        payload.get("chart_structure_decision_hint_source")
        if isinstance(payload.get("chart_structure_decision_hint_source"), dict)
        else {}
    )
    chart_structure_examples = (
        chart_structure_summary.get("applied_examples")
        if isinstance(chart_structure_summary.get("applied_examples"), list)
        else []
    )

    lines = [
        "",
        "## Policy Surface Executive Summary",
        "",
        f"- status: **{str(policy_surface_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(policy_surface_exec.get('headline') or 'Policy surface unknown')}",
        "",
        "## Policy Surface Quality",
        "",
        f"- schema_available_rate: **{float(policy_surface_summary.get('schema_available_rate') or 0.0):.4f}**",
        f"- normalized_policy_rate: **{float(policy_surface_summary.get('normalized_policy_rate') or 0.0):.4f}**",
        f"- invalid_spec_rate: **{float(policy_surface_summary.get('invalid_spec_rate') or 0.0):.4f}**",
        f"- total_invalid_specs: **{int(policy_surface_summary.get('total_invalid_specs') or 0)}**",
        f"- run_count: **{int(policy_surface_source.get('run_count') or 0)}**",
        "",
        "## Chart Structure Decision Hint Executive Summary",
        "",
        f"- status: **{str(chart_structure_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(chart_structure_exec.get('headline') or 'Chart structure guard unknown')}",
        "",
        "## Chart Structure Decision Hint",
        "",
        f"- available_run_count: **{int(chart_structure_summary.get('available_run_count') or 0)}**",
        f"- applied_count: **{int(chart_structure_summary.get('applied_count') or 0)}**",
        f"- applied_rate: **{float(chart_structure_summary.get('applied_rate') or 0.0):.4f}**",
        f"- top_blocking_features: `{facade.json.dumps(chart_structure_summary.get('top_blocking_features') or [], ensure_ascii=False)}`",
        f"- run_count: **{int(chart_structure_source.get('run_count') or 0)}**",
    ]
    if chart_structure_examples:
        lines += ["", "## Chart Structure Decision Hint Applied Examples", ""]
        for example in chart_structure_examples[:3]:
            if not isinstance(example, dict):
                continue
            lines.append(
                f"- `{example.get('run_id') or '-'}` "
                f"[{str(example.get('entry_style') or '-').upper()}] "
                f"{example.get('reason_transition') or '-'} "
                f"blockers=`{facade.json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}`"
            )
    return lines
