"""Pure Markdown rendering for the Q9 full-chain component review (P1.5 DEV-A).

Turns the review payload into report text; writing the files stays in
``libs.reporting.evaluation.full_chain_component_review.write_full_chain_component_review``.
"""
from __future__ import annotations

import json
from typing import Any, Mapping


def render_full_chain_component_review_impl(payload: Mapping[str, Any], *, facade: Any) -> str:
    date_range = payload.get("range") or {}
    components = payload.get("component_decisions") or {}
    lines = [
        f"# Q9 Full-Chain Component Review ({date_range.get('start')} ~ {date_range.get('end')})",
        "",
        "Evaluation-only. No runtime or trading policy change is authorized.",
        "",
        "## Final Component Decisions",
        "",
        "| Component | Decision | Finding / Missing Comparison |",
        "|---|---|---|",
    ]
    for key in ("scanner", "strategist", "commander", "monitor_entry", "monitor_exit", "full_system"):
        row = components.get(key) or {}
        detail = row.get("missing_comparison") or row.get("finding") or ""
        lines.append(f"| {key} | `{row.get('decision')}` | {detail} |")
    scanner = components.get("scanner") or {}
    lines += [
        "",
        "## Scanner: Cost-Adjusted Role Metrics",
        "",
        "| Role | Horizon | Count/Days | Expectancy | Win Rate | PF |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in scanner.get("role_cost_adjusted_metrics") or []:
        lines.append(
            f"| {row.get('role')} | {row.get('horizon')} | "
            f"{row.get('observed_count')}/{row.get('observed_day_count')} | "
            f"{row.get('expectancy_pct')}% | {float(row.get('win_rate') or 0):.1%} | "
            f"{row.get('profit_factor')} |"
        )
    lines += [
        "",
        "## Scanner: Paired Ranking Effect",
        "",
        "| Horizon | Paired Windows/Days | Top-pick Minus Runner-up | Positive Rate |",
        "|---|---:|---:|---:|",
    ]
    for row in scanner.get("paired_role_comparisons") or []:
        lines.append(
            f"| {row.get('horizon')} | {row.get('paired_window_count')}/{row.get('observed_day_count')} | "
            f"{row.get('average_delta_pct')}% | {float(row.get('positive_delta_rate') or 0):.1%} |"
        )
    scanner_quality = ((payload.get("evidence") or {}).get("scanner_quality") or {})
    lines += [
        "",
        "## Scanner: Same-Universe Intrinsic Top-K Forward Performance",
        "",
        "| Top-K | Horizon | Windows/Days | Gross Expectancy | Net Expectancy |",
        "|---:|---|---:|---:|---:|",
    ]
    for row in (scanner_quality.get("topk_forward_performance") or {}).get("rows") or []:
        lines.append(
            f"| {row.get('top_k')} | {row.get('horizon')} | "
            f"{row.get('window_count')}/{row.get('observed_day_count')} | "
            f"{(row.get('gross') or {}).get('expectancy_pct')}% | "
            f"{(row.get('net') or {}).get('expectancy_pct')}% |"
        )
    lines += [
        "",
        "## Scanner: Candidate Source Performance",
        "",
        "| Source | Horizon | Count/Days | Net Expectancy | Win Rate |",
        "|---|---|---:|---:|---:|",
    ]
    for row in (scanner_quality.get("source_performance") or {}).get("rows") or []:
        lines.append(
            f"| {row.get('source')} | {row.get('horizon')} | "
            f"{row.get('count')}/{row.get('observed_day_count')} | "
            f"{row.get('expectancy_pct')}% | {float(row.get('win_rate') or 0):.1%} |"
        )
    problem = payload.get("problem_segment") or {}
    lines += [
        "",
        "## Problem Segment",
        "",
        f"- primary root cause: **{problem.get('primary_root_cause')}**",
        f"- statuses: `{json.dumps(problem.get('statuses') or {}, ensure_ascii=False, sort_keys=True)}`",
    ]
    entry = (components.get("monitor_entry") or {}).get("metrics") or {}
    exit_row = (components.get("monitor_exit") or {}).get("metrics") or {}
    realized = ((components.get("full_system") or {}).get("metrics") or {}).get("performance") or {}
    availability = (payload.get("evidence") or {}).get("selection_availability") or {}
    attribution = (payload.get("evidence") or {}).get("decision_window_attribution") or {}
    lines += [
        "",
        "## Attribution Availability",
        "",
        f"- trade models: {availability.get('trade_model_count')}",
        f"- same-universe intrinsic Scanner controls: {availability.get('raw_scanner_control_count')}",
        f"- Strategist snapshots: {availability.get('strategist_snapshot_count')}",
        f"- Commander snapshots: {availability.get('commander_snapshot_count')}",
        f"- intrinsic vs strategy-weighted comparable: {availability.get('scanner_vs_strategist_comparable_count')}",
        f"- Strategist vs Commander comparable: {availability.get('strategist_vs_commander_comparable_count')}",
        f"- Q9 decision windows with forward candidates: {attribution.get('decision_window_count')}",
        f"- Q9 A/B/C forward candidate rows: {attribution.get('candidate_row_count')}",
        "",
        "## Monitor Entry",
        "",
        f"- matched trades/days: {entry.get('matched_trade_count')} / {entry.get('matched_day_count')}",
        f"- average entry-price delta: {entry.get('average_entry_price_delta_pct')}%",
        f"- median entry-price delta: {entry.get('median_entry_price_delta_pct')}%",
        "",
        "## Monitor Exit",
        "",
        f"- observed exits/days: {exit_row.get('observed_trade_count')} / {exit_row.get('observed_day_count')}",
        f"- +5m average improvement: {next((row.get('average_improvement_pct') for row in exit_row.get('by_hold_offset') or [] if row.get('offset') == '+5m'), None)}%",
        "",
        "## Realized Full System",
        "",
        f"- trades: {realized.get('count')}",
        f"- win rate: {float(realized.get('win_rate') or 0):.1%}",
        f"- expectancy: {realized.get('expectancy_pct')}%",
        f"- profit factor: {realized.get('profit_factor')}",
        f"- maximum drawdown: {realized.get('maximum_drawdown_pct')}%",
        "",
        "## Overall Decision",
        "",
        f"- decision: **{(payload.get('overall_decision') or {}).get('decision')}**",
        f"- first actionable component: `{(payload.get('overall_decision') or {}).get('first_actionable_component')}`",
        f"- reason: {(payload.get('overall_decision') or {}).get('reason')}",
        "- historical review complete: **True**",
        "- open-ended extension authorized: **False**",
        "- behavior change authorized: **False**",
    ]
    return "\n".join(lines) + "\n"
