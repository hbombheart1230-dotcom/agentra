"""Pure Strategist LLM repair-message formatting."""
from __future__ import annotations


def build_repair_messages(payload, raw_response, *, facade):
    compact_payload = facade._build_compact_strategist_llm_payload(payload)
    call_kind = facade._resolve_strategist_llm_call_kind(compact_payload)
    system = (
        "You repair strategist outputs for an automated trading system. "
        "Return exactly one minified JSON object only, matching the required contract exactly. "
        "Do not add commentary, markdown, analysis, or explanations. "
        "If the previous draft contained prose, ignore it and generate a fresh JSON object."
    )
    base_contract = {
        "market_regime": "risk_on|neutral|risk_off",
        "market_regime_rail": "risk_off_breadth_collapse|global_risk_off_pressure|risk_on_supportive|neutral_mixed|macro_packet_unavailable",
        "news_quality": {"status": "ok|partial|weak", "headline_count": 0, "candidate_headline_count": 0, "market_headline_count": 0, "issues": ["string"], "usage_rule": "string"},
        "risk_off_exception_conditions": ["string"],
        "news_event_intelligence_usage": {"status": "used|ignored|insufficient", "used_event_ids": ["news_event_001"], "theme_watchlist": ["space_aerospace"], "symbol_watchlist": ["005930"], "reason": "string", "observation_only": True},
        "market_sentiment": "bullish|neutral|bearish",
        "key_events": ["string"], "themes": ["string"], "selected_themes": ["string from available_themes only when available"],
        "theme_strategy": {"selection_mode": "kiwoom_api_constrained|fallback", "selected_themes": [{"theme": "string", "playbook_overlay": "momentum|pullback|reversal|defensive|fallback", "scanner_directive": "string", "reason": "string"}], "fallback_reason": "string"},
        "avoid_themes": ["string"], "playbook": "breakout|pullback|reversal|defensive",
        "scanner_bias": "large_cap|leader|momentum|value",
        "scanner_priority": ["trading_value", "trend_strength", "volume_surge", "leader_quality"],
        "trade_aggressiveness": "low|medium|high", "risk_tone": "conservative|normal|aggressive",
        "monitor_guidance": "hold_through_noise|defensive_exit|quick_take_profit",
        "market_regime_summary": "string", "policy_rationale": "string", "confidence": 0.0, "policy_source": "strategist",
        "policy_adjustment": {"adjustment_required": True, "baseline_retained": False, "baseline_retained_reason": "string", "adjustment_direction": "tighten|relax|mixed|none", "dominant_failure_pattern": "string", "addressed_failure_patterns": ["string"], "delta_fields": ["volume_ratio_min"], "hold_refresh_considered": True},
        "strategy_refresh_trace": {"summary": "string", "bullets": ["string"], "stages": [{"stage": "initial_frame|post_scanner_refresh|final_application", "label": "string", "summary": "string", "requested": True, "effective": False, "reason": "string"}]},
        "monitor_entry_policy": {"timeframe_minutes": 1, "breakout_lookback": 5, "volume_lookback": 5, "volume_ratio_min": 0.68, "min_extended_from_vwap_pct": -0.02, "max_extended_from_vwap_pct": 0.13, "pullback_min_pct": 0.008, "pullback_max_pct": 0.07, "reclaim_tolerance_pct": 0.0015, "breakout_buffer_pct": 0.0, "intent_cooldown_sec": 60, "require_vwap_reclaim": True, "require_rebound": True},
        "report_focus": ["theme_accuracy", "exit_quality", "overtrading"],
    }
    contract = facade._stage_specific_llm_contract(call_kind, base_contract)
    raw = str(raw_response or "").strip()
    user = (
        "Fix or regenerate the strategist response as valid JSON.\n"
        "JSON contract:\n"
        f"{facade.json.dumps(contract, ensure_ascii=False)}\n\n"
        "Compact input:\n"
        f"{facade.json.dumps(compact_payload, ensure_ascii=False)}\n\n"
        "If Compact input contains available_themes, selected_themes must use only those theme names.\n"
        f"Previous attempt failure reason: {facade._classify_llm_parse_failure(raw)}\n"
        "Return only the repaired JSON object."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
