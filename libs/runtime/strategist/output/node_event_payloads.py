"""Strategist: market_context_snapshot event payload.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_market_context_snapshot_payload(global_signal, macro_stress_overlay, market_context_inputs, market_structure, regime_factors, state, *, facade):
    return (
        {
            "market_structure": str(market_structure or ""),
            "market_context_inputs": dict(market_context_inputs),
            "regime_factors": dict(regime_factors),
            "global_signal": {
                "score": facade._round_optional(global_signal.get("score"), 4),
                "status": str(global_signal.get("status") or ""),
                "source": str(global_signal.get("source") or ""),
                "index_moves": dict(global_signal.get("index_moves") or {}),
                "korea_indices": dict(global_signal.get("korea_indices") or {}),
                "macro_moves": dict(global_signal.get("macro_moves") or {}),
                "fear_index": dict(global_signal.get("fear_index") or {}),
            },
            "macro_stress_overlay": dict(macro_stress_overlay),
            "candidate_symbols_hint": list(state.get("candidate_symbols") or [])[:8],
        }
    )

def build_news_evidence_ranked_payload(candidate_news_ctx, market_news_ctx, news_ctx, news_query_targets, ranked_candidate_news, ranked_market_news):
    return (
        {
        "news_query_targets": list(news_query_targets),
        "candidate_news_ranked": ranked_candidate_news,
        "market_news_ranked": ranked_market_news,
        "candidate_news_context": dict(candidate_news_ctx),
        "market_news_context": dict(market_news_ctx),
        "news_context": dict(news_ctx),
    }
    )

def build_strategist_summary_log_payload(avoid_themes, llm_meta, llm_overrides, macro_stress_overlay, market_regime, market_sentiment, monitor_guidance, news_query_reasoning, news_query_targets, playbook, recent_strategy_feedback, regime_score, report_focus, reporter_feedback_packet, risk_tone, scanner_bias, scanner_priority, scanner_source_policy, sentiment_score, state, strategist_llm_block_reason, strategist_llm_blocked, strategist_output, strategist_policy_resolution, strategy_memory_advisory, themes, trade_aggressiveness):
    return (
        {
            "market_regime": market_regime,
            "market_sentiment": market_sentiment,
            "themes": list(themes),
            "avoid_themes": list(avoid_themes),
            "playbook": playbook,
            "scanner_bias": scanner_bias,
            "scanner_priority": list(scanner_priority),
            "scanner_source_policy": dict(scanner_source_policy),
            "trade_aggressiveness": trade_aggressiveness,
            "risk_tone": risk_tone,
            "monitor_guidance": monitor_guidance,
            "candidate_count": len(list(state["candidate_symbols"])),
            "regime_score": float(regime_score),
            "sentiment_score": float(sentiment_score),
            "report_focus": list(report_focus)[:3],
            "macro_stress_overlay": dict(macro_stress_overlay),
            "feedback_window_size": int(recent_strategy_feedback.get("feedback_window_size") or 0),
            "top_recent_strengths": list(recent_strategy_feedback.get("top_recent_strengths") or [])[:3],
            "top_recent_weaknesses": list(recent_strategy_feedback.get("top_recent_weaknesses") or [])[:3],
            "reporter_feedback_available": bool(reporter_feedback_packet.get("available")),
            "reporter_feedback_packet_available": bool(reporter_feedback_packet.get("source_available")),
            "reporter_feedback_status": str(reporter_feedback_packet.get("status") or ""),
            "reporter_feedback_mode": str(reporter_feedback_packet.get("reporter_feedback_mode") or "auto"),
            "reporter_feedback_mode_source": str(reporter_feedback_packet.get("reporter_feedback_mode_source") or "default_auto"),
            "reporter_feedback_gate_reason": str(reporter_feedback_packet.get("feedback_gate_reason") or ""),
            "reporter_feedback_consumed": bool(reporter_feedback_packet.get("consumed")),
            "reporter_feedback_confidence": str(reporter_feedback_packet.get("confidence") or "none"),
            "strategy_memory_status": str(strategy_memory_advisory.get("status") or ""),
            "best_playbooks": list(strategy_memory_advisory.get("best_playbooks") or [])[:3],
            "worst_playbooks": list(strategy_memory_advisory.get("worst_playbooks") or [])[:3],
            "recent_failures": list(strategy_memory_advisory.get("recent_failures") or [])[:3],
            "recent_success_patterns": list(strategy_memory_advisory.get("recent_success_patterns") or [])[:3],
            "recent_playbook_performance": dict(strategy_memory_advisory.get("playbook_performance_snapshot") or {}),
            "news_query_targets": list(news_query_targets)[:6],
            "news_query_reasoning": news_query_reasoning,
            "memory_packet_visibility": dict(strategist_output.get("memory_packet_visibility") or {}),
            "llm_frame_status": str(llm_meta.get("status") or "disabled"),
            "llm_frame_applied": bool(llm_overrides),
            "llm_frame_model": str(llm_meta.get("model") or ""),
            "llm_frame_recovery_method": str(llm_meta.get("recovery_method") or ""),
            "llm_frame_low_confidence": bool(llm_meta.get("repair_used")),
            "llm_frame_blocked": bool(strategist_llm_blocked),
            "llm_frame_blocked_reason": str(strategist_llm_block_reason or ""),
            "strategy_generation_mode": str(strategist_policy_resolution.get("strategy_generation_mode") or ""),
            "fallback_used": bool(strategist_policy_resolution.get("fallback_used")),
            "fallback_source": str(strategist_policy_resolution.get("fallback_source") or ""),
            "effective_policy_source": str(strategist_policy_resolution.get("effective_policy_source") or ""),
        }
    )

def build_strategic_frame_trace_payload(avoid_themes, key_events, llm_meta, llm_overrides, macro_stress_overlay, market_regime, market_sentiment, monitor_guidance, news_query_reasoning, news_query_targets, playbook, recent_strategy_feedback, regime_score, report_focus, reporter_feedback_packet, risk_tone, scanner_bias, scanner_priority, scanner_source_policy, sentiment_score, strategist_output, strategy_memory_advisory, themes, trade_aggressiveness):
    return (
        {
            "market_regime": market_regime,
            "market_sentiment": market_sentiment,
            "themes": list(themes)[:5],
            "avoid_themes": list(avoid_themes)[:5],
            "playbook": playbook,
            "scanner_bias": scanner_bias,
            "scanner_priority": list(scanner_priority)[:5],
            "scanner_source_policy": dict(scanner_source_policy),
            "trade_aggressiveness": trade_aggressiveness,
            "risk_tone": risk_tone,
            "monitor_guidance": monitor_guidance,
            "report_focus": list(report_focus)[:5],
            "macro_stress_overlay": dict(macro_stress_overlay),
            "feedback_window_size": int(recent_strategy_feedback.get("feedback_window_size") or 0),
            "top_recent_strengths": list(recent_strategy_feedback.get("top_recent_strengths") or [])[:3],
            "top_recent_weaknesses": list(recent_strategy_feedback.get("top_recent_weaknesses") or [])[:3],
            "recent_reporter_summary": list(recent_strategy_feedback.get("recent_reporter_summary") or [])[:2],
            "reporter_feedback_available": bool(reporter_feedback_packet.get("available")),
            "reporter_feedback_packet_available": bool(reporter_feedback_packet.get("source_available")),
            "reporter_feedback_status": str(reporter_feedback_packet.get("status") or ""),
            "reporter_feedback_mode": str(reporter_feedback_packet.get("reporter_feedback_mode") or "auto"),
            "reporter_feedback_mode_source": str(reporter_feedback_packet.get("reporter_feedback_mode_source") or "default_auto"),
            "reporter_feedback_gate_reason": str(reporter_feedback_packet.get("feedback_gate_reason") or ""),
            "reporter_feedback_consumed": bool(reporter_feedback_packet.get("consumed")),
            "reporter_feedback_confidence": str(reporter_feedback_packet.get("confidence") or "none"),
            "reporter_feedback_insight_summary": str(reporter_feedback_packet.get("insight_summary") or ""),
            "strategy_memory_status": str(strategy_memory_advisory.get("status") or ""),
            "best_playbooks": list(strategy_memory_advisory.get("best_playbooks") or [])[:3],
            "worst_playbooks": list(strategy_memory_advisory.get("worst_playbooks") or [])[:3],
            "recent_failures": list(strategy_memory_advisory.get("recent_failures") or [])[:3],
            "recent_success_patterns": list(strategy_memory_advisory.get("recent_success_patterns") or [])[:3],
            "recent_playbook_performance": dict(strategy_memory_advisory.get("playbook_performance_snapshot") or {}),
            "news_query_targets": list(news_query_targets)[:6],
            "news_query_reasoning": news_query_reasoning,
            "memory_packet_visibility": dict(strategist_output.get("memory_packet_visibility") or {}),
            "regime_score": float(regime_score),
            "sentiment_score": float(sentiment_score),
            "key_events": list(key_events)[:3],
            "llm_frame_status": str(llm_meta.get("status") or "disabled"),
            "llm_frame_applied": bool(llm_overrides),
            "llm_frame_model": str(llm_meta.get("model") or ""),
            "llm_frame_low_confidence": bool(llm_meta.get("repair_used")),
        }
    )

def build_strategist_decision_bridge_output(avoid_themes, macro_stress_overlay, market_regime, market_sentiment, monitor_guidance, news_query_reasoning, news_query_targets, playbook, recent_strategy_feedback, report_focus, reporter_feedback_packet, risk_tone, scanner_bias, scanner_priority, scanner_source_policy, state, strategist_output, strategy_memory_advisory, themes, trade_aggressiveness):
    return (
        {
                "market_regime": market_regime,
                "market_sentiment": market_sentiment,
                "themes": list(themes),
                "avoid_themes": list(avoid_themes),
                "playbook": playbook,
                "scanner_bias": scanner_bias,
                "scanner_priority": list(scanner_priority),
                "scanner_source_policy": dict(scanner_source_policy),
                "trade_aggressiveness": trade_aggressiveness,
                "risk_tone": risk_tone,
                "monitor_guidance": monitor_guidance,
                "report_focus": list(report_focus),
                "macro_stress_overlay": dict(macro_stress_overlay),
                "recent_strategy_feedback": {
                    "feedback_window_size": int(recent_strategy_feedback.get("feedback_window_size") or 0),
                    "top_recent_strengths": list(recent_strategy_feedback.get("top_recent_strengths") or [])[:3],
                    "top_recent_weaknesses": list(recent_strategy_feedback.get("top_recent_weaknesses") or [])[:3],
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
                "strategy_memory": {
                    "status": str(strategy_memory_advisory.get("status") or ""),
                    "best_playbooks": list(strategy_memory_advisory.get("best_playbooks") or [])[:3],
                    "worst_playbooks": list(strategy_memory_advisory.get("worst_playbooks") or [])[:3],
                    "recent_failures": list(strategy_memory_advisory.get("recent_failures") or [])[:3],
                    "recent_success_patterns": list(strategy_memory_advisory.get("recent_success_patterns") or [])[:3],
                    "recent_playbook_performance": dict(strategy_memory_advisory.get("playbook_performance_snapshot") or {}),
                },
                "memory_packet_visibility": dict(strategist_output.get("memory_packet_visibility") or {}),
                "news_query_targets": list(news_query_targets),
                "news_query_reasoning": news_query_reasoning,
                "candidate_symbols": list(state.get("candidate_symbols") or []),
            }
    )
