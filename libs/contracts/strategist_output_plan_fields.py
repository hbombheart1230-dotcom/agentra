"""Strategist output artifact: candidate hypotheses, plans and policy resolution fields.

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
)


def strategist_artifact_plan_policy_fields(candidate_hypotheses, entry_plan, exit_plan, market_regime_summary, monitor_entry_policy, policy_fallback_reason, policy_provenance, policy_rationale, policy_resolution, policy_source, policy_validation_issues, policy_validation_status, strategist_output, strategy_summary, symbol_plan):
    return {
            "candidate_hypotheses": candidate_hypotheses,
            "symbol_plan": symbol_plan,
            "entry_plan": entry_plan,
            "exit_plan": exit_plan,
            "policy_provenance": policy_provenance,
            "strategy_summary": strategy_summary,
            "market_regime_summary": market_regime_summary,
            "monitor_entry_policy": monitor_entry_policy,
            "policy_rationale": policy_rationale,
            "policy_source": policy_source,
            "policy_validation_status": policy_validation_status,
            "policy_fallback_used": bool(strategist_output.get("policy_fallback_used")),
            "policy_fallback_reason": policy_fallback_reason,
            "policy_validation_issues": policy_validation_issues,
            "policy_resolution": dict(policy_resolution)
    }


def strategist_artifact_trace_handoff_feedback_fields(explanation_fields, policy_resolution, strategist_output):
    return {
            "strategy_delta_trace": dict(explanation_fields.get("strategy_delta_trace") or {}),
            "strategy_refresh_trace": dict(explanation_fields.get("strategy_refresh_trace") or {}),
            "memory_usage_trace": dict(explanation_fields.get("memory_usage_trace") or {}),
            "news_usage_trace": dict(explanation_fields.get("news_usage_trace") or {}),
            "scanner_handoff": dict(explanation_fields.get("scanner_handoff") or {}),
            "monitor_handoff": dict(explanation_fields.get("monitor_handoff") or {}),
            "conflict_analysis": dict(explanation_fields.get("conflict_analysis") or {}),
            "trade_permission_frame": dict(explanation_fields.get("trade_permission_frame") or {}),
            "responsibility_boundary": dict(explanation_fields.get("responsibility_boundary") or {}),
            "llm_attempted": bool(policy_resolution.get("llm_attempted")),
            "llm_ok": bool(policy_resolution.get("llm_ok")),
            "strategy_memory_snapshot": _dict(strategist_output.get("strategy_memory_snapshot")),
            "strategist_feedback": _dict(strategist_output.get("strategist_feedback")),
            "performance_summary": _dict(strategist_output.get("performance_summary"))
    }


def strategist_artifact_llm_policy_bias_fields(confidence, policy_resolution, strategist_output):
    return {
            "llm_error_type": _clip(policy_resolution.get("llm_error_type"), max_len=80),
            "llm_error_message_short": _clip(policy_resolution.get("llm_error_message_short"), max_len=180),
            "latency_ms": policy_resolution.get("latency_ms"),
            "fallback_source": _clip(policy_resolution.get("fallback_source"), max_len=120),
            "fallback_policy_id": _clip(policy_resolution.get("fallback_policy_id"), max_len=120),
            "effective_policy_source": _clip(policy_resolution.get("effective_policy_source"), max_len=120),
            "effective_prompt_version": _clip(policy_resolution.get("effective_prompt_version"), max_len=120),
            "effective_schema_version": _clip(policy_resolution.get("effective_schema_version"), max_len=120),
            "policy_staleness": policy_resolution.get("policy_staleness"),
            "reused_cached_strategy": bool(policy_resolution.get("reused_cached_strategy")),
            "strategy_generation_mode": _clip(policy_resolution.get("strategy_generation_mode"), max_len=40),
            "confidence": confidence,
            "scanner_bias": _clip(strategist_output.get("scanner_bias"), max_len=80),
            "scanner_bias_context": _dict(strategist_output.get("scanner_bias_context")),
            "scanner_bias_summary": _dict(strategist_output.get("scanner_bias_summary")),
            "scanner_bias_validation_status": _clip(
                strategist_output.get("scanner_bias_validation_status"),
                max_len=80,
            ),
            "scanner_bias_validation_issues": _listify(
                strategist_output.get("scanner_bias_validation_issues"),
                limit=8,
                max_len=180,
            )
    }


def strategist_artifact_refs_macro_fields(avoid_themes, candidate_news_context, evidence_log_path, fear_index, global_signal, macro_overlay, market_news_context, memory_packet_visibility, news_context, strategist_llm, strategist_output, summary, themes, trace_summary):
    return {
            "trace_summary": trace_summary,
            "memory_packet_visibility": memory_packet_visibility,
            "themes": themes,
            "avoid_themes": avoid_themes,
            "llm_metadata_summary": {
                "status": _clip(strategist_llm.get("status"), max_len=40),
                "model": _clip(strategist_llm.get("model"), max_len=120),
                "llm_call_trace": _dict(strategist_llm.get("llm_call_trace")),
                "blocked": bool(strategist_llm.get("blocked")),
                "blocked_reason": _clip(strategist_llm.get("blocked_reason"), max_len=180),
                "prompt_hash": _clip(strategist_llm.get("prompt_hash"), max_len=80),
                "response_hash": _clip(strategist_llm.get("response_hash"), max_len=80),
                "llm_status": _clip(strategist_llm.get("status"), max_len=40),
            },
            "source_refs": {
                "event_names": [
                    "strategist.market_context_snapshot",
                    "strategist.global_sentiment_breakdown",
                    "strategist.news_evidence_ranked",
                    "strategist.decision_frame",
                    "strategist.llm_response_saved",
                ],
                "evidence_log_path": evidence_log_path,
            },
            "evidence_refs": {
                "news_query_targets": list(strategist_output.get("news_query_targets") or [])[:8],
                "key_events": list(strategist_output.get("key_events") or [])[:8],
                "themes": themes,
                "avoid_themes": avoid_themes,
            },
            # compatibility-rich fields for downstream readers
            "global_sentiment_score": strategist_output.get("global_sentiment_score"),
            "global_macro_moves": _dict(global_signal.get("macro_moves")),
            "fear_index": fear_index,
            "macro_stress_overlay": macro_overlay,
            "market_context_inputs": _dict(strategist_output.get("market_context_inputs")),
            "news_query_reasoning": _clip(strategist_output.get("news_query_reasoning"), max_len=240),
            "news_query_targets": list(strategist_output.get("news_query_targets") or [])[:8],
            "market_news_total_headlines": market_news_context.get("total_headlines") or news_context.get("market_total_headlines") or news_context.get("total_headlines"),
            "market_news_query_count": market_news_context.get("query_count") or len(list(strategist_output.get("news_query_targets") or [])),
            "news_total_headlines": news_context.get("total_headlines") or market_news_context.get("total_headlines"),
            "news_symbol_count": candidate_news_context.get("symbol_count") or len(list(strategist_output.get("news_query_targets") or [])),
            "playbook_summary": summary
    }
