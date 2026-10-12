"""Strategist commander context summary, strategist plan and strategy-field augmentation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_commander_context_summary_r3_impl(
    *,
    state,
    commander_decision,
    runtime_phase,
    market_regime,
    playbook,
    facade,
):
    raw = dict(commander_decision or {}) if isinstance(commander_decision, dict) else {}
    source = "commander_decision" if raw else "strategist_node_fallback"
    allowed_playbooks = [str(x) for x in list(raw.get("allowed_playbooks") or []) if str(x or "").strip()]
    if not allowed_playbooks and str(playbook or "").strip():
        allowed_playbooks = [str(playbook)]
    banned_playbooks = [str(x) for x in list(raw.get("banned_playbooks") or []) if str(x or "").strip()]
    strategist_refresh_context = (
        dict(raw.get("strategist_refresh_context") or {})
        if isinstance(raw.get("strategist_refresh_context"), dict)
        else {}
    )
    open_position_refresh_context = (
        dict(raw.get("open_position_refresh_context") or {})
        if isinstance(raw.get("open_position_refresh_context"), dict)
        else dict(strategist_refresh_context)
        if str(strategist_refresh_context.get("refresh_scope") or "").strip().lower() == "open_position_monitor_refresh"
        else {}
    )
    memory_packets = dict(raw.get("memory_packets") or {}) if isinstance(raw.get("memory_packets"), dict) else {}
    commander_memory_policy = (
        dict(raw.get("commander_memory_policy") or {})
        if isinstance(raw.get("commander_memory_policy"), dict)
        else {}
    )
    scanner_memory_bias = dict(raw.get("scanner_memory_bias") or {}) if isinstance(raw.get("scanner_memory_bias"), dict) else {}
    scanner_memory_bias_summary = (
        dict(raw.get("scanner_memory_bias_summary") or {})
        if isinstance(raw.get("scanner_memory_bias_summary"), dict)
        else {}
    )
    monitor_memory_bias = dict(raw.get("monitor_memory_bias") or {}) if isinstance(raw.get("monitor_memory_bias"), dict) else {}
    monitor_memory_bias_summary = (
        dict(raw.get("monitor_memory_bias_summary") or {})
        if isinstance(raw.get("monitor_memory_bias_summary"), dict)
        else {}
    )
    try:
        memory_state = {
            **dict(state),
            "commander_decision": dict(raw),
            "strategist_refresh_context": dict(strategist_refresh_context),
            "commander_open_position_refresh_context": dict(open_position_refresh_context),
        }
        memory_packets = facade.load_commander_memory_packets(state=memory_state)
        commander_memory_policy = facade.build_commander_memory_policy(
            session_bias=str(raw.get("session_bias") or runtime_phase or "session"),
            memory_packets=memory_packets,
            usage_disabled=facade._strategy_memory_usage_disabled(state),
        )
        scanner_memory_bias = facade.build_scanner_memory_bias(
            commander_memory_policy=commander_memory_policy,
            memory_packets=memory_packets,
        )
        scanner_memory_bias_summary = facade.summarize_scanner_memory_bias(scanner_memory_bias)
        monitor_memory_bias = facade.build_monitor_memory_bias(
            commander_memory_policy=commander_memory_policy,
            memory_packets=memory_packets,
        )
        monitor_memory_bias_summary = facade.summarize_monitor_memory_bias(monitor_memory_bias)
    except Exception:
        pass
    if isinstance(raw.get("commander_horizon_policy"), dict):
        commander_horizon_policy = dict(raw.get("commander_horizon_policy") or {})
    else:
        prior_strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
        horizon_proposal = {}
        if isinstance(prior_strategist_output.get("strategist_horizon_proposal"), dict):
            horizon_proposal = dict(prior_strategist_output.get("strategist_horizon_proposal") or {})
        elif isinstance(prior_strategist_output.get("strategy_horizon_feedback"), dict):
            horizon_proposal = dict(prior_strategist_output.get("strategy_horizon_feedback") or {})
        commander_horizon_policy = facade.build_commander_horizon_policy(
            horizon_proposal,
            commander_context={
                "runtime_phase": str(runtime_phase or ""),
                "market_regime": str(raw.get("market_regime") or market_regime or "neutral"),
                "session_bias": str(raw.get("session_bias") or runtime_phase or "session"),
                "risk_mode": str(raw.get("risk_mode") or "balanced"),
                "strategist_refresh_requested": bool(raw.get("strategist_refresh_requested")),
                "strategist_refresh_reason": str(raw.get("strategist_refresh_reason") or ""),
                "commander_memory_policy": dict(commander_memory_policy),
            },
            memory_packets=memory_packets,
            runtime_phase=str(runtime_phase or ""),
            live_validation_mode=True,
            source="strategist_commander_context",
        )
    horizon_context = facade.build_horizon_context(commander_horizon_policy)
    strategist_refresh_context = {
        **dict(strategist_refresh_context or {}),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
    }
    if open_position_refresh_context:
        open_position_refresh_context = {
            **dict(open_position_refresh_context or {}),
            "commander_horizon_policy": dict(commander_horizon_policy),
            "horizon_context": dict(horizon_context),
        }
    return {
        "source": source,
        "market_regime": str(raw.get("market_regime") or market_regime or "neutral"),
        "session_bias": str(raw.get("session_bias") or runtime_phase or "session"),
        "risk_mode": str(raw.get("risk_mode") or "balanced"),
        "allowed_playbooks": allowed_playbooks[:4],
        "banned_playbooks": banned_playbooks[:4],
        "scanner_mission": str(raw.get("scanner_mission") or ""),
        "monitor_mission": str(raw.get("monitor_mission") or ""),
        "llm_policy": str(raw.get("llm_policy") or raw.get("llm_invocation_policy") or ""),
        "command_intent": str(raw.get("command_intent") or ""),
        "strategist_invocation": str(raw.get("strategist_invocation") or ""),
        "flow_instruction": str(raw.get("flow_instruction") or ""),
        "no_trade_reason_code": str(raw.get("no_trade_reason_code") or ""),
        "strategist_refresh_requested": bool(raw.get("strategist_refresh_requested")),
        "strategist_refresh_reason": str(raw.get("strategist_refresh_reason") or ""),
        "strategist_refresh_context": dict(strategist_refresh_context),
        "open_position_refresh_context": dict(open_position_refresh_context),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
        "decision_summary": str(raw.get("decision_summary") or ""),
        "observations": dict(raw.get("observations") or {}) if isinstance(raw.get("observations"), dict) else {},
        "memory_packets": dict(memory_packets),
        "commander_memory_policy": dict(commander_memory_policy),
        "scanner_memory_bias": dict(scanner_memory_bias),
        "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
        "monitor_memory_bias": dict(monitor_memory_bias),
        "monitor_memory_bias_summary": dict(monitor_memory_bias_summary),
        "source_priority": [str(x) for x in list(raw.get("source_priority") or []) if str(x or "").strip()][:4],
        "source_refs": dict(raw.get("source_refs") or {}) if isinstance(raw.get("source_refs"), dict) else {},
        "shadow_used": bool(raw.get("shadow_used")),
        "strategist_fallback_used": bool(raw.get("strategist_fallback_used")),
    }


def _build_strategist_plan_r3_impl(
    *,
    commander_context,
    playbook,
    candidate_symbols,
    themes,
    avoid_themes,
    scanner_priority,
    monitor_guidance,
    trade_aggressiveness,
    risk_tone,
    news_query_reasoning,
    monitor_policy,
    exit_policy,
    facade,
):
    selected_playbook = str(playbook or "defensive")
    candidate_hypotheses: List[Dict[str, Any]] = []
    for symbol in list(candidate_symbols or [])[:5]:
        rationale_parts: List[str] = []
        if list(themes):
            rationale_parts.append(f"theme={themes[0]}")
        if list(scanner_priority):
            rationale_parts.append(f"priority={scanner_priority[0]}")
        if str(commander_context.get("scanner_mission") or "").strip():
            rationale_parts.append(str(commander_context.get("scanner_mission") or ""))
        candidate_hypotheses.append(
            {
                "symbol": str(symbol or ""),
                "hypothesis": (
                    f"{selected_playbook} setup candidate"
                    + (f" with {', '.join(rationale_parts[:2])}" if rationale_parts else "")
                ),
                "source": "candidate_symbols_hint",
            }
        )
    symbol_constraints = {
        "candidate_symbols_hint": [str(x) for x in list(candidate_symbols or [])[:8]],
        "preferred_themes": [str(x) for x in list(themes or [])[:5]],
        "avoid_themes": [str(x) for x in list(avoid_themes or [])[:6]],
        "scanner_priority": [str(x) for x in list(scanner_priority or [])[:6]],
        "candidate_limit": int(min(len(list(candidate_symbols or [])), 8)),
    }
    entry_plan = {
        "setup_family": selected_playbook,
        "monitor_guidance": str(monitor_guidance or ""),
        "risk_tone": str(risk_tone or ""),
        "trade_aggressiveness": str(trade_aggressiveness or ""),
        "scanner_priority": [str(x) for x in list(scanner_priority or [])[:4]],
        "scanner_mission": str(commander_context.get("scanner_mission") or ""),
        "confirmation_required": True,
    }
    exit_plan = {
        "monitor_guidance": str(monitor_guidance or ""),
        "monitor_mission": str(commander_context.get("monitor_mission") or ""),
        "position_guards": dict(monitor_policy or {}),
        "adaptive_exit": dict(exit_policy or {}),
    }
    strategy_summary = (
        f"Strategist refined commander context into {selected_playbook} plan "
        f"for {len(list(candidate_symbols or []))} candidate symbols."
    )
    open_position_refresh_context = (
        dict(commander_context.get("open_position_refresh_context") or {})
        if isinstance(commander_context.get("open_position_refresh_context"), dict)
        else {}
    )
    commander_horizon_policy = (
        dict(commander_context.get("commander_horizon_policy") or {})
        if isinstance(commander_context.get("commander_horizon_policy"), dict)
        else {}
    )
    if str(open_position_refresh_context.get("refresh_summary") or "").strip():
        strategy_summary += f" Hold refresh context: {str(open_position_refresh_context.get('refresh_summary') or '').strip()[:220]}"
    if str(news_query_reasoning or "").strip():
        strategy_summary += f" News focus: {str(news_query_reasoning).strip()[:180]}"
    return {
        "selected_playbook": selected_playbook,
        "candidate_hypotheses": candidate_hypotheses,
        "symbol_constraints": symbol_constraints,
        "entry_plan": entry_plan,
        "exit_plan": exit_plan,
        "open_position_refresh_context": dict(open_position_refresh_context),
        "strategy_summary": strategy_summary,
    }


def _augment_strategy_fields_r3_impl(
    *,
    themes,
    avoid_themes,
    scanner_priority,
    report_focus,
    market_context_inputs,
    news_ctx,
    facade,
):
    out_themes = list(themes or [])
    out_avoid = list(avoid_themes or [])
    out_priority = list(scanner_priority or [])
    out_focus = list(report_focus or [])

    macro_risk = facade._to_float(market_context_inputs.get("macro_risk"), 0.0)
    realized_vol = facade._to_float(market_context_inputs.get("realized_volatility"), 0.0)
    fallback_n = int(news_ctx.get("fallback") or 0)
    unavailable_n = int(news_ctx.get("unavailable") or 0)

    if macro_risk >= 0.65 or realized_vol >= 0.045:
        for x in ("liquidity", "risk_penalty", "drawdown_control"):
            if x not in out_priority:
                out_priority.append(x)
        for x in ("high_gap_speculative", "illiquid_microcap"):
            if x not in out_avoid:
                out_avoid.append(x)
        if "guard_blocks" not in out_focus:
            out_focus.append("guard_blocks")

    if (fallback_n + unavailable_n) > 0:
        if "data_quality" not in out_focus:
            out_focus.append("data_quality")
        if "headline_only_momentum" not in out_avoid:
            out_avoid.append("headline_only_momentum")

    if not out_themes:
        out_themes = ["broad_market_leaders"]

    return out_themes[:5], out_avoid[:6], out_priority[:6], out_focus[:6]
