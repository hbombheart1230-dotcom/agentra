"""Scanner guidance extraction, weight application and structured bias (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _extract_scanner_guidance_r3_impl(state, *, facade):
    strategist_output_raw = state.get("strategist_output")
    strategist_output = facade.coerce_strategist_output(strategist_output_raw) if isinstance(strategist_output_raw, dict) else {}
    strategy_policy = (
        dict(strategist_output.get("strategy_policy") or {})
        if isinstance(strategist_output.get("strategy_policy"), dict)
        else {}
    )
    scanner_policy = (
        dict(strategy_policy.get("scanner_policy") or {})
        if isinstance(strategy_policy.get("scanner_policy"), dict)
        else {}
    )
    monitor_policy = (
        dict(strategy_policy.get("monitor_policy") or {})
        if isinstance(strategy_policy.get("monitor_policy"), dict)
        else {}
    )
    commander_context = (
        dict(strategy_policy.get("commander_context") or {})
        if isinstance(strategy_policy.get("commander_context"), dict)
        else {}
    )
    strategist_plan = (
        dict(strategy_policy.get("strategist_plan") or {})
        if isinstance(strategy_policy.get("strategist_plan"), dict)
        else {}
    )
    policy_provenance = (
        dict(strategy_policy.get("provenance") or {})
        if isinstance(strategy_policy.get("provenance"), dict)
        else {}
    )
    scanner_bias_context = {}
    if isinstance(commander_context.get("scanner_bias"), dict):
        scanner_bias_context = dict(commander_context.get("scanner_bias") or {})
    elif isinstance(scanner_policy.get("scanner_bias"), dict):
        scanner_bias_context = dict(scanner_policy.get("scanner_bias") or {})
    elif isinstance(strategist_output.get("scanner_bias_context"), dict):
        scanner_bias_context = dict(strategist_output.get("scanner_bias_context") or {})
    scanner_memory_bias = {}
    if isinstance(commander_context.get("scanner_memory_bias"), dict):
        scanner_memory_bias = dict(commander_context.get("scanner_memory_bias") or {})
    elif isinstance(scanner_policy.get("scanner_memory_bias"), dict):
        scanner_memory_bias = dict(scanner_policy.get("scanner_memory_bias") or {})
    elif isinstance(strategist_output.get("scanner_memory_bias"), dict):
        scanner_memory_bias = dict(strategist_output.get("scanner_memory_bias") or {})
    symbol_constraints = (
        dict(strategist_plan.get("symbol_constraints") or {})
        if isinstance(strategist_plan.get("symbol_constraints"), dict)
        else {}
    )
    raw_bias = strategist_output.get("scanner_bias")
    if isinstance(raw_bias, dict):
        raw_bias = str(raw_bias.get("style") or "")
    base = {
        "themes": list(strategist_output.get("themes") or []),
        "selected_themes": list(strategist_output.get("selected_themes") or []),
        "avoid_themes": list(strategist_output.get("avoid_themes") or []),
        "playbook": str(
            strategist_output.get("playbook")
            or strategist_plan.get("selected_playbook")
            or ""
        ),
        "tactical_strategy": str(strategist_output.get("tactical_strategy") or ""),
        "tactical_subtype": str(strategist_output.get("tactical_subtype") or ""),
        "scanner_priority": list(
            scanner_policy.get("priority_tilts")
            or strategist_output.get("scanner_priority")
            or symbol_constraints.get("scanner_priority")
            or []
        ),
        "scanner_source_policy": dict(
            scanner_policy.get("candidate_sources")
            if isinstance(scanner_policy.get("candidate_sources"), dict)
            else strategist_output.get("scanner_source_policy")
            or {}
        ),
        "scanner_bias": str(raw_bias or "").strip().lower(),
        "scanner_bias_context": dict(scanner_bias_context),
        "scanner_memory_bias": dict(scanner_memory_bias),
        "trade_aggressiveness": strategist_output.get("trade_aggressiveness"),
        "risk_tone": strategist_output.get("risk_tone"),
        "monitor_guidance": strategist_output.get("monitor_guidance"),
        "theme_source": strategist_output.get("theme_source"),
        "theme_source_status": strategist_output.get("theme_source_status"),
        "theme_strength_packet": dict(strategist_output.get("theme_strength_packet") or {})
        if isinstance(strategist_output.get("theme_strength_packet"), dict)
        else {},
        "available_themes": list(strategist_output.get("available_themes") or []),
        "theme_strategy": dict(strategist_output.get("theme_strategy") or {})
        if isinstance(strategist_output.get("theme_strategy"), dict)
        else {},
        "score_weights": dict(scanner_policy.get("score_weights") or {}),
        "filters": dict(scanner_policy.get("filters") or {}),
        "ranking_rules": dict(scanner_policy.get("ranking_rules") or {}),
        "monitor_policy": dict(monitor_policy),
        "commander_context": commander_context,
        "strategist_plan": strategist_plan,
        "policy_provenance": policy_provenance,
    }

    # Backward-compatible override hook; canonical source remains strategist_output.
    guidance = state.get("scanner_guidance")
    if isinstance(guidance, dict):
        out = dict(base)
        for key in (
            "themes",
            "selected_themes",
            "avoid_themes",
            "playbook",
            "tactical_strategy",
            "tactical_subtype",
            "scanner_priority",
            "scanner_source_policy",
            "scanner_bias",
            "scanner_bias_context",
            "scanner_memory_bias",
            "trade_aggressiveness",
            "risk_tone",
            "monitor_guidance",
            "theme_source",
            "theme_source_status",
            "theme_strength_packet",
            "available_themes",
            "theme_strategy",
            "score_weights",
            "filters",
            "ranking_rules",
            "monitor_policy",
            "commander_context",
            "strategist_plan",
            "policy_provenance",
        ):
            if guidance.get(key) not in (None, ""):
                out[key] = guidance.get(key)
        raw_override_bias = out.get("scanner_bias")
        if isinstance(raw_override_bias, dict):
            out["scanner_bias"] = str(raw_override_bias.get("style") or "")
        return out

    return base


def _apply_scanner_guidance_weights_r3_impl(
    weights,
    *,
    playbook,
    scanner_bias,
    scanner_priority,
    trade_aggressiveness,
    risk_tone,
    facade,
):
    out = dict(weights or {})
    bias = str(scanner_bias or "").strip().lower()
    priority_set = set(facade._normalize_priority_list(scanner_priority))
    playbook_norm = str(playbook or "").strip().lower()
    aggr = str(trade_aggressiveness or "").strip().lower()
    tone = str(risk_tone or "").strip().lower()

    if bias == "large_cap":
        out["trading_value"] = float(out.get("trading_value", 0.0) * 1.10)
        out["volatility_penalty"] = float(out.get("volatility_penalty", 0.0) * 1.12)
    elif bias == "leader":
        out["trend"] = float(out.get("trend", 0.0) * 1.08)
        out["theme_boost"] = float(out.get("theme_boost", 0.0) * 1.08)
    elif bias == "momentum":
        out["momentum"] = float(out.get("momentum", 0.0) * 1.12)
        out["volume_surge"] = float(out.get("volume_surge", 0.0) * 1.08)
    elif bias == "value":
        out["trading_value"] = float(out.get("trading_value", 0.0) * 1.10)
        out["momentum"] = float(out.get("momentum", 0.0) * 0.94)

    # Priority-driven mild boosts (additive-safe, scanner remains quantitative).
    if "liquidity" in priority_set:
        out["trading_value"] = float(out.get("trading_value", 0.0) * 1.10)
    if "momentum" in priority_set or "breakout" in priority_set:
        out["momentum"] = float(out.get("momentum", 0.0) * 1.12)
    if "trend_strength" in priority_set or "trend" in priority_set:
        out["trend"] = float(out.get("trend", 0.0) * 1.10)
    if "ma_alignment" in priority_set or "moving_average_trend" in priority_set:
        out["trend"] = float(out.get("trend", 0.0) * 1.08)
    if "vwap_reclaim" in priority_set or "vwap_distance" in priority_set:
        out["intraday_strength"] = float(out.get("intraday_strength", 0.0) * 1.08)
    if "cross_section_rank" in priority_set or "relative_strength" in priority_set:
        out["trend"] = float(out.get("trend", 0.0) * 1.06)
        out["theme_boost"] = float(out.get("theme_boost", 0.0) * 1.04)
    if "volume_surge" in priority_set or "volume_confirmation" in priority_set:
        out["volume_surge"] = float(out.get("volume_surge", 0.0) * 1.08)
    if "risk_penalty" in priority_set or "drawdown_control" in priority_set:
        out["volatility_penalty"] = float(out.get("volatility_penalty", 0.0) * 1.15)
        out["gap_penalty"] = float(out.get("gap_penalty", 0.0) * 1.15)

    # Playbook guidance remains additive (Scanner still does final quantitative ranking).
    if playbook_norm == "breakout":
        out["momentum"] = float(out.get("momentum", 0.0) * 1.10)
        out["volume_surge"] = float(out.get("volume_surge", 0.0) * 1.06)
    elif playbook_norm == "pullback":
        out["trend"] = float(out.get("trend", 0.0) * 1.08)
        out["intraday_strength"] = float(out.get("intraday_strength", 0.0) * 1.05)
    elif playbook_norm == "reversal":
        out["momentum"] = float(out.get("momentum", 0.0) * 0.92)
        out["gap_penalty"] = float(out.get("gap_penalty", 0.0) * 1.10)
    elif playbook_norm == "defensive":
        out["trading_value"] = float(out.get("trading_value", 0.0) * 1.08)
        out["volatility_penalty"] = float(out.get("volatility_penalty", 0.0) * 1.12)

    # Risk tone / aggressiveness final tuning.
    if aggr == "high" and tone in ("aggressive", "normal"):
        out["momentum"] = float(out.get("momentum", 0.0) * 1.05)
        out["intraday_strength"] = float(out.get("intraday_strength", 0.0) * 1.05)
    if aggr == "low" or tone == "conservative":
        out["volatility_penalty"] = float(out.get("volatility_penalty", 0.0) * 1.20)
        out["gap_penalty"] = float(out.get("gap_penalty", 0.0) * 1.20)
        out["intraday_strength"] = float(out.get("intraday_strength", 0.0) * 0.95)
        out["momentum"] = float(out.get("momentum", 0.0) * 0.95)

    return out


def _compute_structured_scanner_bias_r3_impl(*, symbol, feature_row, metrics, bias_context, facade):
    normalized_context, _meta = facade.normalize_scanner_bias_context(bias_context or None)
    context = normalized_context.to_dict()
    summary = facade.summarize_scanner_bias_context(context)
    if not bool(summary.get("enabled")):
        return {
            "bias_adjustment": 0.0,
            "bias_adjustments": [],
            "bias_summary": dict(summary),
            "bias_signals": {},
        }

    vwap_distance = facade._to_float(feature_row.get("vwap_distance"))
    volume_spike20 = facade._to_float(feature_row.get("volume_spike20"))
    intraday_change_pct = facade._to_float(metrics.get("change_pct"))
    signals = {
        "vwap_distance": float(vwap_distance),
        "volume_spike20": float(volume_spike20),
        "intraday_change_pct": float(intraday_change_pct),
    }
    adjustments: List[Dict[str, Any]] = []
    bias_delta = 0.0
    strength = str(context.get("bias_strength") or "low").strip().lower()
    cap = facade._scanner_bias_total_cap(strength)
    step = 0.005 if strength == "medium" else 0.003

    if bool(context.get("prefer_shallow_pullback_candidates")) and -0.015 <= vwap_distance <= 0.03:
        bias_delta += step
        adjustments.append({"rule": "prefer_shallow_pullback_candidates", "delta": float(step), "reason": "shallow pullback preference applied"})

    if bool(context.get("penalize_overextended")) and vwap_distance >= 0.08:
        delta = -(step * 1.5)
        bias_delta += delta
        adjustments.append({"rule": "penalize_overextended", "delta": float(delta), "reason": "overextended penalty applied"})

    if bool(context.get("prefer_reclaim_candidates")) and -0.01 <= vwap_distance <= 0.02:
        bias_delta += step
        adjustments.append({"rule": "prefer_reclaim_candidates", "delta": float(step), "reason": "reclaim preference applied"})

    if bool(context.get("prefer_volume_confirmation")) and volume_spike20 >= 1.2:
        bias_delta += step
        adjustments.append({"rule": "prefer_volume_confirmation", "delta": float(step), "reason": "volume confirmation bias applied"})

    bias_delta = facade._clamp(bias_delta, -cap, cap)
    if adjustments and abs(bias_delta) < 1e-9:
        adjustments = []

    return {
        "bias_adjustment": float(bias_delta),
        "bias_adjustments": adjustments[:4],
        "bias_summary": dict(summary),
        "bias_signals": signals,
        "symbol": str(symbol or ""),
    }
