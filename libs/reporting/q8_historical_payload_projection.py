"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping


def build_q8_historical_review_payload(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
    facade: Any,
) -> Dict[str, Any]:
    daily_rows = facade._daily_summary_rows(reports_root, start=start, end=end)
    trade_rows = facade._extract_trade_rows(reports_root, start=start, end=end)
    return_rows = [row for row in trade_rows if isinstance(row.get("pnl_pct"), (int, float))]
    shadow = facade._aggregate_shadow_summaries(reports_root, start=start, end=end)
    pattern_by_tactic = facade._pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="strategist",
        group_key="by_tactical_strategy",
    )
    pattern_by_exit = facade._pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="monitor_exit",
        group_key="by_exit_reason",
    )
    payload: Dict[str, Any] = {
        "schema_version": "q8_historical_review.v1",
        "behavior_effect": "evaluation_only",
        "start": str(start)[:10],
        "end": str(end)[:10],
        "daily_count": len(daily_rows),
        "daily_rows": daily_rows,
        "q8_promotion_eligibility": {
            "promotion_allowed_day_count": sum(1 for row in daily_rows if bool(row.get("q8_promotion_allowed"))),
            "trusted_gate_day_count": sum(1 for row in daily_rows if facade._text(row.get("q8_trust_gate_status"))),
            "status": (
                "promotion_review_possible"
                if any(bool(row.get("q8_promotion_allowed")) for row in daily_rows)
                else "promotion_blocked_by_trust_gate_or_legacy_data"
            ),
            "rule": "Historical conclusions require daily evaluation_trust_gate.promotion_allowed=true. Legacy daily summaries without trust gate are observation-only.",
        },
        "trade_summary": {
            "trade_report_count": len(trade_rows),
            "return_sample_count": len(return_rows),
            "avg_return_pct": facade._avg([float(row["pnl_pct"]) for row in return_rows]),
            "win_rate": round(sum(1 for row in return_rows if float(row["pnl_pct"]) > 0) / len(return_rows), 4)
            if return_rows
            else 0.0,
            "truth_sources": [
                {"name": name, "count": count}
                for name, count in facade.Counter(facade._text(row.get("truth_source")) or "missing" for row in trade_rows).most_common(12)
            ],
        },
        "trade_by_tactic": pattern_by_tactic or facade._aggregate_return_rows(return_rows, "tactic"),
        "trade_by_entry_reason": facade._aggregate_return_rows(return_rows, "entry_reason"),
        "trade_by_exit_reason": pattern_by_exit or facade._aggregate_return_rows(return_rows, "exit_reason"),
        **shadow,
    }
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), facade.Mapping) else {}
    if int(eligibility.get("promotion_allowed_day_count") or 0) <= 0:
        payload["promotion_recommendations"] = [
            {
                "candidate": "all_q8_candidates",
                "decision": "retain_under_observation",
                "reason": "no historical day passed the Q8 evaluation trust gate",
            }
        ]
    else:
        payload["promotion_recommendations"] = facade._promotion_recommendations(payload)
    return payload
