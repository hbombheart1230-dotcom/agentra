"""Read-model status and summary projection for the memory surface.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_memory_surface.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def memory_status_active_layers_priority_order(read_model_facts, read_model_visibility, reporter_feedback, reporter_visibility, commander_memory_policy, policy_visibility, strategy_present, strategy_requested_day, strategy_resolved_day, best_playbooks, worst_playbooks, recent_failures, daily_packet, weekly_packet, monthly_packet, symbol_packet, packets_visibility, *, facade):
    read_model_recent_trade_count = facade._read_model_recent_trade_count(read_model_facts, read_model_visibility)
    read_model_symbol_pattern_count = facade._read_model_symbol_pattern_count(read_model_facts, read_model_visibility)
    read_model_symbols = facade._read_model_symbols(read_model_facts, read_model_visibility)
    read_model_daily_summary_present = facade._read_model_daily_summary_present(read_model_facts, read_model_visibility)

    reporter_status = facade._text(
        reporter_feedback.get("status") or reporter_visibility.get("status"),
        max_len=40,
    )
    reporter_gate_reason = facade._text(
        reporter_feedback.get("feedback_gate_reason") or reporter_visibility.get("feedback_gate_reason"),
        max_len=40,
    )
    reporter_confidence = facade._text(
        reporter_feedback.get("confidence") or reporter_visibility.get("confidence"),
        max_len=24,
    )
    reporter_recommendation_count = len(facade._list(reporter_feedback.get("recommendation") or []))
    reporter_source_reports = facade._dict(reporter_feedback.get("source_reports"))
    reporter_trade_report_analysis = facade._dict(reporter_feedback.get("trade_report_analysis"))
    reporter_dominant_patterns = facade._list(reporter_feedback.get("dominant_patterns"))
    reporter_recommendations = facade._list(reporter_feedback.get("recommendation"))
    reporter_insight_summary = facade._text(reporter_feedback.get("insight_summary"), max_len=220)

    active_layers = facade._list(commander_memory_policy.get("active_layers") or policy_visibility.get("active_layers"))
    priority_order = facade._list(commander_memory_policy.get("priority_order") or policy_visibility.get("priority_order"))

    usage_notes: facade.List[str] = []
    if strategy_present:
        usage_notes.append("전략 메모리는 집계형 strategy_memory로 전략가에 전달됐습니다.")
        if strategy_requested_day or strategy_resolved_day:
            usage_notes.append(
                f"전략 메모리 요청일/해석일은 {strategy_requested_day or '-'} / {strategy_resolved_day or '-'}입니다."
            )
        if best_playbooks or worst_playbooks or recent_failures:
            usage_notes.append(
                "전략 메모리상 우세/취약 playbook과 최근 실패 흔적은 "
                f"{facade._join_text(best_playbooks, max_items=2) or '없음'} / "
                f"{facade._join_text(worst_playbooks, max_items=2) or '없음'} / "
                f"{facade._join_text(recent_failures, max_items=3, max_len=48) or '없음'}입니다."
            )
    else:
        usage_notes.append("전략 메모리는 이번 리포트 입력 기준으로 비어 있었습니다.")

    if commander_memory_policy or policy_visibility:
        usage_notes.append(
            "메모리 우선순위와 활성 layer 결정권은 commander가 가졌고, "
            f"active layer / priority는 {facade._join_text(active_layers, max_items=4, max_len=16) or '없음'} / "
            f"{facade._join_text(priority_order, max_items=4, max_len=16) or '없음'}입니다."
        )

    if daily_packet or weekly_packet or monthly_packet or symbol_packet or packets_visibility:
        usage_notes.append(
            "raw memory packet 상태는 "
            f"daily={facade._text(daily_packet.get('status') or facade._dict(packets_visibility.get('daily')).get('status') or 'unavailable', max_len=24)}, "
            f"weekly={facade._text(weekly_packet.get('status') or facade._dict(packets_visibility.get('weekly')).get('status') or 'unavailable', max_len=24)}"
            f"({facade._safe_int(weekly_packet.get('sample_day_count') if weekly_packet else facade._dict(packets_visibility.get('weekly')).get('sample_day_count'))}days), "
            f"monthly={facade._text(monthly_packet.get('status') or facade._dict(packets_visibility.get('monthly')).get('status') or 'unavailable', max_len=24)}"
            f"({facade._safe_int(monthly_packet.get('sample_day_count') if monthly_packet else facade._dict(packets_visibility.get('monthly')).get('sample_day_count'))}days), "
            f"symbol={facade._text(symbol_packet.get('status') or facade._dict(packets_visibility.get('symbol')).get('status') or 'unavailable', max_len=24)}입니다."
        )
    return (active_layers, priority_order, read_model_daily_summary_present, read_model_recent_trade_count, read_model_symbol_pattern_count, read_model_symbols, reporter_confidence, reporter_dominant_patterns, reporter_gate_reason, reporter_insight_summary, reporter_recommendation_count, reporter_recommendations, reporter_source_reports, reporter_status, reporter_trade_report_analysis, usage_notes)
