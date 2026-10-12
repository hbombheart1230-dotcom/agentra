"""Strategist explanation/trace projections (emit and artifact writes stay in the node).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/strategist_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def strat_trace_ranked_candidate_news_ranked_market_news(market_news_items_by_target, market_news_signal_map, news_query_targets, news_items_by_symbol, news_signal_map, state, market_regime, playbook, themes, avoid_themes, monitor_guidance, news_query_reasoning, macro_stress_overlay, *, facade):
    ranked_market_news = facade._rank_news_evidence_rows(
        market_news_items_by_target,
        market_news_signal_map,
        used_targets=list(news_query_targets),
        scope="market",
        max_rows=6,
    )
    ranked_candidate_news = facade._rank_news_evidence_rows(
        news_items_by_symbol,
        news_signal_map,
        used_targets=list(state.get("candidate_symbols") or []),
        scope="candidate",
        max_rows=6,
    )
    reason_chain: facade.List[str] = []
    if str(market_regime or "").strip():
        reason_chain.append(f"Market regime classified as {market_regime}.")
    if str(playbook or "").strip():
        reason_chain.append(f"Playbook set to {playbook}.")
    if list(themes):
        reason_chain.append(f"Themes prioritized: {', '.join(list(themes)[:4])}.")
    if list(avoid_themes):
        reason_chain.append(f"Avoid themes: {', '.join(list(avoid_themes)[:4])}.")
    if str(monitor_guidance or "").strip():
        reason_chain.append(f"Monitor guidance set to {monitor_guidance}.")
    if str(news_query_reasoning or "").strip():
        reason_chain.append(f"News query reasoning: {news_query_reasoning}.")
    if bool(macro_stress_overlay.get("active")) or list(macro_stress_overlay.get("stress_flags") or []):
        reason_chain.append(
            "Macro stress overlay active: "
            + ", ".join([str(x or "") for x in list(macro_stress_overlay.get("stress_flags") or []) if str(x or "").strip()] or ["elevated_stress"])
            + "."
        )
    return (ranked_candidate_news, ranked_market_news, reason_chain)


def strat_trace_decision_frame_payload(market_regime, market_sentiment, playbook, scanner_bias, trade_aggressiveness, risk_tone, monitor_guidance, reason_chain, themes, avoid_themes, scanner_priority, scanner_source_policy, report_focus, commander_horizon_policy, horizon_context, reporter_feedback_packet, strategist_output, strategy_memory_advisory, strategy_policy, theme_strength_packet, *, facade):
    decision_frame_payload = {
        "market_regime": market_regime,
        "market_sentiment": market_sentiment,
        "playbook": playbook,
        "themes": list(themes),
        "avoid_themes": list(avoid_themes),
        "scanner_bias": scanner_bias,
        "scanner_priority": list(scanner_priority),
        "scanner_source_policy": dict(scanner_source_policy),
        "trade_aggressiveness": trade_aggressiveness,
        "risk_tone": risk_tone,
        "monitor_guidance": monitor_guidance,
        "report_focus": list(report_focus),
        "strategy_memory": {
            "status": str(strategy_memory_advisory.get("status") or ""),
            "best_playbooks": list(strategy_memory_advisory.get("best_playbooks") or [])[:3],
            "worst_playbooks": list(strategy_memory_advisory.get("worst_playbooks") or [])[:3],
            "recent_failures": list(strategy_memory_advisory.get("recent_failures") or [])[:3],
            "recent_success_patterns": list(strategy_memory_advisory.get("recent_success_patterns") or [])[:3],
            "recent_playbook_performance": dict(strategy_memory_advisory.get("playbook_performance_snapshot") or {}),
        },
        "reporter_feedback_packet": {
            "available": bool(reporter_feedback_packet.get("available")),
            "status": str(reporter_feedback_packet.get("status") or ""),
            "reporter_feedback_mode": str(reporter_feedback_packet.get("reporter_feedback_mode") or "auto"),
            "reporter_feedback_mode_source": str(reporter_feedback_packet.get("reporter_feedback_mode_source") or "default_auto"),
            "consumed": bool(reporter_feedback_packet.get("consumed")),
            "feedback_gate_reason": str(reporter_feedback_packet.get("feedback_gate_reason") or ""),
            "confidence": str(reporter_feedback_packet.get("confidence") or "none"),
            "insight_summary": str(reporter_feedback_packet.get("insight_summary") or ""),
            "recommendation": list(reporter_feedback_packet.get("recommendation") or [])[:3],
            "route_analysis": dict((reporter_feedback_packet.get("route_analysis") or {})),
        },
        "reason_chain": reason_chain,
        "strategy_policy_summary": {
            "market_policy": dict(strategy_policy.get("market_policy") or {}),
            "scanner_policy": {
                "candidate_sources": dict((strategy_policy.get("scanner_policy") or {}).get("candidate_sources") or {}),
                "filters": dict((strategy_policy.get("scanner_policy") or {}).get("filters") or {}),
            },
            "monitor_policy": dict(strategy_policy.get("monitor_policy") or {}),
            "commander_horizon_policy": dict(commander_horizon_policy),
            "horizon_context": dict(horizon_context),
        },
        "strategy_thesis": dict(strategist_output.get("strategy_thesis") or {}),
        "strategy_refresh_trace": dict(strategist_output.get("strategy_refresh_trace") or {}),
        "memory_usage_trace": dict(strategist_output.get("memory_usage_trace") or {}),
        "news_usage_trace": dict(strategist_output.get("news_usage_trace") or {}),
        "theme_strength_packet": {
            "source": str(theme_strength_packet.get("source") or ""),
            "status": str(theme_strength_packet.get("status") or ""),
            "reason": str(theme_strength_packet.get("reason") or ""),
            "top_themes": list(theme_strength_packet.get("top_themes") or [])[:5],
            "theme_scores": dict(theme_strength_packet.get("theme_scores") or {}),
        },
        "scanner_handoff": dict(strategist_output.get("scanner_handoff") or {}),
        "monitor_handoff": dict(strategist_output.get("monitor_handoff") or {}),
        "conflict_analysis": dict(strategist_output.get("conflict_analysis") or {}),
        "trade_permission_frame": dict(strategist_output.get("trade_permission_frame") or {}),
        "responsibility_boundary": dict(strategist_output.get("responsibility_boundary") or {}),
    }
    return (decision_frame_payload,)
