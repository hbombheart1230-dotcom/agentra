"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/single_trade_report.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _same_day_reporter_paths_r4_impl(*, root, day, facade):
    reporter_dir = root / 'reports' / 'dev' / 'analysis' / 'reporter_analysis'
    return (reporter_dir / f'reporter_analysis_{day}.json', reporter_dir / f'reporter_analysis_{day}.md')


def _find_open_trade_id_r4_impl(trade_day_root, symbol, *, facade):
    for trade_dir in reversed(list(facade._matching_trade_dirs(trade_day_root, symbol))):
        bundle = facade._read_json(trade_dir / 'lifecycle_bundle.json')
        lifecycle = bundle.get('lifecycle') if isinstance(bundle.get('lifecycle'), dict) else {}
        exit_payload = lifecycle.get('exit') if isinstance(lifecycle.get('exit'), dict) else {}
        exit_available = bool((bundle.get('exit') or {}).get('available')) if isinstance(bundle.get('exit'), dict) else False
        if exit_payload or exit_available:
            continue
        status = str(bundle.get('trade_lifecycle_status') or '').strip().lower()
        if status in {'', 'open'}:
            return trade_dir.name
    return ''


def _build_trade_report_inputs_r4_impl(trade_id, state, *, root, facade):
    day = facade._resolve_trade_day(state, root=root)
    trade_paths = facade.trade_artifact_paths(root / 'reports', day, trade_id)
    run_id = str(state.get('run_id') or '').strip()
    symbol = facade._execution_symbol(state)
    action = facade._execution_action(state)
    execution = facade._execution_payload(state)
    monitor = state.get('monitor_output') if isinstance(state.get('monitor_output'), dict) else {}
    scanner = state.get('scanner_output') if isinstance(state.get('scanner_output'), dict) else {}
    commander = state.get('commander_decision') if isinstance(state.get('commander_decision'), dict) else {}
    supervisor = state.get('supervisor_output') if isinstance(state.get('supervisor_output'), dict) else {}
    strategist = facade._entry_strategist_context(state, symbol)
    execution_ts = str(execution.get('ts') or state.get('ts') or facade._utc_iso()).strip()
    execution_details = facade._execution_details_from_state(state)
    prior_entry = facade._load_json_dict(trade_paths['entry_json'])
    controlled_mock_lane = facade.build_controlled_lane_report_surface(state, day=day, root=root, prior_entry=prior_entry)
    entry_execution_details = dict(execution_details if action == 'BUY' else facade._null_execution_details())
    exit_execution_details = dict(execution_details if action == 'SELL' else facade._null_execution_details())
    monitor_snapshot = facade._build_monitor_snapshot(monitor, symbol=symbol, run_id=run_id, ts=execution_ts)
    hold_duration_sec = facade._safe_int(monitor.get('position_age_seconds')) or 0
    entry_reason = str((scanner.get('selected') or {} if isinstance(scanner.get('selected'), dict) else {}).get('why') or monitor.get('entry_reason') or monitor.get('decision_summary') or 'Entry context was recovered from the preserved strategist frame.')
    if controlled_mock_lane:
        entry_reason = f"{controlled_mock_lane.get('lane_label') or controlled_mock_lane.get('lane_id')} 독립 결정 레인이 {symbol}을 선택했습니다. 메인 Scanner 순위는 이 거래에 적용되지 않습니다."
    exit_reason = str(monitor.get('decision_summary') or monitor.get('entry_exit_reason') or execution.get('reason') or '')
    lifecycle_status = 'closed' if action == 'SELL' else 'open'
    execution_view = {'run_id': run_id, 'ts': execution_ts, 'action': action, 'symbol': symbol, 'qty': facade._safe_int((execution.get('order') or {}).get('qty') if isinstance(execution.get('order'), dict) else execution.get('qty')) or 0, 'status': str(execution.get('reason') or ''), 'ord_no': str(execution_details.get('order_id') or '')}
    reporter_js, reporter_md = facade._same_day_reporter_paths(root=root, day=day)
    reporter_day_obj = facade._load_json_dict(reporter_js)
    same_day_reporter_linkage = facade.build_same_day_reporter_linkage(reporter_obj=reporter_day_obj, reporter_js=reporter_js, reporter_md=reporter_md, entry_run_id='', exit_run_id='', entry_bundle={}, exit_bundle={})
    reporter_ctx = {'reporter_analysis_day_file_found': bool(same_day_reporter_linkage.get('reporter_analysis_day_file_found')), 'reporter_analysis_found': False, 'reporter_analysis_summary': str(reporter_day_obj.get('ai_summary') or '')}
    canonical_context = facade._build_canonical_context(root=root, day=day, run_id=run_id, commander=commander, strategist=strategist, scanner=scanner, monitor=monitor, supervisor=supervisor, execution=execution)
    artifacts = dict(canonical_context.get('artifacts') or {})
    artifacts['reporter_analysis_json'] = str(same_day_reporter_linkage.get('reporter_analysis_json_path') or '')
    artifacts['reporter_analysis_md'] = str(same_day_reporter_linkage.get('reporter_analysis_md_path') or '')
    evidence_provenance = dict(canonical_context.get('evidence_provenance') or {})
    if str(same_day_reporter_linkage.get('reporter_analysis_json_path') or '').strip():
        evidence_provenance['reporter'] = 'direct_artifact'
    elif str(same_day_reporter_linkage.get('reporter_analysis_md_path') or '').strip():
        evidence_provenance['reporter'] = 'direct_artifact'
    bundle_out: Dict[str, Any] = {'day': day, 'run_id': run_id, 'trade_id': trade_id, 'story_id': trade_id, 'execution': execution_view, 'commander': dict(commander), 'strategist': dict(strategist), 'scanner': dict(scanner), 'monitor': dict(monitor), 'supervisor': dict(supervisor), 'executor': {'execution_ok': bool(execution.get('ok')), 'broker_env': execution_details.get('broker_env') or '', 'effective_mode': execution.get('effective_mode') or execution.get('execution_mode') or '', 'execution_mode': execution_details.get('execution_mode') or ''}, 'execution_details': dict(execution_details), 'entry_execution_details': dict(entry_execution_details), 'exit_execution_details': dict(exit_execution_details), 'same_day_reporter_linkage': dict(same_day_reporter_linkage), 'failure_classification': {'entry_failure': False, 'hold_failure': False, 'exit_failure': False, 'execution_failure': False, 'reporting_failure': False}, 'hold_duration': facade._format_duration(hold_duration_sec), 'hold_duration_sec': hold_duration_sec, 'holding_phase_summary': '', 'hold_events_count': 0, 'monitor_context_snapshots': [], 'hold_signal_transitions': [], 'pre_exit_context_summary': {}, 'canonical_agent_artifacts': dict(canonical_context.get('canonical_agent_artifacts') or {}), 'evidence_provenance': evidence_provenance, 'artifacts': artifacts}
    if controlled_mock_lane:
        bundle_out['controlled_mock_lane'] = dict(controlled_mock_lane)
    story_contract = facade.build_story_contract(bundle_out)
    market_context_human = facade.build_market_context_human(dict(strategist))
    scanner_reason_human = facade.build_scanner_reason_human(dict(scanner), dict(strategist))
    if controlled_mock_lane:
        scanner_reason_human = {'summary': entry_reason, 'comparison': 'This trade did not use the main Scanner ranking authority.', 'bullets': [f"Independent lane: {controlled_mock_lane.get('lane_id')}", 'Scanner rank: not applicable', f"Signal ID: {controlled_mock_lane.get('signal_id') or 'not_captured'}"], 'selected_symbol': symbol, 'selected_rank': None, 'universe_size': None, 'selection_authority': 'deterministic_independent_lane'}
    filters_human = facade.build_filters_human(dict(scanner), dict(strategist), dict(supervisor))
    monitor_reason_human = facade.build_monitor_reason_human(dict(monitor), dict(execution_view))
    canonical_scanner = canonical_context.get('canonical_agent_artifacts', {}).get('scanner') if isinstance(canonical_context.get('canonical_agent_artifacts', {}).get('scanner'), dict) else dict(scanner)
    canonical_monitor = canonical_context.get('canonical_agent_artifacts', {}).get('monitor') if isinstance(canonical_context.get('canonical_agent_artifacts', {}).get('monitor'), dict) else dict(monitor)
    scanner_selection_trace = facade._build_scanner_selection_trace(scanner_reason_human, canonical_scanner)
    if scanner_selection_trace:
        scanner_reason_human['scanner_selection_trace'] = dict(scanner_selection_trace)
        if scanner_selection_trace.get('ranked_candidates'):
            scanner_reason_human['ranked_candidates'] = list(scanner_selection_trace.get('ranked_candidates') or [])
    monitor_thresholds = (canonical_monitor.get('thresholds_guards_used') or {}).get('thresholds') if isinstance((canonical_monitor.get('thresholds_guards_used') or {}).get('thresholds'), dict) else canonical_monitor.get('thresholds') if isinstance(canonical_monitor.get('thresholds'), dict) else canonical_monitor.get('threshold_snapshot') if isinstance(canonical_monitor.get('threshold_snapshot'), dict) else {}
    monitor_stop_policy_trace = facade._build_monitor_stop_policy_trace(canonical_monitor, monitor_thresholds)
    if monitor_stop_policy_trace:
        monitor_reason_human['monitor_stop_policy_trace'] = dict(monitor_stop_policy_trace)
    monitor_blocker_trace = facade._build_monitor_blocker_trace(monitor_reason_human)
    if monitor_blocker_trace:
        monitor_reason_human['monitor_blocker_trace'] = dict(monitor_blocker_trace)
    guard_reason_human = facade.build_guard_reason_human(dict(supervisor))
    execution_outcome_human = facade.build_execution_outcome_human(dict(execution_view), dict(bundle_out.get('executor') or {}), story_type=str(story_contract.get('story_type') or 'decision_only'), mode_label=str(story_contract.get('execution_mode_label') or ''))
    reporter_status_human = facade.build_reporter_status_human(reporter_ctx, reporter_day_obj)
    operator_conclusion_human = facade.build_operator_conclusion_human(execution=dict(execution_view), scanner_reason_human=scanner_reason_human, filters_human=filters_human, monitor_reason_human=monitor_reason_human, execution_outcome_human=execution_outcome_human, reporter_status_human=reporter_status_human)
    timeline = facade.build_timeline(commander=dict(commander), market_context_human=market_context_human, scanner_reason_human=scanner_reason_human, monitor_reason_human=monitor_reason_human, guard_reason_human=guard_reason_human, execution_outcome_human=execution_outcome_human, reporter_status_human=reporter_status_human, execution=dict(execution_view))
    bundle_out.update({'story_contract': dict(story_contract), 'market_context_human': dict(market_context_human), 'scanner_reason_human': dict(scanner_reason_human), 'filters_human': dict(filters_human), 'monitor_reason_human': dict(monitor_reason_human), 'guard_reason_human': dict(guard_reason_human), 'execution_outcome_human': dict(execution_outcome_human), 'reporter_status_human': dict(reporter_status_human), 'operator_conclusion_human': dict(operator_conclusion_human), 'timeline': list(timeline)})
    lifecycle = {'trade_id': trade_id, 'symbol': symbol, 'status': lifecycle_status, 'story_type': str(story_contract.get('story_type') or ''), 'execution_mode_label': str(story_contract.get('execution_mode_label') or ''), 'run_ids_all': [run_id] if run_id else [], 'entry': {'available': bool(action == 'BUY' or strategist), 'run_id': run_id if action == 'BUY' else '', 'ts': execution_ts if action == 'BUY' else '', 'action': 'BUY' if action in {'BUY', 'SELL'} else action, 'symbol': symbol, 'reason_human': entry_reason, 'strategist_context': dict(strategist), 'scanner_context': dict(scanner if action == 'BUY' else {}), 'monitor_context': dict(monitor if action == 'BUY' else {}), 'guard_context': dict(supervisor if action == 'BUY' else {}), 'execution_context': dict(entry_execution_details), 'execution_details': dict(entry_execution_details), **({'controlled_mock_lane': dict(controlled_mock_lane)} if action == 'BUY' and controlled_mock_lane else {})}, 'holding': {'run_ids': [run_id] if hold_duration_sec > 0 and run_id else [], 'holding_events': [{'run_id': run_id, 'ts': execution_ts, 'monitor_context': dict(monitor_snapshot)}] if hold_duration_sec > 0 else [], 'posture_history': [], 'monitor_updates': [str(monitor.get('decision_summary') or '')] if hold_duration_sec > 0 else [], 'hold_duration': facade._format_duration(hold_duration_sec), 'hold_duration_sec': hold_duration_sec, 'holding_phase_summary': '', 'hold_events_count': 0, 'monitor_context_snapshots': [], 'hold_signal_transitions': [], 'pre_exit_context_summary': {}}, 'exit': {'available': bool(action == 'SELL'), 'run_id': run_id if action == 'SELL' else '', 'ts': execution_ts if action == 'SELL' else '', 'action': action if action == 'SELL' else '', 'symbol': symbol, 'reason_human': exit_reason, 'monitor_context': dict(monitor if action == 'SELL' else {}), 'guard_context': dict(supervisor if action == 'SELL' else {}), 'execution_context': dict(exit_execution_details if action == 'SELL' else {}), 'execution_details': dict(exit_execution_details), 'position_age_seconds': hold_duration_sec if action == 'SELL' else None}, 'summary': {'holding_duration': facade._format_duration(hold_duration_sec), 'entry_reason_human': entry_reason, 'exit_reason_human': exit_reason, 'lifecycle_summary_human': str(execution_outcome_human.get('summary') or ''), 'operator_conclusion_human': str(operator_conclusion_human.get('summary') or '')}, 'reporter': {}, 'timeline': list(timeline), 'same_day_reporter_linkage': dict(bundle_out.get('same_day_reporter_linkage') or {}), 'execution_details': dict(execution_details)}
    holding_phase_observability = facade.build_holding_phase_observability(lifecycle, monitor_timeline={})
    lifecycle['holding']['hold_duration'] = holding_phase_observability.get('hold_duration')
    lifecycle['holding']['hold_duration_sec'] = holding_phase_observability.get('hold_duration_sec')
    lifecycle['holding']['holding_phase_summary'] = holding_phase_observability.get('holding_phase_summary')
    lifecycle['holding']['hold_events_count'] = holding_phase_observability.get('hold_events_count')
    lifecycle['holding']['monitor_context_snapshots'] = list(holding_phase_observability.get('monitor_context_snapshots') or [])
    lifecycle['holding']['hold_signal_transitions'] = list(holding_phase_observability.get('hold_signal_transitions') or [])
    lifecycle['holding']['pre_exit_context_summary'] = dict(holding_phase_observability.get('pre_exit_context_summary') or {})
    lifecycle['summary']['holding_duration'] = str(holding_phase_observability.get('hold_duration') or '')
    bundle_out['hold_duration'] = holding_phase_observability.get('hold_duration')
    bundle_out['hold_duration_sec'] = holding_phase_observability.get('hold_duration_sec')
    bundle_out['holding_phase_summary'] = holding_phase_observability.get('holding_phase_summary')
    bundle_out['hold_events_count'] = holding_phase_observability.get('hold_events_count')
    bundle_out['monitor_context_snapshots'] = list(holding_phase_observability.get('monitor_context_snapshots') or [])
    bundle_out['hold_signal_transitions'] = list(holding_phase_observability.get('hold_signal_transitions') or [])
    bundle_out['pre_exit_context_summary'] = dict(holding_phase_observability.get('pre_exit_context_summary') or {})
    bundle_out['trade_lifecycle'] = dict(lifecycle)
    story_input = facade.build_trade_story_input_from_bundle(bundle_out, trade_lifecycle=lifecycle, existing_story_input={'report_runtime_mode': 'intraday_single_trade', 'enable_separated_narrative': False, 'skip_separated_report_llm': True, 'trade_id': trade_id, 'day': day, 'run_id': run_id})
    story_input['applied_policy'] = dict(state.get('applied_policy') or {})
    story_input['commander'] = {**dict(commander), 'applied_policy': dict(state.get('applied_policy') or {})}
    story_input['reporter_policy'] = dict((state.get('applied_policy') or {}).get('reporter') or {})
    if controlled_mock_lane:
        story_input['controlled_mock_lane'] = dict(controlled_mock_lane)
    artifact_links = {'lifecycle_bundle_json': str(trade_paths['lifecycle_bundle_json']), 'entry_json': str(trade_paths['entry_json']), 'hold_json': str(trade_paths['hold_json']), 'exit_json': str(trade_paths['exit_json']), 'ai_trade_report_json': str(trade_paths['ai_trade_report_json']), 'ai_trade_report_md': str(trade_paths['ai_trade_report_md']), 'ai_trade_report_llm_response_json': str(trade_paths['ai_trade_report_llm_response_json'])}
    canonical_refs = {key: value for key, value in artifacts.items() if str(key).startswith('canonical_') and str(key).endswith('_json')}
    lifecycle_bundle = facade.build_lifecycle_bundle(day=day, trade_id=trade_id, run_id=run_id, symbol=symbol, lifecycle=lifecycle, strategist_summary=dict(strategist), scanner_summary=dict(scanner), monitor_summary=dict(monitor), commander_summary=dict(commander), story_input=dict(story_input), diagnostics={}, canonical_refs=canonical_refs, llm_refs={}, artifact_links=artifact_links)
    lifecycle_bundle.update({'artifacts': dict(artifacts), 'canonical_agent_artifacts': dict(canonical_context.get('canonical_agent_artifacts') or {}), 'evidence_provenance': dict(evidence_provenance), 'section_provenance': dict(story_input.get('section_provenance') or {}), 'same_day_reporter_linkage': dict(same_day_reporter_linkage), 'execution_details': dict(execution_details), 'entry_execution_details': dict(entry_execution_details), 'exit_execution_details': dict(exit_execution_details)})
    if controlled_mock_lane:
        lifecycle_bundle['controlled_mock_lane'] = dict(controlled_mock_lane)
    return {'trade_paths': trade_paths, 'story_input': story_input, 'lifecycle': lifecycle, 'lifecycle_bundle': lifecycle_bundle}
