"""Strategist: frame LLM input payload, news event intelligence and input quality context.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class FrameLlmPayload(NamedTuple):
    """Result of `assemble_frame_llm_payload` (positional order = sorted output names)."""

    llm_payload: Any
    news_event_intelligence: Any
    strategist_input_quality: Any

def assemble_frame_llm_payload(available_themes, candidate_symbols, fallback_theme_hints, global_signal, key_events, macro_stress_overlay, market_context_inputs, market_news_items_by_target, market_news_signal_map, market_regime, market_sentiment, market_structure, news_collection_policy, news_ctx, news_items_by_symbol, news_query_targets, news_signal_map, playbook, pre_llm_commander_context, read_model_facts, recent_strategy_feedback, reporter_feedback_packet, reports_root, selected_themes_hint, strategy_memory_advisory, theme_strength, theme_strength_packet, themes, *, facade):
    llm_payload = {
        "global_sentiment_signal": dict(global_signal),
        "news_context": dict(news_ctx),
        "market_context_inputs": dict(market_context_inputs),
        "recent_strategy_feedback": dict(recent_strategy_feedback),
        "reporter_feedback_packet": dict(reporter_feedback_packet),
        "strategy_memory": dict(strategy_memory_advisory),
        "memory_packets": dict(pre_llm_commander_context.get("memory_packets") or {}),
        "commander_memory_policy": dict(pre_llm_commander_context.get("commander_memory_policy") or {}),
        "scanner_memory_bias": dict(pre_llm_commander_context.get("scanner_memory_bias") or {}),
        "monitor_memory_bias": dict(pre_llm_commander_context.get("monitor_memory_bias") or {}),
        "macro_stress_overlay_hint": dict(macro_stress_overlay),
        "market_regime_hint": market_regime,
        "market_sentiment_hint": market_sentiment,
        "commander_refresh_context": facade._build_llm_commander_refresh_context(
            pre_llm_commander_context,
            read_model_facts,
            reports_root,
        ),
        "read_model_facts": dict(read_model_facts),
        "market_structure_hint": market_structure,
        "playbook_hint": playbook,
        "monitor_entry_policy_baseline": facade.build_default_monitor_entry_policy().to_dict(),
        "theme_strength": dict(theme_strength),
        "theme_strength_packet": dict(theme_strength_packet),
        "available_themes": list(available_themes),
        "themes_hint": list(themes),
        "selected_themes_hint": list(selected_themes_hint),
        "fallback_theme_hints": list(fallback_theme_hints),
        "news_collection_policy": dict(news_collection_policy),
        "news_query_targets": list(news_query_targets),
        "news_sentiment_signal": dict(news_signal_map),
        "market_news_sentiment_signal": dict(market_news_signal_map),
        "reports_root": str(reports_root),
        "market_news_sample": facade._sample_news_for_evidence(
            market_news_items_by_target,
            max_symbols=6,
            max_items_per_symbol=2,
        ),
        "candidate_news_sample": facade._sample_news_for_evidence(
            news_items_by_symbol,
            max_symbols=6,
            max_items_per_symbol=2,
        ),
        "candidate_symbols_hint": list(candidate_symbols)[:10],
        "key_events_hint": list(key_events),
        "recent_monitor_blockers_hint": list(recent_strategy_feedback.get("recent_monitor_issues") or [])[:5],
    }
    news_event_intelligence = facade.build_news_event_intelligence(
        market_news_sample=llm_payload.get("market_news_sample"),
        candidate_news_sample=llm_payload.get("candidate_news_sample"),
        news_query_targets=news_query_targets,
        theme_strength=theme_strength,
        available_themes=available_themes,
        candidate_symbols=candidate_symbols,
    )
    llm_payload["news_event_intelligence"] = dict(news_event_intelligence)
    strategist_input_quality = facade.build_strategist_input_quality_context(llm_payload)
    llm_payload["market_regime_rail"] = dict(strategist_input_quality.get("market_regime_rail") or {})
    llm_payload["news_quality"] = dict(strategist_input_quality.get("news_quality") or {})
    llm_payload["risk_off_exception_policy"] = dict(strategist_input_quality.get("risk_off_exception_policy") or {})
    llm_payload["strategist_input_quality"] = dict(strategist_input_quality)
    return FrameLlmPayload(llm_payload, news_event_intelligence, strategist_input_quality)

def build_theme_selection_raw_input(available_themes, candidate_news_sample, candidate_symbols, global_signal, llm_payload, market_context_inputs, market_news_sample, market_regime, market_sentiment, market_structure, news_collection_policy, news_event_intelligence, news_query_reasoning, news_query_targets, recent_strategy_feedback, reporter_feedback_packet, strategy_memory_advisory, theme_strength_packet, *, facade):
    return (
        {
                "collected_news": facade._merge_news_samples(market_news_sample, candidate_news_sample),
                "collected_market_news": market_news_sample,
                "collected_candidate_news": candidate_news_sample,
                "news_event_intelligence": dict(news_event_intelligence),
                "news_query_targets": list(news_query_targets),
                "news_collection_policy": dict(news_collection_policy),
                "global_sentiment_inputs": dict(global_signal),
                "macro_indicators": dict(market_context_inputs),
                "market_summary": {
                    "market_regime_hint": market_regime,
                    "market_sentiment_hint": market_sentiment,
                    "market_structure_hint": market_structure,
                    "news_query_targets": list(news_query_targets),
                    "news_query_reasoning": news_query_reasoning,
                    "candidate_symbols_hint": list(candidate_symbols)[:10],
                },
                "recent_strategy_feedback": dict(recent_strategy_feedback),
                "reporter_feedback_packet": dict(reporter_feedback_packet),
                "strategy_memory": dict(strategy_memory_advisory),
                "theme_strength_packet": dict(theme_strength_packet),
                "available_themes": list(available_themes),
                "llm_payload": dict(llm_payload),
            }
    )
