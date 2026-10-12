"""Operator summary pattern bucketing and performance aggregation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _pattern_performance_payload_r3_impl(rows, *, facade):
    rows = list(rows or [])
    combined_rows: List[Dict[str, Any]] = []
    for row in rows:
        key = facade._combined_pattern_key(row)
        if key:
            enriched = dict(row)
            enriched["combined_pattern"] = key
            combined_rows.append(enriched)
    return {
        "schema_version": "pattern_performance.v1",
        "source": "operator_summary_trade_artifact_enrichment",
        "trade_count": len(rows),
        "closed_or_realized_count": len(facade._performance_source_rows(rows)),
        "strategist": {
            "by_final_playbook": facade._performance_rows_by_field(rows, "final_playbook"),
            "by_tactical_strategy": facade._performance_rows_by_field(rows, "tactical_strategy"),
            "by_strategy_horizon": facade._performance_rows_by_field(rows, "strategy_horizon"),
            "by_risk_tone": facade._performance_rows_by_field(rows, "risk_tone"),
            "by_trade_aggressiveness": facade._performance_rows_by_field(rows, "trade_aggressiveness"),
            "by_candidate_watch_rank": facade._performance_rows_by_field(rows, "candidate_watch_max_priority_rank"),
            "by_candidate_watch_cascade": facade._performance_rows_by_field(rows, "candidate_watch_cascade_enabled"),
        },
        "scanner": {
            "by_scanner_rank_bucket": facade._performance_rows_by_field(rows, "scanner_rank_bucket"),
            "by_selection_basis": facade._performance_rows_by_field(rows, "scanner_selection_basis"),
            "by_scanner_chart_fit_bucket": facade._performance_rows_by_field(rows, "scanner_chart_fit_score_bucket"),
            "by_scanner_chart_fit_authority": facade._performance_rows_by_field(rows, "scanner_chart_fit_authority"),
            "by_candidate_watch_effect": facade._performance_rows_by_field(rows, "commander_entry_candidate_watch_policy_effect"),
        },
        "monitor_entry": {
            "by_entry_pattern_type": facade._performance_rows_by_field(rows, "entry_pattern_type"),
            "by_human_chart_entry_score": facade._performance_rows_by_field(rows, "human_chart_entry_score_bucket"),
            "by_human_chart_setup_quality": facade._performance_rows_by_field(rows, "human_chart_setup_quality"),
            "by_candle_quality": facade._performance_rows_by_field(rows, "human_candle_quality_score_bucket"),
            "by_vwap_quality": facade._performance_rows_by_field(rows, "human_vwap_reference_quality_score_bucket"),
            "by_reward_room": facade._performance_rows_by_field(rows, "human_reward_room_score_bucket"),
            "by_reward_room_pct": facade._performance_rows_by_field(rows, "reward_room_pct_bucket"),
            "by_late_entry_risk": facade._performance_rows_by_field(rows, "late_entry_risk"),
        },
        "monitor_exit": {
            "by_exit_pattern_type": facade._performance_rows_by_field(rows, "exit_pattern_type"),
            "by_exit_reason": facade._performance_rows_by_field(rows, "exit_reason"),
            "by_cost_floor_state": facade._performance_rows_by_field(rows, "cost_floor_state"),
            "by_peak_drawdown_state": facade._performance_rows_by_field(rows, "peak_drawdown_state"),
            "by_time_limit_reassessment": facade._performance_rows_by_field(rows, "time_limit_reassessment_state"),
            "by_vwap_breakdown_state": facade._performance_rows_by_field(rows, "vwap_breakdown_state"),
            "by_monitor_exit_triggered": facade._performance_rows_by_field(rows, "monitor_exit_triggered"),
        },
        "quant": {
            "by_tactic_id": facade._performance_rows_by_field(rows, "quant_tactic_id"),
            "by_tactic_suitability_tier": facade._performance_rows_by_field(rows, "tactic_suitability_tier"),
            "by_tactic_suitability_score": facade._performance_rows_by_field(rows, "tactic_suitability_score_bucket"),
            "by_entry_decision": facade._performance_rows_by_field(rows, "entry_quant_decision"),
            "by_entry_primary_blocker": facade._performance_rows_by_field(rows, "entry_quant_primary_blocker"),
            "by_entry_cost_floor_state": facade._performance_rows_by_field(rows, "entry_quant_cost_floor_state"),
            "by_entry_cost_edge": facade._performance_rows_by_field(rows, "entry_quant_cost_edge_bucket"),
            "by_exit_decision": facade._performance_rows_by_field(rows, "exit_quant_decision"),
            "by_exit_primary_blocker": facade._performance_rows_by_field(rows, "exit_quant_primary_blocker"),
            "by_exit_confirmation_state": facade._performance_rows_by_field(rows, "exit_quant_confirmation_state"),
            "by_exit_hold_window_state": facade._performance_rows_by_field(rows, "exit_quant_hold_window_state"),
            "by_exit_hard_exit": facade._performance_rows_by_field(rows, "exit_quant_hard_exit"),
        },
        "combined": {
            "by_strategy_scanner_entry_exit": facade._performance_rows_by_field(combined_rows, "combined_pattern", limit=12)
        },
    }


def _pattern_counters_r3_impl(rows, *, facade):
    entry_reasons: facade.Counter[str] = facade.Counter()
    exit_reasons: facade.Counter[str] = facade.Counter()
    entry_patterns: facade.Counter[str] = facade.Counter()
    exit_patterns: facade.Counter[str] = facade.Counter()
    playbooks: facade.Counter[str] = facade.Counter()
    for row in rows:
        if not facade._is_realized_nonclosed_exit(row):
            entry_reason = facade._operator_reason_name(row.get("entry_reason"))
            if entry_reason:
                entry_reasons[entry_reason] += 1
            entry_pattern = facade._operator_pattern_name(
                row.get("entry_pattern_type"),
                axis="entry",
                fallback_reason=row.get("entry_reason"),
            )
            if entry_pattern:
                entry_patterns[entry_pattern] += 1

        if facade._is_closed_trade(row) or facade._is_realized_nonclosed_exit(row):
            exit_reason = facade._operator_reason_name(row.get("exit_reason"))
            if exit_reason:
                exit_reasons[exit_reason] += 1
            exit_pattern = facade._operator_pattern_name(
                row.get("exit_pattern_type"),
                axis="exit",
                fallback_reason=row.get("exit_reason"),
            )
            if exit_pattern:
                exit_patterns[exit_pattern] += 1
        playbook = str(row.get("playbook") or "").strip()
        if playbook:
            playbooks[playbook] += 1
    return {
        "entry_reasons": entry_reasons,
        "exit_reasons": exit_reasons,
        "entry_pattern_types": entry_patterns,
        "exit_pattern_types": exit_patterns,
        "playbooks": playbooks,
    }


def _performance_rows_by_field_r3_impl(rows, field, *, limit, facade):
    grouped: Dict[str, List[Dict[str, Any]]] = facade.defaultdict(list)
    for row in rows:
        axis = "entry" if field.startswith("entry") else "exit" if field.startswith("exit") else ""
        name = facade._operator_label_fallback(facade._performance_field_value(row, field), axis=axis)
        if not name:
            continue
        grouped[name].append(row)
    out: List[Dict[str, Any]] = []
    for name, items in grouped.items():
        sample = facade._performance_source_rows(items)
        stats = facade._return_count_payload(sample)
        out.append(
            {
                "name": name,
                "count": len(items),
                "closed_or_realized_count": len(sample),
                "win_count": stats["win_count"],
                "loss_count": stats["loss_count"],
                "flat_count": stats["flat_count"],
                "win_rate": stats["win_rate"],
                "avg_return_pct": stats["avg_return_pct"],
                "cost_drag_loss_count": stats["cost_drag_loss_count"],
                "avg_hold_seconds": stats["avg_hold_seconds"],
            }
        )
    out.sort(
        key=lambda row: (
            int(row.get("closed_or_realized_count") or 0),
            int(row.get("count") or 0),
            abs(float(row.get("avg_return_pct") or 0.0)),
        ),
        reverse=True,
    )
    return out[:limit]


def _performance_field_value_r3_impl(row, field, *, facade):
    value = row.get(field)
    if field == "entry_pattern_type":
        return facade._operator_pattern_name(value, axis="entry", fallback_reason=row.get("entry_reason"))
    if field == "exit_pattern_type":
        return facade._operator_pattern_name(value, axis="exit", fallback_reason=row.get("exit_reason"))
    if facade._text_value(value):
        if field in {"entry_reason", "exit_reason"}:
            return facade._operator_reason_name(value)
        return value
    if field == "entry_reason":
        return facade._operator_reason_name(row.get("entry_reason"))
    if field == "exit_reason":
        return facade._operator_reason_name(row.get("exit_reason"))
    return value


def _pattern_payload_r3_impl(counters, *, facade):
    return {
        "top_entry_reasons": facade._top_counter(counters.get("entry_reasons") or facade.Counter()),
        "top_exit_reasons": facade._top_counter(counters.get("exit_reasons") or facade.Counter()),
        "top_entry_pattern_types": facade._top_counter(counters.get("entry_pattern_types") or facade.Counter()),
        "top_exit_pattern_types": facade._top_counter(counters.get("exit_pattern_types") or facade.Counter()),
        "top_playbooks": facade._top_counter(counters.get("playbooks") or facade.Counter()),
    }


def _pattern_perf_rows_r3_impl(pattern_performance, *path, facade):
    current: Any = pattern_performance
    for key in path:
        if not isinstance(current, dict):
            return []
        current = current.get(key)
    return [row for row in list(current or []) if isinstance(row, dict)]


def _top_counter_r3_impl(counter, limit, *, facade):
    normalized: facade.Counter[str] = facade.Counter()
    for name, count in counter.items():
        clean_name = facade._operator_label_fallback(name)
        if clean_name:
            normalized[clean_name] += int(count)
    return [
        {"name": name, "count": int(count)}
        for name, count in normalized.most_common(limit)
        if str(name or "").strip()
    ]


def _return_count_payload_r3_impl(rows, *, facade):
    returns = [value for value in (facade._metric_return_pct(row) for row in rows) if value is not None]
    observed_returns = [value for value in (facade._metric_observed_return_pct(row) for row in rows) if value is not None]
    price_moves = [value for value in (facade._safe_float(row.get("truth_price_move_pct")) for row in rows) if value is not None]
    hold_seconds = [value for value in (facade._safe_float(row.get("hold_seconds")) for row in rows) if value is not None]
    win_count = sum(1 for value in returns if value > 0)
    loss_count = sum(1 for value in returns if value < 0)
    flat_count = sum(1 for value in returns if value == 0)
    cost_drag_loss_count = sum(
        1
        for row in rows
        if (facade._metric_return_pct(row) is not None and float(facade._metric_return_pct(row) or 0.0) < 0.0)
        and (facade._safe_float(row.get("truth_price_move_pct")) is not None and float(facade._safe_float(row.get("truth_price_move_pct")) or 0.0) >= 0.0)
    )
    return {
        "return_sample_count": len(returns),
        "unavailable_return_count": max(0, len(rows) - len(returns)),
        "observed_return_sample_count": len(observed_returns),
        "truth_surface_count": sum(1 for row in rows if bool(row.get("truth_surface_available"))),
        "win_count": win_count,
        "loss_count": loss_count,
        "flat_count": flat_count,
        "observed_win_count": sum(1 for value in observed_returns if value > 0),
        "observed_loss_count": sum(1 for value in observed_returns if value < 0),
        "observed_flat_count": sum(1 for value in observed_returns if value == 0),
        "observed_avg_return_pct": round(sum(observed_returns) / len(observed_returns), 4) if observed_returns else 0.0,
        "price_move_win_count": sum(1 for value in price_moves if value > 0),
        "price_move_loss_count": sum(1 for value in price_moves if value < 0),
        "cost_drag_loss_count": cost_drag_loss_count,
        "win_rate": round(win_count / len(returns), 4) if returns else 0.0,
        "avg_return_pct": round(sum(returns) / len(returns), 4) if returns else 0.0,
        "avg_hold_seconds": round(sum(hold_seconds) / len(hold_seconds), 2) if hold_seconds else 0.0,
    }


def _score_bucket_r3_impl(value, *, facade):
    parsed = facade._safe_float(value)
    if parsed is None:
        return ""
    if parsed >= 0.75:
        return ">=0.75"
    if parsed >= 0.60:
        return "0.60-0.75"
    if parsed >= 0.50:
        return "0.50-0.60"
    return "<0.50"


def _rank_bucket_r3_impl(value, *, facade):
    parsed = facade._safe_int(value, default=0)
    if parsed <= 0:
        return ""
    if parsed == 1:
        return "rank1"
    if parsed <= 3:
        return "rank2-3"
    if parsed <= 10:
        return "rank4-10"
    return "rank>10"


def _pct_bucket_r3_impl(value, *, facade):
    parsed = facade._safe_float(value)
    if parsed is None:
        return ""
    if parsed >= 0.012:
        return ">=1.20%"
    if parsed >= 0.006:
        return "0.60-1.20%"
    if parsed >= 0.0:
        return "0.00-0.60%"
    return "<0.00%"


def _mismatch_bucket_r3_impl(value, *, facade):
    if isinstance(value, bool):
        return "mismatch" if value else "aligned_or_unknown"
    text = str(value or "").strip().lower()
    if text in {"true", "1", "yes", "mismatch"}:
        return "mismatch"
    if text in {"false", "0", "no", "aligned_or_unknown"}:
        return "aligned_or_unknown"
    return ""


def _confirmation_bucket_r3_impl(value, *, facade):
    if isinstance(value, bool):
        return "pending" if value else "not_pending"
    text = str(value or "").strip().lower()
    if text in {"true", "1", "yes", "pending"}:
        return "pending"
    if text in {"false", "0", "no", "not_pending"}:
        return "not_pending"
    return ""


def _bool_bucket_r3_impl(value, *, facade):
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value or "").strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return "true"
    if text in {"false", "0", "no", "n"}:
        return "false"
    return ""
