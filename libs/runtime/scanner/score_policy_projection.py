"""Scanner score-component projection (memory/compatibility/macro/tactical; same rounding and clamps).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/scanner_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def scan_score_adj_risk_compatibility_bias(compatibility_result, mock_compatibility_override, feature_row, ma_alignment_component, trend_component, adx_component, momentum_component, volume_surge_component, vwap_alignment_component, cross_section_rank_component, volatility_penalty, gap_penalty, playbook, scanner_priority, risk_tone, trade_aggressiveness, state, symbol, symbol_priors, etf_deviation_bias, scanner_memory_bias_adjustment, repeat_blocker_penalty, repeat_symbol_penalty, rank_bonus, intrinsic_control_risk, legacy_adjust, base_score, intrinsic_control_positive, scanner_bias_adjustment, risk_penalty_score, positive_score, news_s, gs, w, feature_signal, feature_regime, open_order_penalty, practical_scale, base_risk, *, facade):
    if True:
        compatibility_result = facade._merge_mock_compatibility_override(
            compatibility_result,
            override=mock_compatibility_override,
        )
        compatibility_bias = float(compatibility_result.get("compatibility_bias") or 0.0)
        macro_chart_fit = facade._compute_scanner_macro_chart_fit(
            feature_row=feature_row,
            ma_alignment_component=ma_alignment_component,
            trend_component=trend_component,
            adx_component=adx_component,
            momentum_component=momentum_component,
            volume_surge_component=volume_surge_component,
            vwap_alignment_component=vwap_alignment_component,
            cross_section_rank_component=cross_section_rank_component,
            volatility_penalty=volatility_penalty,
            gap_penalty=gap_penalty,
            playbook=playbook,
            scanner_priority=scanner_priority,
            risk_tone=risk_tone,
            trade_aggressiveness=trade_aggressiveness,
        )
        scanner_macro_chart_fit_bias = float(
            macro_chart_fit.get("scanner_macro_chart_fit_bias") or 0.0
        )
        symbol_prior_result = facade._compute_symbol_prior_adjustment(
            symbol_model=dict(symbol_priors.get(symbol) or {}),
            playbook=playbook,
            current_day=facade._resolve_canonical_day(state),
        )
        symbol_prior_adjustment = float(symbol_prior_result.get("adjustment") or 0.0)
        scanner_intrinsic_control_score_total = (
            base_score
            + intrinsic_control_positive
            + legacy_adjust
            - intrinsic_control_risk
            + rank_bonus
            - repeat_symbol_penalty
            - repeat_blocker_penalty
            + scanner_memory_bias_adjustment
            + symbol_prior_adjustment
            + etf_deviation_bias
        )
        pre_adjust_score_total = (
            base_score
            + positive_score
            + legacy_adjust
            - risk_penalty_score
            + rank_bonus
            - repeat_symbol_penalty
            - repeat_blocker_penalty
            + scanner_bias_adjustment
            + scanner_memory_bias_adjustment
            + symbol_prior_adjustment
            + etf_deviation_bias
        )
        score_total = pre_adjust_score_total + compatibility_bias + scanner_macro_chart_fit_bias

        neg_news = max(-news_s, 0.0)
        neg_global = max(-gs, 0.0)
        feature_risk = w["feature_risk_penalty"] * max(-feature_signal, 0.0)
        if feature_regime == "high_volatility":
            feature_risk += w["high_vol_risk_penalty"]
        adj_risk = (
            base_risk
            + w["risk_news_penalty"] * neg_news
            + w["risk_global_penalty"] * neg_global
            + feature_risk
            + (0.35 * volatility_penalty * practical_scale)
            + (0.25 * gap_penalty * practical_scale)
            + (0.10 * open_order_penalty)
        )
    return (adj_risk, compatibility_bias, compatibility_result, feature_risk, macro_chart_fit, neg_global, neg_news, pre_adjust_score_total, scanner_intrinsic_control_score_total, scanner_macro_chart_fit_bias, score_total, symbol_prior_adjustment, symbol_prior_result)


def scan_score_adj_conf_adj_risk(etf_deviation_tradeable, etf_deviation_premium_score, etf_deviation_entry_score, open_order_penalty, base_conf, positive_score, risk_penalty_score, w, news_s, repeat_symbol_penalty, adj_risk, repeat_blocker_penalty, symbol_prior_result, scanner_bias_adjustment, scanner_memory_bias_adjustment, scanner_memory_bias_observed_adjustment, symbol_prior_adjustment, etf_deviation_bias, compatibility_bias, scanner_macro_chart_fit_bias, rank_bonus, trading_value_component, momentum_component, trend_component, ma_alignment_component, adx_component, volume_surge_component, intraday_strength_component, vwap_alignment_component, theme_boost_component, sentiment_component, practical_scale, practical_w, cross_section_rank_component, avoid_theme_penalty, *, facade):
    if True:
        if etf_deviation_tradeable and etf_deviation_premium_score > 0.0:
            adj_risk += 0.05 * etf_deviation_premium_score
        if etf_deviation_tradeable and etf_deviation_entry_score > 0.0:
            adj_risk -= 0.03 * etf_deviation_entry_score
        adj_conf = facade._clamp(
            base_conf
            + w["confidence_news_boost"] * max(news_s, 0.0)
            + 0.15 * (positive_score - risk_penalty_score)
            - 0.08 * open_order_penalty,
            0.0,
            1.0,
        )
        if etf_deviation_tradeable and etf_deviation_entry_score > 0.0:
            adj_conf = facade._clamp(adj_conf + (0.05 * etf_deviation_entry_score), 0.0, 1.0)
        if etf_deviation_tradeable and etf_deviation_premium_score > 0.0:
            adj_conf = facade._clamp(adj_conf - (0.04 * etf_deviation_premium_score), 0.0, 1.0)
        if repeat_symbol_penalty > 0.0:
            adj_conf = facade._clamp(adj_conf - (0.40 * repeat_symbol_penalty), 0.0, 1.0)
            adj_risk = facade._clamp(adj_risk + (0.25 * repeat_symbol_penalty), 0.0, 1.0)
        if repeat_blocker_penalty > 0.0:
            adj_conf = facade._clamp(adj_conf - (0.35 * repeat_blocker_penalty), 0.0, 1.0)
            adj_risk = facade._clamp(adj_risk + (0.20 * repeat_blocker_penalty), 0.0, 1.0)
        adj_conf = facade._clamp(adj_conf + float(symbol_prior_result.get("confidence_delta") or 0.0), 0.0, 1.0)
        adj_risk = facade._clamp(adj_risk + float(symbol_prior_result.get("risk_delta") or 0.0), 0.0, 1.0)

        score_breakdown = {
            "trading_value": float(practical_w["trading_value"] * trading_value_component),
            "momentum": float(practical_w["momentum"] * momentum_component),
            "trend": float(practical_w["trend"] * trend_component),
            "ma_alignment": float(practical_w["trend"] * 0.35 * ma_alignment_component),
            "adx_trend": float(practical_w["trend"] * 0.20 * adx_component),
            "volume_surge": float(practical_w["volume_surge"] * volume_surge_component),
            "intraday_strength": float(practical_w["intraday_strength"] * intraday_strength_component),
            "vwap_alignment": float(practical_w["intraday_strength"] * 0.30 * vwap_alignment_component),
            "theme_boost": float(practical_w["theme_boost"] * theme_boost_component),
            "sentiment": float(practical_w["sentiment"] * sentiment_component),
            "cross_section_rank": float(0.05 * cross_section_rank_component * practical_scale),
            "avoid_theme_penalty": float(-0.20 * avoid_theme_penalty * practical_scale),
            "repeat_symbol_penalty": float(-repeat_symbol_penalty),
            "repeat_blocker_penalty": float(-repeat_blocker_penalty),
            "scanner_bias": float(scanner_bias_adjustment),
            "scanner_memory_bias": float(scanner_memory_bias_adjustment),
            "scanner_memory_bias_observed": float(scanner_memory_bias_observed_adjustment),
            "symbol_prior": float(symbol_prior_adjustment),
            "etf_deviation_bias": float(etf_deviation_bias),
            "entry_compatibility_bias": float(compatibility_bias),
            "scanner_macro_chart_fit_bias": float(scanner_macro_chart_fit_bias),
            "risk_penalty": float(-risk_penalty_score),
            "rank_bonus": float(rank_bonus),
        }
    return (adj_conf, adj_risk, score_breakdown)
