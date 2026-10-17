"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/intraday_trade_reports.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _trade_day_from_trade_id_r4_impl(trade_id, *, facade):
    value = str(trade_id or '').strip()
    match = facade.re.match('^TRD_(\\d{4})(\\d{2})(\\d{2})_', value)
    if not match:
        return ''
    return f'{match.group(1)}-{match.group(2)}-{match.group(3)}'


def _runtime_trade_day_r4_impl(state, *, facade):
    execution = state.get('execution') if isinstance(state.get('execution'), dict) else {}
    payload = execution.get('payload') if isinstance(execution.get('payload'), dict) else {}
    market_status = state.get('kiwoom_market_status') if isinstance(state.get('kiwoom_market_status'), dict) else {}
    parsed_values: List[facade.datetime] = []
    for value in (state.get('ts'), state.get('timestamp'), execution.get('ts'), execution.get('timestamp'), payload.get('ts'), payload.get('timestamp'), market_status.get('received_at')):
        text = str(value or '').strip()
        if not text:
            continue
        normalized = text[:-1] + '+00:00' if text.endswith('Z') else text
        try:
            parsed = facade.datetime.fromisoformat(normalized)
        except Exception:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=facade.timezone.utc)
        parsed_values.append(parsed.astimezone(facade.timezone.utc))
    if not parsed_values:
        return ''
    return max(parsed_values).strftime('%Y-%m-%d')


def _safe_float_r4_impl(value, default, *, facade):
    if value in (None, ''):
        return default
    try:
        return float(value)
    except Exception:
        return default


def _to_epoch_r4_impl(ts, *, facade):
    text = str(ts or '').strip()
    if not text:
        return None
    normalized = text.replace('Z', '+00:00')
    try:
        return int(facade.datetime.fromisoformat(normalized).timestamp())
    except Exception:
        return None


def _null_if_empty_r4_impl(value, *, facade):
    if value in (None, ''):
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return value


def normalize_trade_id_filters_r4_impl(values, *, facade):
    raw_values: List[str] = []
    if isinstance(values, list):
        raw_values = [str(value or '') for value in values]
    elif values not in (None, ''):
        raw_values = [str(values or '')]
    out: List[str] = []
    seen: set[str] = set()
    for raw in raw_values:
        for part in str(raw or '').split(','):
            trade_id = str(part or '').strip()
            if not trade_id or trade_id in seen:
                continue
            out.append(trade_id)
            seen.add(trade_id)
    return out


def build_hold_signal_transitions_r4_impl(monitor_context_snapshots, *, facade):
    out: List[Dict[str, Any]] = []
    previous: Dict[str, Any] | None = None
    keys = ('posture', 'monitor_reason', 'exit_reason', 'active_exit_axis', 'exit_triggered')
    for current in list(monitor_context_snapshots or []):
        if not isinstance(current, dict):
            continue
        if previous is None:
            previous = current
            continue
        changes: Dict[str, Dict[str, Any]] = {}
        for key in keys:
            before = previous.get(key)
            after = current.get(key)
            if before != after:
                changes[str(key)] = {'from': before, 'to': after}
        if changes:
            change_labels = ', '.join(sorted(changes.keys()))
            out.append({'from_run_id': str(previous.get('run_id') or ''), 'to_run_id': str(current.get('run_id') or ''), 'ts': str(current.get('ts') or ''), 'changes': changes, 'summary': f'Hold context changed in {change_labels}.'})
        previous = current
    return out


def build_holding_phase_observability_r4_impl(lifecycle, *, monitor_timeline, facade):
    lifecycle = lifecycle if isinstance(lifecycle, dict) else {}
    summary_obj = lifecycle.get('summary') if isinstance(lifecycle.get('summary'), dict) else {}
    holding = lifecycle.get('holding') if isinstance(lifecycle.get('holding'), dict) else {}
    exit_ctx = lifecycle.get('exit') if isinstance(lifecycle.get('exit'), dict) else {}
    hold_events = [dict(row) for row in list(holding.get('holding_events') or []) if isinstance(row, dict)]
    monitor_context_snapshots: List[Dict[str, Any]] = []
    for row in hold_events:
        monitor_context = row.get('monitor_context') if isinstance(row.get('monitor_context'), dict) else {}
        monitor_context_snapshots.append({'run_id': str(row.get('run_id') or ''), 'ts': str(row.get('ts') or ''), 'posture': str(row.get('posture') or ''), 'monitor_reason': facade._null_if_empty(row.get('monitor_reason') or monitor_context.get('monitor_reason')), 'exit_reason': facade._null_if_empty(row.get('exit_reason') or monitor_context.get('exit_reason')), 'active_exit_axis': facade._null_if_empty(monitor_context.get('active_exit_axis') or monitor_context.get('trigger_type')), 'exit_triggered': monitor_context.get('exit_triggered') if 'exit_triggered' in monitor_context else None, 'current_drawdown': facade._null_if_empty(monitor_context.get('current_drawdown')), 'peak_drawdown': facade._null_if_empty(monitor_context.get('peak_drawdown')), 'price_source': facade._null_if_empty(monitor_context.get('price_source')), 'summary': str(row.get('summary') or '')})
    hold_signal_transitions = facade.build_hold_signal_transitions(monitor_context_snapshots)
    hold_events_count = int(len(hold_events))
    hold_duration = str(summary_obj.get('holding_duration') or '')
    entry = lifecycle.get('entry') if isinstance(lifecycle.get('entry'), dict) else {}
    entry_ts = facade._to_epoch(entry.get('ts'))
    exit_ts = facade._to_epoch(exit_ctx.get('ts'))
    hold_duration_sec = None
    if entry_ts is not None:
        if exit_ts is not None:
            hold_duration_sec = max(0, int(exit_ts - entry_ts))
        elif monitor_context_snapshots:
            latest_hold_ts = facade._to_epoch(monitor_context_snapshots[-1].get('ts'))
            if latest_hold_ts is not None:
                hold_duration_sec = max(0, int(latest_hold_ts - entry_ts))
    last_hold_snapshot = monitor_context_snapshots[-1] if monitor_context_snapshots else {}
    exit_monitor_context = exit_ctx.get('monitor_context') if isinstance(exit_ctx.get('monitor_context'), dict) else {}
    deterioration_signals: List[str] = []
    if bool(exit_monitor_context.get('exit_triggered')):
        deterioration_signals.append('exit_triggered')
    active_axis = str(exit_monitor_context.get('active_exit_axis') or exit_monitor_context.get('trigger_type') or '').strip()
    if active_axis:
        deterioration_signals.append(f'active_exit_axis:{active_axis}')
    current_drawdown = facade._safe_float(exit_monitor_context.get('current_drawdown'), None)
    if current_drawdown is not None and current_drawdown < 0:
        deterioration_signals.append('current_drawdown_negative')
    peak_drawdown = facade._safe_float(exit_monitor_context.get('peak_drawdown'), None)
    if peak_drawdown is not None and peak_drawdown < 0:
        deterioration_signals.append('peak_drawdown_negative')
    pre_exit_context_summary = {'available': bool(exit_ctx), 'last_hold_run_id': str(last_hold_snapshot.get('run_id') or ''), 'last_hold_ts': str(last_hold_snapshot.get('ts') or ''), 'last_hold_posture': facade._null_if_empty(last_hold_snapshot.get('posture')), 'last_hold_monitor_reason': facade._null_if_empty(last_hold_snapshot.get('monitor_reason')), 'last_hold_exit_reason': facade._null_if_empty(last_hold_snapshot.get('exit_reason')), 'deterioration_signals': deterioration_signals, 'summary': f"Pre-exit context captured {hold_events_count} holding updates; last hold posture was {str(last_hold_snapshot.get('posture') or 'not_captured')} before exit." if exit_ctx else 'No exit context yet; pre-exit monitor summary is not available.'}
    timeline_summary = monitor_timeline if isinstance(monitor_timeline, dict) else {}
    threshold_snapshot_count = len(list(timeline_summary.get('threshold_snapshots') or []))
    state_transition_count = len(list(timeline_summary.get('state_transitions') or []))
    hold_evidence_thin = hold_events_count <= 0 or not monitor_context_snapshots
    if hold_evidence_thin:
        recovered_snapshot = {}
        if exit_monitor_context:
            recovered_snapshot = dict(exit_monitor_context)
            recovered_snapshot['_recovery_source'] = 'exit_monitor_context'
            recovered_snapshot['ts'] = str(exit_ctx.get('ts') or '')
            recovered_snapshot['run_id'] = str(exit_ctx.get('run_id') or '')
        elif entry.get('monitor_context'):
            recovered_snapshot = dict(entry.get('monitor_context') or {})
            recovered_snapshot['_recovery_source'] = 'entry_monitor_context'
            recovered_snapshot['ts'] = str(entry.get('ts') or '')
            recovered_snapshot['run_id'] = str(entry.get('run_id') or '')
        if recovered_snapshot:
            monitor_context_snapshots.append({'run_id': recovered_snapshot.get('run_id', ''), 'ts': recovered_snapshot.get('ts', ''), 'posture': recovered_snapshot.get('posture', 'HOLD'), 'monitor_reason': facade._null_if_empty(recovered_snapshot.get('monitor_reason')), 'exit_reason': facade._null_if_empty(recovered_snapshot.get('exit_reason')), 'active_exit_axis': facade._null_if_empty(recovered_snapshot.get('active_exit_axis') or recovered_snapshot.get('trigger_type')), 'exit_triggered': recovered_snapshot.get('exit_triggered'), 'current_drawdown': facade._null_if_empty(recovered_snapshot.get('current_drawdown')), 'peak_drawdown': facade._null_if_empty(recovered_snapshot.get('peak_drawdown')), 'price_source': facade._null_if_empty(recovered_snapshot.get('price_source')), 'summary': 'Recovered from nearby execution context', '_recovery_source': recovered_snapshot.get('_recovery_source')})
            hold_evidence_thin = False
            holding_phase_summary = 'Hold evidence recovered from execution context due to short hold duration.'
            hold_events_count = max(1, hold_events_count)
        else:
            holding_phase_summary = 'No explicit holding monitor updates were captured, and no nearby context was available for recovery.'
    else:
        holding_phase_summary = f"Held across {hold_events_count} monitor updates over {hold_duration or 'uncaptured duration'}. Signal transitions observed: {len(hold_signal_transitions)}. Timeline snapshots: thresholds={threshold_snapshot_count}, state_transitions={state_transition_count}."
    return {'hold_duration': hold_duration, 'hold_duration_sec': hold_duration_sec, 'holding_phase_summary': holding_phase_summary, 'hold_events_count': hold_events_count, 'monitor_context_snapshots': monitor_context_snapshots[:20], 'hold_signal_transitions': hold_signal_transitions[:20], 'pre_exit_context_summary': pre_exit_context_summary, 'deterioration_signals': deterioration_signals, 'hold_evidence_thin': hold_evidence_thin}


def _execution_truth_surface_r4_impl(details, *, facade):
    details_obj = details if isinstance(details, dict) else {}
    out: Dict[str, Any] = {}
    for key in ('order_id', 'filled_qty', 'filled_price', 'broker_truth_source', 'broker_day_truth_source', 'broker_day_match_mode', 'broker_day_authoritative', 'broker_buy_price', 'broker_realized_pnl', 'broker_fee', 'broker_tax'):
        value = details_obj.get(key)
        if value not in (None, '', [], {}):
            out[key] = value
    return out


def _apply_ai_report_diagnostics_summary_r4_impl(payload, diagnostics, *, facade):
    out = dict(payload or {})
    diagnostics_obj = dict(diagnostics or {})
    ai_status = str(diagnostics_obj.get('ai_trade_report_status') or '').strip()
    report_status = str(diagnostics_obj.get('report_status') or '').strip()
    if ai_status:
        out['ai_trade_report_status'] = ai_status
        out['llm_trade_report_status'] = ai_status
    if report_status:
        out['report_generation_status'] = report_status
    for key in ('deterministic_report_status', 'llm_brief_status', 'llm_response_status', 'llm_parse_mode', 'llm_completeness_score', 'llm_required_keys_missing'):
        if key in diagnostics_obj:
            out[key] = diagnostics_obj.get(key)
    if diagnostics_obj.get('report_generation_reason') or diagnostics_obj.get('report_reason_human'):
        out['report_generation_reason'] = str(diagnostics_obj.get('report_generation_reason') or diagnostics_obj.get('report_reason_human') or '')
    return out


def _creation_epoch_from_wmi_r4_impl(value, *, facade):
    raw = str(value or '').strip()
    if not raw:
        return 0.0
    match = facade.re.search('/Date\\((\\d+)', raw)
    if match:
        try:
            return float(match.group(1)) / 1000.0
        except Exception:
            return 0.0
    return 0.0


def _cache_run_ids_r4_impl(summary, current_run_id, *, facade):
    run_bundles = summary.get('run_bundles') if isinstance(summary.get('run_bundles'), list) else []
    matched_trade_ids = {str(row.get('trade_id') or '').strip() for row in run_bundles if str(row.get('run_id') or '').strip() == current_run_id and str(row.get('trade_id') or '').strip()}
    run_ids = {current_run_id}
    for row in run_bundles:
        if not isinstance(row, dict):
            continue
        trade_id = str(row.get('trade_id') or '').strip()
        run_id = str(row.get('run_id') or '').strip()
        if trade_id and trade_id in matched_trade_ids and run_id:
            run_ids.add(run_id)
    return sorted((x for x in run_ids if x))
