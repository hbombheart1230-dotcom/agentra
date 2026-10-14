"""Rebuilt memory packet / feedback and playbook projection.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_memory_surface.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


class RebuiltMemoryFeedbackFacts(NamedTuple):
    """Result of `rebuilt_memory_feedback_facts` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    best_playbooks: Any
    commander_memory_policy_rebuilt: Any
    memory_packets_rebuilt: Any
    prompt_active_layers: Any
    prompt_priority_order: Any
    prompt_read_model_daily_summary_present: Any
    prompt_read_model_recent_trade_count: Any
    prompt_read_model_symbol_pattern_count: Any
    prompt_read_model_symbols: Any
    prompt_reporter_confidence: Any
    prompt_reporter_dominant_patterns: Any
    prompt_reporter_gate_reason: Any
    prompt_reporter_insight_summary: Any
    prompt_reporter_recommendations: Any
    prompt_reporter_source_reports: Any
    prompt_reporter_trade_report_analysis: Any
    prompt_symbol: Any
    recent_failures: Any
    recent_success_patterns: Any
    reconstructed_notes: Any
    reporter_feedback_rebuilt: Any
    selected_blocker: Any
    selected_playbook: Any
    selected_symbol_memory_rebuilt: Any
    selected_trade_count: Any
    selected_win_rate: Any
    strategy_requested_day: Any
    strategy_resolved_day: Any
    strategy_status: Any
    worst_playbooks: Any


def rebuilt_memory_feedback_facts(prompt_reporter_feedback, reporter_visibility, prompt_read_model_facts, read_model_visibility, prompt_commander_memory_policy, policy_visibility, reporter_feedback, selected_symbol_memory, prompt_selected_symbol_memory, memory_packets, prompt_memory_packets, commander_memory_policy, selected_visibility, prompt_symbol_packet, strategy_memory, strategy_visibility, *, facade):
    prompt_reporter_gate_reason = facade._text(
        prompt_reporter_feedback.get("feedback_gate_reason") or reporter_visibility.get("feedback_gate_reason"),
        max_len=40,
    )
    prompt_reporter_confidence = facade._text(
        prompt_reporter_feedback.get("confidence") or reporter_visibility.get("confidence"),
        max_len=24,
    )
    prompt_reporter_source_reports = facade._dict(prompt_reporter_feedback.get("source_reports"))
    prompt_reporter_trade_report_analysis = facade._dict(prompt_reporter_feedback.get("trade_report_analysis"))
    prompt_reporter_dominant_patterns = facade._list(prompt_reporter_feedback.get("dominant_patterns"))
    prompt_reporter_recommendations = facade._list(prompt_reporter_feedback.get("recommendation"))
    prompt_reporter_insight_summary = facade._text(prompt_reporter_feedback.get("insight_summary"), max_len=220)

    prompt_read_model_recent_trade_count = facade._read_model_recent_trade_count(prompt_read_model_facts, read_model_visibility)
    prompt_read_model_symbol_pattern_count = facade._read_model_symbol_pattern_count(prompt_read_model_facts, read_model_visibility)
    prompt_read_model_symbols = facade._read_model_symbols(prompt_read_model_facts, read_model_visibility)
    prompt_read_model_daily_summary_present = facade._read_model_daily_summary_present(prompt_read_model_facts, read_model_visibility)

    prompt_active_layers = facade._list(
        prompt_commander_memory_policy.get("active_layers") or policy_visibility.get("active_layers")
    )
    prompt_priority_order = facade._list(
        prompt_commander_memory_policy.get("priority_order") or policy_visibility.get("priority_order")
    )

    reporter_feedback_rebuilt = facade._reporter_feedback_strength(reporter_feedback) > facade._reporter_feedback_strength(prompt_reporter_feedback)
    selected_symbol_memory_rebuilt = bool(selected_symbol_memory) and not bool(prompt_selected_symbol_memory)
    memory_packets_rebuilt = bool(memory_packets) and not bool(prompt_memory_packets)
    commander_memory_policy_rebuilt = bool(commander_memory_policy) and not bool(prompt_commander_memory_policy)
    prompt_symbol = facade._text(
        prompt_selected_symbol_memory.get("symbol")
        or selected_visibility.get("symbol")
        or prompt_symbol_packet.get("symbol"),
        max_len=24,
    )

    reconstructed_notes: facade.List[str] = []
    if selected_symbol_memory_rebuilt:
        reconstructed_notes.append("trade_symbol_symbol_memory_rebuilt_from_persisted_symbol_history")
    if reporter_feedback_rebuilt:
        reconstructed_notes.append("same_day_reporter_feedback_rebuilt_from_same_day_trade_reports")
    if memory_packets_rebuilt:
        reconstructed_notes.append("memory_packets_rebuilt_from_runtime_loader")
    if commander_memory_policy_rebuilt:
        reconstructed_notes.append("commander_memory_policy_rebuilt_from_runtime_policy")

    strategy_status = facade._text(
        strategy_memory.get("status") or strategy_visibility.get("status"),
        max_len=40,
    )
    strategy_requested_day = facade._text(strategy_memory.get("requested_day") or strategy_visibility.get("requested_day"), max_len=16)
    strategy_resolved_day = facade._text(strategy_memory.get("resolved_day") or strategy_visibility.get("resolved_day"), max_len=16)
    best_playbooks = facade._list(strategy_memory.get("best_playbooks") or [])
    worst_playbooks = facade._list(strategy_memory.get("worst_playbooks") or [])
    recent_failures = facade._list(strategy_memory.get("recent_failures") or [])
    recent_success_patterns = facade._list(strategy_memory.get("recent_success_patterns") or [])

    selected_trade_count = facade._safe_int(
        selected_symbol_memory.get("trade_count")
        if selected_symbol_memory
        else selected_visibility.get("trade_count")
    )
    selected_win_rate = facade._safe_float(
        selected_symbol_memory.get("win_rate")
        if selected_symbol_memory
        else selected_visibility.get("win_rate")
    )
    selected_blocker = facade._text(
        selected_symbol_memory.get("dominant_monitor_blocker")
        if selected_symbol_memory
        else selected_visibility.get("dominant_monitor_blocker"),
        max_len=60,
    )
    selected_playbook = facade._text(
        selected_symbol_memory.get("dominant_playbook")
        if selected_symbol_memory
        else selected_visibility.get("dominant_playbook"),
        max_len=40,
    )
    return RebuiltMemoryFeedbackFacts(best_playbooks, commander_memory_policy_rebuilt, memory_packets_rebuilt, prompt_active_layers, prompt_priority_order, prompt_read_model_daily_summary_present, prompt_read_model_recent_trade_count, prompt_read_model_symbol_pattern_count, prompt_read_model_symbols, prompt_reporter_confidence, prompt_reporter_dominant_patterns, prompt_reporter_gate_reason, prompt_reporter_insight_summary, prompt_reporter_recommendations, prompt_reporter_source_reports, prompt_reporter_trade_report_analysis, prompt_symbol, recent_failures, recent_success_patterns, reconstructed_notes, reporter_feedback_rebuilt, selected_blocker, selected_playbook, selected_symbol_memory_rebuilt, selected_trade_count, selected_win_rate, strategy_requested_day, strategy_resolved_day, strategy_status, worst_playbooks)
