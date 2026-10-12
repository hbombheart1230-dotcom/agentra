"""Strategist deterministic candidate/theme/news/policy seed projections (provider reads and state writes stay in the node).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/strategist_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def strat_ctx_candidates_universe_candidates(state, k, policy, *, facade):
    candidates = facade._candidates_from_state(state, k)
    universe_candidates: facade.List[facade.Dict[str, facade.Any]] = []

    if not candidates:
        if bool(policy.get("use_universe_builder", True)):
            universe_candidates = facade.build_candidate_universe(state=state, policy=policy, topk=k)
            if universe_candidates:
                candidates = [
                    {
                        "symbol": str(r.get("symbol") or ""),
                        "why": str(r.get("why") or "universe_builder"),
                        "sources": list(r.get("sources") or []),
                        "universe_score": float(r.get("score") or 0.0),
                        "source_scores": dict(r.get("source_scores") or {}),
                        "source_count": int(r.get("source_count") or len(list(r.get("sources") or []))),
                    }
                    for r in universe_candidates
                    if str(r.get("symbol") or "").strip()
                ]
    return (candidates, universe_candidates)


def strat_ctx_news_collection_policy_news_collection_s(state, theme_news_symbol_limit, available_themes, theme_hints, symbols, news_collection_limit, news_query_targets, policy, *, facade):
    theme_news_symbols = facade._theme_component_symbols_for_news(
        state=state,
        available_themes=list(available_themes),
        theme_hints=list(theme_hints),
        limit=theme_news_symbol_limit,
    )
    news_collection_symbols = facade._merge_news_collection_symbols(
        base_symbols=list(symbols),
        theme_symbols=list(theme_news_symbols),
        limit=max(len(list(symbols or [])), news_collection_limit),
    )
    news_collection_policy = {
        "provider": str(policy.get("news_provider") or "naver"),
        "market_query_targets": list(news_query_targets),
        "candidate_symbols_requested": list(symbols),
        "theme_component_symbols_requested": list(theme_news_symbols),
        "collection_symbols": list(news_collection_symbols),
        "post_scanner_requery": False,
        "reuse_policy": "reuse_pre_scanner_news_pool",
    }
    return (news_collection_policy, news_collection_symbols, theme_news_symbols)


def strat_ctx_avoid_themes_exit_policy(state, gs, market_context_inputs, market_regime, market_sentiment, policy, *, facade):
    market_structure, regime_factors = facade._market_structure_label(
        state=state,
        global_score=gs,
        market_context_inputs=market_context_inputs,
    )
    playbook = facade._pick_playbook(
        market_structure=market_structure,
        market_regime=market_regime,
        market_sentiment=market_sentiment,
    )
    scanner_priority = facade._scanner_priority(playbook, market_regime)
    scanner_bias = facade._scanner_bias(playbook=playbook, market_regime=market_regime)
    avoid_themes = facade._avoid_themes(market_sentiment=market_sentiment, playbook=playbook)
    trade_aggressiveness = facade._trade_aggressiveness(market_regime=market_regime, market_structure=market_structure)
    risk_tone = facade._risk_tone(trade_aggressiveness)
    monitor_guidance = facade._monitor_guidance(market_regime=market_regime, playbook=playbook)
    pre_llm_market_regime = str(market_regime or "")
    pre_llm_market_sentiment = str(market_sentiment or "")
    pre_llm_market_structure = str(market_structure or "")
    pre_llm_playbook = str(playbook or "")
    pre_llm_monitor_guidance = str(monitor_guidance or "")
    pre_llm_risk_tone = str(risk_tone or "")
    pre_llm_trade_aggressiveness = str(trade_aggressiveness or "")
    monitor_policy = facade._monitor_policy(
        state=state,
        policy=policy,
        monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
    )
    exit_policy = facade._exit_policy(
        playbook=playbook,
        monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
    )
    return (avoid_themes, exit_policy, market_structure, monitor_guidance, monitor_policy, playbook, pre_llm_market_regime, pre_llm_market_sentiment, pre_llm_market_structure, pre_llm_monitor_guidance, pre_llm_playbook, pre_llm_risk_tone, pre_llm_trade_aggressiveness, regime_factors, risk_tone, scanner_bias, scanner_priority, trade_aggressiveness)


def strat_ctx_fallback_theme_hints_pre_llm_commander_c(state, market_regime, playbook, available_themes, themes, *, facade):
    pre_llm_commander_context = facade._build_commander_context_summary(
        state=state,
        commander_decision=state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {},
        runtime_phase=str(state.get("runtime_phase") or "session"),
        market_regime=market_regime,
        playbook=playbook,
    )

    selected_themes_hint = (
        [
            str(x or "")
            for x in list(facade._resolve_selected_themes_from_api(
                available_themes=list(available_themes),
                themes=list(themes),
                raw_selected=[],
            ))
            if str(x or "").strip()
        ]
        if available_themes
        else []
    )
    fallback_theme_hints = [str(x or "") for x in list(themes) if str(x or "").strip()] if not available_themes else []
    return (fallback_theme_hints, pre_llm_commander_context, selected_themes_hint)
