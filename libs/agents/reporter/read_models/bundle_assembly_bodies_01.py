"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_bundle_assembly.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _latest_exit_monitor_context_from_timeline_r4_impl(monitor_timeline, *, exit_run_id, symbol, facade):
    if not exit_run_id:
        return {}
    timeline = dict(monitor_timeline or {})
    rows_by_ts: Dict[str, List[tuple[str, Dict[str, Any]]]] = {}
    collection_order = ('threshold_snapshots', 'exit_decision_details', 'cycle_summaries', 'state_transitions')
    for collection_name in collection_order:
        for row in list(timeline.get(collection_name) or []):
            if not isinstance(row, dict):
                continue
            if str(row.get('run_id') or '').strip() != exit_run_id:
                continue
            payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
            if not payload:
                continue
            ts = str(row.get('ts') or '').strip()
            if not ts:
                continue
            rows_by_ts.setdefault(ts, []).append((collection_name, dict(payload)))
    if not rows_by_ts:
        return {}
    latest_ts = sorted(rows_by_ts.keys())[-1]
    merged: Dict[str, Any] = {}
    for collection_name in collection_order:
        for row_collection, payload in rows_by_ts.get(latest_ts, []):
            if row_collection == collection_name:
                merged.update(payload)
    final_thresholds = merged.get('final_exit_thresholds')
    if isinstance(final_thresholds, dict) and (not isinstance(merged.get('thresholds'), dict)):
        merged['thresholds'] = dict(final_thresholds)
    triggered_rule = str(merged.get('triggered_rule') or '').strip()
    if triggered_rule:
        merged.setdefault('exit_reason', triggered_rule)
        merged.setdefault('trigger_type', triggered_rule)
        merged.setdefault('reason', triggered_rule)
    if bool(merged.get('exit_triggered')) and (not str(merged.get('monitor_reason') or '').strip()):
        merged['monitor_reason'] = 'confirmed_exit_signal'
    if str(merged.get('intent_side') or '').strip().upper() == 'SELL':
        merged.setdefault('posture', 'SELL')
    if str(merged.get('current_posture') or '').strip().upper() == 'SELL':
        merged.setdefault('posture', 'SELL')
    merged.setdefault('run_id', exit_run_id)
    merged.setdefault('ts', latest_ts)
    if symbol:
        merged.setdefault('symbol', symbol)
        merged.setdefault('selected_symbol', symbol)
        merged.setdefault('monitor_symbol', symbol)
    merged['source'] = 'monitor_timeline.latest_exit_run'
    return merged


def apply_latest_exit_monitor_context_from_timeline_r4_impl(lifecycle_bundle, monitor_timeline, *, facade):
    out = dict(lifecycle_bundle or {})
    exit_obj = out.get('exit') if isinstance(out.get('exit'), dict) else {}
    if not exit_obj:
        return out
    exit_run_id = str(exit_obj.get('run_id') or '').strip()
    symbol = facade.normalize_symbol(out.get('symbol') or exit_obj.get('symbol') or '', allow_test_symbols=True)
    latest_exit_monitor_context = facade._latest_exit_monitor_context_from_timeline(monitor_timeline, exit_run_id=exit_run_id, symbol=symbol)
    if not latest_exit_monitor_context:
        return out
    exit_obj = dict(exit_obj)
    monitor_context = dict(exit_obj.get('monitor_context') or {}) if isinstance(exit_obj.get('monitor_context'), dict) else {}
    monitor_context = {**monitor_context, **latest_exit_monitor_context}
    exit_obj['monitor_context'] = monitor_context
    out['monitor'] = {**(out.get('monitor') if isinstance(out.get('monitor'), dict) else {}), **latest_exit_monitor_context}
    monitor_reason_human = facade.build_monitor_reason_human(monitor_context, {'action': str(exit_obj.get('action') or 'SELL').strip().upper() or 'SELL'})
    out['monitor_reason_human'] = monitor_reason_human
    summary = str(monitor_reason_human.get('summary') or '').strip()
    if summary:
        exit_obj['reason_human'] = summary
        exit_obj['summary'] = summary
        trade_outcome = out.get('trade_outcome') if isinstance(out.get('trade_outcome'), dict) else {}
        if trade_outcome:
            trade_outcome = dict(trade_outcome)
            trade_outcome['exit_reason'] = summary
            out['trade_outcome'] = trade_outcome
    out['exit'] = exit_obj
    lifecycle_obj = out.get('lifecycle') if isinstance(out.get('lifecycle'), dict) else {}
    if lifecycle_obj:
        lifecycle_obj = dict(lifecycle_obj)
        lifecycle_obj['exit'] = exit_obj
        out['lifecycle'] = lifecycle_obj
    return out


def _resolve_trade_day_hint_r4_impl(*values, facade):
    for value in values:
        raw = str(value or '').strip()
        if not raw:
            continue
        if len(raw) >= 10 and raw[4] == '-' and (raw[7] == '-'):
            return raw[:10].replace('-', '')
        digits = ''.join((ch for ch in raw if ch.isdigit()))
        if len(digits) >= 8:
            return digits[:8]
    return ''


def _normalize_broker_lookup_side_r4_impl(value, *, facade):
    text = str(value or '').strip().lower()
    if not text:
        return 'all'
    compact = text.replace('_', '').replace('-', '').replace(' ', '')
    if compact in {'sell', 's', '1'} or '매도' in text:
        return 'sell'
    if compact in {'buy', 'b', '2'} or '매수' in text:
        return 'buy'
    return 'all'


def _attach_broker_order_status_r4_impl(bundle, *, context, facade):
    bundle_obj = dict(bundle or {})
    context_obj = dict(context or {})
    execution_context = dict(context_obj.get('execution_context') or {}) if isinstance(context_obj.get('execution_context'), dict) else {}
    execution_details = dict(context_obj.get('execution_details') or {}) if isinstance(context_obj.get('execution_details'), dict) else {}
    bundle_execution_details = dict(bundle_obj.get('execution_details') or {}) if isinstance(bundle_obj.get('execution_details'), dict) else {}
    if isinstance(execution_context.get('broker_order_status'), dict) and execution_context.get('broker_order_status'):
        context_obj['execution_context'] = execution_context
        return context_obj
    execution = bundle_obj.get('execution') if isinstance(bundle_obj.get('execution'), dict) else {}
    executor = bundle_obj.get('executor') if isinstance(bundle_obj.get('executor'), dict) else {}
    broker_result = executor.get('broker_result') if isinstance(executor.get('broker_result'), dict) else {}
    order_request = executor.get('order_request_summary') if isinstance(executor.get('order_request_summary'), dict) else {}
    order_id = str(facade._coalesce_non_empty(execution_details.get('order_id'), execution_details.get('ord_no'), bundle_execution_details.get('order_id'), bundle_execution_details.get('ord_no'), execution.get('ord_no'), execution.get('order_id'), broker_result.get('ord_no'), broker_result.get('order_id'), executor.get('ord_no'), executor.get('order_id'), order_request.get('ord_no'), order_request.get('order_id'), execution_context.get('order_id'), execution_context.get('ord_no')) or '').strip()
    symbol = facade.normalize_symbol(facade._coalesce_non_empty(context_obj.get('symbol'), execution_details.get('symbol'), bundle_execution_details.get('symbol'), execution.get('symbol'), broker_result.get('symbol'), executor.get('symbol'), order_request.get('symbol'), execution_context.get('symbol')) or '', allow_test_symbols=True)
    side = facade._normalize_broker_lookup_side(facade._coalesce_non_empty(context_obj.get('action'), context_obj.get('side'), execution_details.get('action'), execution_details.get('side'), bundle_execution_details.get('action'), bundle_execution_details.get('side'), execution.get('action'), broker_result.get('action'), executor.get('action'), order_request.get('action'), execution_context.get('action')) or '')
    ord_dt = facade._resolve_trade_day_hint(context_obj.get('trade_day'), context_obj.get('ts'), execution_details.get('ts'), bundle_execution_details.get('ts'), execution_context.get('ts'), execution.get('ts'), broker_result.get('ts'), executor.get('ts'), bundle_obj.get('ts'))
    if not (order_id and symbol and ord_dt):
        context_obj['execution_context'] = execution_context
        return context_obj
    reader = context_obj.get('broker_fill_reader')
    if reader is None:
        if not facade._broker_fill_lookup_enabled(context_obj):
            context_obj['execution_context'] = execution_context
            return context_obj
        try:
            from libs.read.kiwoom_order_fill_reader import KiwoomOrderFillReader
            reader = KiwoomOrderFillReader.from_env()
        except Exception as exc:
            execution_context['broker_order_status_error'] = str(exc)
            context_obj['execution_context'] = execution_context
            return context_obj
    try:
        dto = reader.get_order_status(ord_no=order_id, symbol=symbol, ord_dt=ord_dt, side=side or 'all')
    except Exception as exc:
        execution_context['broker_order_status_error'] = str(exc)
        context_obj['execution_context'] = execution_context
        return context_obj
    payload = facade._broker_order_status_payload(dto)
    if payload.get('order_id') in (None, ''):
        payload['order_id'] = order_id
        payload['ord_no'] = order_id
    if payload.get('order_id') not in (None, '') and any((payload.get(key) not in (None, '', 0) for key in ('filled_qty', 'filled_price', 'status'))):
        execution_context['broker_order_status'] = payload
    context_obj['execution_context'] = execution_context
    return context_obj


def build_execution_details_from_bundle_r4_impl(bundle, *, context, facade):
    bundle_obj = dict(bundle or {})
    context_obj = dict(context or {})
    if not isinstance(context_obj.get('monitor_context'), dict):
        monitor_payload = bundle_obj.get('monitor') if isinstance(bundle_obj.get('monitor'), dict) else {}
        if monitor_payload:
            context_obj['monitor_context'] = dict(monitor_payload)
    context_obj = facade._attach_broker_order_status(bundle_obj, context=context_obj)
    context_obj = facade.attach_broker_day_pnl(bundle_obj, context=context_obj)
    return facade.build_execution_details(bundle_obj, context=context_obj)


def _has_meaningful_payload_r4_impl(payload, *, facade):
    if not isinstance(payload, dict) or not payload:
        return False
    for value in payload.values():
        if isinstance(value, dict) and facade._has_meaningful_payload(value):
            return True
        if isinstance(value, list) and any((item not in ({}, [], None, '') for item in value)):
            return True
        if value not in ({}, [], None, ''):
            return True
    return False


def _prefer_canonical_payload_r4_impl(canonical_sources, agent, fallback, *, fallback_source, normalized_payload, normalized_path, facade):
    canonical_sources = dict(canonical_sources or {})
    canonical_payload = (canonical_sources.get('artifacts') or {}).get(agent) if isinstance(canonical_sources.get('artifacts'), dict) else {}
    canonical_path = str((canonical_sources.get('paths') or {}).get(agent) or '').strip() if isinstance(canonical_sources.get('paths'), dict) else ''
    merged = dict(fallback or {})
    if facade._has_meaningful_payload(normalized_payload):
        merged.update(dict(normalized_payload or {}))
        return {'payload': merged, 'source': 'normalized_trade_artifact', 'path': str(normalized_path or '')}
    if facade._has_meaningful_payload(canonical_payload):
        merged.update(dict(canonical_payload or {}))
        return {'payload': merged, 'source': 'canonical', 'path': canonical_path}
    return {'payload': dict(fallback or {}), 'source': str(fallback_source or 'fallback'), 'path': canonical_path}


def preferred_run_ids_for_agent_r4_impl(agent, *, anchor_run_id, entry_run_id, exit_run_id, facade):
    if agent in {'strategist', 'scanner'}:
        ordered = [entry_run_id, anchor_run_id, exit_run_id]
    elif agent in {'monitor', 'supervisor', 'executor'}:
        ordered = [exit_run_id, anchor_run_id, entry_run_id]
    else:
        ordered = [anchor_run_id, entry_run_id, exit_run_id]
    out: List[str] = []
    for item in ordered:
        rid = str(item or '').strip()
        if rid and rid not in out:
            out.append(rid)
    return out


def _is_placeholder_entry_reason_r4_impl(value, *, facade):
    raw = str(value or '').strip().lower()
    return raw in {'', 'no_position', 'entry reasoning was not captured.', 'entry reasoning was not captured', '-', 'n/a'}


def build_strategist_trace_summary_mirror_r4_impl(strategist_summary, market_context_human, *, facade):
    strategist = dict(strategist_summary or {})
    trace = strategist.get('trace_summary') if isinstance(strategist.get('trace_summary'), dict) else {}
    market_context = dict(market_context_human or {})
    strategy_frame = strategist.get('strategy_frame') if isinstance(strategist.get('strategy_frame'), dict) else {}
    policy_selected = strategist.get('policy_selected') if isinstance(strategist.get('policy_selected'), dict) else {}
    if trace:
        out = dict(trace)
        if not out.get('risk_tone'):
            out['risk_tone'] = str(strategist.get('risk_tone') or strategy_frame.get('risk_tone') or policy_selected.get('risk_tone') or market_context.get('risk_tone') or '')
        if not out.get('trade_aggressiveness'):
            out['trade_aggressiveness'] = str(strategist.get('trade_aggressiveness') or strategy_frame.get('trade_aggressiveness') or policy_selected.get('trade_aggressiveness') or market_context.get('trade_aggressiveness') or '')
        if not out.get('monitor_guidance'):
            out['monitor_guidance'] = str(strategist.get('monitor_guidance') or strategy_frame.get('monitor_guidance') or policy_selected.get('monitor_guidance') or market_context.get('monitor_guidance') or '')
        return out
    highlights = [str(x or '') for x in list(market_context.get('bullets') or []) if str(x or '').strip()][:4]
    return {'summary': str(market_context.get('summary') or strategist.get('market_context_summary') or ''), 'highlights': highlights, 'market_regime': str(strategist.get('market_regime') or market_context.get('regime') or ''), 'market_sentiment': str(strategist.get('market_sentiment') or market_context.get('market_sentiment') or ''), 'playbook': str(strategist.get('playbook') or market_context.get('playbook') or ''), 'risk_tone': str(strategist.get('risk_tone') or strategy_frame.get('risk_tone') or policy_selected.get('risk_tone') or market_context.get('risk_tone') or ''), 'trade_aggressiveness': str(strategist.get('trade_aggressiveness') or strategy_frame.get('trade_aggressiveness') or policy_selected.get('trade_aggressiveness') or market_context.get('trade_aggressiveness') or ''), 'monitor_guidance': str(strategist.get('monitor_guidance') or strategy_frame.get('monitor_guidance') or policy_selected.get('monitor_guidance') or market_context.get('monitor_guidance') or ''), 'themes': list(strategist.get('themes') or market_context.get('themes') or []), 'global_sentiment_score': strategist.get('global_sentiment_score', market_context.get('global_sentiment_score')), 'vix_level': (strategist.get('fear_index') or {}).get('level') if isinstance(strategist.get('fear_index'), dict) else market_context.get('vix_level'), 'headline_count': market_context.get('headline_count'), 'news_query_count': market_context.get('news_query_count'), 'reason_chain': list((strategist.get('strategy_frame') or {}).get('reason_chain') or []), 'missing_flags': ['trace_summary_missing']}


def build_scanner_trace_summary_mirror_r4_impl(scanner_summary, scanner_reason_human, *, facade):
    scanner = dict(scanner_summary or {})
    trace = scanner.get('trace_summary') if isinstance(scanner.get('trace_summary'), dict) else {}
    if trace:
        return dict(trace)
    reason = dict(scanner_reason_human or {})
    highlights = [str(x or '') for x in list(reason.get('bullets') or []) if str(x or '').strip()][:4]
    selected_symbol = str(scanner.get('selected_symbol') or reason.get('selected_symbol') or '')
    selected_rank = facade.safe_int(scanner.get('selected_rank'), facade.safe_int(reason.get('selected_rank'), 0))
    universe_size = facade.safe_int(scanner.get('universe_size'), facade.safe_int(reason.get('universe_size'), 0))
    detail = scanner.get('selection_reason_detail') if isinstance(scanner.get('selection_reason_detail'), dict) else {}
    runner_up_symbol = ''
    ranked_rows: List[Dict[str, Any]] = []
    for candidate_key in ('candidate_ranking_table', 'ranking_table', 'ranked_candidates'):
        candidate_value = scanner.get(candidate_key)
        if isinstance(candidate_value, dict):
            ranked_rows = [row for row in list(candidate_value.get('rows') or []) if isinstance(row, dict)]
        elif isinstance(candidate_value, list):
            ranked_rows = [row for row in list(candidate_value or []) if isinstance(row, dict)]
        if ranked_rows:
            break
    if len(ranked_rows) > 1:
        runner_up_symbol = str(ranked_rows[1].get('symbol') or '')
    if not runner_up_symbol:
        runner_up_symbol = str((list(reason.get('runner_ups') or [{}])[:1][0] or {}).get('symbol') or '')
    return {'summary': str(reason.get('summary') or scanner.get('selection_reason') or ''), 'highlights': highlights, 'selected_symbol': selected_symbol, 'runner_up_symbol': runner_up_symbol, 'selected_rank': selected_rank, 'universe_size': universe_size, 'candidate_count': universe_size, 'selected_score_total': detail.get('selected_score_total', reason.get('selected_score')), 'margin_vs_second': detail.get('margin_vs_second'), 'selection_basis': list(reason.get('ranking_basis') or []), 'critical_positive_factors': list(detail.get('critical_positive_factors') or []), 'critical_negative_factors': list(detail.get('critical_negative_factors') or []), 'top_candidates': list(reason.get('top_candidates') or []), 'runner_ups': list(reason.get('runner_ups') or []), 'missing_flags': ['trace_summary_missing']}


def apply_trace_summary_context_r4_impl(*, trade_story_input, lifecycle_bundle, scanner_evidence, facade):
    strategist_trace_summary = facade.build_strategist_trace_summary_mirror(lifecycle_bundle.get('strategist') if isinstance(lifecycle_bundle.get('strategist'), dict) else {}, trade_story_input.get('market_context_human') if isinstance(trade_story_input.get('market_context_human'), dict) else {})
    scanner_trace_summary = facade.build_scanner_trace_summary_mirror(lifecycle_bundle.get('scanner') if isinstance(lifecycle_bundle.get('scanner'), dict) else {}, trade_story_input.get('scanner_reason_human') if isinstance(trade_story_input.get('scanner_reason_human'), dict) else {})
    if not str(scanner_trace_summary.get('runner_up_symbol') or '').strip():
        ranking_tables = list(scanner_evidence.get('candidate_ranking_tables') or []) if isinstance(scanner_evidence, dict) else []
        if ranking_tables:
            payload = ranking_tables[0].get('payload') if isinstance(ranking_tables[0], dict) else {}
            rows = list(payload.get('rows') or []) if isinstance(payload, dict) else []
            if len(rows) > 1 and isinstance(rows[1], dict):
                scanner_trace_summary['runner_up_symbol'] = str(rows[1].get('symbol') or '')
    selected_symbol = str(scanner_trace_summary.get('selected_symbol') or lifecycle_bundle.get('symbol') or '')
    runner_up_symbol = str(scanner_trace_summary.get('runner_up_symbol') or '')
    candidate_count = facade.safe_int(scanner_trace_summary.get('candidate_count'), facade.safe_int(scanner_trace_summary.get('universe_size'), 0))
    trade_story_input['strategist_trace_summary'] = dict(strategist_trace_summary)
    trade_story_input['scanner_trace_summary'] = dict(scanner_trace_summary)
    trade_story_input['selected_symbol'] = selected_symbol
    trade_story_input['runner_up_symbol'] = runner_up_symbol
    trade_story_input['candidate_count'] = candidate_count
    lifecycle_bundle['strategist_trace_summary'] = dict(strategist_trace_summary)
    lifecycle_bundle['scanner_trace_summary'] = dict(scanner_trace_summary)
    lifecycle_bundle['selected_symbol'] = selected_symbol
    lifecycle_bundle['runner_up_symbol'] = runner_up_symbol
    lifecycle_bundle['candidate_count'] = candidate_count
    return {'strategist_trace_summary': strategist_trace_summary, 'scanner_trace_summary': scanner_trace_summary, 'trade_story_input': trade_story_input, 'lifecycle_bundle': lifecycle_bundle}
