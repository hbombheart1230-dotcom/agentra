"""Deterministic Markdown renderers for the Q8 review reports (P1.5 FAST06).

Byte-for-byte moves of the four Q8 report renderers. Thresholds shown in the
trusted-reaggregation decision rule are passed in by the facade, which keeps
importing them from ``q8_evaluation_contract``.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _lane_text(value: Any) -> str:
    return str(value or "").strip()


def _lane_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _lane_rows(value: Any) -> List[Dict[str, Any]]:
    return [dict(row) for row in list(value or []) if isinstance(row, Mapping)]


# --- A1: historical review ---


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> List[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(item) for item in row) + " |")
    return out


def render_q8_historical_review_markdown(payload: Mapping[str, Any]) -> str:
    trade = payload.get("trade_summary") if isinstance(payload.get("trade_summary"), Mapping) else {}
    lines: List[str] = [
        f"# Q8 Historical Review: {payload.get('start')} to {payload.get('end')}",
        "",
        "Purpose: reuse prior live and shadow evidence without mixing incompatible artifact eras.",
        "",
        "This review is evaluation-only. It does not change entry, exit, scanner, Strategist, or execution behavior.",
        "",
        "## Data Windows",
        "",
        "- Live trade performance: usable from 2026-05-18 onward when truth-surface PnL exists.",
        "- Q8 shadow evaluation: most useful from 2026-05-26 onward when candidate shadow summaries are populated.",
        "- Market regime rail: most useful from 2026-06-02 onward when rail IDs are attached to daily summaries.",
        "- Broker truth reconciliation: strongest from 2026-06-08 onward after post-close order-pair repair.",
        "",
        "## Live Trade Summary",
        "",
        f"- Trade report files: **{trade.get('trade_report_count', 0)}**",
        f"- Return samples: **{trade.get('return_sample_count', 0)}**",
        f"- Win rate: **{float(trade.get('win_rate') or 0.0) * 100:.2f}%**",
        f"- Average return: **{float(trade.get('avg_return_pct') or 0.0):.4f}%**",
        "",
    ]
    daily_rows = list(payload.get("daily_rows") or [])
    if daily_rows:
        lines.extend(
            _md_table(
                ["Day", "Trades", "Closed", "Returns", "Missing", "Win", "Avg", "Raw", "Deduped", "Trusted", "Gate", "Allowed", "Rail"],
                [
                    [
                        row.get("day"),
                        row.get("trade_count"),
                        row.get("closed_trade_count"),
                        row.get("return_sample_count"),
                        row.get("unavailable_return_count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.2f}%",
                        row.get("shadow_candidate_count") or 0,
                        row.get("shadow_deduped_candidate_count") or 0,
                        row.get("q8_trusted_forward_count") or 0,
                        row.get("q8_trust_gate_status") or "legacy/no_gate",
                        bool(row.get("q8_promotion_allowed")),
                        row.get("market_regime_rail") or "-",
                    ]
                    for row in daily_rows
                ],
            )
        )
        lines.append("")
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), Mapping) else {}
    lines.extend(
        [
            "## Q8 Promotion Eligibility",
            "",
            f"- status: `{eligibility.get('status') or 'unknown'}`",
            f"- trusted gate days: **{eligibility.get('trusted_gate_day_count') or 0}**",
            f"- promotion allowed days: **{eligibility.get('promotion_allowed_day_count') or 0}**",
            f"- rule: {eligibility.get('rule') or '-'}",
            "",
        ]
    )
    lines.extend(["## Trade Pattern Evidence", ""])
    for title, key in (
        ("By Tactic", "trade_by_tactic"),
        ("By Entry Reason", "trade_by_entry_reason"),
        ("By Exit Reason", "trade_by_exit_reason"),
    ):
        rows = list(payload.get(key) or [])
        lines.extend([f"### {title}", ""])
        lines.extend(
            _md_table(
                ["Name", "Count", "Win", "Avg"],
                [
                    [
                        row.get("name"),
                        row.get("count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.3f}%",
                    ]
                    for row in rows[:10]
                ],
            )
        )
        lines.append("")
    lines.extend(
        [
            "## Q8 Shadow Summary",
            "",
            f"- Q8 shadow summary days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Q8 blocker forward-review days: **{payload.get('q8_group_day_count', 0)}**",
            "",
            "### Top Shadow Reasons",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Reason", "Count"],
            [[row.get("name"), row.get("count")] for row in list(payload.get("by_reason") or [])[:15]],
        )
    )
    lines.extend(["", "### Forward Blocker Review", ""])
    lines.extend(
        _md_table(
            ["Reason", "n", "obs", "Latest", "MFE", "MAE", "Missed", "Adverse", "Decision"],
            [
                [
                    row.get("reason"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_latest_return_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_favorable_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_adverse_pct') or 0.0):.4f}%",
                    f"{float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%",
                    f"{float(row.get('adverse_rate') or 0.0) * 100:.1f}%",
                    row.get("dominant_decision") or "-",
                ]
                for row in list(payload.get("q8_blocker_groups") or [])[:10]
            ],
        )
    )
    subtype_rows = list(payload.get("below_vwap_reclaim_by_subtype") or [])
    subtype_v2_rows = list(payload.get("below_vwap_reclaim_by_subtype_v2") or [])
    subtype_forward_rows = list(payload.get("below_vwap_reclaim_subtype_forward") or [])
    lines.extend(
        [
            "",
            "## Below-VWAP Reclaim Subtype Review",
            "",
            f"- Subtype count days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Subtype forward days: **{payload.get('below_vwap_reclaim_subtype_forward_day_count', 0)}**",
            "- Note: subtype forward evidence is available only after the entry-lane observation fields were added.",
            "",
            "### Subtype Counts",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Subtype", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_rows[:10]],
        )
    )
    lines.extend(["", "### Subtype V2 Counts", ""])
    lines.extend(
        _md_table(
            ["Subtype V2", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_v2_rows[:12]],
        )
    )
    lines.extend(["", "### Subtype Forward Outcomes", ""])
    lines.extend(
        _md_table(
            ["Subtype", "n", "obs", "3m", "5m", "15m", "30m", "60m", "MFE5", "MAE5", "Decision"],
            [
                [
                    row.get("name"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_return_3m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_15m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_30m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_60m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mfe_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mae_5m_pct') or 0.0):.4f}%",
                    row.get("decision") or "-",
                ]
                for row in subtype_forward_rows[:10]
            ],
        )
    )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(
        _md_table(
            ["Candidate", "Decision", "Evidence"],
            [
                [
                    row.get("candidate"),
                    row.get("decision"),
                    row.get("reason")
                    or (
                        f"n={row.get('candidate_count')}, obs={row.get('observed_count')}, "
                        f"latest={float(row.get('avg_latest_return_pct') or 0.0):.4f}%, "
                        f"missed={float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%, "
                        f"adverse={float(row.get('adverse_rate') or 0.0) * 100:.1f}%"
                    ),
                ]
                for row in list(payload.get("promotion_recommendations") or [])
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Operator Conclusion",
            "",
            "- Prior data is useful, but it must be sliced by artifact era.",
            "- Live trade PnL already shows persistent negative expectancy in stop/trend-break/low-break exits.",
            "- Q8 shadow raw sample size alone is not promotion evidence.",
            "- Promotion review requires trusted same-day forward outcomes, canonical dedupe, and evaluation_trust_gate.promotion_allowed=true.",
            "- Historical reports generated before the trust gate are legacy observation material, not policy-promotion evidence.",
            "",
        ]
    )
    return "\n".join(lines)


# --- A2: shadow blocker review ---


def render_q8_shadow_blocker_review_markdown(review: Mapping[str, Any], *, day: str) -> str:
    lines = [
        f"# Q8 Shadow Blocker Review ({day})",
        "",
        "This report is read-only evaluation output. It does not change trading behavior.",
        "",
        "## Summary",
        "",
        f"- candidate_count: **{int(review.get('candidate_count') or 0)}**",
        f"- raw_candidate_count: **{int(review.get('raw_candidate_count') or review.get('candidate_count') or 0)}**",
        f"- duplicate_count: **{int(review.get('duplicate_count') or 0)}**",
        f"- dedupe_key: `{', '.join(list(review.get('dedupe_key') or []))}`",
        f"- review_reason_count: **{int(review.get('review_reason_count') or 0)}**",
        f"- observed_review_candidate_count: **{int(review.get('observed_review_candidate_count') or 0)}**",
    ]
    gate = review.get("evaluation_trust_gate") if isinstance(review.get("evaluation_trust_gate"), Mapping) else {}
    if gate:
        lines.extend(
            [
                f"- trust_gate: `{gate.get('status') or '-'}`",
                f"- promotion_allowed: `{bool(gate.get('promotion_allowed'))}`",
                f"- trust_block_reasons: `{', '.join(list(gate.get('block_reasons') or gate.get('reasons') or [])) or '-'}`",
            ]
        )
    rail = review.get("market_regime_rail") if isinstance(review.get("market_regime_rail"), Mapping) else {}
    if rail:
        lines.append(
            f"- market_regime_rail: `{rail.get('rail_id') or 'not_available'}` "
            f"({rail.get('rail_confidence') or 'none'})"
        )
        lines.append(f"- market_regime_rationale: {rail.get('rationale') or '-'}")
        focus = [str(x) for x in list(rail.get("q8_review_focus") or []) if str(x or "").strip()]
        if focus:
            lines.append(f"- market_regime_q8_focus: `{', '.join(focus)}`")
    lines += [
        "",
        "## Blocker Outcomes",
        "",
        "| Reason | Candidates | Observed | Avg Latest | Avg MFE | Avg MAE | Missed Opp | Adverse | Decision |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    groups = review.get("groups") if isinstance(review.get("groups"), list) else []
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        lines.append(
            f"| `{group.get('reason') or '-'}` "
            f"| {int(group.get('candidate_count') or 0)} "
            f"| {int(group.get('observed_count') or 0)} "
            f"| {float(group.get('avg_latest_return_pct') or 0.0):.4f}% "
            f"| {float(group.get('avg_max_favorable_pct') or 0.0):.4f}% "
            f"| {float(group.get('avg_max_adverse_pct') or 0.0):.4f}% "
            f"| {int(group.get('missed_opportunity_count') or 0)} "
            f"| {int(group.get('adverse_count') or 0)} "
            f"| `{group.get('decision') or 'retain_under_observation'}` |"
        )
    for group in groups:
        if not isinstance(group, Mapping) or not group.get("examples"):
            continue
        lines += ["", f"## Examples: {group.get('reason')}", ""]
        for example in list(group.get("examples") or [])[:5]:
            if not isinstance(example, Mapping):
                continue
            lines.append(
                f"- `{example.get('symbol') or '-'}` role `{example.get('role') or '-'}` "
                f"rank `{example.get('rank') if example.get('rank') is not None else '-'}` "
                f"latest {float(example.get('latest_return_pct') or 0.0):.4f}% "
                f"MFE {float(example.get('max_favorable_pct') or 0.0):.4f}% "
                f"MAE {float(example.get('max_adverse_pct') or 0.0):.4f}%"
            )
    return "\n".join(lines).rstrip() + "\n"


# --- A3: trusted reaggregation ---


def _reagg_fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except Exception:
        return "-"


def _reagg_fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


def render_q8_trusted_reaggregation_markdown(
    payload: Mapping[str, Any],
    *,
    trusted_forward_min_count: Any,
    trusted_forward_min_coverage: float,
    duplicate_rate_max: float,
    promotion_candidate_min_observed: Any,
    promotion_candidate_min_days: Any,
) -> str:
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
        f"- raw candidates: **{_reagg_fmt_num(aggregate.get('candidate_count'))}**",
        f"- deduped candidates: **{_reagg_fmt_num(aggregate.get('deduped_candidate_count'))}**",
        f"- duplicate count/rate: **{_reagg_fmt_num(aggregate.get('duplicate_candidate_count'))} / {_reagg_fmt_pct(aggregate.get('duplicate_rate'))}**",
        f"- trusted forward: **{_reagg_fmt_num(aggregate.get('forward_outcome_available_count'))} / {_reagg_fmt_pct(aggregate.get('trusted_forward_coverage'))}**",
        f"- promotion allowed days: **{_reagg_fmt_num(aggregate.get('promotion_allowed_day_count'))}**",
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
                raw=_reagg_fmt_num(row.get("candidate_count")),
                deduped=_reagg_fmt_num(row.get("deduped_candidate_count")),
                dup_rate=_reagg_fmt_pct(row.get("duplicate_rate")),
                forward=_reagg_fmt_num(row.get("trusted_forward_count")),
                coverage=_reagg_fmt_pct(row.get("trusted_forward_coverage")),
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
                obs=_reagg_fmt_num(item.get("observed_count")),
                count=_reagg_fmt_num(item.get("candidate_count")),
                days=_reagg_fmt_num(item.get("observed_day_count")),
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
                    obs=_reagg_fmt_num(item.get("observed_count")),
                    count=_reagg_fmt_num(item.get("candidate_count")),
                    days=_reagg_fmt_num(item.get("observed_day_count")),
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
        f"- A day is promotion-review eligible only when trusted forward count >= {trusted_forward_min_count}, "
        f"trusted coverage >= {trusted_forward_min_coverage:.0%}, and duplicate rate <= {duplicate_rate_max:.0%}.",
        f"- Candidate-level promotion requires at least {promotion_candidate_min_observed} trusted observations "
        f"across at least {promotion_candidate_min_days} observed days.",
        "- Cross-day or stale forward observations are excluded from trusted forward counts.",
        "- Duplicate candidates are removed before forward performance is averaged.",
    ]
    return "\n".join(lines)


# --- A4: lane decision table ---


def _lane_fmt_pct(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return f"{_lane_float(value):.4f}%"


def render_q8_lane_decision_table_markdown(payload: Mapping[str, Any]) -> str:
    gate = payload.get("evaluation_trust_gate") if isinstance(payload.get("evaluation_trust_gate"), Mapping) else {}
    lines = [
        f"# Q8 Lane Decision Table - {payload.get('day')}",
        "",
        "## Summary",
        "",
        f"- payloads: {payload.get('payload_count')}",
        f"- candidates: {payload.get('candidate_count')}",
        f"- deduped candidates: {payload.get('deduped_candidate_count')}",
        f"- duplicates: {payload.get('duplicate_candidate_count')}",
        f"- dedupe_key: `{', '.join(list(payload.get('dedupe_key') or []))}`",
        f"- evaluated: {payload.get('evaluated_count')}",
        f"- forward observed: {payload.get('forward_outcome_available_count')} "
        f"({float(payload.get('forward_outcome_coverage') or 0.0):.1%})",
        f"- trust_gate: `{gate.get('status') or '-'}`",
        f"- promotion_allowed: `{bool(gate.get('promotion_allowed'))}`",
        f"- trust_block_reasons: `{', '.join(list(gate.get('block_reasons') or gate.get('reasons') or [])) or '-'}`",
        f"- would-enter: {payload.get('would_enter_count')}",
        f"- top reasons: {payload.get('reason_summary') or '-'}",
        "",
        "## Lane Verdicts",
        "",
        "| Lane | Verdict | Decision | n | obs | +5m | +15m | +30m | MFE5 | MAE5 | Rationale |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in _lane_rows(payload.get("rows")):
        lines.append(
            "| "
            + " | ".join(
                [
                    _lane_text(row.get("lane")) or "-",
                    _lane_text(row.get("verdict")) or "-",
                    _lane_text(row.get("decision")) or "-",
                    str(row.get("candidate_count") or 0),
                    str(row.get("observed_count") or 0),
                    _lane_fmt_pct(row.get("avg_return_5m_pct")),
                    _lane_fmt_pct(row.get("avg_return_15m_pct")),
                    _lane_fmt_pct(row.get("avg_return_30m_pct")),
                    _lane_fmt_pct(row.get("avg_mfe_5m_pct")),
                    _lane_fmt_pct(row.get("avg_mae_5m_pct")),
                    _lane_text(row.get("rationale")) or "-",
                ]
            )
            + " |"
        )
    lines += [
        "",
        "## Operating Interpretation",
        "",
        "- `TRUST_GATE_BLOCKED`: lane signal is visible, but Q8 evidence is not eligible for policy promotion.",
        "- `MISSED_OPPORTUNITY`: blocked candidates rose afterward. This is a review target, not direct permission to buy.",
        "- `GOOD_BLOCK`: blocked candidates underperformed after the block. Keep the gate under observation.",
        "- `DATA_INCOMPLETE`: sample or coverage is insufficient for a policy conclusion.",
        "",
        "## Current Action",
        "",
        "No new behavior patch is implied by this table unless the Q8 trust gate allows promotion review.",
        "",
    ]
    return "\n".join(lines)
