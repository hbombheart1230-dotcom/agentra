"""Pure Q8 historical-review Markdown rendering (P1.5 DEV-A).

Render-only: turns the ``q8_historical_review.v1`` payload into the operator Markdown.
Writing (UTF-8 BOM, LF newlines) stays in ``libs.reporting.q8_historical_review``; tables are built
with the injected ``facade._md_table`` looked up at call time.
"""
from __future__ import annotations

from typing import Any, List, Mapping, Sequence


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> List[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(item) for item in row) + " |")
    return out


def render_q8_historical_review_markdown_impl(payload: Mapping[str, Any], *, facade: Any) -> str:
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
            facade._md_table(
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
            facade._md_table(
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
        facade._md_table(
            ["Reason", "Count"],
            [[row.get("name"), row.get("count")] for row in list(payload.get("by_reason") or [])[:15]],
        )
    )
    lines.extend(["", "### Forward Blocker Review", ""])
    lines.extend(
        facade._md_table(
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
        facade._md_table(
            ["Subtype", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_rows[:10]],
        )
    )
    lines.extend(["", "### Subtype V2 Counts", ""])
    lines.extend(
        facade._md_table(
            ["Subtype V2", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_v2_rows[:12]],
        )
    )
    lines.extend(["", "### Subtype Forward Outcomes", ""])
    lines.extend(
        facade._md_table(
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
        facade._md_table(
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
