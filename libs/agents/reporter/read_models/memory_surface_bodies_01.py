"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_memory_surface.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _join_text_r4_impl(values, *, max_items, max_len, facade):
    items: List[str] = []
    for value in facade._list(values):
        text = facade._text(value, max_len=max_len)
        if not text:
            continue
        items.append(text)
        if len(items) >= max(1, int(max_items)):
            break
    return ', '.join(items)


def _strategy_anchor_artifacts_r4_impl(container, *, facade):
    obj = facade._dict(container)
    direct = facade._dict(obj.get('artifacts'))
    anchor = facade._dict(obj.get('strategy_anchor'))
    anchor_artifacts = facade._dict(anchor.get('artifacts'))
    return facade._first_dict(anchor_artifacts, direct)


def _strategist_input_artifact_paths_r4_impl(story_input, *, facade):
    paths: List[str] = []

    def _append(value: Any) -> None:
        text = str(value or '').strip()
        if text and text not in paths:
            paths.append(text)
    for container in (story_input, story_input.get('artifacts'), story_input.get('paths'), story_input.get('strategy_anchor'), story_input.get('market_context_human'), story_input.get('scanner_reason_human'), story_input.get('monitor_reason_human'), story_input.get('filters_human')):
        obj = facade._dict(container)
        _append(obj.get('strategist_input_json'))
        artifacts = facade._strategy_anchor_artifacts(obj)
        _append(artifacts.get('strategist_input_json'))
    return paths


def _resolve_strategist_input_artifact_r4_impl(story_input, *, facade):
    direct = facade._dict(story_input.get('strategist_input'))
    if direct:
        return direct
    for path in facade._strategist_input_artifact_paths(story_input):
        payload = facade._load_json_artifact(path)
        if payload:
            return payload
    return {}


def _symbol_pattern_memory_r4_impl(symbol, read_model_facts, *, facade):
    normalized_symbol = str(symbol or '').strip()
    if not normalized_symbol:
        return {}
    symbol_patterns = facade._dict(read_model_facts.get('symbol_patterns'))
    pattern = facade._dict(symbol_patterns.get(normalized_symbol))
    if not pattern:
        return {}
    trade_count = facade._safe_int(pattern.get('trade_count'))
    if trade_count <= 0:
        return {}
    return {'symbol': str(pattern.get('symbol') or normalized_symbol).strip(), 'trade_count': trade_count, 'closed_trade_count': facade._safe_int(pattern.get('closed_trade_count')), 'win_rate': facade._safe_float(pattern.get('win_rate')), 'dominant_playbook': str(pattern.get('dominant_playbook') or '').strip(), 'dominant_monitor_blocker': str(pattern.get('dominant_monitor_blocker') or '').strip(), 'override_eligible': trade_count >= 5 and facade._safe_int(pattern.get('closed_trade_count')) >= 3, 'source': 'prompt_read_model_symbol_patterns'}


def _packet_symbol_memory_r4_impl(symbol, memory_packets, *, facade):
    packet = facade._dict(memory_packets.get('symbol_memory_packet'))
    packet_symbol = str(packet.get('symbol') or '').strip()
    if not packet or (symbol and packet_symbol and (packet_symbol != str(symbol).strip())):
        return {}
    if not packet_symbol and facade._safe_int(packet.get('trade_count')) <= 0:
        return {}
    return dict(packet)


def _read_model_recent_trade_count_r4_impl(read_model_facts, visibility, *, facade):
    explicit = read_model_facts.get('recent_trade_count')
    if explicit not in (None, ''):
        return facade._safe_int(explicit)
    recent_trades = facade._list(read_model_facts.get('recent_trades'))
    if recent_trades:
        return len(recent_trades)
    return facade._safe_int(visibility.get('recent_trade_count'))


def _read_model_symbol_pattern_count_r4_impl(read_model_facts, visibility, *, facade):
    explicit = read_model_facts.get('symbol_pattern_count')
    if explicit not in (None, ''):
        return facade._safe_int(explicit)
    symbol_patterns = facade._dict(read_model_facts.get('symbol_patterns'))
    if symbol_patterns:
        return len(symbol_patterns)
    return facade._safe_int(visibility.get('symbol_pattern_count'))


def _read_model_symbols_r4_impl(read_model_facts, visibility, *, facade):
    symbols = facade._list(read_model_facts.get('symbols') or visibility.get('symbols'))
    if symbols:
        return symbols
    symbol_patterns = facade._dict(read_model_facts.get('symbol_patterns'))
    return list(symbol_patterns.keys())


def _read_model_daily_summary_present_r4_impl(read_model_facts, visibility, *, facade):
    if read_model_facts.get('daily_summary_present') not in (None, ''):
        return bool(read_model_facts.get('daily_summary_present'))
    if read_model_facts.get('daily_summary') not in (None, '', {}, []):
        return True
    return bool(visibility.get('daily_summary_present'))


def _nested_memory_sources_r4_impl(story_input, *, facade):
    reasoning_trace = facade._dict(story_input.get('reasoning_trace'))
    commander_summary = facade._dict(reasoning_trace.get('commander_summary'))
    strategist_summary = facade._dict(reasoning_trace.get('strategist_summary'))
    llm_output = facade._dict(strategist_summary.get('llm_parsed_output'))
    strategist_input_artifact = facade._resolve_strategist_input_artifact(story_input)
    strategist_source_input = facade._dict(strategist_input_artifact.get('source_input'))
    strategist_evidence = facade._dict(story_input.get('strategist_evidence'))
    decision_frames = facade._list(strategist_evidence.get('decision_frames'))
    first_frame = decision_frames[0] if decision_frames and isinstance(decision_frames[0], dict) else {}
    frame_payload = facade._dict(facade._dict(first_frame).get('payload'))
    visibility = facade._first_dict(story_input.get('memory_packet_visibility'), strategist_summary.get('memory_packet_visibility'), commander_summary.get('memory_packet_visibility'))
    return (commander_summary, strategist_summary, llm_output, frame_payload, visibility, strategist_source_input)


def _resolve_day_r4_impl(source, commander_summary, *, facade):
    for value in (source.get('day'), source.get('trade_day'), commander_summary.get('day'), commander_summary.get('ts'), source.get('ts')):
        text = str(value or '').strip()
        if len(text) >= 10:
            return text[:10]
    return ''


def _reporter_feedback_strength_r4_impl(packet, *, facade):
    source_reports = facade._dict(packet.get('source_reports'))
    trade_report_analysis = facade._dict(packet.get('trade_report_analysis'))
    return (1 if bool(packet.get('available')) else 0, sum((1 for key in ('metrics', 'trade_explain', 'reporter_analysis', 'trade_reports') if source_reports.get(key))), facade._safe_int(trade_report_analysis.get('closed_trade_count')), len(facade._list(packet.get('recommendation') or [])))


def _resolve_reporter_feedback_packet_r4_impl(*, source, commander_summary, reporter_feedback, facade):
    reports_root = facade._resolve_reports_root(source)
    day = facade._resolve_day(source, commander_summary)
    fallback_packet = facade.build_strategist_feedback_packet(mode='trade_report_fallback', payload={}, reports_root=reports_root, day=day) if day else {}
    current = dict(reporter_feedback or {})
    if facade._reporter_feedback_strength(fallback_packet) > facade._reporter_feedback_strength(current):
        return fallback_packet
    return current


def _build_fallback_memory_context_r4_impl(*, source, commander_summary, selected_symbol_memory, memory_packets, commander_memory_policy, facade):
    reports_root = facade._resolve_reports_root(source)
    day = facade._resolve_day(source, commander_summary)
    symbol = str(source.get('symbol') or source.get('selected_symbol') or '').strip()
    resolved_selected_symbol_memory = dict(selected_symbol_memory or {})
    if not resolved_selected_symbol_memory and symbol:
        resolved_selected_symbol_memory = facade._build_symbol_memory_from_persisted(symbol, reports_root)
    fallback_state = {'day': day, 'reports_root': str(reports_root), 'selected': {'symbol': symbol} if symbol else {}, 'selected_symbol_memory': dict(resolved_selected_symbol_memory or {})}
    resolved_packets = dict(memory_packets or {})
    if not resolved_packets:
        resolved_packets = facade.load_commander_memory_packets(state=fallback_state)
    resolved_policy = dict(commander_memory_policy or {})
    if not resolved_policy and resolved_packets:
        session_bias = str(commander_summary.get('session_bias') or facade._dict(commander_summary.get('commander_decision')).get('session_bias') or 'active_selection').strip() or 'active_selection'
        resolved_policy = facade.build_commander_memory_policy(session_bias=session_bias, memory_packets=resolved_packets)
    return (resolved_selected_symbol_memory, resolved_packets, resolved_policy)
