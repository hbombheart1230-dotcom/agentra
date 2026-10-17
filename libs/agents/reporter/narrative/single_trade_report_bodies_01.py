"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/single_trade_report.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _safe_float_r4_impl(value, *, facade):
    try:
        if value in (None, '', []):
            return None
        return float(value)
    except Exception:
        return None


def _safe_int_r4_impl(value, *, facade):
    try:
        if value in (None, '', []):
            return None
        return int(float(value))
    except Exception:
        return None


def _trade_report_policy_r4_impl(state, *, facade):
    applied_policy = state.get('applied_policy') if isinstance(state.get('applied_policy'), dict) else {}
    reporter = applied_policy.get('reporter') if isinstance(applied_policy.get('reporter'), dict) else {}
    trade_report = reporter.get('trade_report') if isinstance(reporter.get('trade_report'), dict) else {}
    if trade_report:
        return dict(trade_report)
    commander = state.get('commander_decision') if isinstance(state.get('commander_decision'), dict) else {}
    commander_policy = commander.get('applied_policy') if isinstance(commander.get('applied_policy'), dict) else {}
    commander_reporter = commander_policy.get('reporter') if isinstance(commander_policy.get('reporter'), dict) else {}
    commander_trade_report = commander_reporter.get('trade_report') if isinstance(commander_reporter.get('trade_report'), dict) else {}
    return dict(commander_trade_report or {})


def _null_execution_details_r4_impl(*, facade):
    return {'order_status': None, 'order_id': None, 'execution_mode': None, 'broker_env': None, 'filled_qty': None, 'avg_price': None}


def _execution_details_from_state_r4_impl(state, *, facade):
    execution = facade._execution_payload(state)
    monitor = state.get('monitor_output') if isinstance(state.get('monitor_output'), dict) else {}
    synthetic_bundle = {'execution': dict(execution), 'executor': dict(execution), 'monitor': dict(monitor)}
    return facade.build_execution_details(synthetic_bundle, context={'monitor_context': dict(monitor), 'execution_context': dict(execution)})


def _entry_strategist_context_r4_impl(state, symbol, *, facade):
    persisted = state.get('persisted_state') if isinstance(state.get('persisted_state'), dict) else {}
    strategy_map = persisted.get('position_strategy_context') if isinstance(persisted.get('position_strategy_context'), dict) else {}
    stored = strategy_map.get(symbol) if isinstance(strategy_map.get(symbol), dict) else {}
    output = stored.get('output') if isinstance(stored.get('output'), dict) else {}
    if output:
        return dict(output)
    strategist = state.get('strategist_output') if isinstance(state.get('strategist_output'), dict) else {}
    return dict(strategist)


def _build_monitor_snapshot_r4_impl(monitor, *, symbol, run_id, ts, facade):
    return {'run_id': str(run_id or ''), 'ts': str(ts or ''), 'symbol': str(symbol or ''), 'decision': str(monitor.get('decision') or ''), 'decision_summary': str(monitor.get('decision_summary') or ''), 'primary_reason_code': str(monitor.get('primary_reason_code') or monitor.get('no_trade_reason_code') or ''), 'current_price': monitor.get('current_price'), 'avg_price': (monitor.get('position_snapshot') or {} if isinstance(monitor.get('position_snapshot'), dict) else {}).get('avg_price'), 'qty': (monitor.get('position_snapshot') or {} if isinstance(monitor.get('position_snapshot'), dict) else {}).get('qty'), 'position_age_seconds': monitor.get('position_age_seconds')}


def _format_duration_r4_impl(seconds, *, facade):
    total = max(0, int(seconds or 0))
    mins, sec = divmod(total, 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return f'{hours:02d}:{mins:02d}:{sec:02d}'
    return f'00:{mins:02d}:{sec:02d}'
