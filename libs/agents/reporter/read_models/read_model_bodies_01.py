"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _section_value_quality_r4_impl(value, *, facade):
    if value in (None, '', [], {}):
        return 0
    if isinstance(value, str):
        lower = value.strip().lower()
        if not lower or lower in {'not_captured', '-', 'unknown', 'none'} or 'not_captured' in lower:
            return 0
        return 2
    if isinstance(value, bool):
        return 1
    if isinstance(value, (int, float)):
        return 1
    if isinstance(value, list):
        return sum((facade._section_value_quality(item) for item in value[:12]))
    if isinstance(value, dict):
        return sum((facade._section_value_quality(item) for item in list(value.values())[:20]))
    return 0


def prefer_richer_trade_report_section_r4_impl(*sections, facade):
    best: Dict[str, Any] = {}
    best_score = -1
    for section in sections:
        if not isinstance(section, dict) or not section:
            continue
        score = 0
        for _, value in section.items():
            score += facade._section_value_quality(value)
        if score > best_score:
            best = section
            best_score = score
    return dict(best or {})


def normalize_trade_report_section_r4_impl(report, key, fallback_summary, *, trim_text, clean_str_list, facade):
    section = report.get(key) if isinstance(report.get(key), dict) else {}
    return {'summary': trim_text(section.get('summary'), max_len=1000) or trim_text(fallback_summary, max_len=1000), 'bullets': clean_str_list(section.get('bullets'), limit=12, max_len=280), 'status': trim_text(section.get('status'), max_len=64), 'grade': trim_text(section.get('grade'), max_len=32), 'current_action': trim_text(section.get('current_action'), max_len=32), 'watch_next': clean_str_list(section.get('watch_next'), limit=8, max_len=220), 'thesis_invalidation': clean_str_list(section.get('thesis_invalidation'), limit=8, max_len=220)}


def normalize_trade_report_detail_sections_r4_impl(report, *, fallback_summaries, trim_text, clean_str_list, facade):
    executive = facade.normalize_trade_report_section(report, 'executive_summary', fallback_summaries.get('executive_summary', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    market_context = facade.normalize_trade_report_section(report, 'market_context_at_entry', fallback_summaries.get('market_context_at_entry', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    why_symbol = facade.normalize_trade_report_section(report, 'why_this_symbol_was_chosen', fallback_summaries.get('why_this_symbol_was_chosen', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    scanner_filters = facade.normalize_trade_report_section(report, 'scanner_filters', fallback_summaries.get('scanner_filters', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    entry_decision = facade.normalize_trade_report_section(report, 'entry_decision', fallback_summaries.get('entry_decision', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    holding_story = facade.normalize_trade_report_section(report, 'holding_monitoring_story', fallback_summaries.get('holding_monitoring_story', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    exit_decision = facade.normalize_trade_report_section(report, 'exit_decision', fallback_summaries.get('exit_decision', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    execution_quality = facade.normalize_trade_report_section(report, 'execution_quality', fallback_summaries.get('execution_quality', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    guard_result = facade.normalize_trade_report_section(report, 'guard_approval_result', fallback_summaries.get('guard_approval_result', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    reporter_eval = facade.normalize_trade_report_section(report, 'reporter_evaluation', fallback_summaries.get('reporter_evaluation', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    weak_points = facade.normalize_trade_report_section(report, 'errors_weaknesses_improvement_points', fallback_summaries.get('errors_weaknesses_improvement_points', ''), trim_text=trim_text, clean_str_list=clean_str_list)
    return {'executive_summary': executive, 'market_context': market_context, 'why_this_symbol': why_symbol, 'scanner_filters': scanner_filters, 'entry_decision': entry_decision, 'holding_monitoring_story': holding_story, 'exit_decision': exit_decision, 'execution_quality': execution_quality, 'guard_approval_result': guard_result, 'reporter_evaluation': reporter_eval, 'errors_weaknesses_improvement_points': weak_points, 'review_focus': {'why_entered': trim_text(entry_decision.get('summary'), max_len=320), 'why_held': trim_text(holding_story.get('summary'), max_len=320), 'why_exited': trim_text(exit_decision.get('summary'), max_len=320), 'execution_quality': trim_text(execution_quality.get('summary'), max_len=320), 'improvement_focus': trim_text(weak_points.get('summary'), max_len=320)}}


def normalize_trade_report_detail_meta_r4_impl(report, *, operator_conclusion_human, action, trim_text, clean_str_list, facade):
    final_conclusion = report.get('final_operator_conclusion') if isinstance(report.get('final_operator_conclusion'), dict) else {}
    generation = report.get('generation') if isinstance(report.get('generation'), dict) else {}
    return {'final_operator_conclusion': {'summary': trim_text(final_conclusion.get('summary'), max_len=1000) or trim_text(operator_conclusion_human.get('summary'), max_len=1000), 'current_action': trim_text(final_conclusion.get('current_action'), max_len=32) or trim_text(action, max_len=32), 'watch_next': clean_str_list(final_conclusion.get('watch_next'), limit=8, max_len=220) or clean_str_list(operator_conclusion_human.get('watch_next'), limit=8, max_len=220), 'thesis_invalidation': clean_str_list(final_conclusion.get('thesis_invalidation'), limit=8, max_len=220) or clean_str_list(operator_conclusion_human.get('thesis_invalidation'), limit=8, max_len=220)}, 'generation': {'status': trim_text(generation.get('status'), max_len=48) or 'not_captured', 'mode': trim_text(generation.get('mode'), max_len=48) or 'not_captured', 'model': trim_text(generation.get('model'), max_len=120) or 'not_captured', 'reason': trim_text(generation.get('reason'), max_len=320)}}


def collect_strategist_feedback_inputs_r4_impl(items, *, facade):
    if not isinstance(items, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        source = item.get('strategist_feedback_input') if isinstance(item.get('strategist_feedback_input'), dict) else (item.get('bundle_data') or {}).get('strategist_feedback_input') if isinstance(item.get('bundle_data'), dict) and isinstance((item.get('bundle_data') or {}).get('strategist_feedback_input'), dict) else (item.get('lifecycle_data') or {}).get('strategist_feedback_input') if isinstance(item.get('lifecycle_data'), dict) and isinstance((item.get('lifecycle_data') or {}).get('strategist_feedback_input'), dict) else (item.get('story_input_data') or {}).get('strategist_feedback_input') if isinstance(item.get('story_input_data'), dict) and isinstance((item.get('story_input_data') or {}).get('strategist_feedback_input'), dict) else {}
        if not isinstance(source, dict) or not source:
            continue
        normalized = facade.normalize_strategist_feedback_input(source)
        normalized['trade_id'] = str(item.get('trade_id') or normalized.get('trade_id') or '')
        normalized['story_id'] = str(item.get('story_id') or normalized.get('story_id') or '')
        normalized['run_id'] = str(item.get('run_id') or normalized.get('run_id') or '')
        normalized['symbol'] = str(item.get('symbol') or normalized.get('selected_symbol') or '')
        normalized['trade_status'] = str(item.get('trade_status') or item.get('status') or normalized.get('trade_status') or '')
        normalized['final_action'] = str(item.get('final_action') or item.get('action') or normalized.get('final_action') or '')
        result_pct = item.get('result_pct')
        if result_pct in (None, '') and isinstance(item.get('summary'), dict):
            result_pct = (item.get('summary') or {}).get('result_pct')
        normalized['result_pct'] = result_pct
        out.append(normalized)
    return out


def build_trade_report_recent_feedback_pack_r4_impl(items, *, window_size, facade):
    window = facade.build_trade_report_recent_feedback_view(items, window_size=window_size)
    return {'schema_version': 'strategist_feedback_recent_window_pack.v1', 'payload_type': 'recent_strategist_feedback_window', 'available': bool(int(window.get('trades_considered') or 0) > 0), 'window': window}


def load_trade_report_recent_feedback_pack_r4_impl(meta, payloads, *, default_window_size, facade):
    meta_obj = meta if isinstance(meta, dict) else {}
    payload_obj = payloads if isinstance(payloads, dict) else {}
    items = payload_obj.get('recent_feedback_items') if payload_obj.get('recent_feedback_items') is not None else meta_obj.get('recent_feedback_items')
    window_size = payload_obj.get('recent_feedback_window_size') if payload_obj.get('recent_feedback_window_size') not in (None, '') else meta_obj.get('recent_feedback_window_size')
    return facade.build_trade_report_recent_feedback_pack(items, window_size=int(window_size or default_window_size))


def load_time_bucketed_trade_report_recent_feedback_pack_r4_impl(meta, payloads, *, default_window_size, facade):
    """Future-facing time-bucketed contract candidate for non-UI consumers.

    This helper does not replace the existing recent-window contract.
    It wraps the existing recent-window pack in a parallel bucketed surface so
    future runtime or reporting consumers can depend on a common bucket shape
    without changing current behavior.

    Current buckets intentionally stay minimal:
    - overall_recent: existing recent-window pack reuse path
    - daily_recent: optional shell fed by meta/payload inputs if available
    - symbol_recent: optional shell fed by meta/payload inputs if available
    """
    meta_obj = meta if isinstance(meta, dict) else {}
    payload_obj = payloads if isinstance(payloads, dict) else {}

    def _resolve_items(base_key: str) -> Any:
        bucket_items_key = f'{base_key}_feedback_items'
        if payload_obj.get(bucket_items_key) is not None:
            return payload_obj.get(bucket_items_key)
        if meta_obj.get(bucket_items_key) is not None:
            return meta_obj.get(bucket_items_key)
        if base_key == 'recent':
            if payload_obj.get('recent_feedback_items') is not None:
                return payload_obj.get('recent_feedback_items')
            return meta_obj.get('recent_feedback_items')
        return None

    def _resolve_window_size(base_key: str) -> int:
        bucket_window_key = f'{base_key}_feedback_window_size'
        if payload_obj.get(bucket_window_key) not in (None, ''):
            return int(payload_obj.get(bucket_window_key) or default_window_size)
        if meta_obj.get(bucket_window_key) not in (None, ''):
            return int(meta_obj.get(bucket_window_key) or default_window_size)
        if base_key == 'recent':
            if payload_obj.get('recent_feedback_window_size') not in (None, ''):
                return int(payload_obj.get('recent_feedback_window_size') or default_window_size)
            if meta_obj.get('recent_feedback_window_size') not in (None, ''):
                return int(meta_obj.get('recent_feedback_window_size') or default_window_size)
        return int(default_window_size)

    def _bucket(base_key: str) -> Dict[str, Any]:
        packed = facade.build_trade_report_recent_feedback_pack(_resolve_items(base_key), window_size=_resolve_window_size(base_key))
        return {'available': bool(packed.get('available')), 'window': dict(packed.get('window') or {})}
    buckets = {'overall_recent': _bucket('recent'), 'daily_recent': _bucket('daily_recent'), 'symbol_recent': _bucket('symbol_recent')}
    return {'schema_version': 'strategist_feedback_time_bucket_pack.v1', 'payload_type': 'time_bucketed_recent_strategist_feedback', 'available': any((bool((bucket or {}).get('available')) for bucket in buckets.values())), 'buckets': buckets}


def build_linked_trade_report_card_r4_impl(trade_report_meta, report_payloads, *, primary_symbol, execution_action, normalize_ai_report_diagnostics, facade):
    story_input_data = dict(report_payloads.get('story_input_data') or {})
    lifecycle_data = dict(report_payloads.get('lifecycle_data') or {})
    report_data = dict(report_payloads.get('report_data') or {})
    payload_sources = dict(report_payloads.get('payload_sources') or {})
    payload_paths = dict(report_payloads.get('paths') or {})
    ai_diag = trade_report_meta.get('ai_report_diagnostics') if isinstance(trade_report_meta.get('ai_report_diagnostics'), dict) else {}
    if not ai_diag:
        ai_diag = normalize_ai_report_diagnostics({}, report_exists=bool(trade_report_meta.get('trade_report_json_path') or trade_report_meta.get('trade_report_md_path')), lifecycle_status=trade_report_meta.get('lifecycle_status'), story_type=trade_report_meta.get('story_type'), model_hint=trade_report_meta.get('report_generation_model'))
    return {'report_available': bool(trade_report_meta.get('report_available')), 'trade_id': str(trade_report_meta.get('trade_id') or ''), 'story_id': str(trade_report_meta.get('story_id') or ''), 'story_type': str(trade_report_meta.get('story_type') or ''), 'story_type_label': str(trade_report_meta.get('story_type_label') or ''), 'story_type_badge_class': str(trade_report_meta.get('story_type_badge_class') or 'status-badge'), 'lifecycle_status': str(trade_report_meta.get('lifecycle_status') or ''), 'lifecycle_summary': str(trade_report_meta.get('lifecycle_summary') or ''), 'execution_mode_label': str(trade_report_meta.get('execution_mode_label') or '-'), 'report_status': str(trade_report_meta.get('report_status') or ai_diag.get('report_status') or 'skipped'), 'report_status_label': str(trade_report_meta.get('report_status_label') or ai_diag.get('report_status_label') or ''), 'report_status_badge_class': str(trade_report_meta.get('report_status_badge_class') or ai_diag.get('report_status_badge_class') or 'status-badge'), 'report_reason_code': str(trade_report_meta.get('report_reason_code') or ai_diag.get('report_reason_code') or ''), 'report_reason_human': str(trade_report_meta.get('report_reason_human') or ai_diag.get('report_reason_human') or ''), 'report_next_expected_step': str(trade_report_meta.get('report_next_expected_step') or ai_diag.get('next_expected_step') or ''), 'report_generation_model': str(trade_report_meta.get('report_generation_model') or ai_diag.get('llm_model_used') or ''), 'report_generation_provider': str(trade_report_meta.get('report_generation_provider') or ai_diag.get('llm_provider') or 'OpenRouter'), 'report_summary': str(trade_report_meta.get('report_summary') or ''), 'reporter_status_human': str(trade_report_meta.get('reporter_status_human') or ''), 'report_link': str(trade_report_meta.get('report_link') or ''), 'operator_brief_available': bool(trade_report_meta.get('operator_brief_available')), 'operator_brief_link': str(trade_report_meta.get('operator_brief_link') or ''), 'operator_brief_json_path': str(trade_report_meta.get('operator_brief_json_path') or ''), 'operator_brief_md_path': str(trade_report_meta.get('operator_brief_md_path') or ''), 'trade_report_json_path': str(trade_report_meta.get('trade_report_json_path') or ''), 'trade_report_md_path': str(trade_report_meta.get('trade_report_md_path') or ''), 'trade_story_input_path': str(trade_report_meta.get('trade_story_input_path') or ''), 'ai_trade_report_json_path': str(trade_report_meta.get('ai_trade_report_json_path') or trade_report_meta.get('trade_report_json_path') or ''), 'ai_trade_report_md_path': str(trade_report_meta.get('ai_trade_report_md_path') or trade_report_meta.get('trade_report_md_path') or ''), 'ai_trade_report_input_path': str(trade_report_meta.get('ai_trade_report_input_path') or trade_report_meta.get('trade_story_input_path') or ''), 'trade_lifecycle_json_path': str(trade_report_meta.get('trade_lifecycle_json_path') or ''), 'aggregated_bundle_path': str(trade_report_meta.get('aggregated_bundle_path') or ''), 'trade_root_path': str(trade_report_meta.get('trade_root_path') or ''), 'strategist_llm_response_path': str(trade_report_meta.get('strategist_llm_response_path') or ''), 'ai_trade_report_llm_response_path': str(trade_report_meta.get('ai_trade_report_llm_response_path') or ''), 'brief_llm_response_path': str(trade_report_meta.get('brief_llm_response_path') or ''), 'trade_provenance_json_path': str(trade_report_meta.get('trade_provenance_json_path') or ''), 'trade_health_json_path': str(trade_report_meta.get('trade_health_json_path') or ''), 'trade_artifact_links_json_path': str(trade_report_meta.get('trade_artifact_links_json_path') or ''), 'section_provenance': dict(trade_report_meta.get('section_provenance') or {}) if isinstance(trade_report_meta.get('section_provenance'), dict) else {}, 'symbol': str(trade_report_meta.get('symbol') or primary_symbol or ''), 'action': str(trade_report_meta.get('action') or execution_action or ''), 'missing_reason': str(trade_report_meta.get('report_reason_human') or ai_diag.get('report_reason_human') or ''), 'ai_report_diagnostics': ai_diag, 'story_input_data': story_input_data if isinstance(story_input_data, dict) else {}, 'lifecycle_data': lifecycle_data if isinstance(lifecycle_data, dict) else {}, 'report_data': report_data if isinstance(report_data, dict) else {}, 'report_payload_sources': payload_sources, 'report_payload_paths': payload_paths}


def build_unlinked_trade_report_card_r4_impl(*, execution_action, monitor_reason_text, symbol, normalize_ai_report_diagnostics, report_reason_human, report_next_step, facade):
    execution_action_upper = str(execution_action or '').upper()
    monitor_reason_lower = str(monitor_reason_text or '').strip().lower()
    if execution_action_upper in {'BUY', 'SELL'}:
        reason_code = 'missing_report_linkage'
        status = 'failed'
    elif 'hold' in monitor_reason_lower:
        reason_code = 'hold_only_run'
        status = 'skipped'
    else:
        reason_code = 'decision_only_run'
        status = 'skipped'
    ai_diag = normalize_ai_report_diagnostics({'report_status': status, 'report_reason_code': reason_code, 'report_reason_human': report_reason_human(reason_code), 'next_expected_step': report_next_step(reason_code), 'generation_attempted': False, 'story_input_available': False, 'report_output_available': False}, report_exists=False, lifecycle_status='', story_type='decision_only' if status == 'skipped' else '', model_hint='')
    return {'report_available': False, 'trade_id': '', 'story_id': '', 'story_type': '', 'story_type_label': 'No linked trade report', 'story_type_badge_class': 'status-badge', 'lifecycle_status': '', 'lifecycle_summary': '', 'execution_mode_label': '-', 'report_status': str(ai_diag.get('report_status') or 'skipped'), 'report_status_label': str(ai_diag.get('report_status_label') or ''), 'report_status_badge_class': str(ai_diag.get('report_status_badge_class') or 'status-badge'), 'report_reason_code': str(ai_diag.get('report_reason_code') or ''), 'report_reason_human': str(ai_diag.get('report_reason_human') or ''), 'report_next_expected_step': str(ai_diag.get('next_expected_step') or ''), 'report_generation_model': str(ai_diag.get('llm_model_used') or ''), 'report_generation_provider': str(ai_diag.get('llm_provider') or 'OpenRouter'), 'report_summary': '', 'reporter_status_human': '', 'report_link': '', 'operator_brief_available': False, 'operator_brief_link': '', 'operator_brief_json_path': '', 'operator_brief_md_path': '', 'trade_report_json_path': '', 'trade_report_md_path': '', 'trade_story_input_path': '', 'ai_trade_report_json_path': '', 'ai_trade_report_md_path': '', 'ai_trade_report_input_path': '', 'trade_lifecycle_json_path': '', 'aggregated_bundle_path': '', 'trade_root_path': '', 'strategist_llm_response_path': '', 'ai_trade_report_llm_response_path': '', 'brief_llm_response_path': '', 'trade_provenance_json_path': '', 'trade_health_json_path': '', 'trade_artifact_links_json_path': '', 'section_provenance': {}, 'symbol': str(symbol or ''), 'action': str(execution_action or ''), 'missing_reason': str(ai_diag.get('report_reason_human') or 'No linked trade report for this run.'), 'ai_report_diagnostics': ai_diag, 'story_input_data': {}, 'lifecycle_data': {}, 'report_data': {}}


def normalize_operator_brief_detail_payload_r4_impl(brief, *, clean_str_list, facade):
    sections = brief.get('sections') if isinstance(brief.get('sections'), dict) else {}
    executive = sections.get('executive_decision') if isinstance(sections.get('executive_decision'), dict) else {}
    ai_trade = sections.get('ai_trade_report') if isinstance(sections.get('ai_trade_report'), dict) else {}
    conclusion = sections.get('operator_conclusion') if isinstance(sections.get('operator_conclusion'), dict) else {}
    return {'headline': str(brief.get('headline') or ''), 'status': str(brief.get('status') or ''), 'model': str(brief.get('model') or ''), 'saved_at': str(brief.get('saved_at') or ''), 'sections': sections, 'operator_takeaways': clean_str_list(brief.get('operator_takeaways'), limit=8, max_len=220), 'executive': executive, 'ai_trade': ai_trade, 'conclusion': conclusion, 'watch_next': clean_str_list(conclusion.get('watch_next'), limit=8, max_len=220), 'thesis_invalidation': clean_str_list(conclusion.get('thesis_invalidation'), limit=8, max_len=220)}


def build_operator_brief_detail_view_r4_impl(meta, brief, *, json_path, md_path, normalize_symbol, clean_str_list, facade):
    brief_view = facade.normalize_operator_brief_detail_payload(brief, clean_str_list=clean_str_list)
    sections = brief_view.get('sections') if isinstance(brief_view.get('sections'), dict) else {}
    executive = brief_view.get('executive') if isinstance(brief_view.get('executive'), dict) else {}
    ai_trade = brief_view.get('ai_trade') if isinstance(brief_view.get('ai_trade'), dict) else {}
    return {'found': True, 'trade_id': str(meta.get('trade_id') or meta.get('story_id') or ''), 'story_id': str(meta.get('story_id') or ''), 'run_id': str(meta.get('run_id') or ''), 'run_link': f"/runs/{meta.get('run_id')}" if str(meta.get('run_id') or '').strip() else '', 'report_link': str(meta.get('report_link') or ''), 'headline': str(brief_view.get('headline') or ''), 'status': str(brief_view.get('status') or ''), 'model': str(brief_view.get('model') or ''), 'saved_at': str(brief_view.get('saved_at') or ''), 'trade_summary': str(meta.get('report_summary') or ''), 'lifecycle_status': str(meta.get('lifecycle_status') or ''), 'story_type_label': str(meta.get('story_type_label') or ''), 'story_type_badge_class': str(meta.get('story_type_badge_class') or 'status-badge'), 'execution_mode_label': str(meta.get('execution_mode_label') or '-'), 'operator_takeaways': list(brief_view.get('operator_takeaways') or []), 'sections': sections, 'executive_action': str(executive.get('final_action') or executive.get('action') or meta.get('action') or '-'), 'executive_symbol': normalize_symbol(executive.get('symbol') or meta.get('symbol') or '', allow_test_symbols=True), 'ai_trade_status_label': str(ai_trade.get('status_label') or meta.get('report_status_label') or '-'), 'ai_trade_status_badge_class': str(ai_trade.get('status_badge_class') or meta.get('report_status_badge_class') or 'status-badge'), 'watch_next': list(brief_view.get('watch_next') or []), 'thesis_invalidation': list(brief_view.get('thesis_invalidation') or []), 'paths': {'operator_brief_json': str(json_path or ''), 'operator_brief_md': str(md_path or '')}, 'raw_brief': brief}


def extract_labeled_bullet_r4_impl(bullets, labels, *, facade):
    normalized_labels = [str(label or '').strip().lower() for label in labels if str(label or '').strip()]
    for bullet in bullets:
        text = str(bullet or '').strip()
        lower = text.lower()
        for label in normalized_labels:
            prefix = f'{label}:'
            if lower.startswith(prefix):
                return text.split(':', 1)[1].strip()
    return ''


def extract_labeled_int_r4_impl(bullets, labels, *, facade):
    value = facade.extract_labeled_bullet(bullets, labels)
    if not value:
        return None
    match = facade.re.search('-?\\d+', value)
    if not match:
        return None
    try:
        return int(match.group(0))
    except Exception:
        return None


def parse_canonical_filter_bullets_r4_impl(bullets, *, facade):
    rows: List[Dict[str, str]] = []
    for bullet in bullets:
        text = str(bullet or '').strip()
        if not text or ':' not in text:
            continue
        name_raw, rest = text.split(':', 1)
        name = name_raw.strip().title()
        status = 'INFO'
        note = rest.strip()
        match = facade.re.match('\\s*(PASS|FAIL|PARTIAL|SKIPPED|NOT_AVAILABLE)\\s*[-:]?\\s*(.*)$', note, flags=facade.re.IGNORECASE)
        if match:
            status = match.group(1).upper()
            note = match.group(2).strip() or note.strip()
        rows.append({'name': name, 'status': status, 'note': note})
    return rows


def normalize_canonical_monitor_snapshot_r4_impl(snapshot, story_monitor, *, format_duration, format_percent, format_float, friendly_exit_reason, facade):
    if not isinstance(snapshot, dict):
        snapshot = {}
    if not isinstance(story_monitor, dict):
        story_monitor = {}
    posture = str(snapshot.get('posture') or story_monitor.get('posture') or '').strip()
    trigger_type = str(snapshot.get('trigger_type') or story_monitor.get('trigger_type') or '').strip()
    raw_effective_reason = str(snapshot.get('effective_stop_reason') or story_monitor.get('effective_stop_reason') or trigger_type or '').strip()
    effective_reason = friendly_exit_reason(raw_effective_reason) if raw_effective_reason else ''
    stop_loss_pct = snapshot.get('stop_loss_pct')
    if stop_loss_pct in (None, ''):
        stop_loss_pct = story_monitor.get('stop_loss_pct')
    effective_stop_loss_pct = snapshot.get('effective_stop_loss_pct')
    if effective_stop_loss_pct in (None, ''):
        effective_stop_loss_pct = story_monitor.get('effective_stop_loss_pct')
    take_profit_pct = snapshot.get('take_profit_pct')
    if take_profit_pct in (None, ''):
        take_profit_pct = story_monitor.get('take_profit_pct')
    position_age_seconds = snapshot.get('position_age_seconds')
    if position_age_seconds in (None, ''):
        position_age_seconds = story_monitor.get('position_age_seconds')
    active_exit_axis = str(snapshot.get('active_exit_axis') or '').strip()
    if not active_exit_axis:
        if trigger_type:
            active_exit_axis = friendly_exit_reason(trigger_type)
        elif raw_effective_reason:
            active_exit_axis = friendly_exit_reason(raw_effective_reason)
        elif posture.upper() == 'HOLD':
            active_exit_axis = 'No trigger yet'
    else:
        active_exit_axis = friendly_exit_reason(active_exit_axis)

    def _fmt_optional_price(value: Any) -> str:
        if value in (None, ''):
            return ''
        return format_float(value, 2)

    def _fmt_optional_pct(value: Any) -> str:
        if value in (None, ''):
            return ''
        return format_percent(value, 2)
    watch_axes = [str(x or '') for x in list(snapshot.get('watch_axes') or []) if str(x or '').strip()]
    hold_reasons = [str(x or '') for x in list(snapshot.get('hold_reasons') or []) if str(x or '').strip()]
    exit_triggers = [str(x or '') for x in list(snapshot.get('exit_triggers') or []) if str(x or '').strip()]
    if not hold_reasons:
        hold_reasons = [str(x or '') for x in list(story_monitor.get('bullets') or []) if str(x or '').strip()][:4]
    return {'posture': posture, 'holding_time': format_duration(position_age_seconds) if position_age_seconds not in (None, '') else str(snapshot.get('holding_time') or '').strip(), 'stop_loss': format_percent(stop_loss_pct, 2) if stop_loss_pct not in (None, '') else str(snapshot.get('stop_loss') or '').strip(), 'effective_stop': format_percent(effective_stop_loss_pct, 2) if effective_stop_loss_pct not in (None, '') else str(snapshot.get('effective_stop') or '').strip(), 'effective_stop_reason': effective_reason, 'take_profit': format_percent(take_profit_pct, 2) if take_profit_pct not in (None, '') else str(snapshot.get('take_profit') or '').strip(), 'current_price': _fmt_optional_price(snapshot.get('current_price')), 'average_price': _fmt_optional_price(snapshot.get('average_price')), 'peak_price': _fmt_optional_price(snapshot.get('peak_price')), 'current_drawdown': _fmt_optional_pct(snapshot.get('current_drawdown')), 'peak_drawdown': _fmt_optional_pct(snapshot.get('peak_drawdown')), 'vwap_distance': _fmt_optional_pct(snapshot.get('vwap_distance')), 'price_source': str(snapshot.get('price_source') or story_monitor.get('price_source') or '').strip(), 'feature_source': str(snapshot.get('feature_source') or story_monitor.get('feature_source') or '').strip(), 'price_source_policy': str(snapshot.get('price_source_policy') or story_monitor.get('price_source_policy') or '').strip(), 'active_exit_axis': active_exit_axis, 'watch_axes': watch_axes, 'hold_reasons': hold_reasons[:6], 'exit_triggers': exit_triggers[:6]}


def brief_headline_text_r4_impl(row, *, trim_text, facade):
    item = row if isinstance(row, dict) else {}
    for key in ('title', 'headline', 'summary', 'description', 'text', 'news_title'):
        text = trim_text(item.get(key), max_len=180)
        if text:
            return text
    return ''


def brief_headline_matches_symbol_r4_impl(row, symbol, *, normalize_symbol, facade):
    item = row if isinstance(row, dict) else {}
    target = facade.brief_norm_symbol_text(symbol, normalize_symbol=normalize_symbol)
    if not target:
        return False
    for candidate in (item.get('symbol'), item.get('code'), item.get('ticker'), item.get('query_target'), item.get('query'), item.get('news_query_target')):
        if facade.brief_norm_symbol_text(candidate, normalize_symbol=normalize_symbol) == target:
            return True
    for key in ('symbols', 'tickers', 'related_symbols'):
        values = item.get(key)
        if not isinstance(values, list):
            continue
        for candidate in values:
            if facade.brief_norm_symbol_text(candidate, normalize_symbol=normalize_symbol) == target:
                return True
    joined = ' '.join([str(item.get('title') or ''), str(item.get('headline') or ''), str(item.get('summary') or ''), str(item.get('description') or ''), str(item.get('query_target') or '')]).upper()
    return bool(target and target in joined)
