from pathlib import Path
from typing import Any, Dict, List

def _render_bundle_markdown(payload: Dict[str, Any], *, repo_root: Path, facade) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    trade_health = artifacts.get("trade_health") if isinstance(artifacts.get("trade_health"), dict) else {}
    symbol_reports = artifacts.get("symbol_reports") if isinstance(artifacts.get("symbol_reports"), list) else []
    latest_runs = artifacts.get("latest_canonical_runs") if isinstance(artifacts.get("latest_canonical_runs"), list) else []
    policy_surface = (
        artifacts.get("policy_surface_quality")
        if isinstance(artifacts.get("policy_surface_quality"), dict)
        else {}
    )
    policy_surface_summary = (
        policy_surface.get("summary")
        if isinstance(policy_surface.get("summary"), dict)
        else {}
    )
    policy_surface_exec = (
        policy_surface.get("executive_summary")
        if isinstance(policy_surface.get("executive_summary"), dict)
        else {}
    )
    policy_surface_source = (
        policy_surface.get("source")
        if isinstance(policy_surface.get("source"), dict)
        else {}
    )
    chart_structure_guard = (
        artifacts.get("chart_structure_decision_hint")
        if isinstance(artifacts.get("chart_structure_decision_hint"), dict)
        else {}
    )
    chart_structure_guard_summary = (
        chart_structure_guard.get("summary")
        if isinstance(chart_structure_guard.get("summary"), dict)
        else {}
    )
    chart_structure_guard_exec = (
        chart_structure_guard.get("executive_summary")
        if isinstance(chart_structure_guard.get("executive_summary"), dict)
        else {}
    )
    chart_structure_guard_source = (
        chart_structure_guard.get("source")
        if isinstance(chart_structure_guard.get("source"), dict)
        else {}
    )
    chart_structure_guard_examples = (
        chart_structure_guard_summary.get("applied_examples")
        if isinstance(chart_structure_guard_summary.get("applied_examples"), list)
        else []
    )

    lines: List[str] = [
        f"# Phase 5 Validation Bundle ({payload.get('day')})",
        "",
        "## Summary",
        "",
        f"- daily_report_generated: **{bool(summary.get('daily_report_generated'))}**",
        f"- operator_daily_summary_generated: **{bool(summary.get('operator_daily_summary_generated'))}**",
        f"- trade_health_ok: **{bool(summary.get('trade_health_ok'))}**",
        f"- symbol_report_count: **{int(summary.get('symbol_report_count') or 0)}**",
        f"- latest_canonical_run_id: `{summary.get('latest_canonical_run_id') or ''}`",
        "",
        "## Daily Surfaces",
        "",
    ]

    daily = artifacts.get("daily_report") if isinstance(artifacts.get("daily_report"), dict) else {}
    operator = artifacts.get("operator_daily_summary") if isinstance(artifacts.get("operator_daily_summary"), dict) else {}
    lines += [
        f"- daily_report_json: `{daily.get('json_path') or ''}`",
        f"- daily_report_md: `{daily.get('md_path') or ''}`",
        f"- operator_daily_summary_json: `{operator.get('json_path') or ''}`",
        f"- operator_daily_summary_md: `{operator.get('md_path') or ''}`",
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
        f"- source: `{policy_surface_source.get('source') or ''}`",
        "",
        "## Chart Structure Decision Hint Executive Summary",
        "",
        f"- status: **{str(chart_structure_guard_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(chart_structure_guard_exec.get('headline') or 'Chart structure guard unknown')}",
        "",
        "## Chart Structure Decision Hint",
        "",
        f"- available_run_count: **{int(chart_structure_guard_summary.get('available_run_count') or 0)}**",
        f"- applied_count: **{int(chart_structure_guard_summary.get('applied_count') or 0)}**",
        f"- applied_rate: **{float(chart_structure_guard_summary.get('applied_rate') or 0.0):.4f}**",
        f"- top_blocking_features: `{facade.json.dumps(chart_structure_guard_summary.get('top_blocking_features') or [], ensure_ascii=False)}`",
        f"- source: `{chart_structure_guard_source.get('source') or ''}`",
        "",
        "## Trade / Report Health",
        "",
        f"- trade_dir_count: **{int(trade_health.get('trade_dir_count') or 0)}**",
        f"- severity_counts: `{facade.json.dumps(trade_health.get('severity_counts') or {}, ensure_ascii=False)}`",
        f"- issue_counts: `{facade.json.dumps(trade_health.get('issue_counts') or {}, ensure_ascii=False)}`",
        "",
        "## Symbol Reports",
        "",
    ]
    if chart_structure_guard_examples:
        lines += ["## Chart Structure Decision Hint Applied Examples", ""]
        for example in chart_structure_guard_examples[:3]:
            if not isinstance(example, dict):
                continue
            lines.append(
                f"- `{example.get('run_id') or '-'}` "
                f"[{str(example.get('entry_style') or '-').upper()}] "
                f"{example.get('reason_transition') or '-'} "
                f"blockers=`{facade.json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}`"
            )
        lines.append("")
    if symbol_reports:
        for row in symbol_reports:
            lines.append(
                f"- `{row.get('symbol')}`: json=`{row.get('json_path')}` md=`{row.get('md_path')}`"
            )
    else:
        lines.append("- (none)")

    decision_story = artifacts.get("decision_story") if isinstance(artifacts.get("decision_story"), dict) else {}
    run_cards = artifacts.get("run_cards") if isinstance(artifacts.get("run_cards"), dict) else {}
    trade_explain = artifacts.get("trade_explain") if isinstance(artifacts.get("trade_explain"), dict) else {}
    pipeline_trace = artifacts.get("pipeline_trace") if isinstance(artifacts.get("pipeline_trace"), dict) else {}
    lines += [
        "",
        "## Inspection Reports",
        "",
        f"- decision_story_md: `{decision_story.get('md_path') or ''}`",
        f"- run_cards_md: `{run_cards.get('md_path') or ''}`",
        f"- trade_explain_json: `{trade_explain.get('json_path') or ''}`",
        f"- trade_explain_md: `{trade_explain.get('md_path') or ''}`",
        f"- pipeline_trace_json: `{pipeline_trace.get('json_path') or ''}`",
        f"- pipeline_trace_md: `{pipeline_trace.get('md_path') or ''}`",
        "",
        "## Latest Canonical Runs",
        "",
    ]
    if latest_runs:
        for row in latest_runs:
            lines.append(
                f"- `{row.get('run_id')}`: commander=`{row.get('commander_json_path')}` monitor=`{row.get('monitor_json_path')}`"
            )
    else:
        lines.append("- (none)")

    issues = trade_health.get("issues") if isinstance(trade_health.get("issues"), list) else []
    lines += ["", "## Top Issues", ""]
    if issues:
        for issue in issues[:10]:
            lines.append(
                f"- [{issue.get('severity')}] `{issue.get('trade_id')}` `{issue.get('component')}` `{issue.get('code')}` - {issue.get('message')}"
            )
            lines.append(f"  path: `{issue.get('path')}`")
    else:
        lines.append("- (none)")

    lines += [
        "",
        "## Notes",
        "",
        "- This bundle is deterministic/read-only. It does not change runtime behavior.",
        "- It is intended to make report quality, schema linkage, and artifact paths easy to inspect by eye.",
        f"- repo_root: `{facade._safe_rel(repo_root, repo_root) or '.'}`",
        "",
    ]
    return "\n".join(lines)
