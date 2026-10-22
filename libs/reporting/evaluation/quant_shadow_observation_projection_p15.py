"""Pure Q8 shadow-candidate observation-shape and diagnostic projections (P1.5 DEV-A).

Entry-shape, below-VWAP reclaim and entry-lane observation counters behind
``libs.reporting.quant_shadow_candidate_evaluation``. Diagnostic/observation-only grouping of already loaded candidate
rows: no loaders, files, clocks, trust-gate or promotion decisions. ``*_impl`` bodies resolve every helper, counter
builder and runtime classifier on the injected ``facade`` at call time, so patching a facade attribute behaves as
before the move.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Mapping, Sequence


def _entry_shape_impl(row: Mapping[str, Any], *, facade: Any) -> str:
    reason = facade._text(row.get("reason"))
    primary = facade._text(row.get("primary_failure_axis"))
    if reason in {
        "pullback_not_mature",
        "pullback_below_vwap_reclaim_not_ready",
        "pullback_structure_above_vwap_with_volume_confirmation",
    } or primary == "pullback_structure":
        return "pullback"
    if reason in {
        "below_vwap_reclaim_not_ready",
        "pullback_below_vwap_reclaim_not_ready",
    } or primary == "vwap_relationship":
        return "vwap_reclaim"
    if reason in {
        "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation",
        "breakout_above_recent_high_with_vwap_structure_confirmation",
        "breakout_not_ready",
    } or primary == "breakout_readiness":
        return "breakout"
    if reason in {"volume_confirmation_missing", "volume_insufficient"} or primary == "volume_confirmation":
        return "volume_confirmation"
    if reason == "human_chart_sanity_guard_blocked" or primary == "human_chart_sanity":
        return "human_chart_sanity"
    return "other"


def _entry_shape_payload_impl(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    shapes = Counter(facade._entry_shape(row) for row in candidates)
    pullback_blocked = sum(
        1
        for row in candidates
        if facade._entry_shape(row) in {"pullback", "vwap_reclaim"}
        and not facade._bool(row.get("would_enter"))
    )
    breakout_ready = sum(
        1
        for row in candidates
        if facade._entry_shape(row) == "breakout"
        and (
            facade._bool(row.get("would_enter"))
            or facade._text(row.get("reason"))
            in {
                "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation",
                "breakout_above_recent_high_with_vwap_structure_confirmation",
            }
        )
    )
    breakout_not_ready = sum(
        1
        for row in candidates
        if facade._entry_shape(row) == "breakout" and not facade._bool(row.get("would_enter"))
    )
    return {
        "behavior_effect": "diagnostic_only",
        "by_shape": facade._top_counter(shapes),
        "pullback_or_vwap_blocked_count": pullback_blocked,
        "breakout_ready_like_count": breakout_ready,
        "breakout_not_ready_count": breakout_not_ready,
    }


def _below_vwap_reclaim_observation_impl(row: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    payload = row.get("below_vwap_reclaim_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return facade.classify_below_vwap_reclaim_observation(row)


def _below_vwap_reclaim_observation_payload_impl(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    subtype_counter: Counter[str] = Counter()
    subtype_v2_counter: Counter[str] = Counter()
    total = 0
    for row in candidates:
        observation = facade._below_vwap_reclaim_observation(row)
        if not facade._bool(observation.get("applies")):
            continue
        total += 1
        subtype_counter[facade._text(observation.get("subtype"))] += 1
        subtype_v2_counter[facade._text(observation.get("subtype_v2"))] += 1
    return {
        "behavior_effect": "observation_only",
        "candidate_count": int(total),
        "by_subtype": facade._top_counter(subtype_counter, limit=8),
        "by_subtype_v2": facade._top_counter(subtype_v2_counter, limit=10),
    }


def _entry_lane_observation_impl(row: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    payload = row.get("entry_lane_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return facade.build_entry_lane_observation(row)


def _entry_lane_observation_payload_impl(candidates: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    lane_counter: Counter[str] = Counter()
    subtype_counter: Counter[str] = Counter()
    subtype_v2_counter: Counter[str] = Counter()
    lane_subtype_counter: Counter[str] = Counter()
    lane_subtype_v2_counter: Counter[str] = Counter()
    time_bucket_counter: Counter[str] = Counter()
    market_regime_counter: Counter[str] = Counter()
    market_rail_counter: Counter[str] = Counter()
    total = 0
    for row in candidates:
        observation = facade._entry_lane_observation(row)
        lane = facade._text(observation.get("primary_lane")) or "unknown"
        subtype = facade._text(observation.get("subtype")) or "unknown"
        subtype_v2 = facade._text(observation.get("subtype_v2")) or subtype
        time_bucket = facade._text(observation.get("time_bucket")) or "unknown"
        market_regime = facade._text(observation.get("market_regime")) or "unknown"
        market_rail = facade._text(observation.get("market_regime_rail")) or "unknown"
        total += 1
        lane_counter[lane] += 1
        subtype_counter[subtype] += 1
        subtype_v2_counter[subtype_v2] += 1
        lane_subtype_counter[f"{lane}:{subtype}"] += 1
        lane_subtype_v2_counter[f"{lane}:{subtype_v2}"] += 1
        time_bucket_counter[time_bucket] += 1
        market_regime_counter[market_regime] += 1
        market_rail_counter[market_rail] += 1
    return {
        "behavior_effect": "observation_only",
        "candidate_count": int(total),
        "by_primary_lane": facade._top_counter(lane_counter, limit=10),
        "by_subtype": facade._top_counter(subtype_counter, limit=10),
        "by_subtype_v2": facade._top_counter(subtype_v2_counter, limit=10),
        "by_lane_subtype": facade._top_counter(lane_subtype_counter, limit=12),
        "by_lane_subtype_v2": facade._top_counter(lane_subtype_v2_counter, limit=12),
        "by_time_bucket": facade._top_counter(time_bucket_counter, limit=8),
        "by_market_regime": facade._top_counter(market_regime_counter, limit=8),
        "by_market_regime_rail": facade._top_counter(market_rail_counter, limit=8),
    }
