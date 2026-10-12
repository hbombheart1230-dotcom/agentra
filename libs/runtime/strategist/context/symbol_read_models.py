"""Strategist symbol read-model / refresh-context compaction (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _compact_symbol_read_model_for_llm_r3_impl(row, *, facade):
    src = row if isinstance(row, dict) else {}
    out = facade._compact_scalar_mapping_for_llm(
        src,
        allowed_keys=[
            "symbol",
            "trade_count",
            "closed_trade_count",
            "win_count",
            "loss_count",
            "win_rate",
            "avg_pnl_pct",
            "avg_return",
            "avg_hold_duration_sec",
            "dominant_playbook",
            "dominant_monitor_blocker",
            "dominant_exit_reason",
            "dominant_entry_reason",
            "override_eligible",
            "status",
        ],
        max_text_len=120,
    )
    out["repeated_failure_pattern"] = facade._compact_pattern_rows_for_llm(src.get("repeated_failure_pattern"), limit=3)
    out["recent_success_pattern"] = facade._compact_pattern_rows_for_llm(src.get("recent_success_pattern"), limit=3)
    data_quality = src.get("data_quality") if isinstance(src.get("data_quality"), dict) else {}
    if data_quality:
        out["data_quality"] = facade._compact_scalar_mapping_for_llm(
            data_quality,
            allowed_keys=["data_source", "unknown_fields_ratio", "status"],
            max_text_len=80,
        )
    return {k: v for k, v in out.items() if v not in ({}, [], "", None)}


def _compact_read_model_facts_for_llm_r3_impl(facts, *, facade):
    src = facts if isinstance(facts, dict) else {}
    recent_trades = [
        compact
        for compact in (facade._compact_trade_read_model_for_llm(row) for row in list(src.get("recent_trades") or [])[:3])
        if compact
    ]
    symbol_patterns: Dict[str, Any] = {}
    raw_patterns = src.get("symbol_patterns") if isinstance(src.get("symbol_patterns"), dict) else {}
    for symbol, row in list(raw_patterns.items())[:5]:
        compact = facade._compact_symbol_read_model_for_llm(row)
        if compact:
            symbol_patterns[str(symbol)] = compact
    daily_summary = facade._operator_summary_for_llm(src.get("daily_summary"))
    return {
        "recent_trades": recent_trades,
        "recent_trade_count": len(list(src.get("recent_trades") or [])),
        "daily_summary": daily_summary,
        "symbol_patterns": symbol_patterns,
        "symbol_pattern_count": len(raw_patterns),
    }


def _compact_candidate_context_for_refresh_r3_impl(row, *, facade):
    src = row if isinstance(row, dict) else {}
    if not src:
        return {}
    keep = (
        "symbol",
        "rank",
        "score",
        "score_total",
        "reason",
        "source",
        "risk_score",
        "confidence",
        "entry_compatibility_score",
        "scanner_chart_fit_score",
        "scanner_macro_chart_fit_score",
        "expected_monitor_block_reason",
        "dominant_block_reason",
        "market_representative_guard_reason",
        "selection_reason_with_bias",
        "status",
    )
    out = {key: src.get(key) for key in keep if src.get(key) not in (None, "", [], {})}
    score_breakdown = src.get("score_breakdown") if isinstance(src.get("score_breakdown"), dict) else {}
    if score_breakdown:
        out["score_breakdown"] = {
            str(key): facade._round_optional(value, 4) if facade._stage_float(value, None) is not None else facade._clip_text_for_llm(value, max_len=60)
            for key, value in list(score_breakdown.items())[:5]
        }
    return out


def _slim_refresh_context_for_llm_r3_impl(context, *, facade):
    src = context if isinstance(context, dict) else {}
    out = dict(src)
    out["feedback_id"] = str(src.get("feedback_id") or facade.stable_evidence_id("feedback", src))
    for key in ("scanner_primary_candidate", "actual_selected_candidate", "scanner_rank1_candidate"):
        out[key] = facade._compact_candidate_context_for_refresh(src.get(key))
    out["scanner_runner_ups"] = [
        facade._compact_candidate_context_for_refresh(row)
        for row in list(src.get("scanner_runner_ups") or [])[:3]
        if isinstance(row, dict)
    ]
    out["scanner_top_candidates"] = [
        facade._compact_candidate_context_for_refresh(row)
        for row in list(src.get("scanner_top_candidates") or [])[:4]
        if isinstance(row, dict)
    ]
    selected_memory = src.get("selected_symbol_memory") if isinstance(src.get("selected_symbol_memory"), dict) else {}
    if selected_memory:
        out["selected_symbol_memory"] = {
            "status": str(selected_memory.get("status") or ""),
            "symbol": str(selected_memory.get("symbol") or ""),
            "trade_count": int(selected_memory.get("trade_count") or 0),
            "override_eligible": bool(selected_memory.get("override_eligible")),
            "operator_summary": facade._operator_summary_for_llm(selected_memory.get("operator_summary")),
        }
    return out
