"""Daily report markdown route provenance and narrative sections (moved verbatim from daily_report_runtime.markdown).

``json`` and ``narrative_axis_policy`` are resolved on ``facade`` (the markdown module) at call time; this module never imports it.
Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_route_and_narrative_sections(payload: Dict[str, Any], *, facade: Any) -> List[str]:
    route_summary = payload.get("route_summary") if isinstance(payload.get("route_summary"), dict) else {}
    narrative_policy = (
        payload.get("narrative_axis_policy")
        if isinstance(payload.get("narrative_axis_policy"), dict)
        else facade.narrative_axis_policy()
    )
    return [
        "",
        "## Route Provenance",
        "",
        f"- route_source: `{route_summary.get('route_source') or '-'}`",
        f"- route_source_run_count: **{int(route_summary.get('route_source_run_count') or 0)}**",
        f"- route_source_missing_count: **{int(route_summary.get('route_source_missing_count') or 0)}**",
        f"- route_source_breakdown: `{facade.json.dumps(route_summary.get('route_source_breakdown') or {}, ensure_ascii=False)}`",
        f"- route_selected_total: `{facade.json.dumps(route_summary.get('route_selected_total') or {}, ensure_ascii=False)}`",
        "",
        "## Narrative Axis Policy",
        "",
        f"- entry_primary_for: `{narrative_policy.get('entry_primary_for') or []}`",
        f"- exit_primary_for: `{narrative_policy.get('exit_primary_for') or []}`",
        f"- mixed_only_for_ambiguous_cases: **{bool(narrative_policy.get('mixed_only_for_ambiguous_cases'))}**",
        f"- runtime_semantics_unchanged: **{bool(narrative_policy.get('runtime_semantics_unchanged'))}**",
    ]
