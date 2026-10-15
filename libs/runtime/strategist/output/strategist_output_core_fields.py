"""Strategist: core strategist_output fields (policy, news, theme, memory, plan, horizon).

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations


def fill_strategist_output_core(ai_overrides, available_themes, candidate_news_ctx, candidate_watch_policy, commander_horizon_policy, compact_reporter_feedback, exit_policy, global_signal, horizon_context, llm_requested_playbook, macro_stress_overlay, market_context_inputs, market_news_ctx, market_regime_summary, market_structure, monitor_entry_policy, monitor_policy, news_collection_policy, news_ctx, news_event_intelligence, news_query_reasoning, news_query_targets, performance_summary, playbook, policy_adjustment, policy_provenance, policy_rationale, pre_llm_market_regime, pre_llm_market_sentiment, pre_llm_market_structure, pre_llm_monitor_guidance, pre_llm_playbook, pre_llm_risk_tone, pre_llm_trade_aggressiveness, recent_strategy_feedback, regime_score, rejected_strategy_reasons, reporter_feedback_packet, requested_playbook, requested_playbook_source, scanner_bias_context, scanner_bias_context_validation, selected_themes, sentiment_score, strategist_feedback, strategist_horizon_proposal, strategist_input_quality, strategist_output, strategist_plan, strategy_adjustment_directives, strategy_horizon_feedback, strategy_memory_advisory, strategy_scores, tactical_strategy, tactical_subtype, theme_hints, theme_strategy, theme_strength, theme_strength_packet, themes, *, facade):
    strategist_output["monitor_policy"] = dict(monitor_policy)
    strategist_output["exit_policy"] = dict(exit_policy)
    strategist_output["macro_stress_overlay"] = dict(macro_stress_overlay)
    strategist_output["market_structure"] = market_structure
    strategist_output["regime_score"] = float(regime_score)
    strategist_output["sentiment_score"] = float(sentiment_score)
    strategist_output["news_context"] = dict(news_ctx)
    strategist_output["candidate_news_context"] = dict(candidate_news_ctx)
    strategist_output["market_news_context"] = dict(market_news_ctx)
    strategist_output["news_query_targets"] = list(news_query_targets)
    strategist_output["news_collection_policy"] = dict(news_collection_policy)
    strategist_output["news_query_reasoning"] = news_query_reasoning
    strategist_output["news_event_intelligence"] = dict(news_event_intelligence)
    strategist_output["news_event_intelligence_usage"] = (
        dict(ai_overrides.get("news_event_intelligence_usage") or {})
        if isinstance(ai_overrides.get("news_event_intelligence_usage"), dict)
        else {"status": "insufficient", "observation_only": True, "reason": "llm_usage_not_reported"}
    )
    strategist_output["market_regime_rail"] = str(
        ai_overrides.get("market_regime_rail")
        or (strategist_input_quality.get("market_regime_rail") or {}).get("market_regime_rail")
        or ""
    )
    strategist_output["news_quality"] = (
        dict(ai_overrides.get("news_quality") or {})
        if isinstance(ai_overrides.get("news_quality"), dict)
        else dict(strategist_input_quality.get("news_quality") or {})
    )
    strategist_output["risk_off_exception_policy"] = dict(
        strategist_input_quality.get("risk_off_exception_policy") or {}
    )
    strategist_output["risk_off_exception_conditions"] = list(
        ai_overrides.get("risk_off_exception_conditions")
        or (strategist_input_quality.get("risk_off_exception_policy") or {}).get("allowed_exception_conditions")
        or []
    )
    strategist_output["strategist_input_quality"] = dict(strategist_input_quality)
    strategist_output["global_sentiment_signal"] = dict(global_signal)
    strategist_output["korea_indices"] = dict(global_signal.get("korea_indices") or {})
    strategist_output["market_context_inputs"] = dict(market_context_inputs)
    strategist_output["theme_strength"] = dict(theme_strength)
    strategist_output["theme_strength_packet"] = dict(theme_strength_packet)
    strategist_output["available_themes"] = list(available_themes)
    strategist_output["selected_themes"] = list(selected_themes)
    strategist_output["theme_strategy"] = dict(theme_strategy)
    strategist_output["theme_source"] = str(theme_strength_packet.get("source") or "")
    strategist_output["theme_source_status"] = str(theme_strength_packet.get("status") or "")
    strategist_output["theme_source_reason"] = str(theme_strength_packet.get("reason") or "")
    strategist_output["theme_source_fallback_used"] = bool(theme_strength_packet.get("fallback_used"))
    strategist_output["theme_fallback_used"] = bool(
        not theme_hints
        and any(str(theme or "").strip().lower() == "broad_market_leaders" for theme in list(themes or []))
    )
    strategist_output["recent_strategy_feedback"] = dict(recent_strategy_feedback)
    strategist_output["strategy_memory"] = dict(strategy_memory_advisory)
    strategist_output["strategy_memory_snapshot"] = dict(strategy_memory_advisory)
    strategist_output["strategist_feedback"] = dict(strategist_feedback)
    strategist_output["reporter_feedback_packet"] = dict(reporter_feedback_packet)
    strategist_output["reporter_feedback_summary"] = dict(compact_reporter_feedback)
    strategist_output["performance_summary"] = dict(performance_summary)
    strategist_output["playbook"] = playbook
    strategist_output["pre_llm_market_regime"] = pre_llm_market_regime
    strategist_output["pre_llm_market_sentiment"] = pre_llm_market_sentiment
    strategist_output["pre_llm_market_structure"] = pre_llm_market_structure
    strategist_output["pre_llm_playbook"] = pre_llm_playbook
    strategist_output["pre_llm_monitor_guidance"] = pre_llm_monitor_guidance
    strategist_output["pre_llm_risk_tone"] = pre_llm_risk_tone
    strategist_output["pre_llm_trade_aggressiveness"] = pre_llm_trade_aggressiveness
    strategist_output["llm_requested_playbook"] = llm_requested_playbook
    strategist_output["requested_playbook"] = requested_playbook
    strategist_output["requested_playbook_source"] = requested_playbook_source
    strategist_output["final_playbook"] = playbook
    strategist_output["tactical_strategy"] = tactical_strategy
    strategist_output["tactical_subtype"] = tactical_subtype
    strategist_output["strategy_scores"] = dict(strategy_scores)
    strategist_output["rejected_strategy_reasons"] = dict(rejected_strategy_reasons)
    strategist_output["candidate_watch_policy"] = dict(candidate_watch_policy)
    strategist_output["selected_playbook"] = strategist_plan.get("selected_playbook")
    strategist_output["candidate_hypotheses"] = list(strategist_plan.get("candidate_hypotheses") or [])
    strategist_output["symbol_constraints"] = dict(strategist_plan.get("symbol_constraints") or {})
    strategist_output["symbol_plan"] = dict(strategist_plan.get("symbol_constraints") or {})
    strategist_output["entry_plan"] = dict(strategist_plan.get("entry_plan") or {})
    strategist_output["exit_plan"] = dict(strategist_plan.get("exit_plan") or {})
    strategist_output["strategy_summary"] = str(strategist_plan.get("strategy_summary") or "")
    strategist_output["policy_provenance"] = dict(policy_provenance)
    strategist_output["market_regime_summary"] = market_regime_summary
    strategist_output["monitor_entry_policy"] = dict(monitor_entry_policy)
    strategist_output["strategy_horizon_feedback"] = dict(strategy_horizon_feedback)
    strategist_output["strategist_horizon_proposal"] = dict(strategist_horizon_proposal)
    strategist_output["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_output["horizon_context"] = dict(horizon_context)
    strategist_output["strategy_horizon"] = str(strategy_horizon_feedback.get("strategy_horizon") or "")
    strategist_output["expected_hold_window"] = dict(strategy_horizon_feedback.get("expected_hold_window") or {})
    strategist_output["exit_guidance"] = dict(strategy_horizon_feedback.get("exit_guidance") or {})
    strategist_output["invalidation_conditions"] = list(strategy_horizon_feedback.get("invalidation_conditions") or [])
    strategist_output["scanner_bias_context"] = dict(scanner_bias_context)
    strategist_output["scanner_bias_summary"] = dict(facade.summarize_scanner_bias_context(scanner_bias_context))
    strategist_output["scanner_bias_validation_status"] = str(scanner_bias_context_validation.get("status") or "ok")
    strategist_output["scanner_bias_validation_issues"] = list(scanner_bias_context_validation.get("issues") or [])
    strategist_output["policy_rationale"] = policy_rationale
    strategist_output["policy_adjustment"] = dict(policy_adjustment)
    strategist_output["strategy_adjustment_directives"] = dict(strategy_adjustment_directives)
    return None
