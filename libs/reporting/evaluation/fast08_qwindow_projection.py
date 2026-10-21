"""Pure Q13/Q14/Q16 window and cost-comparison projections (P1.5 FAST08 A8.3).

Daily Q13/Q14/horizon row projection, root-cause totals, Q13 score-axis summaries
(shared with the range report), Q16/Q17 cohort metric bundles and forward
integrity, cost-basis top-K comparison rows and the Markdown renderers. Window
dates, minimum samples/days, GO/NO_GO and RETAIN/ROLL_BACK decisions, candidate
classes, the positive-day rule, fee/tax constants and every artifact read stay in
``q13_q14_validation``, ``q16_proxy_rejection_review``, ``cost_basis_comparison``
and ``attribution_score_window``.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Sequence

from .metrics import performance_metrics

KST = timezone(timedelta(hours=9))


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def rows_of(value: Any) -> list[Mapping[str, Any]]:
    return [row for row in (value or []) if isinstance(row, Mapping)]


def axis_score(scores: Mapping[str, Any], key: str) -> int | None:
    """Score of one Q13 axis; INSUFFICIENT_EVIDENCE and unparsable values read as None (never 0)."""
    item = mapping(mapping(scores).get(key))
    if str(item.get("status") or "") == "INSUFFICIENT_EVIDENCE":
        return None
    value = item.get("score")
    if value is None:
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


# --- A8.3a: Q13/Q14 validation run -------------------------------------------------


def cause_trade_count(q14: Mapping[str, Any], cause: str) -> int:
    for row in rows_of(q14.get("cause_summary")):
        if str(row.get("root_cause") or "") == cause:
            return int(row.get("trade_count") or 0)
    return 0


def exit_horizon_count(horizon: Mapping[str, Any]) -> int:
    return sum(
        1
        for row in rows_of(horizon.get("rows"))
        if row.get("horizon_violation_candidate")
        or row.get("exited_before_min_hold")
        or row.get("exited_before_target_hold")
        or row.get("target_hold_would_improve_exit")
    )


Q13_AXES = (
    "selection_integrity_score",
    "scanner_alignment_score",
    "entry_timing_score",
    "exit_horizon_score",
    "evidence_quality_score",
)


def validation_day_row(
    day: str,
    *,
    q13: Mapping[str, Any],
    q14: Mapping[str, Any],
    horizon: Mapping[str, Any],
    actionable_causes: Sequence[str],
) -> dict[str, Any]:
    q14_trade_count = int(q14.get("trade_count") or 0)
    missing_count = cause_trade_count(q14, "Missing Evidence")
    root_counts = {
        "Scanner Ranking Failure": cause_trade_count(q14, "Scanner Ranking Failure"),
        "Candidate Filtering": cause_trade_count(q14, "Candidate Filtering"),
        "Strategist Override": cause_trade_count(q14, "Strategist Override"),
        "Exit Horizon": exit_horizon_count(horizon),
        "Missing Evidence": missing_count,
    }
    largest_behavior = str(mapping(q14.get("largest_behavior_root_cause")).get("root_cause") or "")
    if root_counts["Exit Horizon"] > max(root_counts.get(cause, 0) for cause in actionable_causes):
        largest_behavior = "Exit Horizon"
    scores = mapping(q13.get("scores"))
    return {
        "day": day,
        "q13_available": bool(q13),
        "q14_available": bool(q14),
        "horizon_available": bool(horizon),
        "report_complete": bool(q13 and q14 and horizon),
        "trade_count": q14_trade_count,
        "q13_scores": {key: axis_score(scores, key) for key in Q13_AXES},
        "root_cause_counts": root_counts,
        "largest_behavior_root_cause": largest_behavior,
        "missing_evidence_ratio": round(missing_count / q14_trade_count, 4) if q14_trade_count else 0.0,
    }


def validation_totals(daily_rows: Sequence[Mapping[str, Any]], *, max_daily_missing_ratio: float) -> dict[str, Any]:
    root_totals: Counter[str] = Counter()
    largest_counts: Counter[str] = Counter()
    missing_total = 0
    daily_missing_failures = 0
    for row in daily_rows:
        for cause, n in mapping(row.get("root_cause_counts")).items():
            root_totals[str(cause)] += int(n or 0)
        largest = str(row.get("largest_behavior_root_cause") or "")
        if largest:
            largest_counts[largest] += 1
        missing_total += int(mapping(row.get("root_cause_counts")).get("Missing Evidence") or 0)
        if float(row.get("missing_evidence_ratio") or 0.0) > max_daily_missing_ratio:
            daily_missing_failures += 1
    total_trades = sum(int(row.get("trade_count") or 0) for row in daily_rows)
    return {
        "total_trade_count": total_trades,
        "root_totals": root_totals,
        "largest_counts": largest_counts,
        "daily_missing_ratio_failures": daily_missing_failures,
        "missing_ratio": round(missing_total / total_trades, 4) if total_trades else 0.0,
    }


def render_q13_q14_validation_report(payload: Mapping[str, Any], *, tracked_causes: Sequence[str]) -> str:
    lines = [
        "# Q13/Q14 Validation Run",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Decision: `{payload.get('decision', '')}`",
        f"- Decision scope: `{payload.get('decision_scope', 'legacy')}`",
        f"- Behavior patch authorized: `{bool(payload.get('behavior_patch_authorized'))}`",
        f"- Days: {payload.get('day_count', 0)} / {payload.get('required_validation_days', 0)}",
        f"- Completed report days: {payload.get('completed_report_day_count', 0)}",
        f"- Total trades: {payload.get('total_trade_count', 0)}",
        f"- Missing Evidence ratio: {float(payload.get('missing_evidence_ratio') or 0):.1%}",
        f"- Decision reasons: {', '.join(str(row) for row in payload.get('decision_reasons') or []) or '-'}",
        "",
        "## Root Cause Totals",
        "",
        "| Root Cause | Total |",
        "| --- | ---: |",
    ]
    totals = mapping(payload.get("root_cause_totals"))
    for cause in tracked_causes:
        lines.append(f"| {cause} | {int(totals.get(cause) or 0)} |")
    lines.extend(
        [
            "",
            "## Daily Root Cause Table",
            "",
            "| Root Cause | " + " | ".join(str(day) for day in payload.get("days") or []) + " | Total |",
            "| --- | " + " | ".join("---:" for _ in payload.get("days") or []) + " | ---: |",
        ]
    )
    daily_rows = [row for row in payload.get("daily_rows") or [] if isinstance(row, Mapping)]
    for cause in tracked_causes:
        values = [int(mapping(row.get("root_cause_counts")).get(cause) or 0) for row in daily_rows]
        lines.append(f"| {cause} | " + " | ".join(str(value) for value in values) + f" | {sum(values)} |")
    lines.extend(
        [
            "",
            "## Q13 Scores",
            "",
            "| Day | Complete | Selection | Scanner | Entry | Exit | Evidence | Largest Behavior Root Cause | Missing Evidence |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for row in daily_rows:
        scores = mapping(row.get("q13_scores"))
        lines.append(
            f"| {row.get('day')} | {row.get('report_complete')} | "
            f"{scores.get('selection_integrity_score')} | "
            f"{scores.get('scanner_alignment_score')} | "
            f"{scores.get('entry_timing_score')} | "
            f"{scores.get('exit_horizon_score')} | "
            f"{scores.get('evidence_quality_score')} | "
            f"{row.get('largest_behavior_root_cause') or '-'} | "
            f"{float(row.get('missing_evidence_ratio') or 0):.1%} |"
        )
    lines.extend(["", "## Validation Rules", ""])
    for rule in payload.get("validation_rules") or []:
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines)


# --- A8.3b: Q13 attribution-score axes (window and range) ----------------------------


def axis_summary(rows: Sequence[Mapping[str, Any]], score_keys: Sequence[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in score_keys:
        values: list[int] = []
        status_counts: Counter[str] = Counter()
        reason_counts: Counter[str] = Counter()
        for row in rows:
            item = mapping(mapping(row.get("scores")).get(key))
            status_counts[str(item.get("status") or "MISSING")] += 1
            value = axis_score(row.get("scores"), key)
            if value is not None:
                values.append(value)
            for reason in item.get("reasons") or []:
                reason_counts[str(reason)] += 1
        summary[key] = {
            "valid_day_count": len(rows),
            "scored_day_count": len(values),
            "insufficient_day_count": status_counts.get("INSUFFICIENT_EVIDENCE", 0),
            "average_score": round(sum(values) / len(values), 2) if values else None,
            "min_score": min(values) if values else None,
            "max_score": max(values) if values else None,
            "status_counts": dict(status_counts),
            "top_reasons": [{"reason": reason, "count": n} for reason, n in reason_counts.most_common(10)],
        }
    return summary


def weakest_axis_counts(rows: Iterable[Mapping[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        weakest = str(mapping(row.get("weakest_observed_axis")).get("name") or "")
        if weakest:
            counts[weakest] += 1
    return counts


def weakest_average_axis(summary: Mapping[str, Any]) -> dict[str, Any]:
    averages = {key: item.get("average_score") for key, item in summary.items() if item.get("average_score") is not None}
    name, score = min(averages.items(), key=lambda item: float(item[1])) if averages else ("", None)
    return {"name": name, "average_score": score}


def score_day_table(day_rows: Sequence[Mapping[str, Any]], score_keys: Sequence[str]) -> list[dict[str, Any]]:
    return [
        {
            "day": row.get("day"),
            "valid": bool(row.get("counts_as_valid_day")),
            "available": bool(row.get("available")),
            "trade_count": row.get("trade_count"),
            "weakest_axis": mapping(row.get("weakest_observed_axis")).get("name") or "",
            **{key: axis_score(row.get("scores"), key) for key in score_keys},
        }
        for row in day_rows
    ]


def score_day_row(day: str, *, valid: bool, payload: Mapping[str, Any], trade_count: Any) -> dict[str, Any]:
    if not payload:
        return {
            "day": day,
            "counts_as_valid_day": valid,
            "available": False,
            "reason": "attribution_score_missing",
            "scores": {},
            "weakest_observed_axis": {},
            "trade_count": 0,
        }
    return {
        "day": day,
        "counts_as_valid_day": valid,
        "available": True,
        "reason": "",
        "scores": dict(payload.get("scores") or {}),
        "weakest_observed_axis": dict(payload.get("weakest_observed_axis") or {}),
        "trade_count": trade_count,
    }


def render_attribution_score_window(payload: Mapping[str, Any]) -> str:
    lines = [
        f"# Q13 Attribution Score Window - {payload.get('window_id', '')}",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Days: {payload.get('day_count', 0)} total / {payload.get('valid_day_count', 0)} valid",
        f"- Available attribution days: {payload.get('available_day_count', 0)}",
        f"- Valid-day trades: {payload.get('total_trade_count_valid_days', 0)}",
        f"- Weakest by average score: `{mapping(payload.get('weakest_axis_by_average_score')).get('name') or '-'}` "
        f"({mapping(payload.get('weakest_axis_by_average_score')).get('average_score')})",
        "",
        "## Axis Summary",
        "",
        "| Axis | Avg Score | Min | Max | Scored Days | Insufficient Days | Top Reasons |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for key, item in mapping(payload.get("axis_summary")).items():
        obj = mapping(item)
        reasons = ", ".join(f"{row.get('reason')} ({row.get('count')})" for row in obj.get("top_reasons") or []) or "-"
        lines.append(
            f"| {key} | {obj.get('average_score')} | {obj.get('min_score')} | "
            f"{obj.get('max_score')} | {obj.get('scored_day_count')} | "
            f"{obj.get('insufficient_day_count')} | {reasons} |"
        )
    lines.extend(["", "## Weakest Axis Distribution", ""])
    distribution = mapping(payload.get("weakest_axis_distribution"))
    if distribution:
        for key, n in sorted(distribution.items(), key=lambda item: (-int(item[1]), item[0])):
            lines.append(f"- `{key}`: {n}")
    else:
        lines.append("- No valid scored days.")
    lines.extend([
        "",
        "## Daily Rows",
        "",
        "| Day | Valid | Trades | Weakest | Selection | Scanner | Entry | Exit/Horizon | Evidence |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in payload.get("daily_rows") or []:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"| {row.get('day')} | {row.get('valid')} | {row.get('trade_count')} | "
            f"{row.get('weakest_axis') or '-'} | "
            f"{row.get('selection_integrity_score')} | "
            f"{row.get('scanner_alignment_score')} | "
            f"{row.get('entry_timing_score')} | "
            f"{row.get('exit_horizon_score')} | "
            f"{row.get('evidence_quality_score')} |"
        )
    lines.extend(["", "## Interpretation Rule", "", f"- {payload.get('interpretation_rule', '')}", ""])
    return "\n".join(lines)


# --- A8.3c: Q16 / Q17 cohort measurement ----------------------------------------------


def metric_bundle(rows: Sequence[Mapping[str, Any]], drag_pct: float, horizon: str) -> dict[str, Any]:
    gross: list[float] = []
    for row in rows:
        outcome = row.get("shadow_forward_outcome")
        outcome = outcome if isinstance(outcome, Mapping) else {}
        checkpoint = (outcome.get("checkpoints") or {}).get(horizon)
        checkpoint = checkpoint if isinstance(checkpoint, Mapping) else {}
        if checkpoint.get("status") != "observed":
            continue
        try:
            gross.append(float(checkpoint.get("return_pct")))
        except (TypeError, ValueError):
            continue
    return {"gross": performance_metrics(gross), "net": performance_metrics(value - drag_pct for value in gross)}


def observed_rows(rows: Sequence[Mapping[str, Any]], horizon: str) -> list[Mapping[str, Any]]:
    out: list[Mapping[str, Any]] = []
    for row in rows:
        outcome = row.get("shadow_forward_outcome")
        outcome = outcome if isinstance(outcome, Mapping) else {}
        checkpoint = (outcome.get("checkpoints") or {}).get(horizon)
        if isinstance(checkpoint, Mapping) and checkpoint.get("status") == "observed":
            out.append(row)
    return out


def epoch_day(value: Any) -> str:
    try:
        epoch = int(float(value))
    except Exception:
        return ""
    if epoch <= 0:
        return ""
    try:
        return datetime.fromtimestamp(epoch, tz=KST).strftime("%Y%m%d")
    except (OSError, OverflowError, ValueError):
        return ""


def timestamp_day(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) == 8 and text.isdigit():
        return text
    if len(text) in {12, 14} and text.isdigit():
        try:
            datetime.strptime(text[:8], "%Y%m%d")
            return text[:8]
        except ValueError:
            return ""
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10].replace("-", "")
    return epoch_day(value)


def forward_integrity(row: Mapping[str, Any]) -> tuple[str, list[str]]:
    expected_day = str(row.get("q16_day") or "").replace("-", "")
    base = mapping(row.get("shadow_forward_base"))
    base_day = timestamp_day(base.get("baseline_raw_ts")) or timestamp_day(base.get("baseline_epoch"))
    reasons: list[str] = []
    if not expected_day or not base_day:
        reasons.append("baseline_day_missing")
    elif expected_day != base_day:
        reasons.append("baseline_day_mismatch")
    outcome = mapping(row.get("shadow_forward_outcome"))
    for horizon, checkpoint in (outcome.get("checkpoints") or {}).items():
        if not isinstance(checkpoint, Mapping) or checkpoint.get("status") != "observed":
            continue
        observed_day = timestamp_day(checkpoint.get("observed_ts"))
        if observed_day and expected_day and observed_day != expected_day:
            reasons.append(f"{horizon}:observed_day_mismatch")
    return ("TRUSTED" if not reasons else "INVALID", reasons)


def expected_horizon(row: Mapping[str, Any]) -> str:
    value = str(mapping(row.get("directional_edge_estimate")).get("forward_horizon") or "").strip().lower()
    if not value:
        return ""
    return value if value.startswith("+") else f"+{value}"


def expected_horizon_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    live_drag: float,
    mock_drag: float,
    observation_horizons: Sequence[str],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        horizon = expected_horizon(row)
        strategy_horizon = str(mapping(row.get("directional_edge_estimate")).get("strategy_horizon") or "unknown")
        grouped.setdefault((horizon or "unknown", strategy_horizon), []).append(row)
    return [
        {
            "expected_forward_horizon": horizon,
            "strategy_horizon": strategy_horizon,
            "candidate_count": len(group),
            "live": metric_bundle(group, live_drag, horizon) if horizon in observation_horizons else {},
            "mock": metric_bundle(group, mock_drag, horizon) if horizon in observation_horizons else {},
        }
        for (horizon, strategy_horizon), group in sorted(grouped.items())
    ]


def cohort_horizons(
    cohorts: Mapping[str, Sequence[Mapping[str, Any]]],
    horizons: Sequence[str],
    *,
    live_drag: float,
    mock_drag: float,
) -> list[dict[str, Any]]:
    return [
        {
            "horizon": horizon,
            **{
                name: {"live": metric_bundle(rows, live_drag, horizon), "mock": metric_bundle(rows, mock_drag, horizon)}
                for name, rows in cohorts.items()
            },
        }
        for horizon in horizons
    ]


def q17_validation_block(
    q17_rows: Sequence[Mapping[str, Any]],
    *,
    start_day: str,
    live_drag: float,
    mock_drag: float,
    observation_horizons: Sequence[str],
) -> dict[str, Any]:
    class_counts = Counter(str(row.get("q17_candidate_class") or "") for row in q17_rows)
    unavailable = Counter(
        str(mapping(row.get("directional_edge_estimate")).get("reason") or "artifact_missing")
        for row in q17_rows
        if str(row.get("q17_candidate_class") or "")
        in {"DIRECTIONAL_EVIDENCE_UNAVAILABLE", "DIRECTIONAL_ESTIMATE_ARTIFACT_MISSING"}
    )
    below_cost = [row for row in q17_rows if row.get("q17_candidate_class") == "DIRECTIONAL_BELOW_COST_REJECTION"]
    admitted = [row for row in q17_rows if row.get("q17_candidate_class") == "DIRECTIONAL_ADMITTED"]

    def _per_horizon(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [
            {"horizon": h, "live": metric_bundle(rows, live_drag, h), "mock": metric_bundle(rows, mock_drag, h)}
            for h in observation_horizons
        ]

    return {
        "schema_version": "q17_directional_edge_validation.v1",
        "measurement_contract_version": "q17_expected_horizon.v2",
        "behavior_effect": "evaluation_only",
        "start_day": start_day,
        "class_counts": dict(class_counts),
        "unavailable_reasons": dict(unavailable),
        "below_cost_horizons": _per_horizon(below_cost),
        "admitted_horizons": _per_horizon(admitted),
        "below_cost_expected_horizon": expected_horizon_rows(
            below_cost, live_drag=live_drag, mock_drag=mock_drag, observation_horizons=observation_horizons
        ),
        "admitted_expected_horizon": expected_horizon_rows(
            admitted, live_drag=live_drag, mock_drag=mock_drag, observation_horizons=observation_horizons
        ),
    }


def render_q16_proxy_rejection_review(payload: Mapping[str, Any], *, default_q17_start: str) -> str:
    counts = payload.get("counts") or {}
    authority = payload.get("decision_authority") or {}
    lines = [
        "# Q16 Proxy-Only Rejection Review",
        "",
        f"- Window: `{payload.get('start_day')}` to `{payload.get('end_day')}`",
        f"- Evidence: **{payload.get('evidence_status')}**",
        f"- Decision: **{payload.get('decision')}**",
        f"- Decision authority: `{authority.get('status', 'LEGACY')}`",
        f"- Rolling diagnostic decision: `{authority.get('rolling_diagnostic_decision', payload.get('decision'))}`",
        f"- Exact proxy-only rejections: {counts.get('exact_proxy_only_rejection_count', 0)}",
        f"- Trusted forward rows: {counts.get('exact_trusted_forward_count', 0)}",
        f"- Invalid forward rows: {counts.get('forward_integrity_invalid_count', 0)}",
        f"- Exact +30m observations: {counts.get('exact_observed_30m_count', 0)}",
        f"- Exact observed days: {counts.get('exact_observed_day_count', 0)}",
        f"- Positive +30m days: {counts.get('positive_30m_day_count', 0)}",
        f"- Directional admitted candidates: {counts.get('directional_admitted_count', 0)}",
        f"- Legacy cost rejections without proxy attribution: {counts.get('legacy_cost_rejection_unattributed_count', 0)}",
        "",
        "| Horizon | Cohort | Basis | Count | Win Rate | Avg Return | Profit Factor | MDD |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    integrity_reasons = payload.get("forward_integrity_reason_counts") or {}
    if integrity_reasons:
        lines.insert(
            10,
            "- Invalid reasons: " + ", ".join(f"`{name}`={n}" for name, n in sorted(integrity_reasons.items())),
        )
    for horizon in payload.get("horizons") or []:
        for cohort in ("exact_proxy_only", "directional_admitted", "legacy_unattributed_cost_rejection"):
            for basis in ("live", "mock"):
                metric = ((horizon.get(cohort) or {}).get(basis) or {}).get("net") or {}
                lines.append(
                    f"| {horizon.get('horizon')} | {cohort} | {basis} | {metric.get('count', 0)} | "
                    f"{float(metric.get('win_rate') or 0):.2%} | {float(metric.get('average_return_pct') or 0):.4f}% | "
                    f"{float(metric.get('profit_factor') or 0):.4f} | {float(metric.get('maximum_drawdown_pct') or 0):.4f}% |"
                )
    lines += [
        "",
        "## Daily Exact Proxy-Only Decision Evidence",
        "",
        "| Day | Rejections | +30m Observed | Live Win Rate | Live Avg Return | Profit Factor | Positive Day |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload.get("daily_exact_proxy_only") or []:
        metric = row.get("live_net_30m") or {}
        lines.append(
            f"| {row.get('day')} | {row.get('exact_rejection_count', 0)} | "
            f"{row.get('observed_30m_count', 0)} | {float(metric.get('win_rate') or 0):.2%} | "
            f"{float(metric.get('average_return_pct') or 0):.4f}% | "
            f"{float(metric.get('profit_factor') or 0):.4f} | "
            f"{'yes' if row.get('positive_30m_day') else 'no'} |"
        )
    lines += ["", "Legacy rows are shown for context only. They cannot prove that the rejected edge was proxy-only."]
    if payload.get("evidence_status") == "DECISION_READY":
        if authority.get("status") == "FINAL_CLOSED":
            lines.append(
                "Q16 is closed. Later samples update diagnostics only; the authoritative "
                f"policy decision remains **{payload.get('decision')}**."
            )
        else:
            lines.append(f"Q16 decision is final under the fixed sample contract: **{payload.get('decision')}**.")
    else:
        lines.append("Q16 RETAIN/ROLL_BACK is unavailable until exact post-patch fields meet the sample contract.")
    q17 = payload.get("q17_directional_edge_validation") or {}
    lines += [
        "",
        "## Q17 Directional Edge Validation",
        "",
        f"- Start day: `{q17.get('start_day', default_q17_start)}`",
        f"- Measurement contract: `{q17.get('measurement_contract_version', 'legacy')}`",
    ]
    class_counts = q17.get("class_counts") or {}
    if class_counts:
        for name, n in sorted(class_counts.items()):
            lines.append(f"- `{name}`: {n}")
    else:
        lines.append("- No classified Q17 candidates.")
    unavailable_reasons = q17.get("unavailable_reasons") or {}
    if unavailable_reasons:
        lines.append("- Unavailable reasons:")
        for name, n in sorted(unavailable_reasons.items()):
            lines.append(f"  - `{name}`: {n}")
    expected_rows = q17.get("below_cost_expected_horizon") or []
    if expected_rows:
        lines += [
            "",
            "### Below-Cost Results At Intended Horizon",
            "",
            "| Strategy Horizon | Forward Horizon | Candidates | Observed | Live Net Avg |",
            "|---|---|---:|---:|---:|",
        ]
        for row in expected_rows:
            net = (row.get("live") or {}).get("net") or {}
            lines.append(
                f"| {row.get('strategy_horizon')} | {row.get('expected_forward_horizon')} | "
                f"{row.get('candidate_count', 0)} | {net.get('count', 0)} | "
                f"{float(net.get('average_return_pct') or 0):.4f}% |"
            )
    lines += ["", "Q17 fields are additive and do not change the final Q16 RETAIN/ROLL_BACK decision."]
    return "\n".join(lines) + "\n"


# --- A8.3d: cost-basis comparison ----------------------------------------------------------


def topk_rows_by_key(review: Mapping[str, Any]) -> dict[tuple[int, str], dict[str, Any]]:
    topk = mapping(review.get("topk_forward_performance"))
    return {
        (int(row.get("top_k") or 0), str(row.get("horizon") or "")): dict(row)
        for row in topk.get("rows") or []
        if isinstance(row, Mapping)
    }


def cost_comparison_rows(mock_review: Mapping[str, Any], live_review: Mapping[str, Any]) -> list[dict[str, Any]]:
    mock_rows = topk_rows_by_key(mock_review)
    live_rows = topk_rows_by_key(live_review)
    rows: list[dict[str, Any]] = []
    for key in sorted(mock_rows, key=lambda item: (item[1], item[0])):
        mock_row = mock_rows[key]
        live_row = live_rows.get(key, {})
        gross = mock_row.get("gross") if isinstance(mock_row.get("gross"), Mapping) else {}
        mock_net = mock_row.get("net") if isinstance(mock_row.get("net"), Mapping) else {}
        live_net = live_row.get("net") if isinstance(live_row.get("net"), Mapping) else {}
        rows.append(
            {
                "top_k": key[0],
                "horizon": key[1],
                "window_count": int(mock_row.get("window_count") or 0),
                "observed_day_count": int(mock_row.get("observed_day_count") or 0),
                "gross": dict(gross),
                "mock_net": dict(mock_net),
                "live_net": dict(live_net),
                "expectancy_delta_live_minus_mock_pct": round(
                    float(live_net.get("expectancy_pct") or 0.0) - float(mock_net.get("expectancy_pct") or 0.0), 4
                ),
            }
        )
    return rows


def render_cost_basis_comparison(payload: Mapping[str, Any]) -> str:
    date_range = payload.get("range") or {}
    bases = payload.get("cost_bases") or {}
    mock = bases.get("mock_observed") or {}
    live = bases.get("live_deployment_equity") or {}
    lines = [
        f"# Cost Basis Comparison ({date_range.get('start')} ~ {date_range.get('end')})",
        "",
        "Evaluation-only. Runtime entry, exit, and broker accounting are unchanged.",
        f"Forward data source: `{payload.get('forward_data_source') or 'unknown'}`.",
        f"Cohort scope: `{payload.get('cohort_scope') or 'unknown'}`.",
        "",
        "## Cost Assumptions",
        "",
        "| Basis | Round Trip | Slippage | Total Drag | Purpose |",
        "|---|---:|---:|---:|---|",
        f"| Mock observed | {float(mock.get('round_trip_cost_pct') or 0):.4f}% | "
        f"{float(bases.get('slippage_pct') or 0):.4f}% | "
        f"{float(mock.get('total_drag_with_slippage_pct') or 0):.4f}% | Mock PnL/cash truth |",
        f"| Live equity assumption | {float(live.get('round_trip_cost_pct') or 0):.4f}% | "
        f"{float(bases.get('slippage_pct') or 0):.4f}% | "
        f"{float(live.get('total_drag_with_slippage_pct') or 0):.4f}% | Deployment evaluation |",
        "",
        "## Pre-Strategist Scanner Top-K",
        "",
        "| Top-K | Horizon | Windows/Days | Gross | Mock Net | Live Net | Live-Mock Delta |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload.get("rows") or []:
        gross = row.get("gross") or {}
        mock_net = row.get("mock_net") or {}
        live_net = row.get("live_net") or {}
        lines.append(
            f"| {row.get('top_k')} | {row.get('horizon')} | "
            f"{row.get('window_count')}/{row.get('observed_day_count')} | "
            f"{float(gross.get('expectancy_pct') or 0):.4f}% | "
            f"{float(mock_net.get('expectancy_pct') or 0):.4f}% | "
            f"{float(live_net.get('expectancy_pct') or 0):.4f}% | "
            f"{float(row.get('expectancy_delta_live_minus_mock_pct') or 0):+.4f}% |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- Mock net answers whether the signal beats the mock account's observed friction.",
        "- Live net answers whether it beats the explicit 2026 KRX equity assumption.",
        "- ETF/ETN tax treatment requires instrument classification and is not inferred here.",
        "- This report does not authorize a trading-policy change.",
    ]
    return "\n".join(lines) + "\n"
