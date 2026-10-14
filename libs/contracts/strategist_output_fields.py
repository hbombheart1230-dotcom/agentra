"""Strategist output artifact: market context and playbook fields (key order unchanged).

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_strategist_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _listify,
    _safe_float,
)


def strategist_artifact_market_playbook_fields(explanation_fields, fear_index, macro_overlay, market_regime, market_sentiment, news_context, playbook, strategist_output, strategy_detail, strategy_thesis_text, summary):
    return {
            "market_regime": market_regime,
            "market_sentiment": market_sentiment,
            "market_context_summary": summary,
            "news_evidence_summary": _clip(news_context.get("summary") or strategist_output.get("news_query_reasoning"), max_len=400),
            "sentiment_evidence_summary": (
                f"global_sentiment_score={_safe_float(strategist_output.get('global_sentiment_score'), 0.0):.4f}"
                if strategist_output.get("global_sentiment_score") not in (None, "")
                else "global_sentiment_score=not_captured"
            ),
            "volatility_context": {
                "vix_level": fear_index.get("level"),
                "vix_pressure": fear_index.get("level_pressure"),
                "stress_flags": list(macro_overlay.get("stress_flags") or []),
            },
            "strategy_thesis": dict(explanation_fields.get("strategy_thesis") or {}),
            "strategy_thesis_text": strategy_thesis_text,
            "playbook": playbook,
            "pre_llm_playbook": strategy_detail["pre_llm_playbook"],
            "llm_requested_playbook": strategy_detail["llm_requested_playbook"],
            "requested_playbook": strategy_detail["requested_playbook"],
            "requested_playbook_source": strategy_detail["requested_playbook_source"],
            "final_playbook": strategy_detail["final_playbook"],
            "tactical_strategy": strategy_detail["tactical_strategy"],
            "tactical_subtype": strategy_detail["tactical_subtype"],
            "strategy_scores": dict(strategy_detail["strategy_scores"]),
            "rejected_strategy_reasons": dict(strategy_detail["rejected_strategy_reasons"]),
            "candidate_watch_policy": dict(strategy_detail["candidate_watch_policy"]),
            "strategy_detail": dict(strategy_detail),
            "policy_selected": {
                "strategy_policy": _dict(strategist_output.get("strategy_policy")),
                "monitor_guidance": _clip(strategist_output.get("monitor_guidance"), max_len=80),
                "risk_tone": _clip(strategist_output.get("risk_tone"), max_len=40),
                "trade_aggressiveness": _clip(strategist_output.get("trade_aggressiveness"), max_len=40),
            }
    }


def strategist_artifact_context_frame_fields(avoid_themes, candidate_news_context, decision_frame, decision_status, macro_overlay, market_news_context, market_regime, market_sentiment, negative_factors, news_collection_policy, news_context, playbook, positive_factors, selected, selected_score_total, state, strategist_llm, strategist_output, summary, theme_source, theme_source_reason, theme_source_status, theme_strength, theme_strength_packet, themes):
    return {
            "market_context": {
                "market_structure": _clip(strategist_output.get("market_structure"), max_len=80),
                "market_context_inputs": _dict(strategist_output.get("market_context_inputs")),
                "global_signal": _dict(state.get("global_signal")),
                "macro_stress_overlay": macro_overlay,
                "regime_score": strategist_output.get("regime_score"),
                "sentiment_score": strategist_output.get("sentiment_score"),
            },
            "news_context": {
                "summary": _clip(news_context.get("summary") or strategist_output.get("news_query_reasoning"), max_len=400),
                "news_query_targets": list(strategist_output.get("news_query_targets") or [])[:12],
                "news_collection_policy": news_collection_policy,
                "market_news_context": market_news_context,
                "candidate_news_context": candidate_news_context,
                "key_events": list(strategist_output.get("key_events") or [])[:10],
            },
            "strategy_frame": {
                "market_regime": market_regime,
                "market_sentiment": market_sentiment,
                "themes": themes,
                "selected_themes": _listify(strategist_output.get("selected_themes"), limit=5, max_len=80),
                "avoid_themes": avoid_themes,
                "theme_strength": theme_strength,
                "theme_strength_packet": theme_strength_packet,
                "available_themes": list(strategist_output.get("available_themes") or [])[:8]
                if isinstance(strategist_output.get("available_themes"), list)
                else [],
                "theme_strategy": _dict(strategist_output.get("theme_strategy")),
                "theme_source": theme_source,
                "theme_source_status": theme_source_status,
                "theme_source_reason": theme_source_reason,
                "playbook": playbook,
                "scanner_bias": _clip(strategist_output.get("scanner_bias"), max_len=80),
                "scanner_priority": _listify(strategist_output.get("scanner_priority"), limit=8, max_len=80),
                "monitor_guidance": _clip(strategist_output.get("monitor_guidance"), max_len=80),
                "trade_aggressiveness": _clip(strategist_output.get("trade_aggressiveness"), max_len=40),
                "risk_tone": _clip(strategist_output.get("risk_tone"), max_len=40),
            },
            "llm_trace": {
                "llm_status": _clip(strategist_llm.get("status"), max_len=40),
                "model": _clip(strategist_llm.get("model"), max_len=120),
                "llm_call_trace": _dict(strategist_llm.get("llm_call_trace")),
                "prompt_hash": _clip(strategist_llm.get("prompt_hash"), max_len=80),
                "response_hash": _clip(strategist_llm.get("response_hash"), max_len=80),
                "prompt_ref": _clip(strategist_llm.get("prompt_ref"), max_len=240),
                "response_ref": _clip(strategist_llm.get("response_ref"), max_len=240),
                "blocked": bool(strategist_llm.get("blocked")),
                "blocked_reason": _clip(strategist_llm.get("blocked_reason"), max_len=180),
            },
            "decision_summary": {
                "decision_status": decision_status,
                "selected_symbol": _clip(selected.get("symbol"), max_len=24),
                "selected_score_total": selected_score_total,
                "margin_vs_second": state.get("scanner_margin_vs_second"),
                "critical_positive_factors": positive_factors,
                "critical_negative_factors": negative_factors,
                "selection_summary": _clip(selected.get("why"), max_len=240),
                "strategy_thesis": _clip(
                    strategist_output.get("news_query_reasoning")
                    or strategist_output.get("monitor_guidance")
                    or summary,
                    max_len=320,
                ),
            },
            "decision_frame": decision_frame
    }


def strategist_artifact_theme_news_fallback_fields(candidate_symbols_hint, fallback_reason, fallback_used, fear_index, global_sentiment_signal, macro_overlay, news_collection_policy, news_evidence_missing, news_evidence_ranked, strategist_output, theme_source, theme_source_fallback_used, theme_source_reason, theme_source_status, theme_strength, theme_strength_packet):
    return {
            "theme_strength": theme_strength,
            "theme_strength_packet": theme_strength_packet,
            "available_themes": list(strategist_output.get("available_themes") or [])[:8]
            if isinstance(strategist_output.get("available_themes"), list)
            else [],
            "selected_themes": _listify(strategist_output.get("selected_themes"), limit=5, max_len=80),
            "theme_strategy": _dict(strategist_output.get("theme_strategy")),
            "theme_source": theme_source,
            "theme_source_status": theme_source_status,
            "theme_source_reason": theme_source_reason,
            "theme_source_fallback_used": theme_source_fallback_used,
            "theme_fallback_used": theme_source_fallback_used,
            "candidate_symbols_hint": candidate_symbols_hint,
            "news_evidence_ranked": news_evidence_ranked,
            "news_collection_policy": news_collection_policy,
            "global_sentiment_signal": global_sentiment_signal,
            "fear_index": fear_index,
            "stress_flags": _listify(macro_overlay.get("stress_flags"), limit=8, max_len=80),
            "news_evidence_missing": bool(news_evidence_missing),
            "candidate_symbols_hint_missing": not bool(candidate_symbols_hint),
            "fallback_used": bool(fallback_used),
            "fallback_reason": fallback_reason
    }


def strategist_artifact_commander_context_fields(commander_context, strategist_output):
    return {
            "commander_context_ref": {
                "source": _clip(
                    (
                        _dict(strategist_output.get("commander_context_ref")).get("source")
                        if isinstance(strategist_output.get("commander_context_ref"), dict)
                        else commander_context.get("source")
                    ),
                    max_len=80,
                ),
                "market_regime": _clip(commander_context.get("market_regime"), max_len=80),
                "session_bias": _clip(commander_context.get("session_bias"), max_len=80),
                "risk_mode": _clip(commander_context.get("risk_mode"), max_len=80),
                "strategist_refresh_requested": bool(
                    strategist_output.get("commander_refresh_requested")
                    if strategist_output.get("commander_refresh_requested") is not None
                    else commander_context.get("strategist_refresh_requested")
                ),
                "strategist_refresh_reason": _clip(
                    strategist_output.get("commander_refresh_reason")
                    or _dict(strategist_output.get("commander_context_ref")).get("strategist_refresh_reason")
                    or commander_context.get("strategist_refresh_reason"),
                    max_len=120,
                ),
                "strategist_refresh_context": _dict(
                    strategist_output.get("commander_refresh_context")
                    or _dict(strategist_output.get("commander_context_ref")).get("strategist_refresh_context")
                    or commander_context.get("strategist_refresh_context")
                ),
                "decision_summary": _clip(
                    (
                        _dict(strategist_output.get("commander_context_ref")).get("decision_summary")
                        if isinstance(strategist_output.get("commander_context_ref"), dict)
                        else commander_context.get("decision_summary")
                    ),
                    max_len=220,
                ),
            },
            "commander_invocation_hint": _clip(
                strategist_output.get("commander_invocation_hint")
                or commander_context.get("strategist_invocation"),
                max_len=80,
            ),
            "commander_llm_policy": _clip(
                strategist_output.get("commander_llm_policy")
                or commander_context.get("llm_policy"),
                max_len=80,
            ),
            "commander_no_trade_reason_code": _clip(
                strategist_output.get("commander_no_trade_reason_code")
                or commander_context.get("no_trade_reason_code"),
                max_len=80,
            ),
            "commander_refresh_requested": bool(
                strategist_output.get("commander_refresh_requested")
                if strategist_output.get("commander_refresh_requested") is not None
                else commander_context.get("strategist_refresh_requested")
            ),
            "commander_refresh_reason": _clip(
                strategist_output.get("commander_refresh_reason")
                or commander_context.get("strategist_refresh_reason"),
                max_len=120,
            ),
            "commander_refresh_context": _dict(
                strategist_output.get("commander_refresh_context")
                or commander_context.get("strategist_refresh_context")
            ),
            "shadow_used": bool(
                strategist_output.get("shadow_used")
                if strategist_output.get("shadow_used") is not None
                else commander_context.get("shadow_used")
            ),
            "strategist_fallback_used": bool(
                strategist_output.get("strategist_fallback_used")
                if strategist_output.get("strategist_fallback_used") is not None
                else commander_context.get("strategist_fallback_used")
            )
    }


def strategist_artifact_horizon_guidance_fields(commander_horizon_policy, horizon_context, selected_playbook, strategist_horizon_proposal, strategist_output, strategy_horizon_feedback):
    return {
            "selected_playbook": selected_playbook,
            "strategy_horizon_feedback": dict(strategy_horizon_feedback),
            "strategist_horizon_proposal": dict(strategist_horizon_proposal),
            "commander_horizon_policy": dict(commander_horizon_policy),
            "horizon_context": dict(horizon_context),
            "strategy_horizon": _clip(
                strategist_output.get("strategy_horizon") or strategy_horizon_feedback.get("strategy_horizon"),
                max_len=40,
            ),
            "expected_hold_window": _dict(
                strategist_output.get("expected_hold_window")
                or strategy_horizon_feedback.get("expected_hold_window")
            ),
            "exit_guidance": _dict(
                strategist_output.get("exit_guidance")
                or strategy_horizon_feedback.get("exit_guidance")
            )
    }
