"""Strategist operator summary and deterministic strategy scoring (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _operator_summary_for_llm_r3_impl(summary, *, facade):
    src = summary if isinstance(summary, dict) else {}
    if not src:
        return {}
    metrics = src.get("metrics") if isinstance(src.get("metrics"), dict) else {}
    operator_view = src.get("operator_view") if isinstance(src.get("operator_view"), dict) else {}
    out: Dict[str, Any] = {
        "schema_version": str(src.get("schema_version") or ""),
        "available": bool(src.get("available")),
        "status": str(src.get("status") or ""),
        "key": str(src.get("key") or ""),
        "artifact_path": str(src.get("artifact_path") or ""),
        "metrics": facade._compact_scalar_mapping_for_llm(
            metrics,
            allowed_keys=[
                "trade_count",
                "closed_trade_count",
                "win_rate",
                "avg_return_pct",
                "avg_net_return_pct",
                "total_return_pct",
                "total_net_return_pct",
                "profit_factor",
                "avg_hold_duration_sec",
            ],
            max_text_len=80,
        ),
        "operator_view": {
            "conclusion": facade._clip_text_for_llm(operator_view.get("conclusion"), max_len=180),
            "review_points": [
                facade._clip_text_for_llm(x, max_len=120)
                for x in list(operator_view.get("review_points") or [])[:4]
                if str(x or "").strip()
            ],
        },
    }
    for key in ("key_patterns", "repeat_patterns", "risk_notes", "cost_notes"):
        values = src.get(key)
        if isinstance(values, list):
            out[key] = [facade._clip_text_for_llm(x, max_len=120) for x in values[:4] if str(x or "").strip()]

    strategist_eval = src.get("strategist_llm_evaluation") if isinstance(src.get("strategist_llm_evaluation"), dict) else {}
    shadow_eval = (
        src.get("quant_shadow_candidate_evaluation")
        if isinstance(src.get("quant_shadow_candidate_evaluation"), dict)
        else {}
    )
    promotion = (
        shadow_eval.get("promotion_candidate")
        if isinstance(shadow_eval.get("promotion_candidate"), dict)
        else {}
    )
    readiness = (
        shadow_eval.get("shadow_readiness")
        if isinstance(shadow_eval.get("shadow_readiness"), dict)
        else {}
    )
    entry_shape = (
        shadow_eval.get("entry_shape_diagnostics")
        if isinstance(shadow_eval.get("entry_shape_diagnostics"), dict)
        else {}
    )
    lane_guidance: Dict[str, Any] = {}
    if strategist_eval:
        lane_guidance.update(
            facade._compact_scalar_mapping_for_llm(
                strategist_eval,
                allowed_keys=[
                    "lane_selection_quality",
                    "selected_primary_tactic",
                    "selected_primary_lane",
                    "overused_lane_or_tactic",
                    "underused_shadow_lane",
                ],
                max_text_len=100,
            )
        )
    if readiness:
        lane_guidance["shadow_readiness"] = facade._compact_scalar_mapping_for_llm(
            readiness,
            allowed_keys=["status", "action", "candidate", "confidence", "promotion_scope"],
            max_text_len=100,
        )
    if promotion:
        lane_guidance["promotion_candidate"] = facade._compact_scalar_mapping_for_llm(
            promotion,
            allowed_keys=["candidate", "confidence", "recommended_action", "reason"],
            max_text_len=100,
        )
        counts = promotion.get("counts") if isinstance(promotion.get("counts"), dict) else {}
        if counts:
            lane_guidance["promotion_counts"] = facade._compact_scalar_mapping_for_llm(
                counts,
                allowed_keys=["cost_edge", "runner_up", "entry_guard"],
                max_text_len=40,
            )
    if entry_shape:
        lane_guidance["entry_shape_diagnostics"] = facade._compact_scalar_mapping_for_llm(
            entry_shape,
            allowed_keys=[
                "pullback_or_vwap_blocked_count",
                "breakout_ready_like_count",
                "breakout_not_ready_count",
            ],
            max_text_len=40,
        )
    if lane_guidance:
        selected = str(lane_guidance.get("selected_primary_tactic") or "").strip()
        overused = str(lane_guidance.get("overused_lane_or_tactic") or "").strip()
        underused = str(lane_guidance.get("underused_shadow_lane") or "").strip()
        pullback_blocked = facade._to_int(
            facade._nested_mapping_value(lane_guidance, "entry_shape_diagnostics", "pullback_or_vwap_blocked_count"),
            0,
        )
        breakout_ready = facade._to_int(
            facade._nested_mapping_value(lane_guidance, "entry_shape_diagnostics", "breakout_ready_like_count"),
            0,
        )
        directives: List[str] = []
        if selected == "vwap_reclaim_pullback" and overused == "vwap_reclaim_pullback":
            directives.append("downweight_repeated_vwap_reclaim_pullback_unless_cost_volume_and_maturity_are_ready")
        if underused == "breakout" and breakout_ready > 0:
            directives.append("explicitly_score_breakout_or_volume_breakout_against_pullback_before_selecting_tactic")
        if pullback_blocked >= 50 and breakout_ready > 0:
            directives.append("do_not_default_to_late_pullback_when_shadow_breakout_ready_like_candidates_exist")
        if directives:
            lane_guidance["strategist_directives"] = directives[:4]
        out["tactic_lane_guidance"] = lane_guidance
    return {k: v for k, v in out.items() if v not in ({}, [], "", None)}


def _deterministic_strategy_scores_r3_impl(
    *,
    playbook,
    market_regime,
    market_sentiment,
    market_structure,
    market_context_inputs,
    facade,
):
    regime = str(market_regime or "").strip().lower()
    sentiment = str(market_sentiment or "").strip().lower()
    structure = str(market_structure or "").strip().lower()
    index_trend = facade._to_float(market_context_inputs.get("index_trend"), 0.0)
    breadth = facade._to_float(market_context_inputs.get("market_breadth"), 0.0)
    realized_vol = facade._to_float(market_context_inputs.get("realized_volatility"), 0.0)
    macro_risk = facade._to_float(market_context_inputs.get("macro_risk"), 0.0)

    risk_on = 1.0 if regime == "risk_on" else 0.5 if regime == "neutral" else 0.0
    bullish = 1.0 if sentiment == "bullish" else 0.5 if sentiment == "neutral" else 0.0
    trend = facade._clamp(abs(index_trend), 0.0, 1.0)
    positive_tape = facade._clamp((breadth + 1.0) / 2.0, 0.0, 1.0)
    vol_penalty = facade._clamp(realized_vol / 0.08, 0.0, 1.0)
    macro_penalty = facade._clamp(macro_risk, 0.0, 1.0)
    trend_structure = 1.0 if structure.startswith("trend") else 0.35 if structure.startswith("range") else 0.0
    range_structure = 1.0 if structure.startswith("range") else 0.35
    high_vol = 1.0 if structure.startswith("high_volatility") else vol_penalty

    scores = {
        "opening_gap_momentum": (0.30 * risk_on) + (0.30 * bullish) + (0.25 * max(index_trend, 0.0)) + (0.15 * positive_tape),
        "opening_range_breakout": (0.25 * risk_on) + (0.25 * bullish) + (0.30 * trend_structure) + (0.20 * positive_tape),
        "vwap_reclaim_pullback": (0.20 * risk_on) + (0.20 * bullish) + (0.30 * trend_structure) + (0.20 * positive_tape) + (0.10 * (1.0 - vol_penalty)),
        "volume_breakout": (0.25 * risk_on) + (0.25 * bullish) + (0.25 * trend) + (0.15 * positive_tape) + (0.10 * (1.0 - macro_penalty)),
        "reversal_reclaim": (0.25 * range_structure) + (0.25 * (1.0 - positive_tape)) + (0.20 * risk_on) + (0.15 * (1.0 - high_vol)) + (0.15 * bullish),
        "cost_aware_scalp": (0.25 * risk_on) + (0.25 * bullish) + (0.20 * (1.0 - macro_penalty)) + (0.15 * trend_structure) + (0.15 * positive_tape),
        "defensive_observe": (0.35 * (1.0 - risk_on)) + (0.25 * high_vol) + (0.25 * macro_penalty) + (0.15 * (1.0 - bullish)),
    }
    selected = facade._normalize_tactical_strategy("", playbook=playbook)
    if selected in scores:
        scores[selected] = max(float(scores[selected]), 0.55)
    return {key: round(facade._unit_score(value), 4) for key, value in scores.items()}


def _normalize_strategy_scores_r3_impl(
    raw,
    *,
    playbook,
    market_regime,
    market_sentiment,
    market_structure,
    market_context_inputs,
    facade,
):
    scores = facade._deterministic_strategy_scores(
        playbook=playbook,
        market_regime=market_regime,
        market_sentiment=market_sentiment,
        market_structure=market_structure,
        market_context_inputs=market_context_inputs,
    )
    if isinstance(raw, dict):
        for raw_key, raw_value in raw.items():
            key = facade.canonical_tactic_key(raw_key)
            if key in facade._TACTICAL_STRATEGIES:
                scores[key] = round(facade._unit_score(raw_value, scores.get(key, 0.0)), 4)
    return scores
