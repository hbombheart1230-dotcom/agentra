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


# --- A7.2: loss decomposition, no-trade attribution, evaluation lens ------------


def no_trade_pct(value: Any) -> str:
    try:
        number = None if value in (None, "") else float(value)
    except (TypeError, ValueError):
        number = None
    if number is None:
        return "-"
    return f"{number:.4f}%"


def lens_as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def lens_metric_avg(metric: Mapping[str, Any]) -> str:
    data = dict(metric) if isinstance(metric, Mapping) else {}
    if int(data.get("count") or 0) <= 0:
        return "-"
    return str(data.get("average_return_pct"))


def render_loss_decomposition(payload: Mapping[str, Any]) -> str:
    date_range = payload.get("range") or {}
    evidence = payload.get("evidence") or {}
    realized = payload.get("realized_system") or {}
    performance = realized.get("performance") or {}
    lines = [
        f"# Full-Chain Loss Decomposition ({date_range.get('start')} ~ {date_range.get('end')})",
        "",
        "This report is evaluation-only and does not change trading behavior.",
        "",
        "## Evidence",
        "",
        f"- shadow payloads: {evidence.get('shadow_payload_count')}",
        f"- raw/deduped candidates: {evidence.get('raw_shadow_candidate_count')} / {evidence.get('deduped_shadow_candidate_count')}",
        f"- trusted forward: {evidence.get('trusted_forward_count')} ({float(evidence.get('trusted_forward_coverage') or 0):.1%})",
        f"- trusted forward observed days: {', '.join(evidence.get('trusted_forward_observed_days') or []) or '-'}",
        f"- trade models: {evidence.get('trade_model_count')}",
        "",
        "## Stage Diagnosis",
        "",
        "| Stage | Status | Finding |",
        "|---|---|---|",
    ]
    for row in payload.get("diagnosis") or []:
        lines.append(f"| {row.get('stage')} | `{row.get('status')}` | {row.get('finding')} |")
    lines += [
        "",
        "## Candidate Edge By Time Bucket",
        "",
        "| Bucket | Observed | +5m | +15m | +30m | +60m |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in (payload.get("raw_candidate_edge") or {}).get("by_time_bucket") or []:
        lines.append(
            f"| {row.get('name')} | {row.get('observed_count')} | "
            f"{row.get('avg_return_5m_pct')} | {row.get('avg_return_15m_pct')} | "
            f"{row.get('avg_return_30m_pct')} | {row.get('avg_return_60m_pct')} |"
        )
    lines += [
        "",
        "## Shadow Rank Buckets",
        "",
        "| Rank | Observed | +5m | +15m | +30m | +60m |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in (payload.get("scanner_ranking") or {}).get("by_rank_bucket") or []:
        lines.append(
            f"| {row.get('name')} | {row.get('observed_count')} | "
            f"{row.get('avg_return_5m_pct')} | {row.get('avg_return_15m_pct')} | "
            f"{row.get('avg_return_30m_pct')} | {row.get('avg_return_60m_pct')} |"
        )
    lines += [
        "",
        "## Realized System",
        "",
        f"- count: {performance.get('count')}",
        f"- win rate: {performance.get('win_rate')}",
        f"- average return: {performance.get('average_return_pct')}%",
        f"- expectancy: {performance.get('expectancy_pct')}%",
        f"- profit factor: {performance.get('profit_factor')}",
        f"- maximum drawdown: {performance.get('maximum_drawdown_pct')}%",
        "",
        "## Monitor Entry",
        "",
        f"- matched trades: {(payload.get('monitor_entry') or {}).get('matched_trade_count')}",
        f"- average entry price delta: {(payload.get('monitor_entry') or {}).get('average_entry_price_delta_pct')}%",
        f"- late entries over +0.3%: {(payload.get('monitor_entry') or {}).get('late_entry_count')}",
        "",
        "## Monitor Exit Hold Alternatives",
        "",
        "| Offset | Count | Average improvement | Improved | Worsened |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in (payload.get("monitor_exit") or {}).get("by_hold_offset") or []:
        lines.append(
            f"| {row.get('offset')} | {row.get('count')} | "
            f"{row.get('average_improvement_pct')}% | {row.get('improved_count')} | "
            f"{row.get('worsened_count')} |"
        )
    lines += [
        "",
        "## Fixed Interpretation",
        "",
        "- Do not patch every component at once.",
        "- Fix the first stage with a demonstrated loss of edge.",
        "- Strategist and Commander remain unjudged until trusted controls exist.",
        "- Reconstructed evidence is diagnostic and cannot promote behavior.",
        "",
        "## Next Action",
        "",
        f"- component: `{(payload.get('next_action') or {}).get('component')}`",
        f"- decision: **{(payload.get('next_action') or {}).get('decision')}**",
        f"- reason: {(payload.get('next_action') or {}).get('reason')}",
        "- behavior change authorized: **False**",
    ]
    return "\n".join(lines) + "\n"


def render_no_trade_attribution_report(payload: Mapping[str, Any]) -> str:
    lines = [
        "# No-Trade Attribution Report",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Day: `{payload.get('day', '')}`",
        f"- Trades: {payload.get('trade_count', 0)}",
        f"- Q9 windows: {payload.get('q9_window_count', 0)}",
        f"- No-trade class: `{payload.get('no_trade_class', '')}`",
        f"- Primary issue: `{payload.get('primary_issue', '')}`",
        f"- Commander approve + Monitor NOOP: {payload.get('commander_approve_monitor_noop_count', 0)}",
        "",
        "## Q9 Decision Surface",
        "",
    ]
    for title, key in (
        ("Commander Decisions", "commander_decisions"),
        ("Commander Reasons", "commander_reasons"),
        ("Commander Details", "commander_details"),
        ("Monitor Intents", "monitor_intents"),
        ("Monitor NOOP Reasons", "monitor_noop_reasons"),
        ("Scanner Top1", "scanner_top1"),
        ("Strategist Selected", "strategist_selected"),
    ):
        lines.extend([f"### {title}", ""])
        rows = payload.get(key) if isinstance(payload.get(key), list) else []
        if not rows:
            lines.append("- None")
        else:
            for row in rows:
                if isinstance(row, Mapping):
                    lines.append(f"- `{row.get('name', '')}`: {row.get('count', 0)}")
        lines.append("")

    q11 = mapping(payload.get("q11_opening_opportunity"))
    lines.extend([
        "## Shadow Opportunity",
        "",
        f"- Status: `{payload.get('shadow_opportunity_status', '')}`",
        f"- Q11 available: {bool(q11.get('available'))}",
        f"- Q11 signal rows: {q11.get('signal_rows', 0)}",
        f"- Q11 probe candidates: {q11.get('probe_candidates', 0)}",
        f"- Q11 probe near-misses: {q11.get('probe_near_misses', 0)}",
        f"- Q11 virtual trades: {q11.get('virtual_trades', 0)}",
        f"- Q11 win rate: {q11.get('win_rate') if q11.get('win_rate') is not None else '-'}",
        f"- Q11 avg net: {no_trade_pct(q11.get('avg_net_return_pct'))}",
        f"- Q11 avg MFE: {no_trade_pct(q11.get('avg_mfe_pct'))}",
        f"- Q11 avg MAE: {no_trade_pct(q11.get('avg_mae_pct'))}",
        "",
        "## Baseline Summary",
        "",
        "| Baseline | Horizon | Trades | Win Rate | Avg Net | PF |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for baseline_key, label in (
        ("q10_samsung_hynix", "Q10 Samsung/Hynix"),
        ("q12_btc_woori", "Q12 BTC/Woori"),
    ):
        baseline = mapping(payload.get(baseline_key))
        rows = baseline.get("horizons") if isinstance(baseline.get("horizons"), list) else []
        if not rows:
            lines.append(f"| {label} | - | 0 | - | - | - |")
            continue
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            lines.append(
                "| "
                + " | ".join(
                    [
                        label,
                        str(row.get("horizon") or "-"),
                        str(row.get("trade_count") or 0),
                        str(row.get("win_rate") if row.get("win_rate") is not None else "-"),
                        no_trade_pct(row.get("avg_net_return_pct")),
                        str(row.get("profit_factor") if row.get("profit_factor") is not None else "-"),
                    ]
                )
                + " |"
            )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- This report does not change trading behavior.",
        "- If trades are zero, Q13/Q14 trade attribution is insufficient; this report decides whether the absence itself is an over-filtering signal.",
    ])
    return "\n".join(lines) + "\n"


def render_evaluation_lens_report(payload: Mapping[str, Any]) -> str:
    rng = lens_as_dict(payload.get("range"))
    evidence = lens_as_dict(payload.get("evidence"))
    lines = [
        f"# Evaluation Lens Report ({rng.get('start')} ~ {rng.get('end')})",
        "",
        "Behavior effect: evaluation_only. This report does not change trading behavior or reset the freeze window.",
        "",
        "## Evidence",
        f"- shadow payloads: {evidence.get('shadow_payload_count')}",
        f"- shadow candidates: {evidence.get('candidate_count')}",
        f"- Q9 candidates: {evidence.get('q9_candidate_count')}",
        f"- trade models: {evidence.get('trade_model_count')}",
        "",
        "## Blocker Forward Review",
        "| Blocker | Candidates | +5m avg | +15m avg | +30m avg | +30m MFE | +30m cost reachable |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    blocker = lens_as_dict(payload.get("blocker_forward_review"))
    for row in blocker.get("by_blocker") or []:
        h5 = lens_as_dict(row.get("+5m"))
        h15 = lens_as_dict(row.get("+15m"))
        h30 = lens_as_dict(row.get("+30m"))
        lines.append(
            f"| {row.get('name')} | {row.get('candidate_count')} | "
            f"{lens_metric_avg(lens_as_dict(h5.get('return')))} | "
            f"{lens_metric_avg(lens_as_dict(h15.get('return')))} | "
            f"{lens_metric_avg(lens_as_dict(h30.get('return')))} | "
            f"{h30.get('avg_mfe_pct')} | {h30.get('cost_floor_reachable_rate')} |"
        )
    lines += [
        "",
        "## Strategist Delta",
        "| Horizon | Best role | Strategist delta avg | Commander delta avg |",
        "|---|---|---:|---:|",
    ]
    strat = lens_as_dict(payload.get("strategist_delta_review"))
    best_by = {row.get("horizon"): row.get("best_role") for row in strat.get("best_role_by_horizon") or []}
    for row in strat.get("deltas_by_horizon") or []:
        horizon = row.get("horizon")
        sd = lens_as_dict(row.get("strategist_minus_scanner_control"))
        cd = lens_as_dict(row.get("commander_minus_strategist"))
        lines.append(
            f"| {horizon} | {best_by.get(horizon) or ''} | "
            f"{lens_metric_avg(sd)} | {lens_metric_avg(cd)} |"
        )
    lines += [
        "",
        "## Exit Hold Counterfactual",
        "| Exit reason | Trades | +5m improvement | +15m improvement | +30m improvement | EOD improvement |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    exit_review = lens_as_dict(payload.get("exit_hold_counterfactual_review"))
    for row in exit_review.get("by_exit_reason") or []:
        lines.append(
            f"| {row.get('exit_reason')} | {row.get('trade_count')} | "
            f"{lens_metric_avg(lens_as_dict(row.get('+5m')))} | "
            f"{lens_metric_avg(lens_as_dict(row.get('+15m')))} | "
            f"{lens_metric_avg(lens_as_dict(row.get('+30m')))} | "
            f"{lens_metric_avg(lens_as_dict(row.get('EOD')))} |"
        )
    lines += [
        "",
        "## Rules",
        "- This report can be regenerated for past days without resetting evaluation.",
        "- It adds observability only; entry, exit, scanner, strategist, commander, and monitor behavior are unchanged.",
        "- Promotion decisions still require the promotion framework and enough comparable days.",
    ]
    return "\n".join(lines) + "\n"
