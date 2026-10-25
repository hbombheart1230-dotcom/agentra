"""Operator Brief compact-input construction for the LLM prompt (pure projection).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _compact_operator_brief_input_for_llm_r3_impl(prepared_input, *, facade):
    strategist = prepared_input.get("strategist") if isinstance(prepared_input.get("strategist"), dict) else {}
    scanner = prepared_input.get("scanner") if isinstance(prepared_input.get("scanner"), dict) else {}
    monitor = prepared_input.get("monitor") if isinstance(prepared_input.get("monitor"), dict) else {}
    commander = prepared_input.get("commander") if isinstance(prepared_input.get("commander"), dict) else {}
    reporter = prepared_input.get("reporter") if isinstance(prepared_input.get("reporter"), dict) else {}
    supervisor = prepared_input.get("supervisor") if isinstance(prepared_input.get("supervisor"), dict) else {}
    executor = prepared_input.get("executor") if isinstance(prepared_input.get("executor"), dict) else {}
    trade_report = prepared_input.get("trade_report") if isinstance(prepared_input.get("trade_report"), dict) else {}
    compact_kr_facts = facade._build_operator_brief_kr_facts(strategist, scanner, monitor, trade_report)
    scanner_selected_symbol = facade._trim_text(scanner.get("selected_symbol"), max_len=24)
    scanner_candidate_pool = facade._safe_int(scanner.get("candidate_pool_after_filter"), 0)
    scanner_selected_reason = facade._sanitize_operator_brief_text(scanner.get("selected_reason"))
    if facade._count_hangul_chars(scanner_selected_reason) <= 0 and scanner_selected_symbol:
        scanner_selected_reason = (
            f"{scanner_selected_symbol}이 {scanner_candidate_pool}개 후보 비교 결과 우선 감시 대상으로 선정되었습니다."
            if scanner_candidate_pool > 0
            else f"{scanner_selected_symbol}이 우선 감시 대상으로 선정되었습니다."
        )
    return {
        "run_id": facade._trim_text(prepared_input.get("run_id"), max_len=80),
        "commander": {
            "mode": facade._operator_brief_label_ko(commander.get("mode")),
            "phase": facade._operator_brief_label_ko(commander.get("phase")),
            "path": facade._trim_text(commander.get("path"), max_len=80),
            "status": facade._trim_text(commander.get("status"), max_len=24),
            "command_intent": facade._trim_text(commander.get("command_intent"), max_len=40),
            "strategist_invocation": facade._trim_text(commander.get("strategist_invocation"), max_len=40),
            "llm_policy": facade._trim_text(commander.get("llm_policy"), max_len=40),
            "selected_route": facade._trim_text(commander.get("selected_route"), max_len=40),
            "route_reason_text": facade._sanitize_operator_brief_text(commander.get("route_reason_text")),
            "strategist_cache_used": commander.get("strategist_cache_used"),
            "strategist_called": commander.get("strategist_called"),
            "cooldown_applied": commander.get("cooldown_applied"),
            "policy_source": facade._trim_text(commander.get("policy_source"), max_len=40),
            "policy_validation_status": facade._trim_text(commander.get("policy_validation_status"), max_len=40),
            "policy_fallback_used": commander.get("policy_fallback_used"),
            "policy_fallback_reason": facade._sanitize_operator_brief_text(commander.get("policy_fallback_reason")),
            "policy_partial_normalized": commander.get("policy_partial_normalized"),
            "policy_default_filled_fields": facade._clean_str_list(commander.get("policy_default_filled_fields"), limit=6, max_len=80),
            "policy_validation_missing_fields": facade._clean_str_list(commander.get("policy_validation_missing_fields"), limit=6, max_len=80),
            "policy_validation_invalid_fields": facade._clean_str_list(commander.get("policy_validation_invalid_fields"), limit=6, max_len=80),
            "override_reason": facade._sanitize_operator_brief_text(commander.get("override_reason")),
            "applied_policy_source_chain": facade._clean_str_list(
                commander.get("applied_policy_source_chain"), limit=5, max_len=80
            ),
            "applied_policy": facade._compact_scalar_map(commander.get("applied_policy"), limit=12, max_len=80),
        },
        "strategist": {
            "market_regime": facade._operator_brief_label_ko(strategist.get("market_regime")),
            "market_sentiment": facade._operator_brief_label_ko(strategist.get("market_sentiment")),
            "themes": [facade._sanitize_operator_brief_text(x) for x in facade._clean_str_list(strategist.get("themes"), limit=4, max_len=80)],
            "playbook": facade._operator_brief_label_ko(strategist.get("playbook")),
            "scanner_bias": facade._operator_brief_label_ko(strategist.get("scanner_bias")),
            "risk_tone": facade._operator_brief_label_ko(strategist.get("risk_tone")),
            "monitor_guidance": facade._operator_brief_label_ko(strategist.get("monitor_guidance")),
            "news_query_targets": facade._clean_str_list(strategist.get("news_query_targets"), limit=5, max_len=80),
            "news_query_reasoning": facade._trim_text(strategist.get("news_query_reasoning"), max_len=180),
            "global_sentiment_inputs": facade._compact_scalar_map(strategist.get("global_sentiment_inputs"), limit=8, max_len=80),
            "candidate_hints": facade._clean_str_list(strategist.get("candidate_hints"), limit=6, max_len=24),
            "market_headlines": facade._clean_str_list(strategist.get("market_headlines"), limit=3, max_len=120),
            "symbol_headlines": facade._clean_str_list(strategist.get("symbol_headlines"), limit=3, max_len=120),
            "market_news_titles": facade._clean_str_list(strategist.get("market_news_titles"), limit=3, max_len=120),
            "candidate_news_titles": facade._clean_str_list(strategist.get("candidate_news_titles"), limit=3, max_len=120),
            "llm_status": facade._trim_text(strategist.get("llm_status"), max_len=24),
            "llm_low_confidence": strategist.get("llm_low_confidence"),
            "canonical_summary": "",
            "canonical_bullets": [],
            "compact_kr_facts": compact_kr_facts.get("strategist") or [],
        },
        "scanner": {
            "candidate_source": facade._operator_brief_label_ko(scanner.get("candidate_source")),
            "candidate_pool_before_filter": scanner.get("candidate_pool_before_filter"),
            "candidate_pool_after_filter": scanner.get("candidate_pool_after_filter"),
            "top_ranked_symbols": facade._compact_ranked_symbols(scanner.get("top_ranked_symbols"), limit=3),
            "source_mix": facade._compact_scalar_map(scanner.get("source_mix"), limit=6, max_len=60),
            "selected_symbol": scanner_selected_symbol,
            "selected_reason": scanner_selected_reason,
            "source_scores": facade._compact_scalar_map(scanner.get("source_scores"), limit=6, max_len=80),
            "score_total": scanner.get("score_total"),
            "confidence": scanner.get("confidence"),
            "playbook": facade._operator_brief_label_ko(scanner.get("playbook")),
            "policy_source": facade._trim_text(scanner.get("policy_source"), max_len=80),
            "applied_policy_present": scanner.get("applied_policy_present"),
            "monitor_entry_policy_summary": facade._compact_scalar_map(scanner.get("monitor_entry_policy_summary"), limit=8, max_len=80),
            "selection_trace": {
                "ranked_candidates": facade._compact_ranked_symbols(
                    (scanner.get("selection_trace") or {}).get("ranked_candidates"),
                    limit=5,
                ),
                "selected_symbol": facade._trim_text((scanner.get("selection_trace") or {}).get("selected_symbol"), max_len=24),
                "selected_rank": (scanner.get("selection_trace") or {}).get("selected_rank"),
                "selection_reason": facade._sanitize_operator_brief_text((scanner.get("selection_trace") or {}).get("selection_reason")),
                "selected_symbol_score_drivers": facade._compact_scalar_map(
                    (scanner.get("selection_trace") or {}).get("selected_symbol_score_drivers"),
                    limit=6,
                    max_len=80,
                ),
            },
            "selected_symbol_score_drivers": facade._compact_scalar_map(
                scanner.get("selected_symbol_score_drivers"),
                limit=6,
                max_len=80,
            ),
            "feature_coverage": facade._compact_scalar_map(scanner.get("feature_coverage"), limit=6, max_len=80),
            "quote_metrics": facade._compact_scalar_map(scanner.get("quote_metrics"), limit=6, max_len=80),
            "score_breakdown": facade._compact_scalar_map(scanner.get("score_breakdown"), limit=8, max_len=80),
            "why_selected": compact_kr_facts.get("scanner") or [],
            "tie_break_rule": "총점 우선 -> 신뢰도 우선 -> 리스크 점수 낮은 순",
            "runner_ups": facade._compact_ranked_symbols(scanner.get("runner_ups"), limit=3),
            "runner_ups_lost": [
                {
                    "symbol": facade._trim_text((item or {}).get("symbol"), max_len=24),
                    "summary": facade._trim_text((item or {}).get("summary"), max_len=160),
                }
                for item in list(scanner.get("runner_ups_lost") or [])[:3]
                if isinstance(item, dict)
            ],
            "scanner_bias_applied": scanner.get("scanner_bias_applied"),
            "scanner_bias_summary": facade._compact_scalar_map(scanner.get("scanner_bias_summary"), limit=8, max_len=80),
            "candidate_bias_adjustments": [
                {
                    "symbol": facade._trim_text((row or {}).get("symbol"), max_len=24),
                    "bias_adjustment": (row or {}).get("bias_adjustment"),
                    "bias_adjustments": facade._clean_str_list(
                        [str((item or {}).get("reason") or "") for item in list((row or {}).get("bias_adjustments") or []) if isinstance(item, dict)],
                        limit=3,
                        max_len=120,
                    ),
                }
                for row in list(scanner.get("candidate_bias_adjustments") or [])[:3]
                if isinstance(row, dict)
            ],
            "selection_reason_with_bias": facade._sanitize_operator_brief_text(scanner.get("selection_reason_with_bias")),
            "canonical_bullets": [],
            "canonical_filters_summary": "",
            "canonical_filter_bullets": [],
            "compact_kr_facts": compact_kr_facts.get("scanner") or [],
        },
        "monitor": {
            "monitor_reason": facade._sanitize_operator_brief_text(monitor.get("monitor_reason")),
            "exit_reason": facade._trim_text(monitor.get("exit_reason"), max_len=120),
            "position_age_seconds": monitor.get("position_age_seconds"),
            "entry_evaluated": monitor.get("entry_evaluated"),
            "entry_triggered": monitor.get("entry_triggered"),
            "entry_reason": facade._sanitize_operator_brief_text(monitor.get("entry_reason")),
            "entry_pattern": facade._sanitize_operator_brief_text(monitor.get("entry_pattern")),
            "entry_guard_reason": facade._trim_text(monitor.get("entry_guard_reason"), max_len=120),
            "entry_intent_submitted": monitor.get("entry_intent_submitted"),
            "entry_metrics": facade._compact_scalar_map(monitor.get("entry_metrics"), limit=10, max_len=80),
            "entry_thresholds": facade._compact_scalar_map(monitor.get("entry_thresholds"), limit=8, max_len=80),
            "thresholds": facade._compact_monitor_thresholds(monitor.get("thresholds")),
            "entry_check_summary": facade._sanitize_operator_brief_text(monitor.get("entry_check_summary")),
            "entry_blockers": facade._clean_str_list(monitor.get("entry_blockers"), limit=8, max_len=120),
            "policy_ref": facade._compact_scalar_map(monitor.get("policy_ref"), limit=8, max_len=80),
            "timing_assessment": facade._compact_scalar_map(monitor.get("timing_assessment"), limit=8, max_len=80),
            "thresholds_guards_used": facade._compact_scalar_map(monitor.get("thresholds_guards_used"), limit=8, max_len=80),
            "threshold_shortfalls": facade._clean_str_list(monitor.get("threshold_shortfalls"), limit=6, max_len=120),
            "stop_policy_trace": facade._compact_scalar_map(monitor.get("stop_policy_trace"), limit=8, max_len=80),
            "received_policy": facade._compact_scalar_map(monitor.get("received_policy"), limit=12, max_len=80),
            "received_policy_source": facade._trim_text(monitor.get("received_policy_source"), max_len=40),
            "effective_policy": facade._compact_scalar_map(monitor.get("effective_policy"), limit=12, max_len=80),
            "effective_policy_source": facade._trim_text(monitor.get("effective_policy_source"), max_len=40),
            "effective_policy_source_chain": facade._clean_str_list(
                monitor.get("effective_policy_source_chain"), limit=5, max_len=80
            ),
            "policy_adjustments": facade._compact_scalar_map(monitor.get("policy_adjustments"), limit=8, max_len=80),
            "policy_adjustment_summary": facade._sanitize_operator_brief_text(monitor.get("policy_adjustment_summary")),
            "policy_adjustment_reasoning": facade._sanitize_operator_brief_text(monitor.get("policy_adjustment_reasoning")),
            "effective_policy_deltas": [
                facade._trim_text(
                    f"{(row or {}).get('field')}: {(row or {}).get('from')} -> {(row or {}).get('to')}",
                    max_len=120,
                )
                for row in list(monitor.get("effective_policy_deltas") or [])[:6]
                if isinstance(row, dict)
            ],
            "applied_policy": facade._compact_scalar_map(monitor.get("applied_policy"), limit=12, max_len=80),
            "policy_source": facade._trim_text(monitor.get("policy_source"), max_len=40),
            "policy_validation_status": facade._trim_text(monitor.get("policy_validation_status"), max_len=40),
            "policy_fallback_used": monitor.get("policy_fallback_used"),
            "policy_fallback_reason": facade._sanitize_operator_brief_text(monitor.get("policy_fallback_reason")),
            "policy_partial_normalized": monitor.get("policy_partial_normalized"),
            "policy_default_filled_fields": facade._clean_str_list(monitor.get("policy_default_filled_fields"), limit=6, max_len=80),
            "policy_validation_missing_fields": facade._clean_str_list(monitor.get("policy_validation_missing_fields"), limit=6, max_len=80),
            "policy_validation_invalid_fields": facade._clean_str_list(monitor.get("policy_validation_invalid_fields"), limit=6, max_len=80),
            "override_reason": facade._sanitize_operator_brief_text(monitor.get("override_reason")),
            "applied_policy_source_chain": facade._clean_str_list(
                monitor.get("applied_policy_source_chain"), limit=5, max_len=80
            ),
            "strategy_frame_adjustments": facade._clean_str_list(monitor.get("strategy_frame_adjustments"), limit=4, max_len=120),
            "exit_policy_guard_adjustments": facade._clean_str_list(monitor.get("exit_policy_guard_adjustments"), limit=4, max_len=120),
            "canonical_bullets": [],
            "canonical_snapshot": facade._compact_scalar_map(monitor.get("canonical_snapshot"), limit=10, max_len=120),
            "compact_kr_facts": compact_kr_facts.get("monitor") or [],
        },
        "supervisor": facade._compact_scalar_map(supervisor, limit=8, max_len=120),
        "executor": {
            "action": facade._trim_text(executor.get("action"), max_len=24),
            "symbol": facade._trim_text(executor.get("symbol"), max_len=24),
            "qty": executor.get("qty"),
            "status": facade._trim_text(executor.get("status"), max_len=160),
            "canonical_summary": "",
            "canonical_bullets": [],
        },
        "reporter": {
            "ai_summary": facade._trim_text(reporter.get("ai_summary"), max_len=180),
            "ai_run_grade": facade._trim_text(reporter.get("ai_run_grade"), max_len=16),
            "found": reporter.get("found"),
            "status": facade._trim_text(reporter.get("status"), max_len=24),
            "reason": facade._trim_text(reporter.get("reason"), max_len=180),
        },
        "trade_report": {
            "report_available": trade_report.get("report_available"),
            "trade_id": facade._trim_text(trade_report.get("trade_id"), max_len=80),
            "lifecycle_status": facade._trim_text(trade_report.get("lifecycle_status"), max_len=24),
            "lifecycle_summary": "",
            "story_type": facade._trim_text(trade_report.get("story_type"), max_len=32),
            "execution_mode_label": facade._trim_text(trade_report.get("execution_mode_label"), max_len=48),
            "summary": facade._trim_text(trade_report.get("summary"), max_len=180),
        },
        "canonical_trade": facade._compact_canonical_trade_for_brief(prepared_input.get("canonical_trade")),
        "compact_kr_facts": compact_kr_facts,
    }


def _compact_canonical_trade_for_brief_r3_impl(data, *, facade):
    row = data if isinstance(data, dict) else {}
    return {
        "available": bool(row.get("available")),
        "trade_id": facade._trim_text(row.get("trade_id"), max_len=80),
        "story_type": facade._trim_text(row.get("story_type"), max_len=32),
        "execution_mode_label": facade._trim_text(row.get("execution_mode_label"), max_len=48),
        "lifecycle_status": facade._trim_text(row.get("lifecycle_status"), max_len=24),
        "lifecycle_summary": facade._trim_text(row.get("lifecycle_summary"), max_len=220),
        "current_action": facade._trim_text(row.get("current_action"), max_len=24),
        "entry_reason": facade._trim_text(row.get("entry_reason"), max_len=180),
        "exit_reason": facade._trim_text(row.get("exit_reason"), max_len=180),
        "market_context_summary": facade._trim_text(row.get("market_context_summary"), max_len=220),
        "market_context_bullets": facade._clean_str_list(row.get("market_context_bullets"), limit=6, max_len=180),
        "headline_count": row.get("headline_count"),
        "news_query_count": row.get("news_query_count"),
        "news_query_targets": facade._clean_str_list(row.get("news_query_targets"), limit=6, max_len=80),
        "market_news_titles": facade._clean_str_list(row.get("market_news_titles"), limit=3, max_len=120),
        "candidate_news_titles": facade._clean_str_list(row.get("candidate_news_titles"), limit=3, max_len=120),
        "selection_summary": facade._trim_text(row.get("selection_summary"), max_len=220),
        "selection_bullets": facade._clean_str_list(row.get("selection_bullets"), limit=6, max_len=180),
        "selected_score": row.get("selected_score"),
        "selected_sources": facade._clean_str_list(row.get("selected_sources"), limit=5, max_len=80),
        "why_selected": facade._clean_str_list(row.get("why_selected"), limit=4, max_len=160),
        "selection_basis": facade._trim_text(row.get("selection_basis"), max_len=220),
        "tie_break_rule": facade._trim_text(row.get("tie_break_rule"), max_len=160),
        "top_candidates": facade._compact_ranked_symbols(row.get("top_candidates"), limit=3),
        "runner_ups": facade._compact_ranked_symbols(row.get("runner_ups"), limit=3),
        "runner_ups_lost": [
            {
                "symbol": facade._trim_text((item or {}).get("symbol"), max_len=24),
                "summary": facade._trim_text((item or {}).get("summary"), max_len=180),
            }
            for item in list(row.get("runner_ups_lost") or [])[:3]
            if isinstance(item, dict) and (facade._trim_text((item or {}).get("symbol"), max_len=24) or facade._trim_text((item or {}).get("summary"), max_len=180))
        ],
        "filters_summary": facade._trim_text(row.get("filters_summary"), max_len=220),
        "filter_bullets": facade._clean_str_list(row.get("filter_bullets"), limit=5, max_len=180),
        "monitor_summary": facade._trim_text(row.get("monitor_summary"), max_len=220),
        "monitor_bullets": facade._clean_str_list(row.get("monitor_bullets"), limit=6, max_len=180),
        "monitor_snapshot": facade._compact_scalar_map(row.get("monitor_snapshot"), limit=10, max_len=120),
        "monitor_decision_chain": facade._clean_str_list(row.get("monitor_decision_chain"), limit=5, max_len=120),
        "guard_summary": facade._trim_text(row.get("guard_summary"), max_len=180),
        "execution_summary": facade._trim_text(row.get("execution_summary"), max_len=180),
        "execution_bullets": facade._clean_str_list(row.get("execution_bullets"), limit=4, max_len=160),
        "reporter_summary": facade._trim_text(row.get("reporter_summary"), max_len=180),
        "reporter_status": facade._trim_text(row.get("reporter_status"), max_len=32),
        "reporter_grade": facade._trim_text(row.get("reporter_grade"), max_len=16),
    }


def _compact_ranked_symbols_r3_impl(rows, *, limit, facade):
    if not isinstance(rows, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in rows:
        if len(out) >= max(1, int(limit)):
            break
        if isinstance(item, dict):
            row = {
                "symbol": facade._trim_text(item.get("symbol") or item.get("code") or item.get("ticker"), max_len=24),
                "score": item.get("score_total") if item.get("score_total") is not None else item.get("score"),
                "reason": facade._trim_text(item.get("reason") or item.get("why"), max_len=160),
            }
        else:
            row = {
                "symbol": facade._trim_text(item, max_len=24),
                "score": None,
                "reason": "",
            }
        if row["symbol"]:
            out.append(row)
    return out


def _compact_monitor_thresholds_r3_impl(data, *, facade):
    row = data if isinstance(data, dict) else {}
    keys = (
        "hard_stop_pct",
        "effective_stop_loss_pct",
        "effective_stop_reason",
        "take_profit_pct",
        "peak_drawdown_exit_pct",
        "trailing_stop_pct",
        "vwap_breakdown_pct",
        "intraday_low_break_pct",
        "trend_strength_floor",
        "exit_confirm_required",
        "exit_confirm_count",
    )
    return {key: row.get(key) for key in keys if key in row}


def _compact_scalar_map_r3_impl(data, *, limit, max_len, facade):
    if not isinstance(data, dict):
        return {}
    out: Dict[str, Any] = {}
    for key, value in list(data.items()):
        if len(out) >= max(1, int(limit)):
            break
        if isinstance(value, (int, float, bool)) or value is None:
            out[str(key)] = value
            continue
        text = facade._trim_text(value, max_len=max_len)
        if text:
            out[str(key)] = text
    return out
