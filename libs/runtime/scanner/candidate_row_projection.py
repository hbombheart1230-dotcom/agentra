"""Scanner per-candidate scoring row projection (additive deterministic score, risk, compatibility and component evidence).

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/scanner_node.py::scanner_node` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def score_scanner_candidate_row(candidate_meta, compatibility_bias_context, compatibility_policy, feature_map, gs, gs_signal, intrinsic_control_w, minute_rows_by_symbol, mock_by_sym, news_by_sym, news_signal_by_sym, ohlcv_by_symbol, playbook, policy, pool_meta, practical_scale, practical_w, risk_tone, scanner_bias_context, scanner_guidance, scanner_memory_bias, scanner_priority, skill_order_counts, skill_quotes, state, symbol, symbol_priors, trade_aggressiveness, w, *, facade):
    if symbol in mock_by_sym:
        row = dict(mock_by_sym[symbol])
        row.setdefault("symbol", symbol)
    else:
        base = facade._stable_unit_hash(symbol)
        # Simple deterministic defaults (placeholder)
        score = 1.0 - base  # higher is better
        confidence = max(0.0, min(1.0, 0.9 - base * 0.4))
        row = {
            "symbol": symbol,
            "score": float(score),
            "confidence": float(confidence),
            "features": {
                "unit_hash": float(base),
            },
        }

    # ---- Practical scoring model (additive, deterministic) ----
    base_score = facade._to_float(row.get("score") or 0.0)
    base_conf = facade._to_float(row.get("confidence") or 0.55)
    row["raw_score"] = float(base_score)
    row["base_score"] = float(base_score)
    candidate_rank_score, candidate_universe_score, deviation_signal, etf_deviation_bias, etf_deviation_entry_score, etf_deviation_premium_score, etf_deviation_tradeable, feature_regime, feature_row, feature_signal, ma120_gap, ma20_gap, ma60_gap, metrics, news_s, news_sig, open_orders, order_penalty, quote, quote_price, quote_price_num, return20, source_scores, trend_strength = facade.candidate_rank_inputs(candidate_meta=candidate_meta, symbol=symbol, news_by_sym=news_by_sym, news_signal_by_sym=news_signal_by_sym, skill_quotes=skill_quotes, state=state, row=row, feature_map=feature_map, skill_order_counts=skill_order_counts, facade=facade)
    adx14, adx_component, avoid_theme_symbols, base_risk, base_risk_result, cross_section_rank, cross_section_rank_component, gap_pct, intraday_strength_component, ma_alignment_component, momentum_component, momentum_raw, sentiment_component, theme_boost_component, theme_matched_symbols, trading_value_component, trend_component, trend_raw, volatility20, volatility_penalty, volume_spike20, volume_surge_component, vwap_alignment_component, vwap_distance = facade.candidate_score_components(feature_row=feature_row, candidate_meta=candidate_meta, row=row, metrics=metrics, source_scores=source_scores, return20=return20, ma20_gap=ma20_gap, ma120_gap=ma120_gap, ma60_gap=ma60_gap, trend_strength=trend_strength, feature_signal=feature_signal, pool_meta=pool_meta, symbol=symbol, news_s=news_s, gs=gs, facade=facade)
    avoid_theme_penalty, bias_result, blocker_penalty_meta, candidate_rows, gap_penalty, intrinsic_control_positive, intrinsic_control_risk, legacy_adjust, memory_bias_result, open_order_penalty, positive_score, rank_bonus, raw_minute_rows, repeat_blocker_penalty, repeat_penalty_meta, repeat_symbol_penalty, risk_penalty_score, scanner_bias_adjustment, scanner_memory_bias_adjustment, scanner_memory_bias_observation_only, scanner_memory_bias_observed_adjustment = facade.scan_feature_avoid_theme_penalty_bias_result(gap_pct=gap_pct, order_penalty=order_penalty, symbol=symbol, avoid_theme_symbols=avoid_theme_symbols, state=state, policy=policy, practical_scale=practical_scale, cross_section_rank_component=cross_section_rank_component, candidate_universe_score=candidate_universe_score, sentiment_component=sentiment_component, candidate_rank_score=candidate_rank_score, theme_boost_component=theme_boost_component, practical_w=practical_w, intraday_strength_component=intraday_strength_component, volume_surge_component=volume_surge_component, trend_component=trend_component, trading_value_component=trading_value_component, momentum_component=momentum_component, volatility_penalty=volatility_penalty, feature_signal=feature_signal, news_s=news_s, gs=gs, w=w, intrinsic_control_w=intrinsic_control_w, feature_row=feature_row, metrics=metrics, scanner_bias_context=scanner_bias_context, scanner_memory_bias=scanner_memory_bias, candidate_meta=candidate_meta, minute_rows_by_symbol=minute_rows_by_symbol, facade=facade)
    if isinstance(raw_minute_rows, list) and raw_minute_rows:
        candidate_rows = list(raw_minute_rows)
    else:
        raw_ohlcv_rows = ohlcv_by_symbol.get(facade._norm_symbol(symbol)) if isinstance(ohlcv_by_symbol.get(facade._norm_symbol(symbol)), list) else []
        if raw_ohlcv_rows:
            candidate_rows = list(raw_ohlcv_rows)
    compatibility_result = facade._compute_entry_compatibility_signal(
        symbol=symbol,
        feature_row=feature_row,
        metrics=metrics,
        candidate_rows=candidate_rows,
        current_price=quote_price_num or feature_row.get("close_last"),
        policy=compatibility_policy,
        bias_context=compatibility_bias_context,
    )
    mock_row = mock_by_sym.get(symbol) if isinstance(mock_by_sym.get(symbol), facade.Mapping) else {}
    mock_compatibility_override = mock_row.get("compatibility_override") if isinstance(mock_row.get("compatibility_override"), facade.Mapping) else {}
    if not mock_compatibility_override and isinstance(mock_row, facade.Mapping):
        top_level_override = {
            key: mock_row.get(key)
            for key in (
                "entry_compatibility_score",
                "compatibility_bias",
                "expected_monitor_block_reason",
                "dominant_block_reason",
                "dominant_block_reason_ratio",
                "bias_scale",
                "soft_penalty",
                "compatibility_score_pre_penalty",
                "compatibility_score_post_penalty",
            )
            if mock_row.get(key) not in (None, "")
        }
        if top_level_override:
            mock_compatibility_override = top_level_override
    adj_risk, compatibility_bias, compatibility_result, feature_risk, macro_chart_fit, neg_global, neg_news, pre_adjust_score_total, scanner_intrinsic_control_score_total, scanner_macro_chart_fit_bias, score_total, symbol_prior_adjustment, symbol_prior_result = facade.scan_score_adj_risk_compatibility_bias(compatibility_result=compatibility_result, mock_compatibility_override=mock_compatibility_override, feature_row=feature_row, ma_alignment_component=ma_alignment_component, trend_component=trend_component, adx_component=adx_component, momentum_component=momentum_component, volume_surge_component=volume_surge_component, vwap_alignment_component=vwap_alignment_component, cross_section_rank_component=cross_section_rank_component, volatility_penalty=volatility_penalty, gap_penalty=gap_penalty, playbook=playbook, scanner_priority=scanner_priority, risk_tone=risk_tone, trade_aggressiveness=trade_aggressiveness, state=state, symbol=symbol, symbol_priors=symbol_priors, etf_deviation_bias=etf_deviation_bias, scanner_memory_bias_adjustment=scanner_memory_bias_adjustment, repeat_blocker_penalty=repeat_blocker_penalty, repeat_symbol_penalty=repeat_symbol_penalty, rank_bonus=rank_bonus, intrinsic_control_risk=intrinsic_control_risk, legacy_adjust=legacy_adjust, base_score=base_score, intrinsic_control_positive=intrinsic_control_positive, scanner_bias_adjustment=scanner_bias_adjustment, risk_penalty_score=risk_penalty_score, positive_score=positive_score, news_s=news_s, gs=gs, w=w, feature_signal=feature_signal, feature_regime=feature_regime, open_order_penalty=open_order_penalty, practical_scale=practical_scale, base_risk=base_risk, facade=facade)
    adj_conf, adj_risk, score_breakdown = facade.scan_score_adj_conf_adj_risk(etf_deviation_tradeable=etf_deviation_tradeable, etf_deviation_premium_score=etf_deviation_premium_score, etf_deviation_entry_score=etf_deviation_entry_score, open_order_penalty=open_order_penalty, base_conf=base_conf, positive_score=positive_score, risk_penalty_score=risk_penalty_score, w=w, news_s=news_s, repeat_symbol_penalty=repeat_symbol_penalty, adj_risk=adj_risk, repeat_blocker_penalty=repeat_blocker_penalty, symbol_prior_result=symbol_prior_result, scanner_bias_adjustment=scanner_bias_adjustment, scanner_memory_bias_adjustment=scanner_memory_bias_adjustment, scanner_memory_bias_observed_adjustment=scanner_memory_bias_observed_adjustment, symbol_prior_adjustment=symbol_prior_adjustment, etf_deviation_bias=etf_deviation_bias, compatibility_bias=compatibility_bias, scanner_macro_chart_fit_bias=scanner_macro_chart_fit_bias, rank_bonus=rank_bonus, trading_value_component=trading_value_component, momentum_component=momentum_component, trend_component=trend_component, ma_alignment_component=ma_alignment_component, adx_component=adx_component, volume_surge_component=volume_surge_component, intraday_strength_component=intraday_strength_component, vwap_alignment_component=vwap_alignment_component, theme_boost_component=theme_boost_component, sentiment_component=sentiment_component, practical_scale=practical_scale, practical_w=practical_w, cross_section_rank_component=cross_section_rank_component, avoid_theme_penalty=avoid_theme_penalty, facade=facade)

    row["score"] = float(score_total)
    row["score_total"] = float(score_total)
    row["score_breakdown"] = dict(score_breakdown)
    row["bias_adjustment"] = float(scanner_bias_adjustment)
    row["bias_adjustments"] = list(bias_result.get("bias_adjustments") or [])
    row["bias_summary"] = dict(bias_result.get("bias_summary") or {})
    row["memory_bias_adjustment"] = float(scanner_memory_bias_adjustment)
    row["memory_bias_observed_adjustment"] = float(scanner_memory_bias_observed_adjustment)
    row["memory_bias_observation_only"] = bool(scanner_memory_bias_observation_only)
    row["memory_bias_source_delta"] = float(memory_bias_result.get("source_delta") or 0.0)
    row["memory_bias_symbol_delta"] = float(memory_bias_result.get("symbol_delta") or 0.0)
    row["memory_bias_adjustments"] = list(memory_bias_result.get("adjustments") or [])
    row["memory_bias_summary"] = dict(memory_bias_result.get("summary") or {})
    row["symbol_prior_adjustment"] = float(symbol_prior_adjustment)
    row["symbol_prior_reasons"] = list(symbol_prior_result.get("reasons") or [])
    row["symbol_prior_summary"] = dict(symbol_prior_result.get("summary") or {})
    row["etf_deviation_pct"] = deviation_signal.get("etf_deviation_pct")
    row["etf_deviation_source"] = str(deviation_signal.get("etf_deviation_source") or "")
    row["etf_deviation_available"] = bool(deviation_signal.get("available"))
    row["etf_deviation_entry_score"] = float(etf_deviation_entry_score)
    row["etf_deviation_premium_score"] = float(etf_deviation_premium_score)
    row["etf_deviation_bias"] = float(etf_deviation_bias)
    row["entry_compatibility_score"] = float(compatibility_result.get("entry_compatibility_score") or 0.0)
    row["compatibility_bias"] = float(compatibility_bias)
    row["compatibility_components"] = dict(compatibility_result.get("compatibility_components") or {})
    row["scanner_chart_fit_score"] = float(facade._to_float(compatibility_result.get("scanner_chart_fit_score")))
    row["scanner_chart_fit_authority"] = str(compatibility_result.get("scanner_chart_fit_authority") or "")
    row["scanner_chart_fit_components"] = dict(compatibility_result.get("scanner_chart_fit_components") or {})
    row["scanner_chart_fit_penalty"] = float(facade._to_float(compatibility_result.get("scanner_chart_fit_penalty")))
    row["scanner_macro_chart_fit_score"] = float(
        facade._to_float(macro_chart_fit.get("scanner_macro_chart_fit_score"), 0.5)
    )
    row["scanner_macro_chart_fit_bias"] = float(scanner_macro_chart_fit_bias)
    row["scanner_macro_chart_fit_authority"] = str(
        macro_chart_fit.get("scanner_macro_chart_fit_authority") or ""
    )
    row["scanner_macro_chart_fit_components"] = dict(
        macro_chart_fit.get("scanner_macro_chart_fit_components") or {}
    )
    row["scanner_macro_chart_fit_focus"] = dict(
        macro_chart_fit.get("scanner_macro_chart_fit_focus") or {}
    )
    row["expected_monitor_block_reason"] = str(compatibility_result.get("expected_monitor_block_reason") or "")
    row["dominant_block_reason"] = str(compatibility_result.get("dominant_block_reason") or "")
    row["dominant_block_reason_ratio"] = float(facade._to_float(compatibility_result.get("dominant_block_reason_ratio")))
    row["bias_scale"] = float(facade._to_float(compatibility_result.get("bias_scale")))
    row["soft_penalty"] = float(facade._to_float(compatibility_result.get("soft_penalty")))
    row["compatibility_score_pre_penalty"] = float(facade._to_float(compatibility_result.get("compatibility_score_pre_penalty")))
    row["compatibility_score_post_penalty"] = float(facade._to_float(compatibility_result.get("compatibility_score_post_penalty")))
    row["compatibility_trace"] = dict(compatibility_result)
    row["pre_adjust_score_total"] = float(pre_adjust_score_total)
    row["post_adjust_score_total"] = float(score_total)
    row["scanner_intrinsic_control_score_total"] = float(
        scanner_intrinsic_control_score_total
    )
    row["risk_score"] = float(facade._clamp(adj_risk, 0.0, 1.0))
    row["base_risk_source"] = str(base_risk_result.get("source") or "")
    row["base_risk_components"] = dict(base_risk_result.get("components") or {})
    row["base_risk_missing_inputs"] = list(base_risk_result.get("missing_inputs") or [])
    row["confidence"] = float(adj_conf)
    row["why"] = str(candidate_meta.get("why") or row.get("why") or "")
    row["asset_class_detected"] = str(candidate_meta.get("asset_class_detected") or "")
    row["detection_source"] = str(candidate_meta.get("detection_source") or "")
    row["detection_field"] = str(candidate_meta.get("detection_field") or "")
    row["excluded_by_asset_policy"] = bool(candidate_meta.get("excluded_by_asset_policy"))
    row["exclusion_reason"] = str(candidate_meta.get("exclusion_reason") or "")
    row["source_observations"] = dict(candidate_meta.get("source_observations") or {})
    row["candidate"] = {
        "source_why": str(candidate_meta.get("why") or ""),
        "sources": list(candidate_meta.get("sources") or []),
        "rank_score": float(candidate_rank_score),
        "universe_score": float(candidate_universe_score),
        "source_scores": dict(candidate_meta.get("source_scores") or {}),
        "source_observations": dict(candidate_meta.get("source_observations") or {}),
        "source_count": int(candidate_meta.get("source_count") or len(list(candidate_meta.get("sources") or []))),
        "asset_class_detected": str(candidate_meta.get("asset_class_detected") or ""),
        "detection_source": str(candidate_meta.get("detection_source") or ""),
        "detection_field": str(candidate_meta.get("detection_field") or ""),
        "excluded_by_asset_policy": bool(candidate_meta.get("excluded_by_asset_policy")),
        "exclusion_reason": str(candidate_meta.get("exclusion_reason") or ""),
    }
    row.setdefault("features", {})
    if isinstance(row.get("features"), dict):
        row["features"].update(
            {
                "skill_quote_price": quote_price_num,
                "skill_open_orders": open_orders,
                "skill_open_orders_pending_only": True,
                "quote_best_bid": facade._to_float(metrics.get("best_bid")),
                "quote_best_ask": facade._to_float(metrics.get("best_ask")),
                "quote_spread_bps": metrics.get("spread_bps"),
                "quote_payload_available": bool(metrics.get("quote_payload_available")),
                "quote_source": str(metrics.get("quote_source") or ""),
                "quote_evidence_status": str(
                    metrics.get("bid_ask_evidence_status") or ""
                ),
                "etf_deviation_pct": deviation_signal.get("etf_deviation_pct"),
                "etf_deviation_source": str(deviation_signal.get("etf_deviation_source") or ""),
                "etf_deviation_available": bool(deviation_signal.get("available")),
                "etf_deviation_entry_score": float(etf_deviation_entry_score),
                "etf_deviation_premium_score": float(etf_deviation_premium_score),
                "asset_class_detected": str(
                    deviation_signal.get("asset_class_detected")
                    or candidate_meta.get("asset_class_detected")
                    or ""
                ),
                "engine_rsi14": feature_row.get("rsi14"),
                "engine_close_last": feature_row.get("close_last"),
                "engine_ma20_gap": feature_row.get("ma20_gap"),
                "engine_ma60": feature_row.get("ma60"),
                "engine_ma120": feature_row.get("ma120"),
                "engine_adx14": feature_row.get("adx14"),
                "engine_trend_strength": feature_row.get("trend_strength"),
                "engine_atr14": feature_row.get("atr14"),
                "engine_volume_spike20": feature_row.get("volume_spike20"),
                "engine_volatility20": feature_row.get("volatility20"),
                "engine_realized_volatility": feature_row.get("realized_volatility"),
                "engine_vwap_distance": feature_row.get("vwap_distance"),
                "engine_rolling_drawdown20": feature_row.get("rolling_drawdown20"),
                "engine_sector_relative_strength": feature_row.get("sector_relative_strength"),
                "engine_cross_section_rank": feature_row.get("cross_section_rank"),
                "engine_regime": feature_row.get("regime"),
                "engine_signal_score": feature_signal,
                "intraday_change_pct": facade._to_float(metrics.get("change_pct")),
                "quote_trading_value": facade._to_float(metrics.get("trading_value")),
                "quote_volume": facade._to_float(metrics.get("volume")),
                "entry_compatibility_score": compatibility_result.get("entry_compatibility_score"),
                "compatibility_bias": compatibility_result.get("compatibility_bias"),
                "compatibility_components": dict(compatibility_result.get("compatibility_components") or {}),
                "scanner_chart_fit_score": compatibility_result.get("scanner_chart_fit_score"),
                "scanner_chart_fit_authority": compatibility_result.get("scanner_chart_fit_authority"),
                "scanner_chart_fit_components": dict(compatibility_result.get("scanner_chart_fit_components") or {}),
                "scanner_macro_chart_fit_score": macro_chart_fit.get("scanner_macro_chart_fit_score"),
                "scanner_macro_chart_fit_bias": scanner_macro_chart_fit_bias,
                "scanner_macro_chart_fit_authority": macro_chart_fit.get("scanner_macro_chart_fit_authority"),
                "scanner_macro_chart_fit_components": dict(
                    macro_chart_fit.get("scanner_macro_chart_fit_components") or {}
                ),
                "compatibility_source": compatibility_result.get("compatibility_source"),
                "compat_vwap_distance_abs": compatibility_result.get("vwap_distance_abs"),
                "compat_is_below_vwap": compatibility_result.get("is_below_vwap"),
                "compat_reclaim_proximity": compatibility_result.get("reclaim_proximity"),
                "compat_volume_ratio": compatibility_result.get("volume_ratio"),
                "compat_breakout_gap_pct": compatibility_result.get("breakout_gap_pct"),
            }
        )
    row.setdefault("components", {})
    if isinstance(row.get("components"), dict):
        row["components"].update(
            {
                "base_score": base_score,
                "base_risk": base_risk,
                "base_risk_source": str(base_risk_result.get("source") or ""),
                "base_risk_components": dict(base_risk_result.get("components") or {}),
                "base_risk_missing_inputs": list(base_risk_result.get("missing_inputs") or []),
                "base_confidence": base_conf,
                "news_sentiment": news_s,
                "global_sentiment": gs,
                "weight_news": w["weight_news"],
                "weight_global": w["weight_global"],
                "risk_news_penalty": w["risk_news_penalty"],
                "risk_global_penalty": w["risk_global_penalty"],
                "feature_signal": feature_signal,
                "feature_regime": feature_regime,
                "feature_score_weight": w["feature_score_weight"],
                "feature_risk_penalty": w["feature_risk_penalty"],
                "high_vol_risk_penalty": w["high_vol_risk_penalty"],
                "practical_positive_score": float(positive_score),
                "practical_risk_penalty_score": float(risk_penalty_score),
                "skill_open_orders": open_orders,
                "candidate_rank_score": candidate_rank_score,
                "candidate_universe_score": candidate_universe_score,
                "trading_value_component": trading_value_component,
                "momentum_component": momentum_component,
                "trend_component": trend_component,
                "ma_alignment_component": ma_alignment_component,
                "adx_component": adx_component,
                "volume_surge_component": volume_surge_component,
                "intraday_strength_component": intraday_strength_component,
                "vwap_alignment_component": vwap_alignment_component,
                "cross_section_rank_component": cross_section_rank_component,
                "theme_boost_component": theme_boost_component,
                "sentiment_component": sentiment_component,
                "volatility_penalty_component": volatility_penalty,
                "gap_penalty_component": gap_penalty,
                "open_order_penalty_component": open_order_penalty,
                "avoid_theme_penalty_component": avoid_theme_penalty,
                "repeat_symbol_penalty_component": repeat_symbol_penalty,
                "repeat_blocker_penalty_component": repeat_blocker_penalty,
                "scanner_bias_adjustment": float(scanner_bias_adjustment),
                "scanner_memory_bias_adjustment": float(scanner_memory_bias_adjustment),
                "scanner_memory_bias_source_delta": float(memory_bias_result.get("source_delta") or 0.0),
                "scanner_memory_bias_symbol_delta": float(memory_bias_result.get("symbol_delta") or 0.0),
                "scanner_memory_bias_adjustments": list(memory_bias_result.get("adjustments") or []),
                "entry_compatibility_score": compatibility_result.get("entry_compatibility_score"),
                "entry_compatibility_bias": compatibility_result.get("compatibility_bias"),
                "compatibility_components": dict(compatibility_result.get("compatibility_components") or {}),
                "scanner_chart_fit_score": compatibility_result.get("scanner_chart_fit_score"),
                "scanner_chart_fit_authority": compatibility_result.get("scanner_chart_fit_authority"),
                "scanner_chart_fit_components": dict(compatibility_result.get("scanner_chart_fit_components") or {}),
                "scanner_chart_fit_penalty": compatibility_result.get("scanner_chart_fit_penalty"),
                "scanner_macro_chart_fit_score": macro_chart_fit.get("scanner_macro_chart_fit_score"),
                "scanner_macro_chart_fit_bias": scanner_macro_chart_fit_bias,
                "scanner_macro_chart_fit_authority": macro_chart_fit.get("scanner_macro_chart_fit_authority"),
                "scanner_macro_chart_fit_components": dict(
                    macro_chart_fit.get("scanner_macro_chart_fit_components") or {}
                ),
                "scanner_macro_chart_fit_focus": dict(
                    macro_chart_fit.get("scanner_macro_chart_fit_focus") or {}
                ),
                "expected_monitor_block_reason": compatibility_result.get("expected_monitor_block_reason"),
                "dominant_block_reason": compatibility_result.get("dominant_block_reason"),
                "dominant_block_reason_ratio": compatibility_result.get("dominant_block_reason_ratio"),
                "bias_scale": compatibility_result.get("bias_scale"),
                "soft_penalty": compatibility_result.get("soft_penalty"),
                "compatibility_score_pre_penalty": compatibility_result.get("compatibility_score_pre_penalty"),
                "compatibility_score_post_penalty": compatibility_result.get("compatibility_score_post_penalty"),
                "compatibility_source": compatibility_result.get("compatibility_source"),
                "pre_adjust_score_total": float(pre_adjust_score_total),
                "post_adjust_score_total": float(score_total),
                "scanner_bias_signals": dict(bias_result.get("bias_signals") or {}),
                "recent_selection_repeat_count": int(repeat_penalty_meta.get("repeat_count") or 0),
                "recent_selection_streak_count": int(repeat_penalty_meta.get("streak_count") or 0),
                "recent_trade_same_symbol": bool(repeat_penalty_meta.get("recent_trade_same_symbol")),
                "recent_blocker_repeat_count": int(blocker_penalty_meta.get("repeat_count") or 0),
                "recent_blocker_reason": str(blocker_penalty_meta.get("reason") or ""),
                "news_sentiment_status": str(news_sig.get("status") or "fallback"),
                "news_sentiment_source": str(news_sig.get("source") or ""),
                "news_sentiment_reason": str(news_sig.get("reason") or ""),
                "global_sentiment_status": str(gs_signal.get("status") or "fallback"),
                "global_sentiment_source": str(gs_signal.get("source") or ""),
                "global_sentiment_reason": str(gs_signal.get("reason") or ""),
            }
        )

    tactic_id = str(scanner_guidance.get("tactical_strategy") or "")
    row["tactical_strategy"] = tactic_id
    row["tactical_subtype"] = str(scanner_guidance.get("tactical_subtype") or "")
    row["playbook"] = playbook
    row["tactic_suitability"] = facade.score_candidate_tactic_suitability(
        row,
        tactic_id=tactic_id,
        playbook=playbook,
    )
    return row
