"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_lifecycle_builder.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _is_placeholder_entry_reason_r4_impl(value, *, facade):
    raw = str(value or '').strip().lower()
    return raw in {'', 'no_position', 'entry reasoning was not captured.', 'entry reasoning was not captured', '진입 이유는 기록되지 않았습니다.', '-', 'n/a'}


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
    stamped = raw[:-1] + '+00:00' if raw.endswith('Z') else raw
    try:
        dt = facade.datetime.fromisoformat(stamped)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None


def _format_duration_human_r4_impl(seconds, *, facade):
    if seconds <= 0:
        return '0m'
    if seconds < 60:
        return f'{seconds}s'
    if seconds < 3600:
        return f'{seconds / 60.0:.1f}m'
    return f'{seconds / 3600.0:.1f}h'


def _trade_id_sequence_r4_impl(trade_id, *, facade):
    text = str(trade_id or '').strip()
    if not text:
        return 10 ** 9
    tail = text.rsplit('_', 1)[-1]
    try:
        return int(tail)
    except Exception:
        return 10 ** 9


def _extract_lifecycle_entry_r4_impl(payload, *, facade):
    if not isinstance(payload, dict):
        return {}
    entry = payload.get('entry') if isinstance(payload.get('entry'), dict) else {}
    if entry:
        return dict(entry)
    lifecycle = payload.get('lifecycle') if isinstance(payload.get('lifecycle'), dict) else {}
    entry = lifecycle.get('entry') if isinstance(lifecycle.get('entry'), dict) else {}
    return dict(entry)


def _extract_lifecycle_exit_r4_impl(payload, *, facade):
    if not isinstance(payload, dict):
        return {}
    exit_ctx = payload.get('exit') if isinstance(payload.get('exit'), dict) else {}
    if exit_ctx:
        return dict(exit_ctx)
    lifecycle = payload.get('lifecycle') if isinstance(payload.get('lifecycle'), dict) else {}
    exit_ctx = lifecycle.get('exit') if isinstance(lifecycle.get('exit'), dict) else {}
    return dict(exit_ctx)


def _extract_lifecycle_holding_r4_impl(payload, *, facade):
    if not isinstance(payload, dict):
        return {}
    holding = payload.get('hold') if isinstance(payload.get('hold'), dict) else {}
    if holding:
        return dict(holding)
    holding = payload.get('holding') if isinstance(payload.get('holding'), dict) else {}
    if holding:
        return dict(holding)
    lifecycle = payload.get('lifecycle') if isinstance(payload.get('lifecycle'), dict) else {}
    holding = lifecycle.get('holding') if isinstance(lifecycle.get('holding'), dict) else {}
    if holding:
        return dict(holding)
    hold = lifecycle.get('hold') if isinstance(lifecycle.get('hold'), dict) else {}
    return dict(hold)


def _snapshot_execution_debug_r4_impl(snapshot, *, facade):
    execution = snapshot.get('execution') if isinstance(snapshot.get('execution'), dict) else {}
    return {'execution_symbol': str(snapshot.get('symbol') or execution.get('symbol') or ''), 'execution_ts': str(snapshot.get('ts_start') or ''), 'execution_side': str(snapshot.get('execution_action') or execution.get('action') or '').upper(), 'execution_order_id': str(execution.get('ord_no') or snapshot.get('execution_ord_no') or execution.get('order_id') or ''), 'execution_run_id': str(snapshot.get('run_id') or ''), 'execution_filled_qty': facade.safe_int(execution.get('qty') if execution.get('qty') not in (None, '') else snapshot.get('execution_qty'), 0), 'execution_filled_price': execution.get('price') if execution.get('price') not in (None, '') else snapshot.get('execution_price')}


def _has_substantive_entry_evidence_r4_impl(entry, *, facade):
    entry_obj = entry if isinstance(entry, dict) else {}
    if not entry_obj:
        return False
    if str(entry_obj.get('run_id') or '').strip():
        return True
    if str(entry_obj.get('ts') or '').strip():
        return True
    for key in ('price', 'avg_price', 'qty'):
        value = entry_obj.get(key)
        if value not in (None, '', 0, 0.0):
            return True
    scanner_context = entry_obj.get('scanner_context') if isinstance(entry_obj.get('scanner_context'), dict) else {}
    if str(scanner_context.get('selected_symbol') or '').strip():
        return True
    if str(scanner_context.get('summary') or '').strip():
        return True
    execution_context = entry_obj.get('execution_context') if isinstance(entry_obj.get('execution_context'), dict) else {}
    execution_details = entry_obj.get('execution_details') if isinstance(entry_obj.get('execution_details'), dict) else {}
    if str(execution_context.get('order_status') or execution_details.get('order_status') or '').strip():
        return True
    if str(execution_context.get('order_id') or execution_details.get('order_id') or '').strip():
        return True
    return False


def _holding_partial_exit_total_r4_impl(holding, *, facade):
    if not isinstance(holding, dict):
        return 0
    total = 0
    for row in list(holding.get('partial_exits') or []):
        if isinstance(row, dict):
            total += max(0, facade.safe_int(row.get('qty'), 0))
    return int(total)


def _exit_closure_quantity_state_r4_impl(lifecycle, exit_ctx, *, facade):
    entry = lifecycle.get('entry') if isinstance(lifecycle.get('entry'), dict) else {}
    holding = lifecycle.get('holding') if isinstance(lifecycle.get('holding'), dict) else {}
    entry_qty = max(0, facade.safe_int(entry.get('qty'), 0))
    filled_qty_present = exit_ctx.get('filled_qty') not in (None, '')
    exit_qty = max(0, facade.safe_int(exit_ctx.get('filled_qty') if filled_qty_present else exit_ctx.get('qty'), 0))
    previous_partial_exit_qty = facade._holding_partial_exit_total(holding)
    cumulative_exit_qty = int(previous_partial_exit_qty + exit_qty)
    remaining_qty = max(0, int(entry_qty - cumulative_exit_qty)) if entry_qty > 0 else 0
    fill_truth_required = bool(exit_ctx.get('fill_truth_required'))
    fill_truth_confirmed = bool(exit_ctx.get('fill_truth_confirmed'))
    if fill_truth_required and (not fill_truth_confirmed):
        exit_qty = 0
        cumulative_exit_qty = int(previous_partial_exit_qty)
        remaining_qty = max(0, int(entry_qty - cumulative_exit_qty)) if entry_qty > 0 else 0
    return {'entry_qty': int(entry_qty), 'exit_qty': int(exit_qty), 'previous_partial_exit_qty': int(previous_partial_exit_qty), 'cumulative_exit_qty': int(cumulative_exit_qty), 'remaining_qty': int(remaining_qty), 'fill_truth_required': fill_truth_required, 'fill_truth_confirmed': fill_truth_confirmed, 'closes_position': bool((not filled_qty_present and entry_qty <= 0 or (exit_qty > 0 and cumulative_exit_qty >= entry_qty)) and (not fill_truth_required or fill_truth_confirmed))}


def _record_partial_exit_r4_impl(lifecycle, *, exit_ctx, run_id, ts, closure_state, facade):
    holding = lifecycle.get('holding') if isinstance(lifecycle.get('holding'), dict) else {}
    holding.setdefault('run_ids', [])
    holding.setdefault('holding_events', [])
    holding.setdefault('posture_history', [])
    holding.setdefault('monitor_updates', [])
    holding.setdefault('partial_exits', [])
    if run_id and run_id not in holding['run_ids']:
        holding['run_ids'].append(run_id)
    partial_exit = {'run_id': str(run_id or ''), 'ts': str(ts or ''), 'qty': int(closure_state.get('exit_qty') or 0), 'entry_qty': int(closure_state.get('entry_qty') or 0), 'cumulative_exit_qty': int(closure_state.get('cumulative_exit_qty') or 0), 'remaining_qty': int(closure_state.get('remaining_qty') or 0), 'reason_human': str(exit_ctx.get('reason_human') or ''), 'exit_context': dict(exit_ctx or {})}
    holding['partial_exits'].append(partial_exit)
    holding['holding_events'].append({'run_id': str(run_id or ''), 'ts': str(ts or ''), 'posture': 'PARTIAL_EXIT', 'monitor_reason': str(exit_ctx.get('reason_human') or ''), 'exit_reason': str(exit_ctx.get('reason_human') or ''), 'monitor_context': dict(exit_ctx.get('monitor_context') or {}), 'summary': f"Partial SELL {partial_exit['qty']} recorded; remaining qty {partial_exit['remaining_qty']} before full trade report."})
    holding['posture_history'].append({'ts': str(ts or ''), 'posture': 'PARTIAL_EXIT'})
    holding['monitor_updates'].append('partial_exit_recorded')
    lifecycle['holding'] = holding
    lifecycle['partial_exit_qty'] = int(closure_state.get('cumulative_exit_qty') or 0)
    lifecycle['remaining_qty'] = int(closure_state.get('remaining_qty') or 0)
