"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/symbol_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _get_dominant_r4_impl(items, exclude, *, facade):
    valid_items = [str(x).strip() for x in items if str(x).strip() and str(x).strip().lower() != exclude]
    if not valid_items:
        return exclude
    counter = facade.Counter(valid_items)
    if not counter:
        return exclude
    return counter.most_common(1)[0][0]


def _is_unknown_quality_field_r4_impl(field_name, value, *, facade):
    text = str(value or '').strip().lower()
    if not text or text == 'unknown':
        return True
    if field_name == 'data_source' and text == 'lifecycle_bundle':
        return True
    return False


def _safe_float_r4_impl(value, default, *, facade):
    try:
        if value is None or value == '':
            return default
        return float(value)
    except Exception:
        return default


def _date_from_trade_id_r4_impl(value, *, facade):
    text = str(value or '').strip()
    match = facade.re.search('TRD_(\\d{8})_', text)
    if not match:
        return ''
    raw = match.group(1)
    return f'{raw[:4]}-{raw[4:6]}-{raw[6:8]}'


def _empty_symbol_read_model_r4_impl(symbol, *, facade):
    return {'symbol': symbol, 'trade_count': 0, 'closed_trade_count': 0, 'win_count': 0, 'loss_count': 0, 'win_rate': 0.0, 'total_pnl': 0.0, 'avg_pnl': 0.0, 'avg_pnl_pct': 0.0, 'avg_hold_duration_sec': 0.0, 'last_trade_date': '', 'last_status': '', 'dominant_playbook': 'unknown', 'dominant_entry_reason': 'unknown', 'dominant_exit_reason': 'unknown', 'dominant_monitor_blocker': 'unknown', 'recent_success_pattern': [], 'repeated_failure_pattern': [], 'data_quality': {'unknown_fields_ratio': 0.0}}


def _aggregate_symbol_trades_r4_impl(symbol, trades, *, facade):
    trade_count = len(trades)
    playbooks = []
    entry_reasons = []
    exit_reasons = []
    blockers = []
    closed_trade_count = 0
    win_count = 0
    loss_count = 0
    total_pnl = 0.0
    total_pnl_pct = 0.0
    total_hold_sec = 0
    last_trade_date = ''
    success_patterns_counter = facade.Counter()
    failure_patterns_counter = facade.Counter()
    total_fields_checked = 0
    unknown_fields_count = 0
    fields_to_check = ['playbook', 'entry_reason', 'exit_reason', 'primary_blocker_if_no_buy', 'execution_label', 'data_source']
    for t in trades:
        playbooks.append(t.get('playbook'))
        entry_reasons.append(t.get('entry_reason'))
        exit_reasons.append(t.get('exit_reason'))
        blockers.append(t.get('primary_blocker_if_no_buy'))
        for f in fields_to_check:
            total_fields_checked += 1
            if facade._is_unknown_quality_field(f, t.get(f)):
                unknown_fields_count += 1
        pnl = float(t.get('pnl') or 0.0)
        pnl_pct = float(t.get('pnl_pct') or 0.0)
        is_closed = str(t.get('exit_reason') or 'unknown').lower() != 'unknown' or pnl != 0.0
        if is_closed:
            closed_trade_count += 1
            total_pnl += pnl
            total_pnl_pct += pnl_pct
            total_hold_sec += int(t.get('hold_duration_sec') or 0)
            if pnl > 0:
                win_count += 1
                pattern = f"{t.get('playbook')}|{t.get('entry_reason')}|{t.get('exit_reason')}"
                success_patterns_counter[pattern] += 1
            elif pnl < 0:
                loss_count += 1
                failure_patterns_counter['exit_reason', str(t.get('exit_reason'))] += 1
        blocker = str(t.get('primary_blocker_if_no_buy') or 'unknown')
        if blocker.lower() != 'unknown':
            failure_patterns_counter['blocker', blocker] += 1
        candidate_trade_date = str(t.get('trade_date') or t.get('date') or facade._date_from_trade_id(t.get('trade_id')) or '').strip()
        if candidate_trade_date and candidate_trade_date > last_trade_date:
            last_trade_date = candidate_trade_date
    recent_success_pattern = []
    for pat, count in success_patterns_counter.most_common(3):
        pb, ent, ext = pat.split('|')
        recent_success_pattern.append({'playbook': pb, 'entry_reason': ent, 'exit_reason': ext, 'count': count})
    repeated_failure_pattern = []
    for (ptype, pval), count in failure_patterns_counter.most_common(3):
        repeated_failure_pattern.append({'type': ptype, 'value': pval, 'count': count})
    return {'symbol': symbol, 'trade_count': trade_count, 'closed_trade_count': closed_trade_count, 'win_count': win_count, 'loss_count': loss_count, 'win_rate': facade._safe_div(float(win_count), float(win_count + loss_count)), 'total_pnl': float(total_pnl), 'avg_pnl': facade._safe_div(total_pnl, float(closed_trade_count)), 'avg_pnl_pct': facade._safe_div(total_pnl_pct, float(closed_trade_count)), 'avg_hold_duration_sec': facade._safe_div(float(total_hold_sec), float(closed_trade_count)), 'last_trade_date': last_trade_date, 'last_status': '', 'dominant_playbook': facade._get_dominant(playbooks), 'dominant_entry_reason': facade._get_dominant(entry_reasons), 'dominant_exit_reason': facade._get_dominant(exit_reasons), 'dominant_monitor_blocker': facade._get_dominant(blockers), 'recent_success_pattern': recent_success_pattern, 'repeated_failure_pattern': repeated_failure_pattern, 'data_quality': {'unknown_fields_ratio': facade._safe_div(float(unknown_fields_count), float(total_fields_checked))}}
