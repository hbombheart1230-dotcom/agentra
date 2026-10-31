"""q8_shadow_blocker_review projections (moved verbatim from q8_shadow_blocker_review).

Module globals and helpers are resolved on ``facade`` (the q8_shadow_blocker_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence


def build_q8_shadow_blocker_review(
    payloads: Iterable[Mapping[str, Any]],
    *,
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]] | None = None,
    review_reasons: Sequence[str],
    market_regime_rail: Mapping[str, Any] | None = None,
    quant_shadow_evaluation: Mapping[str, Any] | None = None,
    facade: Any,
) -> Dict[str, Any]:
    raw_rows = facade.attach_forward_outcomes(facade._candidate_rows(payloads), minute_rows_by_symbol=minute_rows_by_symbol)
    rows = facade._dedupe_rows(raw_rows)
    trusted_forward_count = 0
    for row in rows:
        outcome = row.get("shadow_forward_outcome") if isinstance(row.get("shadow_forward_outcome"), facade.Mapping) else {}
        if facade._bool(facade._checkpoint_values(outcome).get("available")):
            trusted_forward_count += 1
    trusted_forward_coverage = round(float(trusted_forward_count) / float(len(rows)), 4) if rows else 0.0
    evaluation_gate = (
        quant_shadow_evaluation.get("evaluation_trust_gate")
        if isinstance(quant_shadow_evaluation, facade.Mapping)
        and isinstance(quant_shadow_evaluation.get("evaluation_trust_gate"), facade.Mapping)
        else {}
    )
    trust_gate = (
        dict(evaluation_gate)
        if evaluation_gate
        else facade.build_q8_trust_gate(
            raw_candidate_count=len(raw_rows),
            deduped_candidate_count=len(rows),
            trusted_forward_count=trusted_forward_count,
            trusted_forward_coverage=trusted_forward_coverage,
            candidate_watchlist=[],
        )
    )
    promotion_allowed = bool(trust_gate.get("promotion_allowed"))
    review_reason_set = {str(reason) for reason in review_reasons}
    grouped: Dict[str, List[Dict[str, Any]]] = facade.defaultdict(list)
    for row in rows:
        reason = facade._text(row.get("reason"))
        if reason in review_reason_set:
            grouped[reason].append(row)
    groups = [
        facade._summarize_group(reason, grouped.get(reason, []), promotion_allowed=promotion_allowed)
        for reason in review_reasons
    ]
    observed_total = sum(int(group.get("observed_count") or 0) for group in groups)
    return {
        "schema_version": "q8_shadow_blocker_review.v1",
        "behavior_effect": "evaluation_only",
        "market_regime_rail": dict(market_regime_rail or {}),
        "raw_candidate_count": len(raw_rows),
        "deduped_candidate_count": len(rows),
        "duplicate_count": max(0, len(raw_rows) - len(rows)),
        "dedupe_key": list(facade.CANONICAL_DEDUPE_KEY_FIELDS),
        "evaluation_trust_gate": trust_gate,
        "promotion_allowed": promotion_allowed,
        "candidate_count": len(rows),
        "review_reason_count": len(groups),
        "observed_review_candidate_count": observed_total,
        "groups": groups,
    }
