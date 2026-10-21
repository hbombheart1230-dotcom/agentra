"""Pure cumulative-performance, horizon-compliance and feedback projections (P1.5 FAST08 A8.4).

Cross-day strategist deltas, rank-row lookup, horizon-compliance row/group
aggregation, attribution-score range axes and the feedback exposure records, plus
their Markdown renderers. Artifact reads, day iteration, improvement-candidate
statuses, behavior-patch eligibility, ``DecisionClass`` and every threshold stay
in ``cumulative_improvement_review``, ``horizon_compliance_report``,
``attribution_score_range`` and ``feedback_effectiveness``. Missing evidence is
never converted into a score or an adoption.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping, Sequence

from .metrics import performance_metrics


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


# --- A8.4a: cumulative improvement ---------------------------------------------------


DELTA_HORIZONS = ("+5m", "+15m", "+30m", "EOD")


def strategist_day_delta(payload: Mapping[str, Any]) -> dict[str, float]:
    """B minus A average return per horizon for one daily comparison; only horizons with both sides traded."""
    out: dict[str, float] = {}
    for horizon in payload.get("horizons") or []:
        if not isinstance(horizon, Mapping):
            continue
        name = str(horizon.get("horizon") or "")
        if name not in DELTA_HORIZONS:
            continue
        performers = {
            str(row.get("performer") or ""): row for row in horizon.get("performers") or [] if isinstance(row, Mapping)
        }
        scanner = performers.get("A_SCANNER_CONTROL")
        strategist = performers.get("B_STRATEGIST_RANKED")
        if not scanner or not strategist:
            continue
        if not int(scanner.get("trade_count") or 0) or not int(strategist.get("trade_count") or 0):
            continue
        out[name] = float(strategist.get("avg_return_pct") or 0.0) - float(scanner.get("avg_return_pct") or 0.0)
    return out


def strategist_weighting_review(daily_deltas: Mapping[str, Sequence[float]]) -> dict[str, Any]:
    return {
        "schema_version": "strategist_weighting_cumulative_review.v1",
        "behavior_effect": "evaluation_only",
        "rows": [
            {
                "horizon": horizon,
                "observed_day_count": len(values),
                "strategist_better_day_count": sum(value > 0 for value in values),
                "strategist_worse_day_count": sum(value < 0 for value in values),
                "avg_strategist_minus_scanner_pct": round(sum(values) / len(values), 4) if values else None,
            }
            for horizon, values in daily_deltas.items()
        ],
        "interpretation": (
            "Paired daily B minus A deltas measure strategy-weighted ranking versus "
            "the same Scanner candidate universe. They do not measure candidate sourcing."
        ),
    }


def rank_row(review: Mapping[str, Any], *, bucket: str, horizon: str) -> Mapping[str, Any]:
    return next(
        (
            row
            for row in review.get("rank_horizon_rows") or []
            if isinstance(row, Mapping) and row.get("rank_bucket") == bucket and row.get("horizon") == horizon
        ),
        {},
    )


def outcome_conditioned_trade_count(q14: Mapping[str, Any]) -> int:
    return sum(
        int(row.get("trade_count") or 0)
        for row in q14.get("cause_summary") or []
        if isinstance(row, Mapping) and row.get("diagnostic_kind") == "outcome_conditioned"
    )


def render_cumulative_improvement_review(payload: Mapping[str, Any]) -> str:
    date_range = payload.get("range") or {}
    q14 = payload.get("q14_causal_interpretation") or {}
    episode = payload.get("episode_scanner_review") or {}
    reentry = payload.get("same_symbol_reentry_review") or {}
    reclaim = payload.get("post_reclaim_shadow_review") or {}
    lines = [
        f"# Cumulative Improvement Review - {date_range.get('start')} to {date_range.get('end')}",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect')}`",
        f"- Active validation: `{payload.get('active_validation')}`",
        f"- Behavior patch authorized: `{payload.get('behavior_patch_authorized')}`",
        f"- Scanner rows/episodes: {episode.get('raw_candidate_row_count', 0)} / {episode.get('episode_count', 0)}",
        f"- Score component coverage: {float((episode.get('score_component_review') or {}).get('coverage') or 0):.1%}",
        "",
        "## Q14 Causal Interpretation",
        "",
        f"- Legacy outcome-conditioned result: `{(q14.get('largest_legacy_behavior_root_cause') or {}).get('root_cause') or 'NONE'}`",
        f"- Largest structural result: `{(q14.get('largest_structural_root_cause') or {}).get('root_cause') or 'NONE'}`",
        f"- Outcome-conditioned trades: {q14.get('outcome_conditioned_trade_count', 0)}",
        f"- Rule: {q14.get('rule') or 'N/A'}",
        "",
        "## Episode-Level Scanner Ranking",
        "",
        "| Rank | Horizon | Episodes | Observed | Days | Gross | Live Net | Mock Net |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in episode.get("rank_horizon_rows") or []:
        if not isinstance(row, Mapping) or row.get("rank_bucket") == "unknown":
            continue
        lines.append(
            f"| {row.get('rank_bucket')} | {row.get('horizon')} | "
            f"{row.get('episode_count')} | {row.get('observed_count')} | "
            f"{row.get('observed_day_count')} | "
            f"{float((row.get('gross') or {}).get('expectancy_pct') or 0):.4f}% | "
            f"{float((row.get('live_net') or {}).get('expectancy_pct') or 0):.4f}% | "
            f"{float((row.get('mock_net') or {}).get('expectancy_pct') or 0):.4f}% |"
        )
    lines += [
        "",
        "## Same-Symbol Reentry",
        "",
        "| Cohort | Count | Win Rate | Expectancy | Profit Factor |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for label, key in (
        ("First", "first_entry"),
        ("Repeat", "repeat_entry"),
        ("Repeat after loss", "repeat_after_loss"),
        ("Repeat after non-loss", "repeat_after_non_loss"),
    ):
        row = reentry.get(key) or {}
        lines.append(
            f"| {label} | {row.get('count', 0)} | "
            f"{float(row.get('win_rate') or 0):.1%} | "
            f"{float(row.get('expectancy_pct') or 0):.4f}% | "
            f"{float(row.get('profit_factor') or 0):.4f} |"
        )
    lines += [
        "",
        "## Confirmed Post-Reclaim Shadow",
        "",
        f"- Status: `{reclaim.get('promotion_status')}`",
        f"- Observed: {reclaim.get('observed_count', 0)} across {reclaim.get('observed_day_count', 0)} days",
        "",
        "| Horizon | Gross | Live Net | Mock Net |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in reclaim.get("rows") or []:
        lines.append(
            f"| {row.get('horizon')} | "
            f"{float(row.get('gross_expectancy_pct') or 0):.4f}% | "
            f"{float(row.get('live_net_expectancy_pct') or 0):.4f}% | "
            f"{float(row.get('mock_net_expectancy_pct') or 0):.4f}% |"
        )
    lines += ["", "## Improvement Candidates", "", "| Priority | Candidate | Class | Status |", "| ---: | --- | --- | --- |"]
    for row in payload.get("improvement_candidates") or []:
        lines.append(f"| {row.get('priority')} | {row.get('candidate')} | {row.get('class')} | {row.get('status')} |")
    lines += ["", "## Decision Boundary", "", f"- {payload.get('next_decision')}", ""]
    return "\n".join(lines)


# --- A8.4b: horizon compliance ----------------------------------------------------------


def horizon_bucket_key(evaluation: Mapping[str, Any]) -> tuple[str, str]:
    horizon = mapping(evaluation.get("horizon_alignment"))
    exit_quality = mapping(evaluation.get("exit_quality"))
    return (
        str(horizon.get("strategy_horizon") or "unknown"),
        str(exit_quality.get("reason") or evaluation.get("exit_reason") or "unknown"),
    )


def horizon_compliance_row(evaluation: Mapping[str, Any]) -> dict[str, Any]:
    horizon = mapping(evaluation.get("horizon_alignment"))
    outcome = mapping(evaluation.get("realized_outcome"))
    exit_quality = mapping(evaluation.get("exit_quality"))
    return {
        "trade_id": evaluation.get("trade_id"),
        "symbol": evaluation.get("symbol"),
        "strategy_horizon": str(horizon.get("strategy_horizon") or "unknown"),
        "exit_reason": str(exit_quality.get("reason") or "unknown"),
        "bucket": str(horizon.get("bucket") or "unknown"),
        "actual_hold_sec": number(horizon.get("actual_hold_sec") or outcome.get("holding_seconds")),
        "expected_hold_window": mapping(horizon.get("expected_hold_window")),
        "net_return_pct": number(outcome.get("net_return_pct")),
        "exited_before_min_hold": bool(horizon.get("exited_before_min_hold")),
        "exited_before_target_hold": bool(horizon.get("exited_before_target_hold")),
        "exited_beyond_max_hold": bool(horizon.get("exited_beyond_max_hold")),
        "horizon_violation_candidate": bool(horizon.get("horizon_violation_candidate")),
        "target_hold_would_improve_exit": bool(horizon.get("target_hold_would_improve_exit")),
        "valid_early_exit": bool(horizon.get("valid_early_exit")),
        "early_exit_allowed_match": list(horizon.get("early_exit_allowed_match") or []),
        "target_checkpoint": mapping(horizon.get("target_checkpoint")),
        "max_post_exit_upside_pct": horizon.get("max_post_exit_upside_pct"),
        "max_post_exit_drawdown_pct": horizon.get("max_post_exit_drawdown_pct"),
    }


def horizon_group_rows(pairs: Iterable[tuple[tuple[str, str], Mapping[str, Any]]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "returns": [], "before_min": 0, "before_target": 0, "beyond_max": 0,
                 "target_improve": 0, "violation": 0, "hard_or_allowed": 0, "actual_hold_sec": []}
    )
    for key, row in pairs:
        group = grouped[key]
        group["count"] += 1
        if row["net_return_pct"] is not None:
            group["returns"].append(float(row["net_return_pct"]))
        if row["actual_hold_sec"] is not None:
            group["actual_hold_sec"].append(float(row["actual_hold_sec"]))
        group["before_min"] += int(row["exited_before_min_hold"])
        group["before_target"] += int(row["exited_before_target_hold"])
        group["beyond_max"] += int(row["exited_beyond_max_hold"])
        group["target_improve"] += int(row["target_hold_would_improve_exit"])
        group["violation"] += int(row["horizon_violation_candidate"])
        if row["valid_early_exit"] or row["early_exit_allowed_match"]:
            group["hard_or_allowed"] += 1
    out: list[dict[str, Any]] = []
    for (strategy_horizon, exit_reason), group in sorted(grouped.items()):
        hold = group["actual_hold_sec"]
        out.append(
            {
                "strategy_horizon": strategy_horizon,
                "exit_reason": exit_reason,
                "count": group["count"],
                "average_hold_sec": round(sum(hold) / len(hold), 2) if hold else None,
                "exit_before_min_hold_count": group["before_min"],
                "exit_before_target_hold_count": group["before_target"],
                "exit_beyond_max_hold_count": group["beyond_max"],
                "horizon_violation_candidate_count": group["violation"],
                "target_hold_would_improve_exit_count": group["target_improve"],
                "valid_or_allowed_early_exit_count": group["hard_or_allowed"],
                "performance": performance_metrics(group["returns"]),
            }
        )
    return out


def render_horizon_compliance_report(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Horizon Compliance Report",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Trades: {payload.get('trade_count', 0)}",
        f"- Policy warning: {payload.get('policy_warning', '')}",
        "",
        "## Horizon Counts",
        "",
    ]
    counts = mapping(payload.get("horizon_counts"))
    if counts:
        for key in sorted(counts):
            lines.append(f"- `{key}`: {counts[key]}")
    else:
        lines.append("- No observed horizons.")
    lines.extend([
        "",
        "## By Horizon And Exit Reason",
        "",
        "| Horizon | Exit Reason | Count | Avg Hold Sec | Before Min | Before Target | Target Hold Better | Avg Return |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in payload.get("group_rows") or []:
        if not isinstance(row, Mapping):
            continue
        avg_return = mapping(row.get("performance")).get("average_return_pct")
        lines.append(
            f"| {row.get('strategy_horizon')} | {row.get('exit_reason')} | "
            f"{row.get('count')} | {row.get('average_hold_sec')} | "
            f"{row.get('exit_before_min_hold_count')} | "
            f"{row.get('exit_before_target_hold_count')} | "
            f"{row.get('target_hold_would_improve_exit_count')} | "
            f"{'-' if avg_return is None else f'{float(avg_return):.4f}%'} |"
        )
    lines.append("")
    return "\n".join(lines)


# --- A8.4c: attribution score range ------------------------------------------------------


def range_score_row(
    day: str, *, payload: Mapping[str, Any], trade_count: int, axis_score_of: Any, score_keys: Sequence[str]
) -> dict[str, Any]:
    scores = dict(payload.get("scores") or {}) if payload else {}
    return {
        "day": day,
        "available": bool(payload),
        "scored": any(axis_score_of({"scores": scores}, key) is not None for key in score_keys),
        "reason": "" if payload else "attribution_score_missing",
        "trade_count": trade_count,
        "scores": scores,
        "weakest_observed_axis": dict(payload.get("weakest_observed_axis") or {}) if payload else {},
    }


def range_axis_summary(day_rows: Sequence[Mapping[str, Any]], score_keys: Sequence[str], axis_score_of: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in score_keys:
        values: list[int] = []
        status_counts: Counter[str] = Counter()
        reason_counts: Counter[str] = Counter()
        for row in day_rows:
            item = mapping(mapping(row.get("scores")).get(key))
            status_counts[str(item.get("status") or ("MISSING" if not row.get("available") else "MISSING_SCORE"))] += 1
            value = axis_score_of(row, key)
            if value is not None:
                values.append(value)
            for reason in item.get("reasons") or []:
                reason_counts[str(reason)] += 1
        summary[key] = {
            "day_count": len(day_rows),
            "scored_day_count": len(values),
            "missing_day_count": status_counts.get("MISSING", 0),
            "insufficient_day_count": status_counts.get("INSUFFICIENT_EVIDENCE", 0),
            "average_score": round(sum(values) / len(values), 2) if values else None,
            "min_score": min(values) if values else None,
            "max_score": max(values) if values else None,
            "status_counts": dict(status_counts),
            "top_reasons": [{"reason": r, "count": c} for r, c in reason_counts.most_common(10)],
        }
    return summary


def range_day_table(day_rows: Sequence[Mapping[str, Any]], score_keys: Sequence[str], axis_score_of: Any) -> list[dict[str, Any]]:
    return [
        {
            "day": row.get("day"),
            "available": bool(row.get("available")),
            "scored": bool(row.get("scored")),
            "trade_count": row.get("trade_count"),
            "weakest_axis": mapping(row.get("weakest_observed_axis")).get("name") or "",
            **{key: axis_score_of(row, key) for key in score_keys},
        }
        for row in day_rows
    ]


def render_attribution_score_range(payload: Mapping[str, Any]) -> str:
    title = f"{payload.get('start', '')} to {payload.get('end', '')}"
    lines = [
        f"# Q13 Attribution Score Range - {title}",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Days: {payload.get('day_count', 0)} total / {payload.get('available_day_count', 0)} available / {payload.get('scored_day_count', 0)} scored",
        f"- Trade days: {payload.get('trade_day_count', 0)}",
        f"- Total trades: {payload.get('total_trade_count', 0)}",
        f"- Scored trades: {payload.get('scored_trade_count', 0)}",
        f"- Weakest by average score: `{mapping(payload.get('weakest_axis_by_average_score')).get('name') or '-'}` "
        f"({mapping(payload.get('weakest_axis_by_average_score')).get('average_score')})",
        "",
        "## Axis Summary",
        "",
        "| Axis | Avg Score | Min | Max | Scored Days | Missing Days | Insufficient Days | Top Reasons |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for key, item in mapping(payload.get("axis_summary")).items():
        obj = mapping(item)
        reasons = ", ".join(f"{row.get('reason')} ({row.get('count')})" for row in obj.get("top_reasons") or []) or "-"
        lines.append(
            f"| {key} | {obj.get('average_score')} | {obj.get('min_score')} | "
            f"{obj.get('max_score')} | {obj.get('scored_day_count')} | "
            f"{obj.get('missing_day_count')} | {obj.get('insufficient_day_count')} | {reasons} |"
        )
    lines.extend(["", "## Weakest Axis Distribution", ""])
    distribution = mapping(payload.get("weakest_axis_distribution"))
    if distribution:
        for key, n in sorted(distribution.items(), key=lambda item: (-int(item[1]), item[0])):
            lines.append(f"- `{key}`: {n}")
    else:
        lines.append("- No scored days.")
    lines.extend([
        "",
        "## Daily Rows",
        "",
        "| Day | Available | Scored | Trades | Weakest | Selection | Scanner | Entry | Exit/Horizon | Evidence |",
        "| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in payload.get("daily_rows") or []:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"| {row.get('day')} | {row.get('available')} | {row.get('scored')} | "
            f"{row.get('trade_count')} | {row.get('weakest_axis') or '-'} | "
            f"{row.get('selection_integrity_score')} | "
            f"{row.get('scanner_alignment_score')} | "
            f"{row.get('entry_timing_score')} | "
            f"{row.get('exit_horizon_score')} | "
            f"{row.get('evidence_quality_score')} |"
        )
    lines.extend(["", "## Interpretation Rule", "", f"- {payload.get('interpretation_rule', '')}", ""])
    return "\n".join(lines)


# --- A8.4d: feedback exposure records ------------------------------------------------------


def feedback_window_record(window: Mapping[str, Any]) -> dict[str, Any] | None:
    """Exposure record for one Q9 window; None when the window carries no feedback id."""
    provenance = window.get("strategist_provenance") if isinstance(window.get("strategist_provenance"), dict) else {}
    feedback = provenance.get("feedback") if isinstance(provenance.get("feedback"), dict) else {}
    feedback_id = str(feedback.get("feedback_id") or "")
    if not feedback_id:
        return None
    adoption_status = str(feedback.get("adoption_status") or "")
    return {
        "feedback_id": feedback_id,
        "later_decision_id": str(window.get("decision_id") or window.get("q9_decision_id") or ""),
        "source_day": str(feedback.get("source_day") or ""),
        "consumed": bool(feedback.get("consumed")),
        "adoption_status": adoption_status,
        "adoption_candidate": adoption_status == "CHANGE_OBSERVED_WITH_FEEDBACK_EXPOSURE",
        "changed_fields": list(feedback.get("changed_fields") or []),
        "causal_attribution": False,
        "performance_delta_pct": None,
    }


def feedback_model_source(model: Mapping[str, Any]) -> str:
    """Feedback-bearing policy source of a trade model, or '' when the model was not exposed."""
    references = model.get("provenance") if isinstance(model.get("provenance"), dict) else {}
    fields = references.get("field_sources") if isinstance(references.get("field_sources"), dict) else {}
    source = str(fields.get("strategy_policy_source") or "")
    return source if "feedback" in source.lower() else ""
