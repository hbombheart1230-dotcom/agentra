"""Strategist default and exit policy construction from configuration (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _default_policy_r3_impl(user_policy, *, facade):
    p = dict(user_policy or {})
    default_topn = facade._resolve_top_n_candidates(p)
    pytest_mode = bool(facade.os.getenv("PYTEST_CURRENT_TEST"))
    p.setdefault("use_universe_builder", facade._is_trueish(facade.os.getenv("USE_UNIVERSE_BUILDER", "true")))
    p.setdefault("universe_require_condition", facade._is_trueish(facade.os.getenv("UNIVERSE_REQUIRE_CONDITION", "false")))
    # candidate generation
    p.setdefault("candidate_source", "top_picks")  # top_picks | market_rank
    p.setdefault("candidate_k", int(p.get("candidate_topk", default_topn) or default_topn))
    p.setdefault("candidate_rank_mode", "value")
    p.setdefault("candidate_rank_topn", 30)
    # sentiment toggles
    p.setdefault(
        "use_global_sentiment",
        facade._is_trueish(facade.os.getenv("M10_USE_GLOBAL_SENTIMENT", "false" if pytest_mode else "true")),
    )
    p.setdefault(
        "use_news_analysis",
        facade._is_trueish(facade.os.getenv("M10_USE_NEWS_SENTIMENT", "false" if pytest_mode else "true")),
    )
    exit_enabled = facade._nested_mapping_value(p, "applied_policy", "monitor", "exit", "enabled")
    if exit_enabled is None:
        exit_enabled = p.get("use_exit_policy")
    p.setdefault("use_exit_policy", True if exit_enabled is None else facade._is_trueish(exit_enabled))
    # news plugin
    p.setdefault("news_provider", "naver")
    p.setdefault("news_scorer", "simple")
    # rerank weights
    p.setdefault("candidate_news_weight", 0.2)
    p.setdefault("candidate_global_weight", 0.1)
    p.setdefault("candidate_negative_news_threshold", -0.7)
    p.setdefault("candidate_risk_off_threshold", -0.5)
    p.setdefault("candidate_risk_on_threshold", 0.5)
    p.setdefault("candidate_max_count_risk_off", 3)
    return p


def _exit_policy_r3_impl(*, playbook, monitor_guidance, trade_aggressiveness, risk_tone, facade):
    mode = str(playbook or "").strip().lower()
    guidance = str(monitor_guidance or "").strip().lower()
    tone = str(risk_tone or "").strip().lower()
    aggr = str(trade_aggressiveness or "").strip().lower()

    if mode == "breakout":
        stop_loss_pct = 0.018
        take_profit_pct = 0.040
        baseline_tag = "breakout"
    elif mode == "pullback":
        stop_loss_pct = 0.022
        take_profit_pct = 0.036
        baseline_tag = "pullback"
    elif mode == "reversal":
        stop_loss_pct = 0.016
        take_profit_pct = 0.026
        baseline_tag = "reversal"
    else:
        stop_loss_pct = 0.014
        take_profit_pct = 0.022
        baseline_tag = "defensive"

    env_stop_raw = str(facade.os.getenv("EXIT_POLICY_STOP_LOSS_PCT", "") or "").strip()
    env_take_raw = str(facade.os.getenv("EXIT_POLICY_TAKE_PROFIT_PCT", "") or "").strip()
    if env_stop_raw:
        stop_loss_pct = facade._to_float(env_stop_raw, stop_loss_pct) or stop_loss_pct
        baseline_tag = "env_stop"
    if env_take_raw:
        take_profit_pct = facade._to_float(env_take_raw, take_profit_pct) or take_profit_pct
        baseline_tag = "env_take" if baseline_tag == "env_stop" else baseline_tag

    trailing_stop_pct = facade._to_float(facade.os.getenv("EXIT_POLICY_TRAILING_STOP_PCT", "0.0"), 0.0)
    vol_expansion_ratio = facade._to_float(facade.os.getenv("EXIT_POLICY_VOL_EXPANSION_RATIO", "0.0"), 0.0)
    news_shock_threshold = facade._to_float(facade.os.getenv("EXIT_POLICY_NEWS_SHOCK_THRESHOLD", "0.0"), 0.0)
    peak_drawdown_exit_pct = facade._to_float(facade.os.getenv("EXIT_POLICY_PEAK_DRAWDOWN_EXIT_PCT", "0.0"), 0.0)
    profit_protection_activation_pct = facade._to_float(
        facade.os.getenv("EXIT_POLICY_PROFIT_PROTECTION_ACTIVATION_PCT", "0.008"),
        0.008,
    )
    peak_drawdown_mode = str(facade.os.getenv("EXIT_POLICY_PEAK_DRAWDOWN_MODE", "profit_protection") or "profit_protection").strip().lower()
    confirm_required_for_peak_drawdown = max(
        1,
        int(facade._to_float(facade.os.getenv("EXIT_POLICY_CONFIRM_REQUIRED_FOR_PEAK_DRAWDOWN", "2"), 2.0)),
    )
    vwap_breakdown_pct = facade._to_float(facade.os.getenv("EXIT_POLICY_VWAP_BREAKDOWN_PCT", "0.0"), 0.0)
    intraday_low_break_pct = facade._to_float(facade.os.getenv("EXIT_POLICY_INTRADAY_LOW_BREAK_PCT", "0.0"), 0.0)
    trend_strength_floor = facade._to_float(facade.os.getenv("EXIT_POLICY_TREND_STRENGTH_FLOOR", "0.0"), 0.0)
    adjustments: List[str] = [f"baseline:{baseline_tag}"]

    if mode == "breakout":
        stop_loss_pct *= 0.90
        take_profit_pct *= 1.40
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.90)
        vol_expansion_ratio = max(vol_expansion_ratio, 2.20)
        adjustments.append("playbook:breakout")
    elif mode == "pullback":
        stop_loss_pct *= 1.05
        take_profit_pct *= 1.20
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.75)
        vol_expansion_ratio = max(vol_expansion_ratio, 2.00)
        adjustments.append("playbook:pullback")
    elif mode == "reversal":
        stop_loss_pct *= 0.85
        take_profit_pct *= 1.00
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.70)
        vol_expansion_ratio = max(vol_expansion_ratio, 1.80)
        adjustments.append("playbook:reversal")
    else:
        stop_loss_pct *= 0.80
        take_profit_pct *= 0.90
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.65)
        vol_expansion_ratio = max(vol_expansion_ratio, 1.60)
        adjustments.append("playbook:defensive")

    if guidance == "hold_through_noise":
        stop_loss_pct *= 1.10
        take_profit_pct *= 1.10
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.95)
        adjustments.append("monitor_guidance:hold_through_noise")
    elif guidance == "quick_take_profit":
        stop_loss_pct *= 0.95
        take_profit_pct *= 0.85
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.80)
        adjustments.append("monitor_guidance:quick_take_profit")
    elif guidance == "defensive_exit":
        stop_loss_pct *= 0.92
        take_profit_pct *= 0.92
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.70)
        adjustments.append("monitor_guidance:defensive_exit")

    if tone == "conservative":
        stop_loss_pct *= 0.90
        take_profit_pct *= 0.95
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 0.75)
        adjustments.append("risk_tone:conservative")
    elif tone == "aggressive":
        stop_loss_pct *= 1.10
        take_profit_pct *= 1.10
        trailing_stop_pct = max(trailing_stop_pct, stop_loss_pct * 1.00)
        adjustments.append("risk_tone:aggressive")

    if aggr == "low":
        take_profit_pct *= 0.95
        adjustments.append("trade_aggressiveness:low")
    elif aggr == "high":
        take_profit_pct *= 1.08
        adjustments.append("trade_aggressiveness:high")

    stop_loss_pct = facade._clamp(stop_loss_pct, 0.003, 0.10)
    take_profit_pct = facade._clamp(max(take_profit_pct, stop_loss_pct * 1.05), 0.005, 0.25)
    trailing_stop_pct = facade._clamp(max(trailing_stop_pct, stop_loss_pct * 0.50), 0.0, 0.15)
    if peak_drawdown_exit_pct <= 0.0:
        if guidance == "quick_take_profit":
            peak_drawdown_exit_pct = stop_loss_pct * 0.45
        elif guidance == "hold_through_noise":
            peak_drawdown_exit_pct = stop_loss_pct * 0.80
        elif mode == "defensive":
            peak_drawdown_exit_pct = stop_loss_pct * 0.50
        elif mode == "breakout":
            peak_drawdown_exit_pct = stop_loss_pct * 0.75
        else:
            peak_drawdown_exit_pct = stop_loss_pct * 0.60
        adjustments.append("peak_drawdown_exit_pct:auto")
    if vwap_breakdown_pct <= 0.0:
        if guidance == "quick_take_profit":
            vwap_breakdown_pct = 0.004
        elif mode == "breakout":
            vwap_breakdown_pct = 0.010
        elif mode == "defensive":
            vwap_breakdown_pct = 0.005
        else:
            vwap_breakdown_pct = 0.007
        adjustments.append("vwap_breakdown_pct:auto")
    if intraday_low_break_pct <= 0.0:
        if guidance == "quick_take_profit":
            intraday_low_break_pct = 0.0015
        elif mode == "breakout":
            intraday_low_break_pct = 0.0030
        elif mode == "defensive":
            intraday_low_break_pct = 0.0020
        else:
            intraday_low_break_pct = 0.0025
        adjustments.append("intraday_low_break_pct:auto")
    if trend_strength_floor == 0.0:
        if mode == "breakout":
            trend_strength_floor = -0.05
        elif mode == "defensive":
            trend_strength_floor = -0.15
        else:
            trend_strength_floor = -0.10
        adjustments.append("trend_strength_floor:auto")
    vol_expansion_ratio = facade._clamp(vol_expansion_ratio, 0.0, 5.0)
    news_shock_threshold = facade._clamp(news_shock_threshold, 0.0, 1.0)
    peak_drawdown_exit_pct = facade._clamp(peak_drawdown_exit_pct, 0.0, 0.15)
    profit_protection_activation_pct = facade._clamp(profit_protection_activation_pct, 0.0, 0.25)
    if peak_drawdown_mode not in {"profit_protection", "always_on", "disabled"}:
        peak_drawdown_mode = "profit_protection"
        adjustments.append("peak_drawdown_mode:normalized")
    vwap_breakdown_pct = facade._clamp(vwap_breakdown_pct, 0.0, 0.05)
    intraday_low_break_pct = facade._clamp(intraday_low_break_pct, 0.0, 0.03)
    trend_strength_floor = facade._clamp(trend_strength_floor, -1.0, 1.0)

    return {
        "stop_loss_pct": float(stop_loss_pct),
        "take_profit_pct": float(take_profit_pct),
        "trailing_stop_pct": float(trailing_stop_pct),
        "vol_expansion_ratio": float(vol_expansion_ratio),
        "news_shock_threshold": float(news_shock_threshold),
        "peak_drawdown_exit_pct": float(peak_drawdown_exit_pct),
        "profit_protection_activation_pct": float(profit_protection_activation_pct),
        "peak_drawdown_mode": str(peak_drawdown_mode),
        "confirm_required_for_peak_drawdown": int(confirm_required_for_peak_drawdown),
        "vwap_breakdown_pct": float(vwap_breakdown_pct),
        "intraday_low_break_pct": float(intraday_low_break_pct),
        "trend_strength_floor": float(trend_strength_floor),
        "adjustments": list(adjustments),
        "note": "strategist_exit_policy_baseline",
    }
