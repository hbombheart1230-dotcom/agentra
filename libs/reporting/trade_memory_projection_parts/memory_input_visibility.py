"""Memory packet input and visibility projection for the trade report memory surface (copied mappings in, values out).

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_memory_surface.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def memory_input_commander_memory_policy_daily_packet(story_input, *, facade):
    source = story_input if isinstance(story_input, dict) else {}
    commander_summary, strategist_summary, llm_output, frame_payload, visibility, strategist_source_input = facade._nested_memory_sources(source)
    commander_refresh_context = facade._dict(strategist_source_input.get("commander_refresh_context"))

    strategy_memory = facade._first_dict(
        frame_payload.get("strategy_memory"),
        strategist_source_input.get("strategy_memory"),
        llm_output.get("strategy_memory"),
    )
    reporter_feedback = facade._first_dict(
        frame_payload.get("reporter_feedback_packet"),
        strategist_source_input.get("reporter_feedback_packet"),
        llm_output.get("reporter_feedback_packet"),
    )
    selected_symbol_memory = facade._first_dict(
        frame_payload.get("selected_symbol_memory"),
        strategist_source_input.get("selected_symbol_memory"),
        commander_refresh_context.get("selected_symbol_memory"),
        llm_output.get("selected_symbol_memory"),
    )
    read_model_facts = facade._first_dict(
        frame_payload.get("read_model_facts"),
        strategist_source_input.get("read_model_facts"),
        llm_output.get("read_model_facts"),
    )
    memory_packets = facade._first_dict(
        frame_payload.get("memory_packets"),
        strategist_source_input.get("memory_packets"),
        llm_output.get("memory_packets"),
        commander_summary.get("memory_packets"),
    )
    commander_memory_policy = facade._first_dict(
        frame_payload.get("commander_memory_policy"),
        strategist_source_input.get("commander_memory_policy"),
        llm_output.get("commander_memory_policy"),
        strategist_summary.get("commander_memory_policy"),
        commander_summary.get("commander_memory_policy"),
    )
    symbol_hint = facade._text(
        source.get("symbol")
        or source.get("selected_symbol")
        or commander_refresh_context.get("selected_symbol"),
        max_len=24,
    )
    if not selected_symbol_memory:
        selected_symbol_memory = facade._first_dict(
            facade._packet_symbol_memory(symbol_hint, memory_packets),
            facade._symbol_pattern_memory(symbol_hint, read_model_facts),
        )

    prompt_strategy_memory = dict(strategy_memory or {})
    prompt_reporter_feedback = dict(reporter_feedback or {})
    prompt_selected_symbol_memory = dict(selected_symbol_memory or {})
    prompt_read_model_facts = dict(read_model_facts or {})
    prompt_memory_packets = dict(memory_packets or {})
    prompt_commander_memory_policy = dict(commander_memory_policy or {})

    selected_symbol_memory, memory_packets, commander_memory_policy = facade._build_fallback_memory_context(
        source=source,
        commander_summary=commander_summary,
        selected_symbol_memory=selected_symbol_memory,
        memory_packets=memory_packets,
        commander_memory_policy=commander_memory_policy,
    )
    reporter_feedback = facade._resolve_reporter_feedback_packet(
        source=source,
        commander_summary=commander_summary,
        reporter_feedback=reporter_feedback,
    )

    read_model_visibility = facade._dict(visibility.get("read_model_facts"))
    recent_feedback_visibility = facade._dict(visibility.get("recent_strategy_feedback"))
    strategy_visibility = facade._dict(visibility.get("strategy_memory"))
    selected_visibility = facade._dict(visibility.get("selected_symbol_memory"))
    reporter_visibility = facade._dict(visibility.get("reporter_feedback_packet"))
    packets_visibility = facade._dict(visibility.get("memory_packets"))
    policy_visibility = facade._dict(visibility.get("commander_memory_policy"))

    prompt_daily_packet = facade._dict(prompt_memory_packets.get("daily_strategy_memory"))
    prompt_weekly_packet = facade._dict(prompt_memory_packets.get("weekly_strategy_memory"))
    prompt_monthly_packet = facade._dict(prompt_memory_packets.get("monthly_strategy_memory"))
    prompt_symbol_packet = facade._dict(prompt_memory_packets.get("symbol_memory_packet"))

    daily_packet = facade._dict(memory_packets.get("daily_strategy_memory"))
    weekly_packet = facade._dict(memory_packets.get("weekly_strategy_memory"))
    return (commander_memory_policy, daily_packet, frame_payload, llm_output, memory_packets, packets_visibility, policy_visibility, prompt_commander_memory_policy, prompt_daily_packet, prompt_memory_packets, prompt_monthly_packet, prompt_read_model_facts, prompt_reporter_feedback, prompt_selected_symbol_memory, prompt_strategy_memory, prompt_symbol_packet, prompt_weekly_packet, read_model_facts, read_model_visibility, recent_feedback_visibility, reporter_feedback, reporter_visibility, selected_symbol_memory, selected_visibility, source, strategist_source_input, strategist_summary, strategy_memory, strategy_visibility, weekly_packet)


def memory_input_monitor_guidance_monthly_packet(memory_packets, source, selected_visibility, selected_symbol_memory, llm_output, frame_payload, strategist_summary, strategist_source_input, prompt_strategy_memory, strategy_visibility, prompt_selected_symbol_memory, prompt_reporter_feedback, reporter_visibility, prompt_read_model_facts, read_model_visibility, strategy_memory, reporter_feedback, read_model_facts, *, facade):
    monthly_packet = facade._dict(memory_packets.get("monthly_strategy_memory"))
    symbol_packet = facade._dict(memory_packets.get("symbol_memory_packet"))

    symbol = facade._text(
        source.get("symbol")
        or selected_visibility.get("symbol")
        or selected_symbol_memory.get("symbol")
        or symbol_packet.get("symbol"),
        max_len=24,
    )
    playbook = facade._text(
        llm_output.get("playbook")
        or frame_payload.get("playbook")
        or strategist_summary.get("playbook")
        or strategist_source_input.get("playbook_hint"),
        max_len=40,
    )
    monitor_guidance = facade._text(
        llm_output.get("monitor_guidance")
        or frame_payload.get("monitor_guidance")
        or facade._dict(frame_payload.get("entry_plan")).get("monitor_guidance")
        or facade._dict(frame_payload.get("exit_plan")).get("monitor_guidance"),
        max_len=40,
    )
    scanner_bias = facade._text(
        llm_output.get("scanner_bias") or frame_payload.get("scanner_bias"),
        max_len=40,
    )

    prompt_strategy_present = bool(prompt_strategy_memory) or bool(strategy_visibility.get("present"))
    prompt_selected_present = bool(prompt_selected_symbol_memory) or bool(selected_visibility.get("present"))
    prompt_reporter_present = bool(prompt_reporter_feedback) or bool(reporter_visibility.get("present"))
    prompt_read_model_present = bool(prompt_read_model_facts) or bool(read_model_visibility.get("present"))
    prompt_reporter_available = bool(prompt_reporter_feedback.get("available")) or bool(reporter_visibility.get("available"))
    prompt_reporter_consumed = bool(prompt_reporter_feedback.get("consumed")) or bool(reporter_visibility.get("consumed"))

    strategy_present = bool(strategy_memory) or bool(strategy_visibility.get("present"))
    selected_present = bool(selected_symbol_memory) or bool(selected_visibility.get("present"))
    reporter_present = bool(reporter_feedback) or bool(reporter_visibility.get("present"))
    read_model_present = bool(read_model_facts) or bool(read_model_visibility.get("present"))
    reporter_available = bool(reporter_feedback.get("available")) or bool(reporter_visibility.get("available"))
    reporter_consumed = bool(reporter_feedback.get("consumed")) or bool(reporter_visibility.get("consumed"))

    prompt_strategy_status = facade._text(
        prompt_strategy_memory.get("status") or strategy_visibility.get("status"),
        max_len=40,
    )
    prompt_strategy_requested_day = facade._text(
        prompt_strategy_memory.get("requested_day") or strategy_visibility.get("requested_day"),
        max_len=16,
    )
    prompt_strategy_resolved_day = facade._text(
        prompt_strategy_memory.get("resolved_day") or strategy_visibility.get("resolved_day"),
        max_len=16,
    )
    prompt_best_playbooks = facade._list(prompt_strategy_memory.get("best_playbooks") or [])
    prompt_worst_playbooks = facade._list(prompt_strategy_memory.get("worst_playbooks") or [])
    prompt_recent_failures = facade._list(prompt_strategy_memory.get("recent_failures") or [])
    prompt_recent_success_patterns = facade._list(prompt_strategy_memory.get("recent_success_patterns") or [])

    prompt_selected_trade_count = facade._safe_int(
        prompt_selected_symbol_memory.get("trade_count")
        if prompt_selected_symbol_memory
        else selected_visibility.get("trade_count")
    )
    prompt_selected_win_rate = facade._safe_float(
        prompt_selected_symbol_memory.get("win_rate")
        if prompt_selected_symbol_memory
        else selected_visibility.get("win_rate")
    )
    prompt_selected_blocker = facade._text(
        prompt_selected_symbol_memory.get("dominant_monitor_blocker")
        if prompt_selected_symbol_memory
        else selected_visibility.get("dominant_monitor_blocker"),
        max_len=60,
    )
    prompt_selected_playbook = facade._text(
        prompt_selected_symbol_memory.get("dominant_playbook")
        if prompt_selected_symbol_memory
        else selected_visibility.get("dominant_playbook"),
        max_len=40,
    )

    prompt_reporter_status = facade._text(
        prompt_reporter_feedback.get("status") or reporter_visibility.get("status"),
        max_len=40,
    )
    return (monitor_guidance, monthly_packet, playbook, prompt_best_playbooks, prompt_read_model_present, prompt_recent_failures, prompt_recent_success_patterns, prompt_reporter_available, prompt_reporter_consumed, prompt_reporter_present, prompt_reporter_status, prompt_selected_blocker, prompt_selected_playbook, prompt_selected_present, prompt_selected_trade_count, prompt_selected_win_rate, prompt_strategy_present, prompt_strategy_requested_day, prompt_strategy_resolved_day, prompt_strategy_status, prompt_worst_playbooks, read_model_present, reporter_available, reporter_consumed, reporter_present, scanner_bias, selected_present, strategy_present, symbol, symbol_packet)
