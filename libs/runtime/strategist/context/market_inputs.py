"""Strategist market-context inputs, regime summary and macro-stress frame overlay (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _resolve_top_n_candidates_r3_impl(policy, *, facade):
    raw = (
        policy.get("candidate_k")
        if policy.get("candidate_k") is not None
        else policy.get("candidate_topk")
    )
    if raw is not None:
        return max(1, facade._to_int(raw, 10))

    env_topn = facade._env_int("TOP_N_CANDIDATES")
    if isinstance(env_topn, int) and env_topn > 0:
        return max(1, env_topn)
    # Keep strategist candidate-hint contract stable at Top-5 by default.
    return 5


def _candidates_from_state_r3_impl(state, k, *, facade):
    if isinstance(state.get("candidates"), list) and state["candidates"]:
        out = []
        for x in state["candidates"][:k]:
            if isinstance(x, dict) and "symbol" in x:
                out.append({"symbol": str(x["symbol"]), "why": str(x.get("why") or "injected")})
        return out

    # Next: universe list (tests)
    if isinstance(state.get("universe"), list) and state["universe"]:
        syms = [str(s) for s in state["universe"][:k]]
        return [{"symbol": s, "why": "universe"} for s in syms]

    # Next: direct candidate symbols injection
    if isinstance(state.get("candidate_symbols"), list) and state["candidate_symbols"]:
        syms = [str(s) for s in state["candidate_symbols"][:k]]
        return [{"symbol": s, "why": "candidate_symbols"} for s in syms]

    return []


def _extract_market_context_inputs_r3_impl(state, *, facade):
    market_ctx = state.get("market_context") if isinstance(state.get("market_context"), dict) else {}
    macro_ctx = state.get("macro_context") if isinstance(state.get("macro_context"), dict) else {}
    kiwoom_summary = state.get("kiwoom_market_summary") if isinstance(state.get("kiwoom_market_summary"), dict) else {}
    global_signal = state.get("global_sentiment_signal") if isinstance(state.get("global_sentiment_signal"), dict) else {}
    korea_indices = global_signal.get("korea_indices") if isinstance(global_signal.get("korea_indices"), dict) else {}
    korea_avg_change_pct = facade._to_float(korea_indices.get("average_change_pct"), 0.0)
    korea_breadth = (
        facade._to_float(korea_indices.get("breadth"), 0.0)
        if korea_indices.get("breadth") not in (None, "")
        else None
    )
    index_trend = facade._to_float(
        market_ctx.get("index_trend")
        if market_ctx.get("index_trend") is not None
        else (
            kiwoom_summary.get("index_trend")
            if kiwoom_summary.get("index_trend") is not None
            else korea_avg_change_pct / 5.0
            if korea_indices
            else 0.0
        ),
        0.0,
    )
    realized_vol = facade._to_float(
        market_ctx.get("realized_volatility")
        if market_ctx.get("realized_volatility") is not None
        else (
            market_ctx.get("realized_vol")
            if market_ctx.get("realized_vol") is not None
            else kiwoom_summary.get("realized_volatility")
        ),
        0.0,
    )
    breadth_raw = market_ctx.get("market_breadth")
    if breadth_raw is None:
        breadth_raw = kiwoom_summary.get("market_breadth")
    if breadth_raw is None and korea_breadth is not None:
        breadth_raw = korea_breadth
    market_breadth = facade._to_float(breadth_raw, 0.0)
    if market_breadth > 1.0:
        market_breadth = facade._clamp(market_breadth / 100.0, -1.0, 1.0)
    macro_risk = facade._to_float(
        market_ctx.get("macro_risk")
        if market_ctx.get("macro_risk") is not None
        else (
            macro_ctx.get("macro_risk")
            if macro_ctx.get("macro_risk") is not None
            else kiwoom_summary.get("macro_risk")
        ),
        0.0,
    )
    return {
        "index_trend": float(facade._clamp(index_trend, -1.0, 1.0)),
        "realized_volatility": float(max(0.0, realized_vol)),
        "market_breadth": float(facade._clamp(market_breadth, -1.0, 1.0)),
        "macro_risk": float(facade._clamp(macro_risk, 0.0, 1.0)),
    }


def _market_structure_label_r3_impl(*, state, global_score, market_context_inputs, facade):
    idx_trend = facade._to_float(market_context_inputs.get("index_trend"), 0.0)
    realized_vol = facade._to_float(market_context_inputs.get("realized_volatility"), 0.0)
    breadth = facade._to_float(market_context_inputs.get("market_breadth"), 0.0)
    breadth_01 = facade._clamp((breadth + 1.0) / 2.0, 0.0, 1.0)
    regime_obj = facade.classify_regime_v2(
        ma20_gap=idx_trend,
        volatility20=realized_vol,
        index_trend=idx_trend,
        realized_volatility=realized_vol,
        global_sentiment=global_score,
        market_breadth=breadth_01,
    )
    regime = str(regime_obj.get("regime") or "").strip().lower()
    if regime in ("trend", "range", "high_volatility"):
        return regime, dict(regime_obj.get("factors") or {})
    # fallback
    if realized_vol >= 0.040:
        return "high_volatility", {}
    if abs(idx_trend) >= 0.25 and abs(breadth) >= 0.50:
        return "trend", {}
    return "range", {}


def _compose_regime_score_r3_impl(*, global_score, news_score, market_context_inputs, facade):
    idx = facade._to_float(market_context_inputs.get("index_trend"), 0.0)
    breadth = facade._to_float(market_context_inputs.get("market_breadth"), 0.0)
    macro_risk = facade._to_float(market_context_inputs.get("macro_risk"), 0.0)
    score = (0.45 * global_score) + (0.20 * news_score) + (0.20 * idx) + (0.15 * breadth) - (0.25 * macro_risk)
    return float(facade._clamp(score, -1.0, 1.0))


def _scanner_priority_r3_impl(playbook, market_regime, *, facade):
    if playbook == "breakout":
        return ["momentum", "trend_strength", "volume_surge", "liquidity"]
    if playbook == "pullback":
        return ["trend_strength", "pullback_quality", "relative_strength", "liquidity"]
    if playbook == "reversal":
        return ["oversold_reversal", "volume_confirmation", "risk_reward", "liquidity"]
    # defensive
    base = ["liquidity", "risk_penalty", "low_volatility", "drawdown_control"]
    if market_regime == "risk_off":
        base.insert(0, "capital_preservation")
    return base


def _scanner_bias_r3_impl(*, playbook, market_regime, facade):
    if market_regime == "risk_off":
        return "large_cap"
    if playbook == "breakout":
        return "momentum"
    if playbook == "pullback":
        return "leader"
    if playbook == "reversal":
        return "value"
    return "leader"


def _build_scanner_bias_context_seed_r3_impl(*, playbook, scanner_bias, monitor_entry_policy, facade):
    policy = dict(monitor_entry_policy or {})
    seed = {
        "prefer_shallow_pullback_candidates": playbook in {"pullback", "reversal"},
        "penalize_overextended": True,
        "prefer_reclaim_candidates": bool(policy.get("require_vwap_reclaim", True)),
        "prefer_volume_confirmation": bool(policy.get("volume_ratio_min", 0.68) >= 0.68),
        "bias_strength": "low",
        "bias_source": "strategist",
    }
    style = str(scanner_bias or "").strip().lower()
    if style == "momentum":
        seed["prefer_volume_confirmation"] = True
    elif style == "value":
        seed["prefer_shallow_pullback_candidates"] = True
    elif style == "leader":
        seed["prefer_reclaim_candidates"] = True
    return facade.normalize_scanner_bias_context(seed, bias_source="strategist")[0].to_dict()


def _macro_stress_overlay_r3_impl(global_signal, *, facade):
    macro_moves = global_signal.get("macro_moves") if isinstance(global_signal.get("macro_moves"), dict) else {}
    fear_index = global_signal.get("fear_index") if isinstance(global_signal.get("fear_index"), dict) else {}
    vix_level = facade._to_float(fear_index.get("level"), facade._to_float(macro_moves.get("vix_level"), 0.0))
    vix_pressure = facade._to_float(fear_index.get("level_pressure"), facade._to_float(macro_moves.get("vix_level_pressure"), 0.0))
    dxy_pct = facade._to_float(macro_moves.get("dxy_pct"), 0.0)
    tnx_delta = facade._to_float(macro_moves.get("tnx_delta"), 0.0)

    flags: List[str] = []
    if vix_level >= 25.0 or vix_pressure >= 0.25:
        flags.append("elevated_vix")
    if dxy_pct >= 0.25:
        flags.append("dollar_strength")
    if tnx_delta >= 0.005:
        flags.append("yield_rise")

    return {
        "stress_flags": list(flags),
        "stress_count": len(flags),
        "vix_level": vix_level,
        "vix_pressure": vix_pressure,
        "dxy_pct": dxy_pct,
        "tnx_delta": tnx_delta,
        "active": len(flags) >= 2,
    }


def _apply_macro_stress_to_monitor_frame_r3_impl(
    *,
    global_signal,
    monitor_guidance,
    risk_tone,
    trade_aggressiveness,
    exit_policy,
    report_focus,
    facade,
):
    overlay = facade._macro_stress_overlay(global_signal)
    if not overlay.get("active"):
        return (
            monitor_guidance,
            risk_tone,
            trade_aggressiveness,
            dict(exit_policy or {}),
            list(report_focus or []),
            overlay,
        )

    next_guidance = str(monitor_guidance or "").strip().lower() or "defensive_exit"
    next_tone = str(risk_tone or "").strip().lower() or "normal"
    next_aggr = str(trade_aggressiveness or "").strip().lower() or "medium"
    adjusted_exit_policy = dict(exit_policy or {})
    adjusted_focus = list(report_focus or [])
    adjustments: List[str] = []

    stress_count = int(overlay.get("stress_count") or 0)
    intensity = "high" if stress_count >= 3 else "moderate"
    overlay["intensity"] = intensity

    if intensity == "high":
        if next_guidance != "defensive_exit":
            next_guidance = "defensive_exit"
            adjustments.append("macro_stress:monitor_guidance=defensive_exit")
        if next_tone != "conservative":
            next_tone = "conservative"
            adjustments.append("macro_stress:risk_tone=conservative")
    else:
        if next_guidance == "quick_take_profit":
            next_guidance = "hold_through_noise"
            adjustments.append("macro_stress:monitor_guidance=hold_through_noise")
        if next_tone == "aggressive":
            next_tone = "normal"
            adjustments.append("macro_stress:risk_tone=normal")

    target_aggr = "low" if intensity == "high" else "medium"
    if next_aggr != target_aggr:
        next_aggr = target_aggr
        adjustments.append(f"macro_stress:trade_aggressiveness={target_aggr}")

    stop_loss_pct = facade._to_float(adjusted_exit_policy.get("stop_loss_pct"), 0.0)
    take_profit_pct = facade._to_float(adjusted_exit_policy.get("take_profit_pct"), 0.0)
    trailing_stop_pct = facade._to_float(adjusted_exit_policy.get("trailing_stop_pct"), 0.0)
    if stop_loss_pct > 0.0:
        adjusted_exit_policy["stop_loss_pct"] = stop_loss_pct * (0.90 if intensity == "high" else 0.95)
    if take_profit_pct > 0.0:
        adjusted_exit_policy["take_profit_pct"] = take_profit_pct * (0.88 if intensity == "high" else 0.94)
    if trailing_stop_pct > 0.0:
        adjusted_exit_policy["trailing_stop_pct"] = max(trailing_stop_pct, facade._to_float(adjusted_exit_policy.get("stop_loss_pct"), 0.0) * 0.75)
    adjustments.append("macro_stress:tightened_exit_policy")

    for item in ("macro_stress", "exit_quality", "guard_blocks"):
        if item not in adjusted_focus:
            adjusted_focus.append(item)

    overlay["adjustments"] = list(adjustments)
    overlay["reason"] = (
        f"vix={facade._to_float(overlay.get('vix_level'), 0.0):.2f} "
        f"pressure={facade._to_float(overlay.get('vix_pressure'), 0.0):.3f} "
        f"dxy_pct={facade._to_float(overlay.get('dxy_pct'), 0.0):.2f} "
        f"tnx_delta={facade._to_float(overlay.get('tnx_delta'), 0.0):.4f}"
    )
    return next_guidance, next_tone, next_aggr, adjusted_exit_policy, adjusted_focus[:8], overlay


def _build_market_regime_summary_r3_impl(
    *,
    market_regime,
    market_sentiment,
    market_structure,
    playbook,
    global_signal,
    facade,
):
    fear_index = dict(global_signal.get("fear_index") or {}) if isinstance(global_signal.get("fear_index"), dict) else {}
    vix_level = facade._to_float(fear_index.get("level"), 0.0)
    return (
        f"{str(market_regime or 'neutral')} regime / {str(market_sentiment or 'neutral')} sentiment / "
        f"{str(market_structure or 'mixed')} structure with playbook {str(playbook or 'defensive')}. "
        f"VIX={vix_level:.2f}."
    )
