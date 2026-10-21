"""Deterministic Markdown renderers for the FAST07 evaluation reports.

Byte-for-byte moves of the Q9/Q13/loss/no-trade/lens/full-chain/mining
renderers out of the ``libs.reporting.evaluation`` facades. Pure string
assembly over already-built payloads; no I/O and no evaluation decisions.
"""

from __future__ import annotations

from typing import Any, Mapping


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


# --- A7.1: Q13 entry timing ---------------------------------------------------


def timing_fmt(value: Any, suffix: str = "") -> str:
    if value in (None, ""):
        return "-"
    try:
        return f"{float(value):.4f}{suffix}"
    except (TypeError, ValueError):
        return str(value)


def render_entry_timing_attribution_report(payload: Mapping[str, Any]) -> str:
    lines = [
        f"# Q13 Entry Timing Attribution - {payload.get('day', '')}",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Trades: {payload.get('trade_count', 0)}",
        "",
        "## Label Summary",
        "",
        "| Label | Trades | Win Rate | Avg Return | Avg Delay Sec | Avg 5m MFE | Avg 5m MAE |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload.get("label_summary") or []:
        if not isinstance(row, Mapping):
            continue
        perf = mapping(row.get("performance"))
        lines.append(
            f"| {row.get('label')} | {row.get('trade_count')} | "
            f"{timing_fmt(float(perf.get('win_rate') or 0.0) * 100.0, '%')} | "
            f"{timing_fmt(perf.get('average_return_pct'), '%')} | "
            f"{timing_fmt(row.get('avg_scanner_to_entry_delay_sec'))} | "
            f"{timing_fmt(row.get('avg_5m_mfe_pct'), '%')} | "
            f"{timing_fmt(row.get('avg_5m_mae_pct'), '%')} |"
        )
    lines.extend([
        "",
        "## Trade Rows",
        "",
        "| Trade | Symbol | Label | Delay Sec | Pre-entry Move | +5m Return | +5m MFE | +5m MAE | Realized | Reasons |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for row in payload.get("rows") or []:
        if not isinstance(row, Mapping):
            continue
        quality = mapping(row.get("entry_forward_quality"))
        lines.append(
            f"| {row.get('trade_id')} | {row.get('symbol')} | {row.get('label')} | "
            f"{timing_fmt(row.get('scanner_to_entry_delay_sec'))} | "
            f"{timing_fmt(row.get('pre_entry_move_pct'), '%')} | "
            f"{timing_fmt(quality.get('+5m_return_pct'), '%')} | "
            f"{timing_fmt(quality.get('+5m_mfe_pct'), '%')} | "
            f"{timing_fmt(quality.get('+5m_mae_pct'), '%')} | "
            f"{timing_fmt(row.get('entry_return_pct'), '%')} | "
            f"{', '.join(row.get('label_reasons') or []) or '-'} |"
        )
    lines.extend([
        "",
        "## Limitations",
        "",
    ])
    for item in payload.get("limitations") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


# --- A7.1: horizon alignment -----------------------------------------------


def render_horizon_alignment_review(payload: Mapping[str, Any]) -> str:
    date_range = payload.get("range") or {}
    cost = payload.get("cost_model") or {}
    lines = [
        f"# Horizon Alignment Review ({date_range.get('start')} ~ {date_range.get('end')})",
        "",
        "This report is evaluation-only. It does not change runtime behavior.",
        "",
        "## Cost Basis",
        "",
        f"- source: `{cost.get('source')}`",
        f"- samples: {cost.get('sample_count')}",
        f"- EMA round-trip cost: {float(cost.get('ema_round_trip_cost_pct') or 0):.4f}%",
        f"- conservative round-trip cost: {float(cost.get('conservative_round_trip_cost_pct') or 0):.4f}%",
        "",
        f"## Decision: **{payload.get('decision')}**",
        "",
        "## Time x Tactic x Horizon",
        "",
        "| Time | Tactic | Horizon | Obs/Days | Gross | Net | Net Win | PF | Day Max | Symbol Max | Decision |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload.get("time_tactic") or []:
        dimensions = row.get("dimensions") or {}
        lines.append(
            f"| {dimensions.get('time_bucket')} | {dimensions.get('tactic')} | {row.get('horizon')} | "
            f"{row.get('observed_count')}/{row.get('observed_day_count')} | "
            f"{row.get('average_gross_return_pct')}% | {row.get('average_net_return_pct')}% | "
            f"{float(row.get('net_win_rate') or 0):.1%} | {row.get('net_profit_factor')} | "
            f"{float(row.get('maximum_day_share') or 0):.1%} | "
            f"{float(row.get('maximum_symbol_share') or 0):.1%} | `{row.get('decision')}` |"
        )
    lines += [
        "",
        "## Controlled-Adoption Candidates",
        "",
    ]
    adoption = payload.get("controlled_adoption_candidates") or []
    if not adoption:
        lines.append("- None")
    else:
        for row in adoption:
            dimensions = row.get("dimensions") or {}
            lines.append(
                f"- `{dimensions.get('time_bucket')} | {dimensions.get('tactic')} | {row.get('horizon')}`: "
                f"net {row.get('average_net_return_pct')}%, PF {row.get('net_profit_factor')}, "
                f"{row.get('observed_count')} observations across {row.get('observed_day_count')} days"
            )
    lines += [
        "",
        "## Observation Candidates",
        "",
    ]
    observation = payload.get("observation_candidates") or []
    if not observation:
        lines.append("- None")
    else:
        for row in observation:
            dimensions = row.get("dimensions") or {}
            lines.append(
                f"- `{dimensions.get('time_bucket')} | {dimensions.get('tactic')} | {row.get('horizon')}`: "
                f"net {row.get('average_net_return_pct')}%, PF {row.get('net_profit_factor')}, "
                f"worst leave-one-day-out {row.get('worst_leave_one_day_out_net_return_pct')}%, "
                f"robust={row.get('robust_across_days')}"
            )
    lines += [
        "",
        "## Next Action",
        "",
        f"- decision: **{(payload.get('next_action') or {}).get('decision')}**",
        f"- reason: {(payload.get('next_action') or {}).get('reason')}",
        "- behavior change authorized: **False**",
    ]
    return "\n".join(lines) + "\n"
