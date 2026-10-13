"""Scanner candidate feature projection and deterministic defaults (scale, floating order and risk cap unchanged).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/scanner_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


class CandidateRankInputs(NamedTuple):
    """Result of `candidate_rank_inputs` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    candidate_rank_score: Any
    candidate_universe_score: Any
    deviation_signal: Any
    etf_deviation_bias: Any
    etf_deviation_entry_score: Any
    etf_deviation_premium_score: Any
    etf_deviation_tradeable: Any
    feature_regime: Any
    feature_row: Any
    feature_signal: Any
    ma120_gap: Any
    ma20_gap: Any
    ma60_gap: Any
    metrics: Any
    news_s: Any
    news_sig: Any
    open_orders: Any
    order_penalty: Any
    quote: Any
    quote_price: Any
    quote_price_num: Any
    return20: Any
    source_scores: Any
    trend_strength: Any


def candidate_rank_inputs(candidate_meta, symbol, news_by_sym, news_signal_by_sym, skill_quotes, state, row, feature_map, skill_order_counts, *, facade):
    candidate_rank_score = facade._clamp(facade._to_float(candidate_meta.get("rank_score") or 0.0), -1.0, 1.0)
    candidate_universe_score = facade._clamp(facade._to_float(candidate_meta.get("universe_score") or 0.0), 0.0, 10.0)
    source_scores = dict(candidate_meta.get("source_scores") or {})

    news_s = facade._to_float(news_by_sym.get(symbol, news_by_sym.get(facade._norm_symbol(symbol), 0.0)))
    news_sig = (
        news_signal_by_sym.get(symbol)
        if isinstance(news_signal_by_sym.get(symbol), dict)
        else news_signal_by_sym.get(facade._norm_symbol(symbol), {})
    )
    metrics = facade._candidate_quote_metrics(symbol, skill_quotes=skill_quotes, state=state)
    quote = skill_quotes.get(facade._norm_symbol(symbol), {}) if isinstance(skill_quotes.get(facade._norm_symbol(symbol)), dict) else {}
    quote_price = quote.get("price")
    if quote_price is None:
        quote_price = quote.get("cur")
    quote_price_num = facade._to_float(quote_price) if quote_price is not None else None
    deviation_signal = facade.extract_etf_deviation_signal(
        symbol=symbol,
        candidate={**dict(candidate_meta), **dict(row if isinstance(row, dict) else {})},
        features=feature_map.get(facade._norm_symbol(symbol), {}) if isinstance(feature_map.get(facade._norm_symbol(symbol)), dict) else {},
        quote=quote,
        state=state,
        asset_class_detected=(
            candidate_meta.get("asset_class_detected")
            or (row.get("asset_class_detected") if isinstance(row, dict) else "")
        ),
    )
    etf_deviation_tradeable = bool(
        deviation_signal.get("is_etf_family")
        or deviation_signal.get("available")
    )
    etf_deviation_entry_score = (
        float(deviation_signal.get("entry_discount_score") or 0.0)
        if etf_deviation_tradeable
        else 0.0
    )
    etf_deviation_premium_score = (
        float(deviation_signal.get("exit_premium_score") or 0.0)
        if etf_deviation_tradeable
        else 0.0
    )
    etf_deviation_bias = float((0.08 * etf_deviation_entry_score) - (0.08 * etf_deviation_premium_score))
    open_orders = int(skill_order_counts.get(facade._norm_symbol(symbol), 0))
    order_penalty = min(open_orders, 3)

    feature_row = feature_map.get(facade._norm_symbol(symbol), {})
    if not isinstance(feature_row, dict):
        feature_row = {}
    feature_signal = facade._clamp(facade._to_float(feature_row.get("signal_score") or 0.0), -1.0, 1.0)
    feature_regime = str(feature_row.get("regime") or "").strip().lower()
    return20 = facade._to_float(feature_row.get("return20"))
    ma20_gap = facade._to_float(feature_row.get("ma20_gap"))
    ma60_gap = facade._to_float(feature_row.get("ma60_gap"))
    ma120_gap = facade._to_float(feature_row.get("ma120_gap"))
    trend_strength = facade._to_float(feature_row.get("trend_strength"))
    return CandidateRankInputs(candidate_rank_score, candidate_universe_score, deviation_signal, etf_deviation_bias, etf_deviation_entry_score, etf_deviation_premium_score, etf_deviation_tradeable, feature_regime, feature_row, feature_signal, ma120_gap, ma20_gap, ma60_gap, metrics, news_s, news_sig, open_orders, order_penalty, quote, quote_price, quote_price_num, return20, source_scores, trend_strength)


def scan_feature_adx14_adx_component(feature_row, candidate_meta, row, metrics, source_scores, return20, ma20_gap, ma120_gap, ma60_gap, trend_strength, feature_signal, pool_meta, symbol, news_s, gs, *, facade):
    if True:
        adx14 = facade._to_float(feature_row.get("adx14"))
        volume_spike20 = facade._to_float(feature_row.get("volume_spike20"))
        volatility20 = facade._to_float(feature_row.get("volatility20"))
        vwap_distance = facade._to_float(feature_row.get("vwap_distance"))
        cross_section_rank = facade._to_float(feature_row.get("cross_section_rank"))
        gap_pct = abs(facade._to_float(feature_row.get("gap_pct")))
        base_risk_result = facade.resolve_candidate_base_risk(
            candidate=candidate_meta,
            scanner_row=row,
            features=feature_row,
            quote_metrics=metrics,
        )
        base_risk = float(base_risk_result.get("risk_score") or 0.0)

        trading_value_component = facade._norm01(facade._to_float(source_scores.get("top_value")), 0.0, 2.0)
        momentum_raw = (0.65 * facade._signed01(return20, 0.10)) + (0.35 * facade._signed01(ma20_gap, 0.03))
        momentum_component = max(0.0, momentum_raw)
        ma_alignment_component = max(
            0.0,
            (
                0.45 * facade._signed01(ma20_gap, 0.03)
                + 0.35 * facade._signed01(ma60_gap, 0.05)
                + 0.20 * facade._signed01(ma120_gap, 0.08)
            ),
        )
        adx_component = facade._norm01(adx14, 15.0, 35.0)
        trend_raw = trend_strength if trend_strength != 0.0 else feature_signal
        trend_component = max(
            0.0,
            (
                0.45 * max(0.0, facade._signed01(trend_raw, 1.0))
                + 0.35 * ma_alignment_component
                + 0.20 * adx_component
            ),
        )
        volume_surge_component = facade._norm01(volume_spike20, 1.0, 3.0)
        vwap_alignment_component = max(0.0, facade._signed01(vwap_distance, 0.02))
        intraday_strength_component = max(
            0.0,
            (
                0.70 * max(0.0, facade._signed01(facade._to_float(metrics.get("change_pct")), 5.0))
                + 0.30 * vwap_alignment_component
            ),
        )
        cross_section_rank_component = facade._norm01(cross_section_rank, 0.0, 1.0)

        theme_matched_symbols = set(facade._norm_symbol(x) for x in list(pool_meta.get("theme_matched_symbols") or []))
        avoid_theme_symbols = set(facade._norm_symbol(x) for x in list(pool_meta.get("avoid_matched_symbols") or []))
        theme_boost_component = 1.0 if (symbol in theme_matched_symbols and len(theme_matched_symbols) > 0) else 0.0
        sentiment_component = max(0.0, (0.7 * news_s) + (0.3 * gs))

        volatility_penalty = facade._norm01(volatility20, 0.03, 0.08)
    return (adx14, adx_component, avoid_theme_symbols, base_risk, base_risk_result, cross_section_rank, cross_section_rank_component, gap_pct, intraday_strength_component, ma_alignment_component, momentum_component, momentum_raw, sentiment_component, theme_boost_component, theme_matched_symbols, trading_value_component, trend_component, trend_raw, volatility20, volatility_penalty, volume_spike20, volume_surge_component, vwap_alignment_component, vwap_distance)


def scan_feature_avoid_theme_penalty_bias_result(gap_pct, order_penalty, symbol, avoid_theme_symbols, state, policy, practical_scale, cross_section_rank_component, candidate_universe_score, sentiment_component, candidate_rank_score, theme_boost_component, practical_w, intraday_strength_component, volume_surge_component, trend_component, trading_value_component, momentum_component, volatility_penalty, feature_signal, news_s, gs, w, intrinsic_control_w, feature_row, metrics, scanner_bias_context, scanner_memory_bias, candidate_meta, minute_rows_by_symbol, *, facade):
    if True:
        gap_penalty = facade._norm01(gap_pct, 0.03, 0.10)
        open_order_penalty = facade._norm01(float(order_penalty), 0.0, 3.0)
        avoid_theme_penalty = 1.0 if (symbol in avoid_theme_symbols and len(avoid_theme_symbols) > 0) else 0.0

        repeat_penalty_meta = facade._repeat_symbol_penalty(state, symbol=symbol, policy=policy)
        repeat_symbol_penalty = facade._to_float(repeat_penalty_meta.get("penalty"))
        blocker_penalty_meta = facade._repeat_blocker_cooldown_penalty(state, symbol=symbol, policy=policy)
        repeat_blocker_penalty = facade._to_float(blocker_penalty_meta.get("penalty"))

        positive_score = (
            practical_w["trading_value"] * trading_value_component
            + practical_w["momentum"] * momentum_component
            + practical_w["trend"] * trend_component
            + practical_w["volume_surge"] * volume_surge_component
            + practical_w["intraday_strength"] * intraday_strength_component
            + practical_w["theme_boost"] * theme_boost_component
            + practical_w["sentiment"] * sentiment_component
            + (0.06 * max(0.0, candidate_rank_score))
            + (0.02 * facade._norm01(candidate_universe_score, 0.0, 10.0))
            + (0.05 * cross_section_rank_component)
        ) * practical_scale
        risk_penalty_score = (
            practical_w["volatility_penalty"] * volatility_penalty
            + practical_w["gap_penalty"] * gap_penalty
            + practical_w["open_order_penalty"] * open_order_penalty
            + (0.20 * avoid_theme_penalty)
        ) * practical_scale

        # Keep backward compatibility with previous additive sentiment/risk knobs.
        legacy_adjust = (
            w["weight_news"] * news_s
            + w["weight_global"] * gs
            + w["feature_score_weight"] * feature_signal
            - (0.03 * open_order_penalty)
        )
        rank_bonus = 0.01 * max(0.0, candidate_rank_score)
        intrinsic_control_positive = (
            intrinsic_control_w["trading_value"] * trading_value_component
            + intrinsic_control_w["momentum"] * momentum_component
            + intrinsic_control_w["trend"] * trend_component
            + intrinsic_control_w["volume_surge"] * volume_surge_component
            + intrinsic_control_w["intraday_strength"] * intraday_strength_component
            + intrinsic_control_w["sentiment"] * sentiment_component
            + (0.06 * max(0.0, candidate_rank_score))
            + (0.02 * facade._norm01(candidate_universe_score, 0.0, 10.0))
            + (0.05 * cross_section_rank_component)
        ) * practical_scale
        intrinsic_control_risk = (
            intrinsic_control_w["volatility_penalty"] * volatility_penalty
            + intrinsic_control_w["gap_penalty"] * gap_penalty
            + intrinsic_control_w["open_order_penalty"] * open_order_penalty
        ) * practical_scale
        bias_result = facade._compute_structured_scanner_bias(
            symbol=symbol,
            feature_row=feature_row,
            metrics=metrics,
            bias_context=scanner_bias_context,
        )
        scanner_bias_adjustment = float(bias_result.get("bias_adjustment") or 0.0)
        memory_bias_result = facade.compute_scanner_memory_bias_adjustment(
            symbol=symbol,
            candidate_sources=list(candidate_meta.get("sources") or []),
            memory_bias=scanner_memory_bias,
        )
        scanner_memory_bias_observed_adjustment = float(memory_bias_result.get("bias_adjustment") or 0.0)
        scanner_memory_bias_observation_only = facade._memory_bias_observation_only(state)
        scanner_memory_bias_adjustment = 0.0 if scanner_memory_bias_observation_only else scanner_memory_bias_observed_adjustment
        candidate_rows = []
        raw_minute_rows = minute_rows_by_symbol.get(facade._norm_symbol(symbol)) if isinstance(minute_rows_by_symbol, dict) else None
    return (avoid_theme_penalty, bias_result, blocker_penalty_meta, candidate_rows, gap_penalty, intrinsic_control_positive, intrinsic_control_risk, legacy_adjust, memory_bias_result, open_order_penalty, positive_score, rank_bonus, raw_minute_rows, repeat_blocker_penalty, repeat_penalty_meta, repeat_symbol_penalty, risk_penalty_score, scanner_bias_adjustment, scanner_memory_bias_adjustment, scanner_memory_bias_observation_only, scanner_memory_bias_observed_adjustment)
