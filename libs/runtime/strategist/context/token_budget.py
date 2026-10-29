"""Pure Strategist LLM-frame token budgeting."""
from __future__ import annotations


def apply_frame_token_budget(compact, *, memory_usage_disabled, facade):
    out = dict(compact or {})
    call_kind = facade._resolve_strategist_llm_call_kind(out)
    raw_theme_packet = out.pop("theme_strength_packet", {})
    out["theme_strength_packet_summary"] = facade._theme_packet_summary_for_llm(raw_theme_packet)
    out["theme_strength"] = facade._compact_theme_strength_for_llm(out.get("theme_strength"), limit=6)
    out["monitor_entry_policy_baseline"] = facade._compact_monitor_entry_policy_baseline_for_llm(
        out.get("monitor_entry_policy_baseline")
    )
    out["token_budget_policy"] = {
        "schema_version": "strategist_llm_token_budget.v1", "call_kind": str(call_kind),
        "dedup_theme_strength_packet": True, "stage_specific_context": bool(call_kind != "market_strategy_frame"),
        "memory_usage_disabled": bool(memory_usage_disabled),
    }
    if call_kind == "market_strategy_frame":
        return out
    out["candidate_news_signal_summary"] = list(out.get("candidate_news_signal_summary") or [])[:4]
    out["selected_symbol_news_signal"] = dict(out.get("selected_symbol_news_signal") or {})
    out["market_news_signal_summary"] = list(out.get("market_news_signal_summary") or [])[:3]
    out["market_news_sample"] = {}
    out["candidate_news_sample"] = {}
    news_policy = out.get("news_collection_policy") if isinstance(out.get("news_collection_policy"), dict) else {}
    out["news_collection_policy"] = {
        "provider": str(news_policy.get("provider") or ""), "post_scanner_requery": bool(news_policy.get("post_scanner_requery")),
        "reuse_policy": str(news_policy.get("reuse_policy") or ""),
        "collection_symbol_count": len(list(news_policy.get("collection_symbols") or [])),
    }
    out["available_themes"] = [{**dict(row), "component_symbols": [str(x or "") for x in list((row or {}).get("component_symbols") or [])[:3]]} for row in list(out.get("available_themes") or [])[:4] if isinstance(row, dict)]
    refresh_context = out.get("commander_refresh_context") if isinstance(out.get("commander_refresh_context"), dict) else {}
    out["commander_refresh_context"] = facade._slim_refresh_context_for_llm(refresh_context)
    feedback = out.get("recent_strategy_feedback") if isinstance(out.get("recent_strategy_feedback"), dict) else {}
    out["recent_strategy_feedback"] = {
        "feedback_window_size": int(feedback.get("feedback_window_size") or 0),
        "top_recent_weaknesses": [str(x or "") for x in list(feedback.get("top_recent_weaknesses") or [])[:2]],
        "recent_playbook_performance": dict(feedback.get("recent_playbook_performance") or {}),
        "advisory_only": bool(feedback.get("advisory_only", True)),
    }
    reporter_feedback = out.get("reporter_feedback_packet") if isinstance(out.get("reporter_feedback_packet"), dict) else {}
    out["reporter_feedback_packet"] = {
        "available": bool(reporter_feedback.get("available")), "status": str(reporter_feedback.get("status") or ""),
        "confidence": str(reporter_feedback.get("confidence") or "none"),
        "insight_summary": str(reporter_feedback.get("insight_summary") or "")[:140],
        "blocker_analysis": list(reporter_feedback.get("blocker_analysis") or [])[:2],
        "recommendation": [str(x or "") for x in list(reporter_feedback.get("recommendation") or [])[:2]],
        "advisory_only": True,
    }
    strategy_memory = out.get("strategy_memory") if isinstance(out.get("strategy_memory"), dict) else {}
    snapshot = strategy_memory.get("pattern_performance_snapshot") if isinstance(strategy_memory.get("pattern_performance_snapshot"), dict) else {}
    out["strategy_memory"] = {
        "status": str(strategy_memory.get("status") or ""), "best_playbooks": list(strategy_memory.get("best_playbooks") or [])[:2],
        "worst_playbooks": list(strategy_memory.get("worst_playbooks") or [])[:2],
        "pattern_performance_snapshot": {"problem_patterns": list(snapshot.get("problem_patterns") or [])[:3], "working_patterns": list(snapshot.get("working_patterns") or [])[:2]},
        "advisory_only": bool(strategy_memory.get("advisory_only", True)),
    }
    memory_packets = out.get("memory_packets") if isinstance(out.get("memory_packets"), dict) else {}
    out["memory_packets"] = {"daily_strategy_memory": dict(memory_packets.get("daily_strategy_memory") or {}), "symbol_memory_packet": dict(memory_packets.get("symbol_memory_packet") or {})}
    return out
