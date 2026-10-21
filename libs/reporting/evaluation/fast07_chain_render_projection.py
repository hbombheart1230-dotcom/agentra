"""Deterministic Markdown renderers for the FAST07 evaluation reports.

Byte-for-byte moves of the Q9/Q13/loss/no-trade/lens/full-chain/mining
renderers out of the ``libs.reporting.evaluation`` facades. Pure string
assembly over already-built payloads; no I/O and no evaluation decisions.
"""

from __future__ import annotations

import json
from typing import Any, Mapping, Sequence


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


def _has_evidence_basis(payload: Mapping[str, Any]) -> bool:
    return any(isinstance(row, Mapping) and isinstance(row.get("evidence_basis"), Mapping) for row in payload.get("rows") or [])


def _basis_cell(row: Mapping[str, Any]) -> str:
    basis = row.get("evidence_basis")
    if not isinstance(basis, Mapping):
        return "legacy (no evidence basis)"
    cell = (
        f"fill={basis.get('actual_entry', '?')} / path={basis.get('observed_forward_path', '?')} / "
        f"shadow-anchor={basis.get('shadow_anchor', '?')} / timing={basis.get('timing_integrity', '?')}"
    )
    return cell.replace("|", "/")


def _render_evidence_quality(quality: Mapping[str, Any]) -> list[str]:
    recon = mapping(quality.get("reconciliation"))
    lines = [
        "",
        "## Evidence Quality",
        "",
        "Actual results come from executed fills; the observed path is a price observation after the actual entry; "
        "the shadow anchor is decision-time data that was never executed. They are counted separately.",
        "",
        f"- Models offered: {recon.get('model_count', '-')} = analyzed {recon.get('analyzed_count', '-')} + excluded {recon.get('excluded_count', '-')} "
        f"(reconciled: **{'yes' if recon.get('reconciled') else 'NO'}**)",
        f"- Insufficient evidence rows: {quality.get('insufficient_evidence_count', 0)}",
        f"- Shadow-only rows (decision anchor but no actual fill): {quality.get('shadow_only_count', 0)}",
        f"- Actual fills with a realized return / without: {quality.get('actual_return_observed_count', 0)} / "
        f"{quality.get('actual_return_missing_on_fill_count', 0)}",
        "",
        "| Evidence class | Rows |",
        "| --- | ---: |",
    ]
    for name, count in mapping(quality.get("evidence_classes")).items():
        lines.append(f"| {name} | {count} |")
    for title, key in (("Actual entry", "actual_entry"), ("Observed forward path", "observed_forward_path"),
                       ("Shadow anchor", "shadow_anchor"), ("Timing integrity", "timing_integrity")):
        counts = mapping(quality.get(key))
        lines.append("")
        lines.append(f"- {title}: " + ", ".join(f"{name}={count}" for name, count in counts.items()))
    codes = mapping(quality.get("timing_anomaly_codes"))
    lines.append("")
    lines.append(f"- Timing mismatches ({quality.get('rows_with_timing_anomalies', 0)} rows): "
                 + (", ".join(f"{name}={count}" for name, count in codes.items()) or "none"))
    return lines


def render_entry_timing_attribution_report(payload: Mapping[str, Any]) -> str:
    separated = _has_evidence_basis(payload)
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
    if isinstance(payload.get("evidence_quality"), Mapping):
        lines.extend(_render_evidence_quality(payload["evidence_quality"]))
    lines.extend(["", "## Trade Rows", ""])
    if separated:
        lines.extend([
            "| Trade | Symbol | Label | Delay Sec | Pre-entry Move | +5m Return (observed path) | +5m MFE (observed path) | +5m MAE (observed path) | Realized (actual) | Reasons | Evidence |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ])
    else:
        lines.extend([
            "| Trade | Symbol | Label | Delay Sec | Pre-entry Move | +5m Return | +5m MFE | +5m MAE | Realized | Reasons |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ])
    for row in payload.get("rows") or []:
        if not isinstance(row, Mapping):
            continue
        quality = mapping(row.get("entry_forward_quality"))
        cells = (
            f"| {row.get('trade_id')} | {row.get('symbol')} | {row.get('label')} | "
            f"{timing_fmt(row.get('scanner_to_entry_delay_sec'))} | "
            f"{timing_fmt(row.get('pre_entry_move_pct'), '%')} | "
            f"{timing_fmt(quality.get('+5m_return_pct'), '%')} | "
            f"{timing_fmt(quality.get('+5m_mfe_pct'), '%')} | "
            f"{timing_fmt(quality.get('+5m_mae_pct'), '%')} | "
            f"{timing_fmt(row.get('entry_return_pct'), '%')} | "
            f"{', '.join(row.get('label_reasons') or []) or '-'} |"
        )
        lines.append(cells + (f" {_basis_cell(row)} |" if separated else ""))
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
        *(
            [f"- excluded trade models (split-sell child / confirmed runtime defect): {evidence.get('excluded_trade_model_count')} of {evidence.get('total_trade_model_count')}"]
            if evidence.get("excluded_trade_model_count")
            else []
        ),
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
    if (payload.get("monitor_exit") or {}).get("unrealized_exit_excluded_count"):
        lines.append("")
        lines.append(
            "- Post-exit price observations are virtual (not a realized result); trades without a realized exit are not counted: "
            f"{(payload.get('monitor_exit') or {}).get('unrealized_exit_excluded_count')}"
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


# --- A7.3: full-chain component review ------------------------------------------


def render_full_chain_component_review(payload: Mapping[str, Any]) -> str:
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


# --- A7.3: operator summary mining ----------------------------------------------


def mining_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def mining_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def mining_safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def mining_safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def mining_avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def mining_presence_report(days: Sequence[Any]) -> dict[str, Any]:
    fields = {
        "daily_summary": "daily_summary",
        "operator_summary": "operator_summary",
        "q8_shadow_blocker_review": "q8_review",
        "q9_decision_windows": "q9_windows",
        "closeout_maintenance": "closeout",
        "trade_index": "trade_index",
        "daily_report": "daily_report",
    }
    counts: dict[str, int] = {}
    for name, attr in fields.items():
        count = 0
        for row in days:
            value = getattr(row, attr)
            if isinstance(value, list):
                if value:
                    count += 1
            elif value:
                count += 1
        counts[name] = count
    total = len(days)
    return {
        "daily_count": total,
        "first_day": days[0].day if days else "",
        "last_day": days[-1].day if days else "",
        "presence_counts": counts,
        "presence_ratio": {
            name: round(value / total, 4) if total else 0.0
            for name, value in counts.items()
        },
        "json_error_count": sum(len(row.errors) for row in days),
        "json_errors": [
            {"day": row.day, "error": error}
            for row in days
            for error in row.errors
        ][:25],
    }


def mining_daily_quality(days: Sequence[Any]) -> dict[str, Any]:
    recent = days[-20:]
    rows: list[dict[str, Any]] = []
    for row in recent:
        metrics = mining_dict(row.daily_summary.get("metrics"))
        shadow = mining_dict(row.daily_summary.get("quant_shadow_candidate_evaluation"))
        q8_gate = mining_dict(row.q8_review.get("evaluation_trust_gate"))
        q9_windows = mining_list(row.q9_windows.get("windows"))
        rows.append({
            "day": row.day,
            "trade_count": mining_safe_int(metrics.get("trade_count")),
            "closed_trade_count": mining_safe_int(metrics.get("closed_trade_count")),
            "win_rate": mining_safe_float(metrics.get("win_rate")),
            "avg_return_pct": mining_safe_float(metrics.get("avg_return_pct")),
            "trade_index_count": len(row.trade_index),
            "q8_candidate_count": mining_safe_int(row.q8_review.get("candidate_count")),
            "q8_trusted_forward_count": mining_safe_int(q8_gate.get("trusted_forward_count")),
            "q8_promotion_allowed": q8_gate.get("promotion_allowed"),
            "q9_window_count": mining_safe_int(row.q9_windows.get("window_count"), len(q9_windows)),
            "q9_has_recovery": bool(row.q9_windows.get("recovery")),
            "shadow_candidate_count": mining_safe_int(shadow.get("deduped_candidate_count") or shadow.get("candidate_count")),
            "shadow_forward_coverage": mining_safe_float(shadow.get("forward_outcome_coverage")),
            "closeout_ok": row.closeout.get("ok"),
            "has_daily_report": bool(row.daily_report),
            "has_trade_index": bool(row.trade_index),
        })
    mismatches = [
        {
            "day": row["day"],
            "daily_trade_count": row["trade_count"],
            "trade_index_count": row["trade_index_count"],
        }
        for row in rows
        if row["trade_count"] != row["trade_index_count"] and row["has_trade_index"]
    ]
    missing_runtime_surface = [
        row["day"]
        for row in rows
        if row["trade_count"] > 0 and (not row["has_daily_report"] or not row["has_trade_index"])
    ]
    q9_counts = [row["q9_window_count"] for row in rows if row["q9_window_count"]]
    shadow_coverages = [
        row["shadow_forward_coverage"]
        for row in rows
        if row["shadow_forward_coverage"] is not None
    ]
    return {
        "recent_days": rows,
        "trade_index_mismatch_examples": mismatches[:20],
        "missing_runtime_surface_days": missing_runtime_surface,
        "q9_window_count_average_recent": mining_avg([float(v) for v in q9_counts]),
        "shadow_forward_coverage_average_recent": mining_avg([float(v) for v in shadow_coverages]),
    }


def mining_q9_overlap(days: Sequence[Any]) -> dict[str, Any]:
    q9_days = [row for row in days if row.q9_windows]
    q8_days = [row for row in days if row.q8_review]
    daily_summary_days = [row for row in days if row.daily_summary]
    outside_q9_fields = [
        "weekly pattern_performance",
        "weekly strategist_llm_evaluation",
        "symbol-level pattern_performance",
        "symbol-level quant_shadow_candidate_evaluation",
        "operator_readout recurring issues",
        "market_regime_rail_review joined to realized symbol performance",
    ]
    q9_direct_fields = [
        "daily q9_decision_windows",
        "daily q8_shadow_blocker_review",
        "daily artifact availability/inventory",
        "realized trade scorecards under reports/evaluation",
    ]
    window_counts = [
        mining_safe_int(row.q9_windows.get("window_count"), len(mining_list(row.q9_windows.get("windows"))))
        for row in q9_days
    ]
    return {
        "q9_operator_summary_day_count": len(q9_days),
        "q8_operator_summary_day_count": len(q8_days),
        "daily_summary_day_count": len(daily_summary_days),
        "q9_window_count_total": sum(window_counts),
        "q9_window_count_average": mining_avg([float(v) for v in window_counts]),
        "already_consumed_by_q9": q9_direct_fields,
        "not_fully_consumed_by_q9": outside_q9_fields,
    }


def mining_weekly_row(week: str, summary: dict[str, Any]) -> dict[str, Any]:
    metrics = mining_dict(summary.get("metrics"))
    return {
        "week": week,
        "has_summary": bool(summary),
        "trade_count": mining_safe_int(metrics.get("trade_count")),
        "win_rate": mining_safe_float(metrics.get("win_rate")),
        "avg_return_pct": mining_safe_float(metrics.get("avg_return_pct")),
        "has_pattern_performance": bool(summary.get("pattern_performance")),
        "has_quant_tactic_evaluation": bool(summary.get("quant_tactic_evaluation")),
        "has_shadow_evaluation": bool(summary.get("quant_shadow_candidate_evaluation")),
        "has_strategist_llm_evaluation": bool(summary.get("strategist_llm_evaluation")),
    }


def mining_weekly_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "weekly_count": len(rows),
        "recent_weeks": rows[-6:],
        "usable_week_count": sum(
            1
            for row in rows
            if row["has_pattern_performance"]
            and row["has_quant_tactic_evaluation"]
            and row["has_shadow_evaluation"]
        ),
    }


def mining_symbol_row(symbol: str, summary: dict[str, Any], memory: dict[str, Any]) -> dict[str, Any]:
    metrics = mining_dict(summary.get("metrics"))
    trade_stats = mining_dict(mining_dict(memory.get("symbol_memory")).get("trade_stats") or memory.get("trade_stats"))
    return {
        "symbol": symbol,
        "trade_count": mining_safe_int(metrics.get("trade_count") or trade_stats.get("trade_count")),
        "closed_trade_count": mining_safe_int(metrics.get("closed_trade_count") or trade_stats.get("completed_trade_count")),
        "win_rate": mining_safe_float(metrics.get("win_rate") if metrics else trade_stats.get("win_rate")),
        "avg_return_pct": mining_safe_float(metrics.get("avg_return_pct") if metrics else trade_stats.get("avg_return_pct")),
        "has_pattern_performance": bool(summary.get("pattern_performance")),
        "has_shadow_evaluation": bool(summary.get("quant_shadow_candidate_evaluation")),
        "has_strategist_llm_evaluation": bool(summary.get("strategist_llm_evaluation")),
    }


def mining_symbol_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows.sort(key=lambda row: (row["trade_count"], row["symbol"]), reverse=True)
    return {
        "symbol_count": len(rows),
        "symbols_with_trade_count_ge_2": sum(1 for row in rows if row["trade_count"] >= 2),
        "symbols_with_trade_count_ge_5": sum(1 for row in rows if row["trade_count"] >= 5),
        "top_symbols": rows[:25],
    }


def mining_fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def render_operator_summary_mining_markdown(payload: dict[str, Any]) -> str:
    presence = mining_dict(payload.get("daily_presence"))
    daily = mining_dict(payload.get("daily_quality"))
    weekly = mining_dict(payload.get("weekly_quality"))
    symbols = mining_dict(payload.get("symbol_quality"))
    q9 = mining_dict(payload.get("q9_overlap"))
    readiness = mining_dict(payload.get("readiness"))
    lines = [
        "# Operator Summary Mining Report",
        "",
        f"- Schema: `{payload.get('schema_version')}`",
        f"- Behavior effect: `{payload.get('behavior_effect')}`",
        f"- Source: `{payload.get('source')}`",
        f"- Readiness: **{readiness.get('status', '')}**",
        "",
        "## Coverage",
        "",
        f"- Daily range: {presence.get('first_day', '')} to {presence.get('last_day', '')}",
        f"- Daily directories: {presence.get('daily_count', 0)}",
        f"- Weekly summaries: {weekly.get('weekly_count', 0)}",
        f"- Symbol summaries: {symbols.get('symbol_count', 0)}",
        f"- Symbols with >=5 trades: {symbols.get('symbols_with_trade_count_ge_5', 0)}",
        f"- Q9-linked operator days: {q9.get('q9_operator_summary_day_count', 0)}",
        f"- Q9 decision windows total: {q9.get('q9_window_count_total', 0)}",
        "",
        "## Daily Artifact Presence",
        "",
        "| Artifact | Count | Ratio |",
        "|---|---:|---:|",
    ]
    counts = mining_dict(presence.get("presence_counts"))
    ratios = mining_dict(presence.get("presence_ratio"))
    for name in sorted(counts):
        lines.append(f"| `{name}` | {counts[name]} | {mining_fmt(ratios.get(name))} |")
    lines.extend([
        "",
        "## Recent Daily Quality",
        "",
        "| Day | Trades | Trade Index | Q8 Candidates | Q9 Windows | Shadow Forward Coverage | Closeout |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in mining_list(daily.get("recent_days")):
        lines.append(
            "| {day} | {trades} | {trade_index} | {q8} | {q9w} | {coverage} | {closeout} |".format(
                day=row.get("day", ""),
                trades=row.get("trade_count", 0),
                trade_index=row.get("trade_index_count", 0),
                q8=row.get("q8_candidate_count", 0),
                q9w=row.get("q9_window_count", 0),
                coverage=mining_fmt(row.get("shadow_forward_coverage")),
                closeout=mining_fmt(row.get("closeout_ok")),
            )
        )
    lines.extend([
        "",
        "## Weekly Evidence",
        "",
        "| Week | Trades | Win Rate | Avg Return % | Pattern | Quant | Shadow | Strategist LLM |",
        "|---|---:|---:|---:|---|---|---|---|",
    ])
    for row in mining_list(weekly.get("recent_weeks")):
        lines.append(
            "| {week} | {trades} | {win} | {avg} | {pattern} | {quant} | {shadow} | {llm} |".format(
                week=row.get("week", ""),
                trades=row.get("trade_count", 0),
                win=mining_fmt(row.get("win_rate")),
                avg=mining_fmt(row.get("avg_return_pct")),
                pattern=row.get("has_pattern_performance"),
                quant=row.get("has_quant_tactic_evaluation"),
                shadow=row.get("has_shadow_evaluation"),
                llm=row.get("has_strategist_llm_evaluation"),
            )
        )
    lines.extend([
        "",
        "## Top Symbol Evidence",
        "",
        "| Symbol | Trades | Closed | Win Rate | Avg Return % | Pattern | Shadow | Strategist LLM |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ])
    for row in mining_list(symbols.get("top_symbols"))[:15]:
        lines.append(
            "| {symbol} | {trades} | {closed} | {win} | {avg} | {pattern} | {shadow} | {llm} |".format(
                symbol=row.get("symbol", ""),
                trades=row.get("trade_count", 0),
                closed=row.get("closed_trade_count", 0),
                win=mining_fmt(row.get("win_rate")),
                avg=mining_fmt(row.get("avg_return_pct")),
                pattern=row.get("has_pattern_performance"),
                shadow=row.get("has_shadow_evaluation"),
                llm=row.get("has_strategist_llm_evaluation"),
            )
        )
    lines.extend([
        "",
        "## Q9 Overlap",
        "",
        "Already consumed by Q9:",
    ])
    for item in mining_list(q9.get("already_consumed_by_q9")):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Not fully consumed by Q9:")
    for item in mining_list(q9.get("not_fully_consumed_by_q9")):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Readiness Notes",
        "",
        "Strengths:",
    ])
    for item in mining_list(readiness.get("strengths")):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Issues:")
    issues = mining_list(readiness.get("issues"))
    if issues:
        for item in issues:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Recommended use:")
    for item in mining_list(readiness.get("recommended_use")):
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


# --- A7.3: agent effectiveness scorecard ----------------------------------------


def score_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def scorecard_overlay_metrics(primary: Mapping[str, Any]) -> dict[str, Any]:
    """Overlay keys, falling back to the legacy strategist_* names of older reviews."""
    return {
        "strategy_ranking_overlay_comparison_count": primary.get(
            "strategy_ranking_overlay_comparison_count", primary.get("strategist_comparison_count")
        ),
        "strategy_ranking_overlay_day_count": primary.get(
            "strategy_ranking_overlay_day_count", primary.get("strategist_day_count")
        ),
        "average_strategy_ranking_overlay_delta_pct": primary.get(
            "average_strategy_ranking_overlay_delta_pct", primary.get("average_strategist_delta_pct")
        ),
        "strategy_ranking_overlay_positive_delta_rate": primary.get(
            "strategy_ranking_overlay_positive_delta_rate", primary.get("strategist_positive_delta_rate")
        ),
    }


def _decided(component: Mapping[str, Any], state: str) -> dict[str, Any]:
    return {"state": state, "source_decision": component.get("decision"), "reason": component.get("finding")}


def assemble_agent_effectiveness_scorecard(
    *,
    contract_version: Any,
    date_range: Mapping[str, Any],
    trade_total: int,
    excluded: int,
    scanner_relative: str,
    scanner_absolute: str,
    overlay: dict[str, Any],
    refresh: dict[str, Any],
    commander: dict[str, Any],
    monitor_entry: Mapping[str, Any],
    monitor_exit: Mapping[str, Any],
    full_system: Mapping[str, Any],
    decision_state: Any,
) -> dict[str, Any]:
    return {
        "schema_version": "agent_effectiveness_scorecard.v1",
        "contract_version": contract_version,
        "behavior_effect": "evaluation_only",
        "range": dict(date_range),
        "runtime_order": [
            "commander_operating_context",
            "strategist_initial_frame",
            "strategy_guided_scanner",
            "optional_post_scanner_strategist_refresh",
            "optional_scanner_rerun",
            "monitor_entry",
            "commander_decision",
            "execution",
            "monitor_exit_horizon",
        ],
        "state_contract": ["NOT_MEASURABLE", "DEFECT", "DEGRADING", "NEUTRAL", "VALUE_ADD"],
        "integrity": {
            "state": "PASS_WITH_EXCLUSIONS" if excluded else "PASS",
            "trade_model_count": trade_total,
            "excluded_trade_model_count": excluded,
        },
        "components": {
            "scanner": {
                "relative_ranking_state": scanner_relative,
                "absolute_edge_state": scanner_absolute,
                "question": "Given the Strategist frame, did Scanner rank cost-positive candidates well?",
                "source": "q9_full_chain_component_review.component_decisions.scanner",
            },
            "strategist": {
                "full_contribution": {
                    "state": "NOT_MEASURABLE",
                    "reason": "Strategist runs before Scanner and influences candidate sourcing.",
                    "missing_control": "parallel strategy-neutral candidate sourcing and ranking shadow",
                },
                "scenario_quality": {
                    "state": "NOT_MEASURABLE",
                    "reason": "scenario forecasts are not yet joined to a fixed subsequent-market target in this scorecard",
                    "missing_control": "scenario/horizon forecast outcome join",
                },
                "ranking_overlay": overlay,
                "post_scanner_refresh": refresh,
            },
            "commander": commander,
            "monitor_entry": _decided(monitor_entry, decision_state(monitor_entry)),
            "monitor_exit_horizon": _decided(monitor_exit, decision_state(monitor_exit)),
            "full_system": _decided(full_system, decision_state(full_system)),
        },
        "controls": {
            "A_SCANNER_CONTROL": {
                "semantic_role": "SCANNER_INTRINSIC_SAME_UNIVERSE",
                "full_pre_strategist_control": False,
            },
            "B_STRATEGIST_RANKED": {"semantic_role": "STRATEGY_WEIGHTED_SCANNER_RANKING"},
            "R1_PRE_REFRESH_SCANNER": {"semantic_role": "SCANNER_BEFORE_POST_SCANNER_STRATEGIST_REFRESH"},
            "R2_POST_REFRESH_SCANNER": {"semantic_role": "SCANNER_AFTER_POST_SCANNER_STRATEGIST_REFRESH"},
        },
        "behavior_change_authorized": False,
    }


def render_agent_effectiveness_scorecard(payload: Mapping[str, Any]) -> str:
    date_range = score_mapping(payload.get("range"))
    components = score_mapping(payload.get("components"))
    strategist = score_mapping(components.get("strategist"))
    lines = [
        f"# Agent Effectiveness Scorecard ({date_range.get('start')} ~ {date_range.get('end')})",
        "",
        "Evaluation-only. This report does not change trading behavior.",
        "",
        "## Component States",
        "",
        "| Component | State | Meaning |",
        "|---|---|---|",
        f"| Scanner relative ranking | `{score_mapping(components.get('scanner')).get('relative_ranking_state')}` | Strategy-conditioned rank precision |",
        f"| Scanner absolute edge | `{score_mapping(components.get('scanner')).get('absolute_edge_state')}` | Cost-adjusted candidate edge |",
        f"| Strategist full contribution | `{score_mapping(strategist.get('full_contribution')).get('state')}` | Requires strategy-neutral source control |",
        f"| Strategist ranking overlay | `{score_mapping(strategist.get('ranking_overlay')).get('state')}` | Same-universe intrinsic vs strategy-weighted |",
        f"| Strategist post-Scanner refresh | `{score_mapping(strategist.get('post_scanner_refresh')).get('state')}` | First Scanner vs refreshed Scanner |",
        f"| Commander | `{score_mapping(components.get('commander')).get('state')}` | Presented candidate vs approve/veto |",
        f"| Monitor Entry | `{score_mapping(components.get('monitor_entry')).get('state')}` | Selected baseline vs entry/block |",
        f"| Monitor Exit/Horizon | `{score_mapping(components.get('monitor_exit_horizon')).get('state')}` | Actual exit vs strategy-valid alternatives |",
        f"| Full system | `{score_mapping(components.get('full_system')).get('state')}` | Broker-net result |",
        "",
        "## Strategist Control Boundary",
        "",
        "- `A_SCANNER_CONTROL` is a same-candidate-universe intrinsic ranking control.",
        "- It is not a fully raw pre-Strategist Scanner because Strategist runs first.",
        "- Full Strategist value remains `NOT_MEASURABLE` until a strategy-neutral candidate-source shadow exists.",
        "- Ranking overlay and post-Scanner refresh are evaluated separately.",
        "",
        "## Evidence Shortfalls",
        "",
    ]
    for name, row in (
        ("Strategist full", score_mapping(strategist.get("full_contribution"))),
        ("Strategist scenario", score_mapping(strategist.get("scenario_quality"))),
        ("Strategist overlay", score_mapping(strategist.get("ranking_overlay"))),
        ("Strategist refresh", score_mapping(strategist.get("post_scanner_refresh"))),
        ("Commander", score_mapping(components.get("commander"))),
    ):
        if row.get("state") == "NOT_MEASURABLE":
            lines.append(f"- {name}: {row.get('missing_control') or row.get('reason')}")
    return "\n".join(lines) + "\n"
