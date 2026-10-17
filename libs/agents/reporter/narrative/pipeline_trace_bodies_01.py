"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/agent_pipeline_trace.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _to_epoch_r4_impl(ts, *, facade):
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)
    raw = str(ts).strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except Exception:
        pass
    s = raw[:-1] + '+00:00' if raw.endswith('Z') else raw
    try:
        dt = facade.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None


def _latest_decision_trace_payload_r4_impl(rows, *, event, agent, facade):
    for row in reversed(rows):
        if str(row.get('stage') or '').strip() != 'decision_trace':
            continue
        if str(row.get('event') or '').strip() != event:
            continue
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        row_agent = str(payload.get('agent') or '').strip().lower()
        if row_agent != agent:
            continue
        agent_payload = payload.get('payload') if isinstance(payload.get('payload'), dict) else {}
        return dict(agent_payload or {})
    return {}


def _pick_run_id_r4_impl(rows, *, run_id, day, facade):
    if run_id:
        return str(run_id).strip()
    target_day = str(day or '').strip()
    for row in reversed(rows):
        rid = str(row.get('run_id') or '').strip()
        if not rid:
            continue
        if target_day and facade._utc_day(row.get('ts')) != target_day:
            continue
        if str(row.get('stage') or '') == 'commander_router' and str(row.get('event') or '') == 'route':
            return rid
    for row in reversed(rows):
        rid = str(row.get('run_id') or '').strip()
        if rid and (not target_day or facade._utc_day(row.get('ts')) == target_day):
            return rid
    return ''


def _extract_title_r4_impl(sample_row, *, facade):
    s = str(sample_row or '')
    m = facade.re.search("title='([^']+)'", s)
    if m:
        return m.group(1)
    return s[:120]


def _summarize_collected_news_r4_impl(raw_input, *, key, max_titles, facade):
    collected = raw_input.get(key) if isinstance(raw_input.get(key), dict) else {}
    by_symbol: Dict[str, Dict[str, Any]] = {}
    total_headline_count = 0
    sample_titles: List[str] = []
    for symbol, row in collected.items():
        item = row if isinstance(row, dict) else {}
        count = facade._safe_int(item.get('count'), 0)
        total_headline_count += count
        sample = item.get('sample') if isinstance(item.get('sample'), list) else []
        titles = [facade._extract_title(x) for x in sample[:max_titles]]
        by_symbol[str(symbol)] = {'count': count, 'sample_titles': titles}
        for t in titles:
            if len(sample_titles) < max_titles:
                sample_titles.append(t)
    return {'total_headline_count': int(total_headline_count), 'symbol_count': int(len(by_symbol)), 'by_symbol': by_symbol, 'sample_titles': sample_titles}


def _summarize_scanner_sources_r4_impl(candidates, *, facade):
    counts: Dict[str, int] = {}
    for row in candidates:
        srcs = row.get('sources') if isinstance(row.get('sources'), list) else []
        for src in srcs:
            key = str(src or '').strip()
            if not key:
                continue
            counts[key] = int(counts.get(key, 0) + 1)
    return counts


def _format_strategist_directives_summary_r4_impl(directives, *, facade):
    if not isinstance(directives, dict) or not directives:
        return ''
    parts: List[str] = []
    for key in ('playbook_action', 'entry_policy_action', 'monitor_focus_action', 'selected_symbol_bias_action', 'refresh_action'):
        row = directives.get(key) if isinstance(directives.get(key), dict) else {}
        action = str(row.get('action') or '').strip()
        if not action:
            continue
        target = row.get('target')
        target_fields = row.get('target_fields') if isinstance(row.get('target_fields'), list) else []
        target_axes = row.get('target_axes') if isinstance(row.get('target_axes'), list) else []
        reason = str(row.get('reason') or '').strip()
        detail = ''
        if isinstance(target, str) and target.strip():
            detail = target.strip()
        elif target_fields:
            detail = ','.join((str(x).strip() for x in target_fields if str(x).strip()))
        elif target_axes:
            detail = ','.join((str(x).strip() for x in target_axes if str(x).strip()))
        segment = f'{key}={action}'
        if detail:
            segment += f'({detail})'
        if reason:
            segment += f': {reason}'
        parts.append(segment)
    return ' | '.join(parts)


def _reporter_analysis_has_run_r4_impl(report_obj, run_id, *, facade):
    rid = str(run_id or '').strip()
    if not rid:
        return False
    trace_summary = report_obj.get('decision_trace_chain_summary')
    if isinstance(trace_summary, dict):
        chains = trace_summary.get('chains')
        if isinstance(chains, list):
            for row in chains:
                if isinstance(row, dict) and str(row.get('run_id') or '').strip() == rid:
                    return True
    decision_chains = report_obj.get('decision_chains')
    if isinstance(decision_chains, dict):
        chains = decision_chains.get('chains')
        if isinstance(chains, list):
            for row in chains:
                if isinstance(row, dict) and str(row.get('run_id') or '').strip() == rid:
                    return True
    trade_summaries = report_obj.get('trade_decision_summaries')
    if isinstance(trade_summaries, dict):
        summaries = trade_summaries.get('trade_summaries')
        if isinstance(summaries, list):
            for row in summaries:
                if not isinstance(row, dict):
                    continue
                buy_run = str(row.get('buy_run_id') or '').strip()
                sell_run = str(row.get('sell_run_id') or '').strip()
                if buy_run == rid or sell_run == rid:
                    return True
    return False


def _build_reasoning_trace_r4_impl(out, *, facade):
    commander = out.get('commander') if isinstance(out.get('commander'), dict) else {}
    strategist = out.get('strategist') if isinstance(out.get('strategist'), dict) else {}
    news_symbol_linkage = out.get('news_symbol_linkage') if isinstance(out.get('news_symbol_linkage'), dict) else {}
    scanner = out.get('scanner') if isinstance(out.get('scanner'), dict) else {}
    monitor = out.get('monitor') if isinstance(out.get('monitor'), dict) else {}
    return facade.build_reasoning_trace_from_summaries(commander_summary={'summary': str(commander.get('decision_summary') or commander.get('shadow_assessment_summary') or commander.get('path') or ''), 'command_intent': str(commander.get('command_intent') or ''), 'strategist_invocation': str(commander.get('strategist_invocation') or ''), 'llm_policy': str(commander.get('llm_policy') or ''), 'no_trade_reason_code': str(commander.get('shadow_reason_code') or commander.get('no_trade_reason_code') or ''), 'source_priority': list(commander.get('source_priority') or []), 'applied_policy': dict(commander.get('applied_policy') or {}), 'policy_source': str(commander.get('policy_source') or ''), 'policy_validation_status': str(commander.get('policy_validation_status') or ''), 'policy_fallback_used': bool(commander.get('policy_fallback_used')), 'policy_fallback_reason': str(commander.get('policy_fallback_reason') or ''), 'policy_partial_normalized': bool(commander.get('policy_partial_normalized')), 'policy_default_filled_fields': list(commander.get('policy_default_filled_fields') or []), 'policy_validation_missing_fields': list(commander.get('policy_validation_missing_fields') or []), 'policy_validation_invalid_fields': list(commander.get('policy_validation_invalid_fields') or []), 'override_reason': str(commander.get('override_reason') or ''), 'applied_policy_source_chain': list(commander.get('applied_policy_source_chain') or [])}, strategist_summary={'summary': str(strategist.get('strategy_summary') or strategist.get('news_query_reasoning') or strategist.get('playbook') or ''), 'selected_playbook': str(strategist.get('selected_playbook') or strategist.get('playbook') or ''), 'themes': list(strategist.get('themes') or []), 'monitor_guidance': str(strategist.get('monitor_guidance') or '')}, scanner_summary={'summary': str(((scanner.get('selection_basis') or {}).get('summary') if isinstance(scanner.get('selection_basis'), dict) else '') or ((scanner.get('selected_candidate') or {}).get('selection_summary') if isinstance(scanner.get('selected_candidate'), dict) else '') or scanner.get('top_stock') or ''), 'selected_symbol': str(scanner.get('top_stock') or ''), 'runner_up_symbol': str(scanner.get('runner_up_symbol') or ''), 'ranking_factors': list(scanner.get('ranking_factors') or []), 'rejected_candidates': list(scanner.get('rejected_candidates') or []), 'playbook': str(scanner.get('playbook') or ''), 'policy_source': str(scanner.get('policy_source') or ''), 'applied_policy_present': bool(scanner.get('applied_policy_present')), 'monitor_entry_policy_summary': dict(scanner.get('monitor_entry_policy_summary') or {}), 'scanner_bias_applied': bool(scanner.get('scanner_bias_applied')), 'scanner_bias_summary': dict(scanner.get('scanner_bias_summary') or {}), 'candidate_bias_adjustments': list(scanner.get('candidate_bias_adjustments') or []), 'selection_reason_with_bias': str(scanner.get('selection_reason_with_bias') or ((scanner.get('selection_basis') or {}).get('summary') if isinstance(scanner.get('selection_basis'), dict) else '') or '')}, monitor_summary={'summary': str(monitor.get('entry_check_summary') or monitor.get('monitor_reason') or monitor.get('entry_reason') or monitor.get('exit_reason') or ''), 'decision': str(monitor.get('decision') or ''), 'action': str(monitor.get('action') or ''), 'entry_blockers': list(monitor.get('entry_blockers') or []), 'timing_assessment': dict(monitor.get('timing_assessment') or {}), 'exit_trigger_basis': dict(monitor.get('exit_trigger_basis') or {}), 'received_policy': dict(monitor.get('received_policy') or {}), 'received_policy_source': str(monitor.get('received_policy_source') or ''), 'effective_policy': dict(monitor.get('effective_policy') or monitor.get('applied_policy') or {}), 'effective_policy_source': str(monitor.get('effective_policy_source') or ''), 'effective_policy_source_chain': list(monitor.get('effective_policy_source_chain') or []), 'policy_adjustments': dict(monitor.get('policy_adjustments') or {}), 'policy_adjustment_summary': str(monitor.get('policy_adjustment_summary') or ''), 'policy_adjustment_reasoning': str(monitor.get('policy_adjustment_reasoning') or ''), 'effective_policy_deltas': list(monitor.get('effective_policy_deltas') or []), 'policy_source': str(monitor.get('policy_source') or ''), 'policy_validation_status': str(monitor.get('policy_validation_status') or ''), 'policy_fallback_used': bool(monitor.get('policy_fallback_used')), 'policy_partial_normalized': bool(monitor.get('policy_partial_normalized')), 'policy_default_filled_fields': list(monitor.get('policy_default_filled_fields') or []), 'policy_validation_missing_fields': list(monitor.get('policy_validation_missing_fields') or []), 'policy_validation_invalid_fields': list(monitor.get('policy_validation_invalid_fields') or []), 'override_reason': str(monitor.get('override_reason') or ''), 'applied_policy': dict(monitor.get('applied_policy') or {})})


def _build_reasoning_provenance_r4_impl(out, *, facade):
    commander = out.get('commander') if isinstance(out.get('commander'), dict) else {}
    strategist = out.get('strategist') if isinstance(out.get('strategist'), dict) else {}
    news_symbol_linkage = out.get('news_symbol_linkage') if isinstance(out.get('news_symbol_linkage'), dict) else {}
    scanner = out.get('scanner') if isinstance(out.get('scanner'), dict) else {}
    monitor = out.get('monitor') if isinstance(out.get('monitor'), dict) else {}
    return facade.build_reasoning_provenance(commander_context_source='event_payload' if commander else 'missing', strategist_plan_source='event_payload' if strategist else 'missing', scanner_reason_source='event_payload' if scanner else 'missing', monitor_reason_source='event_payload' if monitor else 'missing', commander_source_ref='commander_router.route/end', strategist_source_ref='strategist.summary', scanner_source_ref='scanner.summary/decision_trace.candidate_selection', monitor_source_ref='monitor.summary/decision_trace.entry_exit_decision', shadow_used=bool(commander.get('shadow_used') or strategist.get('shadow_used')), strategist_fallback_used=bool(commander.get('strategist_fallback_used') or strategist.get('strategist_fallback_used')), source_priority=list(commander.get('source_priority') or []))
