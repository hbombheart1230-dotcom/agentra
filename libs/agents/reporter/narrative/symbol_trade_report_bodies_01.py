"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/symbol_trade_report.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _safe_float_r4_impl(value, *, facade):
    try:
        if value is None or value == '':
            return None
        return float(value)
    except Exception:
        return None


def _normalize_pct_like_r4_impl(value, *, facade):
    parsed = facade._safe_float(value)
    if parsed is None:
        return None
    if abs(parsed) <= 0.2:
        return parsed * 100.0
    return parsed


def _pick_result_pct_r4_impl(*values, facade):
    normalized: List[float] = []
    for value in values:
        parsed = facade._normalize_pct_like(value)
        if parsed is not None:
            normalized.append(parsed)
    if not normalized:
        return None
    for parsed in normalized:
        if abs(parsed) > 1e-12:
            return parsed
    return normalized[0]


def _safe_int_r4_impl(value, *, facade):
    try:
        if value is None or value == '':
            return 0
        return int(float(value))
    except Exception:
        return 0


def _normalize_ts_r4_impl(value, *, facade):
    text = str(value or '').strip()
    if not text:
        return ''
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    return text


def _to_epoch_r4_impl(value, *, facade):
    text = facade._normalize_ts(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except Exception:
        pass
    try:
        dt = facade.datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return 0


def _normalize_lifecycle_bundle_r4_impl(bundle, *, facade):
    lifecycle = bundle.get('lifecycle') if isinstance(bundle.get('lifecycle'), dict) else {}
    entry = lifecycle.get('entry') if isinstance(lifecycle.get('entry'), dict) else {}
    exit_row = lifecycle.get('exit') if isinstance(lifecycle.get('exit'), dict) else {}
    trade_outcome = bundle.get('trade_outcome') if isinstance(bundle.get('trade_outcome'), dict) else {}
    if not entry and (not exit_row):
        return {}
    summary = {'entry_reason_human': str(entry.get('reason_human') or ''), 'exit_reason_human': str(exit_row.get('reason_human') or trade_outcome.get('exit_reason') or ''), 'lifecycle_summary_human': str(bundle.get('summary') or trade_outcome.get('summary') or ''), 'operator_conclusion_human': str((bundle.get('reporter_status_human') or {} if isinstance(bundle.get('reporter_status_human'), dict) else {}).get('operator_conclusion_human') or '')}
    normalized = {'trade_id': str(bundle.get('trade_id') or ''), 'symbol': str(bundle.get('symbol') or ''), 'day': str(bundle.get('day') or ''), 'status': str(bundle.get('trade_lifecycle_status') or bundle.get('status') or ''), 'trade_origin': str(bundle.get('trade_origin') or ('recovered_partial' if str(bundle.get('trade_lifecycle_status') or bundle.get('status') or '').strip().lower() == 'partial' else 'normal_lifecycle')), 'lifecycle_completeness': str(bundle.get('lifecycle_completeness') or ('partial' if str(bundle.get('trade_lifecycle_status') or bundle.get('status') or '').strip().lower() == 'partial' else 'complete')), 'evidence_recovery_used': bool(bundle.get('evidence_recovery_used')), 'entry': entry, 'exit': exit_row, 'summary': summary, 'artifacts': dict(bundle.get('artifacts') or {})}
    return normalized


def _result_pct_from_lifecycle_r4_impl(obj, *, facade):
    entry = obj.get('entry') if isinstance(obj.get('entry'), dict) else {}
    exit_row = obj.get('exit') if isinstance(obj.get('exit'), dict) else {}
    entry_price = facade._safe_float(entry.get('price'))
    exit_price = facade._safe_float(exit_row.get('price'))
    if entry_price is None or exit_price is None or entry_price == 0:
        return None
    return (exit_price - entry_price) / entry_price * 100.0


def _list_text_r4_impl(values, *, limit, facade):
    out: List[str] = []
    for value in list(values or []):
        text = str(value or '').strip()
        if not text or text in out:
            continue
        out.append(text)
        if len(out) >= limit:
            break
    return out


def _clean_symbol_pattern_r4_impl(value, *, axis, fallback_reason, facade):
    text = str(value or '').strip()
    lowered = text.lower()
    if lowered.startswith('scanner selected ') or lowered.startswith('entry reason was not captured') or lowered.startswith('entry evidence was not captured'):
        return ''
    if lowered.startswith('entry context was recovered'):
        return ''
    return facade._operator_pattern_name(value, axis=axis, fallback_reason=fallback_reason)


def _clean_symbol_free_text_r4_impl(value, *, entry_reason, exit_reason, facade):
    text = str(value or '').strip()
    if not text:
        return ''
    lowered = text.lower()
    if 'scanner selected' in text:
        return entry_reason or facade._clean_symbol_reason(text, axis='entry')
    if 'sell was triggered' in text or 'sell 실행 및 잔여수량' in lowered:
        return exit_reason or facade._clean_symbol_reason(text, axis='exit')
    if 'trigger_type=trailing_stop' in lowered or 'trailing_stop' in lowered:
        return text.replace('trigger_type=trailing_stop', '청산축=추적 손절').replace('trailing_stop', '추적 손절')
    if text.lower() == 'unknown':
        return ''
    return text


def _classify_entry_pattern_r4_impl(text, *, facade):
    if facade._contains_any(text, ['돌파']):
        return 'breakout'
    if facade._contains_any(text, ['눌림', '풀백']):
        return 'pullback'
    if facade._contains_any(text, ['재회복']):
        return 'reclaim'
    if facade._contains_any(text, ['breakout']):
        return 'breakout'
    if facade._contains_any(text, ['reclaim']):
        return 'reclaim'
    if facade._contains_any(text, ['pullback']):
        return 'pullback'
    if facade._contains_any(text, ['continuation']):
        return 'continuation'
    return 'unknown'


def _classify_exit_pattern_r4_impl(text, *, facade):
    if facade._contains_any(text, ['장중 저점']):
        return 'intraday_low_break'
    if facade._contains_any(text, ['vwap 이탈']):
        return 'vwap_breakdown'
    if facade._contains_any(text, ['고점 대비']):
        return 'peak_drawdown'
    if facade._contains_any(text, ['손절']):
        return 'hard_stop'
    if facade._contains_any(text, ['익절', '목표 수익']):
        return 'take_profit'
    if facade._contains_any(text, ['intraday_low_break']):
        return 'intraday_low_break'
    if facade._contains_any(text, ['vwap_breakdown']):
        return 'vwap_breakdown'
    if facade._contains_any(text, ['trend_breakdown']):
        return 'trend_breakdown'
    if facade._contains_any(text, ['peak_drawdown']):
        return 'peak_drawdown'
    if facade._contains_any(text, ['hard_stop', 'stop_loss']):
        return 'hard_stop'
    if facade._contains_any(text, ['trailing_stop']):
        return 'trailing_stop'
    if facade._contains_any(text, ['take_profit']):
        return 'take_profit'
    return 'unknown'


def _dict_at_r4_impl(root, *keys, facade):
    cur: Any = root
    for key in keys:
        if not isinstance(cur, dict):
            return {}
        cur = cur.get(key)
    return cur if isinstance(cur, dict) else {}


def _should_prefer_artifact_entry_reason_r4_impl(raw_reason, artifact_reason, *, facade):
    artifact_text = str(artifact_reason or '').strip()
    if not artifact_text:
        return False
    raw_text = str(raw_reason or '').strip()
    if not raw_text:
        return True
    lowered = raw_text.lower()
    return lowered.startswith('scanner selected ') or lowered.startswith('entry evidence was not captured')


def _clean_lifecycle_summary_r4_impl(*, trade_id, status, entry_reason, exit_reason, facade):
    pieces = [f'거래 {trade_id}' if trade_id else '거래', f"상태 {status or '미기록'}"]
    if entry_reason:
        pieces.append(f'진입 {entry_reason}')
    if exit_reason:
        pieces.append(f'청산 {exit_reason}')
    return ' / '.join(pieces)


def _hold_seconds_from_lifecycle_r4_impl(obj, *, facade):
    entry = obj.get('entry') if isinstance(obj.get('entry'), dict) else {}
    exit_row = obj.get('exit') if isinstance(obj.get('exit'), dict) else {}
    entry_ts = facade._to_epoch(entry.get('ts'))
    exit_ts = facade._to_epoch(exit_row.get('ts'))
    if entry_ts > 0 and exit_ts > 0 and (exit_ts >= entry_ts):
        return float(exit_ts - entry_ts)
    return None


def _pattern_rows_r4_impl(history, *, positive, facade):
    counter: facade.Counter[str] = facade.Counter()
    for row in history:
        result_pct = facade._safe_float(row.get('result_pct'))
        if result_pct is None:
            continue
        if positive and result_pct <= 0:
            continue
        if not positive and result_pct >= 0:
            continue
        pattern_type = facade._clean_symbol_pattern(row.get('entry_pattern_type'), axis='entry', fallback_reason=row.get('entry_reason'))
        if pattern_type:
            counter[pattern_type] += 1
            continue
        reason = facade._clean_symbol_reason(row.get('entry_reason'), axis='entry')
        if reason:
            counter[reason] += 1
    return [name for name, _count in counter.most_common(5)]


def _derive_playbook_stats_r4_impl(history, *, facade):
    grouped: Dict[str, Dict[str, Any]] = {}
    for row in history:
        playbook = str(row.get('playbook') or '').strip()
        if not playbook:
            continue
        bucket = grouped.setdefault(playbook, {'count': 0, 'completed_count': 0, 'win_count': 0, 'return_values': []})
        bucket['count'] += 1
        status = str(row.get('status') or '').strip().lower()
        result_pct = facade._safe_float(row.get('result_pct'))
        if status == 'closed':
            bucket['completed_count'] += 1
            if result_pct is not None:
                bucket['return_values'].append(result_pct)
                if result_pct > 0:
                    bucket['win_count'] += 1
    out: Dict[str, Dict[str, Any]] = {}
    for playbook, bucket in grouped.items():
        completed_count = int(bucket.get('completed_count') or 0)
        return_values = [float(v) for v in list(bucket.get('return_values') or [])]
        out[playbook] = {'count': int(bucket.get('count') or 0), 'win_rate': round(facade._ratio(float(bucket.get('win_count') or 0), float(completed_count)), 4), 'avg_return_pct': round(sum(return_values) / len(return_values), 4) if return_values else 0.0}
    return out


def _derive_dominant_exit_failure_axis_r4_impl(history, *, facade):
    counter: facade.Counter[str] = facade.Counter()
    for row in history:
        status = str(row.get('status') or '').strip().lower()
        result_pct = facade._safe_float(row.get('result_pct'))
        if status != 'closed' or result_pct is None or result_pct >= 0:
            continue
        exit_pattern = facade._clean_symbol_pattern(row.get('exit_pattern_type'), axis='exit', fallback_reason=row.get('exit_reason'))
        if exit_pattern:
            counter[exit_pattern] += 1
            continue
        exit_reason = facade._clean_symbol_reason(row.get('exit_reason'), axis='exit')
        if exit_reason:
            counter[exit_reason] += 1
    if not counter:
        return ''
    return str(counter.most_common(1)[0][0])


def _derive_bias_recommendation_r4_impl(*, avg_return_pct, playbook_stats, repeated_blockers, facade):
    prefer_playbook = ''
    avoid_playbook = ''
    scanner_bonus = 0.0
    scanner_penalty = 0.0
    risk_cap = 'normal'
    best_playbook = ''
    best_return = -10 ** 9
    worst_playbook = ''
    worst_return = 10 ** 9
    for playbook, stats in playbook_stats.items():
        avg_return = facade._safe_float((stats or {}).get('avg_return_pct'))
        if avg_return is None:
            continue
        if avg_return > best_return:
            best_return = avg_return
            best_playbook = playbook
        if avg_return < worst_return:
            worst_return = avg_return
            worst_playbook = playbook
    if best_playbook and best_return > 0:
        prefer_playbook = best_playbook
        scanner_bonus = 0.05 if best_return < 1.0 else 0.08
    if worst_playbook and worst_return < 0:
        avoid_playbook = worst_playbook
        scanner_penalty = 0.05 if worst_return > -1.0 else 0.08
    lowered_blockers = {str(x or '').strip().lower() for x in repeated_blockers}
    if avg_return_pct < 0 or {'confirmed_entry', 'breakout_readiness'} & lowered_blockers:
        risk_cap = 'conservative'
        scanner_penalty = max(scanner_penalty, 0.08 if avg_return_pct < 0 else 0.05)
    return {'scanner_penalty': round(scanner_penalty, 4), 'scanner_bonus': round(scanner_bonus, 4), 'prefer_playbook': prefer_playbook, 'avoid_playbook': avoid_playbook, 'risk_cap': risk_cap}
