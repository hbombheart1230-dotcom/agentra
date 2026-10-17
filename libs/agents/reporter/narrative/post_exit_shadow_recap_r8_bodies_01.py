"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/post_exit_shadow_recap.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _post_exit_shadow_from_lifecycle_r4_impl(report_path, *, facade):
    trade_dir = report_path.parents[1]
    bundle = facade._read_json(trade_dir / 'lifecycle_bundle.json')
    if not bundle:
        return {}
    lifecycle = facade._as_dict(bundle.get('lifecycle')) or bundle
    status = str(bundle.get('trade_lifecycle_status') or lifecycle.get('status') or bundle.get('status') or '').strip()
    exit_ctx = facade._as_dict(lifecycle.get('exit')) or facade._as_dict(bundle.get('exit'))
    exit_details = facade._as_dict(exit_ctx.get('execution_details')) or facade._as_dict(bundle.get('exit_execution_details')) or facade._as_dict(bundle.get('execution_details'))
    return facade.build_post_exit_shadow_placeholder(lifecycle_bundle=bundle, lifecycle=lifecycle, status=status, exit_execution_details=exit_details)


def _trade_label_r4_impl(path, report, shadow, *, facade):
    trade_id = str(report.get('trade_id') or report.get('story_id') or path.parents[1].name).strip()
    symbol = str(shadow.get('symbol') or report.get('symbol') or '').strip()
    if symbol:
        return f'{trade_id} / {symbol}'
    return trade_id


def build_post_exit_shadow_recap_r4_impl(*, reports_root, day, state, generated_at, facade):
    state_obj = state if isinstance(state, facade.Mapping) else {}
    trades: List[Dict[str, Any]] = []
    fresh_minute_cache: Dict[str, tuple[List[Dict[str, Any]], Dict[str, Any]]] = {}
    for report_path in facade.iter_trade_report_json_paths(reports_root, day):
        report = facade._read_json(report_path)
        shadow = facade._post_exit_shadow_from_report(report)
        if not shadow:
            shadow = facade._post_exit_shadow_from_lifecycle(report_path)
        if not shadow:
            continue
        symbol = str(shadow.get('symbol') or report.get('symbol') or '').strip()
        rows = facade.minute_rows_for_symbol_from_state(state_obj, symbol) if symbol else []
        rows = facade.same_day_closeout_rows_for_shadow(shadow, rows)
        fresh_minute_fetch: Dict[str, Any] = {'attempted': False}
        if symbol and facade._fresh_minute_fetch_enabled() and facade._post_exit_shadow_needs_fresh_minutes(shadow, rows):
            cached = fresh_minute_cache.get(symbol)
            if cached is None:
                fresh_rows, fresh_minute_fetch = facade.fetch_fresh_minute_rows_for_symbol(symbol, run_id=f'post_exit_shadow_recap:{day}:{symbol}')
                fresh_minute_cache[symbol] = (list(fresh_rows), dict(fresh_minute_fetch))
                fresh_minute_fetch = {**fresh_minute_fetch, 'cache_hit': False}
            else:
                cached_rows, cached_fetch = cached
                fresh_rows = list(cached_rows)
                fresh_minute_fetch = {**cached_fetch, 'cache_hit': True}
            fresh_rows = facade.same_day_closeout_rows_for_shadow(shadow, fresh_rows)
            rows = facade.merge_minute_rows(rows, fresh_rows)
        eod_fallback: Dict[str, Any] = {'applied': False}
        if symbol and (not facade._rows_reach_regular_close(rows)):
            fallback_row, eod_fallback = facade.opening_rank1_eod_fallback_row(reports_root=reports_root, day=day, symbol=symbol)
            if fallback_row:
                rows = facade.merge_minute_rows(rows, [fallback_row])
        updated_shadow = facade.update_post_exit_shadow_with_price_observations(shadow, minute_rows=rows) if rows else dict(shadow)
        updated_shadow = facade._fill_regular_close_bound_pending_checkpoints(updated_shadow)
        checkpoints = facade._checkpoint_summary(updated_shadow)
        trades.append({'trade_id': str(report.get('trade_id') or report.get('story_id') or report_path.parents[1].name), 'symbol': symbol, 'report_path': str(report_path), 'recap_json_path': str(report_path.with_name('post_exit_shadow_recap.json')), 'recap_md_path': str(report_path.with_name('post_exit_shadow_recap.md')), 'price_observation_status': str(updated_shadow.get('price_observation_status') or 'pending'), 'price_observation_reason': str(updated_shadow.get('price_observation_reason') or ''), 'latest_observed_ts': updated_shadow.get('latest_observed_ts'), 'best_exit_offset': str(updated_shadow.get('best_exit_offset') or ''), 'best_exit_price': updated_shadow.get('best_exit_price'), 'max_post_exit_upside_pct': updated_shadow.get('max_post_exit_upside_pct'), 'max_post_exit_drawdown_pct': updated_shadow.get('max_post_exit_drawdown_pct'), 'checkpoints': checkpoints, 'post_exit_shadow': updated_shadow, 'label': facade._trade_label(report_path, report, updated_shadow), 'source_minute_rows': len(rows), 'fresh_minute_fetch': fresh_minute_fetch, 'eod_fallback': eod_fallback})
    observed_count = sum((1 for trade in trades if trade.get('price_observation_status') == 'observed'))
    eod_observed_count = sum((1 for trade in trades if facade._as_dict(facade._as_dict(trade.get('checkpoints')).get('EOD')).get('status') == 'observed'))
    return {'schema_version': 'post_exit_shadow_recap.v1', 'observability_only': True, 'day': str(day), 'generated_at': str(generated_at or facade._utc_now_iso()), 'policy': {'bulk_update_time_kst': 'stage4_closeout_review + 16:00', 'trigger': 'runtime.stage4_carry_review|runtime.closeout_guard_after_sweep|closeout.post_exit_shadow_recap', 'schedule_semantics': 'Refreshes after the runtime stage4 carry review, again after the closeout sweep, and through the 16:00 closeout recap task.', 'rewrite_trade_reports': False, 'refresh_trade_summary': True, 'note': 'ai_trade_report.json is kept immutable; recap artifacts and ai_trade_summary artifacts are refreshed.'}, 'summary': {'total': len(trades), 'observed': observed_count, 'pending': len(trades) - observed_count, 'eod_observed': eod_observed_count}, 'trades': trades}
