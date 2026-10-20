"""Read-only quant shadow candidate evaluation projection (P1.5 BATCH03-A, DEV-A).

Owns the deterministic forward-outcome summaries, entry-lane forward groups, no-trade scorecard and
promotion/readiness calculations moved from ``libs.reporting.quant_shadow_candidate_evaluation``. No file,
stream, environment-dependent loader or report writes live here. Every helper, constant and sibling
calculation is resolved on the injected ``facade`` module at call time, so a monkeypatch of the legacy
module keeps behaving exactly as before the move.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence


def _mean(values: Sequence[float], *, facade: Any) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(sum(clean) / float(len(clean)), 4)


def _checkpoint_value(row: Mapping[str, Any], checkpoint: str, metric: str, *, facade: Any) -> float | None:
    outcome = facade._forward_outcome(row)
    checkpoints = outcome.get("checkpoints")
    if not isinstance(checkpoints, Mapping):
        return None
    payload = checkpoints.get(checkpoint)
    if not isinstance(payload, Mapping) or facade._text(payload.get("status")) != "observed":
        return None
    value = payload.get(metric)
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _forward_outcome_summary(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    observed_rows = [row for row in rows if facade._bool(facade._forward_outcome(row).get("available"))]
    observed_days = Counter(facade._candidate_day(row) for row in observed_rows if facade._candidate_day(row))
    largest_day_count = observed_days.most_common(1)[0][1] if observed_days else 0
    horizon_counts: Dict[str, int] = {}
    horizon_day_counts: Dict[str, int] = {}
    for horizon in ("+3m", "+5m", "+15m", "+30m", "+60m", "EOD"):
        horizon_rows = [
            row
            for row in rows
            if facade._checkpoint_value(row, horizon, "return_pct") is not None
        ]
        horizon_counts[horizon] = len(horizon_rows)
        horizon_day_counts[horizon] = len(
            {facade._candidate_day(row) for row in horizon_rows if facade._candidate_day(row)}
        )
    return {
        "measurement_contract_version": "forward_horizon_coverage.v2",
        "candidate_count": len(rows),
        "observed_count": len(observed_rows),
        "observed_day_count": len(observed_days),
        "sample_concentration": (
            round(float(largest_day_count) / float(len(observed_rows)), 4)
            if observed_rows
            else 0.0
        ),
        "observed_days": [name for name, _count in observed_days.most_common(5)],
        "observed_count_by_horizon": horizon_counts,
        "observed_day_count_by_horizon": horizon_day_counts,
        **{
            f"observed_count_{horizon[1:-1]}m" if horizon.startswith("+") else "observed_count_eod": count
            for horizon, count in horizon_counts.items()
        },
        **{
            f"observed_day_count_{horizon[1:-1]}m" if horizon.startswith("+") else "observed_day_count_eod": count
            for horizon, count in horizon_day_counts.items()
        },
        "avg_return_3m_pct": facade._mean([facade._checkpoint_value(row, "+3m", "return_pct") for row in rows]),
        "avg_return_5m_pct": facade._mean([facade._checkpoint_value(row, "+5m", "return_pct") for row in rows]),
        "avg_return_15m_pct": facade._mean([facade._checkpoint_value(row, "+15m", "return_pct") for row in rows]),
        "avg_return_30m_pct": facade._mean([facade._checkpoint_value(row, "+30m", "return_pct") for row in rows]),
        "avg_return_60m_pct": facade._mean([facade._checkpoint_value(row, "+60m", "return_pct") for row in rows]),
        "avg_mfe_5m_pct": facade._mean([facade._checkpoint_value(row, "+5m", "mfe_pct") for row in rows]),
        "avg_mae_5m_pct": facade._mean([facade._checkpoint_value(row, "+5m", "mae_pct") for row in rows]),
        "coverage": (float(len(observed_rows)) / float(len(rows))) if rows else 0.0,
    }


def _top_forward_groups(groups: Mapping[str, List[Mapping[str, Any]]], *, limit: int = 10, facade: Any) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for name, rows in groups.items():
        summary = facade._forward_outcome_summary(rows)
        if int(summary.get("observed_count") or 0) <= 0:
            continue
        summary["name"] = name
        summaries.append(summary)
    summaries.sort(
        key=lambda item: (
            float(item.get("avg_return_5m_pct") or item.get("avg_return_3m_pct") or -999.0),
            int(item.get("observed_count") or 0),
        ),
        reverse=True,
    )
    return summaries[:limit]


def _entry_lane_forward_outcomes(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    by_lane: Dict[str, List[Mapping[str, Any]]] = {}
    by_subtype: Dict[str, List[Mapping[str, Any]]] = {}
    by_subtype_v2: Dict[str, List[Mapping[str, Any]]] = {}
    by_lane_subtype: Dict[str, List[Mapping[str, Any]]] = {}
    by_lane_subtype_v2: Dict[str, List[Mapping[str, Any]]] = {}
    by_time_bucket: Dict[str, List[Mapping[str, Any]]] = {}
    by_market_rail: Dict[str, List[Mapping[str, Any]]] = {}
    for row in candidates:
        observation = facade._entry_lane_observation(row)
        lane = facade._text(observation.get("primary_lane")) or "unknown"
        subtype = facade._text(observation.get("subtype")) or "unknown"
        subtype_v2 = facade._text(observation.get("subtype_v2")) or subtype
        time_bucket = facade._text(observation.get("time_bucket")) or "unknown"
        market_rail = facade._text(observation.get("market_regime_rail")) or "unknown"
        by_lane.setdefault(lane, []).append(row)
        by_subtype.setdefault(subtype, []).append(row)
        by_subtype_v2.setdefault(subtype_v2, []).append(row)
        by_lane_subtype.setdefault(f"{lane}:{subtype}", []).append(row)
        by_lane_subtype_v2.setdefault(f"{lane}:{subtype_v2}", []).append(row)
        by_time_bucket.setdefault(time_bucket, []).append(row)
        by_market_rail.setdefault(market_rail, []).append(row)
    return {
        "behavior_effect": "evaluation_only",
        "by_primary_lane": facade._top_forward_groups(by_lane, limit=10),
        "by_subtype": facade._top_forward_groups(by_subtype, limit=10),
        "by_subtype_v2": facade._top_forward_groups(by_subtype_v2, limit=10),
        "by_lane_subtype": facade._top_forward_groups(by_lane_subtype, limit=12),
        "by_lane_subtype_v2": facade._top_forward_groups(by_lane_subtype_v2, limit=12),
        "by_time_bucket": facade._top_forward_groups(by_time_bucket, limit=8),
        "by_market_regime_rail": facade._top_forward_groups(by_market_rail, limit=8),
    }


def _scorecard_return_signal(row: Mapping[str, Any], *, facade: Any) -> float | None:
    for key in ("avg_return_15m_pct", "avg_return_5m_pct", "avg_return_30m_pct", "avg_return_3m_pct"):
        value = row.get(key)
        if value not in (None, ""):
            try:
                return float(value)
            except Exception:
                continue
    return None


def _scorecard_rows(rows: Sequence[Mapping[str, Any]], *, mode: str, limit: int = 5, facade: Any) -> List[Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []
    for row in rows:
        observed = int(row.get("observed_count") or 0)
        if observed < 10:
            continue
        signal = facade._scorecard_return_signal(row)
        if signal is None:
            continue
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        try:
            mfe5_f = float(mfe5) if mfe5 not in (None, "") else None
        except Exception:
            mfe5_f = None
        try:
            mae5_f = float(mae5) if mae5 not in (None, "") else None
        except Exception:
            mae5_f = None

        if mode == "missed":
            if signal < 0.10 and not (mfe5_f is not None and mfe5_f >= 0.45 and (mae5_f is None or mae5_f > -0.80)):
                continue
            if mae5_f is not None and mae5_f <= -1.25:
                continue
        elif mode == "blocked":
            if signal > -0.05 and not (mae5_f is not None and mae5_f <= -0.75 and signal <= 0.05):
                continue
        else:
            continue

        selected.append(
            {
                "name": facade._text(row.get("name")),
                "candidate_count": int(row.get("candidate_count") or 0),
                "observed_count": observed,
                "observed_day_count": int(row.get("observed_day_count") or 0),
                "sample_concentration": row.get("sample_concentration"),
                "avg_return_5m_pct": row.get("avg_return_5m_pct"),
                "avg_return_15m_pct": row.get("avg_return_15m_pct"),
                "avg_mfe_5m_pct": row.get("avg_mfe_5m_pct"),
                "avg_mae_5m_pct": row.get("avg_mae_5m_pct"),
                "scorecard_signal_pct": round(signal, 4),
            }
        )

    selected.sort(
        key=lambda item: (
            float(item.get("scorecard_signal_pct") or 0.0),
            int(item.get("observed_count") or 0),
        ),
        reverse=(mode == "missed"),
    )
    return selected[:limit]


def _named_forward_rows(rows: Sequence[Mapping[str, Any]], names: set[str], *, facade: Any) -> List[Dict[str, Any]]:
    by_name = {str(row.get("name") or ""): row for row in rows}
    selected: List[Dict[str, Any]] = []
    for name in sorted(names):
        row = by_name.get(name)
        if not isinstance(row, Mapping):
            continue
        observed_count = int(row.get("observed_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        try:
            ret5_f = float(ret5) if ret5 not in (None, "") else None
        except Exception:
            ret5_f = None
        try:
            ret15_f = float(ret15) if ret15 not in (None, "") else None
        except Exception:
            ret15_f = None
        if observed_count < 20:
            review_state = "sample_insufficient"
        elif int(row.get("observed_day_count") or 0) < 2:
            review_state = "sample_concentrated_single_day"
        elif ret15_f is not None and ret15_f <= 0:
            review_state = "observe_only_negative_15m"
        elif ret5_f is not None and ret5_f <= 0:
            review_state = "observe_only_negative_5m"
        elif observed_count < facade.PROMOTION_CANDIDATE_MIN_OBSERVED:
            review_state = "sample_insufficient"
        else:
            review_state = "promotion_watch"
        selected.append(
            {
                "name": name,
                "candidate_count": int(row.get("candidate_count") or 0),
                "observed_count": observed_count,
                "observed_day_count": int(row.get("observed_day_count") or 0),
                "sample_concentration": row.get("sample_concentration"),
                "avg_return_5m_pct": row.get("avg_return_5m_pct"),
                "avg_return_15m_pct": row.get("avg_return_15m_pct"),
                "avg_mfe_5m_pct": row.get("avg_mfe_5m_pct"),
                "avg_mae_5m_pct": row.get("avg_mae_5m_pct"),
                "review_state": review_state,
            }
        )
    return selected


def _no_trade_scorecard(
    *,
    candidates: Sequence[Mapping[str, Any]],
    entry_lane_forward_outcomes: Mapping[str, Any],
    would_enter_count: int,
    opening_probe_would_enter: int,
    largecap_probe_would_enter: int,
    facade: Any,
) -> Dict[str, Any]:
    candidate_count = len(candidates)
    outcome_count = sum(1 for row in candidates if facade._bool(facade._forward_outcome(row).get("available")))
    coverage = float(outcome_count) / float(candidate_count) if candidate_count else 0.0
    lane_rows = (
        list(entry_lane_forward_outcomes.get("by_primary_lane") or [])
        if isinstance(entry_lane_forward_outcomes, Mapping)
        else []
    )
    lane_subtype_rows = (
        list(entry_lane_forward_outcomes.get("by_lane_subtype") or [])
        if isinstance(entry_lane_forward_outcomes, Mapping)
        else []
    )
    combined_rows = [row for row in lane_rows + lane_subtype_rows if isinstance(row, Mapping)]
    missed = facade._scorecard_rows(combined_rows, mode="missed", limit=6)
    blocked = facade._scorecard_rows(combined_rows, mode="blocked", limit=6)
    watchlist = facade._named_forward_rows(
        lane_subtype_rows,
        {
            "pullback_quality:failed_pullback",
            "vwap_reclaim:reclaim_in_progress_with_improving_volume",
        },
    )
    promotion_ready_watchlist = [
        row for row in watchlist if facade._text(row.get("review_state")) == "promotion_watch"
    ]
    if candidate_count <= 0:
        status = "no_shadow_data"
        verdict = "no shadow candidates were collected"
    elif would_enter_count > 0 or opening_probe_would_enter > 0 or largecap_probe_would_enter > 0:
        status = "trade_candidates_available"
        verdict = "shadow candidates had would-enter paths; compare against actual execution"
    elif missed and blocked:
        status = "mixed_no_trade_day"
        verdict = "major weak groups were blocked, but selected subtypes show missed-opportunity signals"
    elif missed:
        status = "possible_over_blocking"
        verdict = "no would-enter candidates, but forward outcomes show positive missed-opportunity groups"
    elif blocked:
        status = "correctly_blocked"
        verdict = "no would-enter candidates and blocked groups underperformed in forward outcomes"
    else:
        status = "inconclusive_no_trade_day"
        verdict = "no would-enter candidates; forward evidence is not decisive"
    evidence_quality = (
        "high"
        if outcome_count >= facade.TRUSTED_FORWARD_MIN_COUNT and coverage >= facade.TRUSTED_FORWARD_MIN_COVERAGE
        else "medium"
        if outcome_count >= 30
        else "low"
    )
    return {
        "behavior_effect": "evaluation_only",
        "status": status,
        "verdict": verdict,
        "candidate_count": candidate_count,
        "would_enter_count": int(would_enter_count),
        "opening_momentum_probe_would_enter_count": int(opening_probe_would_enter),
        "opening_largecap_surge_would_enter_count": int(largecap_probe_would_enter),
        "forward_outcome_available_count": int(outcome_count),
        "forward_outcome_coverage": coverage,
        "evidence_quality": evidence_quality,
        "correctly_blocked_signals": blocked,
        "missed_opportunity_candidates": missed,
        "promotion_watchlist": watchlist,
        "next_review_action": (
            "review_promotion_watchlist_for_probe_candidate"
            if promotion_ready_watchlist
            else "collect_repeatability_before_promotion_review"
            if missed or watchlist
            else "retain_current_guards_and_continue_observation"
        ),
    }


def _promotion_candidate(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    if not candidates:
        return {
            "candidate": "hold",
            "confidence": "none",
            "reason": "no_shadow_candidates",
            "counts": {},
            "promotion_scope": "none",
            "recommended_action": "hold",
        }
    cost_edge = facade._count_reason(
        candidates,
        {"cost_edge_fail", "cost_filter_failed", "not_met", "cost_floor_not_met", "cost"},
    )
    entry_guard = sum(1 for row in candidates if facade._actionable_entry_guard_block(row))
    runner_up = facade._runner_up_risk_count(candidates)
    counts = {
        "cost_edge": cost_edge,
        "runner_up": runner_up,
        "entry_guard": entry_guard,
    }
    candidate, count = max(counts.items(), key=lambda item: item[1])
    if count <= 0:
        return {
            "candidate": "hold",
            "confidence": "low",
            "reason": "no_dominant_shadow_blocker",
            "counts": counts,
            "promotion_scope": "none",
            "recommended_action": "hold",
        }
    total = max(1, len(candidates))
    share = float(count) / float(total)
    confidence = "high" if count >= 5 and share >= 0.35 else "medium" if count >= 3 else "low"
    reason_by_candidate = {
        "cost_edge": "cost_edge_or_cost_floor_is_the_largest_shadow_blocker",
        "runner_up": "runner_up_fallback_quality_is_the_largest_shadow_issue",
        "entry_guard": "entry_guard_blocks_are_the_largest_shadow_issue",
    }
    promotion_scope = "pre_entry_filter" if candidate == "cost_edge" else "candidate_selection"
    recommended_action = "manual_review_before_live_change"
    promotion_state = "candidate_review"
    behavior_effect = "recommendation_only"
    active_guard_reason = ""
    if candidate == "cost_edge" and confidence in {"high", "medium"}:
        enforcement = facade.build_entry_quant_enforcement(
            {"decision": "block_recommended", "blockers": ["cost_edge_fail"]}
        )
        if bool(enforcement.get("blocked")):
            recommended_action = "already_promoted_monitor_hard_gate"
            promotion_state = "active"
            behavior_effect = str(enforcement.get("behavior_effect") or "entry_guard_enforced")
            active_guard_reason = "quant_entry_block:cost_edge_fail"
        else:
            recommended_action = "promote_shadow_validated_guard"
            promotion_state = "recommended"
    return {
        "candidate": candidate,
        "confidence": confidence,
        "reason": reason_by_candidate.get(candidate, "dominant_shadow_blocker"),
        "counts": counts,
        "share": share,
        "behavior_effect": behavior_effect,
        "promotion_scope": promotion_scope,
        "recommended_action": recommended_action,
        "promotion_state": promotion_state,
        "active_guard_reason": active_guard_reason,
    }


def _shadow_readiness(candidates: Sequence[Mapping[str, Any]], promotion: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    candidate_count = len(candidates)
    evaluated_count = sum(1 for row in candidates if facade._bool(row.get("evaluated")))
    evaluated_ratio = float(evaluated_count) / float(candidate_count) if candidate_count else 0.0
    candidate = facade._text(promotion.get("candidate"))
    confidence = facade._text(promotion.get("confidence"))
    action = facade._text(promotion.get("recommended_action")) or "hold"
    ready = bool(
        candidate_count >= facade.TRUSTED_FORWARD_MIN_COUNT
        and evaluated_count >= facade.PROMOTION_CANDIDATE_MIN_OBSERVED
        and evaluated_ratio >= facade.TRUSTED_FORWARD_MIN_COVERAGE
        and candidate not in {"", "hold"}
        and confidence in {"medium", "high"}
    )
    if not candidate_count:
        status = "hold_no_shadow_candidates"
    elif ready:
        status = "ready"
    elif evaluated_count < facade.PROMOTION_CANDIDATE_MIN_OBSERVED:
        status = "hold_shadow_sample_insufficient"
    elif evaluated_ratio < facade.TRUSTED_FORWARD_MIN_COVERAGE:
        status = "hold_shadow_coverage_insufficient"
    else:
        status = "review_shadow_signal_weak"
    return {
        "status": status,
        "action": action if ready else "hold",
        "candidate_count": candidate_count,
        "evaluated_count": evaluated_count,
        "evaluated_ratio": evaluated_ratio,
        "sample_floor": facade.TRUSTED_FORWARD_MIN_COUNT,
        "evaluated_floor": facade.PROMOTION_CANDIDATE_MIN_OBSERVED,
        "coverage_floor": facade.TRUSTED_FORWARD_MIN_COVERAGE,
        "candidate": candidate or "hold",
        "confidence": confidence or "none",
        "promotion_scope": facade._text(promotion.get("promotion_scope")) or "none",
    }
