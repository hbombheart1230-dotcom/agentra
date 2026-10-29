"""Strategist LLM summary memory/news usage projections (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def memory_usage_from_canonical(canonical: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    trace = facade._as_dict(canonical.get("memory_usage_trace"))
    visibility = facade._as_dict(canonical.get("memory_packet_visibility"))
    layer_decisions = facade._as_dict(trace.get("layer_decisions"))
    compact_layers: Dict[str, Any] = {}
    for layer in ("daily", "weekly", "monthly", "symbol"):
        row = facade._as_dict(layer_decisions.get(layer))
        if not row:
            continue
        compact_layers[layer] = {
            "status": facade._text(row.get("status"), ""),
            "active": bool(row.get("active")),
            "used": bool(row.get("used")),
            "confidence": row.get("confidence"),
            "effect": facade._text(row.get("effect"), ""),
            "reason": facade._text(row.get("reason"), ""),
            "gate_reason": facade._text(row.get("gate_reason"), ""),
            "operator_summary": facade._compact_operator_summary(facade._as_dict(row.get("operator_summary"))),
        }

    return {
        "available": bool(trace or visibility),
        "active_layers": facade._as_list(trace.get("active_layers")),
        "priority_order": facade._as_list(trace.get("priority_order")),
        "human_summary": facade._text(trace.get("human_summary"), ""),
        "applied_to_strategy": facade._as_dict(trace.get("applied_to_strategy")),
        "scanner_application": facade._as_dict(trace.get("scanner_application")),
        "monitor_application": facade._as_dict(trace.get("monitor_application")),
        "layer_decisions": compact_layers,
        "memory_packet_visibility": {
            "reporter_feedback_packet": facade._as_dict(visibility.get("reporter_feedback_packet")),
            "selected_symbol_memory": facade._as_dict(visibility.get("selected_symbol_memory")),
            "commander_refresh_context": facade._as_dict(visibility.get("commander_refresh_context")),
        },
    }


def news_usage_from_canonical(canonical: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    trace = facade._as_dict(canonical.get("news_usage_trace"))
    context = facade._as_dict(canonical.get("news_context"))
    query_targets = facade._as_list(trace.get("query_targets")) or facade._as_list(canonical.get("news_query_targets"))
    market_headlines = facade._as_list(trace.get("market_headlines_used"))
    candidate_headlines = facade._as_list(trace.get("candidate_headlines_used"))
    market_count = len(market_headlines)
    candidate_count = len(candidate_headlines)
    if market_count <= 0:
        market_count = int(context.get("market_headline_count") or 0) or facade._headline_count_from_sample_map(canonical.get("market_news_sample"))
    if candidate_count <= 0:
        candidate_count = int(context.get("candidate_headline_count") or 0) or facade._headline_count_from_sample_map(canonical.get("candidate_news_sample"))
    headline_count = int(context.get("headline_count") or 0)
    if headline_count and market_count <= 0 and candidate_count <= 0:
        market_count = int(context.get("market_signal_total") or 0)
        candidate_count = max(0, headline_count - market_count)
    return {
        "available": bool(trace or context or canonical.get("news_evidence_summary") or query_targets),
        "query_targets": query_targets,
        "human_summary": facade._text(trace.get("human_summary") or context.get("summary"), ""),
        "market_effect": facade._text(trace.get("market_effect"), ""),
        "playbook_effect": facade._text(trace.get("playbook_effect"), ""),
        "scanner_guidance_effect": facade._text(trace.get("scanner_guidance_effect"), ""),
        "monitor_policy_effect": facade._text(trace.get("monitor_policy_effect"), ""),
        "confidence": facade._text(trace.get("confidence") or ("medium" if context else ""), ""),
        "news_evidence_summary": facade._text(canonical.get("news_evidence_summary"), ""),
        "news_query_reasoning": facade._text(canonical.get("news_query_reasoning"), ""),
        "market_headline_count": market_count,
        "candidate_headline_count": candidate_count,
        "market_headlines_sample": market_headlines[:3],
        "candidate_headlines_sample": candidate_headlines[:3],
    }


def news_quality_audit(canonical: Dict[str, Any], news_usage: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    ranked = facade._as_dict(canonical.get("news_evidence_ranked"))
    candidate_ranked = facade._as_list(ranked.get("candidate_news_ranked"))
    market_ranked = facade._as_list(ranked.get("market_news_ranked"))
    query_targets = facade._as_list(news_usage.get("query_targets"))
    market_count = int(news_usage.get("market_headline_count") or len(market_ranked) or 0)
    candidate_count = int(news_usage.get("candidate_headline_count") or len(candidate_ranked) or 0)
    total = market_count + candidate_count
    confidence = facade._text(news_usage.get("confidence"), "")
    summary = facade._text(news_usage.get("human_summary") or news_usage.get("news_evidence_summary"), "")
    no_effect = not any(
        facade._text(news_usage.get(key), "")
        for key in ("market_effect", "playbook_effect", "scanner_guidance_effect", "monitor_policy_effect")
    )
    issues: List[str] = []
    if total <= 0:
        issues.append("news_headlines_missing")
    if not query_targets:
        issues.append("news_query_targets_missing")
    if no_effect:
        issues.append("news_effect_trace_missing")
    if confidence.lower() in {"", "-", "low", "none", "unknown"}:
        issues.append("news_confidence_low_or_missing")
    if not summary:
        issues.append("news_summary_missing")
    if total > 0 and candidate_count <= 0:
        issues.append("candidate_news_missing")
    if total > 0 and market_count <= 0:
        issues.append("market_news_missing")
    if not issues:
        status = "ok"
    elif total > 0:
        status = "partial"
    else:
        status = "weak"
    return {
        "schema_version": "strategist_news_quality_audit.v1",
        "status": status,
        "headline_count": total,
        "market_headline_count": market_count,
        "candidate_headline_count": candidate_count,
        "query_target_count": len(query_targets),
        "query_targets": query_targets[:10],
        "confidence": confidence,
        "issues": issues,
        "market_effect": facade._text(news_usage.get("market_effect"), ""),
        "playbook_effect": facade._text(news_usage.get("playbook_effect"), ""),
        "scanner_guidance_effect": facade._text(news_usage.get("scanner_guidance_effect"), ""),
        "monitor_policy_effect": facade._text(news_usage.get("monitor_policy_effect"), ""),
    }
