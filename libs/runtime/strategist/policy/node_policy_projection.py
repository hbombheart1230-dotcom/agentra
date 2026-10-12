"""Strategist bounded-override, monitor entry/exit policy and theme/strategy plan projections (after the LLM boundary; frame application order unchanged).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/strategist_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def strat_policy_exit_policy_monitor_entry_policy(ai_overrides, monitor_policy, state, policy, monitor_guidance, trade_aggressiveness, risk_tone, playbook, market_regime, scanner_bias, exit_policy, *, facade):
    policy_confidence = None
    try:
        if ai_overrides.get("confidence") not in (None, ""):
            policy_confidence = min(max(float(ai_overrides.get("confidence")), 0.0), 1.0)
    except Exception:
        policy_confidence = None
    policy_source = str(ai_overrides.get("policy_source") or "strategist").strip() or "strategist"
    monitor_policy_override = ai_overrides.get("monitor_policy")
    if isinstance(monitor_policy_override, dict):
        monitor_policy = {**monitor_policy, **dict(monitor_policy_override)}
    else:
        monitor_policy = facade._monitor_policy(
            state=state,
            policy=policy,
            monitor_guidance=monitor_guidance,
            trade_aggressiveness=trade_aggressiveness,
            risk_tone=risk_tone,
        )
    monitor_entry_policy_seed = facade._build_strategist_monitor_entry_policy_seed(
        playbook=playbook,
        market_regime=market_regime,
        monitor_guidance=monitor_guidance,
        risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness,
    )
    monitor_entry_policy_input = (
        dict(ai_overrides.get("monitor_entry_policy") or {})
        if isinstance(ai_overrides.get("monitor_entry_policy"), dict)
        else dict(monitor_entry_policy_seed)
    )
    monitor_entry_policy_obj, monitor_entry_policy_validation = facade.normalize_monitor_entry_policy(
        monitor_entry_policy_input,
        fallback_policy=facade.MonitorEntryPolicy.from_mapping(monitor_entry_policy_seed),
        policy_source=policy_source,
    )
    monitor_entry_policy = facade.build_monitor_entry_policy_bundle(
        threshold_policy=monitor_entry_policy_obj,
        playbook=playbook,
        monitor_guidance=monitor_guidance,
        risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness,
        interpretation_policy=(
            dict(monitor_entry_policy_input.get("interpretation_policy") or {})
            if isinstance(monitor_entry_policy_input.get("interpretation_policy"), dict)
            else None
        ),
    )
    scanner_bias_context_input = {}
    if isinstance(ai_overrides.get("scanner_bias_context"), dict):
        scanner_bias_context_input = dict(ai_overrides.get("scanner_bias_context") or {})
    elif isinstance(ai_overrides.get("scanner_bias"), dict):
        scanner_bias_context_input = dict(ai_overrides.get("scanner_bias") or {})
    scanner_bias_context_seed = facade._build_scanner_bias_context_seed(
        playbook=playbook,
        scanner_bias=scanner_bias,
        monitor_entry_policy=monitor_entry_policy,
    )
    scanner_bias_context_obj, scanner_bias_context_validation = facade.normalize_scanner_bias_context(
        scanner_bias_context_input or scanner_bias_context_seed,
        bias_source="strategist",
    )
    scanner_bias_context = scanner_bias_context_obj.to_dict()
    exit_policy_override = ai_overrides.get("exit_policy")
    if isinstance(exit_policy_override, dict):
        exit_policy = {**exit_policy, **dict(exit_policy_override)}
    else:
        exit_policy = facade._exit_policy(
            playbook=playbook,
            monitor_guidance=monitor_guidance,
            trade_aggressiveness=trade_aggressiveness,
            risk_tone=risk_tone,
        )
    return (exit_policy, monitor_entry_policy, monitor_entry_policy_validation, monitor_policy, policy_confidence, policy_source, scanner_bias_context, scanner_bias_context_validation)


def strat_policy_candidate_watch_policy_rejected_strategy(playbook, ai_overrides, market_regime, market_sentiment, market_structure, market_context_inputs, risk_tone, trade_aggressiveness, *, facade):
    tactical_strategy = facade._normalize_tactical_strategy(ai_overrides.get("tactical_strategy"), playbook=playbook)
    tactical_subtype = facade._normalize_tactical_subtype(
        ai_overrides.get("tactical_subtype"),
        tactical_strategy=tactical_strategy,
    )
    strategy_scores = facade._normalize_strategy_scores(
        ai_overrides.get("strategy_scores"),
        playbook=playbook,
        market_regime=market_regime,
        market_sentiment=market_sentiment,
        market_structure=market_structure,
        market_context_inputs=market_context_inputs,
    )
    rejected_strategy_reasons = facade._normalize_rejected_strategy_reasons(
        ai_overrides.get("rejected_strategy_reasons"),
        tactical_strategy=tactical_strategy,
        strategy_scores=strategy_scores,
    )
    candidate_watch_policy = facade._normalize_candidate_watch_policy(
        ai_overrides.get("candidate_watch_policy"),
        tactical_strategy=tactical_strategy,
        playbook=playbook,
        market_regime=market_regime,
        risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness,
    )
    return (candidate_watch_policy, rejected_strategy_reasons, strategy_scores, tactical_strategy, tactical_subtype)


def strat_policy_commander_context_policy_adjustment(state, market_regime, playbook, market_sentiment, key_events, themes, avoid_themes, scanner_bias, scanner_priority, trade_aggressiveness, risk_tone, monitor_guidance, report_focus, recent_strategy_feedback, strategy_memory_advisory, reports_root, read_model_facts, news_query_reasoning, monitor_policy, exit_policy, ai_overrides, monitor_entry_policy_validation, monitor_entry_policy, *, facade):
    commander_context = facade._build_commander_context_summary(
        state=state,
        commander_decision=state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {},
        runtime_phase=str(state.get("runtime_phase") or "session"),
        market_regime=market_regime,
        playbook=playbook,
    )
    strategic_answers = facade._build_strategic_answers(
        commander_context=commander_context,
        market_regime=market_regime,
        market_sentiment=market_sentiment,
        key_events=key_events,
        themes=themes,
        avoid_themes=avoid_themes,
        playbook=playbook,
        scanner_bias=scanner_bias,
        scanner_priority=scanner_priority,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
        monitor_guidance=monitor_guidance,
        report_focus=report_focus,
        recent_strategy_feedback=recent_strategy_feedback,
        strategy_memory=strategy_memory_advisory,
        read_model_facts=dict(read_model_facts),
        reports_root=reports_root,
    )
    strategist_plan = facade._build_strategist_plan(
        commander_context=commander_context,
        playbook=playbook,
        candidate_symbols=[str(x.get("symbol") or "") for x in list(state.get("candidates") or []) if isinstance(x, dict)]
        or [str(x) for x in list(state.get("candidate_symbols") or []) if str(x or "").strip()],
        themes=list(themes),
        avoid_themes=list(avoid_themes),
        scanner_priority=list(scanner_priority),
        monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
        news_query_reasoning=news_query_reasoning,
        monitor_policy=dict(monitor_policy),
        exit_policy=dict(exit_policy),
    )
    policy_rationale = str(
        ai_overrides.get("policy_rationale")
        or facade._build_monitor_entry_policy_rationale(
            playbook=playbook,
            market_regime=market_regime,
            market_sentiment=market_sentiment,
            monitor_guidance=monitor_guidance,
            risk_tone=risk_tone,
            trade_aggressiveness=trade_aggressiveness,
            validation_meta=monitor_entry_policy_validation,
        )
    ).strip()
    baseline_policy_summary = (
        dict((commander_context.get("strategist_refresh_context") or {}).get("current_monitor_entry_policy_summary") or {})
        if isinstance((commander_context.get("strategist_refresh_context") or {}).get("current_monitor_entry_policy_summary"), dict)
        else {}
    )
    if not baseline_policy_summary:
        baseline_policy_summary = facade._summarize_monitor_entry_policy_for_adjustment(
            facade.build_default_monitor_entry_policy().to_dict()
        )
    current_policy_summary = facade._summarize_monitor_entry_policy_for_adjustment(monitor_entry_policy)
    policy_adjustment = facade._normalize_policy_adjustment_surface(
        raw_adjustment=ai_overrides.get("policy_adjustment"),
        baseline_summary=baseline_policy_summary,
        current_summary=current_policy_summary,
        refresh_requested=bool(commander_context.get("strategist_refresh_requested")),
        recent_strategy_feedback=recent_strategy_feedback,
    )
    strategy_adjustment_directives = facade._normalize_strategy_adjustment_directives(
        raw_directives=ai_overrides.get("strategy_adjustment_directives"),
        playbook=playbook,
        policy_adjustment=policy_adjustment,
        commander_context=commander_context,
        strategy_memory=strategy_memory_advisory,
        selected_symbol_memory=dict(
            ((strategic_answers.get("q15_commander_refresh_context") or {}).get("selected_symbol_memory") or {})
        ),
    )
    return (commander_context, policy_adjustment, policy_rationale, strategic_answers, strategist_plan, strategy_adjustment_directives)


def strat_policy_commander_context_commander_horizon_poli(ai_overrides, playbook, monitor_guidance, trade_aggressiveness, risk_tone, policy_source, commander_context, state, *, facade):
    if isinstance(ai_overrides.get("strategy_horizon_feedback"), dict):
        strategy_horizon_input = dict(ai_overrides.get("strategy_horizon_feedback") or {})
    else:
        strategy_horizon_input = {
            "strategy_horizon": ai_overrides.get("strategy_horizon"),
            "expected_hold_window": (
                dict(ai_overrides.get("expected_hold_window") or {})
                if isinstance(ai_overrides.get("expected_hold_window"), dict)
                else {}
            ),
            "exit_guidance": (
                dict(ai_overrides.get("exit_guidance") or {})
                if isinstance(ai_overrides.get("exit_guidance"), dict)
                else {}
            ),
            "invalidation_conditions": ai_overrides.get("invalidation_conditions"),
            "monitor_handoff": (
                dict(ai_overrides.get("monitor_handoff") or {})
                if isinstance(ai_overrides.get("monitor_handoff"), dict)
                else {}
            ),
        }
    strategy_horizon_feedback = facade.build_strategy_horizon_feedback(
        strategy_horizon_input,
        playbook=playbook,
        monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
        source=policy_source,
    )
    strategist_horizon_proposal = dict(strategy_horizon_feedback)
    commander_horizon_policy = facade.build_commander_horizon_policy(
        strategist_horizon_proposal,
        commander_context=commander_context,
        memory_packets=commander_context.get("memory_packets") if isinstance(commander_context.get("memory_packets"), dict) else {},
        runtime_phase=str(state.get("runtime_phase") or commander_context.get("session_bias") or ""),
        live_validation_mode=True,
        source="strategist_node_commander_context",
    )
    horizon_context = facade.build_horizon_context(commander_horizon_policy)
    commander_context = dict(commander_context)
    strategist_refresh_context = (
        dict(commander_context.get("strategist_refresh_context") or {})
        if isinstance(commander_context.get("strategist_refresh_context"), dict)
        else {}
    )
    strategist_refresh_context["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_refresh_context["horizon_context"] = dict(horizon_context)
    return (commander_context, commander_horizon_policy, horizon_context, strategist_horizon_proposal, strategist_refresh_context, strategy_horizon_feedback)
