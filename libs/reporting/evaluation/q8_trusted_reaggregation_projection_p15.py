"""Pure Q8 trusted-reaggregation projection and Markdown readout (P1.5 DEV-A).

Per-day trust-gate rows, the cumulative aggregate, the report envelope and the Markdown text behind
``libs.reporting.q8_trusted_reaggregation``. No I/O, clock or loaders: the facade iterates the days, loads the
shadow payloads, calls ``build_quant_shadow_candidate_evaluation`` and writes the files. ``*_impl`` bodies resolve
every helper and trust constant on the injected ``facade`` at call time (patching a facade attribute behaves as
before the move).
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping


def _fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except Exception:
        return "-"


def _fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


def _watchlist_rows(scorecard: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [dict(row) for row in list(scorecard.get("promotion_watchlist") or []) if isinstance(row, Mapping)]


def daily_row_impl(day: str, evaluation: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    scorecard = (
        evaluation.get("no_trade_scorecard")
        if isinstance(evaluation.get("no_trade_scorecard"), Mapping)
        else {}
    )
    trust_gate = (
        evaluation.get("evaluation_trust_gate")
        if isinstance(evaluation.get("evaluation_trust_gate"), Mapping)
        else {}
    )
    return {
        "day": day,
        "payload_count": int(evaluation.get("payload_count") or 0),
        "candidate_count": int(evaluation.get("candidate_count") or 0),
        "deduped_candidate_count": int(evaluation.get("deduped_candidate_count") or 0),
        "duplicate_candidate_count": int(evaluation.get("duplicate_candidate_count") or 0),
        "duplicate_rate": float(trust_gate.get("duplicate_rate") or 0.0),
        "trusted_forward_count": int(evaluation.get("forward_outcome_available_count") or 0),
        "trusted_forward_coverage": float(evaluation.get("forward_outcome_coverage") or 0.0),
        "scorecard_status": scorecard.get("status") or "not_available",
        "trust_gate_status": trust_gate.get("status") or "not_available",
        "promotion_allowed": bool(trust_gate.get("promotion_allowed")),
        "trust_reasons": list(trust_gate.get("block_reasons") or trust_gate.get("reasons") or []),
        "promotion_watchlist": facade._watchlist_rows(scorecard),
    }


def reaggregation_payload_impl(
    *,
    start: str,
    end: str,
    daily: List[Dict[str, Any]],
    promotion_allowed_day_count: int,
    cumulative_evaluation: Mapping[str, Any],
    facade: Any,
) -> Dict[str, Any]:
    cumulative_scorecard = (
        cumulative_evaluation.get("no_trade_scorecard")
        if isinstance(cumulative_evaluation.get("no_trade_scorecard"), Mapping)
        else {}
    )
    cumulative_trust_gate = (
        cumulative_evaluation.get("evaluation_trust_gate")
        if isinstance(cumulative_evaluation.get("evaluation_trust_gate"), Mapping)
        else {}
    )
    aggregate = {
        "candidate_count": int(cumulative_evaluation.get("candidate_count") or 0),
        "deduped_candidate_count": int(cumulative_evaluation.get("deduped_candidate_count") or 0),
        "duplicate_candidate_count": int(cumulative_evaluation.get("duplicate_candidate_count") or 0),
        "duplicate_rate": float(cumulative_trust_gate.get("duplicate_rate") or 0.0),
        "forward_outcome_available_count": int(cumulative_evaluation.get("forward_outcome_available_count") or 0),
        "trusted_forward_coverage": float(cumulative_evaluation.get("forward_outcome_coverage") or 0.0),
        "promotion_allowed_day_count": promotion_allowed_day_count,
        "cumulative_trust_gate_status": cumulative_trust_gate.get("status") or "not_available",
        "cumulative_promotion_allowed": bool(cumulative_trust_gate.get("promotion_allowed")),
        "cumulative_trust_reasons": list(
            cumulative_trust_gate.get("block_reasons") or cumulative_trust_gate.get("reasons") or []
        ),
        "promotion_watchlist": facade._watchlist_rows(cumulative_scorecard),
    }
    return {
        "schema_version": "q8_trusted_reaggregation.v2",
        "behavior_effect": "evaluation_only",
        "generated_with": "same_day_max_delay_forward_outcomes_deduped_candidates_and_trust_gate",
        "range": {"start": str(start)[:10], "end": str(end)[:10], "days_with_payloads": len(daily)},
        "aggregate": aggregate,
        "daily": daily,
        "important_note": (
            "Promotion decisions must use trusted same-day forward outcomes, deduped candidates, "
            "and promotion_allowed=true trust-gate rows only."
        ),
    }


def render_q8_trusted_reaggregation_markdown_impl(payload: Mapping[str, Any], *, facade: Any) -> str:
    date_range = payload.get("range") if isinstance(payload.get("range"), Mapping) else {}
    aggregate = payload.get("aggregate") if isinstance(payload.get("aggregate"), Mapping) else {}
    daily = list(payload.get("daily") or [])
    lines = [
        f"# Q8 Trusted Reaggregation ({date_range.get('start') or '-'} ~ {date_range.get('end') or '-'})",
        "",
        "This report is evaluation-only. It does not change trading behavior.",
        "",
        "## Summary",
        "",
        f"- raw candidates: **{facade._fmt_num(aggregate.get('candidate_count'))}**",
        f"- deduped candidates: **{facade._fmt_num(aggregate.get('deduped_candidate_count'))}**",
        f"- duplicate count/rate: **{facade._fmt_num(aggregate.get('duplicate_candidate_count'))} / {facade._fmt_pct(aggregate.get('duplicate_rate'))}**",
        f"- trusted forward: **{facade._fmt_num(aggregate.get('forward_outcome_available_count'))} / {facade._fmt_pct(aggregate.get('trusted_forward_coverage'))}**",
        f"- promotion allowed days: **{facade._fmt_num(aggregate.get('promotion_allowed_day_count'))}**",
        f"- cumulative trust gate: **`{aggregate.get('cumulative_trust_gate_status') or 'not_available'}`**",
        f"- cumulative promotion allowed: **`{bool(aggregate.get('cumulative_promotion_allowed'))}`**",
        f"- cumulative block reasons: **{', '.join(str(x) for x in list(aggregate.get('cumulative_trust_reasons') or [])) or '-'}**",
        "",
        "## Daily Trust Gate",
        "",
        "| Day | Raw | Deduped | Dup Rate | Trusted Forward | Trust Gate | Promotion | Reasons |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in daily:
        reasons = ", ".join(str(x) for x in list(row.get("trust_reasons") or [])) or "-"
        lines.append(
            "| {day} | {raw} | {deduped} | {dup_rate} | {forward} ({coverage}) | `{gate}` | `{allowed}` | {reasons} |".format(
                day=row.get("day") or "-",
                raw=facade._fmt_num(row.get("candidate_count")),
                deduped=facade._fmt_num(row.get("deduped_candidate_count")),
                dup_rate=facade._fmt_pct(row.get("duplicate_rate")),
                forward=facade._fmt_num(row.get("trusted_forward_count")),
                coverage=facade._fmt_pct(row.get("trusted_forward_coverage")),
                gate=row.get("trust_gate_status") or "-",
                allowed=bool(row.get("promotion_allowed")),
                reasons=reasons,
            )
        )
    lines += [
        "",
        "## Promotion Watchlist",
        "",
        "| Day | Candidate | Observed | Days | +5m | +15m | MAE5 | State |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    watch_count = 0
    for item in list(aggregate.get("promotion_watchlist") or []):
        if not isinstance(item, Mapping):
            continue
        watch_count += 1
        lines.append(
            "| {day} | `{name}` | {obs}/{count} | {days} | {ret5} | {ret15} | {mae5} | `{state}` |".format(
                day="cumulative",
                name=item.get("name") or "-",
                obs=facade._fmt_num(item.get("observed_count")),
                count=facade._fmt_num(item.get("candidate_count")),
                days=facade._fmt_num(item.get("observed_day_count")),
                ret5=f"{float(item.get('avg_return_5m_pct')):.4f}%" if item.get("avg_return_5m_pct") is not None else "-",
                ret15=f"{float(item.get('avg_return_15m_pct')):.4f}%" if item.get("avg_return_15m_pct") is not None else "-",
                mae5=f"{float(item.get('avg_mae_5m_pct')):.4f}%" if item.get("avg_mae_5m_pct") is not None else "-",
                state=item.get("review_state") or "-",
            )
        )
    for row in daily:
        for item in list(row.get("promotion_watchlist") or []):
            if not isinstance(item, Mapping):
                continue
            watch_count += 1
            lines.append(
                "| {day} | `{name}` | {obs}/{count} | {days} | {ret5} | {ret15} | {mae5} | `{state}` |".format(
                    day=row.get("day") or "-",
                    name=item.get("name") or "-",
                    obs=facade._fmt_num(item.get("observed_count")),
                    count=facade._fmt_num(item.get("candidate_count")),
                    days=facade._fmt_num(item.get("observed_day_count")),
                    ret5=f"{float(item.get('avg_return_5m_pct')):.4f}%" if item.get("avg_return_5m_pct") is not None else "-",
                    ret15=f"{float(item.get('avg_return_15m_pct')):.4f}%" if item.get("avg_return_15m_pct") is not None else "-",
                    mae5=f"{float(item.get('avg_mae_5m_pct')):.4f}%" if item.get("avg_mae_5m_pct") is not None else "-",
                    state=item.get("review_state") or "-",
                )
            )
    if watch_count <= 0:
        lines.append("| - | - | 0/0 | 0 | - | - | - | no_watchlist |")
    lines += [
        "",
        "## Decision Rule",
        "",
        "- PROMOTE is not allowed unless the daily trust gate has `promotion_allowed=true`.",
        f"- A day is promotion-review eligible only when trusted forward count >= {facade.TRUSTED_FORWARD_MIN_COUNT}, "
        f"trusted coverage >= {facade.TRUSTED_FORWARD_MIN_COVERAGE:.0%}, and duplicate rate <= {facade.DUPLICATE_RATE_MAX:.0%}.",
        f"- Candidate-level promotion requires at least {facade.PROMOTION_CANDIDATE_MIN_OBSERVED} trusted observations "
        f"across at least {facade.PROMOTION_CANDIDATE_MIN_DAYS} observed days.",
        "- Cross-day or stale forward observations are excluded from trusted forward counts.",
        "- Duplicate candidates are removed before forward performance is averaged.",
    ]
    return "\n".join(lines)
