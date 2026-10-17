"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def build_trade_report_detail_view_r4_impl(meta, payloads, *, trim_text, clean_str_list, normalize_symbol, story_type_label, story_type_badge_class, normalize_ai_report_diagnostics, facade):
    report = payloads.get('report_data') if isinstance(payloads.get('report_data'), dict) else {}
    bundle = payloads.get('bundle_data') if isinstance(payloads.get('bundle_data'), dict) else {}
    lifecycle = payloads.get('lifecycle_data') if isinstance(payloads.get('lifecycle_data'), dict) else {}
    market_context_human = bundle.get('market_context_human') if isinstance(bundle.get('market_context_human'), dict) else {}
    scanner_reason_human = bundle.get('scanner_reason_human') if isinstance(bundle.get('scanner_reason_human'), dict) else {}
    filters_human = bundle.get('filters_human') if isinstance(bundle.get('filters_human'), dict) else {}
    monitor_reason_human = bundle.get('monitor_reason_human') if isinstance(bundle.get('monitor_reason_human'), dict) else {}
    monitor_reason_human = bundle.get('monitor_reason_human') if isinstance(bundle.get('monitor_reason_human'), dict) else {}
    guard_reason_human = bundle.get('guard_reason_human') if isinstance(bundle.get('guard_reason_human'), dict) else {}
    execution_outcome_human = bundle.get('execution_outcome_human') if isinstance(bundle.get('execution_outcome_human'), dict) else {}
    reporter_status_human = bundle.get('reporter_status_human') if isinstance(bundle.get('reporter_status_human'), dict) else {}
    operator_conclusion_human = bundle.get('operator_conclusion_human') if isinstance(bundle.get('operator_conclusion_human'), dict) else {}
    lifecycle_entry = lifecycle.get('entry') if isinstance(lifecycle.get('entry'), dict) else {}
    lifecycle_holding = lifecycle.get('holding') if isinstance(lifecycle.get('holding'), dict) else {}
    lifecycle_exit = lifecycle.get('exit') if isinstance(lifecycle.get('exit'), dict) else {}
    lifecycle_summary_obj = lifecycle.get('summary') if isinstance(lifecycle.get('summary'), dict) else {}
    lifecycle_reporter = lifecycle.get('reporter') if isinstance(lifecycle.get('reporter'), dict) else {}
    sections = facade.normalize_trade_report_detail_sections(report, fallback_summaries={'executive_summary': lifecycle_summary_obj.get('lifecycle_summary_human') or operator_conclusion_human.get('summary') or execution_outcome_human.get('summary') or '', 'market_context_at_entry': (lifecycle_entry.get('strategist_context') or {}).get('market_context_summary') if isinstance(lifecycle_entry.get('strategist_context'), dict) else market_context_human.get('summary') or '', 'why_this_symbol_was_chosen': lifecycle_entry.get('reason_human') or scanner_reason_human.get('summary') or '', 'scanner_filters': filters_human.get('summary') or '', 'entry_decision': lifecycle_entry.get('reason_human') or scanner_reason_human.get('summary') or '', 'holding_monitoring_story': monitor_reason_human.get('summary') or (f"Holding phase captured {len(list(lifecycle_holding.get('run_ids') or []))} runs." if list(lifecycle_holding.get('run_ids') or []) else ''), 'exit_decision': lifecycle_exit.get('reason_human') or ('Position is still open; no closing SELL execution has been captured yet.' if str(lifecycle.get('status') or '').lower() == 'open' else ''), 'execution_quality': execution_outcome_human.get('summary') or '', 'guard_approval_result': guard_reason_human.get('summary') or '', 'reporter_evaluation': reporter_status_human.get('summary') or '', 'errors_weaknesses_improvement_points': 'No explicit weaknesses were captured beyond standard warnings.'}, trim_text=trim_text, clean_str_list=clean_str_list)
    executive = sections.get('executive_summary') if isinstance(sections.get('executive_summary'), dict) else {}
    market_context = sections.get('market_context') if isinstance(sections.get('market_context'), dict) else {}
    why_symbol = sections.get('why_this_symbol') if isinstance(sections.get('why_this_symbol'), dict) else {}
    scanner_filters = sections.get('scanner_filters') if isinstance(sections.get('scanner_filters'), dict) else {}
    entry_decision = sections.get('entry_decision') if isinstance(sections.get('entry_decision'), dict) else {}
    holding_story = sections.get('holding_monitoring_story') if isinstance(sections.get('holding_monitoring_story'), dict) else {}
    exit_decision = sections.get('exit_decision') if isinstance(sections.get('exit_decision'), dict) else {}
    execution_quality = sections.get('execution_quality') if isinstance(sections.get('execution_quality'), dict) else {}
    guard_result = sections.get('guard_approval_result') if isinstance(sections.get('guard_approval_result'), dict) else {}
    reporter_eval = sections.get('reporter_evaluation') if isinstance(sections.get('reporter_evaluation'), dict) else {}
    weak_points = sections.get('errors_weaknesses_improvement_points') if isinstance(sections.get('errors_weaknesses_improvement_points'), dict) else {}
    timeline = [row for row in list(report.get('full_timeline') or report.get('timeline') or lifecycle.get('timeline') or bundle.get('timeline') or []) if isinstance(row, dict)][:24]
    report_exists = bool(payloads.get('report_exists'))
    action = trim_text(report.get('action'), max_len=32) or trim_text(meta.get('action'), max_len=32) or 'WAIT'
    detail_meta = facade.normalize_trade_report_detail_meta(report, operator_conclusion_human=operator_conclusion_human, action=action, trim_text=trim_text, clean_str_list=clean_str_list)
    generation = detail_meta.get('generation') if isinstance(detail_meta.get('generation'), dict) else {}
    diagnostics = normalize_ai_report_diagnostics(report.get('ai_report_diagnostics') if isinstance(report.get('ai_report_diagnostics'), dict) else bundle.get('ai_report_diagnostics') if isinstance(bundle.get('ai_report_diagnostics'), dict) else lifecycle.get('ai_report_diagnostics') if isinstance(lifecycle.get('ai_report_diagnostics'), dict) else {}, report_exists=report_exists, lifecycle_status=meta.get('lifecycle_status') or lifecycle.get('status'), story_type=meta.get('story_type') or report.get('story_type'), model_hint=generation.get('model'), generation=generation)
    symbol = normalize_symbol(report.get('symbol') or meta.get('symbol') or '', allow_test_symbols=True)
    reporter_status = trim_text(reporter_eval.get('status'), max_len=48) or trim_text(reporter_status_human.get('status'), max_len=48) or '-'
    reporter_grade = trim_text(reporter_eval.get('grade'), max_len=24) or trim_text(reporter_status_human.get('grade'), max_len=24) or '-'
    review_focus = sections.get('review_focus') if isinstance(sections.get('review_focus'), dict) else {}
    strategist_feedback_input = facade.normalize_strategist_feedback_input(bundle.get('strategist_feedback_input') if isinstance(bundle.get('strategist_feedback_input'), dict) else lifecycle.get('strategist_feedback_input') if isinstance(lifecycle.get('strategist_feedback_input'), dict) else report.get('strategist_feedback_input') if isinstance(report.get('strategist_feedback_input'), dict) else {})
    recent_feedback_items = payloads.get('recent_feedback_items') if payloads.get('recent_feedback_items') is not None else meta.get('recent_feedback_items')
    recent_feedback_window_size = payloads.get('recent_feedback_window_size') if payloads.get('recent_feedback_window_size') not in (None, '') else meta.get('recent_feedback_window_size')
    strategist_feedback_recent_window = facade.build_trade_report_recent_feedback_view(recent_feedback_items, window_size=int(recent_feedback_window_size or 10))
    return {'found': True, 'trade_id': str(meta.get('trade_id') or meta.get('story_id') or ''), 'story_id': str(meta.get('story_id') or ''), 'run_id': str(meta.get('run_id') or ''), 'run_link': f"/runs/{meta.get('run_id')}" if str(meta.get('run_id') or '').strip() else '', 'symbol': symbol, 'action': action, 'status': str(meta.get('lifecycle_status') or report.get('status') or lifecycle.get('status') or ''), 'lifecycle_summary': str(meta.get('lifecycle_summary') or lifecycle_summary_obj.get('lifecycle_summary_human') or ''), 'story_type': str(meta.get('story_type') or report.get('story_type') or ''), 'story_type_label': str(meta.get('story_type_label') or story_type_label(report.get('story_type'))), 'story_type_badge_class': str(meta.get('story_type_badge_class') or story_type_badge_class(report.get('story_type'))), 'execution_mode_label': str(meta.get('execution_mode_label') or report.get('execution_mode_label') or 'not captured'), 'report_available': bool(diagnostics.get('report_status') == 'available' and report_exists), 'report_summary': str(meta.get('report_summary') or executive.get('summary') or ''), 'reporter_status_human': str(meta.get('reporter_status_human') or reporter_eval.get('summary') or ''), 'ai_report_diagnostics': diagnostics, 'executive_summary': executive, 'market_context': market_context, 'why_this_symbol': why_symbol, 'entry_decision': entry_decision, 'holding_monitoring_story': holding_story, 'exit_decision': exit_decision, 'scanner_logic_and_filters': scanner_filters, 'monitor_trigger_reasoning': holding_story, 'guard_approval_result': guard_result, 'execution_result': execution_quality, 'execution_quality': execution_quality, 'review_focus': review_focus, 'strategist_feedback_input': strategist_feedback_input, 'strategist_feedback_recent_window': strategist_feedback_recent_window, 'reporter_evaluation': {**reporter_eval, 'status': reporter_status, 'grade': reporter_grade or trim_text(lifecycle_reporter.get('grade'), max_len=24) or '-'}, 'errors_weaknesses_improvement_points': weak_points, 'timeline': timeline, 'full_timeline': timeline, 'trade_lifecycle': lifecycle if isinstance(lifecycle, dict) else {}, 'final_operator_conclusion': detail_meta.get('final_operator_conclusion') if isinstance(detail_meta.get('final_operator_conclusion'), dict) else {}, 'generation': generation, 'paths': {'trade_report_json': str(meta.get('trade_report_json_path') or ''), 'trade_report_md': str(meta.get('trade_report_md_path') or ''), 'trade_story_input': str(meta.get('trade_story_input_path') or ''), 'ai_trade_report_json': str(meta.get('ai_trade_report_json_path') or meta.get('trade_report_json_path') or ''), 'ai_trade_report_md': str(meta.get('ai_trade_report_md_path') or meta.get('trade_report_md_path') or ''), 'ai_trade_report_input': str(meta.get('ai_trade_report_input_path') or meta.get('trade_story_input_path') or ''), 'trade_lifecycle': str(meta.get('trade_lifecycle_json_path') or ''), 'aggregated_execution_bundle': str(meta.get('aggregated_bundle_path') or ''), 'strategist_llm_response': str(meta.get('strategist_llm_response_path') or ''), 'ai_trade_report_llm_response': str(meta.get('ai_trade_report_llm_response_path') or ''), 'brief_llm_response': str(meta.get('brief_llm_response_path') or '')}, 'raw_report': report if isinstance(report, dict) else {}}


def load_reporter_snippet_for_run_r4_impl(reports_root, run_id, run_day, *, read_json, facade):
    path = reports_root / 'dev' / 'analysis' / 'reporter_analysis' / f'reporter_analysis_{run_day}.json'
    report = read_json(path)
    if not report:
        return {'report_path': str(path), 'found': False, 'ai_summary': '', 'ai_run_grade': '', 'reason': 'same_day_report_missing'}
    chains = (report.get('decision_trace_chain_summary') or {}).get('chains') or [] if isinstance(report.get('decision_trace_chain_summary'), dict) else []
    chain = next((c for c in chains if isinstance(c, dict) and str(c.get('run_id') or '').strip() == str(run_id or '').strip()), {})
    if not chain:
        return {'report_path': str(path), 'found': False, 'ai_summary': '', 'ai_run_grade': str(report.get('ai_run_grade') or ''), 'reason': 'run_not_linked_in_same_day_report'}
    return {'report_path': str(path), 'found': True, 'ai_summary': str(report.get('ai_summary') or ''), 'ai_run_grade': str(report.get('ai_run_grade') or ''), 'chain': chain}
