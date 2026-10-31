"""q8_shadow_blocker_review projections (moved verbatim from q8_shadow_blocker_review).

Module globals and helpers are resolved on ``facade`` (the q8_shadow_blocker_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _summarize_group(
    reason: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    promotion_allowed: bool,
    facade: Any,
) -> Dict[str, Any]:
    observed_rows: List[Dict[str, Any]] = []
    for row in rows:
        outcome = row.get("shadow_forward_outcome") if isinstance(row.get("shadow_forward_outcome"), facade.Mapping) else {}
        values = facade._checkpoint_values(outcome)
        if values.get("available"):
            observed_rows.append({**dict(row), "_q8_forward": values})
    latest_returns = [
        float(row["_q8_forward"]["latest_return_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("latest_return_pct") is not None
    ]
    mfes = [
        float(row["_q8_forward"]["max_favorable_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("max_favorable_pct") is not None
    ]
    maes = [
        float(row["_q8_forward"]["max_adverse_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("max_adverse_pct") is not None
    ]
    positive_count = sum(1 for value in latest_returns if value > 0)
    missed_opportunity_count = sum(1 for value in mfes if value >= 1.0)
    adverse_count = sum(1 for value in maes if value <= -0.5)
    examples = sorted(
        observed_rows,
        key=lambda row: float(row["_q8_forward"].get("max_favorable_pct") or 0.0),
        reverse=True,
    )[:5]
    raw_decision = facade._decision_for_row(rows[0]) if rows else "retain_under_observation"
    decision = raw_decision if promotion_allowed else "retain_under_observation"
    return {
        "reason": reason,
        "candidate_count": len(rows),
        "observed_count": len(observed_rows),
        "coverage": round(float(len(observed_rows)) / float(len(rows)), 4) if rows else 0.0,
        "avg_latest_return_pct": facade._avg(latest_returns),
        "avg_max_favorable_pct": facade._avg(mfes),
        "avg_max_adverse_pct": facade._avg(maes),
        "positive_latest_count": positive_count,
        "positive_latest_rate": round(float(positive_count) / float(len(latest_returns)), 4) if latest_returns else 0.0,
        "missed_opportunity_count": missed_opportunity_count,
        "missed_opportunity_rate": round(float(missed_opportunity_count) / float(len(mfes)), 4) if mfes else 0.0,
        "adverse_count": adverse_count,
        "adverse_rate": round(float(adverse_count) / float(len(maes)), 4) if maes else 0.0,
        "raw_decision": raw_decision,
        "decision": decision,
        "decision_blocked_by_trust_gate": bool(raw_decision != decision),
        "examples": [
            {
                "symbol": facade._text(row.get("symbol")),
                "role": facade._text(row.get("shadow_role")),
                "rank": row.get("rank"),
                "tactic_id": facade._text(row.get("quant_tactic_id")),
                "latest_return_pct": row["_q8_forward"].get("latest_return_pct"),
                "max_favorable_pct": row["_q8_forward"].get("max_favorable_pct"),
                "max_adverse_pct": row["_q8_forward"].get("max_adverse_pct"),
            }
            for row in examples
        ],
    }
