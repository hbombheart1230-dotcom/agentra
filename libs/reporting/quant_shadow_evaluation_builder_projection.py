"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


def build_quant_shadow_candidate_evaluation(
    payloads: Iterable[Mapping[str, Any]],
    *,
    symbol: str = "",
    facade: Any,
) -> Dict[str, Any]:
    symbol_filter = facade._text(symbol).upper()
    payload_count = 0
    candidates: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, facade.Mapping):
            continue
        payload_count += 1
        for row in list(payload.get("candidates") or []):
            if not isinstance(row, facade.Mapping):
                continue
            row_symbol = facade._text(row.get("symbol")).upper()
            if symbol_filter and row_symbol != symbol_filter:
                continue
            enriched = dict(row)
            enriched.setdefault("_payload_generated_at", payload.get("generated_at"))
            candidates.append(enriched)
    candidates = facade.attach_forward_outcomes(candidates)
    deduped_candidates = facade._dedupe_candidates(candidates)

    roles = facade.Counter(facade._text(row.get("shadow_role")) for row in candidates)
    reasons = facade.Counter(facade._text(row.get("reason")) for row in candidates)
    tactics = facade.Counter(facade._tactic_id(row) for row in candidates)
    suitability = facade.Counter(facade._tactic_suitability_tier(row) for row in candidates)
    cost_floor = facade.Counter(facade._cost_floor_state(row) for row in candidates)
    blockers = facade.Counter(facade._text(row.get("primary_failure_axis")) for row in candidates)
    opening_probe_rows = [row for row in candidates if facade._opening_probe(row)]
    opening_probe_reasons = facade.Counter(facade._text(facade._opening_probe(row).get("reason")) for row in opening_probe_rows)
    opening_probe_symbols = facade.Counter(facade._text(row.get("symbol")) for row in opening_probe_rows if facade._opening_probe_would_enter(row))
    largecap_probe_rows = [row for row in candidates if facade._largecap_surge_probe(row)]
    largecap_probe_reasons = facade.Counter(facade._text(facade._largecap_surge_probe(row).get("reason")) for row in largecap_probe_rows)
    largecap_probe_symbols = facade.Counter(
        facade._text(row.get("symbol")) for row in largecap_probe_rows if facade._largecap_surge_would_enter(row)
    )
    would_enter = sum(1 for row in candidates if facade._bool(row.get("would_enter")))
    opening_probe_would_enter = sum(1 for row in candidates if facade._opening_probe_would_enter(row))
    largecap_probe_would_enter = sum(1 for row in candidates if facade._largecap_surge_would_enter(row))
    opening_probe_top_reason = ""
    if opening_probe_reasons:
        opening_probe_top_reason = opening_probe_reasons.most_common(1)[0][0]
    largecap_probe_top_reason = ""
    if largecap_probe_reasons:
        largecap_probe_top_reason = largecap_probe_reasons.most_common(1)[0][0]
    guard_blocked = sum(1 for row in candidates if facade._bool(row.get("guard_blocked")))
    actionable_guard_blocked = sum(1 for row in candidates if facade._actionable_entry_guard_block(row))
    evaluated = sum(1 for row in candidates if facade._bool(row.get("evaluated")))
    forward_base_available = sum(1 for row in candidates if facade._bool(facade._forward_base(row).get("available")))
    deduped_forward_outcome_available = sum(
        1 for row in deduped_candidates if facade._bool(facade._forward_outcome(row).get("available"))
    )
    entry_shape = facade._entry_shape_payload(candidates)
    below_vwap_reclaim = facade._below_vwap_reclaim_observation_payload(candidates)
    entry_lane_observation = facade._entry_lane_observation_payload(candidates)
    entry_lane_forward_outcomes = facade._entry_lane_forward_outcomes(deduped_candidates)
    promotion = facade._promotion_candidate(candidates)
    shadow_readiness = facade._shadow_readiness(candidates, promotion)
    no_trade_scorecard = facade._no_trade_scorecard(
        candidates=deduped_candidates,
        entry_lane_forward_outcomes=entry_lane_forward_outcomes,
        would_enter_count=would_enter,
        opening_probe_would_enter=opening_probe_would_enter,
        largecap_probe_would_enter=largecap_probe_would_enter,
    )
    forward_outcome_coverage = (
        (float(deduped_forward_outcome_available) / float(len(deduped_candidates)))
        if deduped_candidates
        else 0.0
    )
    trust_gate = facade._evaluation_trust_gate(
        raw_candidate_count=len(candidates),
        deduped_candidate_count=len(deduped_candidates),
        trusted_forward_count=deduped_forward_outcome_available,
        trusted_forward_coverage=forward_outcome_coverage,
        no_trade_scorecard=no_trade_scorecard,
    )

    return {
        "schema_version": "quant_shadow_candidate_evaluation.v1",
        "behavior_effect": "observation_only",
        "shadow_readiness": shadow_readiness,
        "payload_count": payload_count,
        "candidate_count": len(candidates),
        "deduped_candidate_count": len(deduped_candidates),
        "duplicate_candidate_count": max(0, len(candidates) - len(deduped_candidates)),
        "dedupe_key": list(facade.CANONICAL_DEDUPE_KEY_FIELDS),
        "evaluated_count": evaluated,
        "forward_base_available_count": forward_base_available,
        "forward_base_coverage": (float(forward_base_available) / float(len(candidates))) if candidates else 0.0,
        "forward_outcome_available_count": deduped_forward_outcome_available,
        "forward_outcome_coverage": forward_outcome_coverage,
        "would_enter_count": would_enter,
        "opening_momentum_probe_count": len(opening_probe_rows),
        "opening_momentum_probe_would_enter_count": opening_probe_would_enter,
        "opening_largecap_surge_count": len(largecap_probe_rows),
        "opening_largecap_surge_would_enter_count": largecap_probe_would_enter,
        "guard_blocked_count": guard_blocked,
        "actionable_guard_blocked_count": actionable_guard_blocked,
        "by_role": facade._top_counter(roles),
        "by_reason": facade._top_counter(reasons),
        "by_tactic_id": facade._top_counter(tactics),
        "by_tactic_suitability_tier": facade._top_counter(suitability),
        "by_cost_floor_state": facade._top_counter(cost_floor),
        "by_primary_failure_axis": facade._top_counter(blockers),
        "opening_momentum_probe": {
            "behavior_effect": "observation_only",
            "candidate_count": len(opening_probe_rows),
            "would_enter_count": opening_probe_would_enter,
            "blocked_dominant_reason": opening_probe_top_reason,
            "zero_would_enter_explanation": (
                f"no opening momentum probe passed; dominant blocker={opening_probe_top_reason or 'none'}"
                if opening_probe_would_enter == 0
                else ""
            ),
            "by_reason": facade._top_counter(opening_probe_reasons),
            "by_would_enter_symbol": facade._top_counter(opening_probe_symbols),
        },
        "opening_largecap_surge": {
            "behavior_effect": "observation_only",
            "candidate_count": len(largecap_probe_rows),
            "would_enter_count": largecap_probe_would_enter,
            "blocked_dominant_reason": largecap_probe_top_reason,
            "zero_would_enter_explanation": (
                f"no opening largecap surge probe passed; dominant blocker={largecap_probe_top_reason or 'none'}"
                if largecap_probe_would_enter == 0
                else ""
            ),
            "by_reason": facade._top_counter(largecap_probe_reasons),
            "by_would_enter_symbol": facade._top_counter(largecap_probe_symbols),
        },
        "entry_shape_diagnostics": entry_shape,
        "below_vwap_reclaim_observation": below_vwap_reclaim,
        "entry_lane_observation": entry_lane_observation,
        "entry_lane_forward_outcomes": entry_lane_forward_outcomes,
        "no_trade_scorecard": no_trade_scorecard,
        "evaluation_trust_gate": trust_gate,
        "promotion_candidate": promotion,
    }
