"""Scanner macro/chart-fit proximity and fit computation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _calc_reclaim_proximity_r3_impl(*, actual, minimum, facade):
    if actual is None:
        return 0.5
    actual_num = float(actual)
    minimum_num = float(minimum if minimum is not None else -0.02)
    if actual_num >= minimum_num:
        return 1.0
    band = max(0.05, abs(minimum_num) * 3.0)
    return facade._clamp(1.0 - abs(actual_num - minimum_num) / band, 0.0, 1.0)


def _calc_breakout_proximity_r3_impl(*, actual, minimum, facade):
    if actual is None:
        return 0.5
    actual_num = float(actual)
    minimum_num = float(minimum if minimum is not None else 0.0)
    if actual_num >= minimum_num:
        return 1.0
    band = 0.02
    return facade._clamp(1.0 - abs(actual_num - minimum_num) / band, 0.0, 1.0)


def _scanner_chart_fit_from_entry_result_r3_impl(result, *, facade):
    chart_features = (
        dict(result.get("chart_structure_features") or {})
        if isinstance(result.get("chart_structure_features"), facade.Mapping)
        else {}
    )
    context = (
        dict(chart_features.get("human_chart_context") or {})
        if isinstance(chart_features.get("human_chart_context"), facade.Mapping)
        else {}
    )
    if not bool(context.get("available")):
        return {
            "available": False,
            "chart_context_score": 0.5,
            "exit_risk_score": 0.0,
            "late_entry_risk": "",
            "soft_penalty": 0.0,
            "components": {},
        }
    late_entry_risk = str(context.get("late_entry_risk") or "").strip().lower()
    late_penalty = {"high": 0.10, "medium": 0.05, "low": 0.02}.get(late_entry_risk, 0.0)
    exit_risk_score = facade._clamp(facade._to_float(context.get("exit_risk_score")), 0.0, 1.0)
    risk_penalty = 0.05 if exit_risk_score >= 0.55 else 0.0
    return {
        "available": True,
        "chart_context_score": facade._clamp(facade._to_float(context.get("entry_chart_score"), 0.5), 0.0, 1.0),
        "exit_risk_score": float(exit_risk_score),
        "late_entry_risk": late_entry_risk,
        "soft_penalty": float(late_penalty + risk_penalty),
        "components": {
            "vwap_reclaim_persistence": context.get("vwap_reclaim_persistence"),
            "ma_bullish_persistence": context.get("ma_bullish_persistence"),
            "volume_expansion_persistence": context.get("volume_expansion_persistence"),
            "late_entry_risk": late_entry_risk,
            "swing_low_above_vwap": bool(context.get("swing_low_above_vwap")),
            "box_breakout_retest_hold": bool(context.get("box_breakout_retest_hold")),
            "exit_risk_score": float(exit_risk_score),
        },
    }


def _compute_scanner_macro_chart_fit_r3_impl(
    *,
    feature_row,
    ma_alignment_component,
    trend_component,
    adx_component,
    momentum_component,
    volume_surge_component,
    vwap_alignment_component,
    cross_section_rank_component,
    volatility_penalty,
    gap_penalty,
    playbook,
    scanner_priority,
    risk_tone,
    trade_aggressiveness,
    bias_cap,
    facade,
):
    coverage_keys = (
        "return20",
        "ma20_gap",
        "ma60_gap",
        "ma120_gap",
        "trend_strength",
        "adx14",
        "volume_spike20",
        "cross_section_rank",
        "rolling_drawdown20",
        "volatility20",
        "gap_pct",
    )
    coverage = sum(1 for key in coverage_keys if feature_row.get(key) not in (None, ""))
    focus = facade._scanner_macro_focus(
        playbook=playbook,
        scanner_priority=scanner_priority,
        risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness,
    )
    if coverage < 3:
        return {
            "scanner_macro_chart_fit_score": 0.5,
            "scanner_macro_chart_fit_bias": 0.0,
            "scanner_macro_chart_fit_authority": "soft_rank_bias_only_insufficient_feature_coverage",
            "scanner_macro_chart_fit_components": {
                "feature_coverage_count": int(coverage),
                "focus": dict(focus),
            },
            "scanner_macro_chart_fit_focus": dict(focus),
        }
    return20 = facade._to_float(feature_row.get("return20"))
    ma20_gap = facade._to_float(feature_row.get("ma20_gap"))
    rolling_drawdown20 = abs(facade._to_float(feature_row.get("rolling_drawdown20")))
    relative_strength = feature_row.get("sector_relative_strength")
    if relative_strength in (None, ""):
        relative_strength = feature_row.get("relative_strength20")
    relative_strength_component = max(
        cross_section_rank_component,
        max(0.0, facade._signed01(facade._to_float(relative_strength), 0.08)),
        max(0.0, facade._signed01(return20, 0.10)),
    )
    trend_alignment_score = facade._clamp(
        (0.48 * ma_alignment_component) + (0.32 * trend_component) + (0.20 * adx_component),
        0.0,
        1.0,
    )
    adx_trend_score = facade._clamp((0.65 * adx_component) + (0.35 * trend_component), 0.0, 1.0)
    volume_accumulation_score = facade._clamp(volume_surge_component, 0.0, 1.0)
    breakout_base_score = facade._clamp(
        (0.45 * momentum_component)
        + (0.25 * trend_component)
        + (0.20 * vwap_alignment_component)
        + (0.10 * max(0.0, facade._signed01(ma20_gap, 0.03))),
        0.0,
        1.0,
    )
    drawdown_penalty = facade._norm01(rolling_drawdown20, 0.08, 0.25)
    overextension_risk = max(
        facade._norm01(max(0.0, ma20_gap), 0.06, 0.15),
        facade._clamp(volatility_penalty, 0.0, 1.0),
        facade._clamp(gap_penalty, 0.0, 1.0),
    )
    risk_balance_score = facade._clamp(
        1.0
        - (
            (0.40 * facade._clamp(volatility_penalty, 0.0, 1.0))
            + (0.35 * facade._clamp(gap_penalty, 0.0, 1.0))
            + (0.25 * drawdown_penalty)
        ),
        0.0,
        1.0,
    )
    components = {
        "trend_alignment_score": float(trend_alignment_score),
        "relative_strength_score": float(facade._clamp(relative_strength_component, 0.0, 1.0)),
        "adx_trend_score": float(adx_trend_score),
        "volume_accumulation_score": float(volume_accumulation_score),
        "breakout_base_score": float(breakout_base_score),
        "risk_balance_score": float(risk_balance_score),
        "overextension_risk": float(facade._clamp(overextension_risk, 0.0, 1.0)),
        "rolling_drawdown20": float(rolling_drawdown20),
        "focus": dict(focus),
    }
    weights = {
        "trend_alignment_score": 0.24 * focus["trend_alignment"],
        "relative_strength_score": 0.18 * focus["relative_strength"],
        "adx_trend_score": 0.12 * focus["adx_trend"],
        "volume_accumulation_score": 0.16 * focus["volume_accumulation"],
        "breakout_base_score": 0.18 * focus["breakout_base"],
        "risk_balance_score": 0.12 * focus["risk_balance"],
    }
    weight_total = sum(float(v) for v in weights.values()) or 1.0
    score = facade._clamp(
        sum(float(components[key]) * weight for key, weight in weights.items()) / weight_total,
        0.0,
        1.0,
    )
    bias_limit = max(0.0, float(bias_cap))
    bias = facade._clamp((score - 0.50) * 0.12, -bias_limit, bias_limit)
    return {
        "scanner_macro_chart_fit_score": float(score),
        "scanner_macro_chart_fit_bias": float(bias),
        "scanner_macro_chart_fit_authority": "soft_rank_bias_only",
        "scanner_macro_chart_fit_components": components,
        "scanner_macro_chart_fit_focus": dict(focus),
    }
