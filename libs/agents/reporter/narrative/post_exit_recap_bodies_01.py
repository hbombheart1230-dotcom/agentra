"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/post_exit_shadow_recap.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _symbol_candidates_r4_impl(symbol, *, facade):
    normalized = facade.normalize_symbol(symbol or '', allow_test_symbols=True)
    out = [normalized] if normalized else []
    if normalized and (not normalized.startswith('A')):
        out.append(f'A{normalized}')
    return out


def _rows_from_record_r4_impl(record, candidates, *, facade):
    if isinstance(record, list):
        return [dict(row) for row in record if isinstance(row, dict)]
    if not isinstance(record, dict):
        return []
    rows = record.get('rows')
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    result = record.get('result') if isinstance(record.get('result'), dict) else {}
    data = result.get('data') if isinstance(result.get('data'), dict) else record.get('data')
    if isinstance(data, dict):
        nested_rows = data.get('rows')
        if isinstance(nested_rows, list):
            return [dict(row) for row in nested_rows if isinstance(row, dict)]
        for candidate in candidates:
            found = facade._rows_from_record(data.get(candidate), candidates)
            if found:
                return found
    for candidate in candidates:
        found = facade._rows_from_record(record.get(candidate), candidates)
        if found:
            return found
    return []


def _latest_epoch_r4_impl(rows, *, facade):
    best = 0
    for row in rows:
        try:
            best = max(best, int(float(row.get('ts'))))
        except Exception:
            continue
    return best


def _epoch_seconds_r4_impl(value, *, facade):
    if value in (None, ''):
        return None
    try:
        raw = float(value)
        if raw > 0:
            return raw
    except Exception:
        pass
    try:
        text = str(value).strip()
        if not text:
            return None
        dt = facade.datetime.fromisoformat(text.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return float(dt.timestamp())
    except Exception:
        return None


def _shadow_latest_required_epoch_r4_impl(shadow, *, facade):
    exit_epoch = facade._epoch_seconds(shadow.get('exit_ts'))
    if exit_epoch is None:
        return None
    checkpoints = facade._as_dict(shadow.get('checkpoints'))
    best: float | None = None
    for label, minutes in (('+5m', 5), ('+15m', 15), ('+30m', 30), ('+60m', 60)):
        row = facade._as_dict(checkpoints.get(label))
        if str(row.get('status') or '').strip().lower() == 'observed':
            continue
        target_epoch = facade._epoch_seconds(row.get('target_ts'))
        if target_epoch is None:
            target_epoch = exit_epoch + minutes * 60
        best = target_epoch if best is None else max(best, target_epoch)
    return best


def _minute_row_key_r4_impl(row, *, facade):
    raw_ts = str(row.get('raw_ts') or '').strip()
    if raw_ts:
        return f'raw:{raw_ts}'
    ts = facade._epoch_seconds(row.get('ts'))
    if ts is not None:
        return f'ts:{int(ts)}'
    return ''


def merge_minute_rows_r4_impl(*row_groups, facade):
    merged: Dict[str, Dict[str, Any]] = {}
    anonymous: List[Dict[str, Any]] = []
    for rows in row_groups:
        for row in rows or []:
            if not isinstance(row, facade.Mapping):
                continue
            item = dict(row)
            key = facade._minute_row_key(item)
            if key:
                merged[key] = item
            else:
                anonymous.append(item)
    out = list(merged.values()) + anonymous
    return sorted(out, key=lambda row: (facade._epoch_seconds(row.get('ts')) or 0.0, str(row.get('raw_ts') or '')))


def fetch_fresh_minute_rows_for_symbol_r4_impl(symbol, *, run_id, facade):
    normalized = facade.normalize_symbol(symbol or '', allow_test_symbols=True)
    meta: Dict[str, Any] = {'attempted': True, 'ok': False, 'symbol': normalized, 'rows': 0, 'source': 'market.minute_ohlcv'}
    if not normalized:
        meta['reason'] = 'missing_symbol'
        return ([], meta)
    try:
        from libs.runtime.monitor_minute_ohlcv import _extract_monitor_minute_rows, _fresh_monitor_skill_runner, _run_monitor_minute_skill
        runner, source = _fresh_monitor_skill_runner()
        meta['runner_source'] = source
        if runner is None:
            meta['reason'] = 'runner_unavailable'
            return ([], meta)
        rec = _run_monitor_minute_skill(runner=runner, run_id=run_id, symbol=normalized, timeframe_minutes=1)
        _result, rows = _extract_monitor_minute_rows(rec)
        clean_rows = [dict(row) for row in rows if isinstance(row, dict)]
        meta['ok'] = bool(clean_rows)
        meta['rows'] = len(clean_rows)
        meta['reason'] = '' if clean_rows else 'no_rows_returned'
        return (clean_rows, meta)
    except Exception as exc:
        meta['reason'] = 'fresh_minute_fetch_failed'
        meta['error'] = str(exc)
        return ([], meta)


def minute_rows_for_symbol_from_state_r4_impl(state, symbol, *, facade):
    candidates = facade._symbol_candidates(symbol)
    if not candidates:
        return []
    found: List[List[Dict[str, Any]]] = []

    def collect(container: Mapping[str, Any]) -> None:
        for key in ('recent_minute_ohlcv_by_symbol', 'minute_ohlcv_by_symbol', 'monitor_minute_ohlcv_by_symbol', 'intraday_ohlcv_by_symbol', 'ohlcv_by_symbol'):
            root = container.get(key)
            if not isinstance(root, dict):
                continue
            for candidate in candidates:
                rows = facade._rows_from_record(root.get(candidate), candidates)
                if rows:
                    found.append(rows)
    collect(state)
    persisted = state.get('persisted_state')
    if isinstance(persisted, dict):
        collect(persisted)
    skill_results = state.get('skill_results') if isinstance(state.get('skill_results'), dict) else {}
    for key in ('market.minute_ohlcv_by_symbol', 'market.minute_ohlcv', 'market.minute_candles', 'market.candles'):
        raw = skill_results.get(key)
        if isinstance(raw, dict):
            for candidate in candidates:
                rows = facade._rows_from_record(raw.get(candidate), candidates)
                if rows:
                    found.append(rows)
            if facade.normalize_symbol(raw.get('symbol') or '', allow_test_symbols=True) in candidates:
                rows = facade._rows_from_record(raw, candidates)
                if rows:
                    found.append(rows)
    history = state.get('skill_results_history') if isinstance(state.get('skill_results_history'), dict) else {}
    minute_history = history.get('market.minute_ohlcv')
    if isinstance(minute_history, list):
        for item in minute_history:
            if not isinstance(item, dict):
                continue
            if facade.normalize_symbol(item.get('symbol') or '', allow_test_symbols=True) not in candidates:
                continue
            rows = facade._rows_from_record(item.get('record'), candidates)
            if rows:
                found.append(rows)
    if not found:
        return []
    found.sort(key=lambda rows: (facade._latest_epoch(rows), len(rows)), reverse=True)
    return [dict(row) for row in found[0] if isinstance(row, dict)]


def _parse_exit_kst_date_r4_impl(exit_ts, *, facade):
    raw = str(exit_ts or '').strip()
    if not raw:
        return ''
    try:
        dt = facade.datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except Exception:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=facade.timezone.utc)
    return dt.astimezone(facade.KST).strftime('%Y%m%d')


def _row_kst_date_r4_impl(row, *, facade):
    raw_ts = str(row.get('raw_ts') or '').strip()
    if len(raw_ts) >= 8 and raw_ts[:8].isdigit():
        return raw_ts[:8]
    try:
        ts = float(row.get('ts'))
    except Exception:
        return ''
    return facade.datetime.fromtimestamp(ts, tz=facade.timezone.utc).astimezone(facade.KST).strftime('%Y%m%d')


def _row_kst_hhmmss_r4_impl(row, *, facade):
    raw_ts = str(row.get('raw_ts') or '').strip()
    if len(raw_ts) >= 14 and raw_ts[8:14].isdigit():
        return raw_ts[8:14]
    try:
        ts = float(row.get('ts'))
    except Exception:
        return ''
    return facade.datetime.fromtimestamp(ts, tz=facade.timezone.utc).astimezone(facade.KST).strftime('%H%M%S')


def same_day_closeout_rows_for_shadow_r4_impl(shadow, rows, *, facade):
    """Keep the recap scoped to the sell date and full close, not T+1 drift."""
    exit_day = facade._parse_exit_kst_date(shadow.get('exit_ts'))
    if not exit_day:
        return [dict(row) for row in rows]
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if facade._row_kst_date(row) != exit_day:
            continue
        hhmmss = facade._row_kst_hhmmss(row)
        if hhmmss and hhmmss > '160000':
            continue
        out.append(dict(row))
    return out


def _checkpoint_target_after_regular_close_r4_impl(row, *, facade):
    target_epoch = facade._epoch_seconds(row.get('target_ts'))
    if target_epoch is None:
        return False
    hhmmss = facade.datetime.fromtimestamp(target_epoch, tz=facade.timezone.utc).astimezone(facade.KST).strftime('%H%M%S')
    return hhmmss > '153000'


def _fill_regular_close_bound_pending_checkpoints_r4_impl(shadow, *, facade):
    """Close reporting-only checkpoints that mature after the regular session.

    A trade sold after 14:30 can have a +60m target past 15:30. Regular-session
    minute bars stop at the close, so a strict target lookup would stay pending
    forever even after the 16:00 recap. In that case the regular close is the
    final same-session observation for the report.
    """
    out = dict(shadow)
    checkpoints = facade._as_dict(out.get('checkpoints'))
    eod = facade._as_dict(checkpoints.get('EOD'))
    if str(eod.get('status') or '').strip().lower() != 'observed':
        return out
    eod_price = eod.get('price') if eod.get('price') is not None else eod.get('close')
    eod_ts = eod.get('observed_ts')
    exit_price = None
    try:
        exit_price = float(out.get('exit_price'))
    except Exception:
        exit_price = None
    for label in ('+5m', '+15m', '+30m', '+60m'):
        row = facade._as_dict(checkpoints.get(label))
        if str(row.get('status') or '').strip().lower() == 'observed':
            continue
        if not facade._checkpoint_target_after_regular_close(row):
            continue
        row.update({'status': 'observed', 'observed_ts': eod_ts, 'raw_ts': eod.get('raw_ts') or '', 'price': eod_price, 'observed_price': eod_price, 'closeout_substitute': True, 'closeout_substitute_reason': 'checkpoint_target_after_regular_session_close'})
        if exit_price and eod_price not in (None, ''):
            try:
                row['return_pct'] = float(eod_price) / float(exit_price) - 1.0
            except Exception:
                pass
        for key in ('high_since_exit', 'low_since_exit', 'max_upside_pct', 'max_drawdown_pct', 'observation_count'):
            if eod.get(key) is not None:
                row[key] = eod.get(key)
        checkpoints[label] = row
    out['checkpoints'] = checkpoints
    return out


def _post_exit_shadow_from_report_r4_impl(report, *, facade):
    fact_payload = facade._as_dict(report.get('fact_payload'))
    fact_trade = facade._as_dict(fact_payload.get('trade'))
    lifecycle = facade._as_dict(report.get('trade_lifecycle'))
    lifecycle_exit = facade._as_dict(lifecycle.get('exit'))
    lifecycle_bundle = facade._as_dict(report.get('lifecycle_bundle'))
    for candidate in (report.get('post_exit_shadow'), fact_trade.get('post_exit_shadow'), lifecycle.get('post_exit_shadow'), lifecycle_exit.get('post_exit_shadow'), lifecycle_bundle.get('post_exit_shadow')):
        if isinstance(candidate, dict) and candidate:
            return dict(candidate)
    return {}


def _checkpoint_summary_r4_impl(shadow, *, facade):
    checkpoints = facade._as_dict(shadow.get('checkpoints'))
    out: Dict[str, Any] = {}
    for label in facade.CHECKPOINT_LABELS:
        row = facade._as_dict(checkpoints.get(label))
        out[label] = {'status': str(row.get('status') or 'pending'), 'price': row.get('price') if row.get('price') is not None else row.get('close'), 'return_pct': row.get('return_pct'), 'observed_ts': row.get('observed_ts'), 'latest_observed_ts': row.get('latest_observed_ts')}
    return out


def _render_trade_recap_markdown_r4_impl(trade, *, facade):
    lines = [f"# 매도 후 가격 추적 Recap - {trade.get('label')}", '', '- 기준: 실제 매도 후 같은 종목을 가상 보유했다고 가정한 관측 전용 결과입니다.', '- 적용: 기존 ai_trade_report 본문은 수정하지 않고 recap과 summary 산출물만 갱신합니다.', f"- 가격 관측 상태: {trade.get('price_observation_status')}", f"- 사유: {trade.get('price_observation_reason') or '-'}", f"- 마지막 관측 시각: {trade.get('latest_observed_ts') or '-'}", f"- 최선 관측 지점: {trade.get('best_exit_offset') or '-'} / {facade._price(trade.get('best_exit_price'))}", f"- 최대 매도 후 상승: {facade._pct(trade.get('max_post_exit_upside_pct'))}", f"- 최대 매도 후 하락: {facade._pct(trade.get('max_post_exit_drawdown_pct'))}", '', '| 지점 | 상태 | 가격 | 수익률 | 관측 시각 |', '| --- | --- | ---: | ---: | --- |']
    checkpoints = facade._as_dict(trade.get('checkpoints'))
    for label in facade.CHECKPOINT_LABELS:
        row = facade._as_dict(checkpoints.get(label))
        lines.append(f"| {label} | {row.get('status') or 'pending'} | {facade._price(row.get('price'))} | {facade._pct(row.get('return_pct'))} | {row.get('observed_ts') or row.get('latest_observed_ts') or '-'} |")
    return '\n'.join(lines) + '\n'
