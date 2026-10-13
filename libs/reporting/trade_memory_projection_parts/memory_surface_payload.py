"""Read-model status and summary projection for the memory surface.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_memory_surface.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def memory_status_value_result(strategy_present, selected_present, read_model_present, strategy_status, strategy_requested_day, strategy_resolved_day, symbol, selected_trade_count, selected_win_rate, selected_playbook, selected_blocker, reporter_present, reporter_available, reporter_consumed, reporter_status, reporter_gate_reason, reporter_confidence, reporter_recommendation_count, reporter_insight_summary, read_model_recent_trade_count, read_model_symbol_pattern_count, read_model_daily_summary_present, playbook, monitor_guidance, scanner_bias, best_playbooks, worst_playbooks, recent_failures, recent_success_patterns, active_layers, priority_order, read_model_symbols, prompt_strategy_present, prompt_selected_present, prompt_reporter_present, prompt_reporter_available, prompt_reporter_consumed, prompt_read_model_present, prompt_strategy_status, prompt_strategy_requested_day, prompt_strategy_resolved_day, prompt_symbol, prompt_selected_trade_count, prompt_selected_win_rate, prompt_selected_playbook, prompt_selected_blocker, prompt_reporter_status, prompt_reporter_gate_reason, prompt_reporter_confidence, prompt_reporter_insight_summary, prompt_read_model_recent_trade_count, prompt_read_model_symbol_pattern_count, prompt_read_model_daily_summary_present, selected_symbol_memory_rebuilt, reporter_feedback_rebuilt, memory_packets_rebuilt, commander_memory_policy_rebuilt, reconstructed_notes, usage_notes, commander_memory_policy, prompt_best_playbooks, prompt_worst_playbooks, prompt_recent_failures, prompt_recent_success_patterns, prompt_active_layers, prompt_priority_order, prompt_read_model_symbols, daily_packet, weekly_packet, monthly_packet, symbol_packet, reporter_dominant_patterns, reporter_recommendations, recent_feedback_visibility, prompt_memory_packets, packets_visibility, prompt_commander_memory_policy, policy_visibility, reporter_source_reports, reporter_trade_report_analysis, prompt_daily_packet, prompt_weekly_packet, prompt_monthly_packet, prompt_symbol_packet, prompt_reporter_dominant_patterns, prompt_reporter_recommendations, prompt_reporter_source_reports, prompt_reporter_trade_report_analysis, *, facade):
    return (
{
        "status": {
            "strategy_memory_used": strategy_present,
            "selected_symbol_memory_used": selected_present,
            "reporter_feedback_used": reporter_available or reporter_consumed,
            "read_model_facts_used": read_model_present,
        },
        "strategy_memory": {
            "present": strategy_present,
            "scope": "aggregated_strategy_memory",
            "separate_daily_weekly_monthly_packets": True,
            "status": strategy_status,
            "requested_day": strategy_requested_day,
            "resolved_day": strategy_resolved_day,
            "best_playbooks": best_playbooks[:3],
            "worst_playbooks": worst_playbooks[:3],
            "recent_failures": recent_failures[:3],
            "recent_success_patterns": recent_success_patterns[:3],
        },
        "commander_memory_policy": {
            "present": bool(commander_memory_policy) or bool(policy_visibility.get("present")),
            "application_mode": facade._text(
                commander_memory_policy.get("application_mode") or policy_visibility.get("application_mode"),
                max_len=24,
            ),
            "active_layers": active_layers[:4],
            "priority_order": priority_order[:4],
            "symbol_memory_override_enabled": bool(
                commander_memory_policy.get("symbol_memory_override_enabled")
                if commander_memory_policy
                else policy_visibility.get("symbol_memory_override_enabled")
            ),
            "scanner_bias_enabled": bool(
                commander_memory_policy.get("scanner_bias_enabled")
                if commander_memory_policy
                else policy_visibility.get("scanner_bias_enabled")
            ),
            "monitor_bias_enabled": bool(
                commander_memory_policy.get("monitor_bias_enabled")
                if commander_memory_policy
                else policy_visibility.get("monitor_bias_enabled")
            ),
        },
        "memory_packets": {
            "daily": {
                "status": facade._text(daily_packet.get("status") or facade._dict(packets_visibility.get("daily")).get("status"), max_len=24),
                "active": bool(daily_packet.get("active") if daily_packet else facade._dict(packets_visibility.get("daily")).get("active")),
                "resolved_day": facade._text(daily_packet.get("resolved_day") or facade._dict(packets_visibility.get("daily")).get("resolved_day"), max_len=16),
                "best_playbook_count": len(facade._list(daily_packet.get("best_playbooks"))),
            },
            "weekly": {
                "status": facade._text(weekly_packet.get("status") or facade._dict(packets_visibility.get("weekly")).get("status"), max_len=24),
                "active": bool(weekly_packet.get("active") if weekly_packet else facade._dict(packets_visibility.get("weekly")).get("active")),
                "resolved_day": facade._text(weekly_packet.get("resolved_day") or facade._dict(packets_visibility.get("weekly")).get("resolved_day"), max_len=16),
                "sample_day_count": facade._safe_int(weekly_packet.get("sample_day_count") if weekly_packet else facade._dict(packets_visibility.get("weekly")).get("sample_day_count")),
            },
            "monthly": {
                "status": facade._text(monthly_packet.get("status") or facade._dict(packets_visibility.get("monthly")).get("status"), max_len=24),
                "active": bool(monthly_packet.get("active") if monthly_packet else facade._dict(packets_visibility.get("monthly")).get("active")),
                "resolved_day": facade._text(monthly_packet.get("resolved_day") or facade._dict(packets_visibility.get("monthly")).get("resolved_day"), max_len=16),
                "sample_day_count": facade._safe_int(monthly_packet.get("sample_day_count") if monthly_packet else facade._dict(packets_visibility.get("monthly")).get("sample_day_count")),
            },
            "symbol": {
                "status": facade._text(symbol_packet.get("status") or facade._dict(packets_visibility.get("symbol")).get("status"), max_len=24),
                "active": bool(symbol_packet.get("active") if symbol_packet else facade._dict(packets_visibility.get("symbol")).get("active")),
                "symbol": facade._text(symbol_packet.get("symbol") or facade._dict(packets_visibility.get("symbol")).get("symbol"), max_len=24),
                "trade_count": facade._safe_int(symbol_packet.get("trade_count") if symbol_packet else facade._dict(packets_visibility.get("symbol")).get("trade_count")),
            },
        },
        "selected_symbol_memory": {
            "present": selected_present,
            "symbol": symbol,
            "trade_count": selected_trade_count,
            "win_rate": selected_win_rate,
            "dominant_playbook": selected_playbook,
            "dominant_monitor_blocker": selected_blocker,
        },
        "reporter_feedback_packet": {
            "present": reporter_present,
            "available": reporter_available,
            "consumed": reporter_consumed,
            "status": reporter_status,
            "feedback_gate_reason": reporter_gate_reason,
            "confidence": reporter_confidence,
            "recommendation_count": reporter_recommendation_count,
            "source_reports": {
                "metrics": bool(reporter_source_reports.get("metrics")),
                "trade_explain": bool(reporter_source_reports.get("trade_explain")),
                "reporter_analysis": bool(reporter_source_reports.get("reporter_analysis")),
                "trade_reports": bool(reporter_source_reports.get("trade_reports")),
                "current_payload": bool(reporter_source_reports.get("current_payload")),
            },
            "insight_summary": reporter_insight_summary,
            "dominant_patterns": [
                {
                    "name": facade._text(facade._dict(item).get("name"), max_len=40),
                    "detail": facade._text(facade._dict(item).get("detail"), max_len=120),
                    "value": facade._safe_float(facade._dict(item).get("value")),
                }
                for item in reporter_dominant_patterns[:4]
                if isinstance(item, dict)
            ],
            "recommendation": [
                facade._text(item, max_len=140)
                for item in reporter_recommendations[:4]
                if facade._text(item, max_len=140)
            ],
            "trade_report_analysis": {
                "closed_trade_count": facade._safe_int(reporter_trade_report_analysis.get("closed_trade_count")),
                "win_count": facade._safe_int(reporter_trade_report_analysis.get("win_count")),
                "loss_count": facade._safe_int(reporter_trade_report_analysis.get("loss_count")),
                "same_price_cost_loss_count": facade._safe_int(reporter_trade_report_analysis.get("same_price_cost_loss_count")),
                "broker_truth_count": facade._safe_int(reporter_trade_report_analysis.get("broker_truth_count")),
                "avg_pnl_pct": facade._safe_float(reporter_trade_report_analysis.get("avg_pnl_pct")),
            },
        },
        "read_model_facts": {
            "present": read_model_present,
            "recent_trade_count": read_model_recent_trade_count,
            "symbol_pattern_count": read_model_symbol_pattern_count,
            "symbols": read_model_symbols[:5],
            "daily_summary_present": read_model_daily_summary_present,
            "recent_strategy_feedback_present": bool(recent_feedback_visibility.get("present")),
            "recent_strategy_feedback_window": facade._safe_int(recent_feedback_visibility.get("feedback_window_size")),
        },
        "prompt_proven": {
            "status": {
                "strategy_memory_present": prompt_strategy_present,
                "memory_packets_present": bool(prompt_memory_packets) or bool(packets_visibility),
                "commander_memory_policy_present": bool(prompt_commander_memory_policy) or bool(policy_visibility.get("present")),
                "selected_symbol_memory_present": prompt_selected_present,
                "reporter_feedback_present": prompt_reporter_present,
                "reporter_feedback_available": prompt_reporter_available,
                "reporter_feedback_consumed": prompt_reporter_consumed,
                "read_model_facts_present": prompt_read_model_present,
            },
            "strategy_memory": {
                "present": prompt_strategy_present,
                "status": prompt_strategy_status,
                "requested_day": prompt_strategy_requested_day,
                "resolved_day": prompt_strategy_resolved_day,
                "best_playbooks": prompt_best_playbooks[:3],
                "worst_playbooks": prompt_worst_playbooks[:3],
                "recent_failures": prompt_recent_failures[:3],
                "recent_success_patterns": prompt_recent_success_patterns[:3],
            },
            "memory_packets": {
                "daily": {
                    "status": facade._text(prompt_daily_packet.get("status") or facade._dict(packets_visibility.get("daily")).get("status"), max_len=24),
                    "active": bool(prompt_daily_packet.get("active") if prompt_daily_packet else facade._dict(packets_visibility.get("daily")).get("active")),
                    "resolved_day": facade._text(prompt_daily_packet.get("resolved_day") or facade._dict(packets_visibility.get("daily")).get("resolved_day"), max_len=16),
                    "best_playbook_count": len(facade._list(prompt_daily_packet.get("best_playbooks"))),
                },
                "weekly": {
                    "status": facade._text(prompt_weekly_packet.get("status") or facade._dict(packets_visibility.get("weekly")).get("status"), max_len=24),
                    "active": bool(prompt_weekly_packet.get("active") if prompt_weekly_packet else facade._dict(packets_visibility.get("weekly")).get("active")),
                    "resolved_day": facade._text(prompt_weekly_packet.get("resolved_day") or facade._dict(packets_visibility.get("weekly")).get("resolved_day"), max_len=16),
                    "sample_day_count": facade._safe_int(prompt_weekly_packet.get("sample_day_count") if prompt_weekly_packet else facade._dict(packets_visibility.get("weekly")).get("sample_day_count")),
                },
                "monthly": {
                    "status": facade._text(prompt_monthly_packet.get("status") or facade._dict(packets_visibility.get("monthly")).get("status"), max_len=24),
                    "active": bool(prompt_monthly_packet.get("active") if prompt_monthly_packet else facade._dict(packets_visibility.get("monthly")).get("active")),
                    "resolved_day": facade._text(prompt_monthly_packet.get("resolved_day") or facade._dict(packets_visibility.get("monthly")).get("resolved_day"), max_len=16),
                    "sample_day_count": facade._safe_int(prompt_monthly_packet.get("sample_day_count") if prompt_monthly_packet else facade._dict(packets_visibility.get("monthly")).get("sample_day_count")),
                },
                "symbol": {
                    "status": facade._text(prompt_symbol_packet.get("status") or facade._dict(packets_visibility.get("symbol")).get("status"), max_len=24),
                    "active": bool(prompt_symbol_packet.get("active") if prompt_symbol_packet else facade._dict(packets_visibility.get("symbol")).get("active")),
                    "symbol": facade._text(prompt_symbol_packet.get("symbol") or facade._dict(packets_visibility.get("symbol")).get("symbol"), max_len=24),
                    "trade_count": facade._safe_int(prompt_symbol_packet.get("trade_count") if prompt_symbol_packet else facade._dict(packets_visibility.get("symbol")).get("trade_count")),
                },
            },
            "commander_memory_policy": {
                "present": bool(prompt_commander_memory_policy) or bool(policy_visibility.get("present")),
                "application_mode": facade._text(
                    prompt_commander_memory_policy.get("application_mode") or policy_visibility.get("application_mode"),
                    max_len=24,
                ),
                "active_layers": prompt_active_layers[:4],
                "priority_order": prompt_priority_order[:4],
                "symbol_memory_override_enabled": bool(
                    prompt_commander_memory_policy.get("symbol_memory_override_enabled")
                    if prompt_commander_memory_policy
                    else policy_visibility.get("symbol_memory_override_enabled")
                ),
                "scanner_bias_enabled": bool(
                    prompt_commander_memory_policy.get("scanner_bias_enabled")
                    if prompt_commander_memory_policy
                    else policy_visibility.get("scanner_bias_enabled")
                ),
                "monitor_bias_enabled": bool(
                    prompt_commander_memory_policy.get("monitor_bias_enabled")
                    if prompt_commander_memory_policy
                    else policy_visibility.get("monitor_bias_enabled")
                ),
            },
            "selected_symbol_memory": {
                "present": prompt_selected_present,
                "symbol": prompt_symbol,
                "trade_count": prompt_selected_trade_count,
                "win_rate": prompt_selected_win_rate,
                "dominant_playbook": prompt_selected_playbook,
                "dominant_monitor_blocker": prompt_selected_blocker,
            },
            "reporter_feedback_packet": {
                "present": prompt_reporter_present,
                "available": prompt_reporter_available,
                "consumed": prompt_reporter_consumed,
                "status": prompt_reporter_status,
                "feedback_gate_reason": prompt_reporter_gate_reason,
                "confidence": prompt_reporter_confidence,
                "source_reports": {
                    "metrics": bool(prompt_reporter_source_reports.get("metrics")),
                    "trade_explain": bool(prompt_reporter_source_reports.get("trade_explain")),
                    "reporter_analysis": bool(prompt_reporter_source_reports.get("reporter_analysis")),
                    "trade_reports": bool(prompt_reporter_source_reports.get("trade_reports")),
                    "current_payload": bool(prompt_reporter_source_reports.get("current_payload")),
                },
                "insight_summary": prompt_reporter_insight_summary,
                "dominant_patterns": [
                    {
                        "name": facade._text(facade._dict(item).get("name"), max_len=40),
                        "detail": facade._text(facade._dict(item).get("detail"), max_len=120),
                        "value": facade._safe_float(facade._dict(item).get("value")),
                    }
                    for item in prompt_reporter_dominant_patterns[:4]
                    if isinstance(item, dict)
                ],
                "recommendation": [
                    facade._text(item, max_len=140)
                    for item in prompt_reporter_recommendations[:4]
                    if facade._text(item, max_len=140)
                ],
                "trade_report_analysis": {
                    "closed_trade_count": facade._safe_int(prompt_reporter_trade_report_analysis.get("closed_trade_count")),
                    "win_count": facade._safe_int(prompt_reporter_trade_report_analysis.get("win_count")),
                    "loss_count": facade._safe_int(prompt_reporter_trade_report_analysis.get("loss_count")),
                    "same_price_cost_loss_count": facade._safe_int(prompt_reporter_trade_report_analysis.get("same_price_cost_loss_count")),
                    "broker_truth_count": facade._safe_int(prompt_reporter_trade_report_analysis.get("broker_truth_count")),
                    "avg_pnl_pct": facade._safe_float(prompt_reporter_trade_report_analysis.get("avg_pnl_pct")),
                },
            },
            "read_model_facts": {
                "present": prompt_read_model_present,
                "recent_trade_count": prompt_read_model_recent_trade_count,
                "symbol_pattern_count": prompt_read_model_symbol_pattern_count,
                "symbols": prompt_read_model_symbols[:5],
                "daily_summary_present": prompt_read_model_daily_summary_present,
                "recent_strategy_feedback_present": bool(recent_feedback_visibility.get("present")),
                "recent_strategy_feedback_window": facade._safe_int(recent_feedback_visibility.get("feedback_window_size")),
            },
        },
        "reconstructed_trade_context": {
            "status": {
                "selected_symbol_memory_rebuilt": selected_symbol_memory_rebuilt,
                "reporter_feedback_rebuilt": reporter_feedback_rebuilt,
                "memory_packets_rebuilt": memory_packets_rebuilt,
                "commander_memory_policy_rebuilt": commander_memory_policy_rebuilt,
            },
            "selected_symbol_memory": {
                "present": selected_present,
                "rebuilt": selected_symbol_memory_rebuilt,
                "source": "persisted_symbol_read_model" if selected_symbol_memory_rebuilt else "prompt_proven",
                "symbol": symbol,
                "trade_count": selected_trade_count,
                "win_rate": selected_win_rate,
                "dominant_playbook": selected_playbook,
                "dominant_monitor_blocker": selected_blocker,
            },
            "reporter_feedback_packet": {
                "present": reporter_present,
                "available": reporter_available,
                "consumed": reporter_consumed,
                "rebuilt": reporter_feedback_rebuilt,
                "source": "same_day_trade_reports_fallback" if reporter_feedback_rebuilt else "prompt_proven",
                "status": reporter_status,
                "confidence": reporter_confidence,
                "feedback_gate_reason": reporter_gate_reason,
                "source_reports": {
                    "metrics": bool(reporter_source_reports.get("metrics")),
                    "trade_explain": bool(reporter_source_reports.get("trade_explain")),
                    "reporter_analysis": bool(reporter_source_reports.get("reporter_analysis")),
                    "trade_reports": bool(reporter_source_reports.get("trade_reports")),
                    "current_payload": bool(reporter_source_reports.get("current_payload")),
                },
                "trade_report_analysis": {
                    "closed_trade_count": facade._safe_int(reporter_trade_report_analysis.get("closed_trade_count")),
                    "win_count": facade._safe_int(reporter_trade_report_analysis.get("win_count")),
                    "loss_count": facade._safe_int(reporter_trade_report_analysis.get("loss_count")),
                    "same_price_cost_loss_count": facade._safe_int(reporter_trade_report_analysis.get("same_price_cost_loss_count")),
                    "broker_truth_count": facade._safe_int(reporter_trade_report_analysis.get("broker_truth_count")),
                    "avg_pnl_pct": facade._safe_float(reporter_trade_report_analysis.get("avg_pnl_pct")),
                },
            },
            "memory_packets": {
                "rebuilt": memory_packets_rebuilt,
                "source": "runtime_loader" if memory_packets_rebuilt else "prompt_proven",
            },
            "commander_memory_policy": {
                "rebuilt": commander_memory_policy_rebuilt,
                "source": "runtime_policy" if commander_memory_policy_rebuilt else "prompt_proven",
                "active_layers": active_layers[:4],
                "priority_order": priority_order[:4],
            },
            "notes": reconstructed_notes[:6],
        },
        "usage_trace": {
            "playbook": playbook,
            "monitor_guidance": monitor_guidance,
            "scanner_bias": scanner_bias,
            "notes": usage_notes[:10],
        },
    }
    )
