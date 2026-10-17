"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/strategy_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def build_news_symbol_linkage_view_r4_impl(*, strategist_summary, strategist_raw_input, strategist_parsed_output, selected_symbol, top_ranked_symbols, facade):
    summary = strategist_summary if isinstance(strategist_summary, dict) else {}
    raw_input = strategist_raw_input if isinstance(strategist_raw_input, dict) else {}
    parsed = strategist_parsed_output if isinstance(strategist_parsed_output, dict) else {}
    selected = facade._norm_symbol(selected_symbol)
    top_ranked = [symbol for symbol in (facade._norm_symbol(value) for value in list(top_ranked_symbols or [])) if symbol][:5]
    runner_up = next((symbol for symbol in top_ranked if symbol and symbol != selected), '')
    candidate_hints = facade._candidate_hints(summary, parsed)
    hypotheses = facade._candidate_hypotheses(summary, parsed)
    news_query_targets = facade._list_text(summary.get('news_query_targets') if summary.get('news_query_targets') is not None else raw_input.get('news_query_targets'), limit=8, max_len=80)
    news_ranked = summary.get('news_evidence_ranked') if isinstance(summary.get('news_evidence_ranked'), dict) else {}
    market_rows = facade._rows_from_news_like(news_ranked.get('market_news_ranked') if news_ranked.get('market_news_ranked') is not None else raw_input.get('collected_market_news'))
    candidate_rows = facade._rows_from_news_like(news_ranked.get('candidate_news_ranked') if news_ranked.get('candidate_news_ranked') is not None else raw_input.get('collected_candidate_news'))
    if not candidate_rows:
        candidate_rows = facade._rows_from_news_like(raw_input.get('collected_news'))
    market_headlines = facade._collect_top_headlines(market_rows, limit=3)
    selected_headlines = facade._collect_top_headlines(candidate_rows, limit=3, symbol=selected)
    runner_up_headlines = facade._collect_top_headlines(candidate_rows, limit=3, symbol=runner_up)
    ordered_symbols: List[str] = []
    for symbol in [selected, *candidate_hints, *top_ranked]:
        normalized = facade._norm_symbol(symbol)
        if normalized and normalized not in ordered_symbols:
            ordered_symbols.append(normalized)
    linked_candidates: List[Dict[str, Any]] = []
    for symbol in ordered_symbols[:5]:
        symbol_headlines = facade._collect_top_headlines(candidate_rows, limit=3, symbol=symbol)
        hypothesis = facade._hypothesis_for_symbol(hypotheses, symbol)
        linkage_flags = [flag for flag, enabled in (('candidate_hint', symbol in candidate_hints), ('top_ranked', symbol in top_ranked), ('headline_link', bool(symbol_headlines)), ('hypothesis', bool(hypothesis)), ('selected', symbol == selected)) if enabled]
        linked_candidates.append({'symbol': symbol, 'top_headlines': symbol_headlines, 'headline_count': len(symbol_headlines), 'hypothesis_summary': hypothesis, 'linkage_flags': linkage_flags, 'selected': symbol == selected})
    selected_link = next((item for item in linked_candidates if item.get('selected')), {})
    selected_in_hints = bool(selected and selected in candidate_hints)
    selected_has_hypothesis = bool(selected_link.get('hypothesis_summary'))
    selected_has_headlines = bool(selected_link.get('headline_count'))
    runner_up_hypothesis = facade._hypothesis_for_symbol(hypotheses, runner_up)
    runner_up_in_hints = bool(runner_up and runner_up in candidate_hints)
    linkage_strength = 'weak'
    if selected and selected_in_hints and (selected_has_hypothesis or selected_has_headlines):
        linkage_strength = 'strong'
    elif selected and (selected_in_hints or selected_has_hypothesis or selected_has_headlines):
        linkage_strength = 'partial'
    summary_text = f"Strategist queried {len(news_query_targets)} news targets and linked selected symbol {selected or '-'} to {int(selected_link.get('headline_count') or 0)} candidate headlines."
    if selected_in_hints:
        summary_text += f' {selected} remained inside strategist candidate hints.'
    comparison_summary = ''
    if selected and runner_up:
        comparison_summary = f'Selected {selected} vs runner-up {runner_up}: headlines {len(selected_headlines)} vs {len(runner_up_headlines)}, hint_match {str(selected_in_hints).lower()} vs {str(runner_up_in_hints).lower()}.'
    return {'selected_symbol': selected, 'runner_up_symbol': runner_up, 'news_query_targets': news_query_targets, 'candidate_symbols_hint': candidate_hints, 'candidate_hypotheses': hypotheses[:8], 'selected_symbol_in_candidate_hints': selected_in_hints, 'runner_up_symbol_in_candidate_hints': runner_up_in_hints, 'market_headlines': market_headlines, 'selected_symbol_headlines': selected_headlines, 'runner_up_symbol_headlines': runner_up_headlines, 'linked_candidates': linked_candidates, 'linkage_strength': linkage_strength, 'selected_vs_runner_up': {'selected_symbol': selected, 'runner_up_symbol': runner_up, 'selected_headline_count': len(selected_headlines), 'runner_up_headline_count': len(runner_up_headlines), 'selected_hypothesis_summary': selected_link.get('hypothesis_summary') or '', 'runner_up_hypothesis_summary': runner_up_hypothesis, 'selected_in_candidate_hints': selected_in_hints, 'runner_up_in_candidate_hints': runner_up_in_hints, 'comparison_summary': comparison_summary}, 'summary': summary_text}


def build_strategist_feedback_input_view_r4_impl(story_input, *, facade):
    story = story_input if isinstance(story_input, dict) else {}
    market_context = story.get('market_context_human') if isinstance(story.get('market_context_human'), dict) else {}
    scanner_reason = story.get('scanner_reason_human') if isinstance(story.get('scanner_reason_human'), dict) else {}
    monitor_reason = story.get('monitor_reason_human') if isinstance(story.get('monitor_reason_human'), dict) else {}
    operator_conclusion = story.get('operator_conclusion_human') if isinstance(story.get('operator_conclusion_human'), dict) else {}
    entry_summary = story.get('entry_summary') if isinstance(story.get('entry_summary'), dict) else {}
    exit_summary = story.get('exit_summary') if isinstance(story.get('exit_summary'), dict) else {}
    lifecycle_summary = story.get('lifecycle_summary') if isinstance(story.get('lifecycle_summary'), dict) else {}
    linkage = story.get('news_symbol_linkage') if isinstance(story.get('news_symbol_linkage'), dict) else {}
    strategist_trace = story.get('strategist_evidence_trace') if isinstance(story.get('strategist_evidence_trace'), dict) else {}
    if not strategist_trace and isinstance(market_context.get('strategist_evidence_trace'), dict):
        strategist_trace = dict(market_context.get('strategist_evidence_trace') or {})
    selected_symbol = facade._norm_symbol(linkage.get('selected_symbol') or scanner_reason.get('selected_symbol') or story.get('symbol') or '')
    playbook = facade._clip(market_context.get('playbook'), max_len=48)
    market_regime = facade._clip(market_context.get('market_regime'), max_len=48)
    market_sentiment = facade._clip(market_context.get('market_sentiment'), max_len=48)
    status = facade._clip(story.get('status'), max_len=24)
    action = facade._clip(story.get('action'), max_len=24)
    news_query_targets = facade._list_text(linkage.get('news_query_targets') if linkage.get('news_query_targets') is not None else market_context.get('news_query_targets'), limit=8, max_len=80)
    candidate_hints = facade._list_text(story.get('strategist_candidate_hints') if story.get('strategist_candidate_hints') is not None else linkage.get('candidate_symbols_hint'), limit=8, max_len=24)
    market_headlines = facade._list_text(linkage.get('market_headlines') if linkage.get('market_headlines') is not None else market_context.get('market_headlines'), limit=3, max_len=180)
    symbol_headlines = facade._list_text(linkage.get('selected_symbol_headlines') if linkage.get('selected_symbol_headlines') is not None else market_context.get('symbol_headlines'), limit=3, max_len=180)
    key_events = facade._list_text(strategist_trace.get('key_events') if strategist_trace.get('key_events') is not None else market_context.get('key_events'), limit=6, max_len=180)
    selected_vs_runner_up = linkage.get('selected_vs_runner_up') if isinstance(linkage.get('selected_vs_runner_up'), dict) else {}
    comparison_summary = facade._clip(selected_vs_runner_up.get('comparison_summary'), max_len=240)
    entry_reason = facade._clip(entry_summary.get('reason_human') or scanner_reason.get('selection_reason') or scanner_reason.get('summary'), max_len=240)
    holding_summary = facade._clip(monitor_reason.get('summary'), max_len=240)
    exit_reason = facade._clip(exit_summary.get('reason_human') or lifecycle_summary.get('exit_reason_human') or operator_conclusion.get('summary'), max_len=240)
    watch_next = facade._list_text(operator_conclusion.get('watch_next'), limit=6, max_len=180)
    thesis_invalidation = facade._list_text(operator_conclusion.get('thesis_invalidation'), limit=6, max_len=180)
    improvement_points = facade._list_text(story.get('improvement_points'), limit=6, max_len=180)
    entry_text = facade._collect_text_fragments(entry_summary.get('reason_human'), scanner_reason.get('selection_reason'), scanner_reason.get('summary'), improvement_points)
    exit_text = facade._collect_text_fragments(exit_summary.get('reason_human'), lifecycle_summary.get('exit_reason_human'), operator_conclusion.get('summary'), thesis_invalidation, improvement_points)
    entry_pattern_type = facade._entry_pattern_type(entry_text)
    entry_timing_quality = facade._entry_timing_quality(entry_text)
    entry_confirmation_quality = facade._entry_confirmation_quality(entry_text, monitor_reason)
    exit_pattern_type = facade._exit_pattern_type(exit_text)
    exit_quality = facade._exit_quality(exit_text, exit_pattern_type)
    thesis_invalidation_code = facade._thesis_invalidation_code(exit_text, exit_pattern_type)
    improvement_tags = facade._improvement_tags(facade._collect_text_fragments(improvement_points, thesis_invalidation, entry_text, exit_text), thesis_invalidation_code, exit_pattern_type)
    review_flags = facade._review_flags(trade_status=status, final_action=action, exit_pattern_type=exit_pattern_type, exit_quality=exit_quality, entry_confirmation_quality=entry_confirmation_quality, improvement_tags=improvement_tags)
    summary_bits: List[str] = []
    if selected_symbol:
        summary_bits.append(selected_symbol)
    if playbook:
        summary_bits.append(f'playbook={playbook}')
    if status:
        summary_bits.append(f'status={status}')
    if action:
        summary_bits.append(f'action={action}')
    summary = ' | '.join(summary_bits) if summary_bits else 'Strategist feedback input was assembled from trade story artifacts.'
    if comparison_summary:
        summary += f' {comparison_summary}'
    return facade.normalize_strategist_feedback_input({'schema_version': 'strategist_feedback_input.v1', 'selected_symbol': selected_symbol, 'playbook': playbook, 'market_regime': market_regime, 'market_sentiment': market_sentiment, 'trade_status': status, 'final_action': action, 'news_query_targets': news_query_targets, 'candidate_symbols_hint': candidate_hints, 'market_headlines': market_headlines, 'selected_symbol_headlines': symbol_headlines, 'key_events': key_events, 'linkage_strength': facade._clip(linkage.get('linkage_strength'), max_len=24), 'selected_vs_runner_up_summary': comparison_summary, 'entry_summary': entry_reason, 'entry_pattern_type': entry_pattern_type, 'entry_timing_quality': entry_timing_quality, 'entry_confirmation_quality': entry_confirmation_quality, 'holding_summary': holding_summary, 'exit_summary': exit_reason, 'exit_pattern_type': exit_pattern_type, 'exit_quality': exit_quality, 'thesis_invalidation_code': thesis_invalidation_code, 'improvement_tags': improvement_tags, 'review_flags': review_flags, 'watch_next': watch_next, 'thesis_invalidation': thesis_invalidation, 'improvement_points': improvement_points, 'summary': summary})


def normalize_strategist_feedback_input_r4_impl(payload, *, facade):
    data = payload if isinstance(payload, dict) else {}
    out = dict(data)
    out['schema_version'] = str(out.get('schema_version') or 'strategist_feedback_input.v1')
    out['selected_symbol'] = facade._norm_symbol(out.get('selected_symbol'))
    out['playbook'] = facade._clip(out.get('playbook'), max_len=48)
    out['market_regime'] = facade._clip(out.get('market_regime'), max_len=48)
    out['market_sentiment'] = facade._clip(out.get('market_sentiment'), max_len=48)
    out['trade_status'] = facade._clip(out.get('trade_status'), max_len=24)
    out['final_action'] = facade._clip(out.get('final_action'), max_len=24)
    out['news_query_targets'] = facade._list_text(out.get('news_query_targets'), limit=8, max_len=80)
    out['candidate_symbols_hint'] = facade._list_text(out.get('candidate_symbols_hint'), limit=8, max_len=24)
    out['market_headlines'] = facade._list_text(out.get('market_headlines'), limit=3, max_len=180)
    out['selected_symbol_headlines'] = facade._list_text(out.get('selected_symbol_headlines'), limit=3, max_len=180)
    out['key_events'] = facade._list_text(out.get('key_events'), limit=6, max_len=180)
    out['linkage_strength'] = facade._clip(out.get('linkage_strength'), max_len=24) or 'unknown'
    out['selected_vs_runner_up_summary'] = facade._clip(out.get('selected_vs_runner_up_summary'), max_len=240)
    out['entry_summary'] = facade._clip(out.get('entry_summary'), max_len=240)
    out['entry_pattern_type'] = facade._clip(out.get('entry_pattern_type'), max_len=32) or 'unknown'
    out['entry_timing_quality'] = facade._clip(out.get('entry_timing_quality'), max_len=32) or 'unknown'
    out['entry_confirmation_quality'] = facade._clip(out.get('entry_confirmation_quality'), max_len=32) or 'unknown'
    out['holding_summary'] = facade._clip(out.get('holding_summary'), max_len=240)
    out['exit_summary'] = facade._clip(out.get('exit_summary'), max_len=240)
    out['exit_pattern_type'] = facade._clip(out.get('exit_pattern_type'), max_len=32) or 'unknown'
    out['exit_quality'] = facade._clip(out.get('exit_quality'), max_len=32) or 'unknown'
    out['thesis_invalidation_code'] = facade._clip(out.get('thesis_invalidation_code'), max_len=48) or 'unknown'
    out['improvement_tags'] = facade._list_text(out.get('improvement_tags'), limit=8, max_len=64)
    out['review_flags'] = facade._list_text(out.get('review_flags'), limit=8, max_len=64)
    out['watch_next'] = facade._list_text(out.get('watch_next'), limit=6, max_len=180)
    out['thesis_invalidation'] = facade._list_text(out.get('thesis_invalidation'), limit=6, max_len=180)
    out['improvement_points'] = facade._list_text(out.get('improvement_points'), limit=6, max_len=180)
    out['summary'] = facade._clip(out.get('summary'), max_len=320)
    return out


def build_recent_strategist_feedback_window_r4_impl(items, *, window_size, facade):
    raw_items = items if isinstance(items, list) else []
    normalized_items: List[Dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        normalized = facade.normalize_strategist_feedback_input(item)
        normalized['trade_id'] = str(item.get('trade_id') or normalized.get('trade_id') or '')
        normalized['story_id'] = str(item.get('story_id') or normalized.get('story_id') or '')
        normalized['run_id'] = str(item.get('run_id') or normalized.get('run_id') or '')
        normalized['result_pct'] = facade._safe_float(item.get('result_pct'))
        if not normalized.get('selected_symbol'):
            normalized['selected_symbol'] = facade._norm_symbol(item.get('symbol'))
        if not normalized.get('trade_status'):
            normalized['trade_status'] = facade._clip(item.get('trade_status') or item.get('status'), max_len=24) or 'unknown'
        if not normalized.get('final_action'):
            normalized['final_action'] = facade._clip(item.get('final_action') or item.get('action'), max_len=24) or 'unknown'
        normalized_items.append(normalized)
    limit = max(0, int(window_size or 0))
    if limit == 0:
        limited_items: List[Dict[str, Any]] = []
    else:
        limited_items = normalized_items[:limit]
    symbols: List[str] = []
    playbooks_seen: List[str] = []
    trade_status_counts: facade.Counter[str] = facade.Counter()
    final_action_counts: facade.Counter[str] = facade.Counter()
    entry_pattern_counts: facade.Counter[str] = facade.Counter()
    exit_pattern_counts: facade.Counter[str] = facade.Counter()
    thesis_invalidation_counts: facade.Counter[str] = facade.Counter()
    improvement_tag_counts: facade.Counter[str] = facade.Counter()
    review_flag_counts: facade.Counter[str] = facade.Counter()
    result_values: List[float] = []
    recent_trade_refs: List[Dict[str, Any]] = []
    for item in limited_items:
        symbol = facade._norm_symbol(item.get('selected_symbol') or item.get('symbol') or '')
        if symbol and symbol not in symbols:
            symbols.append(symbol)
        playbook = facade._clip(item.get('playbook'), max_len=48)
        if playbook and playbook not in playbooks_seen:
            playbooks_seen.append(playbook)
        trade_status_counts[facade._normalize_counter_key(item.get('trade_status'))] += 1
        final_action_counts[facade._normalize_counter_key(item.get('final_action'))] += 1
        entry_pattern_counts[facade._normalize_counter_key(item.get('entry_pattern_type'))] += 1
        exit_pattern_counts[facade._normalize_counter_key(item.get('exit_pattern_type'))] += 1
        thesis_invalidation_counts[facade._normalize_counter_key(item.get('thesis_invalidation_code'))] += 1
        for tag in facade._list_text(item.get('improvement_tags'), limit=8, max_len=64):
            improvement_tag_counts[facade._normalize_counter_key(tag)] += 1
        for flag in facade._list_text(item.get('review_flags'), limit=8, max_len=64):
            review_flag_counts[facade._normalize_counter_key(flag)] += 1
        result_pct = facade._safe_float(item.get('result_pct'))
        if result_pct is not None:
            result_values.append(result_pct)
        recent_trade_refs.append(facade._compact_recent_trade_ref(item))
    average_result_pct = round(sum(result_values) / len(result_values), 6) if result_values else None
    return {'window_size': limit, 'trades_considered': len(limited_items), 'symbols': symbols, 'playbooks_seen': playbooks_seen, 'trade_status_counts': facade._ordered_counter_dict(trade_status_counts), 'final_action_counts': facade._ordered_counter_dict(final_action_counts), 'entry_pattern_counts': facade._ordered_counter_dict(entry_pattern_counts), 'exit_pattern_counts': facade._ordered_counter_dict(exit_pattern_counts), 'thesis_invalidation_counts': facade._ordered_counter_dict(thesis_invalidation_counts), 'improvement_tag_counts': facade._ordered_counter_dict(improvement_tag_counts), 'review_flag_counts': facade._ordered_counter_dict(review_flag_counts), 'known_result_trade_count': len(result_values), 'average_result_pct': average_result_pct, 'recent_trade_refs': recent_trade_refs}
