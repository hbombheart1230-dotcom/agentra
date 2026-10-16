"""Scanner monitor-compatibility policy input, frame and entry-compatibility signal (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_scanner_monitor_policy_input_r3_impl(*, state, commander_context, monitor_policy, facade):
    if isinstance(commander_context.get("applied_policy"), dict):
        return dict(commander_context.get("applied_policy") or {})
    if isinstance(state.get("commander_applied_policy"), dict):
        return dict(state.get("commander_applied_policy") or {})
    if isinstance(monitor_policy.get("entry_policy"), dict):
        return dict(monitor_policy.get("entry_policy") or {})
    if isinstance(state.get("monitor_entry_policy"), dict):
        return dict(state.get("monitor_entry_policy") or {})
    return {}


def _build_scanner_monitor_frame_r3_impl(
    *,
    playbook,
    monitor_guidance,
    risk_tone,
    trade_aggressiveness,
    facade,
):
    out: Dict[str, Any] = {}
    if str(playbook or "").strip():
        out["playbook"] = str(playbook).strip().lower()
    if str(monitor_guidance or "").strip():
        out["monitor_guidance"] = str(monitor_guidance).strip().lower()
    if str(risk_tone or "").strip():
        out["risk_tone"] = str(risk_tone).strip().lower()
    if str(trade_aggressiveness or "").strip():
        out["trade_aggressiveness"] = str(trade_aggressiveness).strip().lower()
    return out


def _compute_entry_compatibility_signal_r3_impl(
    *,
    symbol,
    feature_row,
    metrics,
    candidate_rows,
    current_price,
    policy,
    bias_context,
    facade,
):
    if policy in (None, {}, ""):
        return {
            "entry_compatibility_score": 0.5,
            "compatibility_bias": 0.0,
            "dominant_block_reason": "mixed",
            "dominant_block_reason_ratio": 0.0,
            "bias_scale": 0.10,
            "soft_penalty": 0.0,
            "compatibility_score_pre_penalty": 0.5,
            "compatibility_score_post_penalty": 0.5,
            "compatibility_components": {
                "vwap_proximity_score": 0.5,
                "volume_readiness_score": 0.5,
                "breakout_readiness_score": 0.5,
                "reclaim_proximity": 0.5,
            },
            "scanner_chart_fit_score": 0.5,
            "scanner_chart_fit_authority": "disabled_no_policy",
            "scanner_chart_fit_components": {},
            "scanner_chart_fit_penalty": 0.0,
            "expected_monitor_block_reason": "",
            "compatibility_source": "disabled",
            "triggered_path": "",
            "paths_passed": [],
            "vwap_distance_abs": None,
            "is_below_vwap": False,
            "reclaim_proximity": 0.5,
            "volume_ratio": None,
            "breakout_gap_pct": None,
        }
    result = facade.evaluate_intraday_entry_signal(
        candidate_rows,
        current_price=current_price,
        features=feature_row,
        policy=policy,
        frame=None,
    )
    thresholds = dict(result.get("threshold_margins") or {})
    condition_scores = dict(result.get("condition_scores") or {})
    metrics_map = dict(result.get("metrics") or {})

    vwap_distance = metrics_map.get("extended_from_vwap_pct")
    if vwap_distance in (None, ""):
        vwap_distance = metrics_map.get("vwap_distance")
    volume_ratio = metrics_map.get("volume_ratio")
    breakout_gap_threshold = thresholds.get("breakout_gap_pct") if isinstance(thresholds.get("breakout_gap_pct"), dict) else {}
    extended_threshold = thresholds.get("extended_from_vwap_pct") if isinstance(thresholds.get("extended_from_vwap_pct"), dict) else {}
    volume_threshold = thresholds.get("volume_ratio") if isinstance(thresholds.get("volume_ratio"), dict) else {}
    breakout_gap_pct = breakout_gap_threshold.get("actual")
    min_extended = extended_threshold.get("min")
    max_extended = extended_threshold.get("max")
    volume_min = volume_threshold.get("min")
    below_vwap = bool(vwap_distance is not None and facade._to_float(vwap_distance) < 0.0)

    source = "minute_eval"
    if not bool(result.get("evaluated")):
        source = "feature_heuristic"
        vwap_distance = feature_row.get("vwap_distance")
        volume_ratio = feature_row.get("volume_ratio")
        if volume_ratio in (None, ""):
            volume_ratio = feature_row.get("volume_spike20")
        breakout_gap_pct = None
        min_extended = policy.get("min_extended_from_vwap_pct") if hasattr(policy, "get") else None
        max_extended = policy.get("max_extended_from_vwap_pct") if hasattr(policy, "get") else None
        volume_min = policy.get("volume_ratio_min") if hasattr(policy, "get") else None
        below_vwap = bool(vwap_distance is not None and facade._to_float(vwap_distance) < 0.0)
    elif max_extended in (None, "") and hasattr(policy, "get"):
        max_extended = policy.get("max_extended_from_vwap_pct")

    vwap_distance_num = float(facade._to_float(vwap_distance)) if vwap_distance not in (None, "") else None
    vwap_distance_abs = abs(vwap_distance_num) if vwap_distance_num is not None else None
    max_extended_num = float(facade._to_float(max_extended)) if max_extended not in (None, "") else None
    reclaim_proximity = facade._calc_reclaim_proximity(
        actual=vwap_distance_num,
        minimum=float(min_extended) if min_extended not in (None, "") else None,
    )
    vwap_proximity_score = (
        facade._clamp(1.0 - abs(min(0.0, float(vwap_distance_num))) / 0.10, 0.0, 1.0)
        if vwap_distance_num is not None
        else 0.5
    )
    overextension_score = 1.0
    if vwap_distance_num is not None and max_extended_num is not None and max_extended_num > 0.0:
        overextension_score = facade._clamp(
            1.0 - max(0.0, vwap_distance_num - max_extended_num) / max(0.02, max_extended_num),
            0.0,
            1.0,
        )
        vwap_proximity_score = min(vwap_proximity_score, overextension_score)
    volume_readiness_score = 0.5
    if volume_ratio not in (None, ""):
        volume_floor = max(facade._to_float(volume_min), 1e-6)
        volume_readiness_score = facade._clamp(facade._to_float(volume_ratio) / volume_floor, 0.0, 1.0)
    breakout_readiness_score = 0.5
    if breakout_gap_pct not in (None, ""):
        breakout_readiness_score = facade._clamp(1.0 - abs(min(0.0, facade._to_float(breakout_gap_pct))) / 0.03, 0.0, 1.0)

    base_compatibility_score = facade._clamp(
        (0.45 * vwap_proximity_score)
        + (0.35 * volume_readiness_score)
        + (0.20 * breakout_readiness_score),
        0.0,
        1.0,
    )
    chart_fit = facade._scanner_chart_fit_from_entry_result(result)
    scanner_chart_fit_score = float(base_compatibility_score)
    if bool(chart_fit.get("available")):
        chart_context_score = facade._clamp(facade._to_float(chart_fit.get("chart_context_score"), 0.5), 0.0, 1.0)
        scanner_chart_fit_score = facade._clamp(
            (0.75 * base_compatibility_score)
            + (0.25 * chart_context_score)
            - facade._to_float(chart_fit.get("soft_penalty")),
            0.0,
            1.0,
        )
    entry_compatibility_score = scanner_chart_fit_score
    compatibility_score_pre_penalty = float(entry_compatibility_score)
    soft_penalty = 0.0
    volume_ratio_num = facade._to_float(volume_ratio) if volume_ratio not in (None, "") else None
    volume_min_num = max(facade._to_float(volume_min), 1e-6) if volume_min not in (None, "") else None
    if volume_ratio_num is not None:
        if volume_ratio_num <= 0.0:
            soft_penalty += 0.08
        if volume_min_num is not None and volume_ratio_num < (0.33 * volume_min_num):
            soft_penalty += 0.05
    if vwap_distance_num is not None and vwap_distance_num < -0.07:
        soft_penalty += 0.03
    if (
        vwap_distance_num is not None
        and max_extended_num is not None
        and max_extended_num > 0.0
        and vwap_distance_num > max_extended_num
    ):
        soft_penalty += min(0.12, 0.04 + (vwap_distance_num - max_extended_num))
    if str(result.get("reason") or "").strip() == "too_extended_from_vwap":
        soft_penalty += 0.04
    compatibility_score_post_penalty = max(0.0, compatibility_score_pre_penalty - soft_penalty)
    if str(result.get("reason") or "").strip() == "too_extended_from_vwap":
        compatibility_score_post_penalty = min(compatibility_score_post_penalty, 0.35)
    dominant_block_reason = str((bias_context or {}).get("dominant_block_reason") or "mixed")
    dominant_block_reason_ratio = float(facade._to_float((bias_context or {}).get("dominant_block_reason_ratio")))
    bias_scale = float(facade._to_float((bias_context or {}).get("bias_scale") or 0.10))
    compatibility_bias = bias_scale * (compatibility_score_post_penalty - 0.5)
    expected_monitor_block_reason = ""
    if not bool(result.get("triggered")):
        expected_monitor_block_reason = str(result.get("reason") or "").strip()
    elif below_vwap:
        expected_monitor_block_reason = "below_vwap_reclaim_not_ready"

    return {
        "entry_compatibility_score": float(compatibility_score_post_penalty),
        "compatibility_bias": float(compatibility_bias),
        "dominant_block_reason": dominant_block_reason,
        "dominant_block_reason_ratio": float(dominant_block_reason_ratio),
        "bias_scale": float(bias_scale),
        "soft_penalty": float(soft_penalty),
        "compatibility_score_pre_penalty": float(compatibility_score_pre_penalty),
        "compatibility_score_post_penalty": float(compatibility_score_post_penalty),
        "compatibility_components": {
            "vwap_proximity_score": float(vwap_proximity_score),
            "volume_readiness_score": float(volume_readiness_score),
            "breakout_readiness_score": float(breakout_readiness_score),
            "reclaim_proximity": float(reclaim_proximity),
            "base_compatibility_score": float(base_compatibility_score),
            "scanner_chart_fit_score": float(scanner_chart_fit_score),
            "scanner_chart_fit_available": bool(chart_fit.get("available")),
        },
        "scanner_chart_fit_score": float(scanner_chart_fit_score),
        "scanner_chart_fit_authority": "soft_rank_bias_only",
        "scanner_chart_fit_components": dict(chart_fit.get("components") or {}),
        "scanner_chart_fit_penalty": float(facade._to_float(chart_fit.get("soft_penalty"))),
        "expected_monitor_block_reason": expected_monitor_block_reason,
        "compatibility_source": source,
        "triggered_path": str(result.get("entry_condition_path") or ""),
        "paths_passed": list(result.get("entry_condition_paths_passed") or []),
        "vwap_distance_abs": float(vwap_distance_abs) if vwap_distance_abs is not None else None,
        "is_below_vwap": bool(below_vwap),
        "reclaim_proximity": float(reclaim_proximity),
        "volume_ratio": float(facade._to_float(volume_ratio)) if volume_ratio not in (None, "") else None,
        "breakout_gap_pct": float(facade._to_float(breakout_gap_pct)) if breakout_gap_pct not in (None, "") else None,
    }


def _extract_monitor_entry_block_reason_r3_impl(payload, *, facade):
    if not isinstance(payload, dict):
        return ""
    cascade = payload.get("entry_candidate_cascade") if isinstance(payload.get("entry_candidate_cascade"), dict) else {}
    candidates = [
        cascade.get("reason"),
        cascade.get("top_pick_reason"),
        payload.get("entry_reason"),
        payload.get("entry_exit_reason"),
        payload.get("primary_reason_code"),
    ]
    for value in candidates:
        reason = str(value or "").strip()
        if reason in facade._ENTRY_COMPATIBILITY_BLOCK_REASONS:
            return reason
    return ""


def _merge_mock_compatibility_override_r3_impl(base, *, override, facade):
    if not isinstance(override, facade.Mapping):
        return dict(base or {})
    merged = dict(base or {})
    for key in (
        "entry_compatibility_score",
        "compatibility_bias",
        "dominant_block_reason_ratio",
        "bias_scale",
        "soft_penalty",
        "compatibility_score_pre_penalty",
        "compatibility_score_post_penalty",
        "vwap_distance_abs",
        "reclaim_proximity",
        "volume_ratio",
        "breakout_gap_pct",
    ):
        if override.get(key) not in (None, ""):
            merged[key] = float(facade._to_float(override.get(key)))
    for key in (
        "expected_monitor_block_reason",
        "dominant_block_reason",
        "compatibility_source",
        "triggered_path",
    ):
        if override.get(key) not in (None, ""):
            merged[key] = str(override.get(key) or "")
    if override.get("is_below_vwap") is not None:
        merged["is_below_vwap"] = bool(override.get("is_below_vwap"))
    if isinstance(override.get("paths_passed"), list):
        merged["paths_passed"] = list(override.get("paths_passed") or [])
    if isinstance(override.get("compatibility_components"), facade.Mapping):
        merged["compatibility_components"] = dict(override.get("compatibility_components") or {})
    return merged
